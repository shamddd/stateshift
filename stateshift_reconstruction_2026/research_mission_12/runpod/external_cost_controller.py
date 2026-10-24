#!/usr/bin/env python3
"""
StateShift External RunPod Cost Controller (v4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

An independent, client-side controller operating strictly outside the GPU pod.
Monitors cloud resource consumption, enforces non-negotiable financial ceilings,
and issues hard provider-level termination commands via RunPod GraphQL API.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, Optional, Tuple

RUNPOD_GRAPHQL_ENDPOINT = "https://api.runpod.io/graphql"

class ExternalRunPodCostController:
    """
    Decoupled financial gatekeeper and lifecycle controller.
    Runs locally on the researcher's host environment or monitoring daemon.
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 pod_id: Optional[str] = None,
                 max_cost_usd: float = 3.00,
                 max_runtime_minutes: float = 30.0,
                 gpu_hourly_rate: float = 0.74, # Default RTX 4090 / A5000 rate
                 audit_log_path: Optional[str] = None):
        self.api_key = api_key or os.environ.get("RUNPOD_API_KEY", "")
        self.pod_id = pod_id or os.environ.get("RUNPOD_POD_ID", "")
        self.max_cost_usd = max_cost_usd
        self.max_runtime_minutes = max_runtime_minutes
        self.gpu_hourly_rate = gpu_hourly_rate
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.audit_log_path = audit_log_path or os.path.join(base_dir, "runpod", "cost_controller_audit.jsonl")
        
        self.start_time: Optional[float] = None
        self.last_heartbeat_time: Optional[float] = None
        self.is_terminated: bool = False
        self.termination_receipt: Optional[Dict[str, Any]] = None

    def start_session(self, initial_timestamp: Optional[float] = None):
        """Record session initiation time and heartbeat."""
        if self.start_time is not None and initial_timestamp is None:
            return
        now = initial_timestamp or time.time()
        self.start_time = now
        self.last_heartbeat_time = now
        self.record_audit_event("SESSION_START", {
            "pod_id": self.pod_id,
            "max_cost_usd": self.max_cost_usd,
            "max_runtime_minutes": self.max_runtime_minutes,
            "gpu_hourly_rate": self.gpu_hourly_rate
        })

    def record_heartbeat(self, timestamp: Optional[float] = None):
        """Update last seen heartbeat from pod telemetry or API poll."""
        self.last_heartbeat_time = timestamp or time.time()

    def check_authorization(self) -> Tuple[bool, str]:
        """
        Enforce strict authorization criteria:
        Requires RUNPOD_AUTHORIZED='TRUE' and non-empty RUNPOD_API_KEY.
        """
        auth_flag = os.environ.get("RUNPOD_AUTHORIZED", "").strip().upper()
        if auth_flag != "TRUE":
            return False, "BLOCKED: Environment variable RUNPOD_AUTHORIZED != 'TRUE'."
        if not self.api_key or len(self.api_key.strip()) < 10:
            return False, "BLOCKED: RUNPOD_API_KEY is missing or invalid."
        return True, "AUTHORIZED: Explicit user authorization and API key confirmed."

    def calculate_spend(self, current_time: Optional[float] = None) -> Dict[str, Any]:
        """Compute elapsed wall-clock time, billable compute, and remaining headroom."""
        now = current_time or time.time()
        if self.start_time is None:
            self.start_time = now
            self.last_heartbeat_time = now

        elapsed_sec = now - self.start_time
        elapsed_min = elapsed_sec / 60.0
        elapsed_hr = elapsed_sec / 3600.0
        estimated_spend = elapsed_hr * self.gpu_hourly_rate
        
        remaining_budget = max(0.0, self.max_cost_usd - estimated_spend)
        remaining_minutes = max(0.0, self.max_runtime_minutes - elapsed_min)
        
        cost_limit_hit = estimated_spend >= self.max_cost_usd
        time_limit_hit = elapsed_min >= self.max_runtime_minutes
        
        # Check heartbeat stall (> 300 seconds = 5 minutes)
        heartbeat_stall = False
        stall_duration = 0.0
        if self.last_heartbeat_time:
            stall_duration = now - self.last_heartbeat_time
            if stall_duration > 300.0:
                heartbeat_stall = True

        should_terminate = bool(cost_limit_hit or time_limit_hit or heartbeat_stall)
        reason = "OK"
        if cost_limit_hit:
            reason = f"Budget ceiling exceeded (${estimated_spend:.2f} >= ${self.max_cost_usd:.2f})"
        elif time_limit_hit:
            reason = f"Runtime ceiling exceeded ({elapsed_min:.1f} min >= {self.max_runtime_minutes:.1f} min)"
        elif heartbeat_stall:
            reason = f"Heartbeat lost for {stall_duration:.1f}s (> 300s threshold)"

        return {
            "elapsed_seconds": round(elapsed_sec, 2),
            "elapsed_minutes": round(elapsed_min, 2),
            "estimated_spend_usd": round(estimated_spend, 4),
            "remaining_budget_usd": round(remaining_budget, 4),
            "remaining_minutes": round(remaining_minutes, 2),
            "cost_limit_hit": cost_limit_hit,
            "time_limit_hit": time_limit_hit,
            "heartbeat_stall": heartbeat_stall,
            "should_terminate": should_terminate,
            "reason": reason
        }

    def execute_hard_termination(self, reason: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Sends an authenticated GraphQL podTerminate mutation to RunPod.
        This deletes the container and releases the physical GPU, arresting billing.
        """
        timestamp = time.time()
        if not self.pod_id:
            receipt = {
                "success": False,
                "pod_id": None,
                "action": "TERMINATION_FAILED",
                "reason": reason,
                "error": "Pod ID not specified",
                "timestamp": timestamp
            }
            self.record_audit_event("TERMINATION_FAILED", receipt)
            return receipt

        if dry_run:
            receipt = {
                "success": True,
                "pod_id": self.pod_id,
                "action": "DRY_RUN_TERMINATE",
                "reason": reason,
                "timestamp": timestamp
            }
            self.record_audit_event("DRY_RUN_TERMINATION", receipt)
            self.is_terminated = True
            self.termination_receipt = receipt
            return receipt

        import requests
        mutation = """
        mutation TerminatePod($input: PodTerminateInput!) {
            podTerminate(input: $input)
        }
        """
        variables = {"input": {"podId": self.pod_id}}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            resp = requests.post(
                RUNPOD_GRAPHQL_ENDPOINT,
                json={"query": mutation, "variables": variables},
                headers=headers,
                timeout=15.0
            )
            data = resp.json()
            if "errors" in data and data["errors"]:
                err_msg = str(data["errors"])
                receipt = {
                    "success": False,
                    "pod_id": self.pod_id,
                    "action": "TERMINATION_ERROR",
                    "reason": reason,
                    "error": err_msg,
                    "timestamp": timestamp
                }
            else:
                receipt = {
                    "success": True,
                    "pod_id": self.pod_id,
                    "action": "BILLABLE_RESOURCE_TERMINATED",
                    "reason": reason,
                    "runpod_response": data.get("data", {}),
                    "timestamp": timestamp
                }
                self.is_terminated = True
        except Exception as e:
            receipt = {
                "success": False,
                "pod_id": self.pod_id,
                "action": "NETWORK_EXCEPTION",
                "reason": reason,
                "error": str(e),
                "timestamp": timestamp
            }

        self.record_audit_event("POD_TERMINATION_EXECUTED", receipt)
        self.termination_receipt = receipt
        return receipt

    def record_audit_event(self, event_type: str, payload: Dict[str, Any]):
        """Persist append-only audit event to JSONL ledger."""
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
        event = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": event_type,
            "pod_id": self.pod_id,
            "payload": payload
        }
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logging.error(f"Failed to record audit event: {e}")
