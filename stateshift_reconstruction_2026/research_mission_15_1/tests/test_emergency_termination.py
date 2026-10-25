#!/usr/bin/env python3
"""
StateShift Emergency Termination Regression Suite (Mission 15.1)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Verifies that Financial Safety Overrides Scientific Completion:
1. Callable from ALL active states.
2. Independent of data completeness / LOCAL_VERIFIED.
3. Idempotent across repeated calls.
4. Correctly transitions to EMERGENCY_TERMINATED or TERMINATION_UNCONFIRMED.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_1.runner.robust_cloud_orchestrator_v8 import (
    RobustCloudOrchestratorV8, OrchestratorStateV8, ExecutionMode
)
from research_mission_15_1.transport.runpod_transport import ProductionRunPodTransport

class MockTransportAdapter:
    def __init__(self, terminate_succeeds=True, verify_succeeds=True):
        self.terminate_succeeds = terminate_succeeds
        self.verify_succeeds = verify_succeeds
        self.terminate_calls = 0
        self.verify_calls = 0
        self.fetch_file_calls = 0
        self.sftp_should_fail = False

    def terminate_pod(self, pod_id: str):
        self.terminate_calls += 1
        if self.terminate_succeeds:
            return True, {"status": "SUCCESS"}
        return False, {"error": "API error terminating pod"}

    def verify_pod_terminated(self, pod_id: str, max_checks=3, delay_seconds=1.0):
        self.verify_calls += 1
        return self.verify_succeeds

    def fetch_file(self, remote_path, local_tmp_path, ip=None, port=None):
        self.fetch_file_calls += 1
        if self.sftp_should_fail:
            return False
        with open(local_tmp_path, "w", encoding="utf-8") as f:
            f.write('{"request_id": "r1", "model_output": "test"}\n')
        return True


class TestEmergencyTermination(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = os.path.join(self.test_dir, "manifest.json")
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump({"manifest_version": "v1", "requests": [{"request_id": "r1"}]}, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_orchestrator(self, transport=None):
        return RobustCloudOrchestratorV8(
            experiment_id="test_exp",
            manifest_path=self.manifest_path,
            pod_id="pod_test_123",
            local_data_dir=self.test_dir,
            transport=transport or MockTransportAdapter()
        )

    def test_emergency_termination_from_all_active_states(self):
        """Emergency termination MUST succeed from every active state."""
        states_to_test = [
            OrchestratorStateV8.NOT_STARTED,
            OrchestratorStateV8.RUNNING,
            OrchestratorStateV8.SYNCING,
            OrchestratorStateV8.REMOTE_COMPLETE,
            OrchestratorStateV8.PARTIAL_PRESERVED,
            OrchestratorStateV8.SAFE_HOLD,
            OrchestratorStateV8.FAILURE_REQUIRES_ATTENTION,
            OrchestratorStateV8.BUDGET_EXCEEDED
        ]
        
        for st in states_to_test:
            transport = MockTransportAdapter()
            orch = self._create_orchestrator(transport)
            orch.state = st
            
            # Request emergency termination
            success = orch.terminate_emergency(reason=f"Test emergency from {st.value}")
            self.assertTrue(success, f"Emergency termination failed from state {st.value}")
            self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)
            self.assertEqual(transport.terminate_calls, 1)
            self.assertEqual(transport.verify_calls, 1)

    def test_emergency_termination_idempotency(self):
        """Repeated emergency termination calls must be safe and idempotent."""
        transport = MockTransportAdapter()
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.RUNNING
        
        # Call 1
        res1 = orch.terminate_emergency(reason="Initial threshold trip")
        self.assertTrue(res1)
        self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)
        self.assertEqual(transport.terminate_calls, 1)
        
        # Call 2 (repeated)
        res2 = orch.terminate_emergency(reason="Secondary threshold trip")
        self.assertTrue(res2)
        self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)
        # Should NOT make additional unnecessary terminate calls
        self.assertEqual(transport.terminate_calls, 1)

    def test_emergency_termination_when_sftp_fails(self):
        """SFTP failure during emergency sync must NOT block pod termination."""
        transport = MockTransportAdapter()
        transport.sftp_should_fail = True
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.RUNNING
        
        success = orch.terminate_emergency(reason="Budget exceeded", emergency_sync=True, remote_output_file="/remote/out.jsonl")
        self.assertTrue(success)
        self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)
        self.assertEqual(transport.terminate_calls, 1)

    def test_emergency_termination_when_dataset_invalid(self):
        """Invalid or non-existent local dataset must NOT block emergency termination."""
        transport = MockTransportAdapter()
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.RUNNING
        
        # No local dataset exists at all
        success = orch.terminate_emergency(reason="Critical failure")
        self.assertTrue(success)
        self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)

    def test_termination_unconfirmed_when_provider_fails(self):
        """When provider fails to terminate, state becomes TERMINATION_UNCONFIRMED."""
        transport = MockTransportAdapter(terminate_succeeds=False)
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.RUNNING
        
        success = orch.terminate_emergency(reason="Budget exceeded")
        self.assertFalse(success)
        self.assertEqual(orch.state, OrchestratorStateV8.TERMINATION_UNCONFIRMED)
        self.assertIsNotNone(orch.termination_receipt)
        self.assertFalse(orch.termination_receipt["confirmed_by_provider"])

    def test_termination_unconfirmed_when_verification_fails(self):
        """When provider claims success but verification fails, returns TERMINATION_UNCONFIRMED."""
        transport = MockTransportAdapter(terminate_succeeds=True, verify_succeeds=False)
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.RUNNING
        
        success = orch.terminate_emergency(reason="Budget exceeded")
        self.assertFalse(success)
        self.assertEqual(orch.state, OrchestratorStateV8.TERMINATION_UNCONFIRMED)

if __name__ == "__main__":
    unittest.main()
