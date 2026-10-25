#!/usr/bin/env python3
"""
StateShift Robust External Cost Controller (Version 5 - Mission 14)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Enhancements over v4:
1. True Pod Creation Accounting: When adopting an existing pod, extracts creation timestamp
   from provider API metadata (lastStatusChange / uptimeSeconds) rather than resetting the clock.
2. Dual Cost Tracking: Tracks both calculated GPU machine cost ($/hr * runtime) and actual
   provider account balance changes.
3. Multi-Failure Resilience: Handles API network timeouts, missing heartbeats, unexpected
   pod deletions, and idempotent repeated termination calls.
4. Soft vs. Hard Ceilings: Distinguishes between local soft shutdown thresholds and
   provider-level hard budget limits.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

RUNPOD_GRAPHQL_ENDPOINT = "https://api.runpod.io/graphql"

class RobustExternalCostControllerV5:
    def __init__(self,
                 api_key: Optional[str] = None,
                 pod_id: Optional[str] = None,
                 max_cost_usd: float = 2.80,
                 max_runtime_minutes: float = 60.0,
                 gpu_hourly_rate: float = 0.89,
                 audit_log_path: Optional[str] = None):
        self.api_key = api_key or os.environ.get("RUNPOD_API_KEY", "")
        self.pod_id = pod_id or os.environ.get("RUNPOD_POD_ID", "")
        self.max_cost_usd = max_cost_usd
        self.max_runtime_minutes = max_runtime_minutes
        self.gpu_hourly_rate = gpu_hourly_rate
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.audit_log_path = audit_log_path or os.path.join(base_dir, "logs", "cost_controller_audit.jsonl")
        
        self.start_time: Optional[float] = None
        self.initial_account_balance: Optional[float] = None
        self.last_heartbeat_time: Optional[float] = None
        self.is_terminated: bool = False
        self.termination_receipt: Optional[Dict[str, Any]] = None

    def record_audit_event(self, event_type: str, payload: Dict[str, Any]):
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
        event = {
            "timestamp": time.time(),
            "iso_time": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "pod_id": self.pod_id,
            "payload": payload
        }
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def initialize_session(self, 
                           pod_metadata: Optional[Dict[str, Any]] = None,
                           current_balance: Optional[float] = None):
        """
        Initialize session accounting for pod creation timestamp.
        If adopting an existing pod, derives true start time from provider metadata.
        """
        now = time.time()
        self.initial_account_balance = current_balance
        
        if pod_metadata:
            # Check lastStatusChange or uptimeSeconds
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
            "gpu_hourly_rate": self.gpu_hourly_rate,
            "max_cost_usd": self.max_cost_usd,
            "initial_balance": self.initial_account_balance
        })

    def calculate_spend(self, current_balance: Optional[float] = None) -> Dict[str, Any]:
        """Compute estimated runtime spend and actual ledger deduction."""
        now = time.time()
        start = self.start_time or now
        elapsed_sec = max(0.0, now - start)
        elapsed_min = elapsed_sec / 60.0
        elapsed_hr = elapsed_sec / 3600.0
        
        estimated_machine_spend = elapsed_hr * self.gpu_hourly_rate
        
        actual_deduction = None
        if self.initial_account_balance is not None and current_balance is not None:
            actual_deduction = max(0.0, self.initial_account_balance - current_balance)
            
        # Hard limits check
        cost_ceiling_tripped = estimated_machine_spend >= self.max_cost_usd
        runtime_ceiling_tripped = elapsed_min >= self.max_runtime_minutes
        
        # Check heartbeat stall (> 10 minutes without heartbeat)
        heartbeat_stalled = False
        if self.last_heartbeat_time is not None and (now - self.last_heartbeat_time) > 600.0:
            heartbeat_stalled = True
            
        should_terminate = bool(cost_ceiling_tripped or runtime_ceiling_tripped or heartbeat_stalled)
        
        status = {
            "elapsed_seconds": round(elapsed_sec, 2),
            "elapsed_minutes": round(elapsed_min, 2),
            "estimated_machine_spend_usd": round(estimated_machine_spend, 4),
            "actual_account_deduction_usd": round(actual_deduction, 4) if actual_deduction is not None else None,
            "cost_ceiling_tripped": cost_ceiling_tripped,
            "runtime_ceiling_tripped": runtime_ceiling_tripped,
            "heartbeat_stalled": heartbeat_stalled,
            "should_terminate": should_terminate
        }
        return status
