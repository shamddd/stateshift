# StateShift Mission 15.2: Strict Dataset Provenance and Completion Gate

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_2/05_STRICT_DATASET_PROVENANCE.md`  

---

## 1. Executive Problem Statement

To withstand adversarial peer review at NeurIPS 2027 and maintain total scientific reproducibility, the experimental evaluation pipeline must independently verify that collected inference rollouts are authentic, complete, correctly configured, and uncorrupted.

In earlier versions (`IndependentDatasetVerifierV1`), the verifier only checked for basic keys (`request_id`, `problem_id`, `condition_code`, `model_output`). It omitted:
- Model identity and exact weights/tokenizer commit hashes (`model_revision`, `tokenizer_revision`).
- Decoding parameters (`temperature`, `max_tokens`, `seed`, `sampling_mode`).
- Generation completion status (`completion_status == 'COMPLETED'`), allowing truncated or failed generations to be counted as completed.
- Provenance tags (`source_type == 'REAL_MODEL_INFERENCE'`).

---

## 2. Comprehensive Enforcement Schema (`IndependentDatasetVerifierV2`)

`IndependentDatasetVerifierV2` validates 18 distinct dimensions across every record in the physical JSONL dataset:

### A. Mandatory Metadata Schema
Every record must contain all 20 required keys:
```json
{
  "request_id": "req_001",
  "problem_id": "prob_001",
  "condition_code": "C1_STANDARD",
  "prompt_sha256": "4b68...322f",
  "gold_answer": "42",
  "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
  "model_revision": "c869d27376a8d6728795551322fe323b6",
  "tokenizer_revision": "c869d27376a8d6728795551322fe323b6",
  "inference_engine": "vllm",
  "inference_engine_version": "0.6.3.post1",
  "temperature": 0.0,
  "max_tokens": 768,
  "seed": 42,
  "sampling_mode": "greedy",
  "completion_status": "COMPLETED",
  "finish_reason": "stop",
  "source_type": "REAL_MODEL_INFERENCE",
  "experiment_id": "stateshift_400_replication_2026",
  "manifest_hash": "2a3f...91bc",
  "generation_timestamp": 1774329600.0,
  "model_output": "The step-by-step reasoning solution..."
}
```

### B. Scientific Verification Criteria
1. **Model Identity**: Exact match of `model_id`, non-empty `model_revision` and `tokenizer_revision`, and explicit `inference_engine` identity.
2. **Deterministic Decoding Configuration**:
   - `temperature == 0.0` (strictly greedy).
   - `max_tokens == 768` (standard benchmark budget).
   - `seed == 42` (reproducibility seed).
   - `sampling_mode == 'greedy'`.
3. **Completion Status Segregation**:
   - Only `completion_status == 'COMPLETED'` records are counted towards valid scientific rollouts.
   - Any record with `completion_status` in `['TRUNCATED', 'FAILED', 'TIMEOUT', 'CANCELLED']` is rejected and flagged.
4. **Structured Provenance**:
   - `source_type == 'REAL_MODEL_INFERENCE'` (rejects synthetic/mock test records).
   - `manifest_hash` matches the physical SHA-256 of the frozen experimental manifest.
   - `prompt_sha256` and `condition_code` match the manifest request exactly.
5. **Physical Integrity & Reopening**:
   - Reopens the file from disk after writing (`os.fsync`).
   - Verifies trailing newline.
   - Computes whole-dataset SHA-256.
   - Detects any duplicate `request_id` or missing requests.
   - Writes an atomic `integrity_receipt.json` with cryptographic hashes.

---

## 3. Test Verification Summary

Phase 5 verified all 20 test cases in `research_mission_15_2/tests/test_strict_dataset_provenance.py`:
- Test cases 1–20 passed with 100% success rate, verifying rejection of missing keys, invalid temperatures, wrong revisions, truncated outputs, synthetic contamination, in-memory/disk desynchronization, and confirming atomic integrity receipt creation.
