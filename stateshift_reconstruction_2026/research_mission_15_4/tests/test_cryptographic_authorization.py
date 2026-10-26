"""
Comprehensive Cryptographic Authorization Test Suite (Mission 15.4)
Exercises Ed25519 signature creation, verification, and tamper resistance across 12+ scenarios.
"""

import os
import json
import time
import base64
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from research_mission_15_4.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    NONPRODUCTION_PUBLIC_KEY_B64,
    _nonprod_priv
)


@pytest.fixture
def authorizer(tmp_path):
    registry_path = os.path.join(tmp_path, "nonces.json")
    return CryptographicAuthorizer(
        trusted_public_key_b64=NONPRODUCTION_PUBLIC_KEY_B64,
        nonce_registry_path=registry_path
    )


def test_scenario_1_valid_authorization(authorizer):
    """Scenario 1: Valid signature with authorized parameters passes verification."""
    doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_01",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_1",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY",
        validity_seconds=3600
    )
    ok, msg = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_01",
        active_pod_id="pod_val_1",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert ok
    assert "verified successfully" in msg


def test_scenario_2_missing_signature(authorizer):
    """Scenario 2: Missing signature field is rejected."""
    doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_02",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_2",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY"
    )
    del doc["signature_ed25519_b64"]
    ok, msg = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_02",
        active_pod_id="pod_val_2",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert not ok
    assert "missing required" in msg


def test_scenario_3_invalid_signature_bytes(authorizer):
    """Scenario 3: Corrupted or forged signature bytes fail verification."""
    doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_03",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_3",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY"
    )
    doc["signature_ed25519_b64"] = base64.b64encode(b"0" * 64).decode("utf-8")
    ok, msg = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_03",
        active_pod_id="pod_val_3",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert not ok
    assert "Ed25519 cryptographic signature verification FAILED" in msg


def test_scenario_4_untrusted_public_key(tmp_path):
    """Scenario 4: Valid signature from an untrusted key is rejected."""
    untrusted_priv = ed25519.Ed25519PrivateKey.generate()
    auth_trusted = CryptographicAuthorizer(
        trusted_public_key_b64=NONPRODUCTION_PUBLIC_KEY_B64,
        nonce_registry_path=os.path.join(tmp_path, "nonces.json")
    )
    doc = auth_trusted.create_signed_authorization(
        private_key=untrusted_priv,
        experiment_id="exp_04",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_4",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY"
    )
    ok, msg = auth_trusted.verify_authorization(
        doc,
        active_experiment_id="exp_04",
        active_pod_id="pod_val_4",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert not ok
    assert "Public key mismatch" in msg or "FAILED" in msg


def test_scenario_5_tampered_budget(authorizer):
    """Scenario 5: Modifying budget parameter breaks signature."""
    doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_05",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_5",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY"
    )
    doc["payload"]["max_incremental_spend_usd"] = 2.05
    ok, msg = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_05",
        active_pod_id="pod_val_5",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert not ok
    assert "Ed25519 cryptographic signature verification FAILED" in msg


def test_scenario_6_tampered_pod_id(authorizer):
    """Scenario 6: Modifying pod ID parameter breaks signature."""
    doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_06",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_6",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY"
    )
    doc["payload"]["pod_id"] = "pod_tampered"
    ok, msg = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_06",
        active_pod_id="pod_tampered",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert not ok
    assert "Ed25519 cryptographic signature verification FAILED" in msg


def test_scenario_7_tampered_manifest_hash(authorizer):
    """Scenario 7: Tampering with manifest SHA-256 hash breaks signature."""
    doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_07",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_7",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY"
    )
    doc["payload"]["manifest_sha256"] = "0" * 64
    ok, msg = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_07",
        active_pod_id="pod_val_7",
        active_manifest_sha256="0" * 64,
        active_mode="CALIBRATION_ONLY"
    )
    assert not ok
    assert "Ed25519 cryptographic signature verification FAILED" in msg


def test_scenario_8_tampered_model_revision(authorizer):
    """Scenario 8: Tampering with model revision breaks signature."""
    doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_08",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_8",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY"
    )
    doc["payload"]["model_revision"] = "unpinned_revision"
    ok, msg = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_08",
        active_pod_id="pod_val_8",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY",
        active_model_revision="unpinned_revision"
    )
    assert not ok
    assert "Ed25519 cryptographic signature verification FAILED" in msg


def test_scenario_9_expired_timestamp(authorizer):
    """Scenario 9: Authorization document whose expiration timestamp has passed is rejected."""
    doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_09",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_9",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY",
        validity_seconds=-100.0  # Already expired
    )
    ok, msg = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_09",
        active_pod_id="pod_val_9",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert not ok
    assert "expired" in msg.lower()


def test_scenario_10_future_issued_timestamp(authorizer):
    """Scenario 10: Authorization with issued timestamp far in future is rejected."""
    # Create valid payload manually with future timestamps
    future_payload = {
        "schema_version": "1.0",
        "experiment_id": "exp_10",
        "manifest_sha256": "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
        "model_revision": "c869d27376a8d6728795551322fe323b6",
        "pod_id": "pod_val_10",
        "max_incremental_spend_usd": 2.00,
        "minimum_account_balance_usd": 7.00,
        "maximum_runtime_minutes": 160,
        "authorized_mode": "CALIBRATION_ONLY",
        "issued_at_utc": time.time() + 36000.0,
        "expires_at_utc": time.time() + 40000.0,
        "session_nonce": "nonce_future_test_1234"
    }
    canonical_bytes = authorizer.canonical_bytes(future_payload)
    sig_b64 = base64.b64encode(_nonprod_priv.sign(canonical_bytes)).decode("utf-8")
    doc = {
        "payload": future_payload,
        "signature_ed25519_b64": sig_b64,
        "public_key_ed25519_b64": NONPRODUCTION_PUBLIC_KEY_B64
    }
    
    ok, msg = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_10",
        active_pod_id="pod_val_10",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert not ok
    assert "is in the future" in msg


def test_scenario_11_reused_nonce_replay_attack(authorizer):
    """Scenario 11: Reusing the same session nonce is rejected as a replay attack."""
    doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_11",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_11",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY",
        validity_seconds=3600
    )
    # First use succeeds
    ok1, msg1 = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_11",
        active_pod_id="pod_val_11",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert ok1
    assert "verified successfully" in msg1

    # Second use of same nonce is rejected
    ok2, msg2 = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_11",
        active_pod_id="pod_val_11",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert not ok2
    assert "Replay detected" in msg2


def test_scenario_12_wrong_execution_mode(authorizer):
    """Scenario 12: Authorization granted for CALIBRATION_ONLY is rejected if runner requests PRODUCTION."""
    doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_12",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_val_12",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY",
        validity_seconds=3600
    )
    ok, msg = authorizer.verify_authorization(
        doc,
        active_experiment_id="exp_12",
        active_pod_id="pod_val_12",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="PRODUCTION"  # Active runner mode mismatch
    )
    assert not ok
    assert "Execution mode mismatch" in msg
