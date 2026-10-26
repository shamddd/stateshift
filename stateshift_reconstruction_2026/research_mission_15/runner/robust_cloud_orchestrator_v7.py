#!/usr/bin/env python3
"""
StateShift Robust Cloud Orchestrator (Version 7 - Mission 15)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Core Invariants for Zero-Loss Execution:
1. Formal State Machine:
   NOT_STARTED -> RUNNING -> SYNCING -> REMOTE_COMPLETE -> LOCAL_VERIFIED -> TERMINATION_REQUESTED -> TERMINATED_CONFIRMED
   Failure branches: SAFE_HOLD, BUDGET_EXCEEDED, INTERRUPTED.
2. Durable Execution Record:
   Remote record tracks experiment_id, manifest_hash, model_revision, pid, heartbeat, and completed request IDs.
3. Two-Tier Process Liveness Verification:
   Does NOT rely solely on `kill -0`. Validates remote heartbeat freshness (stale threshold: 120s).
4. Safe Snapshot Incremental SFTP Synchronization:
   - SFTP download to temporary file (.tmp)
   - Line-by-line JSON syntax validation
   - Schema and record completeness checks
   - Deduplication and manifest cross-validation
   - Deterministic disk flush via os.fsync
   - Atomic rename to target snapshot file
5. Immutable Completion Gate:
   The pod is NEVER terminated until exactly the pre-registered manifest count (e.g. 400 requests)
   has been locally verified on disk. If unverified, orchestrator enters SAFE_HOLD.
"""

import os
import sys
import time
import json
import enum
import hashlib
from typing import Dict, Any, List, Set, Optional, Tuple

class OrchestratorState(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    SYNCING = "SYNCING"
    REMOTE_COMPLETE = "REMOTE_COMPLETE"
    LOCAL_VERIFIED = "LOCAL_VERIFIED"
    TERMINATION_REQUESTED = "TERMINATION_REQUESTED"
    TERMINATED_CONFIRMED = "TERMINATED_CONFIRMED"
    SAFE_HOLD = "SAFE_HOLD"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    INTERRUPTED = "INTERRUPTED"


class ManifestValidationError(Exception):
    pass


class SyncValidationError(Exception):
    pass


class RobustCloudOrchestratorV7:
    def __init__(self,
                 experiment_id: str,
                 manifest_path: str,
                 pod_id: Optional[str] = None,
                 ip: Optional[str] = None,
                 port: int = 22,
                 ssh_key_path: Optional[str] = None,
                 local_data_dir: str = "/tmp/stateshift_data",
                 remote_work_dir: str = "/workspace/stateshift",
                 max_runtime_minutes: float = 60.0,
                 heartbeat_timeout_seconds: float = 120.0,
                 sync_interval_seconds: float = 30.0,
                 transport=None):
        self.experiment_id = experiment_id
        self.manifest_path = manifest_path
        self.pod_id = pod_id
        self.ip = ip
        self.port = port
        self.ssh_key_path = ssh_key_path or os.path.expanduser("~/.ssh/id_ed25519")
        self.local_data_dir = local_data_dir
        self.remote_work_dir = remote_work_dir
        self.max_runtime_minutes = max_runtime_minutes
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds
        self.sync_interval_seconds = sync_interval_seconds
        
        # State machine
        self.state = OrchestratorState.NOT_STARTED
        self.remote_pid: Optional[int] = None
        self.last_heartbeat_timestamp: float = 0.0
        self.verified_request_ids: Set[str] = set()
        self.manifest_request_ids: Set[str] = set()
        self.manifest_sha256: str = ""
        self.total_expected_requests: int = 0
        self.is_interrupted: bool = False
        self.termination_confirmed: bool = False
        
        # Transport adapter (allows SSHClient or mock transport for unit tests)
        self.transport = transport
        
        os.makedirs(self.local_data_dir, exist_ok=True)
        self._load_manifest()
        self._persist_local_state()

    def _load_manifest(self) -> None:
        """Load and cryptographically verify the experiment manifest."""
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")
            
        with open(self.manifest_path, "rb") as f:
            raw = f.read()
            self.manifest_sha256 = hashlib.sha256(raw).hexdigest()
            
        manifest_data = json.loads(raw.decode("utf-8"))
        requests = manifest_data.get("requests", [])
        self.manifest_request_ids = {r["request_id"] for r in requests if "request_id" in r}
        self.total_expected_requests = len(self.manifest_request_ids)
        
        if self.total_expected_requests != len(requests):
            raise ManifestValidationError("Duplicate request IDs detected in manifest.")

    def _persist_local_state(self) -> None:
        """Persist orchestrator state to local disk atomically."""
        state_file = os.path.join(self.local_data_dir, f"orchestrator_state_{self.experiment_id}.json")
        tmp_file = state_file + ".tmp"
        payload = {
            "experiment_id": self.experiment_id,
            "manifest_path": self.manifest_path,
            "manifest_sha256": self.manifest_sha256,
            "total_expected_requests": self.total_expected_requests,
            "verified_count": len(self.verified_request_ids),
            "state": self.state.value,
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

    def transition_to(self, new_state: OrchestratorState) -> None:
        """Transition orchestrator state with validation."""
        valid_transitions = {
            OrchestratorState.NOT_STARTED: [OrchestratorState.RUNNING, OrchestratorState.SAFE_HOLD, OrchestratorState.INTERRUPTED],
            OrchestratorState.RUNNING: [OrchestratorState.SYNCING, OrchestratorState.REMOTE_COMPLETE, OrchestratorState.SAFE_HOLD, OrchestratorState.BUDGET_EXCEEDED, OrchestratorState.INTERRUPTED],
            OrchestratorState.SYNCING: [OrchestratorState.RUNNING, OrchestratorState.REMOTE_COMPLETE, OrchestratorState.SAFE_HOLD, OrchestratorState.BUDGET_EXCEEDED, OrchestratorState.INTERRUPTED],
            OrchestratorState.REMOTE_COMPLETE: [OrchestratorState.LOCAL_VERIFIED, OrchestratorState.SAFE_HOLD],
            OrchestratorState.LOCAL_VERIFIED: [OrchestratorState.TERMINATION_REQUESTED, OrchestratorState.SAFE_HOLD],
            OrchestratorState.TERMINATION_REQUESTED: [OrchestratorState.TERMINATED_CONFIRMED, OrchestratorState.SAFE_HOLD],
            OrchestratorState.SAFE_HOLD: [OrchestratorState.SYNCING, OrchestratorState.RUNNING, OrchestratorState.TERMINATION_REQUESTED],
            OrchestratorState.BUDGET_EXCEEDED: [OrchestratorState.SYNCING, OrchestratorState.TERMINATION_REQUESTED],
            OrchestratorState.INTERRUPTED: [OrchestratorState.SYNCING, OrchestratorState.TERMINATION_REQUESTED],
            OrchestratorState.TERMINATED_CONFIRMED: []
        }
        if new_state not in valid_transitions.get(self.state, []):
            raise ValueError(f"Invalid state transition from {self.state.value} to {new_state.value}")
            
        print(f"[Orchestrator v7] State transition: {self.state.value} -> {new_state.value}")
        self.state = new_state
        self._persist_local_state()

    def execute_remote_cmd(self, cmd: str, timeout: int = 30) -> Tuple[int, str]:
        """Execute command via transport."""
        if self.transport:
            return self.transport.execute(cmd, timeout=timeout)
        raise NotImplementedError("Live SSH transport not initialized in CPU-only dry-run mode.")

    def fetch_remote_file(self, remote_path: str, local_tmp_path: str) -> bool:
        """Fetch remote file via transport SFTP."""
        if self.transport:
            return self.transport.fetch_file(remote_path, local_tmp_path)
        raise NotImplementedError("Live SFTP transport not initialized in CPU-only dry-run mode.")

    def launch_detached_runner(self, manifest_remote: str, output_remote: str) -> int:
        """Launch remote runner as detached background process."""
        self.transition_to(OrchestratorState.RUNNING)
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
            self.transition_to(OrchestratorState.SAFE_HOLD)
            raise RuntimeError("Failed to launch detached runner.")
            
        code, pid_str = self.execute_remote_cmd(f"cat {pid_file}")
        self.remote_pid = int(pid_str.strip())
        self.last_heartbeat_timestamp = time.time()
        self._persist_local_state()
        return self.remote_pid

    def check_liveness_and_heartbeat(self) -> Tuple[bool, bool, Dict[str, Any]]:
        """
        Two-tier liveness verification:
        1. Process is running (`kill -0 <pid>`)
        2. Heartbeat has updated within `self.heartbeat_timeout_seconds`
        """
        if not self.remote_pid:
            return False, False, {}
            
        code, _ = self.execute_remote_cmd(f"kill -0 {self.remote_pid}")
        is_process_alive = (code == 0)
        
        record_file = f"{self.remote_work_dir}/logs/execution_record.json"
        code, record_str = self.execute_remote_cmd(f"cat {record_file}")
        record = {}
        is_heartbeat_fresh = False
        
        if code == 0 and record_str.strip():
            try:
                record = json.loads(record_str)
                last_hb = record.get("last_heartbeat", 0.0)
                now = time.time()
                # Check freshness
                if (now - last_hb) <= self.heartbeat_timeout_seconds:
                    is_heartbeat_fresh = True
                    self.last_heartbeat_timestamp = last_hb
                else:
                    print(f"  [Warning] Stale heartbeat: {now - last_hb:.1f}s since last update.")
            except Exception as e:
                print(f"  [Warning] Failed to parse remote execution record: {e}")
                
        return is_process_alive, is_heartbeat_fresh, record

    def validate_and_atomic_sync(self, remote_output_file: str, local_output_name: str = "primary_7b_generations.jsonl") -> Tuple[int, List[str]]:
        """
        Atomic SFTP synchronization and validation pipeline:
        1. Pull to temporary file (.tmp)
        2. Verify JSONL syntax
        3. Check schema completeness and non-empty content
        4. Cross-validate request IDs against manifest
        5. Check for duplicate IDs
        6. Flush and fsync
        7. Atomic rename
        """
        local_dest = os.path.join(self.local_data_dir, local_output_name)
        tmp_dest = local_dest + ".tmp"
        
        success = self.fetch_remote_file(remote_output_file, tmp_dest)
        if not success or not os.path.exists(tmp_dest):
            return len(self.verified_request_ids), ["File transfer failed or empty destination."]
            
        errors = []
        valid_records = []
        seen_requests_in_file = set()
        
        try:
            with open(tmp_dest, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, 1):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    try:
                        rec = json.loads(line_str)
                    except json.JSONDecodeError as jde:
                        errors.append(f"Line {line_idx}: Invalid JSON: {jde}")
                        continue
                        
                    # Schema check
                    rid = rec.get("request_id")
                    if not rid:
                        errors.append(f"Line {line_idx}: Missing request_id.")
                        continue
                    if rid not in self.manifest_request_ids:
                        errors.append(f"Line {line_idx}: Request ID {rid} not found in manifest.")
                        continue
                    if rid in seen_requests_in_file:
                        errors.append(f"Line {line_idx}: Duplicate request ID {rid} in file.")
                        continue
                    seen_requests_in_file.add(rid)
                    
                    if not rec.get("model_output"):
                        errors.append(f"Line {line_idx}: Empty model_output for request {rid}.")
                        continue
                    if not rec.get("problem_id"):
                        errors.append(f"Line {line_idx}: Missing problem_id for request {rid}.")
                        continue
                        
                    valid_records.append(rec)
                    
            if errors:
                # If there are corrupt lines, quarantine and do NOT overwrite valid local destination
                quarantine_dest = local_dest + f".quarantine_{int(time.time())}"
                os.replace(tmp_dest, quarantine_dest)
                print(f"  [Sync Warning] {len(errors)} validation errors found. Quarantined to {quarantine_dest}")
                return len(self.verified_request_ids), errors
                
            # If completely valid, flush and atomic rename
            with open(tmp_dest, "a", encoding="utf-8") as f:
                f.flush()
                os.fsync(f.fileno())
                
            os.replace(tmp_dest, local_dest)
            self.verified_request_ids = seen_requests_in_file
            self._persist_local_state()
            return len(self.verified_request_ids), []
            
        except Exception as e:
            if os.path.exists(tmp_dest):
                try:
                    os.remove(tmp_dest)
                except Exception:
                    pass
            return len(self.verified_request_ids), [f"Sync exception: {str(e)}"]

    def evaluate_completion_gate(self) -> bool:
        """
        Verify that exactly total_expected_requests matching the manifest
        are verified locally on disk.
        """
        is_complete = (len(self.verified_request_ids) == self.total_expected_requests) and \
                      (self.verified_request_ids == self.manifest_request_ids)
        return is_complete

    def request_safe_termination(self, terminate_callback=None) -> bool:
        """
        Safe termination gate:
        Under NO circumstances will pod termination be invoked unless state is LOCAL_VERIFIED.
        """
        if self.state != OrchestratorState.LOCAL_VERIFIED:
            print(f"[Termination Gate] REJECTED: State is {self.state.value}, not LOCAL_VERIFIED. Entering SAFE_HOLD.")
            self.transition_to(OrchestratorState.SAFE_HOLD)
            return False
            
        self.transition_to(OrchestratorState.TERMINATION_REQUESTED)
        if terminate_callback:
            success = terminate_callback(self.pod_id)
            if success:
                self.transition_to(OrchestratorState.TERMINATED_CONFIRMED)
                self.termination_confirmed = True
                return True
            else:
                self.transition_to(OrchestratorState.SAFE_HOLD)
                return False
        return True
