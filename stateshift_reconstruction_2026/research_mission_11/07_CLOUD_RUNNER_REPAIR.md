# 07. Cloud Experiment Runner Hardening Specification

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Audited Runner**: [`runpod/cloud_experiment_runner.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_11/runpod/cloud_experiment_runner.py)  

---

## 1. Weaknesses in the Mission 10 Runner & Key Repairs

1. **Missing Unified Condition Design**:
   The Mission 10 cloud runner omitted strict matching of prompt templates between local Apple Silicon and cloud environments.
   *Repair*: Prompt templates are locked into `PROMPT_TEMPLATES` with matched variable substitution across all 4 conditions (Condition A, D, E, F).
2. **Missing Backend Termination Metadata**:
   The prior runner recorded only raw string length.
   *Repair*: In vLLM and Transformers mode, the runner captures `finish_reason` / `stop_reason` and checks `hit_generation_limit` (`generated_tokens >= 768`).
3. **Fragile State Persistence**:
   A crash or network glitch would require re-running the entire batch from rollout 0.
   *Repair*: Implemented atomic JSON checkpointing with `self.completed_keys` (`{problem_id}::{condition_code}`) and atomic replace (`os.replace`) to guarantee zero redundant computation upon resume.
4. **vLLM Acceleration with Transformers Fallback**:
   Allows ultra-high throughput (~45–60 tokens/sec on RTX 4090) while supporting seamless fallback to PyTorch `transformers` if vLLM is not installed.

---

## 2. Experimental Condition Matrix

| Condition Code | Prompt Strategy | Prefix Injected | Description |
| :--- | :--- | :---: | :--- |
| **`Condition_A_Zero_Shot`** | Standard zero-shot | None | Control baseline for raw mathematical competence. |
| **`Condition_D_Forced_Restart`** | Discard & solve de novo | Recovery | Measures upper bound of clean re-derivation from scratch. |
| **`Condition_E_Explicit_Repair`** | Surgical step repair | Recovery | Explicitly commands model to identify and fix corrupted step. |
| **`Condition_F_State_Preserving`**| Verbatim preservation | Recovery | Commands model to retain valid prefix and correct assertion. |

---

## 3. Resume & Fault Tolerance Verification

The runner writes to `/workspace/output/b1_checkpoint.json.tmp` before atomically replacing the checkpoint file. If execution is interrupted:
```bash
python3 runpod/cloud_experiment_runner.py \
  --benchmark /workspace/benchmark.json \
  --output /workspace/output/b1_results.jsonl \
  --checkpoint /workspace/output/b1_checkpoint.json
```
The runner reads all completed keys and skips completed rollouts in $O(1)$ time.
