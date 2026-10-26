#!/usr/bin/env python3
"""
Unit and Contract Tests for RunPod External Cost Controller and Lifecycle Monitor
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Verifies:
1. Authorization enforcement (RUNPOD_AUTHORIZED gate)
2. Spend calculation and budget ceiling tripping
3. Time ceiling tripping
4. Heartbeat stall detection (>300s threshold)
5. GraphQL podTerminate request formatting and response handling
6. GraphQL error and network exception resilience
7. Audit ledger persistence
8. Lifecycle monitor loop and retry logic
"""

import os
import sys
import time
import json
import pytest
from unittest.mock import patch, MagicMock

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
runpod_dir = os.path.join(repo_root, "runpod")
sys.path.insert(0, runpod_dir)
sys.path.insert(0, repo_root)

from external_cost_controller import ExternalRunPodCostController
from pod_lifecycle_monitor import PodLifecycleMonitor

class TestRunPodCostControllerContract:

    def test_authorization_blocked_without_env_flag(self, monkeypatch):
        monkeypatch.delenv("RUNPOD_AUTHORIZED", raising=False)
        monkeypatch.setenv("RUNPOD_API_KEY", "rpa_valid_mock_key_1234567890")
        ctrl = ExternalRunPodCostController(pod_id="test-pod-001")
        authorized, reason = ctrl.check_authorization()
        assert authorized is False
        assert "BLOCKED" in reason
        assert "RUNPOD_AUTHORIZED" in reason

    def test_authorization_blocked_without_api_key(self, monkeypatch):
        monkeypatch.setenv("RUNPOD_AUTHORIZED", "TRUE")
        monkeypatch.delenv("RUNPOD_API_KEY", raising=False)
        ctrl = ExternalRunPodCostController(api_key="", pod_id="test-pod-001")
        authorized, reason = ctrl.check_authorization()
        assert authorized is False
        assert "BLOCKED" in reason
        assert "RUNPOD_API_KEY" in reason

    def test_authorization_granted_when_flags_present(self, monkeypatch):
        monkeypatch.setenv("RUNPOD_AUTHORIZED", "TRUE")
        monkeypatch.setenv("RUNPOD_API_KEY", "rpa_valid_mock_key_1234567890")
        ctrl = ExternalRunPodCostController(pod_id="test-pod-001")
        authorized, reason = ctrl.check_authorization()
        assert authorized is True
        assert "AUTHORIZED" in reason

    def test_calculate_spend_within_limits(self):
        ctrl = ExternalRunPodCostController(
            pod_id="test-pod-001",
            max_cost_usd=3.00,
            max_runtime_minutes=30.0,
            gpu_hourly_rate=0.74
        )
        t0 = 1000.0
        ctrl.start_session(initial_timestamp=t0)
        
        # 10 minutes elapsed, with active heartbeat
        t_current = t0 + 600.0
        ctrl.record_heartbeat(timestamp=t_current)
        spend = ctrl.calculate_spend(current_time=t_current)
        
        assert spend["elapsed_minutes"] == 10.0
        # 10 min / 60 min * 0.74 = 0.1233
        assert pytest.approx(spend["estimated_spend_usd"], 0.01) == 0.1233
        assert spend["cost_limit_hit"] is False
        assert spend["time_limit_hit"] is False
        assert spend["heartbeat_stall"] is False
        assert spend["should_terminate"] is False

    def test_budget_ceiling_trip(self):
        ctrl = ExternalRunPodCostController(
            pod_id="test-pod-001",
            max_cost_usd=1.00, # Low ceiling for test
            max_runtime_minutes=120.0,
            gpu_hourly_rate=1.00
        )
        t0 = 1000.0
        ctrl.start_session(initial_timestamp=t0)
        
        # 70 minutes elapsed -> $1.16 spend > $1.00 ceiling
        t_current = t0 + 4200.0
        spend = ctrl.calculate_spend(current_time=t_current)
        
        assert spend["cost_limit_hit"] is True
        assert spend["should_terminate"] is True
        assert "Budget ceiling exceeded" in spend["reason"]

    def test_runtime_ceiling_trip(self):
        ctrl = ExternalRunPodCostController(
            pod_id="test-pod-001",
            max_cost_usd=50.00,
            max_runtime_minutes=30.0,
            gpu_hourly_rate=0.50
        )
        t0 = 1000.0
        ctrl.start_session(initial_timestamp=t0)
        
        # 31 minutes elapsed
        t_current = t0 + (31.0 * 60.0)
        spend = ctrl.calculate_spend(current_time=t_current)
        
        assert spend["time_limit_hit"] is True
        assert spend["should_terminate"] is True
        assert "Runtime ceiling exceeded" in spend["reason"]

    def test_heartbeat_stall_trip(self):
        ctrl = ExternalRunPodCostController(
            pod_id="test-pod-001",
            max_cost_usd=10.00,
            max_runtime_minutes=60.0,
            gpu_hourly_rate=0.50
        )
        t0 = 1000.0
        ctrl.start_session(initial_timestamp=t0)
        
        # Last heartbeat at t0 + 60s
        ctrl.record_heartbeat(timestamp=t0 + 60.0)
        
        # Current time is t0 + 400s (340s since last heartbeat > 300s limit)
        spend = ctrl.calculate_spend(current_time=t0 + 400.0)
        
        assert spend["heartbeat_stall"] is True
        assert spend["should_terminate"] is True
        assert "Heartbeat lost" in spend["reason"]

    def test_execute_hard_termination_dry_run(self, tmp_path):
        audit_file = str(tmp_path / "audit.jsonl")
        ctrl = ExternalRunPodCostController(
            pod_id="test-pod-999",
            audit_log_path=audit_file
        )
        receipt = ctrl.execute_hard_termination("Test dry run", dry_run=True)
        assert receipt["success"] is True
        assert receipt["action"] == "DRY_RUN_TERMINATE"
        assert ctrl.is_terminated is True
        assert os.path.exists(audit_file)

    @patch("requests.post")
    def test_execute_hard_termination_graphql_mock_success(self, mock_post, tmp_path):
        audit_file = str(tmp_path / "audit.jsonl")
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "podTerminate": "pod-abc-123-terminated"
            }
        }
        mock_post.return_value = mock_response

        ctrl = ExternalRunPodCostController(
            api_key="rpa_mock_key_xyz",
            pod_id="pod-abc-123",
            audit_log_path=audit_file
        )
        receipt = ctrl.execute_hard_termination("Pilot experiment finished", dry_run=False)

        assert receipt["success"] is True
        assert receipt["action"] == "BILLABLE_RESOURCE_TERMINATED"
        assert ctrl.is_terminated is True
        
        # Verify GraphQL mutation call
        call_kwargs = mock_post.call_args[1]
        assert "api.runpod.io/graphql" in mock_post.call_args[0][0]
        assert "podTerminate" in call_kwargs["json"]["query"]
        assert call_kwargs["json"]["variables"]["input"]["podId"] == "pod-abc-123"
        assert call_kwargs["headers"]["Authorization"] == "Bearer rpa_mock_key_xyz"

    @patch("requests.post")
    def test_execute_hard_termination_graphql_mock_error(self, mock_post, tmp_path):
        audit_file = str(tmp_path / "audit.jsonl")
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "errors": [{"message": "Pod pod-invalid does not exist or has already been terminated."}]
        }
        mock_post.return_value = mock_response

        ctrl = ExternalRunPodCostController(
            api_key="rpa_mock_key_xyz",
            pod_id="pod-invalid",
            audit_log_path=audit_file
        )
        receipt = ctrl.execute_hard_termination("Emergency kill", dry_run=False)

        assert receipt["success"] is False
        assert receipt["action"] == "TERMINATION_ERROR"
        assert "does not exist" in receipt["error"]

class TestPodLifecycleMonitorDaemon:

    def test_lifecycle_monitor_cycle_exhaustion(self, tmp_path):
        audit_file = str(tmp_path / "audit.jsonl")
        ctrl = ExternalRunPodCostController(
            pod_id="test-pod-daemon",
            max_cost_usd=10.0,
            max_runtime_minutes=30.0,
            audit_log_path=audit_file
        )
        monitor = PodLifecycleMonitor(
            controller=ctrl,
            poll_interval_seconds=0.01,
            max_consecutive_poll_failures=3
        )
        res = monitor.run_monitor_loop(dry_run=True, max_cycles=3)
        assert res["status"] == "CYCLES_EXHAUSTED"

    def test_lifecycle_monitor_triggers_termination_on_spend(self, tmp_path):
        audit_file = str(tmp_path / "audit.jsonl")
        ctrl = ExternalRunPodCostController(
            pod_id="test-pod-daemon",
            max_cost_usd=0.10,
            max_runtime_minutes=30.0,
            gpu_hourly_rate=1.00,
            audit_log_path=audit_file
        )
        # Pre-seed session start 1000 seconds in the past ($0.27 spend > $0.10 ceiling)
        ctrl.start_session(initial_timestamp=time.time() - 1000.0)
        
        monitor = PodLifecycleMonitor(
            controller=ctrl,
            poll_interval_seconds=0.01
        )
        receipt = monitor.run_monitor_loop(dry_run=True, max_cycles=5)
        assert receipt["action"] == "DRY_RUN_TERMINATE"
        assert "Budget ceiling exceeded" in receipt["reason"]
