#!/usr/bin/env python3
"""
StateShift Production RunPod Transport Tests (Mission 15.1)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)
"""

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_1.transport.runpod_transport import (
    ProductionRunPodTransport, RunPodAPIError
)

class TestProductionRunPodTransport(unittest.TestCase):
    def test_credential_masking(self):
        """API keys must never be leaked in string representation."""
        transport = ProductionRunPodTransport(api_key="SECRET_KEY_123456789")
        rep = repr(transport)
        self.assertNotIn("SECRET_KEY_123456789", rep)
        self.assertIn("SECR...6789", rep)

    def test_get_pod_metadata_parsing(self):
        """Metadata response correctly extracts uptime and ports."""
        mock_response = {
            "pod": {
                "id": "pod_xyz_123",
                "desiredStatus": "RUNNING",
                "runtime": {
                    "uptimeInSeconds": 3600,
                    "ports": [
                        {"ip": "192.168.1.100", "publicPort": 2222, "privatePort": 22}
                    ]
                }
            }
        }
        mock_http = MagicMock(return_value=mock_response)
        transport = ProductionRunPodTransport(api_key="dummy_key", http_client=mock_http)
        
        meta = transport.get_pod_metadata("pod_xyz_123")
        self.assertTrue(meta["exists"])
        self.assertEqual(meta["status"], "RUNNING")
        self.assertEqual(meta["uptimeSeconds"], 3600)
        self.assertEqual(meta["ssh_ip"], "192.168.1.100")
        self.assertEqual(meta["ssh_port"], 2222)

    def test_terminate_pod_mutation(self):
        """Terminate pod mutation query is dispatched."""
        mock_response = {"podTerminate": True}
        mock_http = MagicMock(return_value=mock_response)
        transport = ProductionRunPodTransport(api_key="dummy_key", http_client=mock_http)
        
        ok, res = transport.terminate_pod("pod_xyz_123")
        self.assertTrue(ok)
        self.assertTrue(res["podTerminate"])
        self.assertEqual(mock_http.call_count, 1)

    def test_verify_pod_terminated_polls_until_gone(self):
        """verify_pod_terminated polls until pod metadata reports not found."""
        call_count = 0
        def mock_query(query, vars):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return {"pod": {"id": "pod_xyz_123", "desiredStatus": "RUNNING"}}
            return {"pod": None} # Pod deleted!

        transport = ProductionRunPodTransport(api_key="dummy_key", http_client=mock_query)
        confirmed = transport.verify_pod_terminated("pod_xyz_123", max_checks=3, delay_seconds=0.01)
        self.assertTrue(confirmed)
        self.assertEqual(call_count, 2)

    def test_missing_api_key_raises_error(self):
        """Transport without API key raises RunPodAPIError upon default http call."""
        transport = ProductionRunPodTransport(api_key="")
        with self.assertRaises(RunPodAPIError):
            transport._default_http_post("query { dummy }")

if __name__ == "__main__":
    unittest.main()
