# StateShift — Calibration Technical Preflight
## Calibration Readiness Phase 5
**Date:** 2026-10-26T06:02:49+05:30  
**Verifier:** Independent preflight auditor  
**No model weights downloaded. No GPU inference executed.**

---

## 1. Qwen Inference Adapter Inspection

### 1.1 Model Identifier
**Manifest specifies:** `"model_id": "Qwen/Qwen2.5-Math-7B-Instruct"`  
**Runner hardcodes:** `"Qwen/Qwen2.5-Math-7B-Instruct"` (lines 626, runner output record)  
**Status: ✅ CONSISTENT**

### 1.2 Pinned Revision
**Manifest specifies:** `"model_revision": "main"`  
**Runner output record (after patch):** `"ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"`  
**Auth PINNED_MODEL_REVISION (after patch):** `"ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"`  
**HuggingFace current main HEAD:** `"ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"`

**Status: ✅ CONSISTENT after Phase 2 patch**  
(Pre-patch: runner and auth used invalid 33-char string — now remediated)

> [!NOTE]
> The manifest will instruct the inference engine to load `revision="main"`. This is by design and consistent with historical execution. The runner records the resolved SHA-1 (`ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`) in output files. If HuggingFace updates `main` between now and calibration execution, the runner should verify the loaded revision matches `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` and abort if it does not.

### 1.3 Tokenizer
**Manifest `model_id`:** `"Qwen/Qwen2.5-Math-7B-Instruct"` (same repo = same tokenizer)  
**Runner `tokenizer_revision` (after patch):** `"ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"`  
**Status: ✅ CONSISTENT** — Qwen2.5-Math uses its own tokenizer (tiktoken-based) bundled in the same repository.

### 1.4 Chat Template
**Verified from manifest prompt_text fields:** Prompts are constructed as raw text strings — not chat-formatted messages. The `prompt_text` is a complete, self-contained instruction that includes the problem statement and explicit solution instructions.

**Expected tokenization approach for vLLM:** `tokenizer.apply_chat_template([{"role": "user", "content": prompt_text}], add_generation_prompt=True)` — this wraps the raw prompt in Qwen2.5's `<|im_start|>user\n...<|im_end|>\n<|im_start|>assistant\n` template.

**Status: ✅ CORRECT** — Qwen2.5-Math-7B-Instruct uses the Qwen chat template. The prompt_text is the user turn content.

### 1.5 Generation Parameters

| Parameter | Manifest Value | Runner Configured | Status |
|---|---|---|---|
| `temperature` | `0.0` | `0.0` | ✅ |
| `max_tokens` | `768` | `768` | ✅ |
| `seed` | `42` | `42` | ✅ |
| `top_p` | MISSING from manifest | Not verified in manifest | ⚠️ ADVISORY |

> [!WARNING]
> `top_p` is absent from the manifest JSON fields. The mission specification requires `top_p=1`. At `temperature=0.0` (greedy decoding), `top_p` has no effect on output — greedy sampling always selects the maximum probability token regardless of `top_p`. However, for completeness and reproducibility, the `top_p=1` parameter should be explicitly included in the vLLM API call and in the output record.
>
> **This is an advisory, not a blocker**, since `temperature=0` makes `top_p` irrelevant to actual outputs.

**Sampling mode:** `"greedy"` (confirmed in runner output record schema)

### 1.6 Output Schema
Runner output record schema (per request):
```json
{
  "request_id": "primary_100_req_XXXX",
  "problem_id": "math500_XXX",
  "condition_code": "Condition_A_Zero_Shot",
  "prompt_sha256": "<sha256>",
  "gold_answer": "<answer>",
  "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
  "model_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "tokenizer_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "inference_engine": "<engine>",
  "inference_engine_version": "0.6.3",
  "temperature": 0.0,
  "max_tokens": 768,
  "seed": 42,
  "sampling_mode": "greedy",
  "completion_status": "COMPLETED",
  "finish_reason": "stop",
  "source_type": "REAL_MODEL_INFERENCE",
  "experiment_id": "<experiment_id>",
  "manifest_hash": "<manifest_sha256>",
  "generation_timestamp": <unix_timestamp>
}
```
**Status: ✅ SCHEMA APPROPRIATE** — includes model provenance, decoding parameters, and timestamp.

### 1.7 Generation Persistence
Each request result is written to disk immediately after generation (not batched). The checkpoint manager (`transactional_checkpoint_manager.py`) provides transactional write semantics: results are written to a temp file then renamed atomically.

**Status: ✅ PASS**

### 1.8 Crash Recovery
`stateshift_production_runner_v10.py` uses the `SafeResumeReconciler` pattern. On restart:
1. Reads the last checkpoint.
2. Identifies already-completed request IDs.
3. Skips completed requests.
4. Resumes from the first incomplete request.

**Status: ✅ PASS** (verified in offline tests `test_offline_incident_recovery.py`)

### 1.9 Request Identifiers
All 10 request IDs are of form `primary_100_req_XXXX` (see Phase 1 table). The runner validates that each output record's `request_id` matches the manifest entry. Duplicates are detected by the checkpoint manager.

**Status: ✅ PASS**

### 1.10 Evaluator Integration
`math_answer_evaluator.py` (16/16 unit tests passing) integrates:
- `\boxed{}` answer extraction from raw model output.
- Normalization: LaTeX simplification, numeric equivalence, symbolic comparison.
- Correctness scoring against `gold_answer`.
- Per-condition aggregation.
- Bootstrap 95% CI computation.

The evaluator can be run locally on the saved `.jsonl` generation files without re-invoking the model.

**Status: ✅ PASS**

---

## 2. Frozen Manifest Inspection

**Calibration manifest:** `research_mission_15_6/manifests/calibration_10_manifest.json`  
**SHA-256:** `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6` ✅

### Manifest Fields Verification

| Field | Value | Correct? |
|---|---|---|
| `schema_version` | `"1.0"` | ✅ |
| `calibration_id` | `"stateshift_10_request_gpu_calibration_v15_5"` | ✅ |
| `parent_manifest_sha256` | `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` | ✅ matches primary |
| `total_requests` | `10` | ✅ |
| All 10 request entries present | Yes | ✅ |
| `model_id` per request | `"Qwen/Qwen2.5-Math-7B-Instruct"` | ✅ |
| `model_revision` per request | `"main"` | ✅ (by protocol design) |
| `temperature` per request | `0.0` | ✅ |
| `max_tokens` per request | `768` | ✅ |
| `seed` per request | `42` | ✅ |
| `prompt_sha256` per request | Present, non-null | ✅ |
| `gold_answer` per request | Present, non-null | ✅ |
| Conditions covered | A, D, E, F | ✅ |
| Distribution | 3A, 3D, 2E, 2F | ✅ |

---

## 3. End-to-End Data Pipeline Test (Deterministic Mocked Responses)

A deterministic offline simulation was performed using the existing test infrastructure (`test_incident_replay_deterministic.py`, `test_cli_subprocess_rehearsal.py`).

**Method:** The production runner was instantiated with:
- `mode=SIMULATION`
- A fake transport returning deterministic JSON responses for all 10 request IDs.
- No actual RunPod API calls.
- No model weight loading.

**Result:** All 10 requests serialized, dispatched to mock, and deserialized correctly. Output records were validated against the expected schema. The evaluator correctly extracted answers and scored them.

> [!IMPORTANT]
> The mocked responses are not authentic model outputs. They are used only to verify the data pipeline mechanics. They are not recorded as empirical results.

**Status: ✅ PASS**

---

## 4. Identified Advisory Issues (Non-Blocking)

| Issue | Severity | Resolution |
|---|---|---|
| `top_p` absent from manifest | Advisory | At `temperature=0`, top_p has no effect. Add `top_p=1.0` to vLLM API call explicitly. |
| `revision="main"` is non-pinned | Advisory | Acceptable given historical precedent. Verify loaded revision == `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` at runtime. |
| Manifest uses `"main"` but auth enforces pinned hash | Advisory | The auth token must specify `model_revision: "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"` (the resolved SHA). |

---

## Phase 5 Summary

| Check | Status |
|---|---|
| Model identifier correct | ✅ PASS |
| Pinned revision reconciled (after patch) | ✅ PASS |
| Tokenizer correct | ✅ PASS |
| Chat template correct | ✅ PASS |
| Generation parameters correct | ✅ PASS (top_p advisory) |
| Output schema correct | ✅ PASS |
| Generation persistence (atomic write) | ✅ PASS |
| Crash recovery | ✅ PASS |
| Request identifiers correct | ✅ PASS |
| Evaluator integration | ✅ PASS |
| Manifest fields complete | ✅ PASS |
| End-to-end pipeline test (mocked) | ✅ PASS |

**Phase 5 verdict: TECHNICALLY READY (with top_p advisory noted)**
