#!/usr/bin/env python3
"""
CPU-Only Integration and Resilience Tests for Robust Orchestrator v6 (Mission 14)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Verifies:
1. Detached process command generation and PID file creation.
2. Resilience to simulated transient SSH disconnections.
3. Atomic incremental SFTP synchronization.
4. Fail-safe artifact retrieval on interruption or termination.
"""

import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from runner.robust_cloud_orchestrator_v6 import RobustCloudOrchestratorV6

class TestRobustCloudOrchestratorV6:

    @pytest.fixture
    def orchestrator(self, tmp_path):
        data_dir = str(tmp_path / "data")
        orch = RobustCloudOrchestratorV6(
            pod_id="test_pod_123",
            ip="127.0.0.1",
            port=22,
            local_data_dir=data_dir,
            remote_work_dir="/workspace/stateshift"
        )
        return orch

    def test_launch_detached_experiment_format(self, orchestrator):
        mock_ssh = MagicMock()
        mock_channel = MagicMock()
        mock_channel.recv_exit_status.return_value = 0
        mock_stdout = MagicMock()
        mock_stdout.channel = mock_channel
        mock_stdout.read.side_effect = [b"", b"9999\n"] # First cmd output, then cat pid output
        mock_ssh.exec_command.return_value = (None, mock_stdout, None)
        
        with patch.object(orchestrator, "get_ssh_client", return_value=mock_ssh):
            pid = orchestrator.launch_detached_experiment(
                manifest_remote_path="/workspace/stateshift/manifests/primary.json",
                output_remote_path="/workspace/stateshift/data/results.jsonl"
            )
            assert pid == 9999
            assert orchestrator.remote_pid == 9999
            
            # Verify nohup was used
            calls = mock_ssh.exec_command.call_args_list
            assert "nohup" in calls[0][0][0]
            assert "echo $! > /workspace/stateshift/logs/runner.pid" in calls[0][0][0]

    def test_ssh_transient_failure_recovery(self, orchestrator):
        """Simulate 2 failed SSH connections before successful retry."""
        mock_client = MagicMock()
        with patch("paramiko.SSHClient") as mock_ssh_cls:
            instance = mock_ssh_cls.return_value
            instance.get_transport.return_value.is_active.return_value = False
            # Fail twice with ConnectionResetError, succeed on 3rd attempt
            instance.connect.side_effect = [
                ConnectionResetError("Socket reset"),
                TimeoutError("Connection timed out"),
                None
            ]
            
            client = orchestrator.get_ssh_client(max_retries=3, retry_delay=0.01)
            assert client is not None
            assert instance.connect.call_count == 3

    def test_atomic_incremental_sync(self, orchestrator, tmp_path):
        """Simulate remote file being pulled and atomically replaced locally."""
        remote_file_content = '{"request_id": "req_1", "status": "RESTART_SUCCESS"}\n{"request_id": "req_2", "status": "RESTART_SUCCESS"}\n'
        
        mock_ssh = MagicMock()
        mock_sftp = MagicMock()
        
        def fake_get(rem, loc):
            with open(loc, "w") as f:
                f.write(remote_file_content)
                
        mock_sftp.get.side_effect = fake_get
        mock_ssh.open_sftp.return_value = mock_sftp
        
        with patch.object(orchestrator, "get_ssh_client", return_value=mock_ssh):
            records = orchestrator.sync_incremental_results("/workspace/stateshift/data/results.jsonl")
            assert records == 2
            assert orchestrator.last_synced_rollouts == 2
            
            # Check local file was created
            local_file = os.path.join(orchestrator.local_data_dir, "primary_7b_generations.jsonl")
            assert os.path.exists(local_file)
            with open(local_file) as f:
                lines = f.readlines()
                assert len(lines) == 2

    def test_monitoring_loop_exits_on_interruption_and_syncs(self, orchestrator):
        """Verify that when interrupted, the orchestrator triggers an immediate final artifact sync."""
        orchestrator.is_interrupted = True
        orchestrator.remote_pid = 1234
        
        with patch.object(orchestrator, "sync_incremental_results", return_value=42) as mock_sync:
            with patch.object(orchestrator, "check_remote_process_alive", return_value=False):
                res = orchestrator.run_monitoring_loop("/workspace/output.jsonl", max_wait_seconds=1.0)
                assert res["total_synced_rollouts"] == 42
                mock_sync.assert_called()
