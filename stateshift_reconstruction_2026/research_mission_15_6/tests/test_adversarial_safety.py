#!/usr/bin/env python3
"""
StateShift Research Mission 15.6 - Adversarial Safety Test Battery (20 Scenarios)
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

These 20 comprehensive adversarial tests exercise:
- Defect B1: Provisioning Boundary Authorization & Lock Enforcement (Scenarios 1-10)
- Defect B2: Explicit Termination State Machine & Provider Inconsistencies (Scenarios 11-20)
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
from research_mission_15_6.transport.runpod_transport_v2 import (
    ProductionRunPodTransportV2,
    safe_channel_wait,
    RunPodAPIError
)
from research_mission_15_6.supervision.independent_financial_watchdog import (
    IndependentFinancialWatchdog,
    WatchdogLifecycleState,
    TerminationDurableState,
    ProviderResponseState
)
from research_mission_15_6.deployment.supervisor_first_provisioner import (
    SupervisorFirstProvisioner,
    ProvisioningSecurityError,
    StagingTimeoutError,
    TerminationLifecycleState
)
from research_mission_15_6.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    AuthorizationSecurityError,
    FROZEN_MANIFEST_SHA256,
    PINNED_MODEL_ID,
    PINNED_MODEL_REVISION
)
from research_mission_15_6.deployment.safe_resume_reconciler import (
    SafeResumeReconciler,
    ReattachmentAction
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
# Scenario 1: Direct Unauthorized Provisioning Attempt
# =========================================================================
def test_adv_01_direct_unauthorized_provisioning(temp_dir):
    """Direct invocation of provision_single_pod without supervisor or with active lock must fail."""
    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_01",
        session_id="sess_01",
        local_data_dir=temp_dir,
        allow_mock_offline_testing=False
    )
    with pytest.raises(ProvisioningSecurityError) as exc_info:
        provisioner.provision_single_pod(lambda: "pod-should-not-exist")
    assert "Cloud execution lock active" in str(exc_info.value) or "Supervisor is not ready" in str(exc_info.value)


# =========================================================================
# Scenario 2: Missing Lock File but Locked Env Var Fails Closed
# =========================================================================
def test_adv_02_missing_lock_file_env_locked():
    """If lock file is absent but env var STATE_SHIFT_CLOUD_EXECUTION_DISABLED=1, execution is locked."""
    with patch.dict(os.environ, {LOCK_ENV_VAR: "1"}):
        with patch("os.path.isfile", return_value=False):
            locked, reason = is_cloud_execution_locked()
            assert locked is True
            assert "environment variable" in reason.lower()


# =========================================================================
# Scenario 3: Permissive Env Var but Lock File Present Fails Closed
# =========================================================================
def test_adv_03_permissive_env_with_lock_file():
    """If env var is set to 0 (permissive) but lock file exists, lock must remain FAIL-CLOSED."""
    with patch.dict(os.environ, {LOCK_ENV_VAR: "0"}):
        with patch("os.path.isfile", return_value=True):
            locked, reason = is_cloud_execution_locked()
            assert locked is True
            assert "Execution lock file found" in reason


# =========================================================================
# Scenario 4: Missing Cryptographic Authorization
# =========================================================================
def test_adv_04_missing_cryptographic_authorization(temp_dir, key_pair):
    """Authorization verification with empty payload fails closed."""
    _, pub = key_pair
    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub, nonce_registry_path=os.path.join(temp_dir, "nonces.json"))
    valid, reason = authorizer.verify_authorization(
        auth_doc={},
        active_experiment_id="adv_test_04",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert valid is False
    assert "missing required" in reason.lower()


# =========================================================================
# Scenario 5: Revoked or Invalid Cryptographic Signature
# =========================================================================
def test_adv_05_revoked_or_invalid_signature(temp_dir, key_pair):
    """Authorization signed with untrusted private key must be rejected."""
    priv1, pub1 = key_pair
    priv2 = ed25519.Ed25519PrivateKey.generate()
    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub1, nonce_registry_path=os.path.join(temp_dir, "nonces.json"))

    doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv2,
        experiment_id="adv_test_05",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="PRE_PROVISION"
    )
    valid, reason = authorizer.verify_authorization(
        auth_doc=doc,
        active_experiment_id="adv_test_05",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert valid is False
    assert "public key mismatch" in reason.lower() or "signature verification failed" in reason.lower()


# =========================================================================
# Scenario 6: Replayed Authorization Nonce
# =========================================================================
def test_adv_06_replayed_authorization_nonce(temp_dir, key_pair):
    """Replaying an authorization with an already recorded nonce must be rejected."""
    priv, pub = key_pair
    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub, nonce_registry_path=os.path.join(temp_dir, "nonces.json"))

    doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv,
        experiment_id="adv_test_06",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="PRE_PROVISION"
    )
    valid1, _ = authorizer.verify_authorization(
        auth_doc=doc,
        active_experiment_id="adv_test_06",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert valid1 is True

    valid2, reason2 = authorizer.verify_authorization(
        auth_doc=doc,
        active_experiment_id="adv_test_06",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert valid2 is False
    assert "replay detected" in reason2.lower() or "already been used" in reason2.lower()


# =========================================================================
# Scenario 7: Expired Authorization Timestamp
# =========================================================================
def test_adv_07_expired_authorization_timestamp(temp_dir, key_pair):
    """Authorization older than validity window must be rejected."""
    priv, pub = key_pair
    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub, nonce_registry_path=os.path.join(temp_dir, "nonces.json"))

    doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv,
        experiment_id="adv_test_07",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="PRE_PROVISION",
        validity_seconds=-10.0
    )
    valid, reason = authorizer.verify_authorization(
        auth_doc=doc,
        active_experiment_id="adv_test_07",
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert valid is False
    assert "expired" in reason.lower()


# =========================================================================
# Scenario 8: Supervisor Not Ready (Receipt Absent)
# =========================================================================
def test_adv_08_supervisor_not_ready_receipt_absent(temp_dir):
    """Attempting provisioning when supervisor readiness file is absent must fail."""
    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_08",
        session_id="sess_08",
        local_data_dir=temp_dir,
        allow_mock_offline_testing=True,
        simulate_supervisor=False
    )
    with pytest.raises(ProvisioningSecurityError) as exc_info:
        provisioner.provision_single_pod(lambda: "pod-123")
    assert "missing readiness receipt" in str(exc_info.value).lower()


# =========================================================================
# Scenario 9: Supervisor Dies After Readiness Receipt
# =========================================================================
def test_adv_09_supervisor_dies_after_readiness(temp_dir):
    """Supervisor dies after emitting readiness receipt; boundary check catches dead process."""
    mock_proc = MagicMock()
    mock_proc.poll.return_value = 137  # SIGKILL exit
    mock_proc.returncode = 137
    mock_proc.pid = 99123

    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_09",
        session_id="sess_09",
        local_data_dir=temp_dir,
        allow_mock_offline_testing=True,
        simulate_supervisor=False
    )
    provisioner.supervisor_ready = True
    provisioner.watchdog_process = mock_proc

    # Write a fresh readiness receipt
    receipt_path = os.path.join(temp_dir, "watchdog", f"watchdog_readiness_adv_test_09_sess_09.json")
    with open(receipt_path, "w") as f:
        json.dump({"status": "READY", "timestamp_utc": time.time()}, f)

    with pytest.raises(ProvisioningSecurityError) as exc_info:
        provisioner.provision_single_pod(lambda: "pod-123")
    assert "supervisor died after readiness handshake" in str(exc_info.value).lower()


# =========================================================================
# Scenario 10: Duplicate Provisioning Attempt Rejected (Single Attempt Invariant)
# =========================================================================
def test_adv_10_duplicate_provisioning_attempt_rejected(temp_dir):
    """Calling provision_single_pod a second time on same instance violates single attempt invariant."""
    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_10",
        session_id="sess_10",
        local_data_dir=temp_dir,
        allow_mock_offline_testing=True,
        simulate_supervisor=True
    )
    provisioner.spawn_preprovision_supervisor(0.5)

    pod_id = provisioner.provision_single_pod(lambda: "pod-first")
    assert pod_id == "pod-first"
    assert provisioner.provisioning_attempts == 1

    with pytest.raises(ProvisioningSecurityError) as exc_info:
        provisioner.provision_single_pod(lambda: "pod-second")
    assert "duplicate provisioning prohibited" in str(exc_info.value).lower() or "single-attempt invariant violated" in str(exc_info.value).lower()


# =========================================================================
# Scenario 11: Creation Callback Raises After Ambiguous Provider Response
# =========================================================================
def test_adv_11_creation_callback_raises_ambiguous_provider_response(temp_dir):
    """If creation callback throws an exception, state remains RESOURCE_POSSIBLY_CREATED."""
    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_11",
        session_id="sess_11",
        local_data_dir=temp_dir,
        allow_mock_offline_testing=True,
        simulate_supervisor=True
    )
    provisioner.spawn_preprovision_supervisor(0.5)

    def failing_callback():
        raise ConnectionResetError("Provider reset connection midway through pod create")

    with pytest.raises(ProvisioningSecurityError) as exc_info:
        provisioner.provision_single_pod(failing_callback)

    assert "Provider creation callback failed" in str(exc_info.value)
    assert provisioner.termination_state == TerminationLifecycleState.RESOURCE_POSSIBLY_CREATED


# =========================================================================
# Scenario 12: Termination API Success Without Destruction Confirmation
# =========================================================================
def test_adv_12_termination_success_without_destruction_confirmation(temp_dir):
    """Provider says OK to terminate, but status poll shows RUNNING. Teardown must NOT confirm destruction."""
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.return_value = (True, {"status": "SUCCESS"})
    mock_transport.get_pod_metadata.return_value = {"exists": True, "status": "RUNNING"}

    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_12",
        session_id="sess_12",
        local_data_dir=temp_dir,
        transport=mock_transport,
        allow_mock_offline_testing=True,
        simulate_supervisor=True
    )
    provisioner.active_pod_id = "pod-zombie-1"

    success, msg = provisioner.emergency_teardown(reason="Test termination unconfirmed", max_verification_checks=2, verification_delay=0.01)
    assert success is False
    assert "UNCONFIRMED" in msg
    assert provisioner.termination_state == TerminationLifecycleState.MANUAL_INTERVENTION_REQUIRED
    assert os.path.exists(provisioner.unresolved_resources_path)


# =========================================================================
# Scenario 13: Termination API Timeout Escalation
# =========================================================================
def test_adv_13_termination_api_timeout_escalation(temp_dir):
    """Provider status queries raise timeout exceptions. Teardown safely escalates to operator."""
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.return_value = (True, {"status": "SUCCESS"})
    mock_transport.get_pod_metadata.side_effect = RunPodAPIError("504 Gateway Timeout")

    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_13",
        session_id="sess_13",
        local_data_dir=temp_dir,
        transport=mock_transport,
        allow_mock_offline_testing=True,
        simulate_supervisor=True
    )
    provisioner.active_pod_id = "pod-timeout-1"

    success, msg = provisioner.emergency_teardown(reason="Provider 504 on teardown", max_verification_checks=2, verification_delay=0.01)
    assert success is False
    assert provisioner.termination_state == TerminationLifecycleState.MANUAL_INTERVENTION_REQUIRED
    with open(provisioner.unresolved_resources_path) as f:
        data = json.load(f)
    assert data["pod_id"] == "pod-timeout-1"


# =========================================================================
# Scenario 14: Provider Reports Pod Still Running / Stopped
# =========================================================================
def test_adv_14_provider_reports_stopped_pod_unconfirmed(temp_dir):
    """Provider reports STOPPED (which still incurs storage/reservation cost). Must NOT confirm destruction."""
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.return_value = (True, {"status": "SUCCESS"})
    mock_transport.get_pod_metadata.return_value = {"exists": True, "status": "STOPPED"}

    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_14",
        session_id="sess_14",
        local_data_dir=temp_dir,
        transport=mock_transport,
        allow_mock_offline_testing=True,
        simulate_supervisor=True
    )
    provisioner.active_pod_id = "pod-stopped-1"

    success, msg = provisioner.emergency_teardown(reason="Test STOPPED is not TERMINATED", max_verification_checks=2, verification_delay=0.01)
    assert success is False
    assert provisioner.termination_state == TerminationLifecycleState.MANUAL_INTERVENTION_REQUIRED


# =========================================================================
# Scenario 15: Provider Reports Pod Absent (Confirmed Destruction)
# =========================================================================
def test_adv_15_provider_reports_pod_absent_confirmed(temp_dir):
    """Provider reports exists=False. Teardown marks TERMINATION_CONFIRMED and cleans up supervisor."""
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None

    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.return_value = (True, {"status": "SUCCESS"})
    mock_transport.get_pod_metadata.return_value = {"exists": False, "status": "NOT_FOUND"}

    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_15",
        session_id="sess_15",
        local_data_dir=temp_dir,
        transport=mock_transport,
        allow_mock_offline_testing=True,
        simulate_supervisor=False
    )
    provisioner.active_pod_id = "pod-clean-1"
    provisioner.watchdog_process = mock_proc

    success, msg = provisioner.emergency_teardown(reason="Clean teardown", max_verification_checks=1, verification_delay=0.01)
    assert success is True
    assert "destruction verified" in msg
    assert provisioner.termination_state == TerminationLifecycleState.TERMINATION_CONFIRMED
    mock_proc.terminate.assert_called_once()


# =========================================================================
# Scenario 16: Provider Returns Inconsistent/500 State During Status Poll
# =========================================================================
def test_adv_16_provider_returns_inconsistent_500_state(temp_dir):
    """Provider returns internal server error responses during verification loop."""
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.return_value = (True, {"status": "SUCCESS"})
    mock_transport.get_pod_metadata.return_value = {"error": "500 Internal Server Error", "exists": True}

    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_16",
        session_id="sess_16",
        local_data_dir=temp_dir,
        transport=mock_transport,
        allow_mock_offline_testing=True,
        simulate_supervisor=True
    )
    provisioner.active_pod_id = "pod-500-error"

    success, _ = provisioner.emergency_teardown(reason="Provider 500 error", max_verification_checks=2, verification_delay=0.01)
    assert success is False
    assert provisioner.termination_state == TerminationLifecycleState.MANUAL_INTERVENTION_REQUIRED


# =========================================================================
# Scenario 17: Safe Resume Reconciliation Crash Handling
# =========================================================================
def test_adv_17_safe_resume_reconciliation_crash_handling():
    """SafeResumeReconciler encountering corrupted remote execution record halts safely for operator."""
    mock_transport = MagicMock()
    mock_transport.execute.return_value = (0, "NOT_JSON_CORRUPTED{")

    reconciler = SafeResumeReconciler(
        transport=mock_transport,
        remote_work_dir="/workspace/stateshift"
    )
    action, active_pid, rationale = reconciler.reconcile_remote_process(
        local_experiment_id="adv_test_17",
        expected_manifest_sha256=FROZEN_MANIFEST_SHA256,
        last_known_pid=1234
    )
    assert action == ReattachmentAction.HALT_FOR_OPERATOR
    assert "corrupted" in rationale.lower()


# =========================================================================
# Scenario 18: Safe Resume After Controller Restart
# =========================================================================
def test_adv_18_safe_resume_after_controller_restart():
    """Reconciler identifies active remote process and returns REATTACH cleanly."""
    mock_transport = MagicMock()
    rec_payload = {
        "experiment_id": "adv_test_18",
        "manifest_sha256": FROZEN_MANIFEST_SHA256,
        "pid": 5544
    }
    hb_payload = {
        "timestamp_utc": time.time(),
        "records_completed": 5,
        "is_running": True
    }
    def mock_exec(cmd, ip=None, port=22):
        if "execution_record.json" in cmd:
            return 0, json.dumps(rec_payload)
        if "runner.pid" in cmd:
            return 0, "5544"
        if "ps -p" in cmd or "remote_experiment_runner.py" in cmd:
            return 0, "5544 python3 remote_experiment_runner.py --experiment-id adv_test_18"
        if "heartbeat.json" in cmd:
            return 0, json.dumps(hb_payload)
        return 0, ""

    mock_transport.execute.side_effect = mock_exec

    reconciler = SafeResumeReconciler(
        transport=mock_transport,
        remote_work_dir="/workspace/stateshift"
    )
    action, active_pid, rationale = reconciler.reconcile_remote_process(
        local_experiment_id="adv_test_18",
        expected_manifest_sha256=FROZEN_MANIFEST_SHA256,
        last_known_pid=5544
    )
    assert action == ReattachmentAction.REATTACH
    assert active_pid == 5544
    assert "reattach" in rationale.lower() or "active" in rationale.lower() or "clean" in rationale.lower()


# =========================================================================
# Scenario 19: Emergency Teardown Invoked Twice (Idempotence)
# =========================================================================
def test_adv_19_emergency_teardown_idempotent(temp_dir):
    """Calling emergency_teardown() twice in succession is fully idempotent."""
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.return_value = (True, {"status": "SUCCESS"})
    mock_transport.get_pod_metadata.return_value = {"exists": False, "status": "NOT_FOUND"}

    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_19",
        session_id="sess_19",
        local_data_dir=temp_dir,
        transport=mock_transport,
        allow_mock_offline_testing=True,
        simulate_supervisor=True
    )
    provisioner.active_pod_id = "pod-idemp-1"

    success1, msg1 = provisioner.emergency_teardown(reason="First call", max_verification_checks=1, verification_delay=0.01)
    assert success1 is True
    assert provisioner.termination_state == TerminationLifecycleState.TERMINATION_CONFIRMED

    # Second invocation
    success2, msg2 = provisioner.emergency_teardown(reason="Second call", max_verification_checks=1, verification_delay=0.01)
    assert success2 is True
    assert provisioner.termination_state == TerminationLifecycleState.TERMINATION_CONFIRMED


# =========================================================================
# Scenario 20: Teardown With No Resource Created (Clean No-Op)
# =========================================================================
def test_adv_20_teardown_with_no_resource_created(temp_dir):
    """Calling emergency_teardown() when active_pod_id is None cleanly returns NO_RESOURCE."""
    provisioner = SupervisorFirstProvisioner(
        experiment_id="adv_test_20",
        session_id="sess_20",
        local_data_dir=temp_dir,
        allow_mock_offline_testing=True,
        simulate_supervisor=True
    )
    assert provisioner.active_pod_id is None
    success, msg = provisioner.emergency_teardown(reason="Teardown before provision")
    assert success is True
    assert "No active resource" in msg
    assert provisioner.termination_state == TerminationLifecycleState.NO_RESOURCE
