#!/usr/bin/env python3
"""
StateShift Ed25519 Cryptographic Session Authorization (Mission 15.4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Provides genuine Ed25519 asymmetric cryptographic signing and verification:
- Canonical JSON serialization of authorization payload
- Non-reusable session nonce replay protection
- Verification before any cloud mutation
"""

import os
import sys
import json
import time
import base64
from typing import Dict, Any, Tuple, Optional, Set
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

FROZEN_MANIFEST_SHA256 = "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"
PINNED_MODEL_ID = "Qwen/Qwen2.5-Math-7B-Instruct"
PINNED_MODEL_REVISION = "c869d27376a8d6728795551322fe323b6"

# Authoritative trusted public key for non-production tests and verification
# (Production keys are held offline by PI Sham Satish Thakare)
NONPRODUCTION_TEST_SEED = b"stateshift_pi_test_key_seed_32b_"
_nonprod_priv = ed25519.Ed25519PrivateKey.from_private_bytes(NONPRODUCTION_TEST_SEED)
NONPRODUCTION_PUBLIC_KEY_B64 = base64.b64encode(_nonprod_priv.public_key().public_bytes_raw()).decode("utf-8")


class CryptographicAuthorizer:
    REQUIRED_PAYLOAD_FIELDS = [
        "schema_version",
        "experiment_id",
        "manifest_sha256",
        "model_id",
        "model_revision",
        "pod_id",
        "max_incremental_spend_usd",
        "minimum_account_balance_usd",
        "maximum_runtime_minutes",
        "authorized_mode",
        "issued_at_utc",
        "expires_at_utc",
        "session_nonce"
    ]

    def __init__(self, trusted_public_key_b64: str = NONPRODUCTION_PUBLIC_KEY_B64, nonce_registry_path: Optional[str] = None):
        self.trusted_public_key_b64 = trusted_public_key_b64
        self.trusted_public_key = ed25519.Ed25519PublicKey.from_public_bytes(
            base64.b64decode(trusted_public_key_b64)
        )
        self.nonce_registry_path = nonce_registry_path
        self.seen_nonces: Set[str] = set()
        self._load_nonces()

    def _load_nonces(self):
        if self.nonce_registry_path and os.path.exists(self.nonce_registry_path):
            try:
                with open(self.nonce_registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.seen_nonces = set(data.get("seen_nonces", []))
            except Exception:
                self.seen_nonces = set()

    def _save_nonce(self, nonce: str):
        self.seen_nonces.add(nonce)
        if self.nonce_registry_path:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(self.nonce_registry_path)), exist_ok=True)
                tmp = self.nonce_registry_path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump({"seen_nonces": list(self.seen_nonces)}, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, self.nonce_registry_path)
            except Exception:
                pass

    @staticmethod
    def canonical_bytes(payload: Dict[str, Any]) -> bytes:
        """Deterministically serializes payload keys in sorted order without whitespace."""
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @classmethod
    def create_signed_authorization(
        cls,
        private_key: ed25519.Ed25519PrivateKey,
        experiment_id: str,
        manifest_sha256: str,
        model_id: str,
        model_revision: str,
        pod_id: str,
        max_spend_usd: float = 2.0,
        min_balance_usd: float = 7.0,
        max_runtime_minutes: int = 160,
        authorized_mode: str = "PRODUCTION",
        validity_seconds: float = 3600.0,
        session_nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates canonically signed authorization document."""
        now = time.time()
        nonce = session_nonce or base64.b64encode(os.urandom(16)).decode("utf-8")
        payload = {
            "schema_version": "1",
            "experiment_id": experiment_id,
            "manifest_sha256": manifest_sha256,
            "model_id": model_id,
            "model_revision": model_revision,
            "pod_id": pod_id,
            "max_incremental_spend_usd": float(max_spend_usd),
            "minimum_account_balance_usd": float(min_balance_usd),
            "maximum_runtime_minutes": int(max_runtime_minutes),
            "authorized_mode": authorized_mode,
            "issued_at_utc": now,
            "expires_at_utc": now + validity_seconds,
            "session_nonce": nonce
        }
        canonical_data = cls.canonical_bytes(payload)
        sig = private_key.sign(canonical_data)
        sig_b64 = base64.b64encode(sig).decode("utf-8")
        pub_b64 = base64.b64encode(private_key.public_key().public_bytes_raw()).decode("utf-8")
        
        return {
            "payload": payload,
            "signature_ed25519_b64": sig_b64,
            "public_key_ed25519_b64": pub_b64
        }

    def verify_authorization(
        self,
        auth_doc: Dict[str, Any],
        active_experiment_id: str,
        active_pod_id: str,
        active_manifest_sha256: str,
        active_mode: str,
        active_model_id: str = PINNED_MODEL_ID,
        active_model_revision: str = PINNED_MODEL_REVISION
    ) -> Tuple[bool, str]:
        """
        Cryptographically verifies Ed25519 signature and enforces all operational bounds.
        Returns: (is_valid: bool, rejection_reason: str)
        """
        if not isinstance(auth_doc, dict):
            return False, "Authorization document must be a JSON dictionary."

        payload = auth_doc.get("payload")
        sig_b64 = auth_doc.get("signature_ed25519_b64")
        if not payload or not sig_b64:
            return False, "Authorization missing required 'payload' or 'signature_ed25519_b64'."

        for field in self.REQUIRED_PAYLOAD_FIELDS:
            if field not in payload:
                return False, f"Missing mandatory authorization field: '{field}'."

        # 1. Cryptographic Signature Verification
        try:
            sig_bytes = base64.b64decode(sig_b64)
            canonical_data = self.canonical_bytes(payload)
            self.trusted_public_key.verify(sig_bytes, canonical_data)
        except InvalidSignature:
            return False, "Ed25519 cryptographic signature verification FAILED: untrusted or forged signature."
        except Exception as e:
            return False, f"Signature verification error: {e}"

        # 2. Expiration Check
        now = time.time()
        if now > payload["expires_at_utc"]:
            return False, f"Authorization expired at UTC {payload['expires_at_utc']} (current: {now})."
        if payload["issued_at_utc"] > (now + 60.0):
            return False, "Authorization issued timestamp is in the future."

        # 3. Nonce Replay Check
        nonce = payload["session_nonce"]
        if nonce in self.seen_nonces:
            return False, f"Replay detected: session_nonce '{nonce}' has already been used."

        # 4. Manifest Hash Binding
        if payload["manifest_sha256"] != FROZEN_MANIFEST_SHA256:
            return False, f"Manifest hash '{payload['manifest_sha256']}' does not match frozen constant."
        if payload["manifest_sha256"] != active_manifest_sha256:
            return False, f"Manifest hash mismatch: auth={payload['manifest_sha256']}, active={active_manifest_sha256}."

        # 5. Pod ID Binding
        if active_mode in ["PRODUCTION", "PREFLIGHT"]:
            if payload["pod_id"] != active_pod_id:
                return False, f"Pod ID mismatch: auth bound to '{payload['pod_id']}', active is '{active_pod_id}'."

        # 6. Mode Binding
        if payload["authorized_mode"] != active_mode:
            return False, f"Execution mode mismatch: auth specifies '{payload['authorized_mode']}', active is '{active_mode}'."

        # 7. Model Identity Binding
        if payload["model_id"] != active_model_id:
            return False, f"Model ID mismatch: auth specifies '{payload['model_id']}', active is '{active_model_id}'."
        if payload["model_revision"] != active_model_revision:
            return False, f"Model revision mismatch: auth specifies '{payload['model_revision']}', active is '{active_model_revision}'."

        # 8. Financial Limits
        if payload["max_incremental_spend_usd"] > 2.00:
            return False, f"Authorized spend ${payload['max_incremental_spend_usd']} exceeds $2.00 hard limit."
        if payload["minimum_account_balance_usd"] < 7.00:
            return False, f"Preservation floor ${payload['minimum_account_balance_usd']} violates $7.00 mandatory floor."

        self._save_nonce(nonce)
        return True, "Authorization verified successfully."
