#!/usr/bin/env python3
"""
StateShift Independent Cloud Watchdog Daemon (v3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Runs as an independent background supervisor:
- Checks budget and elapsed time every 30 seconds
- Triggers RunPod API pod termination when limit reached
- Handles emergency container shutdown if API is unreachable
"""

import os
import sys
import time
import subprocess
from cost_controller import RunPodCostController

def run_watchdog(max_runtime_minutes: int = 90, max_cost_usd: float = 1.00):
    print(f"[Watchdog] Starting independent supervisor. Max runtime: {max_runtime_minutes}m, Max budget: ${max_cost_usd}")
    controller = RunPodCostController(
        max_runtime_minutes=max_runtime_minutes,
        max_cost_usd=max_cost_usd
    )
    
    while True:
        time.sleep(30)
        spend_info = controller.calculate_current_spend()
        print(f"[Watchdog] Runtime: {spend_info['elapsed_minutes']}m | Spend: ${spend_info['estimated_spend_usd']:.4f}")
        
        if spend_info["budget_exceeded"]:
            print(f"[Watchdog] CRITICAL: {spend_info['reason']}. Initiating termination sequence...")
            
            # Step 1: Request provider-side billable pod termination
            term_res = controller.request_pod_termination(max_retries=3)
            print(f"[Watchdog] Termination result: {term_res}")
            
            # Step 2: Emergency fallback if still running
            time.sleep(10)
            print("[Watchdog] Executing local OS shutdown fallback...")
            try:
                subprocess.run(["shutdown", "-h", "now"], check=False)
            except Exception:
                pass
            sys.exit(0)

if __name__ == "__main__":
    max_m = int(os.environ.get("MAX_RUNTIME_MINUTES", "90"))
    max_c = float(os.environ.get("MAX_BUDGET_USD", "1.00"))
    run_watchdog(max_runtime_minutes=max_m, max_cost_usd=max_c)
