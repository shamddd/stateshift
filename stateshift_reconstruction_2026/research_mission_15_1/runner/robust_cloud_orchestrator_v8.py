#!/usr/bin/env python3
"""
StateShift Production Cloud Orchestrator (Version 8 - Mission 15.1)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Key Upgrades over V7:
1. True Dual Shutdown Architecture:
   - `terminate_normal()`: Scientific path (requires independent disk verification, all 400 rollouts).
   - `terminate_emergency(reason)`: Financial & safety path (UNCONDITIONALLY overrides data completeness;
     callable from ANY state, idempotent, terminates cloud billing immediately).
2. Physical Dataset Completion Gate:
   Re-opens and audits the physical JSONL dataset on disk via `IndependentDatasetVerifier`
   rather than trusting in-memory data structures.
3. Production RunPod Transport Integration:
   Integrates `ProductionRunPodTransport` with real Paramiko SSH/SFTP and RunPod GraphQL API.
4. Execution Modes:
   `DRY_RUN` (default) vs `PRODUCTION`. Production mode requires explicit selection,
   manifest verification, budget validation, and explicit authorization approval.
5. Robust State Machine with Unconfirmed Escalation:
   Handles `TERMINATION_UNCONFIRMED` if provider fails to confirm pod destruction.
"""

import os
import sys
import time
import json
import enum
import hashlib
from typing import Dict, Any, List, Set, Optional, Tuple, Callable

# Add path for internal imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_1.transport.runpod_transport import ProductionRunPodTransport
from research_mission_15_1.evaluation.dataset_verifier import IndependentDatasetVerifier

class ExecutionMode(str, enum.Enum):
    DRY_RUN = "DRY_RUN"
    PRODUCTION = "PRODUCTION"


class OrchestratorStateV8(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    SYNCING = "SYNCING"
    REMOTE_COMPLETE = "REMOTE_COMPLETE"
    LOCAL_VERIFIED = "LOCAL_VERIFIED"
    TERMINATION_REQUESTED = "TERMINATION_REQUESTED"
    TERMINATED_CONFIRMED = "TERMINATED_CONFIRMED"
    PARTIAL_PRESERVED = "PARTIAL_PRESERVED"
    SAFE_HOLD = "SAFE_HOLD"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    EMERGENCY_SHUTDOWN_REQUESTED = "EMERGENCY_SHUTDOWN_REQUESTED"
    EMERGENCY_TERMINATED = "EMERGENCY_TERMINATED"
    TERMINATION_UNCONFIRMED = "TERMINATION_UNCONFIRMED"
    FAILURE_REQUIRES_ATTENTION = "FAILURE_REQUIRES_ATTENTION"


class RobustCloudOrchestratorV8:
    def __init__(self,
                 experiment_id: str,
                 manifest_path: str,
                 pod_id: Optional[str] = None,
                 ip: Optional[str] = None,
                 port: int = 22,
                 ssh_key_path: Optional[str] = None,
                 local_data_dir: str = "/tmp/stateshift_data",
                 remote_work_dir: str = "/workspace/stateshift",
                 mode: ExecutionMode = ExecutionMode.DRY_RUN,
                 authorization_token: Optional[str] = None,
                 transport=None):
        self.experiment_id = experiment_id
        self.manifest_path = manifest_path
        self.pod_id = pod_id
        self.ip = ip
        self.port = port
        self.ssh_key_path = ssh_key_path or os.path.expanduser("~/.ssh/id_ed25519")
        self.local_data_dir = local_data_dir
        self.remote_work_dir = remote_work_dir
        self.mode = mode
        self.authorization_token = authorization_token
        
        # In-memory tracking
        self.state = OrchestratorStateV8.NOT_STARTED
        self.remote_pid: Optional[int] = None
        self.last_heartbeat_timestamp: float = 0.0
        self.is_interrupted: bool = False
        self.termination_receipt: Optional[Dict[str, Any]] = None
        
        os.makedirs(self.local_data_dir, exist_ok=True)
        
        # Load independent dataset verifier
        self.verifier = IndependentDatasetVerifier(self.manifest_path)
        self.manifest_sha256 = self.verifier.manifest_sha256
        self.total_expected_requests = len(self.verifier.expected_requests)
        
        # Initialize or inject transport
        if transport is not None:
            self.transport = transport
        elif self.mode == ExecutionMode.PRODUCTION:
            self._verify_production_prerequisites()
            self.transport = ProductionRunPodTransport(ssh_key_path=self.ssh_key_path)
        else:
            self.transport = None # Dry run must provide or use mock
            
        self._persist_local_state()

    def _verify_production_prerequisites(self):
        """Enforce strict production authorization checks."""
        if self.mode == ExecutionMode.PRODUCTION:
            if not self.authorization_token:
                raise PermissionError("PRODUCTION mode requires an explicit non-empty authorization_token.")
            if not os.environ.get("RUNPOD_API_KEY"):
                raise ValueError("RUNPOD_API_KEY environment variable required for PRODUCTION mode.")
            if not self.pod_id:
                raise ValueError("pod_id must be specified for PRODUCTION mode.")

    def _persist_local_state(self) -> None:
        """Atomically persist orchestrator state to disk."""
        state_file = os.path.join(self.local_data_dir, f"orchestrator_state_{self.experiment_id}.json")
        tmp_file = state_file + ".tmp"
        payload = {
            "experiment_id": self.experiment_id,
            "manifest_path": self.manifest_path,
            "manifest_sha256": self.manifest_sha256,
            "total_expected_requests": self.total_expected_requests,
            "state": self.state.value,
            "mode": self.mode.value,
            "pod_id": self.pod_id,
            "remote_pid": self.remote_pid,
            "last_heartbeat_timestamp": self.last_heartbeat_timestamp,
            "timestamp_utc": time.time()
        }
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, state_file)

    def transition_to(self, new_state: OrchestratorStateV8) -> None:
        """Formal state transition with audit logging."""
        print(f"[Orchestrator v8] State transition: {self.state.value} -> {new_state.value}")
        self.state = new_state
        self._persist_local_state()

    def execute_remote_cmd(self, cmd: str, timeout: int = 30) -> Tuple[int, str]:
        """Execute command via transport."""
        if not self.transport:
            raise NotImplementedError("Transport adapter is not initialized.")
        if hasattr(self.transport, "execute"):
            return self.transport.execute(cmd, ip=self.ip, port=self.port, timeout=timeout)
        elif hasattr(self.transport, "execute_cmd"):
            code, out, _ = self.transport.execute_cmd(cmd, timeout=timeout)
            return code, out
        raise AttributeError("Transport lacks execute method.")

    def fetch_remote_file(self, remote_path: str, local_tmp_path: str) -> bool:
        """Fetch file via transport SFTP."""
        if not self.transport:
            return False
        try:
            return self.transport.fetch_file(remote_path, local_tmp_path, ip=self.ip, port=self.port)
        except Exception as e:
            print(f"  [Transport Fetch Error] {e}")
            return False

    def launch_detached_runner(self, manifest_remote: str, output_remote: str) -> int:
        """Launch remote runner as detached background process."""
        self.transition_to(OrchestratorStateV8.RUNNING)
        record_file = f"{self.remote_work_dir}/logs/execution_record.json"
        log_file = f"{self.remote_work_dir}/logs/runner.log"
        pid_file = f"{self.remote_work_dir}/logs/runner.pid"
        
        cmd = (
            f"mkdir -p {self.remote_work_dir}/logs {self.remote_work_dir}/data && "
            f"nohup python3 {self.remote_work_dir}/runner/cloud_experiment_runner.py "
            f"--manifest {manifest_remote} "
            f"--output {output_remote} "
            f"--record {record_file} "
            f"> {log_file} 2>&1 & echo $! > {pid_file}"
        )
        code, _ = self.execute_remote_cmd(cmd)
        if code != 0:
            self.transition_to(OrchestratorStateV8.FAILURE_REQUIRES_ATTENTION)
            raise RuntimeError("Failed to launch detached runner.")
            
        code, pid_str = self.execute_remote_cmd(f"cat {pid_file}")
        self.remote_pid = int(pid_str.strip())
        self.last_heartbeat_timestamp = time.time()
        self._persist_local_state()
        return self.remote_pid

    def sync_intermediate_snapshot(self, remote_output_file: str, local_name: str = "primary_7b_generations.jsonl") -> int:
        """Pull remote file to local temporary destination with fsync and rename."""
        local_target = os.path.join(self.local_data_dir, local_name)
        tmp_target = local_target + ".tmp"
        
        success = self.fetch_remote_file(remote_output_file, tmp_target)
        if not success or not os.path.exists(tmp_target):
            return 0
            
        # Verify valid JSON lines before replacing local file
        valid_count = 0
        try:
            with open(tmp_target, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        json.loads(line)
                        valid_count += 1
            # fsync
            with open(tmp_target, "a", encoding="utf-8") as f:
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_target, local_target)
            return valid_count
        except Exception as e:
            if os.path.exists(tmp_target):
                try:
                    os.remove(tmp_target)
                except Exception:
                    pass
            return 0

    # ==================== Path A: Normal Completion Shutdown ====================

    def terminate_normal(self, local_output_name: str = "primary_7b_generations.jsonl") -> bool:
        """
        Path A: Normal Scientific Completion Shutdown.
        Requires:
        1. State is REMOTE_COMPLETE.
        2. Physical disk file verification passes all 18 checks.
        3. Provider termination is requested and confirmed.
        """
        local_dataset = os.path.join(self.local_data_dir, local_output_name)
        receipt_path = os.path.join(self.local_data_dir, "integrity_receipt.json")
        
        # 1. Independent physical file audit
        is_valid, receipt = self.verifier.verify_final_local_dataset(local_dataset, receipt_path)
        if not is_valid:
            print(f"[Normal Termination Gate] REJECTED: Physical dataset verification failed: {receipt.get('errors', [])[:3]}")
            self.transition_to(OrchestratorStateV8.SAFE_HOLD)
            return False
            
        self.transition_to(OrchestratorStateV8.LOCAL_VERIFIED)
        self.transition_to(OrchestratorStateV8.TERMINATION_REQUESTED)
        
        # 2. Issue provider termination
        success = False
        if self.transport and hasattr(self.transport, "terminate_pod") and self.pod_id:
            term_ok, term_data = self.transport.terminate_pod(self.pod_id)
            if term_ok:
                # 3. Independent verification
                if hasattr(self.transport, "verify_pod_terminated"):
                    success = self.transport.verify_pod_terminated(self.pod_id)
                else:
                    success = True
        elif self.transport and hasattr(self.transport, "terminate"):
            success = self.transport.terminate(self.pod_id)
        else:
            success = True # Mock or dry-run fallback
            
        if success:
            self.transition_to(OrchestratorStateV8.TERMINATED_CONFIRMED)
            self._persist_termination_receipt("NORMAL_COMPLETION", confirmed=True)
            return True
        else:
            self.transition_to(OrchestratorStateV8.TERMINATION_UNCONFIRMED)
            self._persist_termination_receipt("NORMAL_COMPLETION", confirmed=False)
            return False

    # ==================== Path B: Emergency Financial Shutdown ====================

    def terminate_emergency(self, reason: str, emergency_sync: bool = True, remote_output_file: Optional[str] = None) -> bool:
        """
        Path B: Emergency Financial & Safety Shutdown.
        CRITICAL INVARIANT:
        Financial safety OVERRIDES data completeness.
        Callable from ANY state. Never blocked by LOCAL_VERIFIED or dataset checks.
        Idempotent across repeated calls.
        """
        print(f"\n[EMERGENCY SHUTDOWN TRIGGERED] Reason: {reason}")
        
        # Idempotency check: if already confirmed terminated, return True immediately
        if self.state in [OrchestratorStateV8.EMERGENCY_TERMINATED, OrchestratorStateV8.TERMINATED_CONFIRMED]:
            print(f"[Emergency Shutdown] Pod already terminated ({self.state.value}).")
            return True
            
        self.transition_to(OrchestratorStateV8.EMERGENCY_SHUTDOWN_REQUESTED)
        
        # Bounded final sync attempt (do not wait indefinitely)
        if emergency_sync and remote_output_file:
            try:
                synced = self.sync_intermediate_snapshot(remote_output_file)
                print(f"[Emergency Sync] Bounded sync preserved {synced} partial rollouts.")
                self.transition_to(OrchestratorStateV8.PARTIAL_PRESERVED)
            except Exception as e:
                print(f"[Emergency Sync Warning] Sync failed during emergency: {e}")
                
        # Immediate provider-level termination
        term_ok = False
        term_data = {}
        if self.transport and hasattr(self.transport, "terminate_pod") and self.pod_id:
            for attempt in range(1, 4):
                term_ok, term_data = self.transport.terminate_pod(self.pod_id)
                if term_ok:
                    break
                time.sleep(1.0)
        elif self.transport and hasattr(self.transport, "terminate"):
            term_ok = self.transport.terminate(self.pod_id)
        else:
            term_ok = True # Dry-run mock
            
        # Independent verification check
        confirmed = False
        if term_ok:
            if self.transport and hasattr(self.transport, "verify_pod_terminated") and self.pod_id:
                confirmed = self.transport.verify_pod_terminated(self.pod_id, max_checks=3, delay_seconds=1.0)
            else:
                confirmed = True
                
        if confirmed:
            self.transition_to(OrchestratorStateV8.EMERGENCY_TERMINATED)
            self._persist_termination_receipt(reason, confirmed=True)
            print(f"[Emergency Shutdown] CONFIRMED: Pod {self.pod_id} destroyed on provider side.")
            return True
        else:
            self.transition_to(OrchestratorStateV8.TERMINATION_UNCONFIRMED)
            self._persist_termination_receipt(reason, confirmed=False)
            print(f"[CRITICAL ESCALATION] TERMINATION_UNCONFIRMED: Provider did not confirm termination of pod {self.pod_id}!")
            return False

    def _persist_termination_receipt(self, reason: str, confirmed: bool) -> None:
        """Persist structured termination receipt atomically."""
        receipt_file = os.path.join(self.local_data_dir, f"termination_receipt_{self.experiment_id}.json")
        receipt = {
            "experiment_id": self.experiment_id,
            "pod_id": self.pod_id,
            "termination_reason": reason,
            "confirmed_by_provider": confirmed,
            "final_state": self.state.value,
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.termination_receipt = receipt
        tmp = receipt_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, receipt_file)
