#!/usr/bin/env python3
"""
StateShift Robust External Cost Controller (Version 6 - Mission 15)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Enhancements over v5:
1. Strict Remaining Budget Enforcement:
   Maximum campaign budget authorized is $3.00 USD.
   Historical Mission 13 spend: $0.6425 USD.
   Remaining potential authorization: $2.3575 USD.
   Hard ceiling set to min(max_cost_usd, $2.3575).
2. Multi-Stage Thresholds:
   - Soft Warning (75% of limit): Log alert, trigger intermediate sync.
   - Soft Stop (85% of limit): Signal orchestrator to finish current problem batch.
   - Emergency Sync Gate (92% of limit): Halt generation, force atomic sync of partial records.
   - Hard Kill Gate (95% of limit): Force immediate pod termination regardless of job status.
3. Provider API Lag & Jitter Compensation:
   Blends estimated machine-hour spend with reported RunPod balance delta.
   Uses pessimistic maximum of machine cost vs reported deduction.
4. Comprehensive Analytical Forecasting:
   Precomputes runtime and cost bounds across varied token lengths and initialization overheads.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

class RobustCostControllerV6:
    HISTORICAL_SPEND_USD = 0.6425
    TOTAL_AUTHORIZED_CAMPAIGN_USD = 3.0000
    MAX_REMAINING_BUDGET_USD = TOTAL_AUTHORIZED_CAMPAIGN_USD - HISTORICAL_SPEND_USD # 2.3575

    def __init__(self,
                 api_key: Optional[str] = None,
                 pod_id: Optional[str] = None,
                 max_cost_usd: float = 2.30,  # Below $2.3575 hard limit
                 max_runtime_minutes: float = 160.0,
                 gpu_hourly_rate: float = 0.89, # RTX 4090 rate
                 audit_log_path: Optional[str] = None):
        self.api_key = api_key or os.environ.get("RUNPOD_API_KEY", "")
        self.pod_id = pod_id or os.environ.get("RUNPOD_POD_ID", "")
        
        # Enforce strict campaign budget ceiling
        self.max_cost_usd = min(max_cost_usd, self.MAX_REMAINING_BUDGET_USD)
        self.max_runtime_minutes = max_runtime_minutes
        self.gpu_hourly_rate = gpu_hourly_rate
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.audit_log_path = audit_log_path or os.path.join(base_dir, "logs", "cost_controller_audit.jsonl")
        
        self.start_time: Optional[float] = None
        self.initial_account_balance: Optional[float] = None
        self.last_heartbeat_time: Optional[float] = None
        self.is_terminated: bool = False
        
        # Multi-stage thresholds
        self.soft_warning_usd = self.max_cost_usd * 0.75
        self.soft_stop_usd = self.max_cost_usd * 0.85
        self.emergency_sync_usd = self.max_cost_usd * 0.92
        self.hard_kill_usd = self.max_cost_usd * 0.95

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
        Derives true billing start time from provider metadata.
        """
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
            "gpu_hourly_rate": self.gpu_hourly_rate,
            "max_cost_usd": self.max_cost_usd,
            "initial_balance": self.initial_account_balance,
            "remaining_campaign_budget": self.MAX_REMAINING_BUDGET_USD
        })

    def calculate_spend(self, current_balance: Optional[float] = None) -> Dict[str, Any]:
        """
        Pessimistic spend calculation blending machine hours and account deductions.
        """
        now = time.time()
        start = self.start_time or now
        elapsed_sec = max(0.0, now - start)
        elapsed_min = elapsed_sec / 60.0
        elapsed_hr = elapsed_sec / 3600.0
        
        estimated_machine_spend = elapsed_hr * self.gpu_hourly_rate
        
        actual_deduction = None
        if self.initial_account_balance is not None and current_balance is not None:
            actual_deduction = max(0.0, self.initial_account_balance - current_balance)
            
        # Use pessimistic effective spend
        effective_spend = max(estimated_machine_spend, actual_deduction or 0.0)
        
        # Multi-stage threshold checks
        warning_tripped = effective_spend >= self.soft_warning_usd
        stop_tripped = effective_spend >= self.soft_stop_usd
        emergency_sync_tripped = effective_spend >= self.emergency_sync_usd
        hard_kill_tripped = (effective_spend >= self.hard_kill_usd) or (elapsed_min >= self.max_runtime_minutes)
        
        return {
            "elapsed_seconds": round(elapsed_sec, 2),
            "elapsed_minutes": round(elapsed_min, 2),
            "estimated_machine_spend_usd": round(estimated_machine_spend, 4),
            "actual_account_deduction_usd": round(actual_deduction, 4) if actual_deduction is not None else None,
            "effective_spend_usd": round(effective_spend, 4),
            "warning_tripped": warning_tripped,
            "stop_tripped": stop_tripped,
            "emergency_sync_tripped": emergency_sync_tripped,
            "hard_kill_tripped": hard_kill_tripped,
            "should_terminate": hard_kill_tripped
        }

    @staticmethod
    def forecast_400_request_cost(throughput_tok_s: float = 41.2,
                                  init_overhead_minutes: float = 8.0,
                                  gpu_hourly_rate: float = 0.89) -> Dict[str, Any]:
        """
        Analytical cost model for 400 requests across token length regimes.
        """
        scenarios = {
            "conservative_short_400tok": 400,
            "expected_avg_550tok": 550,
            "pessimistic_long_700tok": 700,
            "upper_bound_900tok": 900
        }
        forecasts = {}
        for name, avg_tokens in scenarios.items():
            total_tokens = 400 * avg_tokens
            generation_sec = total_tokens / throughput_tok_s
            generation_min = generation_sec / 60.0
            total_min = init_overhead_minutes + generation_min
            total_hr = total_min / 60.0
            cost_usd = total_hr * gpu_hourly_rate
            forecasts[name] = {
                "avg_tokens": avg_tokens,
                "total_tokens": total_tokens,
                "generation_minutes": round(generation_min, 2),
                "total_minutes": round(total_min, 2),
                "estimated_cost_usd": round(cost_usd, 4),
                "within_budget_limit": cost_usd <= 2.30
            }
        return forecasts
