#!/usr/bin/env python3
"""
Unit Tests for Session-Specific Authorization Validator (Mission 15.3)
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

from research_mission_15_3.auth.session_authorizer import (
    SessionAuthorizer, FROZEN_MANIFEST_SHA256, APPROVED_MODEL_ID, APPROVED_MODEL_REVISION
)


@pytest.fixture
def auth_env():
    tmp_dir = tempfile.mkdtemp()
    
    def make_auth(
        status="APPROVED",
        exp_id="stateshift_400_replication_2026",
        pod_id="pod_123",
        manifest_hash=FROZEN_MANIFEST_SHA256,
        model_id=APPROVED_MODEL_ID,
        model_rev=APPROVED_MODEL_REVISION,
        max_usd=2.00,
        floor_usd=7.00,
        modes=None,
        ttl_seconds=3600.0,
        pi="Sham Satish Thakare"
    ):
        if modes is None:
            modes = ["PRODUCTION", "PREFLIGHT", "DRY_RUN"]
        doc = {
            "approval_status": status,
            "experiment_id": exp_id,
            "principal_investigator": pi,
            "created_at_utc": time.time(),
            "expires_at_utc": time.time() + ttl_seconds,
            "authorized_execution_modes": modes,
            "manifest_sha256": manifest_hash,
            "model_id": model_id,
            "model_revision": model_rev,
            "pod_id": pod_id,
            "max_authorized_incremental_usd": max_usd,
            "min_account_balance_floor_usd": floor_usd
        }
        path = os.path.join(tmp_dir, "auth_doc.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2)
        return path

    yield {
        "dir": tmp_dir,
        "make_auth": make_auth
    }
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_valid_authorization_passes(auth_env):
    path = auth_env["make_auth"]()
    valid, data, reason = SessionAuthorizer.validate_authorization(
        path,
        current_experiment_id="stateshift_400_replication_2026",
        current_pod_id="pod_123",
        current_manifest_sha256=FROZEN_MANIFEST_SHA256,
        current_mode="PRODUCTION"
    )
    assert valid is True
    assert reason == "Authorization validated successfully."


def test_unsigned_template_rejected(auth_env):
    path = auth_env["make_auth"](status="UNSIGNED_TEMPLATE_NOT_VALID_FOR_EXECUTION")
    valid, _, reason = SessionAuthorizer.validate_authorization(
        path, "stateshift_400_replication_2026", "pod_123", FROZEN_MANIFEST_SHA256, "PRODUCTION"
    )
    assert valid is False
    assert "not 'APPROVED'" in reason


def test_expired_authorization_rejected(auth_env):
    path = auth_env["make_auth"](ttl_seconds=-10.0)
    valid, _, reason = SessionAuthorizer.validate_authorization(
        path, "stateshift_400_replication_2026", "pod_123", FROZEN_MANIFEST_SHA256, "PRODUCTION"
    )
    assert valid is False
    assert "Authorization expired" in reason


def test_pod_id_mismatch_rejected(auth_env):
    path = auth_env["make_auth"](pod_id="pod_authorized_abc")
    valid, _, reason = SessionAuthorizer.validate_authorization(
        path, "stateshift_400_replication_2026", "pod_different_xyz", FROZEN_MANIFEST_SHA256, "PRODUCTION"
    )
    assert valid is False
    assert "Pod ID mismatch" in reason


def test_manifest_hash_mismatch_rejected(auth_env):
    path = auth_env["make_auth"](manifest_hash="bad_hash_1234567890abcdef")
    valid, _, reason = SessionAuthorizer.validate_authorization(
        path, "stateshift_400_replication_2026", "pod_123", FROZEN_MANIFEST_SHA256, "PRODUCTION"
    )
    assert valid is False
    assert "does not match frozen manifest constant" in reason


def test_higher_budget_rejected(auth_env):
    path = auth_env["make_auth"](max_usd=2.50) # Exceeds 2.00 limit
    valid, _, reason = SessionAuthorizer.validate_authorization(
        path, "stateshift_400_replication_2026", "pod_123", FROZEN_MANIFEST_SHA256, "PRODUCTION", max_cost_limit=2.00
    )
    assert valid is False
    assert "exceeds runner limit" in reason


def test_preservation_floor_below_seven_rejected(auth_env):
    path = auth_env["make_auth"](floor_usd=6.50)
    valid, _, reason = SessionAuthorizer.validate_authorization(
        path, "stateshift_400_replication_2026", "pod_123", FROZEN_MANIFEST_SHA256, "PRODUCTION"
    )
    assert valid is False
    assert "mandatory floor" in reason


def test_model_revision_mismatch_rejected(auth_env):
    path = auth_env["make_auth"](model_rev="unauthorized_rev_hash")
    valid, _, reason = SessionAuthorizer.validate_authorization(
        path, "stateshift_400_replication_2026", "pod_123", FROZEN_MANIFEST_SHA256, "PRODUCTION"
    )
    assert valid is False
    assert "Model revision mismatch" in reason


def test_mode_not_authorized_rejected(auth_env):
    path = auth_env["make_auth"](modes=["DRY_RUN"])
    valid, _, reason = SessionAuthorizer.validate_authorization(
        path, "stateshift_400_replication_2026", "pod_123", FROZEN_MANIFEST_SHA256, "PRODUCTION"
    )
    assert valid is False
    assert "is not in authorized modes" in reason
