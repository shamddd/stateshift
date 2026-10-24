#!/usr/bin/env python3
"""
StateShift Pod Lifecycle Monitor Daemon (v4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Runs as an external monitoring loop on the local client / host.
Continuously polls the RunPod API, assesses financial ceilings, tracks heartbeat,
and immediately triggers provider-level termination upon task completion,
budget over-run, or communication failure.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, Optional

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_root)

try:
    from external_cost_controller import ExternalRunPodCostController
except ImportError:
    from runpod.external_cost_controller import ExternalRunPodCostController

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class PodLifecycleMonitor:
    """External daemon tracking RunPod instance lifecycle."""

    def __init__(self,
                 controller: ExternalRunPodCostController,
                 poll_interval_seconds: float = 15.0,
                 max_consecutive_poll_failures: int = 5):
        self.controller = controller
        self.poll_interval = poll_interval_seconds
        self.max_failures = max_consecutive_poll_failures
        self.consecutive_failures = 0
        self.running = False

    def query_pod_status_runpod(self) -> Dict[str, Any]:
        """
        Poll RunPod API for pod runtime status:
        Returns: {'status': 'RUNNING'|'EXITED'|'TERMINATED'|'UNKNOWN', 'uptime_sec': float, ...}
        """
        import requests
        if not self.controller.api_key or not self.controller.pod_id:
            return {"status": "MOCK_RUNNING", "uptime_sec": 0, "mock": True}

        query = """
        query GetPod($podId: String!) {
            pod(input: {podId: $podId}) {
                id
                name
                runtime {
                    uptimeInSeconds
                    gpus {
                        id
                        gpuUtilPercent
                        memoryUtilPercent
                    }
                }
                desiredStatus
                lastStatusChange
            }
        }
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.controller.api_key}"
        }
        try:
            resp = requests.post(
                "https://api.runpod.io/graphql",
                json={"query": query, "variables": {"podId": self.controller.pod_id}},
                headers=headers,
                timeout=10.0
            )
            data = resp.json()
            pod_info = data.get("data", {}).get("pod")
            if not pod_info:
                return {"status": "NOT_FOUND", "raw": data}
            
            runtime = pod_info.get("runtime") or {}
            uptime = runtime.get("uptimeInSeconds", 0)
            return {
                "status": "RUNNING" if uptime > 0 else "STARTING",
                "uptime_sec": uptime,
                "desired_status": pod_info.get("desiredStatus"),
                "raw": pod_info
            }
        except Exception as e:
            return {"status": "POLL_ERROR", "error": str(e)}

    def run_monitor_loop(self, dry_run: bool = True, max_cycles: Optional[int] = None) -> Dict[str, Any]:
        """Execute active monitoring cycle."""
        self.running = True
        self.controller.start_session()
        logging.info(f"[Monitor] Starting pod lifecycle monitor for Pod ID: {self.controller.pod_id}")
        logging.info(f"[Monitor] Budget Ceiling: ${self.controller.max_cost_usd:.2f} | Time Ceiling: {self.controller.max_runtime_minutes:.1f} min")

        cycle = 0
        while self.running:
            cycle += 1
            spend_status = self.controller.calculate_spend()
            
            # Poll RunPod Provider
            pod_status = self.query_pod_status_runpod()
            if pod_status.get("status") in ("RUNNING", "MOCK_RUNNING"):
                self.consecutive_failures = 0
                self.controller.record_heartbeat()
            elif pod_status.get("status") == "POLL_ERROR":
                self.consecutive_failures += 1
                logging.warning(f"[Monitor] Poll failure {self.consecutive_failures}/{self.max_failures}: {pod_status.get('error')}")
            
            logging.info(
                f"[Cycle {cycle}] Elapsed: {spend_status['elapsed_minutes']:.1f}m | "
                f"Est. Spend: ${spend_status['estimated_spend_usd']:.3f} / ${self.controller.max_cost_usd:.2f} | "
                f"Status: {pod_status.get('status')}"
            )

            # Check termination triggers
            if spend_status["should_terminate"]:
                logging.warning(f"[Monitor] Triggering TERMINATION: {spend_status['reason']}")
                receipt = self.controller.execute_hard_termination(spend_status["reason"], dry_run=dry_run)
                self.running = False
                return receipt

            if self.consecutive_failures >= self.max_failures:
                reason = f"Exceeded max consecutive poll failures ({self.max_failures})"
                logging.error(f"[Monitor] Triggering EMERGENCY TERMINATION: {reason}")
                receipt = self.controller.execute_hard_termination(reason, dry_run=dry_run)
                self.running = False
                return receipt

            if max_cycles and cycle >= max_cycles:
                logging.info(f"[Monitor] Completed designated cycles ({max_cycles}). Ending monitor loop.")
                self.running = False
                return {"status": "CYCLES_EXHAUSTED", "spend_status": spend_status}

            time.sleep(self.poll_interval)

        return {"status": "STOPPED", "final_spend": self.controller.calculate_spend()}
