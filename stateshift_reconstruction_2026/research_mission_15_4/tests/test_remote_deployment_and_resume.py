"""
Remote Deployment Verifier & Safe Resume Reconciler Test Suite (Mission 15.4)
Exercises remote preflight environment checks, hash checks, PID capture, ps verification,
heartbeat timeouts, and reattachment / safe restart decisions.
"""

import os
import json
import time
import tempfile
import pytest

from research_mission_15_4.deployment.remote_deployment_verifier import RemoteDeploymentVerifier
from research_mission_15_4.deployment.safe_resume_reconciler import SafeResumeReconciler, ReattachmentAction


class MockTransport:
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.history = []

    def execute(self, cmd, ip=None, port=22):
        self.history.append(cmd)
        for pattern, res in self.responses.items():
            if pattern in cmd:
                return res
        return 1, "Default mock: command not recognized"


@pytest.fixture
def deployment_files(tmp_path):
    man = os.path.join(tmp_path, "manifest.json")
    with open(man, "w") as f:
        f.write('{"manifest": "content"}')
    run = os.path.join(tmp_path, "runner.py")
    with open(run, "w") as f:
        f.write('# runner code')
    return man, run


def test_deployment_verifier_success(deployment_files):
    """Test full verification pass when remote environment and hashes match."""
    man, run = deployment_files
    import hashlib
    with open(man, "rb") as f:
        man_h = hashlib.sha256(f.read()).hexdigest()
    with open(run, "rb") as f:
        run_h = hashlib.sha256(f.read()).hexdigest()

    transport = MockTransport({
        "python3 --version": (0, "Python 3.10.12"),
        "df -k /workspace": (0, "Filesystem 104857600 20971520 83886080 20% /workspace"),
        "sha256sum /workspace/manifests/primary_100_manifest.json": (0, f"{man_h}  /workspace/manifests/primary_100_manifest.json"),
        "sha256sum /workspace/runner/remote_experiment_runner.py": (0, f"{run_h}  /workspace/runner/remote_experiment_runner.py")
    })

    verifier = RemoteDeploymentVerifier(
        transport=transport,
        remote_work_dir="/workspace",
        local_manifest_path=man,
        local_runner_path=run
    )
    ok, msg = verifier.verify_preflight_environment()
    assert ok
    assert "verified successfully" in msg


def test_deployment_verifier_disk_space_failure(deployment_files):
    """Test verification rejection when available disk space is under 20 GB."""
    man, run = deployment_files
    transport = MockTransport({
        "python3 --version": (0, "Python 3.10.12"),
        "df -k /workspace": (0, "Filesystem 104857600 95000000 9857600 90% /workspace") # ~9.4 GB free
    })

    verifier = RemoteDeploymentVerifier(
        transport=transport,
        remote_work_dir="/workspace",
        local_manifest_path=man,
        local_runner_path=run
    )
    ok, msg = verifier.verify_preflight_environment()
    assert not ok
    assert "Insufficient disk space" in msg


def test_deployment_launch_and_verify_success(deployment_files):
    """Test successful process launch, PID capture, ps check, and heartbeat verification."""
    man, run = deployment_files
    transport = MockTransport({
        "nohup python3": (0, ""),
        "cat /workspace/logs/runner.pid": (0, "78910"),
        "ps -p 78910": (0, "78910 python3 /workspace/runner/remote_experiment_runner.py"),
        "cat /workspace/logs/heartbeat.json": (0, json.dumps({
            "experiment_id": "exp_launch_01",
            "status": "RUNNING",
            "timestamp_utc": time.time()
        }))
    })

    verifier = RemoteDeploymentVerifier(
        transport=transport,
        remote_work_dir="/workspace",
        local_manifest_path=man,
        local_runner_path=run
    )
    ok, pid, msg = verifier.launch_and_verify_process(
        experiment_id="exp_launch_01",
        execution_id="exec_01",
        heartbeat_timeout_seconds=2.0
    )
    assert ok
    assert pid == 78910
    assert "verified running" in msg


def test_safe_resume_reattach_active_process():
    """Test safe resume reattaches to an active remote process with fresh heartbeat."""
    transport = MockTransport({
        "cat /workspace/logs/execution_record.json": (0, json.dumps({
            "experiment_id": "exp_res_01",
            "manifest_sha256": "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"
        })),
        "cat /workspace/logs/runner.pid": (0, "65432"),
        "ps -p 65432": (0, "65432 python3 /workspace/runner/remote_experiment_runner.py"),
        "cat /workspace/logs/heartbeat.json": (0, json.dumps({
            "experiment_id": "exp_res_01",
            "timestamp_utc": time.time()
        }))
    })

    reconciler = SafeResumeReconciler(transport=transport, remote_work_dir="/workspace")
    action, pid, rationale = reconciler.reconcile_remote_process(
        local_experiment_id="exp_res_01",
        expected_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        last_known_pid=65432
    )
    assert action == ReattachmentAction.REATTACH
    assert pid == 65432
    assert "Reattaching" in rationale


def test_safe_resume_safe_restart_on_dead_process():
    """Test safe resume allows restart when remote process is confirmed dead."""
    transport = MockTransport({
        "cat /workspace/logs/execution_record.json": (0, json.dumps({
            "experiment_id": "exp_res_02",
            "manifest_sha256": "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"
        })),
        "cat /workspace/logs/runner.pid": (0, "65432"),
        "ps -p 65432": (1, "")  # Process dead
    })

    reconciler = SafeResumeReconciler(transport=transport, remote_work_dir="/workspace")
    action, pid, rationale = reconciler.reconcile_remote_process(
        local_experiment_id="exp_res_02",
        expected_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        last_known_pid=65432
    )
    assert action == ReattachmentAction.SAFE_RESTART
    assert pid is None
    assert "confirmed dead" in rationale


def test_safe_resume_halt_on_conflicting_experiment():
    """Test safe resume halts if remote workspace holds a different experiment ID."""
    transport = MockTransport({
        "cat /workspace/logs/execution_record.json": (0, json.dumps({
            "experiment_id": "other_experiment_id",
            "manifest_sha256": "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"
        }))
    })

    reconciler = SafeResumeReconciler(transport=transport, remote_work_dir="/workspace")
    action, pid, rationale = reconciler.reconcile_remote_process(
        local_experiment_id="exp_res_03",
        expected_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        last_known_pid=None
    )
    assert action == ReattachmentAction.HALT_FOR_OPERATOR
    assert "Conflicting experiment ID" in rationale
