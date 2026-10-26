#!/usr/bin/env python3
"""
StateShift RunPod Cost & Lifecycle Controller (v3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Enforces multi-layer financial safety and true cloud resource termination:
Distinguishes:
1. Process exit (experiment completed/failed)
2. Container stop (Docker container terminates)
3. Pod stop (allocated GPU reserved, still billed storage)
4. Billable Resource Termination (pod deleted via RunPod GraphQL API, billing halts)
"""

import os
import sys
import time
import json
import requests
from typing import Dict, Any, Optional, Tuple

RUNPOD_GRAPHQL_URL = "https://api.runpod.io/graphql"

class RunPodCostController:
    """Manages cloud spending limits and provider-side pod termination."""

    def __init__(self, 
                 api_key: Optional[str] = None,
                 pod_id: Optional[str] = None,
                 max_runtime_minutes: int = 90,
                 max_cost_usd: float = 1.00,
                 gpu_hourly_rate: float = 0.34):
        self.api_key = api_key or os.environ.get("RUNPOD_API_KEY", "")
        self.pod_id = pod_id or os.environ.get("RUNPOD_POD_ID", "")
        self.max_runtime_minutes = max_runtime_minutes
        self.max_cost_usd = max_cost_usd
        self.gpu_hourly_rate = gpu_hourly_rate
        self.start_time = time.time()

    def check_authorization(self) -> Tuple[bool, str]:
        """Verify that explicit user authorization is provided."""
        auth_env = os.environ.get("RUNPOD_AUTHORIZED", "").strip().upper()
        if auth_env != "TRUE":
            return False, "BLOCKED: Environment variable RUNPOD_AUTHORIZED != TRUE."
        if not self.api_key:
            return False, "BLOCKED: RUNPOD_API_KEY missing from environment."
        if not self.pod_id:
            return False, "BLOCKED: RUNPOD_POD_ID missing from environment."
        return True, "AUTHORIZED: Valid credentials and explicit authorization flag detected."

    def calculate_current_spend(self) -> Dict[str, Any]:
        """Calculate elapsed runtime and current estimated billing."""
        elapsed_sec = time.time() - self.start_time
        elapsed_min = elapsed_sec / 60.0
        elapsed_hr = elapsed_sec / 3600.0
        current_spend = elapsed_hr * self.gpu_hourly_rate
        
        exceeded_time = elapsed_min >= self.max_runtime_minutes
        exceeded_cost = current_spend >= self.max_cost_usd
        
        return {
            "elapsed_seconds": round(elapsed_sec, 1),
            "elapsed_minutes": round(elapsed_min, 2),
            "estimated_spend_usd": round(current_spend, 4),
            "max_runtime_minutes": self.max_runtime_minutes,
            "max_cost_usd": self.max_cost_usd,
            "budget_exceeded": bool(exceeded_time or exceeded_cost),
            "reason": "Max runtime exceeded" if exceeded_time else "Max cost exceeded" if exceeded_cost else "Within budget"
        }

    def request_pod_termination(self, max_retries: int = 3) -> Dict[str, Any]:
        """
        Sends an authenticated GraphQL mutation to RunPod to PERMANENTLY TERMINATE
        the billable pod resource. This halts GPU billing at the cloud provider level.
        """
        if not self.api_key or not self.pod_id:
            return {
                "success": False,
                "action": "TERMINATION_FAILED",
                "error": "Cannot terminate: Missing RUNPOD_API_KEY or RUNPOD_POD_ID"
            }
            
        mutation = """
        mutation TerminatePod($input: PodTerminateInput!) {
            podTerminate(input: $input)
        }
        """
        variables = {
            "input": {
                "podId": self.pod_id
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"[CostController] Requesting pod termination from RunPod API (Attempt {attempt}/{max_retries})...")
                resp = requests.post(
                    RUNPOD_GRAPHQL_URL,
                    json={"query": mutation, "variables": variables},
                    headers=headers,
                    timeout=15
                )
                if resp.status_code == 200:
                    res_data = resp.json()
                    if "errors" in res_data:
                        print(f"[CostController] API returned GraphQL errors: {res_data['errors']}")
                    else:
                        print(f"[CostController] Pod {self.pod_id} successfully terminated. Billing stopped.")
                        return {
                            "success": True,
                            "action": "POD_TERMINATED",
                            "pod_id": self.pod_id,
                            "provider_response": res_data
                        }
                else:
                    print(f"[CostController] HTTP {resp.status_code}: {resp.text}")
            except Exception as e:
                print(f"[CostController] Network error during termination request: {e}")
                
            time.sleep(2)
            
        return {
            "success": False,
            "action": "POD_TERMINATION_FAILED",
            "error": "Exceeded maximum retry attempts to RunPod API"
        }

if __name__ == "__main__":
    controller = RunPodCostController()
    auth, msg = controller.check_authorization()
    print(f"Authorization: {auth} ({msg})")
    print("Spend stats:", controller.calculate_current_spend())
