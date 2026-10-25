#!/usr/bin/env python3
"""
StateShift Production Cryptographic Session Authorization (Mission 15.5)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Hardened Cryptographic Authorization:
- Complete removal of embedded default test keys for production modes.
- Production/Calibration execution strictly requires an external, PI-controlled trusted public key.
- Strict rejection of known repository test keys in CALIBRATION or PRODUCTION.
- Exact pod-ID binding enforced for ALL paid/cloud modes (both CALIBRATION and PRODUCTION).
- Single-use session nonces with persistent replay registry.
- Canonical sorted JSON serialization.
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

# Known repository test seed / key (Prohibited from authorizing real cloud execution)
KNOWN_TEST_SEED = b"stateshift_pi_test_key_seed_32b_"
_known_test_priv = ed25519.Ed25519PrivateKey.from_private_bytes(KNOWN_TEST_SEED)
KNOWN_TEST_PUBLIC_KEY_B64 = base64.b64encode(_known_test_priv.public_key().public_bytes_raw()).decode("utf-8")


class AuthorizationSecurityError(Exception):
    pass


class CryptographicAuthorizer:
    REQUIRED_PAYLOAD_FIELDS = [
        "schema_version",
        "experiment_id",
        "manifest_sha256",
        "model_id",
        "model_revision",
        "pod_id",
        "max_incremental_spend_usd",
        "emergency_trigger_usd",
        "minimum_account_balance_usd",
        "maximum_runtime_minutes",
        "authorized_mode",
        "issued_at_utc",
        "expires_at_utc",
        "session_nonce"
    ]

    def __init__(
        self,
        trusted_public_key_b64: Optional[str] = None,
        nonce_registry_path: Optional[str] = None,
        allow_test_key_for_testing: bool = False
    ):
        """
        Production constructor.
        If trusted_public_key_b64 is omitted, attempts to load from STATESHIFT_TRUSTED_PUBLIC_KEY env var.
        No default repository test key is ever trusted implicitly.
        """
        self.allow_test_key_for_testing = allow_test_key_for_testing
        raw_key = trusted_public_key_b64 or os.environ.get("STATESHIFT_TRUSTED_PUBLIC_KEY", "").strip()

        if not raw_key:
            self.trusted_public_key_b64 = None
            self.trusted_public_key = None
        else:
            self.trusted_public_key_b64 = raw_key
            try:
                key_bytes = base64.b64decode(raw_key)
                if len(key_bytes) != 32:
                    raise ValueError(f"Key length is {len(key_bytes)} bytes, must be exactly 32 bytes.")
                self.trusted_public_key = ed25519.Ed25519PublicKey.from_public_bytes(key_bytes)
            except Exception as e:
                raise ValueError(f"Malformed trusted public key: {e}")

        self.nonce_registry_path = nonce_registry_path
        self.seen_nonces: Set[str] = set()
        self._load_nonces()

    def _load_nonces(self):
        if self.nonce_registry_path and os.path.exists(self.nonce_registry_path):
            try:
                with open(self.nonce_registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.seen_nonces = set(data.get("used_nonces", []))
            except Exception:
                self.seen_nonces = set()

    def _save_nonce(self, nonce: str):
        self.seen_nonces.add(nonce)
        if self.nonce_registry_path:
            os.makedirs(os.path.dirname(os.path.abspath(self.nonce_registry_path)), exist_ok=True)
            tmp = self.nonce_registry_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"used_nonces": sorted(list(self.seen_nonces))}, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.nonce_registry_path)

    @staticmethod
    def canonical_bytes(payload: Dict[str, Any]) -> bytes:
        """Deterministic canonical JSON serialization."""
        return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode("utf-8")

    @classmethod
    def create_signed_authorization(
        cls,
        private_key: ed25519.Ed25519PrivateKey,
        experiment_id: str,
        manifest_sha256: str,
        model_id: str,
        model_revision: str,
        pod_id: str,
        max_spend_usd: float = 0.35,
        emergency_trigger_usd: float = 0.25,
        min_balance_usd: float = 7.00,
        max_runtime_minutes: int = 60,
        authorized_mode: str = "CALIBRATION",
        validity_seconds: float = 3600.0,
        session_nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """Utility for authorized operators to generate signed session approval."""
        now = time.time()
        nonce = session_nonce or base64.b64encode(os.urandom(16)).decode("utf-8")
        
        payload = {
            "schema_version": "1.0",
            "experiment_id": experiment_id,
            "manifest_sha256": manifest_sha256,
            "model_id": model_id,
            "model_revision": model_revision,
            "pod_id": pod_id,
            "max_incremental_spend_usd": round(max_spend_usd, 4),
            "emergency_trigger_usd": round(emergency_trigger_usd, 4),
            "minimum_account_balance_usd": round(min_balance_usd, 4),
            "maximum_runtime_minutes": max_runtime_minutes,
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
        if not self.trusted_public_key:
            return False, "Security Error: No trusted public key configured. Paid execution prohibited."

        if not isinstance(auth_doc, dict):
            return False, "Authorization document must be a JSON dictionary."

        payload = auth_doc.get("payload")
        sig_b64 = auth_doc.get("signature_ed25519_b64")
        doc_pub_b64 = auth_doc.get("public_key_ed25519_b64")

        if not payload or not sig_b64:
            return False, "Authorization missing required 'payload' or 'signature_ed25519_b64'."

        for field in self.REQUIRED_PAYLOAD_FIELDS:
            if field not in payload:
                return False, f"Missing mandatory authorization field: '{field}'."

        # Prohibit embedded test key in paid cloud modes unless explicit test flag set
        if active_mode in ["CALIBRATION", "PRODUCTION"]:
            if self.trusted_public_key_b64 == KNOWN_TEST_PUBLIC_KEY_B64 and not self.allow_test_key_for_testing:
                return False, "Security Violation: Embedded repository test key cannot authorize CALIBRATION or PRODUCTION."

        # Public key binding check
        if doc_pub_b64 and doc_pub_b64 != self.trusted_public_key_b64:
            return False, f"Public key mismatch: signer={doc_pub_b64}, trusted={self.trusted_public_key_b64}."

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

        # 5. Pod ID Binding (ENFORCED FOR BOTH CALIBRATION AND PRODUCTION)
        if active_mode in ["CALIBRATION", "PRODUCTION", "PREFLIGHT"]:
            if not active_pod_id:
                return False, f"Pod ID must be provided for {active_mode} mode."
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

        # 8. Experiment ID Binding
        if payload["experiment_id"] != active_experiment_id:
            return False, f"Experiment ID mismatch: auth specifies '{payload['experiment_id']}', active is '{active_experiment_id}'."

        # 9. Financial Limits Enforcement
        if active_mode == "CALIBRATION":
            if payload["max_incremental_spend_usd"] > 0.35:
                return False, f"Authorized calibration spend ${payload['max_incremental_spend_usd']} exceeds $0.35 limit."
            if payload["emergency_trigger_usd"] > payload["max_incremental_spend_usd"]:
                return False, f"Emergency trigger ${payload['emergency_trigger_usd']} exceeds authorized budget ${payload['max_incremental_spend_usd']}."
        else:
            if payload["max_incremental_spend_usd"] > 2.00:
                return False, f"Authorized spend ${payload['max_incremental_spend_usd']} exceeds $2.00 hard limit."
            if payload["emergency_trigger_usd"] > 1.65:
                return False, f"Emergency trigger ${payload['emergency_trigger_usd']} exceeds $1.65 limit."

        if payload["minimum_account_balance_usd"] < 7.00:
            return False, f"Preservation floor ${payload['minimum_account_balance_usd']} violates $7.00 mandatory floor."

        self._save_nonce(nonce)
        return True, "Authorization verified successfully."
