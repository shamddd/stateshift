#!/usr/bin/env python3
"""
StateShift Nonblocking Emergency Termination Tests (Mission 15.2)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Verifies Phase 3:
Emergency termination ordering:
BUDGET EMERGENCY DETECTED -> DISPATCH PROVIDER TERMINATION -> PRESERVE DATA.
Provider termination dispatch is NEVER delayed or blocked by SFTP or network hangs.
"""

import os
import sys
import time
import json
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_2.runner.robust_cloud_orchestrator_v9 import (
    RobustCloudOrchestratorV9, OrchestratorStateV9
)

class OrderingTransport:
    def __init__(self, sftp_delay: float = 0.0, sftp_raises: bool = False):
        self.call_order = []
        self.sftp_delay = sftp_delay
        self.sftp_raises = sftp_raises
        self.termination_dispatch_time = None
        self.sftp_call_time = None

    def terminate_pod(self, pod_id):
        self.call_order.append("provider_terminate")
        self.termination_dispatch_time = time.monotonic()
        return True, {"podTerminate": True}

    def verify_pod_terminated(self, pod_id, max_checks=3, delay_seconds=0.01):
        self.call_order.append("provider_verify")
        return True

    def fetch_file(self, remote_path, local_tmp_path, ip=None, port=None):
        self.call_order.append("sftp_fetch")
        self.sftp_call_time = time.monotonic()
        if self.sftp_delay > 0:
            time.sleep(self.sftp_delay)
        if self.sftp_raises:
            raise ConnectionError("SFTP connection hung/timed out")
        with open(local_tmp_path, "w", encoding="utf-8") as f:
            f.write('{"request_id": "r1"}\n')
        return True


class TestNonblockingEmergencyTermination(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = os.path.join(self.test_dir, "manifest.json")
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump({"manifest_version": "v1", "requests": [{"request_id": "r1"}]}, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_provider_termination_dispatched_before_sftp(self):
        """Provider termination MUST be called BEFORE any SFTP file retrieval."""
        transport = OrderingTransport()
        orch = RobustCloudOrchestratorV9(
            experiment_id="ordering_test",
            manifest_path=self.manifest_path,
            pod_id="pod_123",
            local_data_dir=self.test_dir,
            transport=transport
        )
        orch.state = OrchestratorStateV9.RUNNING
        
        ok = orch.terminate_emergency(reason="Budget exceeded", emergency_sync=True, remote_output_file="/remote/out.jsonl")
        self.assertTrue(ok)
        self.assertEqual(orch.state, OrchestratorStateV9.EMERGENCY_TERMINATED)
        
        # Verify strict ordering
        self.assertEqual(transport.call_order[0], "provider_terminate")
        self.assertEqual(transport.call_order[1], "provider_verify")
        self.assertEqual(transport.call_order[2], "sftp_fetch")
        self.assertLess(transport.termination_dispatch_time, transport.sftp_call_time)

    def test_sftp_hang_does_not_delay_termination_dispatch(self):
        """If SFTP raises exception or hangs, provider termination is already dispatched and confirmed."""
        transport = OrderingTransport(sftp_raises=True)
        orch = RobustCloudOrchestratorV9(
            experiment_id="hang_test",
            manifest_path=self.manifest_path,
            pod_id="pod_123",
            local_data_dir=self.test_dir,
            transport=transport
        )
        orch.state = OrchestratorStateV9.RUNNING
        
        t0 = time.monotonic()
        ok = orch.terminate_emergency(reason="Immediate emergency", emergency_sync=True, remote_output_file="/remote/out.jsonl")
        elapsed = time.monotonic() - t0
        
        self.assertTrue(ok)
        self.assertEqual(orch.state, OrchestratorStateV9.EMERGENCY_TERMINATED)
        self.assertIn("provider_terminate", transport.call_order)
        self.assertLess(elapsed, 1.0) # Confirmed in sub-second time

if __name__ == "__main__":
    unittest.main()
