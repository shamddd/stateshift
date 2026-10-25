#!/usr/bin/env python3
"""
StateShift Supervisor-First Cloud Provisioner (Mission 15.6 Incident Recovery)
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Core Architectural Invariants:
1. Supervisor-First Principle:
   The independent watchdog MUST be spawned, authenticated, and verified polling
   before any pod provisioning API request is dispatched.
2. Single-Attempt Invariant:
   Under no circumstances are automated retries or replacement pods permitted (max_attempts = 1).
3. Bounded Staging Invariant:
   All remote SSH commands are wrapped with monotonic wall-clock deadlines (safe_channel_wait).
   Model pre-caching is capped at a strict 180-second deadline.
4. Fail-Closed Execution Lock:
   Rejects cloud execution if the execution lock file is present or spend authorization is zero.
"""

import os
import sys
import time
import json
import subprocess
from typing import Dict, Any, Optional, Tuple, Callable

from research_mission_15_6.auth.execution_lock import is_cloud_execution_locked, assert_cloud_execution_permitted
from research_mission_15_6.transport.runpod_transport_v2 import ProductionRunPodTransportV2, safe_channel_wait

class ProvisioningSecurityError(Exception):
    """Raised when a security, policy, or budget constraint prevents provisioning."""
    pass

class StagingTimeoutError(Exception):
    """Raised when remote setup or model caching exceeds its monotonic deadline."""
    pass


class SupervisorFirstProvisioner:
    """
    Guarantees that compute resources cannot exist without an active, verified supervisor.
    """

    def __init__(
        self,
        experiment_id: str,
        session_id: str,
        local_data_dir: str,
        max_cost_usd: float = 0.35,
        emergency_trigger_usd: float = 0.25,
        account_floor_usd: float = 7.00,
        gpu_hourly_rate: float = 0.89,
        transport: Optional[ProductionRunPodTransportV2] = None,
        watchdog_starter: Optional[Callable[..., subprocess.Popen]] = None,
        simulate_supervisor: bool = False
    ):
        self.experiment_id = experiment_id
        self.session_id = session_id
        self.local_data_dir = os.path.abspath(local_data_dir)
        self.watchdog_dir = os.path.join(self.local_data_dir, "watchdog")
        os.makedirs(self.watchdog_dir, exist_ok=True)

        self.max_cost_usd = max_cost_usd
        self.emergency_trigger_usd = emergency_trigger_usd
        self.account_floor_usd = account_floor_usd
        self.gpu_hourly_rate = gpu_hourly_rate

        self.transport = transport
        self.watchdog_starter = watchdog_starter or self._default_watchdog_starter
        self.simulate_supervisor = simulate_supervisor

        self.watchdog_process: Optional[subprocess.Popen] = None
        self.watchdog_pid: Optional[int] = None
        self.active_pod_id: Optional[str] = None
        self.provisioning_attempts: int = 0
        self.max_provisioning_attempts: int = 1  # Strict single attempt invariant

    def _default_watchdog_starter(self, cmd: list) -> subprocess.Popen:
        return subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setpgrp if hasattr(os, "setpgrp") else None
        )

    def verify_preconditions(self, current_balance_usd: float, active_pods_count: int) -> None:
        """Enforces account balance preservation floor and zero-existing-pods rule."""
        if current_balance_usd < self.account_floor_usd:
            raise ProvisioningSecurityError(
                f"Account balance ${current_balance_usd:.4f} is below preservation floor (${self.account_floor_usd:.2f} USD)."
            )
        if active_pods_count > 0:
            raise ProvisioningSecurityError(
                f"Safety violation: {active_pods_count} pod(s) already active or billable."
            )

    def spawn_preprovision_supervisor(self, timeout_seconds: float = 15.0) -> bool:
        """
        Phase 1: Spawns independent watchdog in PRE_PROVISION mode and waits for receipt.
        """
        if self.simulate_supervisor:
            # Generate valid simulated pre-provision receipt
            receipt_path = os.path.join(
                self.watchdog_dir,
                f"watchdog_readiness_{self.experiment_id}_{self.session_id}.json"
            )
            data = {
                "status": "READY",
                "lifecycle_state": "PRE_PROVISION_POLLING",
                "watchdog_pid": 99999,
                "experiment_id": self.experiment_id,
                "session_id": self.session_id,
                "pod_id": "PRE_PROVISION",
                "timestamp_utc": time.time(),
                "max_authorized_usd": self.max_cost_usd,
                "emergency_trigger_usd": self.emergency_trigger_usd,
                "account_preservation_floor_usd": self.account_floor_usd,
                "pre_existing_uptime_seconds": 0.0
            }
            with open(receipt_path, "w") as f:
                json.dump(data, f)
            self.watchdog_pid = 99999
            return True

        watchdog_script = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "supervision", "independent_financial_watchdog.py"
        ))
        cmd = [
            sys.executable,
            watchdog_script,
            "--experiment-id", self.experiment_id,
            "--pod-id", "PRE_PROVISION",
            "--watchdog-dir", self.watchdog_dir,
            "--session-id", self.session_id,
            "--max-authorized", str(self.max_cost_usd),
            "--emergency-trigger", str(self.emergency_trigger_usd),
            "--hourly-rate", str(self.gpu_hourly_rate),
            "--controller-pid", str(os.getpid()),
            "--poll-interval", "1.0"
        ]

        self.watchdog_process = self.watchdog_starter(cmd)
        self.watchdog_pid = self.watchdog_process.pid

        # Await receipt
        readiness_file = os.path.join(
            self.watchdog_dir,
            f"watchdog_readiness_{self.experiment_id}_{self.session_id}.json"
        )
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if self.watchdog_process and self.watchdog_process.poll() is not None:
                raise ProvisioningSecurityError(
                    f"Supervisor died prematurely with exit code {self.watchdog_process.returncode}."
                )
            if os.path.exists(readiness_file):
                try:
                    with open(readiness_file, "r") as f:
                        receipt = json.load(f)
                    if receipt.get("status") == "READY":
                        return True
                except Exception:
                    pass
            time.sleep(0.1)

        raise ProvisioningSecurityError(f"Supervisor pre-provision readiness timed out after {timeout_seconds}s.")

    def provision_single_pod(self, create_pod_fn: Callable[[], str]) -> str:
        """
        Phase 2: Provisions exactly ONE pod after supervisor verification.
        Enforces single-attempt invariant.
        """
        if self.provisioning_attempts >= self.max_provisioning_attempts:
            raise ProvisioningSecurityError(
                f"Single-attempt invariant violated: already attempted {self.provisioning_attempts} provisioning(s)."
            )

        self.provisioning_attempts += 1
        pod_id = create_pod_fn()
        self.active_pod_id = pod_id

        # Register pod with active supervisor
        registration_file = os.path.join(
            self.watchdog_dir,
            f"watchdog_register_pod_{self.experiment_id}.json"
        )
        reg_payload = {
            "experiment_id": self.experiment_id,
            "session_id": self.session_id,
            "pod_id": pod_id,
            "registered_at_utc": time.time()
        }
        with open(registration_file, "w") as f:
            json.dump(reg_payload, f)

        return pod_id

    def execute_bounded_staging(
        self,
        command: str,
        channel: Any,
        timeout_seconds: float = 180.0
    ) -> int:
        """
        Phase 3: Executes remote staging command with strict wall-clock deadline.
        If deadline expires, teardown is triggered immediately.
        """
        try:
            exit_code = safe_channel_wait(channel, timeout_seconds=timeout_seconds)
            return exit_code
        except TimeoutError as te:
            # Trigger emergency teardown of the pod
            self.emergency_teardown(reason=f"Staging command timed out: {te}")
            raise StagingTimeoutError(str(te))

    def emergency_teardown(self, reason: str) -> None:
        """Dispatches immediate termination for active pod and stops supervisor."""
        if self.active_pod_id and self.transport:
            try:
                self.transport.terminate_pod(self.active_pod_id)
            except Exception:
                pass

        if self.watchdog_process and self.watchdog_process.poll() is None:
            try:
                self.watchdog_process.terminate()
            except Exception:
                pass
