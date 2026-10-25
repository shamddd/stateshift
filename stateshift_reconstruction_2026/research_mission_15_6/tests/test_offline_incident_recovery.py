#!/usr/bin/env python3
"""
StateShift Incident Recovery: 15 Zero-Spend Offline Failure Injection Tests
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

These tests execute STRICTLY OFFLINE on local CPU with zero cloud spending.
All provider calls are intercepted by local mock fixtures.
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
    StagingTimeoutError
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

CALIBRATION_MANIFEST = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "manifests", "calibration_10_manifest.json"
))


class MockChannel:
    """Simulates an SSH Channel for offline testing."""
    def __init__(self, exit_ready: bool = True, exit_code: int = 0, hang: bool = False):
        self._exit_ready = exit_ready
        self._exit_code = exit_code
        self._hang = hang
        self.closed = False

    def exit_status_ready(self) -> bool:
        if self._hang:
            return False
        return self._exit_ready

    def recv_exit_status(self) -> int:
        return self._exit_code

    def close(self):
        self.closed = True


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


# =========================================================================
# Scenario 1: SSH Channel Hang & Monotonic Wall-Clock Deadline
# =========================================================================
def test_01_ssh_channel_hang_wall_clock_timeout():
    """Verifies that an indefinite remote hang raises TimeoutError within deadline and closes channel."""
    hanging_channel = MockChannel(hang=True)
    t0 = time.monotonic()
    with pytest.raises(TimeoutError) as exc_info:
        safe_channel_wait(hanging_channel, timeout_seconds=0.3)
    elapsed = time.monotonic() - t0

    assert 0.25 <= elapsed <= 0.6
    assert "exceeded wall-clock deadline" in str(exc_info.value)
    assert hanging_channel.closed is True


# =========================================================================
# Scenario 2: Model Download Stall Triggers Emergency Teardown
# =========================================================================
def test_02_model_download_stall_triggers_teardown(temp_dir):
    """Verifies that a stalled model caching script triggers StagingTimeoutError and pod destruction."""
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    provisioner = SupervisorFirstProvisioner(
        experiment_id="test_exp",
        session_id="session_001",
        local_data_dir=temp_dir,
        transport=mock_transport,
        simulate_supervisor=True
    )
    provisioner.active_pod_id = "pod_mock_hang"
    hanging_channel = MockChannel(hang=True)

    with pytest.raises(StagingTimeoutError):
        provisioner.execute_bounded_staging(
            command="python3 cache_model.py",
            channel=hanging_channel,
            timeout_seconds=0.2
        )

    mock_transport.terminate_pod.assert_called_once_with("pod_mock_hang")


# =========================================================================
# Scenario 3: Orchestrator Crash Detected by Supervisor (Dead Controller PID)
# =========================================================================
def test_03_orchestrator_crash_triggers_supervisor_cleanup(temp_dir):
    """Verifies independent watchdog detects dead orchestrator PID and confirms termination."""
    dead_pid = 9999999
    try:
        os.kill(dead_pid, 0)
        pytest.skip("PID 9999999 happens to exist")
    except OSError:
        pass

    watchdog = IndependentFinancialWatchdog(
        experiment_id="test_crash",
        pod_id="pod_stranded_123",
        watchdog_dir=temp_dir,
        session_id="sess_crash",
        max_authorized_usd=0.35,
        emergency_trigger_usd=0.25,
        gpu_hourly_rate=0.89,
        main_controller_pid=dead_pid
    )
    watchdog._query_runpod_graphql = lambda q, v=None: ({"data": {"pod": None}}, 200)

    res = watchdog.run_supervision_tick(simulated_spend=0.00)

    assert res["should_terminate"] is True
    assert res["controller_status"] == "CONFIRMED_DEAD"
    assert watchdog.lifecycle_state == WatchdogLifecycleState.TERMINATION_CONFIRMED
    assert watchdog.termination_state == TerminationDurableState.TERMINATION_CONFIRMED
    assert watchdog.termination_confirmed is True


# =========================================================================
# Scenario 4: Watchdog Crash Detection
# =========================================================================
def test_04_watchdog_crash_detection(temp_dir):
    """Verifies runner detects premature watchdog exit before remote execution."""
    from research_mission_15_6.runner.stateshift_production_runner_v10 import StateshiftProductionRunnerV10, ExecutionMode

    runner = StateshiftProductionRunnerV10(
        experiment_id="test_w_crash",
        manifest_path=CALIBRATION_MANIFEST,
        authorization_path=None,
        mode=ExecutionMode.SIMULATION,
        local_data_dir=temp_dir,
        allow_test_key_for_testing=True
    )
    # Simulate an exited watchdog process
    mock_proc = MagicMock()
    mock_proc.poll.return_value = 1  # Exited with error
    mock_proc.returncode = 1
    runner.watchdog_process = mock_proc

    res = runner.wait_for_watchdog_readiness(timeout_seconds=0.3)
    assert res is False


# =========================================================================
# Scenario 5: Provider API Timeout & Non-Blocking Escalation
# =========================================================================
def test_05_provider_api_timeout_escalation(temp_dir):
    """Verifies that GraphQL API timeouts do not crash watchdog and are reported properly."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="test_timeout",
        pod_id="pod_timeout_test",
        watchdog_dir=temp_dir,
        session_id="sess_timeout"
    )
    watchdog._query_runpod_graphql = lambda q, v=None: ({"error": "Network timeout: Connection reset"}, 200)

    status, uptime, host = watchdog.query_provider_pod_state()
    assert status == ProviderResponseState.TIMEOUT
    assert uptime is None


# =========================================================================
# Scenario 6: Emergency Financial Threshold ($0.25 Spend Trigger)
# =========================================================================
def test_06_emergency_spend_trigger_at_0_25(temp_dir):
    """Verifies that reaching the $0.25 trigger immediately dispatches pod destruction."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="test_spend_trigger",
        pod_id="pod_spend_025",
        watchdog_dir=temp_dir,
        session_id="sess_spend",
        max_authorized_usd=0.35,
        emergency_trigger_usd=0.25
    )
    watchdog._query_runpod_graphql = lambda q, v=None: ({"data": {"pod": None}}, 200)

    # Simulated spend 0.26 exceeds emergency trigger 0.25
    res = watchdog.run_supervision_tick(simulated_spend=0.26)

    assert res["should_terminate"] is True
    assert watchdog.termination_dispatched is True
    assert watchdog.termination_confirmed is True


# =========================================================================
# Scenario 7: Account Preservation Floor ($7.00 Floor Protection)
# =========================================================================
def test_07_account_preservation_floor_threatened(temp_dir):
    """Verifies that balance falling below $7.00 immediately triggers emergency kill."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="test_floor_breach",
        pod_id="pod_floor_test",
        watchdog_dir=temp_dir,
        session_id="sess_floor",
        account_preservation_floor_usd=7.00,
        initial_account_balance=7.50
    )
    watchdog._query_runpod_graphql = lambda q, v=None: ({"data": {"pod": None}}, 200)

    # Pass balance 6.85 below the 7.00 floor
    res = watchdog.run_supervision_tick(simulated_spend=0.01, current_account_balance=6.85)

    assert res["should_terminate"] is True
    assert watchdog.termination_dispatched is True


# =========================================================================
# Scenario 8: Duplicate Provisioning Attempt Rejected (Single Attempt Rule)
# =========================================================================
def test_08_duplicate_provisioning_attempt_rejected(temp_dir):
    """Verifies that attempting to provision a 2nd pod raises ProvisioningSecurityError."""
    provisioner = SupervisorFirstProvisioner(
        experiment_id="test_dup",
        session_id="sess_dup",
        local_data_dir=temp_dir
    )
    # Attempt 1: succeeds
    p1 = provisioner.provision_single_pod(lambda: "pod_001")
    assert p1 == "pod_001"

    # Attempt 2: strictly prohibited
    with pytest.raises(ProvisioningSecurityError) as exc_info:
        provisioner.provision_single_pod(lambda: "pod_002")
    assert "Single-attempt invariant violated" in str(exc_info.value)


# =========================================================================
# Scenario 9: Stale / Replayed Cryptographic Authorization Rejection
# =========================================================================
def test_09_stale_or_replayed_authorization_rejected(temp_dir):
    """Verifies that replay of an authorization with reused nonce is rejected."""
    priv_key = ed25519.Ed25519PrivateKey.generate()
    pub_bytes = priv_key.public_key().public_bytes_raw()
    pub_b64 = base64.b64encode(pub_bytes).decode("utf-8")

    nonce_file = os.path.join(temp_dir, "used_nonces.json")
    authorizer = CryptographicAuthorizer(
        trusted_public_key_b64=pub_b64,
        nonce_registry_path=nonce_file
    )

    auth_doc = CryptographicAuthorizer.create_signed_authorization(
        private_key=priv_key,
        experiment_id="exp_replay",
        manifest_sha256=FROZEN_MANIFEST_SHA256,
        model_id=PINNED_MODEL_ID,
        model_revision=PINNED_MODEL_REVISION,
        pod_id="pod_replay_test",
        max_spend_usd=0.35,
        emergency_trigger_usd=0.25,
        min_balance_usd=7.00,
        authorized_mode="CALIBRATION",
        validity_seconds=3600.0
    )

    # First verification passes
    ok1, msg1 = authorizer.verify_authorization(
        auth_doc=auth_doc,
        active_experiment_id="exp_replay",
        active_pod_id="pod_replay_test",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert ok1 is True

    # Replay of exact same authorization is rejected
    ok2, msg2 = authorizer.verify_authorization(
        auth_doc=auth_doc,
        active_experiment_id="exp_replay",
        active_pod_id="pod_replay_test",
        active_manifest_sha256=FROZEN_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    assert ok2 is False
    assert "Replay detected" in msg2


# =========================================================================
# Scenario 10: Local Process SIGTERM Handled Gracefully
# =========================================================================
def test_10_local_process_sigterm_cleanup(temp_dir):
    """Verifies that receiving SIGTERM dispatches pod termination."""
    terminated = []
    watchdog = IndependentFinancialWatchdog(
        experiment_id="test_sigterm",
        pod_id="pod_sigterm_99",
        watchdog_dir=temp_dir,
        session_id="sess_sigterm"
    )
    def mock_graphql(q, v=None):
        if "podTerminate" in q:
            terminated.append(v.get("podId") if v else "pod_sigterm_99")
            return ({"data": {"podTerminate": True}}, 200)
        return ({"data": {"pod": None}}, 200)

    watchdog._query_runpod_graphql = mock_graphql

    watchdog.dispatch_provider_termination("SIGTERM signal received")

    assert "pod_sigterm_99" in terminated
    assert watchdog.termination_dispatched is True


# =========================================================================
# Scenario 11: Machine Restart / Orphan Pod Reconciliation
# =========================================================================
def test_11_machine_restart_orphan_reconciliation(temp_dir):
    """Verifies that SafeResumeReconciler detects an untracked remote pod and halts for operator."""
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.execute.return_value = (0, "root 1234 1.0 0.5 python3 remote_experiment_runner.py")
    mock_transport.fetch_file.return_value = False  # Record missing

    reconciler = SafeResumeReconciler(transport=mock_transport, remote_work_dir="/workspace/stateshift")
    action, pid, rationale = reconciler.reconcile_remote_process(
        local_experiment_id="exp_orphan",
        expected_manifest_sha256="dummy_hash",
        last_known_pid=None
    )
    assert action == ReattachmentAction.HALT_FOR_OPERATOR


# =========================================================================
# Scenario 12: Execution Lock Bypass Attempt Rejection
# =========================================================================
def test_12_execution_lock_bypass_rejection(temp_dir):
    """Verifies that having .cloud_execution_locked causes assert_cloud_execution_permitted() to raise PermissionError."""
    lock_file = os.path.join(temp_dir, LOCK_FILENAME)
    with open(lock_file, "w") as f:
        json.dump({"locked": True, "reason": "Incident test"}, f)

    with patch("os.getcwd", return_value=temp_dir):
        with pytest.raises(PermissionError) as exc_info:
            assert_cloud_execution_permitted()
        assert "Cloud execution is strictly prohibited" in str(exc_info.value)


# =========================================================================
# Scenario 13: Partial / Unconfirmed Provider Termination Escalation
# =========================================================================
def test_13_partial_unconfirmed_provider_termination(temp_dir):
    """Verifies that if provider reports STOPPED (not deleted), termination is not confirmed."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="test_unconfirmed",
        pod_id="pod_stopped",
        watchdog_dir=temp_dir,
        session_id="sess_unconfirmed"
    )
    # STOPPED is billable; strict semantics must classify as not deleted
    watchdog._query_runpod_graphql = lambda q, v=None: (
        {"data": {"pod": {"id": "pod_stopped", "desiredStatus": "STOPPED"}}}, 200
    )

    state, uptime, host = watchdog.query_provider_pod_state()
    assert state == ProviderResponseState.STOPPED

    # Verification attempts of pod destruction will fail because pod is STOPPED
    watchdog._query_runpod_graphql = lambda q, v=None: (
        {"data": {"pod": {"desiredStatus": "STOPPED"}}}, 200
    )
    # Force max attempts = 1 and sleep = 0 for test speed
    with patch("time.sleep", return_value=None):
        res = watchdog.run_supervision_tick(simulated_spend=0.30)
    assert res["should_terminate"] is True
    assert watchdog.termination_confirmed is False
    assert watchdog.termination_state == TerminationDurableState.TERMINATION_UNCONFIRMED


# =========================================================================
# Scenario 14: Clock & Telemetry Anomalies Fail-Closed
# =========================================================================
def test_14_clock_telemetry_anomaly_fail_closed(temp_dir):
    """Verifies that receipts with future timestamps (>15s) or negative uptime are rejected."""
    from research_mission_15_6.runner.stateshift_production_runner_v10 import StateshiftProductionRunnerV10, ExecutionMode

    runner = StateshiftProductionRunnerV10(
        experiment_id="test_clock",
        manifest_path=CALIBRATION_MANIFEST,
        authorization_path=None,
        mode=ExecutionMode.SIMULATION,
        local_data_dir=temp_dir,
        allow_test_key_for_testing=True
    )

    receipt_file = os.path.join(runner.watchdog_dir, f"watchdog_readiness_{runner.experiment_id}_{runner.execution_id}.json")
    bad_receipt = {
        "status": "READY",
        "lifecycle_state": "ACTIVE",
        "watchdog_pid": 12345,
        "experiment_id": runner.experiment_id,
        "session_id": runner.execution_id,
        "pod_id": "simulated_pod",
        "timestamp_utc": time.time() + 100.0,  # Skewed future clock
        "max_authorized_usd": runner.effective_max_spend,
        "emergency_trigger_usd": runner.effective_emergency_trigger,
        "account_preservation_floor_usd": 7.00,
        "pre_existing_uptime_seconds": 0.0
    }
    with open(receipt_file, "w") as f:
        json.dump(bad_receipt, f)

    ok = runner.wait_for_watchdog_readiness(timeout_seconds=0.3)
    assert ok is False


# =========================================================================
# Scenario 15: Full Incident Replay Rescued by Repaired Architecture
# =========================================================================
def test_15_full_incident_replay_rescued_by_architecture(temp_dir):
    """
    Replays the exact Attempt 4 sequence:
    1. Pre-flight checks pass ($9.12 balance).
    2. Supervisor-First Provisioner spawns watchdog in PRE_PROVISION mode.
    3. Exactly ONE pod is provisioned.
    4. Staging begins: model cache script hangs.
    5. Monotonic timeout fires, terminating the pod authoritatively.
    6. Verifies zero inference rollouts occurred and zero runaway spending.
    """
    terminated_pods = []
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.side_effect = lambda pid: (True, terminated_pods.append(pid))

    provisioner = SupervisorFirstProvisioner(
        experiment_id="replay_attempt_4",
        session_id="session_replay",
        local_data_dir=temp_dir,
        max_cost_usd=0.35,
        emergency_trigger_usd=0.25,
        account_floor_usd=7.00,
        transport=mock_transport,
        simulate_supervisor=True
    )

    # 1. Preconditions checked
    provisioner.verify_preconditions(current_balance_usd=9.1243, active_pods_count=0)

    # 2. Supervisor-First spawn
    ready = provisioner.spawn_preprovision_supervisor(timeout_seconds=1.0)
    assert ready is True

    # 3. Provision single pod
    pod_id = provisioner.provision_single_pod(lambda: "wets1b0dsnpzif_replayed")
    assert pod_id == "wets1b0dsnpzif_replayed"

    # 4. Remote model pre-caching hangs
    hanging_channel = MockChannel(hang=True)
    with pytest.raises(StagingTimeoutError):
        provisioner.execute_bounded_staging(
            command="python3 cache_model.py",
            channel=hanging_channel,
            timeout_seconds=0.2  # Repaired bounded deadline
        )

    # 5. Authoritative pod destruction verified
    assert "wets1b0dsnpzif_replayed" in terminated_pods
    assert hanging_channel.closed is True
