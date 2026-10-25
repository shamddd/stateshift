#!/usr/bin/env python3
"""
Mission 15.3 End-to-End Exact CLI Subprocess Tests (10 Scenarios)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Invokes the actual production CLI entry point (stateshift_production_runner.py)
via Python subprocess across all 10 mandatory scenarios:
Scenario A — Complete experiment (400/400 verified, FINISHED)
Scenario B — Budget stop (143 rollouts, $2.05 spend, emergency shutdown)
Scenario C — SSH failure (transient disconnect, reconnection)
Scenario D — SFTP failure (sync failure, watchdog active)
Scenario E — Controller crash & restart (resume from checkpoint)
Scenario F — Provider outage (unconfirmed termination escalation)
Scenario G — Dataset corruption (unparseable JSON line, gate fails)
Scenario H — Authorization mismatch (rejection before cloud actions)
Scenario I — Engine fallback (vLLM fails, Transformers selected)
Scenario J — Runtime overrun (runtime exceeded, safety stop)
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
import pytest

sys_py = sys.executable
RUNNER_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "runner", "stateshift_production_runner.py"
)
MANIFEST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "manifests", "primary_100_manifest.json"
)


@pytest.fixture
def cli_env():
    tmp_dir = tempfile.mkdtemp()
    data_dir = os.path.join(tmp_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    yield {
        "dir": tmp_dir,
        "data_dir": data_dir,
        "manifest": MANIFEST_PATH
    }
    shutil.rmtree(tmp_dir, ignore_errors=True)


# Scenario A: Complete experiment
def test_scenario_a_complete_experiment(cli_env):
    cmd = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "DRY_RUN",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"],
        "--simulate-records", "400",
        "--poll-interval", "0.01"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Scenario A failed: {res.stderr}\nOutput: {res.stdout}"
    assert "Verified 400/400 rollouts" in res.stdout
    assert "PROVIDER_TERMINATION_CONFIRMED -> FINISHED" in res.stdout
    assert os.path.exists(os.path.join(cli_env["data_dir"], "integrity_receipt.json"))


# Scenario B: Budget stop at 143 records
def test_scenario_b_budget_stop(cli_env):
    cmd = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "DRY_RUN",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"],
        "--simulate-records", "143",
        "--simulate-spend-usd", "2.05",
        "--poll-interval", "0.01"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    # Expected returncode is 1 because experiment stopped due to budget emergency
    assert "Watchdog tripped" in res.stdout or "BUDGET_EMERGENCY" in res.stdout
    assert "CRITICAL EMERGENCY SHUTDOWN" in res.stdout
    receipt_file = os.path.join(cli_env["data_dir"], "termination_receipt_stateshift_400_replication_2026.json")
    assert os.path.exists(receipt_file)
    with open(receipt_file, "r") as f:
        rc = json.load(f)
    assert rc["confirmed_by_provider"] is True
    assert rc["completed_rollouts"] == 143


# Scenario C: SSH failure with reconnection
def test_scenario_c_ssh_failure_reconnect(cli_env):
    cmd = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "DRY_RUN",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"],
        "--simulate-records", "400",
        "--simulate-ssh-disconnect",
        "--poll-interval", "0.01"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "Simulated transient SSH disconnection" in res.stdout
    assert "Verified 400/400 rollouts" in res.stdout


# Scenario D: SFTP failure with watchdog active
def test_scenario_d_sftp_failure_watchdog_active(cli_env):
    cmd = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "DRY_RUN",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"],
        "--simulate-records", "100",
        "--simulate-sftp-failure",
        "--simulate-spend-usd", "2.10",
        "--poll-interval", "0.01"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert "Simulated SFTP connection failure" in res.stdout
    assert "CRITICAL EMERGENCY SHUTDOWN" in res.stdout
    # Verifies watchdog was NOT blocked by SFTP failure


# Scenario E: Controller crash and restart (resume)
def test_scenario_e_controller_crash_and_resume(cli_env):
    # Run 1: generate 200 records, then crash (kill process)
    cmd1 = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "DRY_RUN",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"],
        "--simulate-records", "200",
        "--poll-interval", "0.01"
    ]
    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    import time
    time.sleep(0.5) # Allow 200 records and state to be written to disk
    p1.kill() # Simulate sudden crash / power loss / OOM
    p1.wait()

    # Verify state and partial dataset were persisted
    assert os.path.exists(os.path.join(cli_env["data_dir"], "runner_state_stateshift_400_replication_2026.json"))

    # Run 2: resume and complete remaining records to 400
    cmd2 = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "DRY_RUN",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"],
        "--simulate-records", "400",
        "--resume",
        "--poll-interval", "0.01"
    ]
    res2 = subprocess.run(cmd2, capture_output=True, text=True)
    assert res2.returncode == 0
    assert "Resumed session" in res2.stdout
    assert "Verified 400/400 rollouts" in res2.stdout


# Scenario F: Provider outage (unconfirmed termination escalation)
def test_scenario_f_provider_outage_escalation(cli_env):
    cmd = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "DRY_RUN",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"],
        "--simulate-records", "400",
        "--simulate-unconfirmed-termination",
        "--poll-interval", "0.01"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert "TERMINATION_UNCONFIRMED" in res.stdout
    assert "CRITICAL CLOUD ESCALATION ALERT" in res.stdout
    # Check alert files written
    alert_txt = os.path.join(cli_env["data_dir"], "CRITICAL_ALERT_POD_simulated_pod.txt")
    assert os.path.exists(alert_txt)


# Scenario G: Dataset corruption
def test_scenario_g_dataset_corruption(cli_env):
    cmd = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "DRY_RUN",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"],
        "--simulate-records", "400",
        "--simulate-corrupt-dataset",
        "--poll-interval", "0.01"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 1
    assert "INTEGRITY_FAILURE" in res.stdout
    assert "JSON decode failure" in res.stdout or "REJECTED: Physical dataset" in res.stdout


# Scenario H: Authorization mismatch
def test_scenario_h_authorization_mismatch(cli_env):
    # Create invalid auth doc with wrong pod id
    bad_auth = {
        "approval_status": "APPROVED",
        "experiment_id": "stateshift_400_replication_2026",
        "principal_investigator": "Sham Satish Thakare",
        "expires_at_utc": 9999999999.0,
        "authorized_execution_modes": ["PRODUCTION"],
        "manifest_sha256": "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
        "model_revision": "c869d27376a8d6728795551322fe323b6",
        "pod_id": "different_unauthorized_pod",
        "max_authorized_incremental_usd": 2.00,
        "min_account_balance_floor_usd": 7.00
    }
    bad_auth_path = os.path.join(cli_env["dir"], "bad_auth.json")
    with open(bad_auth_path, "w") as f:
        json.dump(bad_auth, f)

    cmd = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "PRODUCTION",
        "--authorization", bad_auth_path,
        "--pod-id", "target_pod_xyz",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"]
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 1
    assert "Pod ID mismatch" in res.stderr or "Pod ID mismatch" in res.stdout


# Scenario I: Engine fallback
def test_scenario_i_engine_fallback(cli_env):
    cmd = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "DRY_RUN",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"],
        "--simulate-records", "400",
        "--simulate-engine-fallback",
        "--poll-interval", "0.01"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    # Check dataset has transformers recorded as engine
    dataset_file = os.path.join(cli_env["data_dir"], "primary_7b_generations.jsonl")
    with open(dataset_file, "r") as f:
        first_line = json.loads(f.readline())
    assert first_line["inference_engine"] == "transformers"


# Scenario J: Runtime overrun safety stop
def test_scenario_j_runtime_overrun(cli_env):
    cmd = [
        sys_py, RUNNER_SCRIPT,
        "--mode", "DRY_RUN",
        "--manifest", cli_env["manifest"],
        "--local-data-dir", cli_env["data_dir"],
        "--simulate-records", "50",
        "--simulate-runtime-overrun",
        "--poll-interval", "0.01"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert "Watchdog tripped" in res.stdout or "CRITICAL EMERGENCY SHUTDOWN" in res.stdout
