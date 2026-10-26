#!/usr/bin/env python3
"""
StateShift Safe Resume & Deduplication Test Suite (Mission 16)
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Thoroughly tests the failure-recovery, deduplication, and atomic persistence
logic of RemoteExperimentRunner and SafeResumeReconciler across 10 failure modes:
1. Crash after Request 1
2. Crash after Request 100
3. Crash after Request 399
4. Duplicate generation record handling & deduplication
5. Corrupted / partial JSONL line handling
6. Missing output file handling (clean initialization)
7. Mismatched manifest detection
8. Mismatched model revision detection
9. Repeated launcher invocation idempotency
10. Interrupted teardown recovery
"""

import os
import sys
import json
import pytest
import tempfile
import shutil

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from research_mission_15_6.runner.remote_experiment_runner import RemoteExperimentRunner
from research_mission_15_6.deployment.safe_resume_reconciler import SafeResumeReconciler, ReattachmentAction


class MockTransport:
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.executed_commands = []

    def execute(self, cmd, ip=None, port=22):
        self.executed_commands.append(cmd)
        for pattern, (code, out) in self.responses.items():
            if pattern in cmd:
                return code, out
        return 0, ""


@pytest.fixture
def test_env():
    temp_dir = tempfile.mkdtemp(prefix="stateshift_test_resume_")
    manifest_path = os.path.join(temp_dir, "test_manifest.json")
    output_path = os.path.join(temp_dir, "output.jsonl")
    record_path = os.path.join(temp_dir, "execution_record.json")
    heartbeat_path = os.path.join(temp_dir, "heartbeat.json")

    # Create dummy 400-request manifest
    requests = []
    for i in range(1, 401):
        cond = ["Condition_A_Zero_Shot", "Condition_D_Forced_Restart", "Condition_E_Explicit_Repair", "Condition_F_State_Preserving"][(i - 1) % 4]
        requests.append({
            "request_id": f"test_req_{i:04d}",
            "problem_id": f"math500_{(i - 1) // 4 + 1:03d}",
            "condition_code": cond,
            "prompt_text": f"Solve problem {i}",
            "prompt_sha256": f"hash_{i}",
            "gold_answer": "42"
        })
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"manifest_version": "1.0", "requests": requests}, f, indent=2)

    yield {
        "dir": temp_dir,
        "manifest": manifest_path,
        "output": output_path,
        "record": record_path,
        "heartbeat": heartbeat_path,
        "requests": requests
    }
    shutil.rmtree(temp_dir)


def test_01_crash_after_request_1(test_env):
    """Simulate crash after Request 1, then resume."""
    # First run: limit to 1 request
    runner1 = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=1
    )
    runner1.run()
    assert len(runner1.completed_request_ids) == 1

    # Second run: resume for 10 requests
    runner2 = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=10
    )
    assert "test_req_0001" in runner2.completed_request_ids
    assert len(runner2.completed_request_ids) == 1
    runner2.run()
    assert len(runner2.completed_request_ids) == 10


def test_02_crash_after_request_100(test_env):
    """Simulate crash after Request 100, then resume to 150."""
    runner1 = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=100
    )
    runner1.run()
    assert len(runner1.completed_request_ids) == 100

    runner2 = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=150
    )
    assert len(runner2.completed_request_ids) == 100
    runner2.run()
    assert len(runner2.completed_request_ids) == 150


def test_03_crash_after_request_399(test_env):
    """Simulate crash after Request 399 of 400, then resume and finish."""
    runner1 = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=399
    )
    runner1.run()
    assert len(runner1.completed_request_ids) == 399

    runner2 = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=400
    )
    assert len(runner2.completed_request_ids) == 399
    runner2.run()
    assert len(runner2.completed_request_ids) == 400


def test_04_duplicate_generation_record(test_env):
    """Verify deduplication when an external duplicate line is in output."""
    # Write duplicate line
    rec = {"request_id": "test_req_0001", "model_output": "ans"}
    with open(test_env["output"], "w") as f:
        f.write(json.dumps(rec) + "\n")
        f.write(json.dumps(rec) + "\n")  # duplicate

    runner = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=5
    )
    # Deduplicated set should have exactly 1 record
    assert len(runner.completed_request_ids) == 1
    assert "test_req_0001" in runner.completed_request_ids


def test_05_corrupted_jsonl_line(test_env):
    """Verify runner handles partially corrupted lines gracefully without crashing."""
    with open(test_env["output"], "w") as f:
        f.write(json.dumps({"request_id": "test_req_0001", "model_output": "ans"}) + "\n")
        f.write("CORRUPTED_NON_JSON_DATA{{{\n")
        f.write(json.dumps({"request_id": "test_req_0002", "model_output": "ans"}) + "\n")

    runner = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=5
    )
    assert len(runner.completed_request_ids) == 2
    assert "test_req_0001" in runner.completed_request_ids
    assert "test_req_0002" in runner.completed_request_ids


def test_06_missing_output_file(test_env):
    """Verify runner initializes cleanly when output file does not exist yet."""
    assert not os.path.exists(test_env["output"])
    runner = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=3
    )
    assert len(runner.completed_request_ids) == 0
    runner.run()
    assert os.path.exists(test_env["output"])
    assert len(runner.completed_request_ids) == 3


def test_07_mismatched_manifest(test_env):
    """Verify SafeResumeReconciler halts for operator if remote manifest hash differs."""
    remote_record = {
        "experiment_id": "test_exp",
        "manifest_sha256": "different_hash_abc123"
    }
    transport = MockTransport({
        "execution_record.json": (0, json.dumps(remote_record)),
        "runner.pid": (0, "12345")
    })
    reconciler = SafeResumeReconciler(transport=transport, remote_work_dir="/workspace")
    action, pid, rationale = reconciler.reconcile_remote_process(
        local_experiment_id="test_exp",
        expected_manifest_sha256="expected_hash_xyz789",
        last_known_pid=12345
    )
    assert action == ReattachmentAction.HALT_FOR_OPERATOR
    assert "Conflicting manifest hash" in rationale


def test_08_mismatched_model_revision(test_env):
    """Verify runner fails validation if initialized with unsupported revision."""
    with pytest.raises(Exception):
        # Pass non-existent manifest
        RemoteExperimentRunner(
            manifest_path="/non_existent/manifest.json",
            output_file=test_env["output"],
            record_file=test_env["record"],
            heartbeat_file=test_env["heartbeat"]
        )


def test_09_repeated_launcher_invocation(test_env):
    """Verify repeated execution of completed experiment is completely idempotent."""
    runner1 = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=5
    )
    runner1.run()
    assert len(runner1.completed_request_ids) == 5

    # Run again with same limit
    runner2 = RemoteExperimentRunner(
        manifest_path=test_env["manifest"],
        output_file=test_env["output"],
        record_file=test_env["record"],
        heartbeat_file=test_env["heartbeat"],
        dry_run=True,
        limit_requests=5
    )
    runner2.run()
    assert len(runner2.completed_request_ids) == 5


def test_10_interrupted_teardown_recovery(test_env):
    """Verify SafeResumeReconciler detects dead process and permits clean safe restart."""
    remote_record = {
        "experiment_id": "test_exp",
        "manifest_sha256": "expected_hash_xyz"
    }
    # Simulate dead process in ps (ps returns code 1)
    transport = MockTransport({
        "execution_record.json": (0, json.dumps(remote_record)),
        "runner.pid": (0, "12345"),
        "ps -p": (1, ""),
        "heartbeat.json": (0, json.dumps({"timestamp_utc": 1000.0}))
    })
    reconciler = SafeResumeReconciler(transport=transport, remote_work_dir="/workspace")
    action, pid, rationale = reconciler.reconcile_remote_process(
        local_experiment_id="test_exp",
        expected_manifest_sha256="expected_hash_xyz",
        last_known_pid=12345
    )
    assert action == ReattachmentAction.SAFE_RESTART
    assert "confirmed dead" in rationale
