# StateShift: Cryptographic Authorization Token Validation
## Deliverable 04 — Session Authorization Generation & Cryptographic Verification
**Minting Timestamp:** 2026-10-26T07:24:38+05:30  
**Authorization Document:** [`data/primary_run/session_auth_calib_b1.json`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/data/primary_run/session_auth_calib_b1.json)  
**Signing Key:** Principal Investigator Authentic Ed25519 Key (`~/.ssh/id_ed25519`)  
**Public Key (Base64):** `IaQok2nQchG5qvIaMsLKHLe2zXqkarD7U7RLjO1H+bk=`  
**Algorithm:** Pure Ed25519 (`RFC 8032`) over Canonical JSON serialization  

---

## 1. Signed Authorization Payload

```json
{
  "schema_version": "1.0",
  "experiment_id": "stateshift_calib_b1_01",
  "manifest_sha256": "f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6",
  "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
  "model_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "pod_id": "PRE_PROVISION",
  "max_incremental_spend_usd": 1.0,
  "emergency_trigger_usd": 0.7,
  "minimum_account_balance_usd": 0.32,
  "maximum_runtime_minutes": 45,
  "authorized_mode": "CALIBRATION",
  "financial_policy_version": "POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION"
}
```

---

## 2. Invariant Validation Matrix

| Payload Field | Target Specification | Signed Value | Authorizer Check | Status |
|---|---|---|---|---|
| **`experiment_id`** | `stateshift_calib_b1_01` | `"stateshift_calib_b1_01"` | Matches runner execution ID | ✅ PASS |
| **`manifest_sha256`** | Frozen 10-Request Manifest | `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6` | Matches `calibration_10_manifest.json` | ✅ PASS |
| **`model_id`** | `Qwen/Qwen2.5-Math-7B-Instruct` | `"Qwen/Qwen2.5-Math-7B-Instruct"` | Canonical target model | ✅ PASS |
| **`model_revision`** | 40-char canonical SHA-1 | `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` | Live HuggingFace certified revision | ✅ PASS |
| **`pod_id`** | `PRE_PROVISION` | `"PRE_PROVISION"` | Pre-provision handshake binding | ✅ PASS |
| **`max_spend_usd`** | Planned Spending Ceiling | `$1.0000 USD` | Complies with Policy V2 Ceiling | ✅ PASS |
| **`emergency_trigger_usd`** | Watchdog Emergency Tripwire | `$0.7000 USD` | < $1.00 ceiling ($0.30 buffer) | ✅ PASS |
| **`min_balance_usd`** | Target Preservation Floor | `$0.3200 USD` | Policy V2 Target Reserve | ✅ PASS |
| **`maximum_runtime_minutes`** | Hard Wall-Clock Limit | `45` minutes | $0.6675 USD compute cap | ✅ PASS |
| **`authorized_mode`** | `CALIBRATION` | `"CALIBRATION"` | Primary 400 run strictly forbidden | ✅ PASS |
| **`financial_policy_version`** | `POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION` | `"POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION"` | Approved temporary policy exception | ✅ PASS |
| **`signature_ed25519_b64`** | Valid Ed25519 signature | Verified via Public Key | `authorizer.verify_authorization()` | ✅ PASS |

---

## 3. Authorizer Verification Result

- **Authorizer Status:** `is_valid: True`
- **Rejection Reason:** `None` (`"Authorization verified successfully."`)
- **Nonce State:** Fresh, unique nonce registered; no replay detected.
- **Validity Window:** 3600.0 seconds (1 hour).
