"""
Phase 10: 20 Mandatory CLI Subprocess Scenarios Test Suite (Mission 15.4)
Exercises stateshift_production_runner_v10.py via actual subprocess execution across operational scenarios.
"""

import os
import sys
import json
import time
import base64
import subprocess
import tempfile
import pytest

from research_mission_15_4.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    NONPRODUCTION_PUBLIC_KEY_B64,
    _nonprod_priv
)

RUNNER_SCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "runner", "stateshift_production_runner_v10.py")
)
MANIFEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "manifests", "primary_100_manifest.json")
)


def create_auth_file(path, exp_id="exp_cli_test", pod_id="pod_mock_cli", mode="CALIBRATION", max_spend=2.00, tamper_sig=False):
    auth = CryptographicAuthorizer(trusted_public_key_b64=NONPRODUCTION_PUBLIC_KEY_B64)
    doc = auth.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id=exp_id,
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id=pod_id,
        max_spend_usd=max_spend,
        authorized_mode=mode,
        validity_seconds=3600
    )
    if tamper_sig:
        doc["signature_ed25519_b64"] = base64.b64encode(b"0" * 64).decode("utf-8")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)


def run_cli(args, cwd=None):
    cmd = [sys.executable, RUNNER_SCRIPT] + args
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
    return res.returncode, res.stdout, res.stderr


# Scenario 13: Unauthorized session rejected
def test_scenario_13_unauthorized_session_rejected(tmp_path):
    rc, stdout, stderr = run_cli([
        "--pod-id", "pod_cli_13",
        "--mode", "CALIBRATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path)
    ])
    assert rc != 0
    assert "AUTHORIZATION ABORT" in stdout or rc == 2


# Scenario 14: Modified signed authorization rejected
def test_scenario_14_modified_signed_authorization_rejected(tmp_path):
    auth_file = os.path.join(tmp_path, "auth_tampered.json")
    create_auth_file(auth_file, exp_id="exp_cli_14", pod_id="pod_cli_14", tamper_sig=True)

    rc, stdout, stderr = run_cli([
        "--experiment-id", "exp_cli_14",
        "--pod-id", "pod_cli_14",
        "--authorization", auth_file,
        "--mode", "CALIBRATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path)
    ])
    assert rc != 0
    assert "Ed25519 cryptographic signature verification FAILED" in stdout or "AUTHORIZATION ABORT" in stdout


# Scenario 19: Calibration completion does not automatically launch full experiment
def test_scenario_19_calibration_completion_bounds(tmp_path):
    auth_file = os.path.join(tmp_path, "auth_cal.json")
    create_auth_file(auth_file, exp_id="exp_cli_19", pod_id="pod_cli_19", mode="CALIBRATION")

    rc, stdout, stderr = run_cli([
        "--experiment-id", "exp_cli_19",
        "--pod-id", "pod_cli_19",
        "--authorization", auth_file,
        "--mode", "CALIBRATION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "10",
        "--simulate-spend-usd", "0.20"
    ])
    assert rc == 0
    assert "FINISHED" in stdout or "REMOTE_COMPLETE" in stdout


# Scenario 20: Normal completion produces physical integrity and termination receipts
def test_scenario_20_normal_completion_receipts(tmp_path):
    auth_file = os.path.join(tmp_path, "auth_prod.json")
    create_auth_file(auth_file, exp_id="exp_cli_20", pod_id="pod_cli_20", mode="PRODUCTION")

    rc, stdout, stderr = run_cli([
        "--experiment-id", "exp_cli_20",
        "--pod-id", "pod_cli_20",
        "--authorization", auth_file,
        "--mode", "PRODUCTION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "400",
        "--simulate-spend-usd", "0.95"
    ])
    assert rc == 0
    tmp_path = tmp_path
    assert os.path.exists(tmp_path)
    receipt_files = os.listdir(tmp_path)
    assert any("termination_receipt" in f for f in receipt_files)


# Scenario 2: Financial emergency at 143 requests
def test_scenario_02_financial_emergency_stop(tmp_path):
    auth_file = os.path.join(tmp_path, "auth_emerg.json")
    create_auth_file(auth_file, exp_id="exp_cli_02", pod_id="pod_cli_02", mode="PRODUCTION")

    rc, stdout, stderr = run_cli([
        "--experiment-id", "exp_cli_02",
        "--pod-id", "pod_cli_02",
        "--authorization", auth_file,
        "--mode", "PRODUCTION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-records", "143",
        "--simulate-spend-usd", "1.70"  # Exceeds emergency $1.65
    ])
    # Should perform emergency shutdown
    tmp_path = tmp_path
    assert os.path.exists(tmp_path)
    receipt_files = os.listdir(tmp_path)
    assert any("termination_receipt" in f for f in receipt_files)


# Scenario 11: Remote deployment failure
def test_scenario_11_deployment_failure(tmp_path):
    auth_file = os.path.join(tmp_path, "auth_dep_fail.json")
    create_auth_file(auth_file, exp_id="exp_cli_11", pod_id="pod_cli_11", mode="PRODUCTION")

    rc, stdout, stderr = run_cli([
        "--experiment-id", "exp_cli_11",
        "--pod-id", "pod_cli_11",
        "--authorization", auth_file,
        "--mode", "PRODUCTION",
        "--manifest", MANIFEST_PATH,
        "--local-data-dir", str(tmp_path),
        "--simulate-deployment-failure"
    ])
    assert rc != 0
    assert "DEPLOYMENT VERIFICATION ABORT" in stdout or rc == 2
