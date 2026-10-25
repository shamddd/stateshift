#!/usr/bin/env python3
"""
StateShift Genuinely Independent Financial Watchdog Daemon (Mission 15.6 Production)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Hardened Financial Watchdog Architecture (Issues A, B, C, D, E):
- Issue A: Immediate emergency termination upon confirmed controller death.
- Issue B: Explicit 8-state lifecycle ownership (NOT_STARTED -> ACTIVE -> ... -> WATCHDOG_EXITED).
- Issue C: Billing accounts for pre-watchdog uptime and conservative elapsed time estimate:
    effective_spend = max(provider_estimated_spend, verified_balance_delta, conservative_elapsed_estimate).
- Issue D: Durable termination retry state machine:
    TERMINATION_NOT_REQUESTED -> TERMINATION_REQUEST_ATTEMPTED -> TERMINATION_ACKNOWLEDGED ->
    TERMINATION_UNCONFIRMED -> TERMINATION_CONFIRMED.
- Issue E: Independent verification of signed cryptographic authorization document.
"""

import os
import sys
import time
import json
import enum
import urllib.request
import urllib.error
import argparse
from typing import Dict, Any, Tuple, Optional

# Ensure repository root is in sys.path
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# Constants
RUNPOD_GRAPHQL_ENDPOINT = "https://api.runpod.io/graphql"


class WatchdogLifecycleState(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    STARTING = "STARTING"
    ACTIVE = "ACTIVE"
    CONTROLLER_FAILED = "CONTROLLER_FAILED"
    TERMINATION_REQUESTED = "TERMINATION_REQUESTED"
    TERMINATION_UNCONFIRMED = "TERMINATION_UNCONFIRMED"
    TERMINATION_CONFIRMED = "TERMINATION_CONFIRMED"
    WATCHDOG_EXITED = "WATCHDOG_EXITED"


class TerminationDurableState(str, enum.Enum):
    TERMINATION_NOT_REQUESTED = "TERMINATION_NOT_REQUESTED"
    TERMINATION_REQUEST_ATTEMPTED = "TERMINATION_REQUEST_ATTEMPTED"
    TERMINATION_ACKNOWLEDGED = "TERMINATION_ACKNOWLEDGED"
    TERMINATION_UNCONFIRMED = "TERMINATION_UNCONFIRMED"
    TERMINATION_CONFIRMED = "TERMINATION_CONFIRMED"


class ProviderResponseState:
    CONFIRMED_TERMINATED = "CONFIRMED_TERMINATED"
    CONFIRMED_ACTIVE = "CONFIRMED_ACTIVE"
    API_ERROR = "API_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    TIMEOUT = "TIMEOUT"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    AUTHORITATIVE_NOT_FOUND = "AUTHORITATIVE_NOT_FOUND"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    STOPPING = "STOPPING"
    TERMINATED = "TERMINATED"
    DELETED = "DELETED"
    UNKNOWN = "UNKNOWN"
    TERMINATION_UNCONFIRMED = "TERMINATION_UNCONFIRMED"


class IndependentFinancialWatchdog:
    def __init__(
        self,
        experiment_id: str,
        pod_id: str,
        watchdog_dir: str,
        session_id: str = "default_session",
        authorization_path: Optional[str] = None,
        trusted_public_key_b64: Optional[str] = None,
        allow_test_key_for_testing: bool = False,
        max_authorized_usd: float = 0.35,
        emergency_trigger_usd: float = 0.25,
        account_preservation_floor_usd: float = 7.00,
        gpu_hourly_rate: float = 0.89,
        max_runtime_minutes: float = 60.0,
        poll_interval_seconds: float = 1.0,
        api_key: Optional[str] = None,
        main_controller_heartbeat_path: Optional[str] = None,
        main_controller_pid: Optional[int] = None,
        pre_existing_uptime_seconds: float = 0.0,
        initial_account_balance: Optional[float] = None
    ):
        self.experiment_id = experiment_id
        self.pod_id = pod_id
        self.watchdog_dir = os.path.abspath(watchdog_dir)
        self.session_id = session_id
        self.authorization_path = authorization_path
        self.trusted_public_key_b64 = trusted_public_key_b64
        self.allow_test_key_for_testing = allow_test_key_for_testing
        
        self.max_authorized_usd = max_authorized_usd
        self.emergency_trigger_usd = emergency_trigger_usd
        self.account_preservation_floor_usd = account_preservation_floor_usd
        self.gpu_hourly_rate = gpu_hourly_rate
        self.reported_gpu_hourly_rate: Optional[float] = None
        self.max_runtime_minutes = max_runtime_minutes
        self.poll_interval_seconds = poll_interval_seconds
        self.api_key = api_key or os.environ.get("RUNPOD_API_KEY", "")
        self.main_controller_heartbeat_path = main_controller_heartbeat_path
        self.main_controller_pid = main_controller_pid
        self.pre_existing_uptime_seconds = float(pre_existing_uptime_seconds)
        self.initial_account_balance = initial_account_balance

        os.makedirs(self.watchdog_dir, exist_ok=True)
        self.watchdog_pid_file = os.path.join(self.watchdog_dir, f"watchdog_{self.experiment_id}.pid")
        self.watchdog_heartbeat_file = os.path.join(self.watchdog_dir, f"watchdog_heartbeat_{self.experiment_id}.json")
        self.watchdog_state_file = os.path.join(self.watchdog_dir, f"watchdog_state_{self.experiment_id}.json")
        self.readiness_receipt_path = os.path.join(self.watchdog_dir, f"watchdog_readiness_{self.experiment_id}_{self.session_id}.json")
        self.alert_dir = os.path.join(self.watchdog_dir, "termination_alerts")
        os.makedirs(self.alert_dir, exist_ok=True)

        self.start_monotonic = time.monotonic()
        self.start_wall_time = time.time()
        self.stop_requested = False
        
        # State tracking
        self.lifecycle_state = WatchdogLifecycleState.STARTING
        self.termination_state = TerminationDurableState.TERMINATION_NOT_REQUESTED
        self.termination_dispatched = False
        self.termination_confirmed = False
        self.termination_receipt_path: Optional[str] = None
        
        # Issue E: Independently verify cryptographic authorization if supplied
        if self.authorization_path:
            self._verify_authorization_independently()

        # Defect 1: Establish verified financial baseline & check preservation floor
        baseline_ok, baseline_msg = self.establish_financial_baseline()
        if not baseline_ok:
            self.lifecycle_state = WatchdogLifecycleState.CONTROLLER_FAILED
            self._persist_watchdog_state("BASELINE_FAILED", baseline_msg)
            raise PermissionError(f"[Watchdog Financial Baseline Refused] {baseline_msg}")

        self._write_pid_file()
        self.lifecycle_state = WatchdogLifecycleState.ACTIVE
        self._persist_watchdog_state("WATCHDOG_ACTIVE")

        # Defect 2: Publish atomic readiness receipt for startup handshake
        self.publish_readiness_receipt()

    def _verify_authorization_independently(self):
        """Issue E: Cryptographically verify authorization directly inside watchdog."""
        if not os.path.exists(self.authorization_path):
            raise FileNotFoundError(f"[Watchdog Independent Auth Verification Failed] Authorization file not found: {self.authorization_path}")

        with open(self.authorization_path, "r", encoding="utf-8") as f:
            auth_doc = json.load(f)

        from research_mission_15_6.auth.session_authorizer_v2 import CryptographicAuthorizer, FROZEN_MANIFEST_SHA256
        authorizer = CryptographicAuthorizer(
            trusted_public_key_b64=self.trusted_public_key_b64,
            allow_test_key_for_testing=self.allow_test_key_for_testing
        )
        
        payload = auth_doc.get("payload", {})
        active_mode = payload.get("authorized_mode", "CALIBRATION")
        is_valid, msg = authorizer.verify_authorization(
            auth_doc=auth_doc,
            active_experiment_id=self.experiment_id,
            active_pod_id=self.pod_id,
            active_manifest_sha256=FROZEN_MANIFEST_SHA256,
            active_mode=active_mode
        )
        if not is_valid:
            raise PermissionError(f"[Watchdog Independent Auth Verification Failed] {msg}")

        # Check exact bindings
        if payload.get("pod_id") != self.pod_id:
            raise ValueError(
                f"[Watchdog Auth Tamper] Authorized pod_id '{payload.get('pod_id')}' != watchdog pod_id '{self.pod_id}'"
            )
        if payload.get("experiment_id") != self.experiment_id:
            raise ValueError(
                f"[Watchdog Auth Tamper] Authorized exp_id '{payload.get('experiment_id')}' != watchdog exp_id '{self.experiment_id}'"
            )
        
        # Authoritative threshold adoption directly from verified signature
        auth_max = float(payload.get("max_incremental_spend_usd", self.max_authorized_usd))
        auth_trig = float(payload.get("emergency_trigger_usd", self.emergency_trigger_usd))
        
        # Never permit CLI args to exceed signed bounds
        self.max_authorized_usd = min(self.max_authorized_usd, auth_max)
        self.emergency_trigger_usd = min(self.emergency_trigger_usd, auth_trig)
        self.account_preservation_floor_usd = float(payload.get("minimum_account_balance_usd", self.account_preservation_floor_usd))
        self.verified_authorization_payload = payload

    def _write_pid_file(self):
        with open(self.watchdog_pid_file, "w") as f:
            f.write(str(os.getpid()))

    def classify_provider_pod_response(self, raw_resp: Dict[str, Any], http_code: int = 200) -> Tuple[str, Optional[float], str]:
        """Strict classification of RunPod GraphQL response."""
        if http_code in [401, 403]:
            return ProviderResponseState.AUTH_ERROR, None, f"Authentication error (HTTP {http_code})"
        if http_code in [500, 502, 503, 504]:
            return ProviderResponseState.API_ERROR, None, f"Server error (HTTP {http_code})"
        if http_code != 200:
            return ProviderResponseState.API_ERROR, None, f"Unexpected HTTP status {http_code}"

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
            return ProviderResponseState.AUTHORITATIVE_NOT_FOUND, 0.0, "Authoritative: Pod does not exist on RunPod."

        status_str = str(pod.get("desiredStatus", "")).upper()
        uptime = 0.0
        if pod.get("runtime"):
            uptime = float(pod["runtime"].get("uptimeInSeconds", 0.0))

        cost_per_hr = pod.get("costPerHr")
        if cost_per_hr is not None:
            try:
                self.reported_gpu_hourly_rate = float(cost_per_hr)
            except (ValueError, TypeError):
                pass

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
        if not self.api_key:
            return {"error": "NO_API_KEY"}, 0
        payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
        req = urllib.request.Request(
            f"{RUNPOD_GRAPHQL_ENDPOINT}?api_key={self.api_key}",
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "StateShift-Watchdog-v15.6"}
        )
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=15.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data, resp.getcode()
            except urllib.error.HTTPError as e:
                return {"error": str(e)}, e.code
            except Exception as e:
                if attempt == 1:
                    return {"error": str(e)}, 0
                time.sleep(1.0)
        return {"error": "TIMEOUT"}, 0

    def query_provider_pod_state(self) -> Tuple[str, Optional[float], str]:
        query = """
        query Pod($podId: String!) {
            pod(input: {podId: $podId}) {
                id
                desiredStatus
                costPerHr
                runtime {
                    uptimeInSeconds
                }
            }
        }
        """
        raw_resp, http_code = self._query_runpod_graphql(query, {"podId": self.pod_id})
        return self.classify_provider_pod_response(raw_resp, http_code=http_code)

    def query_account_balance(self) -> Tuple[Optional[float], str]:
        """Defect 1: Live query to RunPod account balance endpoint."""
        if not self.api_key:
            return None, "NO_API_KEY"
        query = """
        query AccountBalance {
            myself {
                id
                clientBalance
            }
        }
        """
        raw_resp, http_code = self._query_runpod_graphql(query, {})
        if http_code != 200:
            return None, f"HTTP error {http_code}"
        if "errors" in raw_resp and raw_resp["errors"]:
            return None, f"GraphQL errors: {raw_resp['errors']}"
        if "error" in raw_resp:
            return None, f"API error: {raw_resp['error']}"
        data = raw_resp.get("data")
        if not data or "myself" not in data or data["myself"] is None:
            return None, "Missing 'myself' in GraphQL response"
        bal = data["myself"].get("clientBalance")
        if bal is None:
            return None, "Missing 'clientBalance' field in myself object"
        try:
            return float(bal), "Success"
        except (ValueError, TypeError) as e:
            return None, f"Malformed clientBalance value: {e}"

    def establish_financial_baseline(self) -> Tuple[bool, str]:
        """
        Defect 1: Establishes initial financial baseline and enforces preservation floor ($7.00 USD).
        """
        if self.initial_account_balance is not None:
            if self.initial_account_balance <= self.account_preservation_floor_usd:
                return False, f"Initial balance ${self.initial_account_balance:.4f} <= preservation floor ${self.account_preservation_floor_usd:.4f}"
            return True, f"Baseline established from initial balance: ${self.initial_account_balance:.4f}"

        if not self.api_key:
            return True, "Mock baseline established (no RunPod API key configured)"

        bal, msg = self.query_account_balance()
        if bal is not None:
            self.initial_account_balance = bal
            if bal <= self.account_preservation_floor_usd:
                return False, f"Current balance ${bal:.4f} <= preservation floor ${self.account_preservation_floor_usd:.4f}"
            return True, f"Live baseline established: ${bal:.4f}"

        if self.allow_test_key_for_testing:
            return True, f"Test mode baseline established without live balance: {msg}"

        return False, f"Failed to retrieve account balance: {msg}"

    def publish_readiness_receipt(self) -> str:
        """Defect 2: Publish atomic readiness receipt for controller verification."""
        receipt = {
            "status": "READY",
            "lifecycle_state": self.lifecycle_state.value,
            "watchdog_pid": os.getpid(),
            "experiment_id": self.experiment_id,
            "pod_id": self.pod_id,
            "session_id": self.session_id,
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "max_authorized_usd": self.max_authorized_usd,
            "emergency_trigger_usd": self.emergency_trigger_usd,
            "account_preservation_floor_usd": self.account_preservation_floor_usd,
            "initial_account_balance": self.initial_account_balance,
            "pre_existing_uptime_seconds": self.pre_existing_uptime_seconds,
            "gpu_hourly_rate": self.gpu_hourly_rate,
            "reported_gpu_hourly_rate": self.reported_gpu_hourly_rate
        }
        tmp = self.readiness_receipt_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.readiness_receipt_path)
        return self.readiness_receipt_path

    def calculate_effective_spend(
        self,
        simulated_spend: Optional[float] = None,
        provider_uptime_seconds: Optional[float] = None,
        current_account_balance: Optional[float] = None
    ) -> float:
        """
        Defect 1 & Issue C: Reconciled, conservative financial baseline accounting:
        effective_spend = max(provider_estimated_spend, verified_balance_delta, conservative_elapsed_estimate).
        Uses max(configured_hourly_rate, reported_gpu_hourly_rate).
        Includes pre_existing_uptime_seconds so clock never restarts at zero.
        """
        if simulated_spend is not None:
            return float(simulated_spend)

        effective_rate = max(self.gpu_hourly_rate, self.reported_gpu_hourly_rate or 0.0)

        # 1. Conservative elapsed time estimate
        now_mono = time.monotonic()
        watchdog_elapsed_sec = max(0.0, now_mono - self.start_monotonic)
        total_conservative_uptime_sec = self.pre_existing_uptime_seconds + watchdog_elapsed_sec
        conservative_elapsed_estimate = (total_conservative_uptime_sec / 3600.0) * effective_rate

        # 2. Provider estimated spend
        provider_estimated_spend = 0.0
        if provider_uptime_seconds is not None and provider_uptime_seconds > 0:
            provider_estimated_spend = (provider_uptime_seconds / 3600.0) * effective_rate

        # 3. Verified account balance delta
        verified_balance_delta = 0.0
        if current_account_balance is not None and self.initial_account_balance is not None:
            verified_balance_delta = max(0.0, self.initial_account_balance - current_account_balance)

        return max(provider_estimated_spend, verified_balance_delta, conservative_elapsed_estimate)

    def dispatch_provider_termination(self, reason: str, max_retries: int = 5) -> bool:
        """
        Issues C & D: Durable termination retry state machine:
        TERMINATION_REQUEST_ATTEMPTED -> TERMINATION_ACKNOWLEDGED ->
        TERMINATION_UNCONFIRMED -> TERMINATION_CONFIRMED.
        """
        print(f"\n[INDEPENDENT WATCHDOG EMERGENCY TRIGGER] Reason: {reason}")
        self.termination_dispatched = True
        self.lifecycle_state = WatchdogLifecycleState.TERMINATION_REQUESTED
        self.termination_state = TerminationDurableState.TERMINATION_REQUEST_ATTEMPTED
        self._persist_watchdog_state("TERMINATION_REQUEST_ATTEMPTED", reason)

        query = """
        mutation TerminatePod($podId: String!) {
            podTerminate(input: {podId: $podId})
        }
        """
        raw_resp, http_code = self._query_runpod_graphql(query, {"podId": self.pod_id})
        if http_code == 200 and not raw_resp.get("errors"):
            self.termination_state = TerminationDurableState.TERMINATION_ACKNOWLEDGED
            self._persist_watchdog_state("TERMINATION_ACKNOWLEDGED", reason)

        # Bounded durable retry loop with exponential backoff
        backoff = 1.0
        for attempt in range(1, max_retries + 1):
            time.sleep(backoff)
            state, _, expl = self.query_provider_pod_state()
            if state in [
                ProviderResponseState.AUTHORITATIVE_NOT_FOUND,
                ProviderResponseState.TERMINATED,
                ProviderResponseState.DELETED
            ]:
                self.termination_confirmed = True
                self.termination_state = TerminationDurableState.TERMINATION_CONFIRMED
                self.lifecycle_state = WatchdogLifecycleState.TERMINATION_CONFIRMED
                print(f"[Independent Watchdog] CONFIRMED: Pod {self.pod_id} destroyed ({state}).")
                receipt = self._persist_final_receipt(reason, confirmed=True, attempts=attempt)
                self._persist_watchdog_state("TERMINATION_CONFIRMED", reason)
                return True

            print(f"[Independent Watchdog] Verification attempt {attempt}/{max_retries}: {state} ({expl}). Retrying...")
            backoff = min(backoff * 1.5, 5.0)

        # If not confirmed after retries, persist UNCONFIRMED alert but DO NOT falsely claim destruction
        self.termination_confirmed = False
        self.termination_state = TerminationDurableState.TERMINATION_UNCONFIRMED
        self.lifecycle_state = WatchdogLifecycleState.TERMINATION_UNCONFIRMED
        self._persist_final_receipt(reason, confirmed=False, attempts=max_retries)
        self._persist_watchdog_state("TERMINATION_UNCONFIRMED", reason)
        self._record_unconfirmed_escalation(reason, attempts=max_retries)
        return False

    def _persist_final_receipt(self, reason: str, confirmed: bool, attempts: int) -> str:
        receipt_file = os.path.join(self.watchdog_dir, f"watchdog_termination_receipt_{self.experiment_id}.json")
        receipt = {
            "experiment_id": self.experiment_id,
            "pod_id": self.pod_id,
            "session_id": self.session_id,
            "watchdog_pid": os.getpid(),
            "reason": reason,
            "confirmed_by_provider": confirmed,
            "termination_durable_state": self.termination_state.value,
            "verification_attempts": attempts,
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        with open(receipt_file, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)
        self.termination_receipt_path = receipt_file
        return receipt_file

    def _record_unconfirmed_escalation(self, reason: str, attempts: int = 5):
        alert_path = os.path.join(self.alert_dir, f"CRITICAL_UNCONFIRMED_TERMINATION_{self.pod_id}.json")
        alert = {
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pod_id": self.pod_id,
            "experiment_id": self.experiment_id,
            "session_id": self.session_id,
            "attempts": attempts,
            "reason": reason,
            "error": "Provider failed to confirm destruction or returned API errors. Operational escalation required."
        }
        with open(alert_path, "w") as f:
            json.dump(alert, f, indent=2)

    def _persist_watchdog_state(self, state_str: str, reason: Optional[str] = None):
        payload = {
            "experiment_id": self.experiment_id,
            "pod_id": self.pod_id,
            "session_id": self.session_id,
            "state": state_str,
            "lifecycle_state": self.lifecycle_state.value,
            "termination_durable_state": self.termination_state.value,
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
            "lifecycle_state": self.lifecycle_state.value,
            "status": "WATCHING"
        }
        tmp = self.watchdog_heartbeat_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.watchdog_heartbeat_file)

    def evaluate_controller_status(self, stale_seconds: float = 30.0) -> Tuple[str, str]:
        """
        Issue A: Distinguishes:
        - NORMAL: Controller process alive, heartbeat recent.
        - STALE_HEARTBEAT: Process alive but heartbeat hasn't updated.
        - CONFIRMED_DEAD: OS PID dead (ESRCH), emergency termination required!
        - CLEAN_EXIT_CONFIRMED: Controller exited intentionally after verified termination.
        """
        # 1. Check if controller intentionally finished with verified termination
        if self.main_controller_heartbeat_path and os.path.exists(self.main_controller_heartbeat_path):
            try:
                with open(self.main_controller_heartbeat_path, "r", encoding="utf-8") as f:
                    c_data = json.load(f)
                    c_state = str(c_data.get("state", "")).upper()
                    if c_state in ["PROVIDER_TERMINATION_CONFIRMED", "FINISHED", "LOCAL_VERIFIED"]:
                        return "CLEAN_EXIT_CONFIRMED", f"Controller completed normal termination ({c_state})"
            except Exception:
                pass

        # 2. Check OS process status via kill(0)
        if self.main_controller_pid is not None:
            try:
                os.kill(self.main_controller_pid, 0)
            except OSError as e:
                # Process dead (e.g. SIGKILL, crash)
                return "CONFIRMED_DEAD", f"Controller process {self.main_controller_pid} is confirmed dead: {e}"

        # 3. Check heartbeat freshness
        if self.main_controller_heartbeat_path and os.path.exists(self.main_controller_heartbeat_path):
            try:
                with open(self.main_controller_heartbeat_path, "r", encoding="utf-8") as f:
                    c_data = json.load(f)
                    ts = c_data.get("timestamp_utc", 0.0)
                    if (time.time() - ts) > stale_seconds:
                        return "STALE_HEARTBEAT", f"Controller heartbeat stale (>{stale_seconds}s)"
            except Exception:
                pass

        return "NORMAL", "Controller operational"

    def run_supervision_tick(
        self,
        simulated_spend: Optional[float] = None,
        provider_uptime_seconds: Optional[float] = None,
        current_account_balance: Optional[float] = None
    ) -> Dict[str, Any]:
        """Single independent watchdog evaluation tick with Issues A-E active."""
        now_mono = time.monotonic()
        watchdog_elapsed_sec = now_mono - self.start_monotonic
        watchdog_elapsed_min = watchdog_elapsed_sec / 60.0

        effective_spend = self.calculate_effective_spend(
            simulated_spend=simulated_spend,
            provider_uptime_seconds=provider_uptime_seconds,
            current_account_balance=current_account_balance
        )

        self.write_heartbeat(effective_spend, watchdog_elapsed_min)

        # Spend, runtime, and preservation floor checks
        spend_breached = effective_spend >= self.emergency_trigger_usd
        runtime_breached = watchdog_elapsed_min >= self.max_runtime_minutes
        floor_breached = (current_account_balance is not None and current_account_balance <= self.account_preservation_floor_usd)
        
        # Issue A: Controller death evaluation
        ctrl_status, ctrl_expl = self.evaluate_controller_status()
        controller_dead = (ctrl_status == "CONFIRMED_DEAD")

        should_terminate = spend_breached or runtime_breached or controller_dead or floor_breached
        action = "CONTINUE"

        if ctrl_status == "CLEAN_EXIT_CONFIRMED" and not self.termination_dispatched:
            # Controller exited normally after pod was confirmed dead
            self.stop_requested = True
            self.lifecycle_state = WatchdogLifecycleState.WATCHDOG_EXITED
            self._persist_watchdog_state("WATCHDOG_EXITED", "Controller clean exit after verified termination")
            return {
                "watchdog_pid": os.getpid(),
                "should_terminate": False,
                "action": "CLEAN_SHUTDOWN",
                "termination_dispatched": False,
                "termination_confirmed": True
            }

        if should_terminate and not self.termination_dispatched:
            reasons = []
            if controller_dead:
                self.lifecycle_state = WatchdogLifecycleState.CONTROLLER_FAILED
                reasons.append(f"Controller confirmed dead ({ctrl_expl})")
            if floor_breached:
                reasons.append(f"Account preservation floor breached: balance ${current_account_balance:.4f} <= ${self.account_preservation_floor_usd:.4f}")
            if spend_breached:
                reasons.append(f"Spend ${effective_spend:.4f} >= emergency trigger ${self.emergency_trigger_usd:.4f}")
            if runtime_breached:
                reasons.append(f"Runtime {watchdog_elapsed_min:.1f}m >= max allowed {self.max_runtime_minutes:.1f}m")

            reason_str = " | ".join(reasons)
            success = self.dispatch_provider_termination(reason_str)
            action = "TERMINATED" if success else ProviderResponseState.TERMINATION_UNCONFIRMED

        return {
            "watchdog_pid": os.getpid(),
            "elapsed_minutes": watchdog_elapsed_min,
            "effective_spend_usd": effective_spend,
            "controller_status": ctrl_status,
            "controller_explanation": ctrl_expl,
            "should_terminate": should_terminate,
            "action": action,
            "lifecycle_state": self.lifecycle_state.value,
            "termination_durable_state": self.termination_state.value,
            "termination_dispatched": self.termination_dispatched,
            "termination_confirmed": self.termination_confirmed
        }


def main():
    parser = argparse.ArgumentParser(description="StateShift Independent Financial Watchdog Daemon (Mission 15.6)")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--pod-id", required=True)
    parser.add_argument("--watchdog-dir", default="data/primary_run/watchdog")
    parser.add_argument("--session-id", default="default_session")
    parser.add_argument("--authorization", default=None, help="Path to signed cryptographic authorization document")
    parser.add_argument("--trusted-public-key", default=None, help="Base64-encoded PI public key")
    parser.add_argument("--allow-test-key", action="store_true")
    parser.add_argument("--max-authorized", type=float, default=0.35)
    parser.add_argument("--emergency-trigger", type=float, default=0.25)
    parser.add_argument("--hourly-rate", type=float, default=0.89)
    parser.add_argument("--max-runtime", type=float, default=60.0)
    parser.add_argument("--poll-interval", type=float, default=1.0)
    parser.add_argument("--controller-heartbeat", default=None)
    parser.add_argument("--controller-pid", type=int, default=None)
    parser.add_argument("--pre-existing-uptime", type=float, default=0.0)
    parser.add_argument("--initial-balance", type=float, default=None)
    parser.add_argument("--simulate-spend", type=float, default=None)
    parser.add_argument("--single-tick", action="store_true")
    args = parser.parse_args()

    watchdog = IndependentFinancialWatchdog(
        experiment_id=args.experiment_id,
        pod_id=args.pod_id,
        watchdog_dir=args.watchdog_dir,
        session_id=args.session_id,
        authorization_path=args.authorization,
        trusted_public_key_b64=args.trusted_public_key,
        allow_test_key_for_testing=args.allow_test_key,
        max_authorized_usd=args.max_authorized,
        emergency_trigger_usd=args.emergency_trigger,
        gpu_hourly_rate=args.hourly_rate,
        max_runtime_minutes=args.max_runtime,
        poll_interval_seconds=args.poll_interval,
        main_controller_heartbeat_path=args.controller_heartbeat,
        main_controller_pid=args.controller_pid,
        pre_existing_uptime_seconds=args.pre_existing_uptime,
        initial_account_balance=args.initial_balance
    )

    if args.single_tick:
        res = watchdog.run_supervision_tick(simulated_spend=args.simulate_spend)
        print(json.dumps(res, indent=2))
        sys.exit(0 if not res["should_terminate"] else 2)

    print(f"[Watchdog Daemon PID {os.getpid()}] Started for pod {args.pod_id} (Trigger: ${watchdog.emergency_trigger_usd:.2f}).")
    while not watchdog.stop_requested:
        # 1. Operator handoff check
        handoff_path = os.path.join(watchdog.watchdog_dir, f"operator_handoff_{watchdog.pod_id}.json")
        if os.path.exists(handoff_path):
            print(f"[Watchdog Daemon] Operator handoff file detected at {handoff_path}. Relinquishing supervision.")
            watchdog.lifecycle_state = WatchdogLifecycleState.WATCHDOG_EXITED
            watchdog._persist_watchdog_state("OPERATOR_HANDOFF_ACCEPTED", "Operator assumed manual pod ownership")
            break

        # 2. Live telemetry ingestion
        live_uptime = None
        live_balance = None
        if args.simulate_spend is None and watchdog.api_key:
            try:
                st, up, _ = watchdog.query_provider_pod_state()
                live_uptime = up
                if watchdog.termination_state == TerminationDurableState.TERMINATION_UNCONFIRMED:
                    if st in [ProviderResponseState.AUTHORITATIVE_NOT_FOUND, ProviderResponseState.TERMINATED, ProviderResponseState.DELETED]:
                        print(f"[Watchdog Daemon] Reconciliation confirmed: Pod {watchdog.pod_id} destroyed ({st}).")
                        watchdog.termination_confirmed = True
                        watchdog.termination_state = TerminationDurableState.TERMINATION_CONFIRMED
                        watchdog.lifecycle_state = WatchdogLifecycleState.TERMINATION_CONFIRMED
                        watchdog._persist_final_receipt("Background reconciliation confirmed destruction", confirmed=True, attempts=1)
                        watchdog._persist_watchdog_state("TERMINATION_CONFIRMED", "Reconciliation successful")
                        break
            except Exception:
                pass

            try:
                bal, _ = watchdog.query_account_balance()
                live_balance = bal
            except Exception:
                pass

        res = watchdog.run_supervision_tick(
            simulated_spend=args.simulate_spend,
            provider_uptime_seconds=live_uptime,
            current_account_balance=live_balance
        )
        if res["should_terminate"]:
            if watchdog.termination_confirmed:
                print(f"[Watchdog Daemon] Termination confirmed. Final status: {res['action']}.")
                break
            elif watchdog.termination_state == TerminationDurableState.TERMINATION_UNCONFIRMED:
                print(f"[Watchdog Daemon] Termination UNCONFIRMED. Maintaining supervision for operator protection...")
        time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
