# StateShift — Scientific Calibration Verification
## Deliverable 04 — Protocol Integrity & Frozen Manifest Audit
**Manifest File:** `research_mission_15_6/manifests/calibration_10_manifest.json`  
**Verified SHA-256:** `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6`  
**Parent Manifest SHA-256:** `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`  

---

## 1. Frozen Calibration Selection & Request Mapping

The 10 calibration requests represent a strictly deterministic, stratified sample from the primary 400-request MATH-500 experiment across all four experimental conditions:

| # | Request Identifier | Problem ID | Subject Domain | Difficulty | Experimental Condition | Prefix Type | Gold Answer |
|---|---|---|---|---|---|---|---|
| **1** | `primary_100_req_0001` | `math500_001` | Intermediate Algebra | Level 1 | `Condition_A_Zero_Shot` | None (Standard) | `p - q` |
| **2** | `primary_100_req_0002` | `math500_001` | Intermediate Algebra | Level 1 | `Condition_D_Forced_Restart` | Forced Restart Prompt | `p - q` |
| **3** | `primary_100_req_0003` | `math500_001` | Intermediate Algebra | Level 1 | `Condition_E_Explicit_Repair` | Explicit Surgical Repair | `p - q` |
| **4** | `primary_100_req_0004` | `math500_001` | Intermediate Algebra | Level 1 | `Condition_F_State_Preserving` | State-Preserving Recovery | `p - q` |
| **5** | `primary_100_req_0005` | `math500_012` | Prealgebra | Level 2 | `Condition_A_Zero_Shot` | None (Standard) | `12` |
| **6** | `primary_100_req_0006` | `math500_012` | Prealgebra | Level 2 | `Condition_D_Forced_Restart` | Forced Restart Prompt | `12` |
| **7** | `primary_100_req_0007` | `math500_012` | Prealgebra | Level 2 | `Condition_E_Explicit_Repair` | Explicit Surgical Repair | `12` |
| **8** | `primary_100_req_0008` | `math500_012` | Prealgebra | Level 2 | `Condition_F_State_Preserving` | State-Preserving Recovery | `12` |
| **9** | `primary_100_req_0009` | `math500_023` | Algebra | Level 3 | `Condition_A_Zero_Shot` | None (Standard) | `\\frac{1}{2}` |
| **10** | `primary_100_req_0010` | `math500_023` | Algebra | Level 3 | `Condition_D_Forced_Restart` | Forced Restart Prompt | `\\frac{1}{2}` |

### Condition Distribution:
- **Condition A (Zero-Shot Baseline):** 3 Requests (30%)
- **Condition D (Forced Restart):** 3 Requests (30%)
- **Condition E (Explicit Surgical Repair):** 2 Requests (20%)
- **Condition F (State-Preserving Recovery):** 2 Requests (20%)
- **Total:** Exactly 10 requests. Zero duplicates. Zero omissions.

---

## 2. Model & Tokenizer Provenance

- **Target Model ID:** `Qwen/Qwen2.5-Math-7B-Instruct`
- **Canonical Model Commit (Pinned):** `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` (Full 40-character SHA-1)
- **HuggingFace Hub Verification:** Confirmed matching HEAD of `Qwen/Qwen2.5-Math-7B-Instruct`.
- **Tokenizer ID & Revision:** Bound directly to model commit `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`.
- **Chat Template:** Standard Qwen2.5 template (`<|im_start|>user\n{prompt}\n<|im_end|>\n<|im_start|>assistant\n`).

---

## 3. Strict Decoding Specification

All 10 inference requests are configured with deterministic decoding:

$$\text{Decoding Policy} = \arg\max_{w} P(w \mid \text{context})$$

| Hyperparameter | Frozen Value | Scientific Justification |
|---|---|---|
| **Sampling Mode** | `greedy` | Eliminates stochastic generation variance across replications. |
| **Temperature** | `0.0` | Mathematical reasoning determinism anchor. |
| **Top-P (Nucleus Sampling)** | `1.0` | Full vocabulary consideration under greedy argmax. |
| **Maximum New Tokens** | `768` | Matches the calibrated reasoning trace budget for MATH-500. |
| **Random Seed** | `42` | Cryptographic pseudorandom determinism anchor. |
| **Stop Sequences** | `["<|im_end|>", "<|endoftext|>"]` | Standard EOS delimiters. |

---

## 4. Output Record Schema & Provenance

Each generated record is written as a self-describing JSON line conforming to the StateShift provenance standard:

```json
{
  "request_id": "primary_100_req_0001",
  "problem_id": "math500_001",
  "condition_code": "Condition_A_Zero_Shot",
  "prompt_sha256": "7b282914d5e21a79700905c75ae8d3e69c05a1fdb96ea6d99a47f99dcb2e5b5e",
  "gold_answer": "p - q",
  "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
  "model_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "tokenizer_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "inference_engine": "vllm",
  "inference_engine_version": "0.6.3",
  "temperature": 0.0,
  "top_p": 1.0,
  "max_tokens": 768,
  "seed": 42,
  "sampling_mode": "greedy",
  "completion_status": "COMPLETED",
  "finish_reason": "stop",
  "source_type": "REAL_MODEL_INFERENCE",
  "raw_output": "...",
  "prompt_tokens": 142,
  "generated_tokens": 489,
  "latency_seconds": 12.34,
  "tokens_per_second": 39.62,
  "experiment_id": "stateshift_calib_20261026_01",
  "manifest_hash": "f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6",
  "generation_timestamp": 1729924800.0
}
```

---

## 5. Scientific Integrity Safeguards

1. **Zero Manifest Mutations:** `calibration_10_manifest.json` is treated as strictly read-only.
2. **Zero Model Substitutions:** Prohibits substituting smaller models (e.g. 1.5B or 0.5B).
3. **Zero Synthetic Generation:** Prohibits counting mock, heuristic, or simulation records as empirical evidence.
4. **Independent Math Answer Evaluation:** All model outputs will be evaluated by `math_answer_evaluator.py` using SymPy-verified canonical LaTeX answer extraction and comparison.
