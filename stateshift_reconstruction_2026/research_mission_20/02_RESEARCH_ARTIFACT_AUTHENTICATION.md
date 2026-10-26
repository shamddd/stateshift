# StateShift: Research Mission 20 — Research Artifact Authentication Report

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training
**Date**: October 26, 2026
**Repository**: `https://github.com/shamddd/stateshift`

---

## 1. Executive Summary

This authentication audit independently verifies every experimental dataset and empirical artifact in Project StateShift. The empirical basis of the research is cleanly separated into two distinct scientific investigations with strictly bounded data provenance:
1. **Study 1 (Historical Checkpoint Lineage)**: An exploratory investigation across DeepScaleR-7B post-training checkpoints ($N=454$ problem pairs, $29,056$ outcome-level evaluations). Verified as **Tier 2 (Outcome-Level Dataset)**.
2. **Study 2 (Physical GPU Reasoning Recovery)**: A pre-registered prompt-scaffolding experiment on `Qwen/Qwen2.5-Math-7B-Instruct` executed on an NVIDIA RTX 4090 ($N=100$ problems, 400 prompt-controlled generations). Verified as **Tier 1 (Generation-Level Dataset)**.

---

## 2. Study 1: Historical Checkpoint-Lineage Authentication

### 2.1 File Integrity & Metadata
* **Canonical Path**: `artifacts/endpoint/controlled_endpoint_outcomes.csv` (and mirrored in `data/study1/controlled_endpoint_outcomes.csv`)
* **SHA-256 Checksum**: `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139`
* **File Size**: $1,617,543\text{ bytes}$
* **Row Count**: Exactly $29,056$ rows (excluding header)
* **Columns**: `rollout_id`, `pair_id`, `state_type`, `checkpoint_t`, `rollout_k`, `target_transition_success`, `generated_token_count`
* **Missing / Null Values**: Exactly $0$ missing values across all columns
* **Unique Problem Pairs ($N$)**: $454$ unique mathematical problem pairs
* **Checkpoints Evaluated**: Step $0$ (base) vs. Step $256$ (post-trained)
* **Experimental Conditions**: `control` vs. `recovery` ($32$ rollouts per condition per checkpoint per problem pair)

### 2.2 Statistical Reproduction
* **Step-256 Recovery Interaction**: $\Gamma_{256} = +11.76\text{ percentage points}$ ($p = 1.05 \times 10^{-22}$, clustered $SE = 0.0114$, $t = 10.34$).
* **Strict Decontamination Subset ($N=388$)**: $\Gamma_{\text{Strict}} = +11.60\text{ pp}$, bootstrap $95\%$ CI $[+9.61, +13.96]\text{ pp}$.
* **TOST Generation Length Invariance**: $\Delta = +0.02$ tokens ($p = 0.0256$), establishing that recovery gains are not confounded by generation verbosity.

### 2.3 Critical Provenance Boundary (Tier 2 Classification)
* **Status**: Tier 2 (Outcome-Level Reproduction).
* **Limitation**: While all tabular labels, token lengths, transition outcomes, and statistical aggregations are 100% reproducible from disk, the raw text completions for the historical 29,056 rollouts were not stored in this repository.
* **Integrity Mandate**: The manuscript and public documentation strictly disclose this limitation, avoiding any claim of full text generation reconstruction for Study 1.

---

## 3. Study 2: Physical GPU Reasoning-Recovery Authentication

### 3.1 Raw Generation Ledger (Tier 1 Execution)
* **Canonical Path**: `data/primary_run/stateshift_primary_400_generations.jsonl` (and mirrored in `data/study2/stateshift_primary_400_generations.jsonl`)
* **SHA-256 Checksum**: `bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2`
* **Generation Count**: Exactly 400 complete, authentic neural completions
* **Hardware Execution**: RunPod Secure Cloud NVIDIA RTX 4090 ($24\text{ GB}$ VRAM)
* **Model**: `Qwen/Qwen2.5-Math-7B-Instruct` (pinned revision: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`)
* **Inference Parameters**: Temperature = 0.0, Top-p = 1.0, Max New Tokens = 768, Seed = 42

### 3.2 Evaluation Matrix & Accuracy
* **Canonical Path**: `stateshift_reconstruction_2026/research_mission_19/data/final_verified_outcomes.csv`
* **Sample Size**: $N = 100$ MATH-500 problem pairs across 4 prompt conditions:

| Experimental Condition | Description | Successes / Total | Verified Accuracy |
| :--- | :--- | :---: | :---: |
| **Condition A** | Zero-Shot Direct Problem Prompt | $64 / 100$ | **$64.0\%$** |
| **Condition D** | Truncated Reasoning Chain (No Intervention) | $67 / 100$ | **$67.0\%$** |
| **Condition E** | Truncated Chain + Intermediate Lemmas Only | $71 / 100$ | **$71.0\%$** |
| **Condition F** | Full State Restoration Scaffold | $73 / 100$ | **$73.0\%$** |

### 3.3 Paired Contingency & McNemar Inference
* **Primary Contrast**: $\hat{\tau}_{F-D} = \text{Acc}(F) - \text{Acc}(D) = 73.0\% - 67.0\% = +6.00\text{ percentage points}$.
* **$2 \times 2$ Contingency Matrix ($F$ vs $D$)**:
  * $a$ (Both Correct): $65$
  * $b$ ($F$ Correct, $D$ Incorrect): $8$
  * $c$ ($D$ Correct, $F$ Incorrect): $2$
  * $d$ (Both Incorrect): $25$
* **Off-Diagonal Recovery Odds Ratio**: $b / c = 8 / 2 = 4.00$ ($4:1$ favorable recovery ratio).
* **Exact Discrete McNemar Significance**:
  * Two-sided test: $p = 2 \times \sum_{k=0}^{2} \binom{10}{k} 0.5^{10} = \frac{112}{1024} = \mathbf{0.109375}$
  * One-sided test ($H_1: p_b > p_c$): $p = \sum_{k=0}^{2} \binom{10}{k} 0.5^{10} = \frac{56}{1024} = \mathbf{0.054688}$
* **Baseline Contrast**: $\hat{\tau}_{F-A} = 73.0\% - 64.0\% = +9.00\text{ percentage points}$ ($p = 0.0117$, statistically significant at $\alpha = 0.05$).

---

## 4. Synthesis of Artifact Verification

Both studies have been 100% verified against raw bytes on disk:
1. No synthetic or interpolated values are present.
2. Exact discrete statistical properties match the mathematical preregistration.
3. Provenance boundaries between Tier 2 (Study 1) and Tier 1 (Study 2) are formally maintained.
