#!/usr/bin/env python3
"""
Unit tests for Fail-Closed GPU Authorization Gate (Mission 22)
Author: Sham Satish Thakare (github.com/shamddd)
"""

import sys
import os
import json
import time
import pytest
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUNNER_SCRIPT = os.path.join(REPO_ROOT, "research_mission_22", "scripts", "run_confirmatory_trial.py")
LOCK_FILE = os.path.join(REPO_ROOT, ".cloud_execution_locked")

def test_lock_file_present_on_disk():
    # Invariant: Lock file must be present
    assert os.path.exists(LOCK_FILE), f"Critical safety violation: {LOCK_FILE} is missing!"

def test_runner_fails_closed_when_cloud_requested():
    # Calling runner without --dry-run must exit with code 101 due to lock file
    res = subprocess.run(
        [sys.executable, RUNNER_SCRIPT],
        capture_output=True,
        text=True
    )
    assert res.returncode == 101
    assert "Cloud execution lock active" in res.stdout

def test_runner_dry_run_succeeds_with_zero_cloud_calls():
    # Calling runner with --dry-run must succeed (exit 0) on CPU
    res = subprocess.run(
        [sys.executable, RUNNER_SCRIPT, "--dry-run"],
        capture_output=True,
        text=True
    )
    assert res.returncode == 0
    assert "DRY-RUN STATUS: FULL PREFLIGHT SUCCESS" in res.stdout

def test_authorization_token_validation_logic():
    sys.path.insert(0, os.path.join(REPO_ROOT, "research_mission_22", "scripts"))
    from run_confirmatory_trial import verify_session_authorization
    
    # Test missing file -> exit 102
    with pytest.raises(SystemExit) as exc:
        verify_session_authorization("/nonexistent/token.json", max_spend_cap=1.60)
    assert exc.value.code == 102

    # Test cap exceeded -> exit 103
    temp_auth = "/tmp/test_auth_high_cap.json"
    with open(temp_auth, "w") as f:
        json.dump({"authorized_spend_cap_usd": 50.0, "expires_at_epoch": time.time() + 3600}, f)
    with pytest.raises(SystemExit) as exc:
        verify_session_authorization(temp_auth, max_spend_cap=1.60)
    assert exc.value.code == 103

    # Test expired token -> exit 104
    temp_auth_exp = "/tmp/test_auth_exp.json"
    with open(temp_auth_exp, "w") as f:
        json.dump({"authorized_spend_cap_usd": 1.0, "expires_at_epoch": time.time() - 3600}, f)
    with pytest.raises(SystemExit) as exc:
        verify_session_authorization(temp_auth_exp, max_spend_cap=1.60)
    assert exc.value.code == 104

    # Cleanup temp
    if os.path.exists(temp_auth):
        os.remove(temp_auth)
    if os.path.exists(temp_auth_exp):
        os.remove(temp_auth_exp)
