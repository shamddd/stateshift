#!/usr/bin/env python3
"""
StateShift Hardened Production Runner V10 (Mission 15.5)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Integrated Production Architecture:
- Execution Modes: DRY_RUN, SIMULATION, PREFLIGHT, CALIBRATION, PRODUCTION.
- Strict isolation: Simulation flags are strictly REJECTED if CALIBRATION or PRODUCTION is selected.
- Independent Watchdog Process: Spawns independent background OS subprocess with its own PID.
- Watchdog-derived limits: Derives budget and emergency trigger ($0.25 for calibration) from verified signed authorization.
- Ed25519 Cryptographic Session Authorization with exact pod-ID binding for both CALIBRATION and PRODUCTION.
- Transactional Checkpoint Manager with atomic promotion, monotonicity, and backup rollback.
- Remote Deployment Verifier and Safe Resume Reconciler.
- Priority-1 Termination Receipt Ordering.
"""

import os
import sys
import json
import time
import signal
import hashlib
import argparse
import subprocess
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

from research_mission_15_6.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    FROZEN_MANIFEST_SHA256,
    PINNED_MODEL_ID,
    PINNED_MODEL_REVISION
)
from research_mission_15_6.calibration.calibration_config import (
    FROZEN_CALIBRATION_REQUEST_IDS,
    generate_calibration_manifest
)
from research_mission_15_6.checkpoint.transactional_checkpoint_manager import TransactionalCheckpointManager
from research_mission_15_6.deployment.remote_deployment_verifier import RemoteDeploymentVerifier
from research_mission_15_6.deployment.safe_resume_reconciler import SafeResumeReconciler, ReattachmentAction
from research_mission_15_6.evaluation.dataset_verifier_v2 import IndependentDatasetVerifierV2
from research_mission_15_6.runner.escalation_manager import DurableEscalationManager
from research_mission_15_6.runner.robust_cost_controller_v8 import RobustCostControllerV8
from research_mission_15_6.scheduler.budget_aware_scheduler import BudgetAwareScheduler
from research_mission_15_6.supervision.independent_financial_watchdog import (
    IndependentFinancialWatchdog,
    ProviderResponseState
)
from research_mission_15_6.transport.runpod_transport_v2 import ProductionRunPodTransportV2


class ExecutionMode(str, Enum):
    DRY_RUN = "DRY_RUN"
    SIMULATION = "SIMULATION"
    PREFLIGHT = "PREFLIGHT"
    CALIBRATION = "CALIBRATION"
    PRODUCTION = "PRODUCTION"


class ProductionState(str, Enum):
    CREATED = "CREATED"
    AUTHORIZATION_VALIDATED = "AUTHORIZATION_VALIDATED"
    MANIFEST_VERIFIED = "MANIFEST_VERIFIED"
    PROVIDER_CONNECTED = "PROVIDER_CONNECTED"
    WATCHDOG_SPAWNED = "WATCHDOG_SPAWNED"
    REMOTE_DEPLOYMENT_VERIFIED = "REMOTE_DEPLOYMENT_VERIFIED"
    REMOTE_RUNNER_LAUNCHED = "REMOTE_RUNNER_LAUNCHED"
    RUNNING = "RUNNING"
    PARTIAL_PRESERVED = "PARTIAL_PRESERVED"
    REMOTE_COMPLETE = "REMOTE_COMPLETE"
    FINAL_DATASET_VERIFICATION = "FINAL_DATASET_VERIFICATION"
    LOCAL_VERIFIED = "LOCAL_VERIFIED"
    TERMINATION_REQUESTED = "TERMINATION_REQUESTED"
    NORMAL_TERMINATION = "NORMAL_TERMINATION"
    BUDGET_EMERGENCY = "BUDGET_EMERGENCY"
    PROVIDER_TERMINATION_CONFIRMED = "PROVIDER_TERMINATION_CONFIRMED"
    TERMINATION_UNCONFIRMED = "TERMINATION_UNCONFIRMED"
    FINISHED = "FINISHED"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"
    DEPLOYMENT_FAILURE = "DEPLOYMENT_FAILURE"


class StateshiftProductionRunnerV10:
    def __init__(
        self,
        experiment_id: str,
        manifest_path: str,
        authorization_path: Optional[str],
        mode: ExecutionMode = ExecutionMode.DRY_RUN,
        pod_id: Optional[str] = None,
        ip: Optional[str] = None,
        port: int = 22,
        ssh_key_path: Optional[str] = None,
        local_data_dir: str = "data/primary_run",
        remote_work_dir: str = "/workspace/stateshift",
        max_cost_usd: float = 0.35,
        max_runtime_minutes: float = 60.0,
        gpu_hourly_rate: float = 0.89,
        poll_interval_seconds: float = 1.0,
        trusted_public_key_b64: Optional[str] = None,
        allow_test_key_for_testing: bool = False,
        # Simulation switches (Strictly prohibited in CALIBRATION and PRODUCTION)
        simulate_records: Optional[int] = None,
        simulate_spend_usd: Optional[float] = None,
        simulate_corrupt_dataset: bool = False,
        simulate_unconfirmed_termination: bool = False,
        simulate_sftp_failure: bool = False,
        simulate_ssh_disconnect: bool = False,
        simulate_runtime_overrun: bool = False,
        simulate_engine_fallback: bool = False,
        simulate_deployment_failure: bool = False,
        simulate_watchdog_crash: bool = False,
        simulate_corrupt_checkpoint: bool = False,
        resume: bool = False
    ):
        self.experiment_id = experiment_id
        self.execution_id = f"exec_{int(time.time())}"
        self.manifest_path = os.path.abspath(manifest_path)
        self.authorization_path = os.path.abspath(authorization_path) if authorization_path else None
        self.mode = mode
        self.pod_id = pod_id
        self.ip = ip
        self.port = port
        self.ssh_key_path = ssh_key_path
        self.local_data_dir = os.path.abspath(local_data_dir)
        self.remote_work_dir = remote_work_dir
        self.max_cost_usd = max_cost_usd
        self.max_runtime_minutes = max_runtime_minutes
        self.gpu_hourly_rate = gpu_hourly_rate
        self.poll_interval_seconds = poll_interval_seconds
        self.trusted_public_key_b64 = trusted_public_key_b64
        self.allow_test_key_for_testing = allow_test_key_for_testing

        # Simulation flags
        self.simulate_records = simulate_records
        self.simulate_spend_usd = simulate_spend_usd
        self.simulate_corrupt_dataset = simulate_corrupt_dataset
        self.simulate_unconfirmed_termination = simulate_unconfirmed_termination
        self.simulate_sftp_failure = simulate_sftp_failure
        self.simulate_ssh_disconnect = simulate_ssh_disconnect
        self.simulate_runtime_overrun = simulate_runtime_overrun
        self.simulate_engine_fallback = simulate_engine_fallback
        self.simulate_deployment_failure = simulate_deployment_failure
        self.simulate_watchdog_crash = simulate_watchdog_crash
        self.simulate_corrupt_checkpoint = simulate_corrupt_checkpoint
        self.resume = resume

        # Block 4: Strict Execution Mode Isolation Enforcement
        self._validate_execution_mode_isolation()

        os.makedirs(self.local_data_dir, exist_ok=True)
        self.watchdog_dir = os.path.join(self.local_data_dir, "watchdog")
        os.makedirs(self.watchdog_dir, exist_ok=True)

        self.state = ProductionState.CREATED
        self.remote_pid: Optional[int] = None
        self.watchdog_process: Optional[subprocess.Popen] = None
        self.watchdog_pid: Optional[int] = None
        self.completed_rollouts: int = 0
        self.total_expected_requests: int = 0
        self.manifest_sha256: str = ""
        self.stop_requested: bool = False
        self.verified_auth_payload: Dict[str, Any] = {}
        self.pre_existing_uptime_seconds: float = 0.0

        # Derived financial thresholds (Derived from authorization)
        self.effective_max_spend: float = self.max_cost_usd
        self.effective_emergency_trigger: float = 0.25 if self.mode in [ExecutionMode.CALIBRATION, ExecutionMode.SIMULATION] else 1.65

        # Local files
        self.local_dataset_file = os.path.join(self.local_data_dir, f"{self.experiment_id}_dataset.jsonl")
        self.termination_receipt_file = os.path.join(self.local_data_dir, f"termination_receipt_{self.experiment_id}.json")
        self.receipt_file = os.path.join(self.local_data_dir, f"{self.experiment_id}_verification_receipt.json")
        self.state_file = os.path.join(self.local_data_dir, f"runner_state_{self.experiment_id}.json")

        # Subsystems
        self.transport = ProductionRunPodTransportV2() if self.mode in [ExecutionMode.CALIBRATION, ExecutionMode.PRODUCTION, ExecutionMode.PREFLIGHT] else None
        self.checkpoint_manager = TransactionalCheckpointManager(
            target_checkpoint_path=self.local_dataset_file,
            manifest_path=self.manifest_path
        )
        is_cal = (self.mode in [ExecutionMode.CALIBRATION, ExecutionMode.SIMULATION])
        self.verifier = IndependentDatasetVerifierV2(manifest_path=self.manifest_path, is_calibration=is_cal)
        self.cost_controller = RobustCostControllerV8(
            experiment_id=self.experiment_id,
            max_cost_usd=self.effective_max_spend,
            max_runtime_minutes=self.max_runtime_minutes,
            gpu_hourly_rate=self.gpu_hourly_rate,
            state_dir=self.local_data_dir
        )
        self.scheduler = BudgetAwareScheduler(
            max_authorized_usd=self.effective_max_spend,
            safety_reserve_usd=max(0.05, self.effective_max_spend - self.effective_emergency_trigger),
            gpu_hourly_rate=self.gpu_hourly_rate
        )

        local_runner = os.path.abspath(os.path.join(os.path.dirname(__file__), "remote_experiment_runner.py"))
        self.deployment_verifier = RemoteDeploymentVerifier(
            transport=self.transport,
            remote_work_dir=self.remote_work_dir,
            local_manifest_path=self.manifest_path,
            local_runner_path=local_runner
        )
        self.resume_reconciler = SafeResumeReconciler(
            transport=self.transport,
            remote_work_dir=self.remote_work_dir
        )

        self._persist_runner_state()

    def _validate_execution_mode_isolation(self):
        """Blocker 4: Rejects simulation flags when paid modes (CALIBRATION or PRODUCTION) are selected."""
        has_sim_flag = any([
            self.simulate_records is not None,
            self.simulate_spend_usd is not None,
            self.simulate_corrupt_dataset,
            self.simulate_unconfirmed_termination,
            self.simulate_sftp_failure,
            self.simulate_ssh_disconnect,
            self.simulate_runtime_overrun,
            self.simulate_engine_fallback,
            self.simulate_deployment_failure,
            self.simulate_watchdog_crash,
            self.simulate_corrupt_checkpoint
        ])
        if self.mode in [ExecutionMode.CALIBRATION, ExecutionMode.PRODUCTION] and has_sim_flag:
            raise ValueError(
                f"Security Violation: Simulation arguments are strictly prohibited in paid mode '{self.mode.value}'. "
                f"Use mode 'SIMULATION' or 'DRY_RUN' for testing."
            )

    def transition_to(self, new_state: ProductionState):
        old_state = self.state
        self.state = new_state
        print(f"[Production Runner] State: {old_state.value} -> {new_state.value}")
        self._persist_runner_state()

    def _persist_runner_state(self):
        payload = {
            "experiment_id": self.experiment_id,
            "execution_id": self.execution_id,
            "state": self.state.value,
            "mode": self.mode.value,
            "pod_id": self.pod_id,
            "controller_pid": os.getpid(),
            "watchdog_pid": self.watchdog_pid,
            "remote_pid": self.remote_pid,
            "manifest_sha256": self.manifest_sha256,
            "completed_rollouts": self.completed_rollouts,
            "total_expected_requests": self.total_expected_requests,
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        tmp = self.state_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.state_file)

    # ==================== Step 1: Session Authorization ====================

    def validate_session_authorization(self) -> bool:
        if self.mode in [ExecutionMode.DRY_RUN, ExecutionMode.SIMULATION]:
            if not self.authorization_path:
                print(f"[Production Runner] {self.mode.value} mode: bypassing strict production authorization.")
                self.transition_to(ProductionState.AUTHORIZATION_VALIDATED)
                return True

        if not self.authorization_path or not os.path.exists(self.authorization_path):
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            print(f"[Production Runner] AUTHORIZATION ABORT: Authorization document missing: '{self.authorization_path}'.")
            return False

        with open(self.authorization_path, "r", encoding="utf-8") as f:
            auth_doc = json.load(f)

        authorizer = CryptographicAuthorizer(
            trusted_public_key_b64=self.trusted_public_key_b64,
            nonce_registry_path=os.path.join(self.local_data_dir, "used_nonces.json"),
            allow_test_key_for_testing=self.allow_test_key_for_testing
        )
        active_manifest = getattr(self, "parent_manifest_sha256", self.manifest_sha256)
        is_valid, reason = authorizer.verify_authorization(
            auth_doc=auth_doc,
            active_experiment_id=self.experiment_id,
            active_pod_id=self.pod_id or "",
            active_manifest_sha256=active_manifest,
            active_mode=self.mode.value
        )
        if not is_valid:
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            print(f"[Production Runner] AUTHORIZATION ABORT: Session authorization REJECTED: {reason}")
            return False

        self.verified_auth_payload = auth_doc.get("payload", {})
        # Derive watchdog financial thresholds strictly from authorization
        auth_max = float(self.verified_auth_payload.get("max_incremental_spend_usd", self.max_cost_usd))
        if self.max_cost_usd is not None and self.max_cost_usd > (auth_max + 1e-4):
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            print(f"[Production Runner] AUTHORIZATION ABORT: CLI budget ${self.max_cost_usd:.2f} exceeds signed authorized limit ${auth_max:.2f}.")
            return False

        self.effective_max_spend = auth_max
        self.effective_emergency_trigger = float(self.verified_auth_payload.get("emergency_trigger_usd", 0.25 if self.mode == ExecutionMode.CALIBRATION else 1.65))

        print(f"[Production Runner] Cryptographic authorization verified (Ed25519 signature valid).")
        print(f"[Production Runner] Enforced Financial Thresholds: Max Spend=${self.effective_max_spend:.4f}, Emergency Trigger=${self.effective_emergency_trigger:.4f}.")
        self.transition_to(ProductionState.AUTHORIZATION_VALIDATED)
        return True

    # ==================== Step 2: Manifest Verification ====================

    def verify_manifest(self) -> bool:
        if not os.path.exists(self.manifest_path):
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            print(f"[Production Runner] Manifest file not found: {self.manifest_path}")
            return False

        with open(self.manifest_path, "rb") as f:
            self.manifest_sha256 = hashlib.sha256(f.read()).hexdigest()

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception as e:
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            print(f"[Production Runner] Malformed manifest JSON: {e}")
            return False

        self.total_expected_requests = len(manifest_data.get("requests", []))
        self.parent_manifest_sha256 = manifest_data.get("parent_manifest_sha256", self.manifest_sha256)

        is_primary = (self.manifest_sha256 == FROZEN_MANIFEST_SHA256)
        is_calib = (manifest_data.get("parent_manifest_sha256") == FROZEN_MANIFEST_SHA256)

        if self.mode in [ExecutionMode.CALIBRATION, ExecutionMode.SIMULATION]:
            if not (is_primary or is_calib):
                self.transition_to(ProductionState.INTEGRITY_FAILURE)
                print(f"[Production Runner] Manifest hash mismatch: {self.manifest_sha256} vs {FROZEN_MANIFEST_SHA256}.")
                return False
            # In calibration mode, check all 10 frozen IDs are present
            req_ids = {r.get("request_id") for r in manifest_data.get("requests", [])}
            missing = [cid for cid in FROZEN_CALIBRATION_REQUEST_IDS if cid not in req_ids]
            if missing:
                self.transition_to(ProductionState.INTEGRITY_FAILURE)
                print(f"[Production Runner] CALIBRATION Manifest missing expected frozen IDs: {missing}.")
                return False
            print(f"[Production Runner] Calibration Manifest cryptographically verified (10 frozen requests present).")
        else:
            if not is_primary:
                self.transition_to(ProductionState.INTEGRITY_FAILURE)
                print(f"[Production Runner] Manifest hash mismatch: {self.manifest_sha256} vs {FROZEN_MANIFEST_SHA256}.")
                return False
            if self.total_expected_requests != 400:
                self.transition_to(ProductionState.INTEGRITY_FAILURE)
                print(f"[Production Runner] Manifest request count must be 400, found {self.total_expected_requests}.")
                return False
            print(f"[Production Runner] Manifest cryptographically verified: 400 requests.")

        self.transition_to(ProductionState.MANIFEST_VERIFIED)
        return True

    # ==================== Step 3: Provider Connection ====================

    def connect_and_verify_provider(self) -> bool:
        if self.mode in [ExecutionMode.DRY_RUN, ExecutionMode.SIMULATION] or not self.transport:
            print(f"[Production Runner] {self.mode.value} simulation: mocking provider connection.")
            self.cost_controller.initialize_session()
            self.transition_to(ProductionState.PROVIDER_CONNECTED)
            return True

        if not self.pod_id:
            raise ValueError("pod_id must be specified for cloud execution.")

        meta = self.transport.get_pod_metadata(self.pod_id)
        if not meta.get("exists", False):
            raise ConnectionError(f"Pod {self.pod_id} not found on RunPod.")

        status = meta.get("status")
        if status != "RUNNING":
            raise ConnectionError(f"Pod {self.pod_id} status is '{status}', must be 'RUNNING'.")

        self.pre_existing_uptime_seconds = float(meta.get("uptimeSeconds", 0.0) or 0.0)
        self.cost_controller.initialize_session(pod_metadata=meta)
        print(f"[Production Runner] Connected to RunPod pod {self.pod_id} (Status: RUNNING).")
        self.transition_to(ProductionState.PROVIDER_CONNECTED)
        return True

    # ==================== Step 4: Spawn Independent Watchdog Subprocess ====================

    def spawn_independent_watchdog(self) -> bool:
        """Blocker 1: Spawns genuinely independent OS background process."""
        watchdog_script = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "supervision", "independent_financial_watchdog.py")
        )
        cmd = [
            sys.executable,
            watchdog_script,
            "--experiment-id", self.experiment_id,
            "--pod-id", self.pod_id or "simulated_pod",
            "--watchdog-dir", self.watchdog_dir,
            "--session-id", self.execution_id,
            "--max-authorized", str(self.effective_max_spend),
            "--emergency-trigger", str(self.effective_emergency_trigger),
            "--hourly-rate", str(self.gpu_hourly_rate),
            "--max-runtime", str(self.max_runtime_minutes),
            "--poll-interval", str(self.poll_interval_seconds),
            "--controller-heartbeat", self.state_file,
            "--controller-pid", str(os.getpid())
        ]
        if self.simulate_spend_usd is not None:
            cmd.extend(["--simulate-spend", str(self.simulate_spend_usd)])
        if self.pre_existing_uptime_seconds > 0.0:
            cmd.extend(["--pre-existing-uptime", str(self.pre_existing_uptime_seconds)])
        if self.authorization_path and os.path.exists(self.authorization_path):
            cmd.extend(["--authorization", self.authorization_path])
        if self.trusted_public_key_b64:
            cmd.extend(["--trusted-public-key", self.trusted_public_key_b64])
        if self.allow_test_key_for_testing:
            cmd.append("--allow-test-key")

        # Spawn decoupled OS process
        self.watchdog_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setpgrp if hasattr(os, "setpgrp") else None
        )
        self.watchdog_pid = self.watchdog_process.pid
        print(f"[Production Runner] Genuinely independent watchdog spawned (Watchdog PID: {self.watchdog_pid}, Controller PID: {os.getpid()}).")
        self.transition_to(ProductionState.WATCHDOG_SPAWNED)

        if self.simulate_watchdog_crash:
            # Simulate a watchdog crash by immediately killing the spawned process
            if self.watchdog_process:
                self.watchdog_process.kill()
                self.watchdog_process.wait()
            # Remove any heartbeat file so check_watchdog_alive fails immediately
            hb_file = os.path.join(self.watchdog_dir, f"watchdog_heartbeat_{self.experiment_id}.json")
            if os.path.exists(hb_file):
                os.remove(hb_file)

        return True

    def wait_for_watchdog_readiness(self, timeout_seconds: float = 15.0) -> bool:
        """
        Defect 2: Mandatory Watchdog Startup Handshake.
        Awaiting and validating 12 distinct points on the atomic readiness receipt
        before remote deployment or inference is authorized.
        """
        readiness_file = os.path.join(
            self.watchdog_dir,
            f"watchdog_readiness_{self.experiment_id}_{self.execution_id}.json"
        )
        start_t = time.time()
        receipt_data = None
        while (time.time() - start_t) < timeout_seconds:
            # Check if watchdog process crashed before writing receipt
            if self.watchdog_process and self.watchdog_process.poll() is not None:
                print(f"[Watchdog Handshake Failure] Watchdog process died prematurely with exit code {self.watchdog_process.returncode}.")
                return False

            if os.path.exists(readiness_file):
                try:
                    with open(readiness_file, "r", encoding="utf-8") as f:
                        receipt_data = json.load(f)
                    break
                except Exception:
                    pass
            time.sleep(0.1)

        if not receipt_data:
            print(f"[Watchdog Handshake Timeout] Readiness receipt not found after {timeout_seconds:.1f}s.")
            return False

        # 12-point validation check:
        # 1. status == "READY"
        if receipt_data.get("status") != "READY":
            print(f"[Watchdog Handshake Validation Failure] Status '{receipt_data.get('status')}' != 'READY'")
            return False

        # 2. lifecycle_state in ["ACTIVE", "STARTING"]
        if receipt_data.get("lifecycle_state") not in ["ACTIVE", "STARTING"]:
            print(f"[Watchdog Handshake Validation Failure] Invalid lifecycle state: {receipt_data.get('lifecycle_state')}")
            return False

        # 3. watchdog_pid != os.getpid()
        w_pid = receipt_data.get("watchdog_pid")
        if not w_pid or w_pid == os.getpid():
            print(f"[Watchdog Handshake Validation Failure] Invalid watchdog PID {w_pid} (matches controller {os.getpid()})")
            return False

        # 4. watchdog_pid is alive in OS process table
        try:
            os.kill(w_pid, 0)
        except OSError as e:
            print(f"[Watchdog Handshake Validation Failure] Watchdog PID {w_pid} is not alive: {e}")
            return False

        # 5. experiment_id matches
        if receipt_data.get("experiment_id") != self.experiment_id:
            print(f"[Watchdog Handshake Validation Failure] Experiment ID mismatch: {receipt_data.get('experiment_id')} != {self.experiment_id}")
            return False

        # 6. session_id matches
        if receipt_data.get("session_id") != self.execution_id:
            print(f"[Watchdog Handshake Validation Failure] Session ID mismatch: {receipt_data.get('session_id')} != {self.execution_id}")
            return False

        # 7. pod_id matches
        expected_pod = self.pod_id or "simulated_pod"
        if receipt_data.get("pod_id") != expected_pod:
            print(f"[Watchdog Handshake Validation Failure] Pod ID mismatch: {receipt_data.get('pod_id')} != {expected_pod}")
            return False

        # 8. max_authorized_usd matches or is conservative
        r_max = float(receipt_data.get("max_authorized_usd", 0.0))
        if r_max > self.effective_max_spend + 1e-4:
            print(f"[Watchdog Handshake Validation Failure] Max authorized spend ${r_max} exceeds runner limit ${self.effective_max_spend}")
            return False

        # 9. emergency_trigger_usd matches or is conservative
        r_trig = float(receipt_data.get("emergency_trigger_usd", 0.0))
        if r_trig > self.effective_emergency_trigger + 1e-4:
            print(f"[Watchdog Handshake Validation Failure] Emergency trigger ${r_trig} exceeds runner limit ${self.effective_emergency_trigger}")
            return False

        # 10. Freshness check
        receipt_ts = float(receipt_data.get("timestamp_utc", 0.0))
        age = time.time() - receipt_ts
        if age > (timeout_seconds + 5.0) or age < -5.0:
            print(f"[Watchdog Handshake Validation Failure] Stale or future receipt timestamp (age: {age:.1f}s)")
            return False

        # 11. account_preservation_floor_usd verified
        floor = float(receipt_data.get("account_preservation_floor_usd", 0.0))
        policy_ver = getattr(self, "verified_auth_payload", {}).get("financial_policy_version", "POLICY_V1_STANDARD")
        required_floor = 0.32 if policy_ver == "POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION" else 7.00
        if floor < required_floor - 1e-4:
            print(f"[Watchdog Handshake Validation Failure] Preservation floor ${floor} is below required ${required_floor:.2f} USD")
            return False

        # 12. Pre-existing uptime matches or is non-negative
        r_uptime = float(receipt_data.get("pre_existing_uptime_seconds", 0.0))
        if r_uptime < 0.0:
            print(f"[Watchdog Handshake Validation Failure] Negative pre-existing uptime: {r_uptime}")
            return False

        print(f"[Production Runner] Watchdog readiness handshake verified successfully (Watchdog PID: {w_pid}, Session: {self.execution_id}).")
        return True

    # ==================== Step 5: Remote Deployment Verification & Launch ====================

    def deploy_and_launch_remote(self) -> int:
        if self.mode == ExecutionMode.PREFLIGHT:
            print("[Production Runner] PREFLIGHT mode: skipping execution launch.")
            return 0

        # Check deployment artifacts
        if self.simulate_deployment_failure:
            self.transition_to(ProductionState.DEPLOYMENT_FAILURE)
            print("[Production Runner] DEPLOYMENT VERIFICATION ABORT: Remote deployment verification failed: Missing remote script.")
            return 0

        if self.mode in [ExecutionMode.DRY_RUN, ExecutionMode.SIMULATION] or not self.transport:
            print(f"[Production Runner] {self.mode.value} simulation: verified remote deployment.")
            self.transition_to(ProductionState.REMOTE_DEPLOYMENT_VERIFIED)
        else:
            env_ok, env_msg = self.deployment_verifier.verify_preflight_environment(ip=self.ip, port=self.port)
            if not env_ok:
                self.transition_to(ProductionState.DEPLOYMENT_FAILURE)
                raise RuntimeError(f"Deployment environment rejected: {env_msg}")
            self.transition_to(ProductionState.REMOTE_DEPLOYMENT_VERIFIED)

        # Handle --resume reattachment reconciliation
        if self.resume:
            action, pid, rationale = self.resume_reconciler.reconcile_remote_process(
                local_experiment_id=self.experiment_id,
                expected_manifest_sha256=self.manifest_sha256,
                last_known_pid=self.remote_pid,
                ip=self.ip,
                port=self.port
            )
            print(f"[Production Runner] Resume reconciliation: {action} ({rationale})")
            if action == ReattachmentAction.HALT_FOR_OPERATOR:
                raise RuntimeError(f"Reattachment halted for operator: {rationale}")
            elif action == ReattachmentAction.REATTACH:
                self.remote_pid = pid
                self.transition_to(ProductionState.RUNNING)
                return self.remote_pid

        self.transition_to(ProductionState.REMOTE_RUNNER_LAUNCHED)

        if self.mode in [ExecutionMode.DRY_RUN, ExecutionMode.SIMULATION] or not self.transport:
            print(f"[Production Runner] {self.mode.value} simulation: Simulating detached background runner.")
            self.remote_pid = 99999
        else:
            ok, real_pid, msg = self.deployment_verifier.launch_and_verify_process(
                experiment_id=self.experiment_id,
                execution_id=self.execution_id,
                ip=self.ip,
                port=self.port
            )
            if not ok or not real_pid:
                self.transition_to(ProductionState.DEPLOYMENT_FAILURE)
                raise RuntimeError(f"Remote process verification failed: {msg}")
            self.remote_pid = real_pid

        self.transition_to(ProductionState.RUNNING)
        return self.remote_pid

    def _generate_simulated_records(self, count: int):
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

        engine_name = "transformers_fallback" if self.simulate_engine_fallback else "vllm"
        records = []
        for i in range(min(count, len(manifest_data.get("requests", [])))):
            req = manifest_data["requests"][i]
            rec = {
                "request_id": req["request_id"],
                "problem_id": req.get("problem_id", f"prob_{i}"),
                "condition_code": req.get("condition_code", "A"),
                "prompt_sha256": req.get("prompt_sha256", hashlib.sha256(f"p_{i}".encode()).hexdigest()),
                "gold_answer": req.get("gold_answer", "42"),
                "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
                "model_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
                "tokenizer_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
                "inference_engine": engine_name,
                "inference_engine_version": "0.6.3",
                "temperature": 0.0,
                "max_tokens": 768,
                "seed": 42,
                "sampling_mode": "greedy",
                "completion_status": "COMPLETED",
                "finish_reason": "stop",
                "source_type": "REAL_MODEL_INFERENCE",
                "experiment_id": self.experiment_id,
                "manifest_hash": self.manifest_sha256,
                "generation_timestamp": time.time(),
                "model_output": f"Step by step solution to \\boxed{{{req.get('gold_answer', '42')}}}."
            }
            records.append(rec)

        tmp_cand = self.local_dataset_file + ".candidate.tmp"
        with open(tmp_cand, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
            if self.simulate_corrupt_dataset:
                f.write('{"request_id": "corrupted_incomplete_json\n')
            f.flush()
            os.fsync(f.fileno())

        if self.simulate_corrupt_checkpoint:
            with open(tmp_cand, "w") as f:
                f.write("corrupted garbage line\n")

        promoted, n_promoted, reason = self.checkpoint_manager.promote_candidate_checkpoint(tmp_cand)
        if promoted:
            self.completed_rollouts = n_promoted
        else:
            print(f"[Checkpoint Notice] Promotion deferred: {reason}")
            if self.simulate_corrupt_checkpoint:
                # In simulation of corrupted candidate, stop to avoid infinite loop
                self.stop_requested = True

    # ==================== Step 6: Supervision & Watchdog Monitoring ====================

    def sync_checkpoint_transactional(self) -> int:
        if self.simulate_records is not None:
            self._generate_simulated_records(self.simulate_records)
            return len(self.checkpoint_manager.promoted_records)

        if self.simulate_sftp_failure:
            print("[Sync Notice] Simulated SFTP connection failure: Socket timeout.")
            self.stop_requested = True
            return self.completed_rollouts

        if self.simulate_ssh_disconnect:
            print("[SSH Notice] Simulated transient SSH drop: Connection reset by peer.")
            self.stop_requested = True
            return self.completed_rollouts

        if self.mode in [ExecutionMode.DRY_RUN, ExecutionMode.SIMULATION] or not self.transport:
            return len(self.checkpoint_manager.promoted_records)

        remote_out = f"{self.remote_work_dir}/data/output.jsonl"
        tmp_candidate = self.local_dataset_file + ".candidate.tmp"
        try:
            success = self.transport.fetch_file(remote_out, tmp_candidate, ip=self.ip, port=self.port)
            if success and os.path.exists(tmp_candidate):
                promoted, count, msg = self.checkpoint_manager.promote_candidate_checkpoint(tmp_candidate)
                if promoted:
                    self.completed_rollouts = count
                else:
                    print(f"[Checkpoint Rejected] {msg}")
        except Exception as e:
            print(f"[Sync Notice] Fetch deferred: {e}")
        return len(self.checkpoint_manager.promoted_records)

    def check_watchdog_alive(self, stale_seconds: float = 10.0) -> bool:
        """Audits independent watchdog process and heartbeat file."""
        if self.watchdog_process:
            poll = self.watchdog_process.poll()
            if poll is not None:
                return False

        hb_file = os.path.join(self.watchdog_dir, f"watchdog_heartbeat_{self.experiment_id}.json")
        if os.path.exists(hb_file):
            try:
                with open(hb_file, "r") as f:
                    hb_data = json.load(f)
                    if (time.time() - hb_data.get("timestamp_utc", 0.0)) > stale_seconds:
                        return False
            except Exception:
                return False
        return True

    def run_supervision_loop(self) -> bool:
        print("[Production Runner] Supervision loop engaged.")
        while not self.stop_requested:
            # 1. Update controller state heartbeat
            self._persist_runner_state()

            # 2. Check independent watchdog health
            if not self.check_watchdog_alive():
                print("[Production Runner] CRITICAL: Independent watchdog process died or stopped beating! Halting scheduling.")
                self.transition_to(ProductionState.INTEGRITY_FAILURE)
                self.terminate_emergency(reason="Watchdog process failure")
                return False

            # Check watchdog state file for external termination dispatch
            state_file = os.path.join(self.watchdog_dir, f"watchdog_state_{self.experiment_id}.json")
            if os.path.exists(state_file):
                try:
                    with open(state_file, "r") as f:
                        w_state = json.load(f)
                        if w_state.get("termination_dispatched"):
                            print(f"[Production Runner] Watchdog dispatched termination independently ({w_state.get('reason')}).")
                            self.transition_to(ProductionState.BUDGET_EMERGENCY)
                            return False
                except Exception:
                    pass

            # In-process cost controller check
            if self.simulate_runtime_overrun:
                self.cost_controller.start_time = time.time() - (self.max_runtime_minutes * 60.0 + 100.0)

            eff_spend = self.simulate_spend_usd if self.simulate_spend_usd is not None else None
            cost_status = self.cost_controller.check_and_enforce_budget()
            if cost_status["should_emergency_terminate"] or (eff_spend is not None and eff_spend >= self.effective_emergency_trigger):
                print(f"[Production Runner] In-process cost controller tripped.")
                self.terminate_emergency(reason="In-process budget limit reached")
                return False

            # 3. Transactional Checkpoint Sync
            completed = self.sync_checkpoint_transactional()

            # 4. Budget Scheduler Check
            current_est_spend = eff_spend if eff_spend is not None else cost_status.get("estimated_cost", 0.0)
            can_sched, sched_reason, _ = self.scheduler.can_schedule_next_batch(
                batch_size=4,
                current_spend_usd=current_est_spend
            )
            if not can_sched:
                print(f"[Production Runner] Scheduler HALT: {sched_reason}")
                self.transition_to(ProductionState.PARTIAL_PRESERVED)
                self.terminate_normal(is_partial=True)
                return False

            # 5. Check for completion (10 for CALIBRATION, 400 for PRODUCTION)
            target = 10 if self.mode in [ExecutionMode.CALIBRATION, ExecutionMode.SIMULATION] else self.total_expected_requests
            if completed >= target:
                print(f"[Production Runner] Target {target} rollouts achieved.")
                self.transition_to(ProductionState.REMOTE_COMPLETE)
                return True

            time.sleep(self.poll_interval_seconds)
        return False

    # ==================== Step 7: Dataset Verification Gate ====================

    def verify_final_dataset(self) -> bool:
        self.transition_to(ProductionState.FINAL_DATASET_VERIFICATION)
        is_valid, receipt = self.verifier.verify_final_local_dataset(
            self.local_dataset_file,
            receipt_output_path=self.receipt_file
        )
        if not is_valid:
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            print(f"[Completion Gate] REJECTED: {receipt.get('errors', [])[:3]}")
            return False

        if self.mode in [ExecutionMode.CALIBRATION, ExecutionMode.SIMULATION]:
            print(f"[Completion Gate] PASSED: Verified 10/10 rollouts. CALIBRATION_COMPLETE.")
            self.transition_to(ProductionState.LOCAL_VERIFIED)
            return True

        self.transition_to(ProductionState.LOCAL_VERIFIED)
        print(f"[Completion Gate] PASSED: Verified 400/400 rollouts.")
        return True

    # ==================== Step 8: Termination & Escalation ====================

    def terminate_normal(self, is_partial: bool = False) -> bool:
        self.transition_to(ProductionState.NORMAL_TERMINATION)
        term_ok = False
        if self.simulate_unconfirmed_termination:
            term_ok = False
        elif (self.simulate_records is not None or self.simulate_spend_usd is not None or self.mode in [ExecutionMode.DRY_RUN, ExecutionMode.SIMULATION]):
            term_ok = True
        elif self.transport and self.pod_id:
            term_ok, _ = self.transport.terminate_pod(self.pod_id)
            if term_ok:
                term_ok = self.transport.verify_pod_terminated(self.pod_id)
        else:
            term_ok = True

        reason = "PARTIAL_BUDGET_STOP" if is_partial else "NORMAL_COMPLETION"
        # Priority-1: Persist receipt before anything else
        self._persist_termination_receipt(reason, confirmed=term_ok)

        # Defect 3: Only shut down watchdog if provider destruction is confirmed!
        if term_ok:
            if self.watchdog_process:
                try:
                    self.watchdog_process.terminate()
                    self.watchdog_process.wait(timeout=5.0)
                except Exception:
                    pass
            self.transition_to(ProductionState.PROVIDER_TERMINATION_CONFIRMED)
            self.transition_to(ProductionState.FINISHED)
            return True
        else:
            print(f"[Production Runner] WARNING: Termination unconfirmed by provider. Preserving independent watchdog PID {self.watchdog_pid} for background reconciliation and operator protection.")
            self.transition_to(ProductionState.TERMINATION_UNCONFIRMED)
            DurableEscalationManager.record_unconfirmed_termination(
                pod_id=self.pod_id or "simulated_pod",
                reason=reason,
                attempts=1,
                last_known_status="STOPPED_OR_UNCONFIRMED",
                error_message="Provider failed to confirm destruction",
                alert_dir=self.local_data_dir
            )
            return False

    def terminate_emergency(self, reason: str) -> bool:
        print(f"\n[EMERGENCY SHUTDOWN] Reason: {reason}")
        self.stop_requested = True
        self.transition_to(ProductionState.TERMINATION_REQUESTED)

        term_ok = False
        if self.simulate_unconfirmed_termination:
            term_ok = False
        elif (self.simulate_records is not None or self.simulate_spend_usd is not None or self.mode in [ExecutionMode.DRY_RUN, ExecutionMode.SIMULATION]):
            term_ok = True
        elif self.transport and self.pod_id:
            for _ in range(3):
                ok, _ = self.transport.terminate_pod(self.pod_id)
                if ok:
                    term_ok = self.transport.verify_pod_terminated(self.pod_id)
                    if term_ok:
                        break
                time.sleep(1.0)
        else:
            term_ok = True

        # Priority-1: Persist termination receipt
        self._persist_termination_receipt(reason, confirmed=term_ok)

        try:
            self.sync_checkpoint_transactional()
        except Exception:
            pass

        # Defect 3: Only shut down watchdog if provider destruction is confirmed!
        if term_ok:
            if self.watchdog_process:
                try:
                    self.watchdog_process.terminate()
                    self.watchdog_process.wait(timeout=5.0)
                except Exception:
                    pass
            self.transition_to(ProductionState.PROVIDER_TERMINATION_CONFIRMED)
            return True
        else:
            print(f"[Production Runner] WARNING: Termination unconfirmed by provider. Preserving independent watchdog PID {self.watchdog_pid} for background reconciliation and operator protection.")
            self.transition_to(ProductionState.TERMINATION_UNCONFIRMED)
            DurableEscalationManager.record_unconfirmed_termination(
                pod_id=self.pod_id or "simulated_pod",
                reason=reason,
                attempts=3,
                last_known_status="UNCONFIRMED",
                error_message="All termination retries exhausted",
                alert_dir=self.local_data_dir
            )
            return False

    def _persist_termination_receipt(self, reason: str, confirmed: bool):
        receipt = {
            "experiment_id": self.experiment_id,
            "pod_id": self.pod_id,
            "reason": reason,
            "confirmed_by_provider": confirmed,
            "final_state": self.state.value,
            "completed_rollouts": self.completed_rollouts,
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        tmp = self.termination_receipt_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.termination_receipt_file)

    def execute_complete_lifecycle(self) -> bool:
        print(f"================================================================================")
        print(f"  STATESHIFT HARDENED PRODUCTION RUNNER V10 (Mode: {self.mode.value})")
        print(f"================================================================================")
        if not self.verify_manifest():
            return False
        if not self.validate_session_authorization():
            return False
        if not self.connect_and_verify_provider():
            return False

        if self.mode == ExecutionMode.PREFLIGHT:
            print("[Production Runner] PREFLIGHT complete: All checks verified.")
            return True

        # Spawn independent watchdog process
        self.spawn_independent_watchdog()

        # Defect 2: Mandatory Startup Handshake Gate
        if not self.wait_for_watchdog_readiness():
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            self.terminate_emergency("Watchdog startup handshake failed or timed out")
            return False

        pid = self.deploy_and_launch_remote()
        if self.simulate_deployment_failure:
            return False

        complete = self.run_supervision_loop()
        if not complete:
            return False

        verified = self.verify_final_dataset()
        if not verified:
            return False

        return self.terminate_normal()

    def run(self) -> bool:
        """Canonical execution alias."""
        return self.execute_complete_lifecycle()


def parse_cli_args():
    parser = argparse.ArgumentParser(description="StateShift Hardened Production Runner (Mission 15.5)")
    parser.add_argument("--mode", type=str, default="DRY_RUN", choices=["DRY_RUN", "SIMULATION", "PREFLIGHT", "CALIBRATION", "PRODUCTION"])
    parser.add_argument("--authorization", type=str, default=None)
    parser.add_argument("--manifest", type=str, required=True)
    parser.add_argument("--experiment-id", type=str, default="stateshift-calibration-10")
    parser.add_argument("--pod-id", type=str, default=None)
    parser.add_argument("--ip", type=str, default=None)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--ssh-key-path", type=str, default=None)
    parser.add_argument("--local-data-dir", type=str, default="data/primary_run")
    parser.add_argument("--remote-work-dir", type=str, default="/workspace/stateshift")
    parser.add_argument("--max-cost-usd", type=float, default=0.35)
    parser.add_argument("--max-runtime-minutes", type=float, default=60.0)
    parser.add_argument("--gpu-hourly-rate", type=float, default=0.89)
    parser.add_argument("--poll-interval", type=float, default=0.1)
    parser.add_argument("--trusted-public-key", type=str, default=None)
    parser.add_argument("--allow-test-key-for-testing", action="store_true")

    # Simulation switches (Strictly for SIMULATION or DRY_RUN mode)
    parser.add_argument("--simulate-records", type=int, default=None)
    parser.add_argument("--simulate-spend-usd", type=float, default=None)
    parser.add_argument("--simulate-corrupt-dataset", action="store_true")
    parser.add_argument("--simulate-unconfirmed-termination", action="store_true")
    parser.add_argument("--simulate-sftp-failure", action="store_true")
    parser.add_argument("--simulate-ssh-disconnect", action="store_true")
    parser.add_argument("--simulate-runtime-overrun", action="store_true")
    parser.add_argument("--simulate-engine-fallback", action="store_true")
    parser.add_argument("--simulate-deployment-failure", action="store_true")
    parser.add_argument("--simulate-watchdog-crash", action="store_true")
    parser.add_argument("--simulate-corrupt-checkpoint", action="store_true")
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main():
    args = parse_cli_args()
    try:
        runner = StateshiftProductionRunnerV10(
            experiment_id=args.experiment_id,
            manifest_path=args.manifest,
            authorization_path=args.authorization,
            mode=ExecutionMode(args.mode),
            pod_id=args.pod_id,
            ip=args.ip,
            port=args.port,
            ssh_key_path=args.ssh_key_path,
            local_data_dir=args.local_data_dir,
            remote_work_dir=args.remote_work_dir,
            max_cost_usd=args.max_cost_usd,
            max_runtime_minutes=args.max_runtime_minutes,
            gpu_hourly_rate=args.gpu_hourly_rate,
            poll_interval_seconds=args.poll_interval,
            trusted_public_key_b64=args.trusted_public_key,
            allow_test_key_for_testing=args.allow_test_key_for_testing,
            simulate_records=args.simulate_records,
            simulate_spend_usd=args.simulate_spend_usd,
            simulate_corrupt_dataset=args.simulate_corrupt_dataset,
            simulate_unconfirmed_termination=args.simulate_unconfirmed_termination,
            simulate_sftp_failure=args.simulate_sftp_failure,
            simulate_ssh_disconnect=args.simulate_ssh_disconnect,
            simulate_runtime_overrun=args.simulate_runtime_overrun,
            simulate_engine_fallback=args.simulate_engine_fallback,
            simulate_deployment_failure=args.simulate_deployment_failure,
            simulate_watchdog_crash=args.simulate_watchdog_crash,
            simulate_corrupt_checkpoint=args.simulate_corrupt_checkpoint,
            resume=args.resume
        )
    except ValueError as e:
        print(f"[Production Runner] CONFIGURATION REJECTED: {e}")
        sys.exit(2)

    success = runner.execute_complete_lifecycle()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
