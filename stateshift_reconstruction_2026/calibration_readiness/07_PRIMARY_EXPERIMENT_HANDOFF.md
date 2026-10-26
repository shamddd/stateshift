# StateShift — Primary Experiment Handoff
## Calibration Readiness Phase 7
**Date:** 2026-10-26T06:02:49+05:30  
**Status:** PREPARED — NOT AUTHORIZED — NOT STARTED  
**Prerequisite:** Successful completion of the 10-request calibration AND separate human authorization.

> [!CAUTION]
> The 400-request primary experiment must not be initiated automatically or as a continuation of the calibration session. It requires independent PI authorization with new cryptographic tokens after calibration results are reviewed.

---

## Frozen Request Manifest

| Field | Value |
|---|---|
| File | `research_mission_15_6/manifests/primary_100_manifest.json` |
| SHA-256 | `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` |
| Schema version | `1.0` |
| Total requests | `400` (100 problems × 4 conditions) |
| Conditions | A (Zero-Shot), D (Forced Restart), E (Explicit Repair), F (State-Preserving) |
| Distribution | 100 requests per condition |
| Problems | 100 MATH-500 problems across subjects and difficulties |

**Manifest integrity:** SHA-256 must be verified against `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` before execution.

---

## Model Revision

| Component | Value |
|---|---|
| Model ID | `Qwen/Qwen2.5-Math-7B-Instruct` |
| Protocol revision (manifest) | `"main"` |
| Resolved pinned SHA-1 | `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` |
| Runner record revision | `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` |

**Requirement:** At execution time, verify that `revision="main"` resolves to `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`. If the HuggingFace `main` branch has been updated in the interim, the PI must decide whether to pin to the original SHA or accept the new weights (requires documented protocol amendment and new authorization token).

---

## Expected Output Schema

Each of the 400 records must contain:
```json
{
  "request_id":              "primary_100_req_XXXX",
  "problem_id":              "math500_XXX",
  "condition_code":          "Condition_A_Zero_Shot | Condition_D_... | Condition_E_... | Condition_F_...",
  "prompt_sha256":           "<sha256 of prompt_text>",
  "gold_answer":             "<ground truth>",
  "model_id":                "Qwen/Qwen2.5-Math-7B-Instruct",
  "model_revision":          "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "tokenizer_revision":      "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "temperature":             0.0,
  "max_tokens":              768,
  "seed":                    42,
  "top_p":                   1.0,
  "sampling_mode":           "greedy",
  "completion_status":       "COMPLETED",
  "finish_reason":           "stop | length",
  "source_type":             "REAL_MODEL_INFERENCE",
  "raw_output":              "<full model text output>",
  "prompt_tokens":           <integer>,
  "generated_tokens":        <integer>,
  "latency_seconds":         <float>,
  "tokens_per_second":       <float>,
  "experiment_id":           "<chosen_id>",
  "manifest_hash":           "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
  "generation_timestamp":    <unix_timestamp>
}
```

---

## Generation Configuration

| Parameter | Value | Notes |
|---|---|---|
| Temperature | `0.0` | Greedy decoding |
| Top-p | `1.0` | Irrelevant at temperature=0, but must be explicitly set |
| Max new tokens | `768` | Per the frozen protocol |
| Seed | `42` | Determinism anchor |
| Sampling mode | `greedy` | Argmax at each step |
| Stop condition | EOS token or max_tokens | No custom stop strings |

---

## Checkpointing Strategy

- Write each result atomically to `<experiment_id>_generations.jsonl` immediately after generation (append mode, atomic rename).
- The checkpoint file is the single source of truth for completed requests.
- `SafeResumeReconciler` identifies completed `request_id` values by reading the checkpoint on startup.
- On resume: skip all already-present request IDs, continue from first absent one.

**Checkpoint file location:** `research_mission_15_6/data/<experiment_id>_generations.jsonl`

---

## Resume Behavior

```bash
# Resume after crash (same experiment_id, same manifest):
python -m research_mission_15_6.runner.stateshift_launch \
    --mode production \
    --experiment-id <same_experiment_id> \
    --manifest research_mission_15_6/manifests/primary_100_manifest.json \
    --authorization <new_authorization_token_for_new_pod_id>
```

**Note:** A new pod ID requires a new cryptographic authorization token. The nonce registry prevents reuse of old tokens.

---

## Duplicate Prevention

1. **Checkpoint deduplication:** `SafeResumeReconciler` reads existing `request_id` values from checkpoint before starting.
2. **Pod ID enforcement:** Each token is bound to a specific pod ID; if a new pod is used for resume, a new token is generated (with the new pod ID).
3. **Manifest immutability:** The frozen manifest is read-only. No new requests can be added.

---

## Data Integrity Checks (Pre-Analysis)

Run before statistical analysis:
```bash
python -m research_mission_15_6.evaluation.dataset_verifier_v2 \
    --generations research_mission_15_6/data/<experiment_id>_generations.jsonl \
    --manifest research_mission_15_6/manifests/primary_100_manifest.json \
    --expected-count 400
```

Verifier checks:
- [ ] Exactly 400 records present.
- [ ] All `request_id` values unique.
- [ ] All `request_id` values present in the primary manifest.
- [ ] All records have `"source_type": "REAL_MODEL_INFERENCE"`.
- [ ] All records have `"completion_status": "COMPLETED"`.
- [ ] Manifest SHA-256 matches frozen value in all records.
- [ ] Model revision matches `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` in all records.
- [ ] Generation timestamps are monotonic within each condition batch.

---

## Statistical Analysis Command

```bash
python -m research_mission_15_6.evaluation.math_answer_evaluator \
    --input research_mission_15_6/data/<experiment_id>_generations.jsonl \
    --output research_mission_15_6/results/primary_experiment_analysis.json \
    --n-bootstrap 10000 \
    --alpha 0.05
```

Produces:
- Per-condition accuracy (proportion correct).
- Bootstrap 95% CIs (10,000 resamples).
- Pairwise condition comparisons (Cohen's h effect size).
- Overall accuracy table.
- Per-problem breakdown.

---

## Calibration Metrics Required for Budgeting

Before the 400-request experiment can be budgeted, the following must be measured from the 10-request calibration:

| Metric | Why Needed |
|---|---|
| Actual tokens/second on RTX 4090 | Estimate generation time for 400 requests |
| Actual latency per request (mean, max) | Bound runtime estimate |
| Actual cost per 10 requests | Scale to 400 |
| Model download time | One-time fixed cost (if pod is fresh) |
| Pod startup time | One-time overhead |

**Estimated 400-request runtime (pending calibration data):**  
`= (10-request calibration_duration × 40) + pod_startup_overhead`

**Estimated 400-request cost (pending calibration data):**  
`= (10-request_cost × 40) + one_time_startup_cost`

These figures cannot be estimated reliably without real calibration data. Do not authorize the 400-request experiment until the calibration receipt is reviewed.

---

## Independent Authorization Required

The 400-request experiment requires:
1. A written PI authorization separate from the calibration authorization.
2. A new Ed25519-signed token with:
   - A new `nonce`
   - The primary manifest SHA-256 (`3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`)
   - An updated `max_incremental_spend_usd` reflecting the actual calibration-derived estimate.
   - An updated `maximum_runtime_minutes` reflecting the estimated runtime.
3. A fresh balance check and financial reserve confirmation.
4. A new independent supervisor instance.

The calibration authorization token must not be reused for the primary experiment (nonce replay prevention will block it regardless).

---

## Phase 7 Summary

The 400-request primary experiment plan is documented, frozen, and ready. Execution is blocked pending:
1. Completion of 10-request calibration.
2. Review of calibration results (accuracy, runtime, cost).
3. Separate independent PI authorization.

**No aspect of this document authorizes GPU execution.**
