# 03 Production Signing Key Trust Model

**Module:** `research_mission_15_5/auth/session_authorizer_v2.py`

---

## 1. Cryptographic Trust Architecture
- **Algorithm:** Ed25519 (PureEdDSA over Curve25519) per RFC 8032.
- **Trust Anchor:** The runner requires an externally injected Base64-encoded PI public key (`trusted_public_key_b64`).
- **Embedded Test Key Quarantine:** The embedded test key seed (`stateshift_test_signing_key_32b!`) is strictly quarantined.
  - In `CALIBRATION` and `PRODUCTION` modes, the authorizer checks the public key fingerprint. Any authorization signed with the test key is rejected with a fatal `PermissionError`.
  - The parameter `allow_test_key_for_testing=True` is restricted to unit test fixtures and dry-run simulations.

## 2. Signature Payload Invariants
The signed authorization document binds:
- `experiment_id`: Unique campaign identifier.
- `manifest_sha256`: Cryptographic hash of the frozen 400-request manifest.
- `model_id`: Exactly `Qwen/Qwen2.5-Math-7B-Instruct`.
- `model_revision`: Exactly `c869d27376a8d6728795551322fe323b6`.
- `target_pod_id`: Mandatory physical pod ID for both calibration and production.
- `max_authorized_cost_usd`: Maximum spend cap ($0.35 for calibration).
- `emergency_trigger_usd`: Immediate shutdown threshold ($0.25 for calibration).
- `issued_at_utc` & `expires_at_utc`: Validity window (maximum 4 hours).
