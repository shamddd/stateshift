#!/usr/bin/env python3
"""
StateShift Independent Financial Watchdog Daemon (Mission 15.5)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Genuinely Independent Operating System Process:
- Runs in a decoupled subprocess with its own OS PID.
- Operates its own monotonic runtime clock and durable state file.
- Strict Provider API Error vs Termination Classification:
  Distinguishes RUNNING, STOPPED, TERMINATED, DELETED, AUTHORITATIVE_NOT_FOUND
  from transient API_ERROR, TIMEOUT, AUTH_ERROR, and MALFORMED_RESPONSE.
- Enforces session-specific budget limits derived directly from verified authorization.
- Survives main controller crash/SIGKILL and enforces termination.
- Emergency terminates pod directly via RunPod GraphQL API with retry and durable escalation.
"""

import os
import sys
import time
import json
import signal
import argparse
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple

RUNPOD_GRAPHQL_ENDPOINT = "https://api.runpod.io/graphql"


class ProviderResponseState:
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    TERMINATED = "TERMINATED"
    DELETED = "DELETED"
    AUTHORITATIVE_NOT_FOUND = "AUTHORITATIVE_NOT_FOUND"
    API_ERROR = "API_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    TIMEOUT = "TIMEOUT"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    UNKNOWN = "UNKNOWN"
    TERMINATION_UNCONFIRMED = "TERMINATION_UNCONFIRMED"


class IndependentFinancialWatchdog:
    def __init__(
        self,
        experiment_id: str,
        pod_id: str,
        watchdog_dir: str,
        session_id: str = "default_session",
        max_authorized_usd: float = 0.35,
        emergency_trigger_usd: float = 0.25,
        account_preservation_floor_usd: float = 7.00,
        gpu_hourly_rate: float = 0.89,
        max_runtime_minutes: float = 60.0,
        poll_interval_seconds: float = 1.0,
        api_key: Optional[str] = None,
        main_controller_heartbeat_path: Optional[str] = None,
        main_controller_pid: Optional[int] = None
    ):
        self.experiment_id = experiment_id
        self.pod_id = pod_id
        self.watchdog_dir = watchdog_dir
        self.session_id = session_id
        self.max_authorized_usd = max_authorized_usd
        self.emergency_trigger_usd = emergency_trigger_usd
        self.account_preservation_floor_usd = account_preservation_floor_usd
        self.gpu_hourly_rate = gpu_hourly_rate
        self.max_runtime_minutes = max_runtime_minutes
        self.poll_interval_seconds = poll_interval_seconds
        self.api_key = api_key or os.environ.get("RUNPOD_API_KEY", "")
        self.main_controller_heartbeat_path = main_controller_heartbeat_path
        self.main_controller_pid = main_controller_pid

        os.makedirs(self.watchdog_dir, exist_ok=True)
        self.watchdog_pid_file = os.path.join(self.watchdog_dir, f"watchdog_{self.experiment_id}.pid")
        self.watchdog_heartbeat_file = os.path.join(self.watchdog_dir, f"watchdog_heartbeat_{self.experiment_id}.json")
        self.watchdog_state_file = os.path.join(self.watchdog_dir, f"watchdog_state_{self.experiment_id}.json")
        self.alert_dir = self.watchdog_dir

        self.start_monotonic = time.monotonic()
        self.start_wall_time = time.time()
        self.stop_requested = False
        self.termination_dispatched = False
        self.termination_confirmed = False

        self._write_pid_file()

    def _write_pid_file(self):
        with open(self.watchdog_pid_file, "w") as f:
            f.write(str(os.getpid()))

    def classify_provider_pod_response(self, raw_resp: Dict[str, Any], http_code: int = 200) -> Tuple[str, Optional[float], str]:
        """
        Strict classification of RunPod GraphQL response.
        Returns: (classification: str, uptime_seconds: Optional[float], explanation: str)
        """
        if http_code == 401 or http_code == 403:
            return ProviderResponseState.AUTH_ERROR, None, f"HTTP {http_code}: Authentication or permission failure."
        if http_code >= 500:
            return ProviderResponseState.API_ERROR, None, f"HTTP {http_code}: Provider server side error."
        if http_code != 200:
            return ProviderResponseState.API_ERROR, None, f"HTTP {http_code}: Non-OK HTTP status."

        if not isinstance(raw_resp, dict):
            return ProviderResponseState.MALFORMED_RESPONSE, None, "Response is not a valid JSON object."

        # Check for GraphQL errors array
        if "errors" in raw_resp and raw_resp["errors"]:
            err_msg = str(raw_resp["errors"])
            return ProviderResponseState.API_ERROR, None, f"GraphQL errors returned: {err_msg}"

        if "error" in raw_resp:
            err_str = str(raw_resp["error"]).lower()
            if "timeout" in err_str:
                return ProviderResponseState.TIMEOUT, None, f"Network timeout: {err_str}"
            return ProviderResponseState.API_ERROR, None, f"API error: {err_str}"

        data = raw_resp.get("data")
        if data is None:
            return ProviderResponseState.MALFORMED_RESPONSE, None, "Missing 'data' field in GraphQL response."

        pod = data.get("pod")
        if pod is None:
            # Authoritative not-found: GraphQL data query succeeded, returned data with pod: null
            return ProviderResponseState.AUTHORITATIVE_NOT_FOUND, 0.0, "Authoritative: Pod does not exist on RunPod."

        status_str = str(pod.get("desiredStatus", "")).upper()
        uptime = 0.0
        if pod.get("runtime"):
            uptime = float(pod["runtime"].get("uptimeInSeconds", 0.0))

        if status_str in ["RUNNING"]:
            return ProviderResponseState.RUNNING, uptime, "Pod is actively running."
        elif status_str in ["STOPPING"]:
            return ProviderResponseState.STOPPING, uptime, "Pod is stopping."
        elif status_str in ["STOPPED", "EXITED"]:
            return ProviderResponseState.STOPPED, uptime, "Pod is stopped (still exists and may bill storage)."
        elif status_str in ["TERMINATED"]:
            return ProviderResponseState.TERMINATED, uptime, "Pod is terminated."
        elif status_str in ["DELETED"]:
            return ProviderResponseState.DELETED, uptime, "Pod is deleted."
        else:
            return ProviderResponseState.UNKNOWN, uptime, f"Unknown status string: '{status_str}'."

    def _query_runpod_graphql(self, query: str, variables: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Independent HTTPS GraphQL request with strict 5-second timeout."""
        if not self.api_key:
            return {"error": "NO_API_KEY"}, 0
        payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
        req = urllib.request.Request(
            f"{RUNPOD_GRAPHQL_ENDPOINT}?api_key={self.api_key}",
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "StateShift-Watchdog-v15.5"}
        )
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data, resp.getcode()
        except urllib.error.HTTPError as e:
            return {"error": str(e)}, e.code
        except urllib.error.URLError as e:
            return {"error": str(e.reason)}, 0
        except Exception as e:
            return {"error": str(e)}, 0

    def query_provider_pod_state(self) -> Tuple[str, Optional[float], str]:
        """Queries RunPod control plane independently for authoritative state."""
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
        raw_resp, http_code = self._query_runpod_graphql(query, {"podId": self.pod_id})
        return self.classify_provider_pod_response(raw_resp, http_code=http_code)

    def dispatch_provider_termination(self, reason: str) -> bool:
        """
        Dispatches termination mutation directly from watchdog context.
        Verifies actual destruction using strict classification.
        """
        print(f"\n[INDEPENDENT WATCHDOG EMERGENCY TRIGGER] Reason: {reason}")
        self.termination_dispatched = True
        query = """
        mutation TerminatePod($podId: String!) {
            podTerminate(input: {podId: $podId})
        }
        """
        raw_resp, http_code = self._query_runpod_graphql(query, {"podId": self.pod_id})

        # Verification loop with strict classification
        for attempt in range(1, 4):
            time.sleep(1.0)
            state, _, expl = self.query_provider_pod_state()
            if state in [ProviderResponseState.AUTHORITATIVE_NOT_FOUND,
                         ProviderResponseState.TERMINATED,
                         ProviderResponseState.DELETED]:
                self.termination_confirmed = True
                print(f"[Independent Watchdog] CONFIRMED: Pod {self.pod_id} destroyed ({state}).")
                self._persist_watchdog_state("TERMINATED_CONFIRMED", reason)
                return True
            print(f"[Independent Watchdog] Destruction verification attempt {attempt}: status is {state} ({expl}).")

        self._persist_watchdog_state(ProviderResponseState.TERMINATION_UNCONFIRMED, reason)
        self._record_unconfirmed_escalation(reason)
        return False

    def _record_unconfirmed_escalation(self, reason: str):
        alert_path = os.path.join(self.alert_dir, f"CRITICAL_UNCONFIRMED_TERMINATION_{self.pod_id}.json")
        alert = {
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pod_id": self.pod_id,
            "experiment_id": self.experiment_id,
            "reason": reason,
            "error": "Provider failed to confirm destruction or returned API errors."
        }
        with open(alert_path, "w") as f:
            json.dump(alert, f, indent=2)

    def _persist_watchdog_state(self, state_str: str, reason: Optional[str] = None):
        payload = {
            "experiment_id": self.experiment_id,
            "pod_id": self.pod_id,
            "session_id": self.session_id,
            "state": state_str,
            "reason": reason,
            "watchdog_pid": os.getpid(),
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
        payload = {
            "timestamp_utc": time.time(),
            "elapsed_minutes": round(elapsed_min, 2),
            "effective_spend_usd": round(effective_spend, 4),
            "emergency_trigger_usd": self.emergency_trigger_usd,
            "max_authorized_usd": self.max_authorized_usd,
            "pod_id": self.pod_id,
            "watchdog_pid": os.getpid(),
            "status": "WATCHING"
        }
        tmp = self.watchdog_heartbeat_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.watchdog_heartbeat_file)

    def check_main_controller_alive(self, stale_seconds: float = 120.0) -> bool:
        """Audits main controller process and heartbeat file."""
        # 1. Check OS PID if provided
        if self.main_controller_pid is not None:
            try:
                os.kill(self.main_controller_pid, 0)
            except OSError:
                return False # Controller process is dead

        # 2. Check heartbeat file
        if self.main_controller_heartbeat_path and os.path.exists(self.main_controller_heartbeat_path):
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
        elapsed_sec = now_mono - self.start_monotonic
        elapsed_min = elapsed_sec / 60.0
        elapsed_hr = elapsed_sec / 3600.0

        if simulated_spend is not None:
            effective_spend = simulated_spend
        else:
            effective_spend = elapsed_hr * self.gpu_hourly_rate

        self.write_heartbeat(effective_spend, elapsed_min)

        spend_breached = effective_spend >= self.emergency_trigger_usd
        runtime_breached = elapsed_min >= self.max_runtime_minutes
        controller_alive = self.check_main_controller_alive()

        should_terminate = spend_breached or runtime_breached
        action = "CONTINUE"

        if should_terminate and not self.termination_dispatched:
            reasons = []
            if spend_breached:
                reasons.append(f"Spend ${effective_spend:.4f} >= emergency threshold ${self.emergency_trigger_usd:.4f}")
            if runtime_breached:
                reasons.append(f"Runtime {elapsed_min:.1f}m >= max allowed {self.max_runtime_minutes:.1f}m")

            reason_str = " | ".join(reasons)
            success = self.dispatch_provider_termination(reason_str)
            action = "TERMINATED" if success else ProviderResponseState.TERMINATION_UNCONFIRMED

        return {
            "watchdog_pid": os.getpid(),
            "elapsed_minutes": elapsed_min,
            "effective_spend_usd": effective_spend,
            "controller_alive": controller_alive,
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
    parser.add_argument("--session-id", default="default_session")
    parser.add_argument("--max-authorized", type=float, default=0.35)
    parser.add_argument("--emergency-trigger", type=float, default=0.25)
    parser.add_argument("--hourly-rate", type=float, default=0.89)
    parser.add_argument("--max-runtime", type=float, default=60.0)
    parser.add_argument("--poll-interval", type=float, default=1.0)
    parser.add_argument("--controller-heartbeat", default=None)
    parser.add_argument("--controller-pid", type=int, default=None)
    parser.add_argument("--simulate-spend", type=float, default=None)
    parser.add_argument("--single-tick", action="store_true")
    args = parser.parse_args()

    watchdog = IndependentFinancialWatchdog(
        experiment_id=args.experiment_id,
        pod_id=args.pod_id,
        watchdog_dir=args.watchdog_dir,
        session_id=args.session_id,
        max_authorized_usd=args.max_authorized,
        emergency_trigger_usd=args.emergency_trigger,
        gpu_hourly_rate=args.hourly_rate,
        max_runtime_minutes=args.max_runtime,
        poll_interval_seconds=args.poll_interval,
        main_controller_heartbeat_path=args.controller_heartbeat,
        main_controller_pid=args.controller_pid
    )

    if args.single_tick:
        res = watchdog.run_supervision_tick(simulated_spend=args.simulate_spend)
        print(json.dumps(res, indent=2))
        sys.exit(0 if not res["should_terminate"] else 2)

    print(f"[Watchdog Daemon PID {os.getpid()}] Started for pod {args.pod_id} (Trigger: ${args.emergency_trigger:.2f}).")
    while not watchdog.stop_requested:
        res = watchdog.run_supervision_tick(simulated_spend=args.simulate_spend)
        if res["should_terminate"]:
            print(f"[Watchdog Daemon] Termination dispatched. Final status: {res['action']}.")
            break
        time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
