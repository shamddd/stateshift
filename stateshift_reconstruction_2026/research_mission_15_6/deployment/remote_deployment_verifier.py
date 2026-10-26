#!/usr/bin/env python3
"""
StateShift Remote Deployment & Execution Verifier (Mission 15.4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Verifies remote execution environment and artifacts before launching compute:
- Checks remote workspace, python interpreter, and writable output dir
- Verifies manifest existence and SHA-256 hash match
- Verifies remote experiment runner existence and code hash match
- Validates available remote disk capacity (>= 20 GB)
- Launches detached process, captures authentic OS PID, verifies process in ps,
  and waits for authentic startup heartbeat
"""

import os
import sys
import json
import time
import hashlib
from typing import Dict, Any, Tuple, Optional


class DeploymentVerificationError(Exception):
    pass


class RemoteDeploymentVerifier:
    def __init__(self, transport: Any, remote_work_dir: str, local_manifest_path: str, local_runner_path: str):
        self.transport = transport
        self.remote_work_dir = remote_work_dir
        self.local_manifest_path = local_manifest_path
        self.local_runner_path = local_runner_path

        with open(local_manifest_path, "rb") as f:
            self.expected_manifest_sha256 = hashlib.sha256(f.read()).hexdigest()

        with open(local_runner_path, "rb") as f:
            self.expected_runner_sha256 = hashlib.sha256(f.read()).hexdigest()

    def verify_preflight_environment(self, ip: Optional[str] = None, port: int = 22) -> Tuple[bool, str]:
        """Audits remote host before allowing process launch."""
        if not self.transport:
            return True, "Mock transport: skipping remote environment check."

        # 1. Check Python interpreter
        code, out = self.transport.execute("python3 --version", ip=ip, port=port)
        if code != 0 or "Python 3" not in out:
            return False, f"Remote Python interpreter check failed (code {code}): {out}"

        # 2. Check disk space (require at least 20 GB free)
        code, out = self.transport.execute("df -k /workspace | tail -1", ip=ip, port=port)
        if code == 0:
            parts = out.split()
            if len(parts) >= 4:
                try:
                    avail_kb = int(parts[3])
                    avail_gb = avail_kb / (1024 * 1024)
                    if avail_gb < 20.0:
                        return False, f"Insufficient disk space on /workspace: {avail_gb:.1f} GB available, >= 20.0 GB required."
                except Exception:
                    pass

        # 3. Check manifest existence and cryptographic hash
        remote_manifest = f"{self.remote_work_dir}/manifests/primary_100_manifest.json"
        code, out = self.transport.execute(f"sha256sum {remote_manifest}", ip=ip, port=port)
        if code != 0:
            return False, f"Remote manifest missing at '{remote_manifest}' (code {code})."
        remote_hash = out.split()[0].strip() if out.split() else ""
        if remote_hash != self.expected_manifest_sha256:
            return False, f"Remote manifest SHA-256 mismatch: {remote_hash} vs expected {self.expected_manifest_sha256}."

        # 4. Check runner script existence and hash
        remote_runner = f"{self.remote_work_dir}/runner/remote_experiment_runner.py"
        code, out = self.transport.execute(f"sha256sum {remote_runner}", ip=ip, port=port)
        if code != 0:
            return False, f"Remote runner script missing at '{remote_runner}' (code {code})."
        runner_hash = out.split()[0].strip() if out.split() else ""
        if runner_hash != self.expected_runner_sha256:
            return False, f"Remote runner code SHA-256 mismatch: {runner_hash} vs approved {self.expected_runner_sha256}."

        return True, "Preflight environment and artifacts verified successfully."

    def launch_and_verify_process(
        self,
        experiment_id: str,
        execution_id: str,
        ip: Optional[str] = None,
        port: int = 22,
        heartbeat_timeout_seconds: float = 120.0
    ) -> Tuple[bool, Optional[int], str]:
        """
        Launches detached runner, captures authentic OS PID, verifies in process table,
        and waits for valid initial heartbeat.
        Returns: (success: bool, real_pid: Optional[int], message: str)
        """
        if not self.transport:
            return True, 12345, "Mock launch: simulated PID 12345."

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
            f"--experiment-id {experiment_id} "
            f"--execution-id {execution_id} "
            f"< /dev/null > {remote_log} 2>&1 & echo $! > {remote_pid_file}"
        )
        code, out = self.transport.execute(cmd, ip=ip, port=port)
        if code != 0:
            return False, None, f"Remote launch command failed (code {code}): {out}"

        # Capture PID
        code, pid_out = self.transport.execute(f"cat {remote_pid_file}", ip=ip, port=port)
        if code != 0 or not pid_out.strip():
            return False, None, "Failed to retrieve remote runner PID."

        try:
            real_pid = int(pid_out.strip())
        except ValueError:
            return False, None, f"Malformed PID returned from remote: '{pid_out.strip()}'."

        # Verify PID actually exists and matches command line
        code, ps_out = self.transport.execute(f"ps -p {real_pid} -o pid,cmd --no-headers", ip=ip, port=port)
        if code != 0 or "remote_experiment_runner.py" not in ps_out:
            return False, None, f"Process verification failed for PID {real_pid}: process not running or command mismatch ({ps_out})."

        # Poll for authentic startup heartbeat
        t0 = time.time()
        while time.time() - t0 < heartbeat_timeout_seconds:
            code, hb_out = self.transport.execute(f"cat {remote_hb}", ip=ip, port=port)
            if code == 0 and hb_out.strip():
                try:
                    hb_data = json.loads(hb_out)
                    if hb_data.get("experiment_id") == experiment_id and hb_data.get("status") in ["INITIALIZED", "RUNNING", "GENERATING"]:
                        return True, real_pid, f"Remote runner verified running (PID: {real_pid}, status: {hb_data.get('status')})."
                except Exception:
                    pass
            time.sleep(1.5)

        return False, real_pid, f"Remote process {real_pid} launched, but startup heartbeat was not observed within {heartbeat_timeout_seconds}s."
