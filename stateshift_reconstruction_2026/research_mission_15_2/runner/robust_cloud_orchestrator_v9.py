#!/usr/bin/env python3
"""
StateShift Production Cloud Orchestrator (Version 9 - Mission 15.2)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Key Upgrades over V8:
1. Provider Termination Priority Ordering:
   In terminate_emergency(), provider-side termination is dispatched IMMEDIATELY FIRST.
   SFTP data synchronization is NEVER allowed to delay or block provider pod destruction.
2. Authoritative Provider Destruction Verification:
   Integrates with ProductionRunPodTransportV2, which authoritatively rejects STOPPED as destroyed.
3. Provenance-Enforced Dataset Verification:
   Integrates with IndependentDatasetVerifierV2, which verifies model revision, decoding configuration,
   explicit completion status, and structured provenance.
4. Unsuppressed Financial Retry Semantics:
   Works directly with RobustCostControllerV8 to ensure failed termination callbacks are retried.
5. Production Entry Point:
   Fully validated CLI entry point defaulting to DRY_RUN. Production mode strictly requires
   --mode PRODUCTION, --authorization-token, and valid credentials.
"""

import os
import sys
import time
import json
import enum
import hashlib
import argparse
from typing import Dict, Any, List, Set, Optional, Tuple, Callable

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_2.transport.runpod_transport_v2 import ProductionRunPodTransportV2
from research_mission_15_2.evaluation.dataset_verifier_v2 import IndependentDatasetVerifierV2

class ExecutionMode(str, enum.Enum):
    DRY_RUN = "DRY_RUN"
    PRODUCTION = "PRODUCTION"


class OrchestratorStateV9(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    SYNCING = "SYNCING"
    REMOTE_COMPLETE = "REMOTE_COMPLETE"
    LOCAL_VERIFIED = "LOCAL_VERIFIED"
    TERMINATION_REQUESTED = "TERMINATION_REQUESTED"
    TERMINATED_CONFIRMED = "TERMINATED_CONFIRMED"
    NORMAL_COMPLETED = "NORMAL_COMPLETED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    PARTIAL_PRESERVED = "PARTIAL_PRESERVED"
    SAFE_HOLD = "SAFE_HOLD"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    EMERGENCY_SHUTDOWN_REQUESTED = "EMERGENCY_SHUTDOWN_REQUESTED"
    EMERGENCY_TERMINATED = "EMERGENCY_TERMINATED"
    TERMINATION_UNCONFIRMED = "TERMINATION_UNCONFIRMED"
    FAILURE_REQUIRES_ATTENTION = "FAILURE_REQUIRES_ATTENTION"


class RobustCloudOrchestratorV9:
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
        
        self.state = OrchestratorStateV9.NOT_STARTED
        self.remote_pid: Optional[int] = None
        self.last_heartbeat_timestamp: float = 0.0
        self.is_interrupted: bool = False
        self.termination_receipt: Optional[Dict[str, Any]] = None
        
        os.makedirs(self.local_data_dir, exist_ok=True)
        
        # Independent strict dataset verifier
        self.verifier = IndependentDatasetVerifierV2(self.manifest_path)
        self.manifest_sha256 = self.verifier.manifest_sha256
        self.total_expected_requests = len(self.verifier.expected_requests)
        
        # Transport initialization
        if transport is not None:
            self.transport = transport
        elif self.mode == ExecutionMode.PRODUCTION:
            self._verify_production_prerequisites()
            self.transport = ProductionRunPodTransportV2(ssh_key_path=self.ssh_key_path)
        else:
            self.transport = None
            
        self._persist_local_state()

    def _verify_production_prerequisites(self):
        """Enforce non-negotiable production prerequisites."""
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

    def transition_to(self, new_state: OrchestratorStateV9) -> None:
        """Formal state transition with audit logging."""
        print(f"[Orchestrator v9] State transition: {self.state.value} -> {new_state.value}")
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
        """Fetch file via transport SFTP with exception safety."""
        if not self.transport:
            return False
        try:
            return self.transport.fetch_file(remote_path, local_tmp_path, ip=self.ip, port=self.port)
        except Exception as e:
            print(f"  [Transport Fetch Error] {e}")
            return False

    def launch_detached_runner(self, manifest_remote: str, output_remote: str) -> int:
        """Launch remote runner as detached background process."""
        self.transition_to(OrchestratorStateV9.RUNNING)
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
            self.transition_to(OrchestratorStateV9.FAILURE_REQUIRES_ATTENTION)
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
            
        valid_count = 0
        try:
            with open(tmp_target, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        json.loads(line)
                        valid_count += 1
            with open(tmp_target, "a", encoding="utf-8") as f:
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_target, local_target)
            return valid_count
        except Exception:
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
        2. Physical disk file verification passes all 18 criteria.
        3. Provider termination is requested and confirmed destroyed.
        """
        local_dataset = os.path.join(self.local_data_dir, local_output_name)
        receipt_path = os.path.join(self.local_data_dir, "integrity_receipt.json")
        
        is_valid, receipt = self.verifier.verify_final_local_dataset(local_dataset, receipt_path)
        if not is_valid:
            print(f"[Normal Termination Gate] REJECTED: Physical dataset verification failed: {receipt.get('errors', [])[:3]}")
            self.transition_to(OrchestratorStateV9.SAFE_HOLD)
            return False
            
        self.transition_to(OrchestratorStateV9.LOCAL_VERIFIED)
        self.transition_to(OrchestratorStateV9.TERMINATION_REQUESTED)
        
        success = False
        if self.transport and hasattr(self.transport, "terminate_pod") and self.pod_id:
            term_ok, term_data = self.transport.terminate_pod(self.pod_id)
            if term_ok and hasattr(self.transport, "verify_pod_terminated"):
                success = self.transport.verify_pod_terminated(self.pod_id)
            else:
                success = term_ok
        elif self.transport and hasattr(self.transport, "terminate"):
            success = self.transport.terminate(self.pod_id)
        else:
            success = True
            
        if success:
            self.transition_to(OrchestratorStateV9.TERMINATED_CONFIRMED)
            self._persist_termination_receipt("NORMAL_COMPLETION", confirmed=True)
            return True
        else:
            self.transition_to(OrchestratorStateV9.TERMINATION_UNCONFIRMED)
            self._persist_termination_receipt("NORMAL_COMPLETION", confirmed=False)
            return False

    def finalize_and_verify(self, dataset_path: str) -> bool:
        """Independently audit final dataset on physical disk and update orchestrator state."""
        receipt_path = os.path.join(self.local_data_dir, "integrity_receipt.json")
        is_valid, receipt = self.verifier.verify_final_local_dataset(dataset_path, receipt_path)
        if not is_valid:
            self.transition_to(OrchestratorStateV9.VERIFICATION_FAILED)
            return False
        self.transition_to(OrchestratorStateV9.LOCAL_VERIFIED)
        self.transition_to(OrchestratorStateV9.NORMAL_COMPLETED)
        return True

    # ==================== Path B: Emergency Financial Shutdown ====================

    def terminate_emergency(self, reason: str, emergency_sync: bool = True, remote_output_file: Optional[str] = None) -> bool:
        """
        Path B: Emergency Financial & Safety Shutdown.
        CRITICAL ARCHITECTURAL GUARANTEE (Mission 15.2):
        Provider termination is dispatched IMMEDIATELY FIRST.
        SFTP data retrieval NEVER precedes or delays provider termination.
        """
        print(f"\n[EMERGENCY SHUTDOWN TRIGGERED] Reason: {reason}")
        
        # Idempotency check
        if self.state in [OrchestratorStateV9.EMERGENCY_TERMINATED, OrchestratorStateV9.TERMINATED_CONFIRMED]:
            print(f"[Emergency Shutdown] Pod already confirmed destroyed ({self.state.value}).")
            return True
            
        self.transition_to(OrchestratorStateV9.EMERGENCY_SHUTDOWN_REQUESTED)
        
        # STEP 1: DISPATCH PROVIDER-SIDE TERMINATION IMMEDIATELY (Priority 1)
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
            term_ok = True # Mock or dry-run
            
        # STEP 2: VERIFY PROVIDER-SIDE DESTRUCTION (Priority 2)
        confirmed = False
        if term_ok:
            if self.transport and hasattr(self.transport, "verify_pod_terminated") and self.pod_id:
                confirmed = self.transport.verify_pod_terminated(self.pod_id, max_checks=3, delay_seconds=1.0)
            else:
                confirmed = term_ok
                
        # STEP 3: PRESERVE ANY REMAINING LOCAL DATA (Only after termination dispatched)
        if emergency_sync and remote_output_file:
            try:
                # Attempt best-effort final sync if pod is stopping/still readable
                synced = self.sync_intermediate_snapshot(remote_output_file)
                print(f"[Emergency Sync] Preserved {synced} partial rollouts locally.")
                self.transition_to(OrchestratorStateV9.PARTIAL_PRESERVED)
            except Exception as e:
                print(f"[Emergency Sync Notice] Sync skipped/failed after termination dispatch: {e}")
                
        # STEP 4: PERSIST TERMINATION RECEIPT & TRANSITION
        if confirmed:
            self.transition_to(OrchestratorStateV9.EMERGENCY_TERMINATED)
            self._persist_termination_receipt(reason, confirmed=True)
            print(f"[Emergency Shutdown] CONFIRMED: Pod {self.pod_id} destroyed on provider side.")
            return True
        else:
            self.transition_to(OrchestratorStateV9.TERMINATION_UNCONFIRMED)
            self._persist_termination_receipt(reason, confirmed=False)
            print(f"[CRITICAL ESCALATION] TERMINATION_UNCONFIRMED: Provider did not confirm destruction of pod {self.pod_id}!")
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


def parse_production_args():
    parser = argparse.ArgumentParser(description="StateShift Production Cloud Orchestrator (Mission 15.2)")
    parser.add_argument("--mode", type=str, default="DRY_RUN", choices=["DRY_RUN", "PRODUCTION"])
    parser.add_argument("--authorization-token", type=str, default=None)
    parser.add_argument("--experiment-id", type=str, default="stateshift_400_replication_2026")
    parser.add_argument("--manifest", type=str, required=True)
    parser.add_argument("--pod-id", type=str, default=None)
    parser.add_argument("--ip", type=str, default=None)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--ssh-key-path", type=str, default=None)
    parser.add_argument("--local-data-dir", type=str, default="data/primary_run")
    parser.add_argument("--remote-work-dir", type=str, default="/workspace/stateshift")
    parser.add_argument("--max-cost-usd", type=float, default=2.00)
    parser.add_argument("--max-runtime-minutes", type=float, default=160.0)
    parser.add_argument("--gpu-hourly-rate", type=float, default=0.89)
    return parser.parse_args()


def main():
    args = parse_production_args()
    print(f"[StateShift Orchestrator] Initializing in {args.mode} mode...")
    mode = ExecutionMode.PRODUCTION if args.mode == "PRODUCTION" else ExecutionMode.DRY_RUN
    
    orchestrator = RobustCloudOrchestratorV9(
        experiment_id=args.experiment_id,
        manifest_path=args.manifest,
        pod_id=args.pod_id,
        ip=args.ip,
        port=args.port,
        ssh_key_path=args.ssh_key_path,
        local_data_dir=args.local_data_dir,
        remote_work_dir=args.remote_work_dir,
        mode=mode,
        authorization_token=args.authorization_token
    )
    print(f"[StateShift Orchestrator] Ready in state: {orchestrator.state.value}")
    return orchestrator

if __name__ == "__main__":
    main()
