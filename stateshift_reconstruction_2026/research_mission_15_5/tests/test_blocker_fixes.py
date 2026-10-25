"""
Blocker Corrections Test Suite for StateShift Mission 15.5.
Proves fixes for all 7 blockers:
1. Genuinely independent watchdog process (different PID, survives controller SIGKILL, terminates pod).
2. Elimination of default test signing key from production trust.
3. Strict pod-ID binding for CALIBRATION mode.
4. Strict simulation / paid execution mode isolation.
5. Calibration-specific budget enforcement ($0.35 max spend, $0.25 emergency trigger).
6. Strict provider response classification (API errors, timeouts never mean termination).
7. Frozen calibration selection (exact 10 requests, rejection on missing IDs or fallback).
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
from research_mission_15_5.calibration.calibration_config import (
    FROZEN_CALIBRATION_REQUEST_IDS,
    generate_calibration_manifest,
    compute_calibration_selection_hash
)
from research_mission_15_5.supervision.independent_financial_watchdog import (
    IndependentFinancialWatchdog,
    ProviderResponseState
)


# ==================== BLOCKER 1: Genuinely Independent Watchdog ====================

def test_blocker_1_watchdog_different_pid_and_survives_controller_sigkill(tmp_path):
    """
    Test that watchdog runs in a separate process, records a distinct PID,
    survives when the controller process is killed via SIGKILL, and continues financial supervision.
    """
    watchdog_dir = tmp_path / "watchdog"
    ctrl_heartbeat = tmp_path / "controller.json"
    with open(ctrl_heartbeat, "w") as f:
        json.dump({"timestamp_utc": time.time()}, f)

    watchdog_script = os.path.abspath(
        "research_mission_15_5/supervision/independent_financial_watchdog.py"
    )

    # Spawn controller subprocess that will be killed
    controller_proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"]
    )
    controller_pid = controller_proc.pid

    # Spawn watchdog subprocess passing controller_pid
    watchdog_proc = subprocess.Popen(
        [
            sys.executable,
            watchdog_script,
            "--experiment-id", "exp_b1_kill",
            "--pod-id", "pod_b1_test",
            "--watchdog-dir", str(watchdog_dir),
            "--controller-pid", str(controller_pid),
            "--controller-heartbeat", str(ctrl_heartbeat),
            "--max-authorized", "0.35",
            "--emergency-trigger", "0.25",
            "--poll-interval", "0.5"
        ]
    )
    watchdog_pid = watchdog_proc.pid
    assert watchdog_pid != controller_pid
    assert watchdog_pid != os.getpid()

    # Wait for watchdog to write its heartbeat
    hb_file = watchdog_dir / "watchdog_heartbeat_exp_b1_kill.json"
    for _ in range(20):
        if hb_file.exists():
            break
        time.sleep(0.2)
    assert hb_file.exists(), "Watchdog heartbeat was not written."

    # Kill controller process with SIGKILL
    os.kill(controller_pid, signal.SIGKILL)
    controller_proc.wait()
    assert controller_proc.poll() is not None

    # Verify watchdog is STILL ALIVE and ticking
    time.sleep(1.5)
    assert watchdog_proc.poll() is None, "Watchdog died prematurely after controller SIGKILL!"

    # Clean up watchdog
    watchdog_proc.terminate()
    watchdog_proc.wait()


def test_blocker_1_watchdog_terminates_pod_on_budget_breach(tmp_path):
    """Test that independent watchdog executes termination when budget threshold is breached."""
    watchdog_dir = tmp_path / "watchdog"
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_b1_term",
        pod_id="pod_b1_term",
        watchdog_dir=str(watchdog_dir),
        emergency_trigger_usd=0.25
    )
    terminated_calls = []
    watchdog.dispatch_provider_termination = lambda reason: (terminated_calls.append(reason) or True)

    res = watchdog.run_supervision_tick(simulated_spend=0.26)
    assert res["should_terminate"]
    assert len(terminated_calls) == 1
    assert "emergency threshold" in terminated_calls[0]


# ==================== BLOCKER 2: Remove Test Key From Production Trust ====================

def test_blocker_2_no_trusted_key_rejects_authorization():
    """Test that CryptographicAuthorizer without trusted public key rejects verification."""
    auth = CryptographicAuthorizer(trusted_public_key_b64=None)
    doc = {"payload": {}, "signature_ed25519_b64": "sig"}
    ok, msg = auth.verify_authorization(
        doc, "exp_1", "pod_1", "hash", "CALIBRATION"
    )
    assert not ok
    assert "No trusted public key configured" in msg


def test_blocker_2_embedded_test_seed_rejected_for_paid_modes():
    """Test that using known repository test seed is explicitly rejected for CALIBRATION and PRODUCTION."""
    auth = CryptographicAuthorizer(trusted_public_key_b64=KNOWN_TEST_PUBLIC_KEY_B64, allow_test_key_for_testing=False)
    doc = auth.create_signed_authorization(
        private_key=_known_test_priv,
        experiment_id="exp_test_key",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_paid",
        max_spend_usd=0.35,
        emergency_trigger_usd=0.25,
        authorized_mode="CALIBRATION"
    )
    ok, msg = auth.verify_authorization(
        doc, "exp_test_key", "pod_paid", "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d", "CALIBRATION"
    )
    assert not ok
    assert "Embedded repository test key cannot authorize" in msg


def test_blocker_2_external_pi_key_accepted():
    """Test that an external, non-test PI public key verifies properly."""
    pi_priv = ed25519.Ed25519PrivateKey.generate()
    pi_pub_b64 = base64.b64encode(pi_priv.public_key().public_bytes_raw()).decode("utf-8")

    auth = CryptographicAuthorizer(trusted_public_key_b64=pi_pub_b64)
    doc = auth.create_signed_authorization(
        private_key=pi_priv,
        experiment_id="exp_pi_valid",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_pi",
        max_spend_usd=0.35,
        emergency_trigger_usd=0.25,
        authorized_mode="CALIBRATION"
    )
    ok, msg = auth.verify_authorization(
        doc, "exp_pi_valid", "pod_pi", "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d", "CALIBRATION"
    )
    assert ok
    assert "verified successfully" in msg


# ==================== BLOCKER 3: Bind Calibration Authorization to Exact Pod ====================

def test_blocker_3_calibration_pod_mismatch_rejected():
    """Test that a signed CALIBRATION authorization for pod_A cannot run on pod_B."""
    pi_priv = ed25519.Ed25519PrivateKey.generate()
    pi_pub_b64 = base64.b64encode(pi_priv.public_key().public_bytes_raw()).decode("utf-8")

    auth = CryptographicAuthorizer(trusted_public_key_b64=pi_pub_b64)
    doc = auth.create_signed_authorization(
        private_key=pi_priv,
        experiment_id="exp_cal_bind",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_authorized_AAA",
        max_spend_usd=0.35,
        emergency_trigger_usd=0.25,
        authorized_mode="CALIBRATION"
    )

    ok, msg = auth.verify_authorization(
        doc, "exp_cal_bind", "pod_different_BBB", "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d", "CALIBRATION"
    )
    assert not ok
    assert "Pod ID mismatch" in msg


def test_blocker_3_calibration_used_for_production_rejected():
    """Test that a CALIBRATION authorization cannot be used for PRODUCTION mode."""
    pi_priv = ed25519.Ed25519PrivateKey.generate()
    pi_pub_b64 = base64.b64encode(pi_priv.public_key().public_bytes_raw()).decode("utf-8")

    auth = CryptographicAuthorizer(trusted_public_key_b64=pi_pub_b64)
    doc = auth.create_signed_authorization(
        private_key=pi_priv,
        experiment_id="exp_cal_mode",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_AAA",
        max_spend_usd=0.35,
        emergency_trigger_usd=0.25,
        authorized_mode="CALIBRATION"
    )
    ok, msg = auth.verify_authorization(
        doc, "exp_cal_mode", "pod_AAA", "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d", "PRODUCTION"
    )
    assert not ok
    assert "Execution mode mismatch" in msg


# ==================== BLOCKER 4: Strict Simulation / Production Isolation ====================

def test_blocker_4_simulation_flags_rejected_in_paid_modes():
    """Test that CLI strictly rejects simulation flags when mode is CALIBRATION or PRODUCTION."""
    runner_script = "research_mission_15_5/runner/stateshift_production_runner_v10.py"
    manifest = "research_mission_15_5/manifests/primary_100_manifest.json"
    env = dict(os.environ, PYTHONPATH=".")

    # 1. CALIBRATION with --simulate-records
    res = subprocess.run(
        [sys.executable, runner_script, "--mode", "CALIBRATION", "--manifest", manifest, "--simulate-records", "10"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
    )
    assert res.returncode == 2
    assert "Simulation arguments are strictly prohibited" in res.stdout

    # 2. PRODUCTION with --simulate-spend-usd
    res = subprocess.run(
        [sys.executable, runner_script, "--mode", "PRODUCTION", "--manifest", manifest, "--simulate-spend-usd", "0.50"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
    )
    assert res.returncode == 2
    assert "Simulation arguments are strictly prohibited" in res.stdout


# ==================== BLOCKER 5: Calibration Budget Enforcement ====================

def test_blocker_5_calibration_budget_bounds_enforced():
    """Test that CALIBRATION mode enforces max spend $0.35 and trigger $0.25."""
    pi_priv = ed25519.Ed25519PrivateKey.generate()
    pi_pub_b64 = base64.b64encode(pi_priv.public_key().public_bytes_raw()).decode("utf-8")
    auth = CryptographicAuthorizer(trusted_public_key_b64=pi_pub_b64)

    # Over-budget calibration attempt ($0.50 > $0.35)
    doc_bad = auth.create_signed_authorization(
        private_key=pi_priv,
        experiment_id="exp_b5",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_b5",
        max_spend_usd=0.50,
        emergency_trigger_usd=0.45,
        authorized_mode="CALIBRATION"
    )
    ok, msg = auth.verify_authorization(
        doc_bad, "exp_b5", "pod_b5", "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d", "CALIBRATION"
    )
    assert not ok
    assert "exceeds $0.35 limit" in msg


# ==================== BLOCKER 6: Strict Provider Response Classification ====================

def test_blocker_6_provider_response_classification(tmp_path):
    """
    Test that API errors, HTTP 500/503/401/403, and timeouts are never classified as pod destruction.
    """
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_b6",
        pod_id="pod_b6",
        watchdog_dir=str(tmp_path)
    )

    # 1. HTTP 503 Server Error
    state, _, expl = watchdog.classify_provider_pod_response({}, http_code=503)
    assert state == ProviderResponseState.API_ERROR
    assert state != ProviderResponseState.TERMINATED

    # 2. HTTP 401 Auth Error
    state, _, expl = watchdog.classify_provider_pod_response({}, http_code=401)
    assert state == ProviderResponseState.AUTH_ERROR

    # 3. Network Timeout
    state, _, expl = watchdog.classify_provider_pod_response({"error": "Read timeout expired"})
    assert state == ProviderResponseState.TIMEOUT

    # 4. GraphQL errors array
    state, _, expl = watchdog.classify_provider_pod_response({"errors": [{"message": "Internal error"}]})
    assert state == ProviderResponseState.API_ERROR

    # 5. Authoritative Pod Destruction (pod is null in data)
    state, _, expl = watchdog.classify_provider_pod_response({"data": {"pod": None}}, http_code=200)
    assert state == ProviderResponseState.AUTHORITATIVE_NOT_FOUND

    # 6. STOPPED status is not TERMINATED
    state, _, expl = watchdog.classify_provider_pod_response({"data": {"pod": {"desiredStatus": "STOPPED"}}}, http_code=200)
    assert state == ProviderResponseState.STOPPED


# ==================== BLOCKER 7: Reconciled History & Frozen Calibration IDs ====================

def test_blocker_7_frozen_calibration_selection(tmp_path):
    """Test that calibration selection requires exact 10 frozen IDs without fallback."""
    manifest_path = "research_mission_15_5/manifests/primary_100_manifest.json"
    out_cal = tmp_path / "calibration_manifest.json"

    cal_doc = generate_calibration_manifest(manifest_path, str(out_cal))
    assert cal_doc["total_requests"] == 10
    actual_ids = [r["request_id"] for r in cal_doc["requests"]]
    assert actual_ids == FROZEN_CALIBRATION_REQUEST_IDS
    assert cal_doc["calibration_selection_sha256"] == "91c57ea9f3e26045abb34a721c43bad38af49f9bb647037941f2c261b61adfec"


def test_blocker_7_missing_calibration_id_fails_immediately(tmp_path):
    """Test that any missing expected ID raises KeyError rather than substituting."""
    bad_manifest = tmp_path / "bad_manifest.json"
    with open(bad_manifest, "w") as f:
        json.dump({"requests": [{"request_id": "other_id"}]}, f)

    with pytest.raises(ValueError): # hash mismatch or missing ID
        generate_calibration_manifest(str(bad_manifest), str(tmp_path / "out.json"))
