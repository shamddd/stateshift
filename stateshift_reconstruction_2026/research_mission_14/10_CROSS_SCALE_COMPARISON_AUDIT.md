# StateShift Research Mission 14 — Deliverable 10: Cross-Scale Comparison Audit

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Investigating Role**: Independent Forensic Recovery Auditor  
**Date**: October 25, 2026  

---

## 1. Audit of Cross-Scale Experimental Match (1.5B vs. 7B)

Mission 13 presented a direct comparative analysis between:
- `Qwen/Qwen2.5-Math-1.5B-Instruct` (Executed locally on Apple Silicon Metal in Mission 12).
- `Qwen/Qwen2.5-Math-7B-Instruct` (Executed on NVIDIA RTX 4090 in Mission 13).

To qualify as a rigorous, controlled scaling experiment, both cohorts must share identical experimental parameters:

| Experimental Parameter | 1.5B Experiment (Mission 12) | 7B Experiment (Mission 13) | Match Status |
| :--- | :--- | :--- | :--- |
| **Problem Benchmark** | MATH-500 | MATH-500 | **MATCH** |
| **Problem Subsets** | 30 selected problems | 100 planned problems | **PARTIAL OVERLAP** |
| **Prompt Templates** | Frozen Conditions A, D, E, F | Frozen Conditions A, D, E, F | **MATCH** |
| **Decoding Temperature** | $T = 0.0$ (Greedy) | $T = 0.0$ (Greedy) | **MATCH** |
| **Top-p Sampling** | 1.0 | 1.0 | **MATCH** |
| **Max Output Tokens** | 768 tokens | 768 tokens | **MATCH** |
| **Inference Hardware** | Apple Silicon M1 (Metal / MPS) | NVIDIA RTX 4090 (CUDA 12.4) | **DIFFERENT HARDWARE** |
| **Inference Backend** | Hugging Face Transformers (PyTorch) | Hugging Face Transformers (PyTorch) | **MATCH** |
| **Evaluator Version** | Evaluator v4 | Evaluator v4 | **MATCH** (both subject to v4 bias) |
| **Sample Size Verified** | 30 completed rollouts | 4 smoke + 2 traces physically local | **ASYMMETRIC POWER** |

---

## 2. Methodological Classification: Controlled vs. Exploratory

Because the 1.5B experiment evaluated 30 problems on Apple Silicon while the 7B experiment had only 1 complete four-condition problem block physically preserved on local disk:
1. **The comparison CANNOT be published as a fully controlled scaling experiment.**
2. In accordance with Phase 3 instructions:
   > *"If these conditions are not satisfied, describe the comparison as exploratory rather than a controlled scaling experiment."*
3. **Formal Classification**: The cross-scale comparison is formally designated as an **EXPLORATORY SCALING STUDY**.

---

## 3. Supported Exploratory Hypotheses

Subject to confirmation in a future full-cohort matched execution:
- **Hypothesis 1 (Zero Local Repair Emergence)**: Surgical local repair does not emerge spontaneously between 1.5B and 7B parameters; both models exhibit zero verified local repairs.
- **Hypothesis 2 (Scale Enhances Context Evacuation)**: Increasing model scale from 1.5B to 7B increases the model's propensity to detect and abandon corrupted context (implicit restart) rather than compounding the error into the final answer.
