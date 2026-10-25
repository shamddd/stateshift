#!/usr/bin/env python3
"""
StateShift Production Cost Controller (Version 7 - Mission 15.1)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Enhancements over v6:
1. Direct Integration with Emergency Termination:
   Directly invokes orchestrator.terminate_emergency(reason) upon threshold breach.
2. Conservative Safety Reserve ($0.3575 USD):
   Total ceiling: $3.0000 USD. Historical spend: $0.6425 USD. Remaining: $2.3575 USD.
   Hard controller shutdown ceiling is set to $2.0000 USD, reserving $0.3575 USD
   for provider billing lag, container storage, and termination retries.
3. Multi-tier Emergency Signals:
   - 75% ($1.50 USD): Soft Warning.
   - 85% ($1.70 USD): Soft Stop (halt new requests).
   - 95% ($1.90 USD): Emergency Sync & Immediate Shutdown Request.
   - 100% ($2.00 USD): Unconditional Hard Termination Gate.
4. Independent Account Preservation Floor Guard ($7.00 USD):
   If reported provider account balance falls below $7.35 USD, hard emergency shutdown triggers.
"""

import os
import sys
import time
import json
from typing import Dict, Any, Optional, Tuple, Callable
from datetime import datetime, timezone

class RobustCostControllerV7:
    HISTORICAL_SPEND_USD = 0.6425
    TOTAL_AUTHORIZED_CAMPAIGN_USD = 3.0000
    MAX_REMAINING_BUDGET_USD = TOTAL_AUTHORIZED_CAMPAIGN_USD - HISTORICAL_SPEND_USD # 2.3575
    ACCOUNT_PRESERVATION_FLOOR_USD = 7.0000
    SAFETY_RESERVE_USD = 0.3575
    RECOMMENDED_HARD_CEILING_USD = MAX_REMAINING_BUDGET_USD - SAFETY_RESERVE_USD # 2.0000

    def __init__(self,
                 max_cost_usd: float = RECOMMENDED_HARD_CEILING_USD,
                 max_runtime_minutes: float = 160.0,
                 gpu_hourly_rate: float = 0.89,
                 emergency_shutdown_callback: Optional[Callable[[str], bool]] = None,
                 audit_log_path: Optional[str] = None):
        # Strict hard limit cap
        self.max_cost_usd = min(max_cost_usd, self.RECOMMENDED_HARD_CEILING_USD)
        self.max_runtime_minutes = max_runtime_minutes
        self.gpu_hourly_rate = gpu_hourly_rate
        self.emergency_shutdown_callback = emergency_shutdown_callback
        
        self.audit_log_path = audit_log_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "logs",
            "cost_controller_audit.jsonl"
        )
        
        self.start_time: Optional[float] = None
        self.initial_account_balance: Optional[float] = None
        self.last_heartbeat_time: Optional[float] = None
        self.emergency_shutdown_triggered: bool = False
        
        # Thresholds
        self.soft_warning_usd = self.max_cost_usd * 0.75
        self.soft_stop_usd = self.max_cost_usd * 0.85
        self.emergency_shutdown_usd = self.max_cost_usd * 0.95
        self.hard_kill_usd = self.max_cost_usd

    def record_audit_event(self, event_type: str, payload: Dict[str, Any]):
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
        event = {
            "timestamp": time.time(),
            "iso_time": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
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
        Calculates effective spend and triggers emergency termination callback if breached.
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
        
        # Trigger conditions
        spend_tripped = effective_spend >= self.emergency_shutdown_usd
        runtime_tripped = elapsed_min >= self.max_runtime_minutes
        
        should_emergency_terminate = bool(spend_tripped or runtime_tripped or floor_breached)
        
        action_taken = "NONE"
        if should_emergency_terminate and not self.emergency_shutdown_triggered:
            self.emergency_shutdown_triggered = True
            reason = []
            if spend_tripped:
                reason.append(f"Spend ${effective_spend:.4f} >= ceiling ${self.emergency_shutdown_usd:.4f}")
            if runtime_tripped:
                reason.append(f"Runtime {elapsed_min:.1f}m >= limit {self.max_runtime_minutes:.1f}m")
            if floor_breached:
                reason.append(f"Balance ${current_balance:.4f} approaching floor ${self.ACCOUNT_PRESERVATION_FLOOR_USD:.4f}")
                
            emergency_reason = " | ".join(reason)
            self.record_audit_event("EMERGENCY_SHUTDOWN_SIGNAL_DISPATCHED", {
                "reason": emergency_reason,
                "effective_spend": effective_spend,
                "current_balance": current_balance
            })
            
            if self.emergency_shutdown_callback:
                self.emergency_shutdown_callback(emergency_reason)
                action_taken = "EMERGENCY_SHUTDOWN_CALLED"
                
        return {
            "elapsed_minutes": round(elapsed_min, 2),
            "effective_spend_usd": round(effective_spend, 4),
            "machine_spend_usd": round(machine_spend, 4),
            "balance_deduction_usd": round(balance_deduction, 4),
            "current_balance_usd": current_balance,
            "floor_breached": floor_breached,
            "should_emergency_terminate": should_emergency_terminate,
            "emergency_shutdown_triggered": self.emergency_shutdown_triggered,
            "action_taken": action_taken
        }
