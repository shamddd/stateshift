#!/usr/bin/env python3
"""
Unit Tests for Budget-Aware Scheduler & Durable Escalation Manager (Mission 15.3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)
"""

import os
import sys
import json
import time
import shutil
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_3.scheduler.budget_aware_scheduler import BudgetAwareScheduler
from research_mission_15_3.runner.escalation_manager import DurableEscalationManager


def test_scheduler_allows_batch_when_budget_sufficient():
    scheduler = BudgetAwareScheduler(max_authorized_usd=2.00, safety_reserve_usd=0.35)
    can_sched, reason, meta = scheduler.can_schedule_next_batch(
        batch_size=4,
        current_spend_usd=0.50
    )
    assert can_sched is True
    assert reason == "CAN_SCHEDULE"
    assert meta["current_spend_usd"] == 0.50


def test_scheduler_halts_when_batch_exceeds_headroom():
    scheduler = BudgetAwareScheduler(max_authorized_usd=2.00, safety_reserve_usd=0.35)
    # With spend at $1.64, next batch of 8 requests will push projected spend over $1.65 (2.00 - 0.35)
    can_sched, reason, meta = scheduler.can_schedule_next_batch(
        batch_size=8,
        current_spend_usd=1.64
    )
    assert can_sched is False
    assert reason == "PARTIAL_BUDGET_STOP"


def test_scheduler_updates_observed_metrics():
    scheduler = BudgetAwareScheduler(max_authorized_usd=2.00)
    scheduler.update_observed_metrics(latency_seconds=10.0, generated_tokens=500)
    assert scheduler.tokens_per_second == 50.0
    est_sec, est_cost = scheduler.estimate_batch_cost(batch_size=4, concurrency=4)
    assert est_sec > 0
    assert est_cost > 0


def test_escalation_manager_records_and_resolves_alert():
    tmp_dir = tempfile.mkdtemp()
    try:
        json_path = DurableEscalationManager.record_unconfirmed_termination(
            pod_id="test_pod_escalate_1",
            reason="Watchdog limit $2.00 breached",
            attempts=3,
            last_known_status="STOPPED",
            error_message="504 Gateway Timeout from RunPod",
            alert_dir=tmp_dir
        )
        assert os.path.exists(json_path)
        txt_path = os.path.join(tmp_dir, "CRITICAL_ALERT_POD_test_pod_escalate_1.txt")
        assert os.path.exists(txt_path)

        unresolved = DurableEscalationManager.get_unresolved_escalations(tmp_dir)
        assert len(unresolved) == 1
        assert unresolved[0]["pod_id"] == "test_pod_escalate_1"

        # Mark resolved
        DurableEscalationManager.mark_resolved("test_pod_escalate_1", tmp_dir, "Manual termination verified in web UI")
        unresolved_after = DurableEscalationManager.get_unresolved_escalations(tmp_dir)
        assert len(unresolved_after) == 0
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
