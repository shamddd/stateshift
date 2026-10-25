# StateShift Mission 15.6: Calibration Completion Semantics & Receipt Verification

**Project:** StateShift Research Mission 15.6  
**Document:** `10_CALIBRATION_COMPLETION_VERIFICATION.md`  
**Focus:** 10-Request GPU Calibration Dataset Verification & Cryptographic Receipts  

---

## 1. Frozen 10-Request Calibration Selection

The calibration experiment evaluates exactly 10 requests selected deterministically from the frozen parent manifest (`primary_100_manifest.json`):

- **Parent Manifest SHA-256:** `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`
- **Calibration Selection SHA-256:** `91c57ea9f3e26045abb34a721c43bad38af49f9bb647037941f2c261b61adfec`

### The 10 Frozen Calibration Requests

| # | Request ID | Problem ID | Subject | Difficulty | Condition Code | Condition Name |
| :-: | :--- | :--- | :--- | :-: | :--- | :--- |
| **1** | `primary_100_req_0001` | `math500_001` | Intermediate Algebra | 1 | `Condition_A_Zero_Shot` | neutral |
| **2** | `primary_100_req_0002` | `math500_001` | Intermediate Algebra | 1 | `Condition_D_Forced_Restart` | forced restart |
| **3** | `primary_100_req_0003` | `math500_001` | Intermediate Algebra | 1 | `Condition_E_Explicit_Repair` | explicit repair |
| **4** | `primary_100_req_0004` | `math500_001` | Intermediate Algebra | 1 | `Condition_F_State_Preserving` | state preserving |
| **5** | `primary_100_req_0005` | `math500_012` | Prealgebra | 1 | `Condition_A_Zero_Shot` | neutral |
| **6** | `primary_100_req_0006` | `math500_012` | Prealgebra | 1 | `Condition_D_Forced_Restart` | forced restart |
| **7** | `primary_100_req_0007` | `math500_012` | Prealgebra | 1 | `Condition_E_Explicit_Repair` | explicit repair |
| **8** | `primary_100_req_0008` | `math500_012` | Prealgebra | 1 | `Condition_F_State_Preserving` | state preserving |
| **9** | `primary_100_req_0009` | `math500_023` | Algebra | 1 | `Condition_A_Zero_Shot` | neutral |
| **10**| `primary_100_req_0010` | `math500_023` | Algebra | 1 | `Condition_D_Forced_Restart` | forced restart |

---

## 2. Exact Completion Verification Rules

In `IndependentDatasetVerifierV2(is_calibration=True)`:
1. **Exact Cardinality:** Exactly 10 records must be present. 9 records $\rightarrow$ `INCOMPLETE`; 11 records $\rightarrow$ `CORRUPT`.
2. **Exact Identity:** All 10 record IDs must match the frozen set. Any unexpected ID $\rightarrow$ `CORRUPT`.
3. **No Fallback Substitutions:** Silent substitution of alternate problems or conditions is strictly prohibited and fails verification.
4. **Decoding Invariants:**
   - `temperature == 0.0` (greedy decoding)
   - `max_tokens == 768`
   - `seed == 42`
   - `sampling_mode == "greedy"`
5. **Model Identity:**
   - `model_id == "Qwen/Qwen2.5-Math-7B-Instruct"`
   - `model_revision == "c869d27376a8d6728795551322fe323b6"`
   - `inference_engine == "vllm"`
   - `inference_engine_version == "0.6.3"`
6. **Contamination Screening:** Any record containing synthetic infrastructure dry-run strings is rejected.

---

## 3. Cryptographic Verification Receipt Schema

Upon successful verification, the verifier fsyncs `verification_receipt.json`:

```json
{
  "passed": true,
  "manifest_path": "/workspace/research_mission_15_6/manifests/calibration_10_manifest.json",
  "manifest_sha256": "f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6",
  "dataset_path": "/workspace/data/stateshift-calibration-10_dataset.jsonl",
  "dataset_sha256": "...",
  "total_records_found": 10,
  "total_records_expected": 10,
  "completed_valid_count": 10,
  "failed_count": 0,
  "truncated_count": 0,
  "duplicate_count": 0,
  "missing_count": 0,
  "error_count": 0,
  "errors": [],
  "verification_timestamp_utc": 1729861500.0,
  "is_calibration": true,
  "calibration_subset_hash": "91c57ea9f3e26045abb34a721c43bad38af49f9bb647037941f2c261b61adfec"
}
```

---

## 4. Test Verification Traceability

- **`test_issue_f_calibration_exact_10_records_pass`**: Verifies exact 10 records matching frozen calibration IDs pass verification.
- **`test_issue_f_calibration_rejects_incomplete_dataset`**: Verifies 9 records are rejected as incomplete.
- **`test_issue_f_calibration_rejects_extra_unexpected_records`**: Verifies unexpected 11th record is rejected as corrupt.
- **`test_scenario_A_valid_10_request_simulation`**: Verifies end-to-end receipt generation in simulated calibration.
- **`test_scenario_M_missing_calibration_id_fails`**: Proves missing calibration IDs fail launch immediately.
