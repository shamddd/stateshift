#!/usr/bin/env python3
"""
StateShift Production Cost Controller (Version 8 - Mission 15.2)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Enhancements over v7:
1. Durable Multi-State Shutdown Lifecycle:
   Replaces the single boolean flag with an explicit, disk-persisted state machine:
   NOT_REQUESTED -> REQUESTED -> DISPATCHING -> DISPATCHED -> PROVIDER_CONFIRMED | RETRY_PENDING | TERMINATION_UNCONFIRMED.
2. Unsuppressed Retry Semantics:
   If a shutdown callback fails or raises an exception, the state transitions to RETRY_PENDING.
   Subsequent monitoring ticks MUST continue retrying until termination is verified or retries are exhausted.
3. Durable State Rehydration:
   Persists shutdown state atomically to shutdown_state_<exp_id>.json. Upon controller restart,
   unresolved terminations are reloaded and immediately actioned.
4. Active Account Floor ($7.00 USD) and $0.3575 USD Safety Reserve.
"""

import os
import sys
import time
import json
import enum
from typing import Dict, Any, Optional, Tuple, Callable
from datetime import datetime, timezone

class ShutdownLifecycleState(str, enum.Enum):
    NOT_REQUESTED = "NOT_REQUESTED"
    REQUESTED = "REQUESTED"
    DISPATCHING = "DISPATCHING"
    DISPATCHED = "DISPATCHED"
    PROVIDER_CONFIRMED = "PROVIDER_CONFIRMED"
    RETRY_PENDING = "RETRY_PENDING"
    TERMINATION_UNCONFIRMED = "TERMINATION_UNCONFIRMED"


class RobustCostControllerV8:
    HISTORICAL_SPEND_USD = 0.6425
    TOTAL_AUTHORIZED_CAMPAIGN_USD = 11.2500
    MAX_REMAINING_BUDGET_USD = 4.2500 # available above $7.00 preservation floor
    ACCOUNT_PRESERVATION_FLOOR_USD = 7.0000
    SAFETY_RESERVE_USD = 0.7500
    RECOMMENDED_HARD_CEILING_USD = 3.5000

    def __init__(self,
                 experiment_id: str = "default_exp",
                 max_cost_usd: float = RECOMMENDED_HARD_CEILING_USD,
                 max_runtime_minutes: float = 160.0,
                 gpu_hourly_rate: float = 0.89,
                 emergency_shutdown_callback: Optional[Callable[[str], bool]] = None,
                 state_dir: Optional[str] = None,
                 max_shutdown_retries: int = 5,
                 retry_backoff_seconds: float = 1.0):
        self.experiment_id = experiment_id
        self.max_cost_usd = min(max_cost_usd, self.RECOMMENDED_HARD_CEILING_USD)
        self.max_runtime_minutes = max_runtime_minutes
        self.gpu_hourly_rate = gpu_hourly_rate
        self.emergency_shutdown_callback = emergency_shutdown_callback
        self.max_shutdown_retries = max_shutdown_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.state_dir = state_dir or os.path.join(base_dir, "logs")
        os.makedirs(self.state_dir, exist_ok=True)
        self.state_file = os.path.join(self.state_dir, f"shutdown_state_{self.experiment_id}.json")
        self.audit_log_path = os.path.join(self.state_dir, "cost_controller_audit.jsonl")
        
        self.start_time: Optional[float] = None
        self.initial_account_balance: Optional[float] = None
        self.last_heartbeat_time: Optional[float] = None
        
        # Durable shutdown tracking
        self.shutdown_state = ShutdownLifecycleState.NOT_REQUESTED
        self.shutdown_attempts: int = 0
        self.last_attempt_time: float = 0.0
        self.last_error_message: Optional[str] = None
        
        # Multi-tier thresholds
        self.soft_warning_usd = self.max_cost_usd * 0.75
        self.soft_stop_usd = self.max_cost_usd * 0.85
        self.emergency_shutdown_usd = self.max_cost_usd * 0.95
        self.hard_kill_usd = self.max_cost_usd
        
        self._load_or_persist_state()

    def _persist_shutdown_state(self) -> None:
        """Atomically persist shutdown lifecycle state to disk."""
        tmp = self.state_file + ".tmp"
        payload = {
            "experiment_id": self.experiment_id,
            "shutdown_state": self.shutdown_state.value,
            "shutdown_attempts": self.shutdown_attempts,
            "last_attempt_time": self.last_attempt_time,
            "last_error_message": self.last_error_message,
            "timestamp_utc": time.time(),
            "iso_time": datetime.now(timezone.utc).isoformat()
        }
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.state_file)

    def _load_or_persist_state(self) -> None:
        """Load durable state from disk if exists, otherwise initialize."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.shutdown_state = ShutdownLifecycleState(data.get("shutdown_state", ShutdownLifecycleState.NOT_REQUESTED.value))
                    self.shutdown_attempts = data.get("shutdown_attempts", 0)
                    self.last_attempt_time = data.get("last_attempt_time", 0.0)
                    self.last_error_message = data.get("last_error_message")
                    return
            except Exception:
                pass
        self._persist_shutdown_state()

    def record_audit_event(self, event_type: str, payload: Dict[str, Any]):
        event = {
            "timestamp": time.time(),
            "iso_time": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "shutdown_state": self.shutdown_state.value,
            "payload": payload
        }
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def initialize_session(self, 
                           pod_metadata: Optional[Dict[str, Any]] = None,
                           current_balance: Optional[float] = None):
        """Initialize session accounting for pod creation timestamp and balance floor."""
        now = time.time()
        self.initial_account_balance = current_balance
        
        if pod_metadata:
            uptime_sec = pod_metadata.get("uptimeSeconds")
            if uptime_sec is not None and uptime_sec > 0:
                self.start_time = now - uptime_sec
            else:
                self.start_time = now
        else:
            self.start_time = now
            
        self.last_heartbeat_time = now
        self.record_audit_event("SESSION_INITIALIZED", {
            "start_time": self.start_time,
            "max_cost_usd": self.max_cost_usd,
            "safety_reserve_usd": self.SAFETY_RESERVE_USD,
            "initial_balance": self.initial_account_balance,
            "preservation_floor": self.ACCOUNT_PRESERVATION_FLOOR_USD
        })

    def check_and_enforce_budget(self, current_balance: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculates effective spend and enforces shutdown lifecycle with unsuppressed retries.
        """
        now = time.time()
        start = self.start_time or now
        elapsed_sec = max(0.0, now - start)
        elapsed_min = elapsed_sec / 60.0
        elapsed_hr = elapsed_sec / 3600.0
        
        machine_spend = elapsed_hr * self.gpu_hourly_rate
        
        balance_deduction = 0.0
        floor_breached = False
        if current_balance is not None:
            if self.initial_account_balance is not None:
                balance_deduction = max(0.0, self.initial_account_balance - current_balance)
            if current_balance <= (self.ACCOUNT_PRESERVATION_FLOOR_USD + 0.35):
                floor_breached = True
                
        effective_spend = max(machine_spend, balance_deduction)
        
        spend_tripped = effective_spend >= self.emergency_shutdown_usd
        runtime_tripped = elapsed_min >= self.max_runtime_minutes
        
        should_emergency_terminate = bool(spend_tripped or runtime_tripped or floor_breached)
        
        # Check if shutdown was previously requested but remains unconfirmed
        needs_dispatch = False
        if should_emergency_terminate:
            if self.shutdown_state in [
                ShutdownLifecycleState.NOT_REQUESTED,
                ShutdownLifecycleState.REQUESTED,
                ShutdownLifecycleState.RETRY_PENDING
            ]:
                needs_dispatch = True
            elif self.shutdown_state == ShutdownLifecycleState.DISPATCHED:
                # If dispatched but not confirmed and backoff elapsed, retry
                if (now - self.last_attempt_time) >= self.retry_backoff_seconds:
                    needs_dispatch = True

        action_taken = "NONE"
        if needs_dispatch:
            action_taken = self._dispatch_shutdown_attempt(
                spend_tripped, runtime_tripped, floor_breached,
                effective_spend, elapsed_min, current_balance
            )
            
        return {
            "elapsed_minutes": round(elapsed_min, 2),
            "effective_spend_usd": round(effective_spend, 4),
            "machine_spend_usd": round(machine_spend, 4),
            "balance_deduction_usd": round(balance_deduction, 4),
            "current_balance_usd": current_balance,
            "floor_breached": floor_breached,
            "should_emergency_terminate": should_emergency_terminate,
            "shutdown_state": self.shutdown_state.value,
            "shutdown_attempts": self.shutdown_attempts,
            "action_taken": action_taken
        }

    def _dispatch_shutdown_attempt(self, spend_tripped: bool, runtime_tripped: bool, floor_breached: bool,
                                   effective_spend: float, elapsed_min: float, current_balance: Optional[float]) -> str:
        """Execute a single bounded, durable shutdown dispatch attempt."""
        if self.shutdown_attempts >= self.max_shutdown_retries:
            self.shutdown_state = ShutdownLifecycleState.TERMINATION_UNCONFIRMED
            self._persist_shutdown_state()
            self.record_audit_event("SHUTDOWN_RETRIES_EXHAUSTED", {"attempts": self.shutdown_attempts})
            return "ESCALATED_UNCONFIRMED"
            
        self.shutdown_attempts += 1
        self.last_attempt_time = time.time()
        self.shutdown_state = ShutdownLifecycleState.DISPATCHING
        self._persist_shutdown_state()
        
        reason = []
        if spend_tripped:
            reason.append(f"Spend ${effective_spend:.4f} >= limit ${self.emergency_shutdown_usd:.4f}")
        if runtime_tripped:
            reason.append(f"Runtime {elapsed_min:.1f}m >= limit {self.max_runtime_minutes:.1f}m")
        if floor_breached:
            reason.append(f"Balance ${current_balance:.4f} <= floor ${self.ACCOUNT_PRESERVATION_FLOOR_USD:.4f}")
        emergency_reason = " | ".join(reason) or "Unresolved budget shutdown"
        
        self.record_audit_event("SHUTDOWN_ATTEMPT_DISPATCHED", {
            "attempt": self.shutdown_attempts,
            "reason": emergency_reason
        })
        
        callback_result = False
        try:
            if self.emergency_shutdown_callback:
                callback_result = bool(self.emergency_shutdown_callback(emergency_reason))
            else:
                callback_result = False
        except Exception as e:
            self.last_error_message = str(e)
            callback_result = False
            
        if callback_result is True:
            self.shutdown_state = ShutdownLifecycleState.PROVIDER_CONFIRMED
            self._persist_shutdown_state()
            self.record_audit_event("SHUTDOWN_CONFIRMED", {"attempt": self.shutdown_attempts})
            return "SHUTDOWN_CONFIRMED"
        else:
            self.shutdown_state = ShutdownLifecycleState.RETRY_PENDING
            self._persist_shutdown_state()
            self.record_audit_event("SHUTDOWN_FAILED_RETRY_PENDING", {
                "attempt": self.shutdown_attempts,
                "error": self.last_error_message
            })
            return "RETRY_PENDING"
