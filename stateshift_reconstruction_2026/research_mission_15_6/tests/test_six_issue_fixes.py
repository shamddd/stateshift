#!/usr/bin/env python3
"""
Test Suite: StateShift Mission 15.6 Six Remaining Defect Fixes (Issues A-F)
Verifies:
  - Issue A: Controller death emergency termination policy (SIGKILL / dead PID)
  - Issue B: Explicit watchdog lifecycle ownership & transitions (8 states)
  - Issue C: Reconciled conservative financial accounting with pre-existing uptime
  - Issue D: Durable termination retry state machine and unconfirmed escalation
  - Issue E: Independent cryptographic authorization verification inside watchdog
  - Issue F: Exact mode-specific completion semantics in dataset verifier (10 vs 400)
"""

import os
import json
import time
import base64
import pytest
import tempfile
import shutil
import hashlib
from typing import Dict, Any
from cryptography.hazmat.primitives.asymmetric import ed25519

from research_mission_15_6.supervision.independent_financial_watchdog import (
    IndependentFinancialWatchdog,
    WatchdogLifecycleState,
    TerminationDurableState,
    ProviderResponseState
)
from research_mission_15_6.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    AuthorizationSecurityError,
    FROZEN_MANIFEST_SHA256,
    PINNED_MODEL_ID,
    PINNED_MODEL_REVISION
)
from research_mission_15_6.evaluation.dataset_verifier_v2 import (
    IndependentDatasetVerifierV2,
    DatasetVerificationError
)
from research_mission_15_6.calibration.calibration_config import (
    FROZEN_CALIBRATION_REQUEST_IDS,
    FROZEN_CALIBRATION_HASH
)


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


# ==================== Issue A Tests: Controller Death ====================

def test_issue_a_controller_confirmed_dead_triggers_emergency_termination(temp_dir):
    """Issue A: Dead controller PID triggers immediate termination on tick without spend breach."""
    dead_pid = 9999999
    try:
        os.kill(dead_pid, 0)
        pytest.skip("PID 9999999 happens to exist")
    except OSError:
        pass

    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_ctrl_death_test",
        pod_id="pod_ctrl_dead",
        watchdog_dir=temp_dir,
        session_id="sess_issue_a",
        main_controller_pid=dead_pid,
        max_authorized_usd=0.35,
        emergency_trigger_usd=0.25
    )

    watchdog._query_runpod_graphql = lambda q, v: ({"data": {"pod": None}}, 200)

    # Tick 1: Spend is $0.00, runtime is 0m, but controller is confirmed dead
    res = watchdog.run_supervision_tick(simulated_spend=0.00)
    assert res["should_terminate"] is True
    assert res["controller_status"] == "CONFIRMED_DEAD"
    assert "dead" in res["controller_explanation"].lower()
    assert watchdog.lifecycle_state == WatchdogLifecycleState.TERMINATION_CONFIRMED
    assert watchdog.termination_state == TerminationDurableState.TERMINATION_CONFIRMED
    assert watchdog.termination_confirmed is True


def test_issue_a_controller_clean_exit_allows_graceful_watchdog_shutdown(temp_dir):
    """Issue A: Controller clean exit with LOCAL_VERIFIED does NOT trigger emergency termination."""
    c_heartbeat = os.path.join(temp_dir, "controller_heartbeat.json")
    with open(c_heartbeat, "w") as f:
        json.dump({
            "state": "LOCAL_VERIFIED",
            "timestamp_utc": time.time()
        }, f)

    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_ctrl_clean_test",
        pod_id="pod_ctrl_clean",
        watchdog_dir=temp_dir,
        session_id="sess_issue_a_clean",
        main_controller_heartbeat_path=c_heartbeat,
        max_authorized_usd=0.35,
        emergency_trigger_usd=0.25
    )

    res = watchdog.run_supervision_tick(simulated_spend=0.05)
    assert res["should_terminate"] is False
    assert res["action"] == "CLEAN_SHUTDOWN"
    assert watchdog.lifecycle_state == WatchdogLifecycleState.WATCHDOG_EXITED
    assert watchdog.stop_requested is True


def test_issue_a_controller_stale_heartbeat_detection(temp_dir):
    """Issue A: Heartbeat older than stale_seconds is classified as STALE_HEARTBEAT."""
    c_heartbeat = os.path.join(temp_dir, "stale_heartbeat.json")
    with open(c_heartbeat, "w") as f:
        json.dump({
            "state": "INFERENCE_RUNNING",
            "timestamp_utc": time.time() - 45.0  # 45 seconds old
        }, f)

    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_ctrl_stale_test",
        pod_id="pod_ctrl_stale",
        watchdog_dir=temp_dir,
        session_id="sess_issue_a_stale",
        main_controller_heartbeat_path=c_heartbeat,
        main_controller_pid=os.getpid(),  # Alive
        max_authorized_usd=0.35,
        emergency_trigger_usd=0.25
    )

    status, expl = watchdog.evaluate_controller_status(stale_seconds=30.0)
    assert status == "STALE_HEARTBEAT"
    assert ">30" in expl


# ==================== Issue B Tests: Watchdog Lifecycle ====================

def test_issue_b_watchdog_lifecycle_states(temp_dir):
    """Issue B: Verifies explicit lifecycle states and state persistence."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_lifecycle_test",
        pod_id="pod_lifecycle",
        watchdog_dir=temp_dir,
        session_id="sess_issue_b",
        main_controller_pid=os.getpid()
    )

    assert watchdog.lifecycle_state == WatchdogLifecycleState.ACTIVE
    assert os.path.exists(watchdog.watchdog_state_file)

    with open(watchdog.watchdog_state_file, "r") as f:
        state_data = json.load(f)
    assert state_data["lifecycle_state"] == "ACTIVE"


# ==================== Issue C Tests: Conservative Baseline Accounting ====================

def test_issue_c_pre_existing_uptime_spend_calculation(temp_dir):
    """Issue C: Pre-existing uptime is included in conservative elapsed spend estimate."""
    # 1800 seconds pre-existing (0.5 hour) at $0.89/hr = $0.445
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_uptime_test",
        pod_id="pod_uptime",
        watchdog_dir=temp_dir,
        session_id="sess_issue_c",
        gpu_hourly_rate=0.89,
        pre_existing_uptime_seconds=1800.0
    )

    spend = watchdog.calculate_effective_spend(
        simulated_spend=None,
        provider_uptime_seconds=None,
        current_account_balance=None
    )
    assert spend >= 0.445


def test_issue_c_max_effective_spend_reconciliation(temp_dir):
    """Issue C: effective_spend = max(provider_estimated_spend, verified_balance_delta, conservative_elapsed_estimate)."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_max_spend_test",
        pod_id="pod_max_spend",
        watchdog_dir=temp_dir,
        session_id="sess_issue_c_max",
        gpu_hourly_rate=1.00,
        pre_existing_uptime_seconds=360.0  # 0.1 hr -> $0.10
    )
    watchdog.initial_account_balance = 10.00

    # Scenario 1: provider uptime gives higher spend ($0.30)
    s1 = watchdog.calculate_effective_spend(
        provider_uptime_seconds=1080.0,  # 0.3 hr -> $0.30
        current_account_balance=9.85     # delta $0.15
    )
    assert abs(s1 - 0.30) < 1e-4

    # Scenario 2: balance delta is higher ($0.50)
    s2 = watchdog.calculate_effective_spend(
        provider_uptime_seconds=720.0,   # 0.2 hr -> $0.20
        current_account_balance=9.50     # delta $0.50
    )
    assert abs(s2 - 0.50) < 1e-4

    # Scenario 3: conservative elapsed estimate is higher
    watchdog.pre_existing_uptime_seconds = 2880.0  # 0.8 hr -> $0.80
    s3 = watchdog.calculate_effective_spend(
        provider_uptime_seconds=360.0,   # $0.10
        current_account_balance=9.90     # delta $0.10
    )
    assert s3 >= 0.80


# ==================== Issue D Tests: Durable Termination Retry ====================

def test_issue_d_durable_termination_success(temp_dir):
    """Issue D: Bounded retry succeeds when pod is authoritatively deleted."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_term_success",
        pod_id="pod_term_succ",
        watchdog_dir=temp_dir,
        session_id="sess_issue_d_succ"
    )

    watchdog._query_runpod_graphql = lambda q, v: ({"data": {"pod": None}}, 200)

    success = watchdog.dispatch_provider_termination("Test termination success", max_retries=3)
    assert success is True
    assert watchdog.termination_confirmed is True
    assert watchdog.termination_state == TerminationDurableState.TERMINATION_CONFIRMED
    assert watchdog.lifecycle_state == WatchdogLifecycleState.TERMINATION_CONFIRMED

    receipt_file = os.path.join(temp_dir, "watchdog_termination_receipt_exp_term_success.json")
    assert os.path.exists(receipt_file)
    with open(receipt_file, "r") as f:
        rcpt = json.load(f)
    assert rcpt["confirmed_by_provider"] is True


def test_issue_d_durable_termination_unconfirmed_escalation(temp_dir):
    """Issue D: When provider fails to confirm destruction, sets TERMINATION_UNCONFIRMED and logs alert."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_term_unconfirmed",
        pod_id="pod_term_unconf",
        watchdog_dir=temp_dir,
        session_id="sess_issue_d_unconf"
    )

    running_resp = {
        "data": {
            "pod": {
                "id": "pod_term_unconf",
                "desiredStatus": "RUNNING",
                "runtime": {"uptimeInSeconds": 100}
            }
        }
    }
    watchdog._query_runpod_graphql = lambda q, v: (running_resp, 200)

    orig_sleep = time.sleep
    time.sleep = lambda s: None
    try:
        success = watchdog.dispatch_provider_termination("Test unconfirmed timeout", max_retries=2)
    finally:
        time.sleep = orig_sleep

    assert success is False
    assert watchdog.termination_confirmed is False
    assert watchdog.termination_state == TerminationDurableState.TERMINATION_UNCONFIRMED
    assert watchdog.lifecycle_state == WatchdogLifecycleState.TERMINATION_UNCONFIRMED

    receipt_file = os.path.join(temp_dir, "watchdog_termination_receipt_exp_term_unconfirmed.json")
    assert os.path.exists(receipt_file)
    with open(receipt_file, "r") as f:
        rcpt = json.load(f)
    assert rcpt["confirmed_by_provider"] is False

    alert_file = os.path.join(watchdog.alert_dir, "CRITICAL_UNCONFIRMED_TERMINATION_pod_term_unconf.json")
    assert os.path.exists(alert_file)
    with open(alert_file, "r") as f:
        alert = json.load(f)
    assert "escalation required" in alert["error"].lower()


# ==================== Issue E Tests: Independent Authorization Verification ====================

def test_issue_e_watchdog_verifies_valid_signed_authorization(temp_dir):
    """Issue E: Watchdog independently validates Ed25519 signature and binds limits."""
    priv_key = ed25519.Ed25519PrivateKey.generate()
    pub_key_b64 = base64.b64encode(priv_key.public_key().public_bytes_raw()).decode("utf-8")
    auth_file = os.path.join(temp_dir, "signed_auth.json")

    auth_doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv_key,
        experiment_id="exp_auth_valid",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="pod_auth_valid",
        max_spend_usd=0.35,
        emergency_trigger_usd=0.25,
        authorized_mode="CALIBRATION"
    )
    with open(auth_file, "w") as f:
        json.dump(auth_doc, f)

    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_auth_valid",
        pod_id="pod_auth_valid",
        watchdog_dir=temp_dir,
        session_id="sess_issue_e_valid",
        authorization_path=auth_file,
        trusted_public_key_b64=pub_key_b64
    )

    assert watchdog.max_authorized_usd == 0.35
    assert watchdog.emergency_trigger_usd == 0.25
    assert watchdog.verified_authorization_payload["experiment_id"] == "exp_auth_valid"


def test_issue_e_watchdog_rejects_tampered_authorization(temp_dir):
    """Issue E: Watchdog raises exception when authorization signature is invalid."""
    priv_key = ed25519.Ed25519PrivateKey.generate()
    pub_key_b64 = base64.b64encode(priv_key.public_key().public_bytes_raw()).decode("utf-8")
    auth_file = os.path.join(temp_dir, "tampered_auth.json")

    auth_doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv_key,
        experiment_id="exp_auth_tamper",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="pod_auth_tamper",
        max_spend_usd=0.35,
        emergency_trigger_usd=0.25,
        authorized_mode="CALIBRATION"
    )
    # Tamper with the spend limit without updating signature
    auth_doc["payload"]["max_incremental_spend_usd"] = 99.99

    with open(auth_file, "w") as f:
        json.dump(auth_doc, f)

    with pytest.raises(Exception) as exc_info:
        IndependentFinancialWatchdog(
            experiment_id="exp_auth_tamper",
            pod_id="pod_auth_tamper",
            watchdog_dir=temp_dir,
            session_id="sess_issue_e_tamper",
            authorization_path=auth_file,
            trusted_public_key_b64=pub_key_b64
        )
    assert "signature" in str(exc_info.value).lower() or "rejected" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()


def test_issue_e_watchdog_rejects_pod_mismatch(temp_dir):
    """Issue E: Watchdog raises exception when pod_id does not match authorization."""
    priv_key = ed25519.Ed25519PrivateKey.generate()
    pub_key_b64 = base64.b64encode(priv_key.public_key().public_bytes_raw()).decode("utf-8")
    auth_file = os.path.join(temp_dir, "mismatched_pod_auth.json")

    auth_doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv_key,
        experiment_id="exp_auth_mismatch",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="authorized_pod_123",
        max_spend_usd=0.35,
        emergency_trigger_usd=0.25,
        authorized_mode="CALIBRATION"
    )
    with open(auth_file, "w") as f:
        json.dump(auth_doc, f)

    with pytest.raises(Exception) as exc_info:
        IndependentFinancialWatchdog(
            experiment_id="exp_auth_mismatch",
            pod_id="DIFFERENT_POD_456",
            watchdog_dir=temp_dir,
            session_id="sess_issue_e_mismatch",
            authorization_path=auth_file,
            trusted_public_key_b64=pub_key_b64
        )
    assert "pod" in str(exc_info.value).lower()


# ==================== Issue F Tests: Exact Mode-Specific Completion Semantics ====================

def create_sample_rollout(manifest_req: Dict[str, Any], manifest_hash: str, experiment_id: str = "exp_calib_f_test") -> Dict[str, Any]:
    return {
        "request_id": manifest_req["request_id"],
        "problem_id": manifest_req["problem_id"],
        "condition_code": manifest_req["condition_code"],
        "prompt_sha256": manifest_req["prompt_sha256"],
        "gold_answer": manifest_req["gold_answer"],
        "model_id": manifest_req.get("model_id", "Qwen/Qwen2.5-Math-7B-Instruct"),
        "model_revision": manifest_req.get("model_revision", "main"),
        "tokenizer_revision": "main",
        "inference_engine": "vllm",
        "inference_engine_version": "0.6.3",
        "temperature": 0.0,
        "max_tokens": 768,
        "seed": 42,
        "sampling_mode": "greedy",
        "completion_status": "COMPLETED",
        "finish_reason": "stop",
        "source_type": "REAL_MODEL_INFERENCE",
        "experiment_id": experiment_id,
        "manifest_hash": manifest_hash,
        "generation_timestamp": time.time(),
        "model_output": "Let's solve step by step. \\boxed{" + str(manifest_req["gold_answer"]) + "}"
    }


def test_issue_f_calibration_exact_10_records_pass(temp_dir):
    """Issue F: CALIBRATION verifier accepts exactly the 10 frozen request IDs."""
    dataset_file = os.path.join(temp_dir, "calib_dataset.jsonl")
    manifest_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "manifests", "calibration_10_manifest.json")
    )
    with open(manifest_file, "rb") as f:
        m_hash = hashlib.sha256(f.read()).hexdigest()
    with open(manifest_file, "r") as f:
        m_data = json.load(f)

    with open(dataset_file, "w", encoding="utf-8") as f:
        for req in m_data["requests"]:
            f.write(json.dumps(create_sample_rollout(req, m_hash)) + "\n")

    verifier = IndependentDatasetVerifierV2(
        manifest_path=manifest_file,
        is_calibration=True
    )

    receipt_path = os.path.join(temp_dir, "receipt.json")
    passed, receipt = verifier.verify_final_local_dataset(dataset_file, receipt_output_path=receipt_path)
    assert passed is True
    assert receipt["passed"] is True
    assert receipt["completed_valid_count"] == 10
    assert receipt["total_records_expected"] == 10
    assert os.path.exists(receipt_path)


def test_issue_f_calibration_rejects_incomplete_dataset(temp_dir):
    """Issue F: CALIBRATION verifier rejects 9 records (requires exact 10)."""
    dataset_file = os.path.join(temp_dir, "incomplete_calib_dataset.jsonl")
    manifest_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "manifests", "calibration_10_manifest.json")
    )
    with open(manifest_file, "rb") as f:
        m_hash = hashlib.sha256(f.read()).hexdigest()
    with open(manifest_file, "r") as f:
        m_data = json.load(f)

    with open(dataset_file, "w", encoding="utf-8") as f:
        # Write only 9 records
        for req in m_data["requests"][:9]:
            f.write(json.dumps(create_sample_rollout(req, m_hash)) + "\n")

    verifier = IndependentDatasetVerifierV2(
        manifest_path=manifest_file,
        is_calibration=True
    )

    passed, receipt = verifier.verify_final_local_dataset(dataset_file)
    assert passed is False
    assert receipt["passed"] is False
    assert receipt["completed_valid_count"] == 9
    assert receipt["total_records_expected"] == 10
    assert receipt["missing_count"] == 1


def test_issue_f_calibration_rejects_extra_unexpected_records(temp_dir):
    """Issue F: CALIBRATION verifier rejects unexpected record outside frozen 10 IDs."""
    dataset_file = os.path.join(temp_dir, "overrun_calib_dataset.jsonl")
    manifest_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "manifests", "calibration_10_manifest.json")
    )
    with open(manifest_file, "rb") as f:
        m_hash = hashlib.sha256(f.read()).hexdigest()
    with open(manifest_file, "r") as f:
        m_data = json.load(f)

    with open(dataset_file, "w", encoding="utf-8") as f:
        for req in m_data["requests"]:
            f.write(json.dumps(create_sample_rollout(req, m_hash)) + "\n")
        # Add 11th unexpected record
        bad_req = dict(m_data["requests"][0])
        bad_req["request_id"] = "extra_unexpected_id_0011"
        f.write(json.dumps(create_sample_rollout(bad_req, m_hash)) + "\n")

    verifier = IndependentDatasetVerifierV2(
        manifest_path=manifest_file,
        is_calibration=True
    )

    passed, receipt = verifier.verify_final_local_dataset(dataset_file)
    assert passed is False
    assert receipt["passed"] is False
    assert any("not found in manifest" in err.lower() for err in receipt["errors"])
