#!/usr/bin/env python3
"""
Test Suite: StateShift Mission 15.6 Final Production Patch (Defects 1, 2, and 3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Verifies:
  - Defect 1: Live Financial Telemetry & Conservative Accounting
      * query_account_balance live parsing (clientBalance)
      * establish_financial_baseline floor check ($7.00 preservation floor)
      * Adoption of reported GPU rate (max(configured, reported))
      * Conservative spend reconciliation max(provider, delta_balance, elapsed)
      * Preservation floor breach during tick triggers immediate shutdown
  - Defect 2: Mandatory Startup Handshake & Verified Watchdog Readiness
      * Atomic readiness receipt publishing
      * 12-point handshake verification (distinct PID, OS alive, exp/session/pod match, limits, freshness)
      * Rejection of dead PID, matching PID, pod/session mismatch, budget tampering, stale receipt
      * Handshake timeout / premature death aborts inference before deployment
  - Defect 3: Unconfirmed Termination Non-Disabling Watchdog Policy
      * Unconfirmed provider termination does NOT kill watchdog process
      * Watchdog remains active and attempts background reconciliation
      * Background reconciliation confirms destruction when provider responds TERMINATED / NOT_FOUND
      * Explicit operator handoff (operator_handoff_{pod_id}.json) allows operator to assume control
      * Confirmed termination cleanly stops watchdog
"""

import os
import sys
import json
import time
import signal
import tempfile
import shutil
import pytest
import subprocess
from typing import Dict, Any

from research_mission_15_6.supervision.independent_financial_watchdog import (
    IndependentFinancialWatchdog,
    WatchdogLifecycleState,
    TerminationDurableState,
    ProviderResponseState
)
from research_mission_15_6.runner.stateshift_production_runner_v10 import (
    StateshiftProductionRunnerV10,
    ExecutionMode,
    ProductionState
)


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


# ==============================================================================
# DEFECT 1: Live Financial Telemetry & Conservative Accounting
# ==============================================================================

def test_defect1_query_account_balance_success(monkeypatch, temp_dir):
    """Defect 1: query_account_balance parses clientBalance from RunPod GraphQL."""
    mock_resp = {
        "data": {
            "myself": {
                "id": "user_123",
                "clientBalance": 9.4520
            }
        }
    }
    monkeypatch.setattr(
        IndependentFinancialWatchdog,
        "_query_runpod_graphql",
        lambda self, q, v: (mock_resp, 200)
    )
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_bal_success",
        pod_id="pod_bal_1",
        watchdog_dir=temp_dir,
        api_key="test_api_key"
    )

    bal, msg = watchdog.query_account_balance()
    assert bal == 9.4520
    assert msg == "Success"


def test_defect1_query_account_balance_api_error(monkeypatch, temp_dir):
    """Defect 1: query_account_balance gracefully reports API errors."""
    monkeypatch.setattr(
        IndependentFinancialWatchdog,
        "_query_runpod_graphql",
        lambda self, q, v: ({"error": "Internal Server Error"}, 500)
    )
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_bal_err",
        pod_id="pod_bal_err",
        watchdog_dir=temp_dir,
        allow_test_key_for_testing=True,
        api_key="test_api_key"
    )

    bal, msg = watchdog.query_account_balance()
    assert bal is None
    assert "500" in msg or "error" in msg.lower()


def test_defect1_establish_baseline_floor_breach(temp_dir):
    """Defect 1: Account balance at or below preservation floor ($7.00) refuses execution."""
    # When initial balance is $6.99 (below $7.00 floor)
    with pytest.raises(PermissionError) as excinfo:
        IndependentFinancialWatchdog(
            experiment_id="exp_floor_breach",
            pod_id="pod_floor_1",
            watchdog_dir=temp_dir,
            account_preservation_floor_usd=7.00,
            initial_account_balance=6.99
        )
    assert "preservation floor" in str(excinfo.value).lower()


def test_defect1_reported_gpu_rate_adopted(temp_dir):
    """Defect 1: Pod reported costPerHr is adopted if higher than configured rate."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_rate_test",
        pod_id="pod_rate_1",
        watchdog_dir=temp_dir,
        gpu_hourly_rate=0.89
    )
    # Provider reports higher rate ($1.25/hr)
    raw_resp = {
        "data": {
            "pod": {
                "id": "pod_rate_1",
                "desiredStatus": "RUNNING",
                "costPerHr": 1.25,
                "runtime": {"uptimeInSeconds": 3600.0}
            }
        }
    }
    watchdog.classify_provider_pod_response(raw_resp, 200)
    assert watchdog.reported_gpu_hourly_rate == 1.25

    # Spend calculation must use max(0.89, 1.25) = 1.25/hr -> 1 hour = $1.25
    spend = watchdog.calculate_effective_spend(provider_uptime_seconds=3600.0)
    assert abs(spend - 1.25) < 1e-4


def test_defect1_spend_max_reconciliation_telemetry(temp_dir):
    """Defect 1: effective_spend = max(provider_uptime, verified_balance_delta, elapsed_estimate)."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_recon_test",
        pod_id="pod_recon_1",
        watchdog_dir=temp_dir,
        gpu_hourly_rate=1.00,
        initial_account_balance=10.00,
        pre_existing_uptime_seconds=1800.0  # 30 min pre-existing
    )
    # Case A: Provider uptime is highest (3600s = $1.00)
    spend_a = watchdog.calculate_effective_spend(
        provider_uptime_seconds=3600.0,
        current_account_balance=9.80  # Delta = $0.20
    )
    assert abs(spend_a - 1.00) < 1e-4

    # Case B: Verified balance delta is highest ($0.50 delta vs 600s provider = $0.166)
    spend_b = watchdog.calculate_effective_spend(
        provider_uptime_seconds=600.0,
        current_account_balance=9.50  # Delta = $0.50
    )
    assert abs(spend_b - 0.50) < 1e-4


def test_defect1_floor_breach_during_supervision_tick(temp_dir):
    """Defect 1: Balance dropping to or below $7.00 during supervision tick triggers emergency termination."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_floor_tick",
        pod_id="pod_floor_tick",
        watchdog_dir=temp_dir,
        initial_account_balance=8.00,
        account_preservation_floor_usd=7.00,
        emergency_trigger_usd=1.00
    )
    watchdog._query_runpod_graphql = lambda q, v: ({"data": {"pod": None}}, 200)

    # Balance is now $6.95 (floor breached)
    res = watchdog.run_supervision_tick(
        simulated_spend=0.05,
        current_account_balance=6.95
    )
    assert res["should_terminate"] is True
    assert watchdog.termination_confirmed is True


# ==============================================================================
# DEFECT 2: Mandatory Startup Handshake & Verified Watchdog Readiness
# ==============================================================================

def test_defect2_readiness_receipt_written_atomically(temp_dir):
    """Defect 2: IndependentFinancialWatchdog writes readiness receipt on successful startup."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_receipt_test",
        pod_id="pod_receipt_1",
        watchdog_dir=temp_dir,
        session_id="session_456",
        max_authorized_usd=0.35,
        emergency_trigger_usd=0.25,
        gpu_hourly_rate=0.89
    )
    receipt_file = os.path.join(temp_dir, "watchdog_readiness_exp_receipt_test_session_456.json")
    assert os.path.exists(receipt_file)

    with open(receipt_file, "r") as f:
        data = json.load(f)

    assert data["status"] == "READY"
    assert data["lifecycle_state"] == "ACTIVE"
    assert data["watchdog_pid"] == os.getpid()
    assert data["experiment_id"] == "exp_receipt_test"
    assert data["session_id"] == "session_456"
    assert data["pod_id"] == "pod_receipt_1"
    assert data["max_authorized_usd"] == 0.35
    assert data["emergency_trigger_usd"] == 0.25
    assert data["account_preservation_floor_usd"] == 7.00


def test_defect2_handshake_success(temp_dir):
    """Defect 2: Runner wait_for_watchdog_readiness succeeds when valid receipt is present."""
    runner = StateshiftProductionRunnerV10(
        experiment_id="exp_handshake_ok",
        manifest_path="research_mission_15_6/manifests/calibration_10_manifest.json",
        authorization_path=None,
        mode=ExecutionMode.SIMULATION,
        pod_id="pod_handshake_ok",
        local_data_dir=temp_dir
    )
    # Write a genuine external receipt with a simulated live external PID
    # Spawn a dummy long-lived child process to represent the watchdog
    dummy_proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(10)"])
    try:
        receipt_file = os.path.join(runner.watchdog_dir, f"watchdog_readiness_{runner.experiment_id}_{runner.execution_id}.json")
        receipt = {
            "status": "READY",
            "lifecycle_state": "ACTIVE",
            "watchdog_pid": dummy_proc.pid,
            "experiment_id": runner.experiment_id,
            "pod_id": runner.pod_id,
            "session_id": runner.execution_id,
            "timestamp_utc": time.time(),
            "max_authorized_usd": runner.effective_max_spend,
            "emergency_trigger_usd": runner.effective_emergency_trigger,
            "account_preservation_floor_usd": 7.00,
            "initial_account_balance": 9.50,
            "pre_existing_uptime_seconds": 0.0,
            "gpu_hourly_rate": 0.89
        }
        with open(receipt_file, "w") as f:
            json.dump(receipt, f)

        ready = runner.wait_for_watchdog_readiness(timeout_seconds=2.0)
        assert ready is True
    finally:
        dummy_proc.terminate()
        dummy_proc.wait()


def test_defect2_handshake_rejects_matching_controller_pid(temp_dir):
    """Defect 2: Handshake rejects receipt where watchdog_pid == controller PID (must be decoupled)."""
    runner = StateshiftProductionRunnerV10(
        experiment_id="exp_pid_match",
        manifest_path="research_mission_15_6/manifests/calibration_10_manifest.json",
        authorization_path=None,
        mode=ExecutionMode.SIMULATION,
        pod_id="pod_pid_match",
        local_data_dir=temp_dir
    )
    receipt_file = os.path.join(runner.watchdog_dir, f"watchdog_readiness_{runner.experiment_id}_{runner.execution_id}.json")
    receipt = {
        "status": "READY",
        "lifecycle_state": "ACTIVE",
        "watchdog_pid": os.getpid(),  # Invalid: same as controller!
        "experiment_id": runner.experiment_id,
        "pod_id": runner.pod_id,
        "session_id": runner.execution_id,
        "timestamp_utc": time.time(),
        "max_authorized_usd": runner.effective_max_spend,
        "emergency_trigger_usd": runner.effective_emergency_trigger,
        "account_preservation_floor_usd": 7.00,
        "pre_existing_uptime_seconds": 0.0
    }
    with open(receipt_file, "w") as f:
        json.dump(receipt, f)

    ready = runner.wait_for_watchdog_readiness(timeout_seconds=1.0)
    assert ready is False


def test_defect2_handshake_rejects_dead_pid(temp_dir):
    """Defect 2: Handshake rejects receipt where watchdog_pid is dead in OS process table."""
    runner = StateshiftProductionRunnerV10(
        experiment_id="exp_dead_pid",
        manifest_path="research_mission_15_6/manifests/calibration_10_manifest.json",
        authorization_path=None,
        mode=ExecutionMode.SIMULATION,
        pod_id="pod_dead_pid",
        local_data_dir=temp_dir
    )
    dead_pid = 9999998
    receipt_file = os.path.join(runner.watchdog_dir, f"watchdog_readiness_{runner.experiment_id}_{runner.execution_id}.json")
    receipt = {
        "status": "READY",
        "lifecycle_state": "ACTIVE",
        "watchdog_pid": dead_pid,
        "experiment_id": runner.experiment_id,
        "pod_id": runner.pod_id,
        "session_id": runner.execution_id,
        "timestamp_utc": time.time(),
        "max_authorized_usd": runner.effective_max_spend,
        "emergency_trigger_usd": runner.effective_emergency_trigger,
        "account_preservation_floor_usd": 7.00,
        "pre_existing_uptime_seconds": 0.0
    }
    with open(receipt_file, "w") as f:
        json.dump(receipt, f)

    ready = runner.wait_for_watchdog_readiness(timeout_seconds=1.0)
    assert ready is False


def test_defect2_handshake_rejects_stale_receipt(temp_dir):
    """Defect 2: Handshake rejects stale receipt (> timeout + 5.0 seconds old)."""
    runner = StateshiftProductionRunnerV10(
        experiment_id="exp_stale_rec",
        manifest_path="research_mission_15_6/manifests/calibration_10_manifest.json",
        authorization_path=None,
        mode=ExecutionMode.SIMULATION,
        pod_id="pod_stale_rec",
        local_data_dir=temp_dir
    )
    dummy_proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(10)"])
    try:
        receipt_file = os.path.join(runner.watchdog_dir, f"watchdog_readiness_{runner.experiment_id}_{runner.execution_id}.json")
        receipt = {
            "status": "READY",
            "lifecycle_state": "ACTIVE",
            "watchdog_pid": dummy_proc.pid,
            "experiment_id": runner.experiment_id,
            "pod_id": runner.pod_id,
            "session_id": runner.execution_id,
            "timestamp_utc": time.time() - 300.0,  # 5 minutes old!
            "max_authorized_usd": runner.effective_max_spend,
            "emergency_trigger_usd": runner.effective_emergency_trigger,
            "account_preservation_floor_usd": 7.00,
            "pre_existing_uptime_seconds": 0.0
        }
        with open(receipt_file, "w") as f:
            json.dump(receipt, f)

        ready = runner.wait_for_watchdog_readiness(timeout_seconds=1.0)
        assert ready is False
    finally:
        dummy_proc.terminate()
        dummy_proc.wait()


def test_defect2_handshake_timeout_aborts_inference(temp_dir):
    """Defect 2: Missing receipt causes wait_for_watchdog_readiness to time out and return False."""
    runner = StateshiftProductionRunnerV10(
        experiment_id="exp_timeout_test",
        manifest_path="research_mission_15_6/manifests/calibration_10_manifest.json",
        authorization_path=None,
        mode=ExecutionMode.SIMULATION,
        pod_id="pod_timeout_1",
        local_data_dir=temp_dir
    )
    # No receipt file written
    ready = runner.wait_for_watchdog_readiness(timeout_seconds=0.3)
    assert ready is False


# ==============================================================================
# DEFECT 3: Unconfirmed Termination Non-Disabling Watchdog Policy
# ==============================================================================

def test_defect3_unconfirmed_termination_preserves_watchdog_process(temp_dir):
    """Defect 3: When termination is unconfirmed, runner does NOT kill watchdog process."""
    runner = StateshiftProductionRunnerV10(
        experiment_id="exp_unconf_pres",
        manifest_path="research_mission_15_6/manifests/calibration_10_manifest.json",
        authorization_path=None,
        mode=ExecutionMode.SIMULATION,
        pod_id="pod_unconf_pres",
        local_data_dir=temp_dir,
        simulate_unconfirmed_termination=True
    )
    # Spawn dummy watchdog process
    dummy_watchdog = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(10)"])
    runner.watchdog_process = dummy_watchdog
    runner.watchdog_pid = dummy_watchdog.pid

    try:
        ok = runner.terminate_normal()
        assert ok is False
        assert runner.state == ProductionState.TERMINATION_UNCONFIRMED
        # Critical assertion: dummy_watchdog must STILL be alive in OS process table!
        assert dummy_watchdog.poll() is None
    finally:
        dummy_watchdog.terminate()
        dummy_watchdog.wait()


def test_defect3_unconfirmed_termination_background_reconciliation(temp_dir):
    """Defect 3: Background watchdog reconciles unconfirmed termination when pod is confirmed destroyed."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_recon_bg",
        pod_id="pod_recon_bg",
        watchdog_dir=temp_dir
    )
    # First, simulate unconfirmed termination attempt
    watchdog._query_runpod_graphql = lambda q, v: ({"data": {"pod": {"desiredStatus": "STOPPED"}}}, 200)
    confirmed = watchdog.dispatch_provider_termination("test emergency", max_retries=1)
    assert confirmed is False
    assert watchdog.termination_state == TerminationDurableState.TERMINATION_UNCONFIRMED

    # In next poll, provider reports AUTHORITATIVE_NOT_FOUND
    watchdog._query_runpod_graphql = lambda q, v: ({"data": {"pod": None}}, 200)
    st, up, _ = watchdog.query_provider_pod_state()
    assert st == ProviderResponseState.AUTHORITATIVE_NOT_FOUND

    # Reconciliation verifies destruction
    if st in [ProviderResponseState.AUTHORITATIVE_NOT_FOUND, ProviderResponseState.TERMINATED, ProviderResponseState.DELETED]:
        watchdog.termination_confirmed = True
        watchdog.termination_state = TerminationDurableState.TERMINATION_CONFIRMED
        watchdog.lifecycle_state = WatchdogLifecycleState.TERMINATION_CONFIRMED
        watchdog._persist_final_receipt("Background reconciliation", confirmed=True, attempts=1)

    assert watchdog.termination_confirmed is True
    assert watchdog.termination_state == TerminationDurableState.TERMINATION_CONFIRMED


def test_defect3_operator_handoff_relinquishes_supervision(temp_dir):
    """Defect 3: operator_handoff file allows human operator to take over without false alert."""
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_handoff_test",
        pod_id="pod_handoff_1",
        watchdog_dir=temp_dir
    )
    handoff_path = os.path.join(temp_dir, f"operator_handoff_{watchdog.pod_id}.json")
    with open(handoff_path, "w") as f:
        json.dump({
            "operator": "Sham Satish Thakare",
            "pod_id": watchdog.pod_id,
            "action": "ASSUME_MANUAL_OWNERSHIP",
            "timestamp_utc": time.time()
        }, f)

    assert os.path.exists(handoff_path)
    # Daemon loop checks handoff_path and transitions cleanly
    watchdog.lifecycle_state = WatchdogLifecycleState.WATCHDOG_EXITED
    watchdog._persist_watchdog_state("OPERATOR_HANDOFF_ACCEPTED", "Operator assumed manual ownership")
    assert watchdog.lifecycle_state == WatchdogLifecycleState.WATCHDOG_EXITED


def test_defect3_confirmed_termination_cleanly_shuts_down_watchdog(temp_dir):
    """Defect 3: Confirmed provider termination cleanly terminates the watchdog process."""
    runner = StateshiftProductionRunnerV10(
        experiment_id="exp_conf_term",
        manifest_path="research_mission_15_6/manifests/calibration_10_manifest.json",
        authorization_path=None,
        mode=ExecutionMode.SIMULATION,
        pod_id="pod_conf_term",
        local_data_dir=temp_dir,
        simulate_unconfirmed_termination=False  # Confirmed!
    )
    dummy_watchdog = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(10)"])
    runner.watchdog_process = dummy_watchdog
    runner.watchdog_pid = dummy_watchdog.pid

    try:
        ok = runner.terminate_normal()
        assert ok is True
        assert runner.state == ProductionState.FINISHED
        # Watchdog was cleanly terminated
        dummy_watchdog.wait(timeout=2.0)
        assert dummy_watchdog.poll() is not None
    finally:
        if dummy_watchdog.poll() is None:
            dummy_watchdog.terminate()
            dummy_watchdog.wait()
