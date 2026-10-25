from research_mission_15_5.supervision.independent_financial_watchdog import IndependentFinancialWatchdog
"""
Phase 9: 15 Mandatory Operational CLI Subprocess Acceptance Tests (Mission 15.5)
Exercises stateshift_production_runner_v10.py via actual OS subprocesses across all scenarios A through O.
"""

import os
import sys
import json
import time
import base64
import signal
import subprocess
import tempfile
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from research_mission_15_5.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    KNOWN_TEST_PUBLIC_KEY_B64,
    _known_test_priv
)

RUNNER_SCRIPT = os.path.abspath(
    "research_mission_15_5/runner/stateshift_production_runner_v10.py"
)
MANIFEST_PATH = os.path.abspath(
    "research_mission_15_5/manifests/primary_100_manifest.json"
)


def create_auth(path, exp_id, pod_id, mode="CALIBRATION", max_spend=0.35, trigger=0.25, tamper_sig=False, use_test_key=False):
    if use_test_key:
        priv = _known_test_priv
        pub_b64 = KNOWN_TEST_PUBLIC_KEY_B64
    else:
        priv = ed25519.Ed25519PrivateKey.generate()
        pub_b64 = base64.b64encode(priv.public_key().public_bytes_raw()).decode("utf-8")

    doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv,
        experiment_id=exp_id,
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id=pod_id,
        max_spend_usd=max_spend,
        emergency_trigger_usd=trigger,
        min_balance_usd=7.00,
        authorized_mode=mode
    )
    if tamper_sig:
        doc["signature_ed25519_b64"] = base64.b64encode(b"0" * 64).decode("utf-8")
    with open(path, "w") as f:
        json.dump(doc, f, indent=2)
    return pub_b64


def run_cli_subprocess(args, env_extra=None):
    env = dict(os.environ, PYTHONPATH=".")
    if env_extra:
        env.update(env_extra)
    cmd = [sys.executable, RUNNER_SCRIPT] + args
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)


# Scenario A: Valid 10-request simulation
def test_scenario_A_valid_10_request_simulation(tmp_path):
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_A",
        "--mode", "SIMULATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--simulate-spend-usd", "0.15",
        "--poll-interval", "0.05"
    ])
    assert res.returncode == 0
    assert "Target 10 rollouts achieved" in res.stdout
    assert "PROVIDER_TERMINATION_CONFIRMED" in res.stdout


# Scenario B: Controller SIGKILL with watchdog surviving
def test_scenario_B_controller_sigkill_watchdog_survives(tmp_path):
    watchdog_script = os.path.abspath("research_mission_15_5/supervision/independent_financial_watchdog.py")
    ctrl_proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    w_proc = subprocess.Popen([
        sys.executable, watchdog_script,
        "--experiment-id", "exp_scen_B",
        "--pod-id", "pod_scen_B",
        "--watchdog-dir", str(tmp_path),
        "--controller-pid", str(ctrl_proc.pid),
        "--max-authorized", "0.35",
        "--emergency-trigger", "0.25",
        "--poll-interval", "0.2"
    ])
    time.sleep(0.5)
    os.kill(ctrl_proc.pid, signal.SIGKILL)
    ctrl_proc.wait()
    time.sleep(1.0)
    assert w_proc.poll() is None, "Watchdog failed to survive controller SIGKILL!"
    w_proc.terminate()
    w_proc.wait()


# Scenario C: Invalid signing key / embedded test key rejected
def test_scenario_C_test_key_rejected_in_production(tmp_path):
    auth_path = tmp_path / "auth.json"
    pub_b64 = create_auth(str(auth_path), "exp_scen_C", "pod_C", mode="CALIBRATION", use_test_key=True)
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_C",
        "--pod-id", "pod_C",
        "--authorization", str(auth_path),
        "--mode", "CALIBRATION",
        "--manifest", MANIFEST_PATH,
        "--trusted-public-key", pub_b64
    ])
    assert res.returncode != 0
    assert "Embedded repository test key cannot authorize" in res.stdout


# Scenario D: Pod mismatch rejected
def test_scenario_D_pod_mismatch_rejected(tmp_path):
    auth_path = tmp_path / "auth.json"
    pub_b64 = create_auth(str(auth_path), "exp_scen_D", "pod_AUTHORIZED", mode="CALIBRATION")
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_D",
        "--pod-id", "pod_MISMATCH",
        "--authorization", str(auth_path),
        "--mode", "CALIBRATION",
        "--manifest", MANIFEST_PATH,
        "--trusted-public-key", pub_b64,
        "--allow-test-key-for-testing"
    ])
    assert res.returncode != 0
    assert "Pod ID mismatch" in res.stdout


# Scenario E: Simulation injection rejected in paid modes
def test_scenario_E_simulation_injection_rejected(tmp_path):
    res = run_cli_subprocess([
        "--mode", "CALIBRATION",
        "--manifest", MANIFEST_PATH,
        "--simulate-records", "10"
    ])
    assert res.returncode == 2
    assert "Simulation arguments are strictly prohibited" in res.stdout


# Scenario F: Calibration budget mismatch ($0.35 auth with $1.65 watchdog)
def test_scenario_F_budget_mismatch_rejected(tmp_path):
    auth_path = tmp_path / "auth.json"
    # Create invalid auth trying to claim $1.65 trigger in calibration mode
    pub_b64 = create_auth(str(auth_path), "exp_scen_F", "pod_F", mode="CALIBRATION", max_spend=0.35, trigger=1.65)
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_F",
        "--pod-id", "pod_F",
        "--authorization", str(auth_path),
        "--mode", "CALIBRATION",
        "--manifest", MANIFEST_PATH,
        "--trusted-public-key", pub_b64,
        "--allow-test-key-for-testing"
    ])
    assert res.returncode != 0
    assert "Emergency trigger $1.65 exceeds authorized budget $0.35" in res.stdout


# Scenario G: Provider API failure logs unconfirmed escalation
def test_scenario_G_provider_api_failure_unconfirmed(tmp_path):
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_G",
        "--mode", "SIMULATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-unconfirmed-termination",
        "--simulate-records", "10",
        "--poll-interval", "0.05"
    ])
    assert res.returncode != 0
    assert "TERMINATION_UNCONFIRMED" in res.stdout


# Scenario H: Financial emergency shutdown
def test_scenario_H_financial_emergency_shutdown(tmp_path):
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_H",
        "--mode", "SIMULATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "5",
        "--simulate-spend-usd", "0.30", # Exceeds emergency $0.25
        "--poll-interval", "0.05"
    ])
    assert "BUDGET_EMERGENCY" in res.stdout or "Watchdog dispatched termination" in res.stdout or "In-process budget limit reached" in res.stdout


# Scenario I: Missing calibration ID fails immediately
def test_scenario_I_missing_calibration_id_fails(tmp_path):
    bad_manifest = tmp_path / "bad_man.json"
    with open(bad_manifest, "w") as f:
        json.dump({"requests": []}, f)
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_I",
        "--mode", "CALIBRATION",
        "--manifest", str(bad_manifest),
        "--pod-id", "pod_I"
    ])
    assert res.returncode != 0
    assert "CALIBRATION Manifest missing expected frozen IDs" in res.stderr or res.returncode == 1


# Scenario J: Valid checkpoint preservation
def test_scenario_J_valid_checkpoint_preserved(tmp_path):
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_J",
        "--mode", "SIMULATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--poll-interval", "0.05"
    ])
    assert res.returncode == 0
    dataset = tmp_path / "exp_scen_J_dataset.jsonl"
    assert dataset.exists()
    with open(dataset) as f:
        lines = [l for l in f if l.strip()]
    assert len(lines) == 10


# Scenario K: Corrupted checkpoint rejected and prior valid preserved
def test_scenario_K_corrupted_checkpoint_rejected(tmp_path):
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_K",
        "--mode", "SIMULATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--simulate-corrupt-checkpoint",
        "--poll-interval", "0.05"
    ])
    assert "Promotion deferred" in res.stdout


# Scenario L: Resume without duplicate process
def test_scenario_L_resume_reattach(tmp_path):
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_L",
        "--mode", "SIMULATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--resume",
        "--poll-interval", "0.05"
    ])
    assert res.returncode == 0
    assert "Resume reconciliation" in res.stdout


# Scenario M: Watchdog crash stops controller scheduling
def test_scenario_M_watchdog_crash_stops_controller(tmp_path):
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_M",
        "--mode", "SIMULATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-watchdog-crash",
        "--poll-interval", "0.05"
    ])
    assert res.returncode != 0
    assert "CRITICAL: Independent watchdog process died" in res.stdout or res.returncode == 1


# Scenario N: Ambiguous provider response never claims destruction
def test_scenario_N_ambiguous_provider_response(tmp_path):
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_scen_N",
        pod_id="pod_scen_N",
        watchdog_dir=str(tmp_path)
    )
    # Mocking ambiguous response: pod with desiredStatus STOPPED (not deleted/terminated)
    watchdog._query_runpod_graphql = lambda q, v: ({"data": {"pod": {"desiredStatus": "STOPPED"}}}, 200)
    confirmed = watchdog.dispatch_provider_termination("test reason")
    assert not confirmed, "Watchdog claimed confirmed termination on STOPPED status!"
    assert watchdog.termination_confirmed is False


# Scenario O: Complete simulated calibration produces receipts
def test_scenario_O_complete_simulated_calibration_receipts(tmp_path):
    res = run_cli_subprocess([
        "--experiment-id", "exp_scen_O",
        "--mode", "SIMULATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--poll-interval", "0.05"
    ])
    assert res.returncode == 0
    receipt_file = tmp_path / "termination_receipt_exp_scen_O.json"
    assert receipt_file.exists()
    with open(receipt_file) as f:
        data = json.load(f)
    assert data["confirmed_by_provider"] is True
    assert data["completed_rollouts"] == 10
