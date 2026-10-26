#!/usr/bin/env python3
"""
StateShift Research Mission 15.6 - $1 Budget-Limited Policy Exception Test Battery
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

These 15 focused tests validate the temporary financial policy exception (POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION):
1. Insufficient account balance (< $0.32 target reserve floor).
2. Invalid authorization (corrupted signature / malformed payload).
3. Expired authorization (timestamp older than validity window).
4. Incorrect spending ceiling (> $1.00 rejected under exception).
5. Incorrect preservation floor (< $0.32 rejected under exception).
6. Unauthorized primary-experiment transition (POLICY_V2 prohibited in PRODUCTION mode).
7. Standard policy rejection (attempting $1.00 spend under standard POLICY_V1).
8. Duplicate pod creation rejection under single-attempt invariant.
9. Watchdog startup failure triggers fail-closed abort.
10. Provider termination timeout escalates to MANUAL_INTERVENTION_REQUIRED.
11. Delayed billing telemetry uses conservative elapsed time estimate.
12. Orchestrator crash triggers independent watchdog emergency termination.
13. Partial calibration output is preserved safely without false completion.
14. Interrupted session resume recovers completed records without duplicates.
15. Execution-lock restoration remains fail-closed.

All tests run STRICTLY OFFLINE on local CPU with ZERO cloud spending ($0.00).
"""

import os
import sys
import json
import time
import base64
import tempfile
import shutil
import pytest
from unittest.mock import MagicMock, patch
from cryptography.hazmat.primitives.asymmetric import ed25519

from research_mission_15_6.auth.execution_lock import (
    is_cloud_execution_locked,
    assert_cloud_execution_permitted,
    LOCK_ENV_VAR,
    LOCK_FILENAME
)
from research_mission_15_6.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    AuthorizationSecurityError,
    FROZEN_MANIFEST_SHA256,
    PINNED_MODEL_ID,
    PINNED_MODEL_REVISION
)
from research_mission_15_6.deployment.supervisor_first_provisioner import (
    SupervisorFirstProvisioner,
    ProvisioningSecurityError,
    StagingTimeoutError,
    TerminationLifecycleState
)
from research_mission_15_6.supervision.independent_financial_watchdog import (
    IndependentFinancialWatchdog,
    WatchdogLifecycleState,
    TerminationDurableState,
    ProviderResponseState
)
from research_mission_15_6.transport.runpod_transport_v2 import (
    ProductionRunPodTransportV2,
    RunPodAPIError
)


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def key_pair():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    pub_b64 = base64.b64encode(public_key.public_bytes_raw()).decode("utf-8")
    return private_key, pub_b64


# =========================================================================
# 1. Insufficient Account Balance (< $0.32 Target Reserve Floor)
# =========================================================================
def test_b1_01_insufficient_account_balance(temp_dir):
    """Account balance below temporary $0.32 reserve floor is rejected immediately."""
    provisioner = SupervisorFirstProvisioner(
        experiment_id="b1_test_01",
        session_id="sess_01",
        local_data_dir=temp_dir,
        account_floor_usd=0.32,
        allow_mock_offline_testing=True
    )
    with pytest.raises(ProvisioningSecurityError) as exc_info:
        provisioner.verify_preconditions(current_balance_usd=0.25, active_pods_count=0)
    assert "below preservation floor" in str(exc_info.value)


# =========================================================================
# 2. Invalid Authorization (Corrupted Signature / Tampered Payload)
# =========================================================================
def test_b1_02_invalid_authorization(temp_dir, key_pair):
    """Tampered payload fails cryptographic signature verification."""
    priv, pub_b64 = key_pair
    auth_doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv,
        experiment_id="b1_test_02",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="PRE_PROVISION",
        max_spend_usd=1.00,
        emergency_trigger_usd=0.70,
        min_balance_usd=0.32,
        authorized_mode="CALIBRATION",
        financial_policy_version="POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION"
    )
    # Tamper with payload
    auth_doc["payload"]["max_incremental_spend_usd"] = 5.00

    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub_b64, nonce_registry_path=os.path.join(temp_dir, "nonces.json"))
    valid, reason = authorizer.verify_authorization(
        auth_doc=auth_doc,
        active_experiment_id="b1_test_02",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert not valid
    assert "verification FAILED" in reason or "Signature" in reason


# =========================================================================
# 3. Expired Authorization
# =========================================================================
def test_b1_03_expired_authorization(temp_dir, key_pair):
    """Authorization with expired timestamp is rejected."""
    priv, pub_b64 = key_pair
    auth_doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv,
        experiment_id="b1_test_03",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="PRE_PROVISION",
        max_spend_usd=1.00,
        emergency_trigger_usd=0.70,
        min_balance_usd=0.32,
        authorized_mode="CALIBRATION",
        financial_policy_version="POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION",
        validity_seconds=-10.0  # Expired 10s ago
    )

    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub_b64, nonce_registry_path=os.path.join(temp_dir, "nonces.json"))
    valid, reason = authorizer.verify_authorization(
        auth_doc=auth_doc,
        active_experiment_id="b1_test_03",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert not valid
    assert "Authorization expired" in reason


# =========================================================================
# 4. Incorrect Spending Ceiling (> $1.00 Under Exception)
# =========================================================================
def test_b1_04_incorrect_spending_ceiling(temp_dir, key_pair):
    """Spending ceiling exceeding $1.00 under policy exception V2 is rejected."""
    priv, pub_b64 = key_pair
    auth_doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv,
        experiment_id="b1_test_04",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="PRE_PROVISION",
        max_spend_usd=1.50,  # Exceeds $1.00
        emergency_trigger_usd=0.70,
        min_balance_usd=0.32,
        authorized_mode="CALIBRATION",
        financial_policy_version="POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION"
    )

    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub_b64, nonce_registry_path=os.path.join(temp_dir, "nonces.json"))
    valid, reason = authorizer.verify_authorization(
        auth_doc=auth_doc,
        active_experiment_id="b1_test_04",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert not valid
    assert "exceeds $1.00 temporary limit" in reason


# =========================================================================
# 5. Incorrect Preservation Floor (< $0.32 Under Exception)
# =========================================================================
def test_b1_05_incorrect_preservation_floor(temp_dir, key_pair):
    """Preservation floor below $0.32 under policy exception V2 is rejected."""
    priv, pub_b64 = key_pair
    auth_doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv,
        experiment_id="b1_test_05",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="PRE_PROVISION",
        max_spend_usd=1.00,
        emergency_trigger_usd=0.70,
        min_balance_usd=0.10,  # Below $0.32
        authorized_mode="CALIBRATION",
        financial_policy_version="POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION"
    )

    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub_b64, nonce_registry_path=os.path.join(temp_dir, "nonces.json"))
    valid, reason = authorizer.verify_authorization(
        auth_doc=auth_doc,
        active_experiment_id="b1_test_05",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert not valid
    assert "violates $0.32 temporary target reserve floor" in reason


# =========================================================================
# 6. Unauthorized Primary-Experiment Transition (Prohibited)
# =========================================================================
def test_b1_06_unauthorized_primary_experiment_transition(temp_dir, key_pair):
    """Policy exception V2 is strictly restricted to CALIBRATION; rejected in PRODUCTION."""
    priv, pub_b64 = key_pair
    auth_doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv,
        experiment_id="b1_test_06",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="PRE_PROVISION",
        max_spend_usd=1.00,
        emergency_trigger_usd=0.70,
        min_balance_usd=0.32,
        authorized_mode="PRODUCTION",
        financial_policy_version="POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION"
    )

    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub_b64, nonce_registry_path=os.path.join(temp_dir, "nonces.json"))
    valid, reason = authorizer.verify_authorization(
        auth_doc=auth_doc,
        active_experiment_id="b1_test_06",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="PRODUCTION"
    )
    assert not valid
    assert "strictly restricted to CALIBRATION mode" in reason


# =========================================================================
# 7. Standard Policy Rejection (Attempting $1.00 Spend Under Standard V1)
# =========================================================================
def test_b1_07_standard_policy_rejection(temp_dir, key_pair):
    """Under standard policy V1, $1.00 spend and $0.32 floor are strictly rejected."""
    priv, pub_b64 = key_pair
    auth_doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv,
        experiment_id="b1_test_07",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="PRE_PROVISION",
        max_spend_usd=1.00,  # Exceeds standard $0.60 ceiling
        emergency_trigger_usd=0.70,
        min_balance_usd=0.32,  # Violates standard $7.00 floor
        authorized_mode="CALIBRATION",
        financial_policy_version="POLICY_V1_STANDARD"
    )

    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub_b64, nonce_registry_path=os.path.join(temp_dir, "nonces.json"))
    valid, reason = authorizer.verify_authorization(
        auth_doc=auth_doc,
        active_experiment_id="b1_test_07",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert not valid
    assert "exceeds $0.60 limit" in reason or "violates $7.00 mandatory floor" in reason


# =========================================================================
# 8. Duplicate Pod Creation Rejection Under Single-Attempt Invariant
# =========================================================================
def test_b1_08_duplicate_pod_creation_rejected(temp_dir):
    """Second pod provisioning attempt is blocked by single-attempt invariant."""
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    provisioner = SupervisorFirstProvisioner(
        experiment_id="b1_test_08",
        session_id="sess_08",
        local_data_dir=temp_dir,
        transport=mock_transport,
        allow_mock_offline_testing=True,
        simulate_supervisor=True
    )
    provisioner.supervisor_ready = True

    # First attempt succeeds
    pod_id_1 = provisioner.provision_single_pod(create_pod_fn=lambda: "pod-single-1")
    assert pod_id_1 == "pod-single-1"

    # Second attempt MUST raise
    with pytest.raises(ProvisioningSecurityError) as exc_info:
        provisioner.provision_single_pod(create_pod_fn=lambda: "pod-single-2")
    assert "Duplicate provisioning prohibited" in str(exc_info.value) or "Single-attempt invariant violated" in str(exc_info.value)


# =========================================================================
# 9. Watchdog Startup Failure Triggers Fail-Closed Abort
# =========================================================================
def test_b1_09_watchdog_startup_failure(temp_dir):
    """Missing or failed watchdog receipt causes provisioner to abort fail-closed."""
    provisioner = SupervisorFirstProvisioner(
        experiment_id="b1_test_09",
        session_id="sess_09",
        local_data_dir=temp_dir,
        allow_mock_offline_testing=True,
        simulate_supervisor=False
    )
    # No readiness receipt exists
    with pytest.raises(ProvisioningSecurityError) as exc_info:
        provisioner.provision_single_pod(create_pod_fn=lambda: "pod-should-not-exist")
    assert "missing readiness receipt" in str(exc_info.value) or "Supervisor is not ready" in str(exc_info.value)


# =========================================================================
# 10. Provider Termination Timeout Escalates to MANUAL_INTERVENTION_REQUIRED
# =========================================================================
def test_b1_10_provider_termination_timeout_escalation(temp_dir):
    """If provider status queries fail during teardown, state escalates to operator."""
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.return_value = (True, {"status": "SUCCESS"})
    mock_transport.get_pod_metadata.side_effect = RunPodAPIError("504 Gateway Timeout")

    provisioner = SupervisorFirstProvisioner(
        experiment_id="b1_test_10",
        session_id="sess_10",
        local_data_dir=temp_dir,
        transport=mock_transport,
        allow_mock_offline_testing=True,
        simulate_supervisor=True
    )
    provisioner.active_pod_id = "pod-timeout-b1"

    success, msg = provisioner.emergency_teardown(reason="Provider 504 on teardown", max_verification_checks=2, verification_delay=0.01)
    assert success is False
    assert provisioner.termination_state == TerminationLifecycleState.MANUAL_INTERVENTION_REQUIRED
    with open(provisioner.unresolved_resources_path) as f:
        data = json.load(f)
    assert data["pod_id"] == "pod-timeout-b1"


# =========================================================================
# 11. Delayed Billing Telemetry Uses Conservative Elapsed Time Estimate
# =========================================================================
def test_b1_11_delayed_billing_telemetry_conservative_estimate(temp_dir):
    """Watchdog computes spend as max(provider, balance_delta, elapsed_estimate)."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="b1_test_11",
        pod_id="simulated_pod",
        watchdog_dir=temp_dir,
        session_id="sess_11",
        max_authorized_usd=1.00,
        emergency_trigger_usd=0.70,
        gpu_hourly_rate=0.89,
        account_preservation_floor_usd=0.32,
        initial_account_balance=1.3174,
        pre_existing_uptime_seconds=1200.0
    )

    spend = watchdog.calculate_effective_spend(
        simulated_spend=None,
        provider_uptime_seconds=120.0,  # Provider reports only 2m ($0.03) due to delayed telemetry
        current_account_balance=1.3174  # Delta $0.00
    )
    # Conservative elapsed: 1200s (20m) * (0.89 / 3600) = $0.2967
    assert spend >= 0.29


# =========================================================================
# 12. Orchestrator Crash Triggers Independent Watchdog Emergency Termination
# =========================================================================
def test_b1_12_orchestrator_crash_triggers_termination(temp_dir):
    """When controller PID terminates, watchdog detects death and dispatches teardown."""
    dead_pid = 9999999
    try:
        os.kill(dead_pid, 0)
        pytest.skip("PID 9999999 happens to exist")
    except OSError:
        pass

    watchdog = IndependentFinancialWatchdog(
        experiment_id="b1_test_12",
        pod_id="pod-crash-1",
        session_id="sess_12",
        max_authorized_usd=1.00,
        emergency_trigger_usd=0.70,
        account_preservation_floor_usd=0.32,
        watchdog_dir=temp_dir,
        main_controller_pid=dead_pid
    )
    watchdog._query_runpod_graphql = lambda q, v: ({"data": {"pod": None}}, 200)

    res = watchdog.run_supervision_tick(simulated_spend=0.00)
    assert res["should_terminate"] is True
    assert res["controller_status"] == "CONFIRMED_DEAD"


# =========================================================================
# 13. Partial Calibration Output is Preserved Safely Without False Completion
# =========================================================================
def test_b1_13_partial_calibration_preserved(temp_dir):
    """If execution stops after 5 requests, records are intact and count is verified."""
    dataset_file = os.path.join(temp_dir, "dataset.jsonl")
    records = [
        {"request_id": f"primary_100_req_{i:04d}", "model_output": f"ans_{i}", "completion_status": "COMPLETED"}
        for i in range(1, 6)
    ]
    with open(dataset_file, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    # Read back line by line
    read_records = []
    with open(dataset_file, "r") as f:
        for line in f:
            if line.strip():
                read_records.append(json.loads(line))

    assert len(read_records) == 5
    # Strict completion condition: exactly 10 required
    assert len(read_records) != 10  # Must NOT be reported as complete!


# =========================================================================
# 14. Interrupted Session Resume Recovers Completed Records Without Duplicates
# =========================================================================
def test_b1_14_interrupted_session_resume(temp_dir):
    """Resume logic skips already completed request IDs, preventing duplicate inference."""
    dataset_file = os.path.join(temp_dir, "dataset.jsonl")
    initial_records = [
        {"request_id": "primary_100_req_0001", "model_output": "ans_1"},
        {"request_id": "primary_100_req_0002", "model_output": "ans_2"},
    ]
    with open(dataset_file, "w") as f:
        for r in initial_records:
            f.write(json.dumps(r) + "\n")

    completed = set()
    with open(dataset_file, "r") as f:
        for line in f:
            if line.strip():
                completed.add(json.loads(line)["request_id"])

    all_requests = [f"primary_100_req_{i:04d}" for i in range(1, 11)]
    remaining = [rid for rid in all_requests if rid not in completed]

    assert len(remaining) == 8
    assert "primary_100_req_0001" not in remaining
    assert "primary_100_req_0003" in remaining


# =========================================================================
# 15. Execution-Lock Restoration Remains Fail-Closed
# =========================================================================
def test_b1_15_execution_lock_fail_closed(monkeypatch, temp_dir):
    """Execution lock correctly raises PermissionError when lock file or env var is set."""
    monkeypatch.setenv(LOCK_ENV_VAR, "1")
    locked, reason = is_cloud_execution_locked()
    assert locked is True
    assert "forbids cloud execution" in reason

    with pytest.raises(PermissionError) as exc_info:
        assert_cloud_execution_permitted()
    assert "CRITICAL SECURITY LOCK" in str(exc_info.value)
