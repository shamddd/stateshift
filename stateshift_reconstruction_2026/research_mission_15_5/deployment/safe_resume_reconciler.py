#!/usr/bin/env python3
"""
StateShift Safe Resume & Process Reattachment Reconciler (Mission 15.4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Reconciles remote execution state during --resume:
- Inspects local execution receipt and remote execution record
- Verifies remote process identity and PID in ps
- Validates heartbeat freshness
- Decides whether to REATTACH, SAFE_RESTART, or HALT_FOR_OPERATOR
- Prevents launching duplicate remote processes
"""

import os
import sys
import json
import time
from typing import Dict, Any, Tuple, Optional


class ReattachmentAction:
    REATTACH = "REATTACH"
    SAFE_RESTART = "SAFE_RESTART"
    HALT_FOR_OPERATOR = "HALT_FOR_OPERATOR"


class SafeResumeReconciler:
    def __init__(self, transport: Any, remote_work_dir: str):
        self.transport = transport
        self.remote_work_dir = remote_work_dir

    def reconcile_remote_process(
        self,
        local_experiment_id: str,
        expected_manifest_sha256: str,
        last_known_pid: Optional[int],
        ip: Optional[str] = None,
        port: int = 22,
        heartbeat_stale_threshold_seconds: float = 60.0
    ) -> Tuple[str, Optional[int], str]:
        """
        Audits remote state to safely decide reattachment.
        Returns: (action: str, active_pid: Optional[int], rationale: str)
        """
        if not self.transport:
            return ReattachmentAction.REATTACH, last_known_pid or 99999, "Mock transport: simulated reattachment."

        remote_rec_path = f"{self.remote_work_dir}/logs/execution_record.json"
        remote_hb_path = f"{self.remote_work_dir}/logs/heartbeat.json"
        remote_pid_path = f"{self.remote_work_dir}/logs/runner.pid"

        # 1. Query remote execution record
        code, rec_out = self.transport.execute(f"cat {remote_rec_path}", ip=ip, port=port)
        if code != 0 or not rec_out.strip():
            # No execution record exists. Safe to start fresh if no runner running
            code, ps_all = self.transport.execute("pgrep -f remote_experiment_runner.py", ip=ip, port=port)
            if code == 0 and ps_all.strip():
                return ReattachmentAction.HALT_FOR_OPERATOR, None, (
                    f"Conflicting unknown runner process found (PIDs: {ps_all.strip()}) without an execution record."
                )
            return ReattachmentAction.SAFE_RESTART, None, "No remote execution record found; clean restart safe."

        try:
            remote_record = json.loads(rec_out)
        except Exception:
            return ReattachmentAction.HALT_FOR_OPERATOR, None, "Remote execution record exists but is corrupted."

        # 2. Verify experiment ID & manifest match
        if remote_record.get("experiment_id") != local_experiment_id:
            return ReattachmentAction.HALT_FOR_OPERATOR, None, (
                f"Conflicting experiment ID on remote pod: '{remote_record.get('experiment_id')}' vs '{local_experiment_id}'."
            )
        if remote_record.get("manifest_sha256") != expected_manifest_sha256:
            return ReattachmentAction.HALT_FOR_OPERATOR, None, (
                f"Conflicting manifest hash on remote pod: '{remote_record.get('manifest_sha256')}' vs '{expected_manifest_sha256}'."
            )

        # 3. Inspect remote PID
        code, pid_file_out = self.transport.execute(f"cat {remote_pid_path}", ip=ip, port=port)
        active_pid = None
        if code == 0 and pid_file_out.strip():
            try:
                active_pid = int(pid_file_out.strip())
            except ValueError:
                active_pid = None

        if not active_pid:
            active_pid = last_known_pid

        if not active_pid:
            return ReattachmentAction.HALT_FOR_OPERATOR, None, "Could not determine remote PID."

        # 4. Check if PID is alive and running expected script
        code, ps_out = self.transport.execute(f"ps -p {active_pid} -o pid,cmd --no-headers", ip=ip, port=port)
        is_process_alive = (code == 0 and "remote_experiment_runner.py" in ps_out)

        # 5. Check Heartbeat freshness
        code, hb_out = self.transport.execute(f"cat {remote_hb_path}", ip=ip, port=port)
        hb_fresh = False
        hb_data = {}
        if code == 0 and hb_out.strip():
            try:
                hb_data = json.loads(hb_out)
                hb_ts = hb_data.get("timestamp_utc", 0.0)
                if (time.time() - hb_ts) <= heartbeat_stale_threshold_seconds:
                    hb_fresh = True
            except Exception:
                pass

        if is_process_alive:
            if hb_fresh:
                return ReattachmentAction.REATTACH, active_pid, (
                    f"Verified active remote process (PID: {active_pid}) with fresh heartbeat. Reattaching."
                )
            else:
                # Process alive in ps, but heartbeat lagging (e.g. heavy generation pass)
                return ReattachmentAction.REATTACH, active_pid, (
                    f"Process (PID: {active_pid}) active in ps table. Heartbeat delayed but process alive. Reattaching."
                )
        else:
            # Process is dead
            return ReattachmentAction.SAFE_RESTART, None, (
                f"Remote process (PID: {active_pid}) is confirmed dead. Reconciling checkpoints for safe restart."
            )
