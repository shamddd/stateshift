# StateShift: Experimental Data Registry & Provenance Guide

This directory houses the empirical data supporting the two investigations reported in Project StateShift.

---

## 1. Directory Structure

```text
data/
├── README.md                                  # This document
├── study1/
│   └── controlled_endpoint_outcomes.csv       # Study 1: DeepScaleR checkpoint lineage (29,056 rows)
└── study2/
    ├── stateshift_primary_400_generations.jsonl # Study 2: Raw Qwen2.5-Math-7B generations (400 records)
    └── final_verified_outcomes.csv             # Study 2: Verified outcome matrix (100 problem pairs)
```

---

## 2. Study 1: Historical Checkpoint-Lineage Dataset

* **File**: `data/study1/controlled_endpoint_outcomes.csv`
* **File Size**: $1,617,543\text{ bytes}$
* **SHA-256**: `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139`
* **Total Rows**: Exactly $29,056$ rows (excluding header)
* **Sample Scope**: $N = 454$ mathematical problem pairs evaluated across Step 0 (base) and Step 256 (RL post-trained) under `control` and `recovery` states (32 rollouts per cell).
* **Provenance Tier**: **Tier 2 (Outcome-Level Reproduction)**.
* **Limitation Disclosure**: Tabular outcomes, token lengths, transition labels, and statistical aggregations ($\Gamma_{256} = +11.76\text{ pp}$, $p = 1.05 \times 10^{-22}$) are 100% mathematically reproducible from this file. However, original raw text generations for the 29,056 rollouts are not stored in this repository.

---

## 3. Study 2: Physical GPU Reasoning-Recovery Dataset

### 3.1 Raw Neural Generations
* **File**: `data/study2/stateshift_primary_400_generations.jsonl`
* **File Size**: $741,452\text{ bytes}$
* **SHA-256**: `bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2`
* **Generation Count**: Exactly 400 complete, authentic neural generation records.
* **Hardware Execution**: Physical NVIDIA RTX 4090 GPU ($24\text{ GB}$ VRAM) on RunPod Secure Cloud.
* **Model**: `Qwen/Qwen2.5-Math-7B-Instruct` (pinned revision: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`).
* **Inference Settings**: Temperature = 0.0, Top-p = 1.0, Max New Tokens = 768, Seed = 42.
* **Provenance Tier**: **Tier 1 (Generation-Level Execution)**. Includes complete input prompts, generated completions, stop reasons, and token counts.

### 3.2 Verified Evaluation Matrix
* **File**: `data/study2/final_verified_outcomes.csv`
* **File Size**: $11,048\text{ bytes}$
* **SHA-256**: `19a328a95dd25ec326fe824361386cc0ddf731f2bf1c392253be0aa19c2385ba`
* **Sample Scope**: $N = 100$ MATH-500 problem pairs across 4 prompt conditions:
  * Condition A (Zero-Shot Baseline): $64.0\%$ accuracy ($64/100$)
  * Condition D (No-Intervention Control): $67.0\%$ accuracy ($67/100$)
  * Condition E (Lemma Generation Control): $71.0\%$ accuracy ($71/100$)
  * Condition F (Full State Restoration): $73.0\%$ accuracy ($73/100$)
* **Exact McNemar Inference ($F$ vs $D$)**:
  * Contingency: $a=65, b=8, c=2, d=25$
  * Off-diagonal odds ratio: $4:1$
  * Exact two-sided $p = 0.109375$ (not significant at $\alpha = 0.05$)
  * Exact one-sided $p = 0.054688$
  * Baseline recovery contrast ($F$ vs $A$): $+9.00\%$ ($p = 0.0117$, statistically significant)
