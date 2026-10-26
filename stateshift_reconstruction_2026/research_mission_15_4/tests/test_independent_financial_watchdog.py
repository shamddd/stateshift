"""
Independent Financial Watchdog Process Test Suite (Mission 15.4)
Exercises monotonic runtime tracking, warning/emergency threshold triggers,
stale controller heartbeat detection, and direct provider termination dispatch.
"""

import os
import json
import time
import tempfile
import pytest

from research_mission_15_4.supervision.independent_financial_watchdog import IndependentFinancialWatchdog


@pytest.fixture
def watchdog_setup(tmp_path):
    watchdog_dir = os.path.join(tmp_path, "watchdog")
    ctrl_hb = os.path.join(tmp_path, "controller_hb.json")
    with open(ctrl_hb, "w") as f:
        json.dump({"timestamp_utc": time.time(), "status": "ALIVE"}, f)

    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_watch_01",
        pod_id="pod_test_123",
        watchdog_dir=watchdog_dir,
        max_authorized_usd=2.00,
        emergency_trigger_usd=1.65,
        account_preservation_floor_usd=7.00,
        gpu_hourly_rate=0.89,
        max_runtime_minutes=160.0,
        poll_interval_seconds=1.0,
        main_controller_heartbeat_path=ctrl_hb
    )
    return watchdog, watchdog_dir, ctrl_hb


def test_watchdog_normal_operation(watchdog_setup):
    """Test watchdog normal evaluation tick under budget."""
    watchdog, watchdog_dir, _ = watchdog_setup
    res = watchdog.run_supervision_tick(simulated_spend=0.50)
    assert not res["should_terminate"]
    assert res["action"] == "CONTINUE"
    assert not res["termination_dispatched"]

    # Check heartbeat file was written
    assert os.path.exists(watchdog.watchdog_heartbeat_file)
    with open(watchdog.watchdog_heartbeat_file) as f:
        data = json.load(f)
    assert data["effective_spend_usd"] == 0.50


def test_watchdog_emergency_spend_trigger(watchdog_setup):
    """Test watchdog triggers emergency termination when spend >= $1.65."""
    watchdog, _, _ = watchdog_setup
    # Mock dispatch termination to avoid real network call
    terminated_calls = []
    watchdog.dispatch_provider_termination = lambda reason: (terminated_calls.append(reason) or True)

    res = watchdog.run_supervision_tick(simulated_spend=1.66)
    assert res["should_terminate"]
    assert len(terminated_calls) == 1
    assert "emergency threshold" in terminated_calls[0]


def test_watchdog_max_runtime_trigger(watchdog_setup):
    """Test watchdog triggers emergency termination when runtime >= 160 minutes."""
    watchdog, _, _ = watchdog_setup
    terminated_calls = []
    watchdog.dispatch_provider_termination = lambda reason: (terminated_calls.append(reason) or True)

    # Artificially age monotonic start time by 165 minutes (9900 seconds)
    watchdog.start_monotonic -= 9900.0

    res = watchdog.run_supervision_tick()
    assert res["should_terminate"]
    assert len(terminated_calls) == 1
    assert "max allowed" in terminated_calls[0]


def test_watchdog_stale_controller_heartbeat(watchdog_setup):
    """Test watchdog triggers termination when main controller stops updating heartbeat (> 120s)."""
    watchdog, _, ctrl_hb = watchdog_setup
    terminated_calls = []
    watchdog.dispatch_provider_termination = lambda reason: (terminated_calls.append(reason) or True)

    # Write stale heartbeat timestamp (150 seconds ago)
    with open(ctrl_hb, "w") as f:
        json.dump({"timestamp_utc": time.time() - 150.0, "status": "FROZEN"}, f)

    res = watchdog.run_supervision_tick(simulated_spend=0.20)
    assert res["should_terminate"]
    assert len(terminated_calls) == 1
    assert "heartbeat stale" in terminated_calls[0]
