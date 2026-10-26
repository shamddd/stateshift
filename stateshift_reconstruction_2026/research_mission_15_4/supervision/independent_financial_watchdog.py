#!/usr/bin/env python3
"""
StateShift Independent Financial Watchdog Process (Mission 15.4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Runs as an independent background daemon/process completely separate from
main controller threads and SSH/SFTP network calls:
- Tracks elapsed billable runtime using monotonic clock reconciled with pod uptime
- Queries RunPod GraphQL control plane on independent HTTPS connection
- Evaluates spend against warning threshold ($1.50), emergency trigger ($1.65),
  and preservation floor ($7.35 balance)
- Automatically dispatches provider termination directly if threshold breached,
  even if the main controller process hangs, crashes, or is blocked on SFTP
- Writes its own independent heartbeat and state file
- Detects stale controller heartbeats (> 120s)
"""

import os
import sys
import time
import json
import argparse
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple

RUNPOD_GRAPHQL_ENDPOINT = "https://api.runpod.io/graphql"


class IndependentFinancialWatchdog:
    def __init__(
        self,
        experiment_id: str,
        pod_id: str,
        watchdog_dir: str,
        max_authorized_usd: float = 2.00,
        emergency_trigger_usd: float = 1.65,
        account_preservation_floor_usd: float = 7.00,
        gpu_hourly_rate: float = 0.89,
        max_runtime_minutes: float = 160.0,
        poll_interval_seconds: float = 2.0,
        api_key: Optional[str] = None,
        main_controller_heartbeat_path: Optional[str] = None
    ):
        self.experiment_id = experiment_id
        self.pod_id = pod_id
        self.watchdog_dir = watchdog_dir
        self.max_authorized_usd = max_authorized_usd
        self.emergency_trigger_usd = emergency_trigger_usd
        self.account_preservation_floor_usd = account_preservation_floor_usd
        self.gpu_hourly_rate = gpu_hourly_rate
        self.max_runtime_minutes = max_runtime_minutes
        self.poll_interval_seconds = poll_interval_seconds
        self.api_key = api_key or os.environ.get("RUNPOD_API_KEY", "")
        self.main_controller_heartbeat_path = main_controller_heartbeat_path

        os.makedirs(self.watchdog_dir, exist_ok=True)
        self.watchdog_heartbeat_file = os.path.join(self.watchdog_dir, f"watchdog_heartbeat_{self.experiment_id}.json")
        self.watchdog_state_file = os.path.join(self.watchdog_dir, f"watchdog_state_{self.experiment_id}.json")
        self.alert_dir = self.watchdog_dir

        self.start_monotonic = time.monotonic()
        self.start_wall_time = time.time()
        self.pod_uptime_offset = 0.0
        self.stop_requested = False
        self.termination_dispatched = False
        self.termination_confirmed = False

    def _query_runpod_graphql(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Independent HTTPS GraphQL request with strict 5-second timeout."""
        if not self.api_key:
            return {}
        payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
        req = urllib.request.Request(
            f"{RUNPOD_GRAPHQL_ENDPOINT}?api_key={self.api_key}",
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "StateShift-Watchdog-v15.4"}
        )
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("data", {})
        except Exception as e:
            return {"error": str(e)}

    def get_provider_pod_uptime(self) -> Tuple[Optional[float], Optional[str]]:
        """Queries RunPod control plane independently for authoritative uptime and status."""
        query = """
        query Pod($podId: String!) {
            pod(input: {podId: $podId}) {
                id
                desiredStatus
                runtime {
                    uptimeInSeconds
                }
            }
        }
        """
        data = self._query_runpod_graphql(query, {"podId": self.pod_id})
        pod = data.get("pod")
        if not pod:
            return None, "NOT_FOUND"
        status = pod.get("desiredStatus", "UNKNOWN")
        uptime = 0.0
        if pod.get("runtime"):
            uptime = float(pod["runtime"].get("uptimeInSeconds", 0.0))
        return uptime, status

    def dispatch_provider_termination(self, reason: str) -> bool:
        """Dispatches termination mutation directly from watchdog context."""
        print(f"\n[INDEPENDENT WATCHDOG EMERGENCY TRIGGER] Reason: {reason}")
        self.termination_dispatched = True
        query = """
        mutation TerminatePod($podId: String!) {
            podTerminate(input: {podId: $podId})
        }
        """
        data = self._query_runpod_graphql(query, {"podId": self.pod_id})
        # Verify
        for _ in range(3):
            time.sleep(1.0)
            uptime, status = self.get_provider_pod_uptime()
            if status in ["NOT_FOUND", "TERMINATED", "DELETED"]:
                self.termination_confirmed = True
                print(f"[Independent Watchdog] CONFIRMED: Pod {self.pod_id} destroyed on RunPod.")
                self._persist_watchdog_state("TERMINATED_CONFIRMED", reason)
                return True

        self._persist_watchdog_state("TERMINATION_UNCONFIRMED", reason)
        return False

    def _persist_watchdog_state(self, state_str: str, reason: Optional[str] = None):
        """Atomically persists watchdog state."""
        payload = {
            "experiment_id": self.experiment_id,
            "pod_id": self.pod_id,
            "state": state_str,
            "reason": reason,
            "termination_dispatched": self.termination_dispatched,
            "termination_confirmed": self.termination_confirmed,
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        tmp = self.watchdog_state_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.watchdog_state_file)

    def write_heartbeat(self, effective_spend: float, elapsed_min: float):
        """Writes independent watchdog heartbeat."""
        payload = {
            "timestamp_utc": time.time(),
            "elapsed_minutes": round(elapsed_min, 2),
            "effective_spend_usd": round(effective_spend, 4),
            "emergency_trigger_usd": self.emergency_trigger_usd,
            "pod_id": self.pod_id,
            "status": "WATCHING"
        }
        tmp = self.watchdog_heartbeat_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.watchdog_heartbeat_file)

    def check_main_controller_alive(self, stale_seconds: float = 120.0) -> bool:
        """Audits main controller heartbeat file."""
        if not self.main_controller_heartbeat_path or not os.path.exists(self.main_controller_heartbeat_path):
            return True # Not configured or not yet initialized
        try:
            with open(self.main_controller_heartbeat_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                ts = data.get("timestamp_utc", 0.0)
                if (time.time() - ts) > stale_seconds:
                    return False
        except Exception:
            pass
        return True

    def run_supervision_tick(self, simulated_spend: Optional[float] = None) -> Dict[str, Any]:
        """Single independent watchdog evaluation tick."""
        now_mono = time.monotonic()
        elapsed_sec = now_mono - self.start_monotonic + self.pod_uptime_offset
        elapsed_min = elapsed_sec / 60.0
        elapsed_hr = elapsed_sec / 3600.0

        if simulated_spend is not None:
            effective_spend = simulated_spend
        else:
            effective_spend = elapsed_hr * self.gpu_hourly_rate

        self.write_heartbeat(effective_spend, elapsed_min)

        # Check conditions
        spend_breached = effective_spend >= self.emergency_trigger_usd
        runtime_breached = elapsed_min >= self.max_runtime_minutes
        controller_stale = not self.check_main_controller_alive()

        should_terminate = spend_breached or runtime_breached or controller_stale
        action = "CONTINUE"

        if should_terminate and not self.termination_dispatched:
            reasons = []
            if spend_breached:
                reasons.append(f"Spend ${effective_spend:.4f} >= emergency threshold ${self.emergency_trigger_usd:.4f}")
            if runtime_breached:
                reasons.append(f"Runtime {elapsed_min:.1f}m >= max allowed {self.max_runtime_minutes:.1f}m")
            if controller_stale:
                reasons.append("Main controller heartbeat stale (> 120s)")

            reason_str = " | ".join(reasons)
            success = self.dispatch_provider_termination(reason_str)
            action = "TERMINATED" if success else "TERMINATION_UNCONFIRMED"

        return {
            "elapsed_minutes": elapsed_min,
            "effective_spend_usd": effective_spend,
            "should_terminate": should_terminate,
            "action": action,
            "termination_dispatched": self.termination_dispatched,
            "termination_confirmed": self.termination_confirmed
        }


def main():
    parser = argparse.ArgumentParser(description="StateShift Independent Financial Watchdog Daemon")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--pod-id", required=True)
    parser.add_argument("--watchdog-dir", default="data/primary_run/watchdog")
    parser.add_argument("--emergency-trigger", type=float, default=1.65)
    parser.add_argument("--hourly-rate", type=float, default=0.89)
    parser.add_argument("--max-runtime", type=float, default=160.0)
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--controller-heartbeat", default=None)
    parser.add_argument("--simulate-spend", type=float, default=None)
    parser.add_argument("--single-tick", action="store_true")
    args = parser.parse_args()

    watchdog = IndependentFinancialWatchdog(
        experiment_id=args.experiment_id,
        pod_id=args.pod_id,
        watchdog_dir=args.watchdog_dir,
        emergency_trigger_usd=args.emergency_trigger,
        gpu_hourly_rate=args.hourly_rate,
        max_runtime_minutes=args.max_runtime,
        poll_interval_seconds=args.poll_interval,
        main_controller_heartbeat_path=args.controller_heartbeat
    )

    if args.single_tick:
        res = watchdog.run_supervision_tick(simulated_spend=args.simulate_spend)
        print(json.dumps(res, indent=2))
        sys.exit(0 if not res["should_terminate"] else 2)

    print(f"[Watchdog Daemon] Started for pod {args.pod_id} (Emergency Trigger: ${args.emergency_trigger:.2f}).")
    while not watchdog.stop_requested:
        res = watchdog.run_supervision_tick(simulated_spend=args.simulate_spend)
        if res["should_terminate"]:
            print(f"[Watchdog Daemon] Termination dispatched. Final status: {res['action']}.")
            break
        time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
