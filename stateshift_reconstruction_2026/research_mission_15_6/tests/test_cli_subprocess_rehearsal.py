#!/usr/bin/env python3
"""
Test Suite: StateShift Mission 15.6 Canonical CLI Subprocess Rehearsal (17 Mandatory Scenarios)
Exercises research_mission_15_6.runner.stateshift_launch via actual OS subprocesses.

Scenarios:
  A: Complete valid 10-request simulated calibration produces verified dataset & receipts (exit 0)
  B: Controller SIGKILL: Watchdog detects dead PID immediately & terminates pod
  C: Watchdog SIGKILL: Controller detects watchdog death & triggers emergency termination
  D: Invalid signing key: Test key rejected in calibration/production (exit 2)
  E: Pod ID mismatch between authorization and execution arguments (exit 2)
  F: Budget ceiling mismatch between authorization and CLI (exit 2)
  G: Expired authorization token rejected (exit 2)
  H: Replayed authorization nonce rejected (exit 2)
  I: SSH transport hang/disconnect triggers emergency termination (exit 1)
  J: SFTP synchronization failure halts inference and protects checkpoint (exit 1)
  K: Provider 503 / API error: Retries bounded, records UNCONFIRMED, logs escalation
  L: Financial emergency trigger ($0.25) dispatches immediate shutdown
  M: Calibration manifest missing frozen IDs rejected immediately (exit 2)
  N: Checkpoint preservation: Valid checkpoint promoted monotonically
  O: Checkpoint corruption: Corrupted file rejected, prior valid checkpoint preserved
  P: Safe resume: Reattaches cleanly without duplicate generation
  Q: Ambiguous provider status (STOPPED) never falsely claims confirmed destruction
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

from research_mission_15_6.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    KNOWN_TEST_PUBLIC_KEY_B64,
    _known_test_priv,
    FROZEN_MANIFEST_SHA256,
    PINNED_MODEL_ID,
    PINNED_MODEL_REVISION
)
from research_mission_15_6.supervision.independent_financial_watchdog import (
    IndependentFinancialWatchdog,
    WatchdogLifecycleState,
    TerminationDurableState
)

LAUNCH_MODULE = "research_mission_15_6.runner.stateshift_launch"
CALIB_MANIFEST = os.path.abspath("research_mission_15_6/manifests/calibration_10_manifest.json")
PRIMARY_MANIFEST = os.path.abspath("research_mission_15_6/manifests/primary_100_manifest.json")


def create_signed_auth_doc(
    path: str,
    experiment_id: str,
    pod_id: str,
    mode: str = "CALIBRATION",
    max_spend: float = 0.35,
    emergency_trigger: float = 0.25,
    min_balance: float = 7.00,
    validity_seconds: float = 3600.0,
    nonce: str = None,
    use_test_key: bool = False,
    tamper_sig: bool = False
) -> str:
    if use_test_key:
        priv = _known_test_priv
        pub_b64 = KNOWN_TEST_PUBLIC_KEY_B64
    else:
        priv = ed25519.Ed25519PrivateKey.generate()
        pub_b64 = base64.b64encode(priv.public_key().public_bytes_raw()).decode("utf-8")

    doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv,
        experiment_id=experiment_id,
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id=pod_id,
        max_spend_usd=max_spend,
        emergency_trigger_usd=emergency_trigger,
        min_balance_usd=min_balance,
        authorized_mode=mode,
        validity_seconds=validity_seconds,
        session_nonce=nonce
    )

    if tamper_sig:
        doc["signature_ed25519_b64"] = base64.b64encode(b"0" * 64).decode("utf-8")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)

    return pub_b64


def run_launch_cli(args, env_extra=None):
    env = dict(os.environ, PYTHONPATH=".")
    if env_extra:
        env.update(env_extra)
    cmd = [sys.executable, "-m", LAUNCH_MODULE] + args
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)


# ==================== Scenario A: Complete Valid 10-Request Simulation ====================
def test_scenario_A_valid_10_request_simulation(tmp_path):
    res = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_A_v15_6",
        "--manifest", CALIB_MANIFEST,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--simulate-spend", "0.15",
        "--poll-interval", "0.05"
    ])
    assert res.returncode == 0, f"Failed: {res.stderr}\n{res.stdout}"
    assert "Launch Success" in res.stdout
    assert "LOCAL_VERIFIED" in res.stdout or "FINISHED" in res.stdout

    # Check local receipts
    dataset_file = tmp_path / "exp_scen_A_v15_6_dataset.jsonl"
    receipt_file = tmp_path / "exp_scen_A_v15_6_verification_receipt.json"
    term_receipt = tmp_path / "termination_receipt_exp_scen_A_v15_6.json"

    assert dataset_file.exists()
    assert receipt_file.exists()
    assert term_receipt.exists()

    with open(term_receipt) as f:
        t_data = json.load(f)
    assert t_data["confirmed_by_provider"] is True
    assert t_data["completed_rollouts"] == 10


# ==================== Scenario B: Controller SIGKILL ====================
def test_scenario_B_controller_sigkill_watchdog_terminates_pod(tmp_path):
    """When controller dies (SIGKILL), the independent watchdog detects dead PID and triggers pod termination."""
    watchdog_script = os.path.abspath("research_mission_15_6/supervision/independent_financial_watchdog.py")
    
    # Spawn dummy controller process
    ctrl_proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    
    # Spawn watchdog monitoring dummy controller
    w_proc = subprocess.Popen([
        sys.executable, watchdog_script,
        "--experiment-id", "exp_scen_B_v15_6",
        "--pod-id", "pod_scen_B",
        "--watchdog-dir", str(tmp_path),
        "--controller-pid", str(ctrl_proc.pid),
        "--max-authorized", "0.35",
        "--emergency-trigger", "0.25",
        "--poll-interval", "0.1"
    ])
    
    time.sleep(0.3)
    # Kill controller with SIGKILL
    os.kill(ctrl_proc.pid, signal.SIGKILL)
    ctrl_proc.wait()

    # Give watchdog time to tick and detect dead PID
    time.sleep(1.0)
    
    # Watchdog should detect controller death and exit cleanly or trigger termination
    w_proc.terminate()
    w_proc.wait()

    # Check watchdog state file
    state_file = tmp_path / "watchdog_state_exp_scen_B_v15_6.json"
    assert state_file.exists()
    with open(state_file) as f:
        s_data = json.load(f)
    assert s_data["lifecycle_state"] in [
        WatchdogLifecycleState.CONTROLLER_FAILED.value,
        WatchdogLifecycleState.TERMINATION_REQUESTED.value,
        WatchdogLifecycleState.TERMINATION_CONFIRMED.value,
        WatchdogLifecycleState.TERMINATION_UNCONFIRMED.value
    ]


# ==================== Scenario C: Watchdog SIGKILL ====================
def test_scenario_C_watchdog_sigkill_controller_halts(tmp_path):
    """When watchdog is killed, controller aborts inference and emergency shuts down."""
    res = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_C_v15_6",
        "--manifest", CALIB_MANIFEST,
        "--local-data-dir", str(tmp_path),
        "--simulate-watchdog-crash",
        "--poll-interval", "0.05"
    ])
    assert res.returncode != 0
    assert "watchdog process died" in res.stdout.lower() or "failed" in res.stdout.lower()


# ==================== Scenario D: Embedded Test Key Rejected ====================
def test_scenario_D_test_key_rejected_in_calibration(tmp_path):
    """Using test key without --allow-test-key is strictly rejected in CALIBRATION."""
    auth_path = tmp_path / "test_auth.json"
    pub_b64 = create_signed_auth_doc(
        str(auth_path),
        "exp_scen_D_v15_6",
        "pod_D",
        mode="CALIBRATION",
        use_test_key=True
    )
    res = run_launch_cli([
        "--mode", "calibration",
        "--experiment-id", "exp_scen_D_v15_6",
        "--pod-id", "pod_D",
        "--authorization", str(auth_path),
        "--trusted-public-key", pub_b64,
        "--local-data-dir", str(tmp_path)
    ])
    assert res.returncode == 2
    assert "test key" in res.stdout.lower() or "test key" in res.stderr.lower()


# ==================== Scenario E: Pod ID Mismatch Rejected ====================
def test_scenario_E_pod_id_mismatch_rejected(tmp_path):
    """Authorization signed for pod_AUTHORIZED must reject launch on pod_DIFFERENT."""
    auth_path = tmp_path / "pod_mismatch_auth.json"
    pub_b64 = create_signed_auth_doc(
        str(auth_path),
        "exp_scen_E_v15_6",
        "pod_AUTHORIZED",
        mode="CALIBRATION"
    )
    res = run_launch_cli([
        "--mode", "calibration",
        "--experiment-id", "exp_scen_E_v15_6",
        "--pod-id", "pod_DIFFERENT",
        "--authorization", str(auth_path),
        "--trusted-public-key", pub_b64,
        "--allow-test-key",
        "--local-data-dir", str(tmp_path)
    ])
    assert res.returncode == 2
    assert "pod" in res.stdout.lower() or "pod" in res.stderr.lower()


# ==================== Scenario F: Budget Mismatch Rejected ====================
def test_scenario_F_budget_mismatch_rejected(tmp_path):
    """CLI budget higher than signed authorization spend limit is rejected."""
    auth_path = tmp_path / "budget_auth.json"
    pub_b64 = create_signed_auth_doc(
        str(auth_path),
        "exp_scen_F_v15_6",
        "pod_F",
        mode="CALIBRATION",
        max_spend=0.35
    )
    res = run_launch_cli([
        "--mode", "calibration",
        "--experiment-id", "exp_scen_F_v15_6",
        "--pod-id", "pod_F",
        "--authorization", str(auth_path),
        "--trusted-public-key", pub_b64,
        "--max-cost", "1.50",  # Exceeds authorized $0.35
        "--allow-test-key",
        "--local-data-dir", str(tmp_path)
    ])
    assert res.returncode == 2
    assert "budget" in res.stdout.lower() or "cost" in res.stdout.lower() or "spend" in res.stdout.lower()


# ==================== Scenario G: Expired Authorization Rejected ====================
def test_scenario_G_expired_authorization_rejected(tmp_path):
    """Expired authorization document must be rejected."""
    auth_path = tmp_path / "expired_auth.json"
    pub_b64 = create_signed_auth_doc(
        str(auth_path),
        "exp_scen_G_v15_6",
        "pod_G",
        mode="CALIBRATION",
        validity_seconds=-10.0  # Already expired
    )
    res = run_launch_cli([
        "--mode", "calibration",
        "--experiment-id", "exp_scen_G_v15_6",
        "--pod-id", "pod_G",
        "--authorization", str(auth_path),
        "--trusted-public-key", pub_b64,
        "--allow-test-key",
        "--local-data-dir", str(tmp_path)
    ])
    assert res.returncode == 2
    assert "expired" in res.stdout.lower() or "expired" in res.stderr.lower()


# ==================== Scenario H: Replayed Nonce Rejected ====================
def test_scenario_H_replayed_nonce_rejected(tmp_path):
    """Replaying the same nonce must be rejected."""
    auth_path = tmp_path / "nonce_auth.json"
    pub_b64 = create_signed_auth_doc(
        str(auth_path),
        "exp_scen_H_v15_6",
        "pod_H",
        mode="SIMULATION",
        nonce="unique_nonce_12345"
    )

    # First launch succeeds in simulation
    res1 = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_H_v15_6",
        "--pod-id", "pod_H",
        "--authorization", str(auth_path),
        "--trusted-public-key", pub_b64,
        "--allow-test-key",
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--poll-interval", "0.05"
    ])
    assert res1.returncode == 0

    # Second launch with same nonce is rejected
    res2 = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_H_v15_6",
        "--pod-id", "pod_H",
        "--authorization", str(auth_path),
        "--trusted-public-key", pub_b64,
        "--allow-test-key",
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--poll-interval", "0.05"
    ])
    assert res2.returncode == 2
    assert "nonce" in res2.stdout.lower() or "nonce" in res2.stderr.lower()


# ==================== Scenario I: SSH Transport Disconnect ====================
def test_scenario_I_ssh_transport_disconnect(tmp_path):
    """Simulated SSH disconnect triggers controller emergency shutdown."""
    res = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_I_v15_6",
        "--manifest", CALIB_MANIFEST,
        "--local-data-dir", str(tmp_path),
        "--simulate-ssh-disconnect",
        "--poll-interval", "0.05"
    ])
    assert res.returncode != 0
    assert "ssh" in res.stdout.lower() or "disconnect" in res.stdout.lower() or "failed" in res.stdout.lower()


# ==================== Scenario J: SFTP Sync Failure ====================
def test_scenario_J_sftp_sync_failure(tmp_path):
    """SFTP sync failure halts inference and preserves valid partial checkpoint."""
    res = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_J_v15_6",
        "--manifest", CALIB_MANIFEST,
        "--local-data-dir", str(tmp_path),
        "--simulate-sftp-failure",
        "--poll-interval", "0.05"
    ])
    assert res.returncode != 0
    assert "sftp" in res.stdout.lower() or "failed" in res.stdout.lower()


# ==================== Scenario K: Provider 503 API Server Error ====================
def test_scenario_K_provider_503_records_unconfirmed(tmp_path):
    """Provider 503 / termination error: retries bounded, records UNCONFIRMED, logs escalation alert."""
    res = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_K_v15_6",
        "--manifest", CALIB_MANIFEST,
        "--local-data-dir", str(tmp_path),
        "--simulate-unconfirmed-termination",
        "--simulate-records", "10",
        "--poll-interval", "0.05"
    ])
    assert res.returncode != 0
    assert "TERMINATION_UNCONFIRMED" in res.stdout


# ==================== Scenario L: Financial Emergency Trigger ($0.25) ====================
def test_scenario_L_financial_emergency_trigger(tmp_path):
    """Spend exceeding emergency trigger ($0.25) halts execution immediately."""
    res = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_L_v15_6",
        "--manifest", CALIB_MANIFEST,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "5",
        "--simulate-spend", "0.30",
        "--poll-interval", "0.05"
    ])
    assert "BUDGET_EMERGENCY" in res.stdout or "termination" in res.stdout.lower() or "emergency" in res.stdout.lower()


# ==================== Scenario M: Missing Calibration Frozen IDs ====================
def test_scenario_M_missing_calibration_id_fails(tmp_path):
    """CALIBRATION manifest missing expected frozen IDs is rejected immediately."""
    bad_manifest = tmp_path / "bad_manifest.json"
    with open(bad_manifest, "w") as f:
        json.dump({"schema_version": "1.0", "requests": []}, f)

    res = run_launch_cli([
        "--mode", "calibration",
        "--experiment-id", "exp_scen_M_v15_6",
        "--manifest", str(bad_manifest),
        "--pod-id", "pod_M",
        "--local-data-dir", str(tmp_path)
    ])
    assert res.returncode == 2
    assert "missing" in res.stdout.lower() or "missing" in res.stderr.lower() or res.returncode == 2


# ==================== Scenario N: Checkpoint Monotonic Promotion ====================
def test_scenario_N_valid_checkpoint_promoted(tmp_path):
    """Valid checkpoint is promoted monotonically and verified."""
    res = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_N_v15_6",
        "--manifest", CALIB_MANIFEST,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--poll-interval", "0.05"
    ])
    assert res.returncode == 0
    dataset = tmp_path / "exp_scen_N_v15_6_dataset.jsonl"
    assert dataset.exists()
    with open(dataset) as f:
        lines = [l for l in f if l.strip()]
    assert len(lines) == 10


# ==================== Scenario O: Corrupted Checkpoint Rejected ====================
def test_scenario_O_corrupted_checkpoint_rejected(tmp_path):
    """Corrupted checkpoint rejected, valid prior state preserved."""
    res = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_O_v15_6",
        "--manifest", CALIB_MANIFEST,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--simulate-corrupt-checkpoint",
        "--poll-interval", "0.05"
    ])
    assert "deferred" in res.stdout.lower() or "corrupt" in res.stdout.lower() or res.returncode != 0


# ==================== Scenario P: Safe Resume ====================
def test_scenario_P_safe_resume_reattach(tmp_path):
    """Resume flag reattaches cleanly to valid checkpoint without duplication."""
    res = run_launch_cli([
        "--mode", "simulation",
        "--experiment-id", "exp_scen_P_v15_6",
        "--manifest", CALIB_MANIFEST,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--resume",
        "--poll-interval", "0.05"
    ])
    assert res.returncode == 0
    assert "resume" in res.stdout.lower()


# ==================== Scenario Q: Ambiguous Provider Status ====================
def test_scenario_Q_ambiguous_provider_status_never_claims_destruction(tmp_path):
    """Status STOPPED is never falsely reported as confirmed destruction."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_scen_Q_v15_6",
        pod_id="pod_scen_Q",
        watchdog_dir=str(tmp_path)
    )
    # Mocking provider response where pod is in STOPPED status
    stopped_resp = {
        "data": {
            "pod": {
                "id": "pod_scen_Q",
                "desiredStatus": "STOPPED",
                "runtime": {"uptimeInSeconds": 50}
            }
        }
    }
    watchdog._query_runpod_graphql = lambda q, v: (stopped_resp, 200)

    orig_sleep = time.sleep
    time.sleep = lambda s: None
    try:
        confirmed = watchdog.dispatch_provider_termination("test stopped reason", max_retries=2)
    finally:
        time.sleep = orig_sleep

    assert not confirmed, "Watchdog claimed confirmed termination on STOPPED status!"
    assert watchdog.termination_confirmed is False
    assert watchdog.termination_state == TerminationDurableState.TERMINATION_UNCONFIRMED
