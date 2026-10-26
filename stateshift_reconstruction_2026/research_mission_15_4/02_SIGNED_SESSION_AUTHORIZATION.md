# Phase 2: Signed Session Authorization Specification

**Module**: `research_mission_15_4/auth/session_authorizer_v2.py`  
**Test Suite**: `research_mission_15_4/tests/test_cryptographic_authorization.py` (12 Tests Passing)  

### Architecture
- Asymmetric cryptography utilizing standard `ed25519` primitives via the `cryptography` Python package.
- Canonical sorted JSON serialization (`json.dumps(payload, sort_keys=True, separators=(',', ':'))`) ensures deterministic byte representations across all platforms and environments.
- Payload binds:
  1. `experiment_id`
  2. `manifest_sha256` (`3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`)
  3. `model_id` (`Qwen/Qwen2.5-Math-7B-Instruct`)
  4. `model_revision` (`c869d27376a8d6728795551322fe323b6`)
  5. `pod_id`
  6. `max_incremental_spend_usd`
  7. `minimum_account_balance_usd` (`$7.0000`)
  8. `maximum_runtime_minutes` (`160`)
  9. `authorized_mode` (`CALIBRATION` or `PRODUCTION`)
  10. `issued_at_utc` and `expires_at_utc`
  11. `session_nonce`
- Persistent Nonce Registry ensures single-use nonce consumption, completely neutralizing replay attacks.
