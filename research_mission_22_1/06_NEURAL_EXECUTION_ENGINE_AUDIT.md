# Phase 6: Neural Execution Engine Audit & Verification

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22.1 — Final Confirmatory Scientific Audit  
**Date & Timestamp**: 2026-10-27T05:49:00+05:30  
**Target Publication Venue**: NeurIPS 2027 Main Track  

---

## 1. Executive Summary

The execution engine responsible for conducting neural inference during the confirmatory trial (`run_confirmatory_trial.py`) was audited against strict software and scientific integrity criteria. The runner has been enhanced to produce standardized 23-field JSONL records that preserve the complete raw generation text, cleanroom parsed answers, token counts (prompt, output, and total), timing, and execution identifiers.

Mock generations are strictly restricted to local CPU unit tests and are explicitly labeled `source_type: MOCK_LOCAL_TEST`. In genuine GPU execution, only authentic outputs from `Qwen/Qwen2.5-Math-7B-Instruct` will be serialized (`source_type: REAL_MODEL_INFERENCE`).

---

## 2. Neural Runner Architecture & Invariant Verification

| Subsystem Component | Specification / Setting | Verification Status |
| :--- | :--- | :---: |
| **Model ID** | `Qwen/Qwen2.5-Math-7B-Instruct` | **VERIFIED** |
| **Model Git Revision** | `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` | **PINNED** |
| **Tokenizer Revision** | `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` | **PINNED** |
| **Precision** | `torch.bfloat16` | **VERIFIED** |
| **Device Mapping** | `device_map="auto"` (single physical GPU) | **VERIFIED** |
| **Decoding Strategy** | Pure greedy decoding (`do_sample=False`) | **VERIFIED** |
| **Temperature** | `0.0` | **VERIFIED** |
| **Random Seed** | `42` (`torch.manual_seed(42)`) | **VERIFIED** |
| **Maximum Generation Limit** | `768` tokens | **VERIFIED** |
| **Transaction Persistence** | Incremental `fsync` after every generation | **VERIFIED** |
| **Crash Resumption** | Checks existing `request_id`s in output JSONL | **VERIFIED** |

---

## 3. Standardized Generation Record Schema

Every output line emitted by the engine adheres to the following audited schema:

```json
{
  "request_id": "confirmatory_231_req_0001",
  "problem_id": "math500_113",
  "condition_code": "Condition_A_Zero_Shot",
  "prompt_sha256": "62c4a68225e33698d260b9c6b119a63b7db491ff6d8b1e4da21695e393ab40c0",
  "gold_answer": "8000",
  "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
  "model_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "tokenizer_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "temperature": 0.0,
  "max_tokens": 768,
  "seed": 42,
  "sampling_mode": "greedy",
  "prompt_tokens": 50,
  "output_tokens": 25,
  "total_tokens": 75,
  "finish_reason": "stop",
  "elapsed_seconds": 0.0013,
  "generation_timestamp": 1793060266.30373,
  "execution_id": "stateshift_confirmatory_2027",
  "source_type": "MOCK_LOCAL_TEST",
  "extracted_answer": "8000",
  "is_correct": true,
  "model_output": "Let us solve step by step. Evaluating the expression gives \\boxed{8000}."
}
```

---

## 4. Crash Recovery & Resumability Protocol

1. **Pre-Run Checkpoint Audit**: Before dispatching any request, the runner inspects the target output JSONL file, reads all previously generated records, and builds an in-memory set of completed `request_id`s.
2. **Atomic Append**: After each generation finishes, the complete JSON record is appended with explicit OS file synchronization (`os.fsync`), preventing data corruption in the event of an unexpected network disconnect or container interruption.
3. **Zero Duplication**: If the trial is interrupted, re-launching the runner resumes from the exact uncompleted request index without re-running or duplicating previously paid generations.

**Phase 6 Audit Verdict**: **PASS** (Model execution engine verified, instrumented, and resumable).
