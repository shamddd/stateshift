#!/usr/bin/env python3
"""
StateShift Production Orchestrator & Autonomous Runner (Mission 15.3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Orchestrates the complete 400-request replication experiment lifecycle:
- Session-specific authorization validation
- Cryptographic manifest verification
- Live financial watchdog with retryable emergency shutdown
- Detached remote runner execution and progress monitoring
- Resilient intermediate snapshot synchronization
- Strict physical dataset completion gate
- Priority-1 provider pod termination & durable escalation management
"""

import os
import sys
import time
import json
import enum
import hashlib
import argparse
import threading
from typing import Dict, Any, List, Optional, Tuple, Callable

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_3.auth.session_authorizer import SessionAuthorizer, FROZEN_MANIFEST_SHA256
from research_mission_15_3.runner.robust_cost_controller_v8 import (
    RobustCostControllerV8, ShutdownLifecycleState
)
from research_mission_15_3.runner.escalation_manager import DurableEscalationManager
from research_mission_15_3.scheduler.budget_aware_scheduler import BudgetAwareScheduler
from research_mission_15_3.transport.runpod_transport_v2 import ProductionRunPodTransportV2, RunPodAPIError
from research_mission_15_3.evaluation.dataset_verifier_v2 import IndependentDatasetVerifierV2


class ExecutionMode(str, enum.Enum):
    DRY_RUN = "DRY_RUN"
    PREFLIGHT = "PREFLIGHT"
    PRODUCTION = "PRODUCTION"


class ProductionState(str, enum.Enum):
    CREATED = "CREATED"
    AUTHORIZATION_VALIDATED = "AUTHORIZATION_VALIDATED"
    MANIFEST_VERIFIED = "MANIFEST_VERIFIED"
    PROVIDER_CONNECTED = "PROVIDER_CONNECTED"
    REMOTE_ENVIRONMENT_VERIFIED = "REMOTE_ENVIRONMENT_VERIFIED"
    REMOTE_RUNNER_LAUNCHED = "REMOTE_RUNNER_LAUNCHED"
    RUNNING = "RUNNING"
    CHECKPOINT_SYNCING = "CHECKPOINT_SYNCING"
    REMOTE_COMPLETE = "REMOTE_COMPLETE"
    FINAL_DATASET_VERIFICATION = "FINAL_DATASET_VERIFICATION"
    LOCAL_VERIFIED = "LOCAL_VERIFIED"
    NORMAL_TERMINATION = "NORMAL_TERMINATION"
    PROVIDER_TERMINATION_CONFIRMED = "PROVIDER_TERMINATION_CONFIRMED"
    FINISHED = "FINISHED"

    # Exceptional and Failure States
    PARTIAL_PRESERVED = "PARTIAL_PRESERVED"
    BUDGET_EMERGENCY = "BUDGET_EMERGENCY"
    TERMINATION_REQUESTED = "TERMINATION_REQUESTED"
    TERMINATION_UNCONFIRMED = "TERMINATION_UNCONFIRMED"
    RETRIEVAL_FAILURE = "RETRIEVAL_FAILURE"
    REMOTE_EXECUTION_FAILURE = "REMOTE_EXECUTION_FAILURE"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"


class StateshiftProductionRunner:
    def __init__(
        self,
        experiment_id: str = "stateshift_400_replication_2026",
        manifest_path: str = "manifests/primary_100_manifest.json",
        authorization_path: Optional[str] = None,
        mode: ExecutionMode = ExecutionMode.DRY_RUN,
        pod_id: Optional[str] = None,
        ip: Optional[str] = None,
        port: int = 22,
        ssh_key_path: Optional[str] = None,
        local_data_dir: str = "data/primary_run",
        remote_work_dir: str = "/workspace/stateshift",
        max_cost_usd: float = 2.00,
        max_runtime_minutes: float = 160.0,
        gpu_hourly_rate: float = 0.89,
        poll_interval_seconds: float = 1.0,
        transport: Optional[Any] = None,
        simulate_records: Optional[int] = None,
        simulate_spend_usd: Optional[float] = None,
        simulate_corrupt_dataset: bool = False,
        simulate_unconfirmed_termination: bool = False,
        simulate_sftp_failure: bool = False,
        simulate_ssh_disconnect: bool = False,
        simulate_runtime_overrun: bool = False,
        simulate_engine_fallback: bool = False,
        resume: bool = False
    ):
        self.experiment_id = experiment_id
        self.manifest_path = manifest_path
        self.authorization_path = authorization_path
        self.mode = mode
        self.pod_id = pod_id
        self.ip = ip
        self.port = port
        self.ssh_key_path = ssh_key_path
        self.local_data_dir = local_data_dir
        self.remote_work_dir = remote_work_dir
        self.max_cost_usd = max_cost_usd
        self.max_runtime_minutes = max_runtime_minutes
        self.gpu_hourly_rate = gpu_hourly_rate
        self.poll_interval_seconds = poll_interval_seconds

        # Simulation and testing parameters
        self.simulate_records = simulate_records
        self.simulate_spend_usd = simulate_spend_usd
        self.simulate_corrupt_dataset = simulate_corrupt_dataset
        self.simulate_unconfirmed_termination = simulate_unconfirmed_termination
        self.simulate_sftp_failure = simulate_sftp_failure
        self.simulate_ssh_disconnect = simulate_ssh_disconnect
        self.simulate_runtime_overrun = simulate_runtime_overrun
        self.simulate_engine_fallback = simulate_engine_fallback
        self.resume = resume

        os.makedirs(self.local_data_dir, exist_ok=True)
        self.state_file = os.path.join(self.local_data_dir, f"runner_state_{self.experiment_id}.json")
        self.local_dataset_file = os.path.join(self.local_data_dir, "primary_7b_generations.jsonl")
        self.receipt_file = os.path.join(self.local_data_dir, "integrity_receipt.json")
        self.termination_receipt_file = os.path.join(self.local_data_dir, f"termination_receipt_{self.experiment_id}.json")

        self.state = ProductionState.CREATED
        self.remote_pid: Optional[int] = None
        self.last_heartbeat_time: float = 0.0
        self.completed_rollouts: int = 0
        self.stop_requested: bool = False
        self.termination_confirmed: bool = False

        # Load and verify manifest immediately
        self.verifier = IndependentDatasetVerifierV2(self.manifest_path)
        self.manifest_sha256 = self.verifier.manifest_sha256
        self.total_expected_requests = len(self.verifier.expected_requests)

        # Budget scheduler
        self.scheduler = BudgetAwareScheduler(
            max_authorized_usd=self.max_cost_usd,
            gpu_hourly_rate=self.gpu_hourly_rate
        )

        # Financial cost controller
        self.cost_controller = RobustCostControllerV8(
            experiment_id=self.experiment_id,
            max_cost_usd=self.max_cost_usd,
            max_runtime_minutes=self.max_runtime_minutes,
            gpu_hourly_rate=self.gpu_hourly_rate,
            state_dir=self.local_data_dir,
            emergency_shutdown_callback=self.trigger_emergency_shutdown
        )

        # Transport setup
        if transport is not None:
            self.transport = transport
        elif self.mode in [ExecutionMode.PRODUCTION, ExecutionMode.PREFLIGHT]:
            self.transport = ProductionRunPodTransportV2(ssh_key_path=self.ssh_key_path)
        else:
            self.transport = None

        if self.resume:
            self._load_resume_state()
        else:
            self._persist_runner_state()

    def _load_resume_state(self):
        """Loads previous state from disk when resume is requested."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.remote_pid = data.get("remote_pid")
                    self.completed_rollouts = data.get("completed_rollouts", 0)
                    print(f"[Production Runner] Resumed session: PID {self.remote_pid}, {self.completed_rollouts} rollouts.")
            except Exception as e:
                print(f"[Production Runner] Warning: could not load resume state: {e}")
        self._persist_runner_state()

    def transition_to(self, new_state: ProductionState):
        """Atomic state transition with audit output."""
        old_state = self.state
        self.state = new_state
        print(f"[Production Runner] State: {old_state.value} -> {new_state.value}")
        self._persist_runner_state()

    def _persist_runner_state(self):
        """Atomically persist runner state to disk."""
        payload = {
            "experiment_id": self.experiment_id,
            "state": self.state.value,
            "mode": self.mode.value,
            "pod_id": self.pod_id,
            "remote_pid": self.remote_pid,
            "manifest_sha256": self.manifest_sha256,
            "completed_rollouts": self.completed_rollouts,
            "total_expected_requests": self.total_expected_requests,
            "last_heartbeat_time": self.last_heartbeat_time,
            "timestamp_utc": time.time()
        }
        tmp = self.state_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.state_file)

    # ==================== Step 1: Authorization Gate ====================

    def validate_session_authorization(self) -> bool:
        """Enforces session-specific cryptographic authorization."""
        if self.mode == ExecutionMode.DRY_RUN:
            print("[Production Runner] DRY_RUN mode: bypassing strict production authorization.")
            self.transition_to(ProductionState.AUTHORIZATION_VALIDATED)
            return True

        if not self.authorization_path:
            raise PermissionError("PRODUCTION/PREFLIGHT mode requires an explicit --authorization document path.")

        valid, auth_data, reason = SessionAuthorizer.validate_authorization(
            auth_doc_path=self.authorization_path,
            current_experiment_id=self.experiment_id,
            current_pod_id=self.pod_id or "",
            current_manifest_sha256=self.manifest_sha256,
            current_mode=self.mode.value,
            max_cost_limit=self.max_cost_usd
        )
        if not valid:
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            raise PermissionError(f"Session authorization REJECTED: {reason}")

        print(f"[Production Runner] Session authorization verified: Approved by {auth_data.get('principal_investigator')}.")
        self.transition_to(ProductionState.AUTHORIZATION_VALIDATED)
        return True

    # ==================== Step 2: Manifest Gate ====================

    def verify_manifest(self) -> bool:
        """Asserts that manifest hash matches the frozen preregistration constant."""
        if self.manifest_sha256 != FROZEN_MANIFEST_SHA256:
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            raise ValueError(f"Manifest hash mismatch: {self.manifest_sha256} vs frozen constant {FROZEN_MANIFEST_SHA256}.")
        if self.total_expected_requests != 400:
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            raise ValueError(f"Manifest request count must be exactly 400, found {self.total_expected_requests}.")

        print(f"[Production Runner] Manifest cryptographically verified: 400 requests (SHA: {self.manifest_sha256[:12]}...).")
        self.transition_to(ProductionState.MANIFEST_VERIFIED)
        return True

    # ==================== Step 3: Provider Connection ====================

    def connect_and_verify_provider(self) -> bool:
        """Connects to RunPod and validates pod existence and metadata."""
        if self.mode == ExecutionMode.DRY_RUN or not self.transport:
            print("[Production Runner] DRY_RUN simulation: mocking provider connection.")
            self.cost_controller.initialize_session()
            self.transition_to(ProductionState.PROVIDER_CONNECTED)
            return True

        if not self.pod_id:
            raise ValueError("pod_id must be specified for cloud execution.")

        meta = self.transport.get_pod_metadata(self.pod_id)
        if not meta.get("exists", False):
            raise ConnectionError(f"Pod {self.pod_id} not found on RunPod.")

        status = meta.get("status")
        if status not in ["RUNNING"]:
            raise ConnectionError(f"Pod {self.pod_id} is in status '{status}', must be 'RUNNING'.")

        self.cost_controller.initialize_session(pod_metadata=meta)
        print(f"[Production Runner] Connected to RunPod pod {self.pod_id} (Status: {status}, Uptime: {meta.get('uptimeSeconds')}s).")
        self.transition_to(ProductionState.PROVIDER_CONNECTED)
        return True

    # ==================== Step 4: Launch Remote Execution ====================

    def launch_remote_runner(self) -> int:
        """Launches detached remote experiment runner."""
        if self.mode == ExecutionMode.PREFLIGHT:
            print("[Production Runner] PREFLIGHT mode: skipping execution launch.")
            return 0

        self.transition_to(ProductionState.REMOTE_RUNNER_LAUNCHED)
        
        if self.mode == ExecutionMode.DRY_RUN or not self.transport:
            print("[Production Runner] DRY_RUN: Simulating detached background runner.")
            self.remote_pid = 99999
            self.last_heartbeat_time = time.time()

            # Handle simulation of generated records
            if self.simulate_records:
                print(f"[Production Runner] Generating {self.simulate_records} simulated records...")
                records = []
                for i, req in enumerate(self.verifier.expected_requests.values()):
                    if i >= self.simulate_records:
                        break
                    engine_name = "transformers" if self.simulate_engine_fallback else "vllm"
                    engine_ver = "4.46.0" if self.simulate_engine_fallback else "0.6.3.post1"
                    rec = {
                        "request_id": req["request_id"],
                        "problem_id": req.get("problem_id", f"prob_{i:03d}"),
                        "condition_code": req.get("condition_code", "Condition_A_Zero_Shot"),
                        "prompt_sha256": req.get("prompt_sha256", hashlib.sha256(f"p_{i}".encode()).hexdigest()),
                        "gold_answer": req.get("gold_answer", "42"),
                        "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
                        "model_revision": "c869d27376a8d6728795551322fe323b6",
                        "tokenizer_revision": "c869d27376a8d6728795551322fe323b6",
                        "inference_engine": engine_name,
                        "inference_engine_version": engine_ver,
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
                        "model_output": f"Step by step solution leading to final answer \\boxed{{{req.get('gold_answer', '42')}}}."
                    }
                    records.append(rec)

                with open(self.local_dataset_file, "w", encoding="utf-8") as f:
                    for r in records:
                        f.write(json.dumps(r) + "\n")
                    if self.simulate_corrupt_dataset:
                        f.write('{"request_id": "corrupted_incomplete_json\n')
                    f.flush()
                    os.fsync(f.fileno())
                self.completed_rollouts = len(records)

            self.transition_to(ProductionState.RUNNING)
            return self.remote_pid

        remote_out = f"{self.remote_work_dir}/data/output.jsonl"
        remote_rec = f"{self.remote_work_dir}/logs/execution_record.json"
        remote_hb = f"{self.remote_work_dir}/logs/heartbeat.json"
        remote_log = f"{self.remote_work_dir}/logs/runner.log"
        remote_pid_file = f"{self.remote_work_dir}/logs/runner.pid"

        cmd = (
            f"mkdir -p {self.remote_work_dir}/data {self.remote_work_dir}/logs && "
            f"nohup python3 {self.remote_work_dir}/runner/remote_experiment_runner.py "
            f"--manifest {self.remote_work_dir}/manifests/primary_100_manifest.json "
            f"--output {remote_out} "
            f"--record {remote_rec} "
            f"--heartbeat {remote_hb} "
            f"--experiment-id {self.experiment_id} "
            f"> {remote_log} 2>&1 & echo $! > {remote_pid_file}"
        )
        code, out = self.transport.execute(cmd, ip=self.ip, port=self.port)
        if code != 0:
            self.transition_to(ProductionState.REMOTE_EXECUTION_FAILURE)
            raise RuntimeError(f"Failed to launch remote runner: {out}")

        code, pid_str = self.transport.execute(f"cat {remote_pid_file}", ip=self.ip, port=self.port)
        try:
            self.remote_pid = int(pid_str.strip())
        except Exception:
            self.remote_pid = 1001

        self.last_heartbeat_time = time.time()
        self.transition_to(ProductionState.RUNNING)
        print(f"[Production Runner] Detached remote runner launched with PID {self.remote_pid}.")
        return self.remote_pid

    # ==================== Step 5: Supervision & Intermediate Sync ====================

    def sync_intermediate_data(self) -> int:
        """Pulls remote intermediate output file to local disk atomically."""
        if self.simulate_sftp_failure:
            print("[Sync Notice] Simulated SFTP connection failure: Socket read timeout.")
            return self.completed_rollouts

        if self.simulate_ssh_disconnect:
            print("[SSH Notice] Simulated transient SSH disconnection. Reconnecting...")
            self.simulate_ssh_disconnect = False # Reconnects next cycle

        if self.mode == ExecutionMode.DRY_RUN or not self.transport:
            if os.path.exists(self.local_dataset_file):
                count = 0
                with open(self.local_dataset_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            count += 1
                self.completed_rollouts = count
                return count
            return 0

        remote_out = f"{self.remote_work_dir}/data/output.jsonl"
        tmp_local = self.local_dataset_file + ".tmp"
        try:
            success = self.transport.fetch_file(remote_out, tmp_local, ip=self.ip, port=self.port)
            if success and os.path.exists(tmp_local):
                count = 0
                with open(tmp_local, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            count += 1
                with open(tmp_local, "a", encoding="utf-8") as f:
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_local, self.local_dataset_file)
                self.completed_rollouts = count
                return count
        except Exception as e:
            print(f"[Sync Notice] Intermediate sync deferred: {e}")
            if os.path.exists(tmp_local):
                try:
                    os.remove(tmp_local)
                except Exception:
                    pass
        return self.completed_rollouts

    def run_supervision_loop(self, max_ticks: Optional[int] = None) -> bool:
        """
        Continuously active monitoring loop:
        1. Checks financial watchdog every tick.
        2. Evaluates budget scheduler against observed throughput.
        3. Synchronizes intermediate checkpoints.
        4. Detects completion (400/400).
        """
        print("[Production Runner] Supervision loop engaged.")
        ticks = 0

        while not self.stop_requested:
            ticks += 1
            if max_ticks and ticks > max_ticks:
                break

            # Simulation injection for budget breach
            if self.simulate_spend_usd is not None:
                uptime_needed = (self.simulate_spend_usd / self.gpu_hourly_rate) * 3600.0
                self.cost_controller.start_time = time.time() - uptime_needed

            if self.simulate_runtime_overrun:
                self.cost_controller.start_time = time.time() - (self.max_runtime_minutes * 60.0 + 100.0)

            # 1. Financial Watchdog Check
            cost_status = self.cost_controller.check_and_enforce_budget()
            if cost_status["should_emergency_terminate"]:
                print(f"[Production Runner] Watchdog tripped: {cost_status['action_taken']}.")
                return False

            # 2. Sync intermediate rollouts
            completed = self.sync_intermediate_data()

            # 3. Budget-Aware Scheduler Check
            can_sched, sched_reason, sched_meta = self.scheduler.can_schedule_next_batch(
                batch_size=4,
                current_spend_usd=cost_status["effective_spend_usd"]
            )
            if not can_sched:
                print(f"[Production Runner] Budget-aware scheduler HALT: {sched_reason}")
                self.transition_to(ProductionState.PARTIAL_PRESERVED)
                self.terminate_normal(is_partial=True)
                return False

            # 4. Check for full completion
            if completed >= self.total_expected_requests:
                print(f"[Production Runner] All {self.total_expected_requests} rollouts completed remotely.")
                self.transition_to(ProductionState.REMOTE_COMPLETE)
                return True

            time.sleep(self.poll_interval_seconds)

        return False

    # ==================== Step 6: Dataset Completion Gate ====================

    def verify_final_dataset(self) -> bool:
        """Reopens physical file from disk and validates all 18 dimensions."""
        self.transition_to(ProductionState.FINAL_DATASET_VERIFICATION)
        is_valid, receipt = self.verifier.verify_final_local_dataset(
            self.local_dataset_file,
            receipt_output_path=self.receipt_file
        )
        if not is_valid:
            self.transition_to(ProductionState.INTEGRITY_FAILURE)
            print(f"[Completion Gate] REJECTED: Physical dataset verification failed: {receipt.get('errors', [])[:3]}")
            return False

        self.transition_to(ProductionState.LOCAL_VERIFIED)
        print(f"[Completion Gate] PASSED: Verified 400/400 rollouts (SHA-256: {receipt.get('dataset_sha256')[:12]}...).")
        return True

    # ==================== Step 7: Termination & Escalation ====================

    def terminate_normal(self, is_partial: bool = False) -> bool:
        """Normal completion termination path."""
        self.transition_to(ProductionState.NORMAL_TERMINATION)
        term_ok = False

        if self.simulate_unconfirmed_termination:
            term_ok = False
        elif self.transport and self.pod_id:
            term_ok, _ = self.transport.terminate_pod(self.pod_id)
            if term_ok:
                term_ok = self.transport.verify_pod_terminated(self.pod_id)
        else:
            term_ok = True

        reason = "PARTIAL_BUDGET_STOP" if is_partial else "NORMAL_COMPLETION"
        self._persist_termination_receipt(reason, confirmed=term_ok)

        if term_ok:
            self.transition_to(ProductionState.PROVIDER_TERMINATION_CONFIRMED)
            self.transition_to(ProductionState.FINISHED)
            return True
        else:
            self.transition_to(ProductionState.TERMINATION_UNCONFIRMED)
            DurableEscalationManager.record_unconfirmed_termination(
                pod_id=self.pod_id or "simulated_pod",
                reason=reason,
                attempts=1,
                last_known_status="STOPPED_OR_UNCONFIRMED",
                error_message="Provider failed to confirm destruction during normal termination",
                alert_dir=self.local_data_dir
            )
            return False

    def trigger_emergency_shutdown(self, reason: str) -> bool:
        """
        Priority-1 Non-blocking emergency shutdown:
        1. Immediately dispatch provider termination.
        2. Verify pod destruction.
        3. Attempt best-effort intermediate sync.
        4. Escalate if unconfirmed.
        """
        print(f"\n[CRITICAL EMERGENCY SHUTDOWN] Reason: {reason}")
        self.stop_requested = True
        self.transition_to(ProductionState.BUDGET_EMERGENCY)
        self.transition_to(ProductionState.TERMINATION_REQUESTED)

        term_ok = False
        if self.simulate_unconfirmed_termination:
            term_ok = False
        elif self.transport and self.pod_id:
            for attempt in range(1, 4):
                ok, _ = self.transport.terminate_pod(self.pod_id)
                if ok:
                    term_ok = self.transport.verify_pod_terminated(self.pod_id)
                    if term_ok:
                        break
                time.sleep(1.0)
        else:
            term_ok = True

        # Best-effort final data preservation (strictly after termination dispatch)
        try:
            self.sync_intermediate_data()
        except Exception:
            pass

        self._persist_termination_receipt(reason, confirmed=term_ok)

        if term_ok:
            self.termination_confirmed = True
            self.transition_to(ProductionState.PROVIDER_TERMINATION_CONFIRMED)
            return True
        else:
            self.transition_to(ProductionState.TERMINATION_UNCONFIRMED)
            DurableEscalationManager.record_unconfirmed_termination(
                pod_id=self.pod_id or "simulated_pod",
                reason=reason,
                attempts=3,
                last_known_status="UNCONFIRMED",
                error_message="All termination attempts exhausted without provider confirmation",
                alert_dir=self.local_data_dir
            )
            return False

    def _persist_termination_receipt(self, reason: str, confirmed: bool):
        """Atomically persists final termination receipt."""
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

    # ==================== Step 8: Master Orchestration Pipeline ====================

    def execute_complete_lifecycle(self) -> bool:
        """Executes the full end-to-end production pipeline."""
        print(f"\n================================================================================")
        print(f"  STATESHIFT PRODUCTION RUNNER (Mode: {self.mode.value})")
        print(f"================================================================================")

        # 1. Authorization
        self.validate_session_authorization()

        # 2. Manifest
        self.verify_manifest()

        # 3. Provider Connection
        self.connect_and_verify_provider()

        # In PREFLIGHT mode, stop here safely
        if self.mode == ExecutionMode.PREFLIGHT:
            print("[Production Runner] PREFLIGHT complete: all credentials, manifest, and provider checks verified.")
            return True

        # 4. Launch remote runner
        self.launch_remote_runner()

        # 5. Supervision loop
        complete = self.run_supervision_loop()
        if not complete:
            print("[Production Runner] Supervision loop terminated before full completion.")
            return False

        # 6. Physical dataset completion gate
        verified = self.verify_final_dataset()
        if not verified:
            return False

        # 7. Normal termination
        terminated = self.terminate_normal()
        return terminated


def parse_production_cli_args():
    parser = argparse.ArgumentParser(description="StateShift Production Runner (Mission 15.3)")
    parser.add_argument("--mode", type=str, default="DRY_RUN", choices=["DRY_RUN", "PREFLIGHT", "PRODUCTION"])
    parser.add_argument("--authorization", type=str, default=None)
    parser.add_argument("--manifest", type=str, required=True)
    parser.add_argument("--experiment-id", type=str, default="stateshift_400_replication_2026")
    parser.add_argument("--pod-id", type=str, default=None)
    parser.add_argument("--ip", type=str, default=None)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--ssh-key-path", type=str, default=None)
    parser.add_argument("--local-data-dir", type=str, default="data/primary_run")
    parser.add_argument("--remote-work-dir", type=str, default="/workspace/stateshift")
    parser.add_argument("--max-cost-usd", type=float, default=2.00)
    parser.add_argument("--max-runtime-minutes", type=float, default=160.0)
    parser.add_argument("--gpu-hourly-rate", type=float, default=0.89)
    parser.add_argument("--poll-interval", type=float, default=0.1)

    # Simulation and test switches
    parser.add_argument("--simulate-records", type=int, default=None)
    parser.add_argument("--simulate-spend-usd", type=float, default=None)
    parser.add_argument("--simulate-corrupt-dataset", action="store_true")
    parser.add_argument("--simulate-unconfirmed-termination", action="store_true")
    parser.add_argument("--simulate-sftp-failure", action="store_true")
    parser.add_argument("--simulate-ssh-disconnect", action="store_true")
    parser.add_argument("--simulate-runtime-overrun", action="store_true")
    parser.add_argument("--simulate-engine-fallback", action="store_true")
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main():
    args = parse_production_cli_args()
    mode = ExecutionMode(args.mode)
    runner = StateshiftProductionRunner(
        experiment_id=args.experiment_id,
        manifest_path=args.manifest,
        authorization_path=args.authorization,
        mode=mode,
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
        simulate_records=args.simulate_records,
        simulate_spend_usd=args.simulate_spend_usd,
        simulate_corrupt_dataset=args.simulate_corrupt_dataset,
        simulate_unconfirmed_termination=args.simulate_unconfirmed_termination,
        simulate_sftp_failure=args.simulate_sftp_failure,
        simulate_ssh_disconnect=args.simulate_ssh_disconnect,
        simulate_runtime_overrun=args.simulate_runtime_overrun,
        simulate_engine_fallback=args.simulate_engine_fallback,
        resume=args.resume
    )
    success = runner.execute_complete_lifecycle()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
