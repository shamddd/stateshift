# Study 2: Physical GPU Reasoning-Recovery Protocol & Replication

This directory contains reproduction code for **Study 2**, evaluating the primary 400-request reasoning-recovery experiment executed on physical NVIDIA RTX 4090 hardware on RunPod Secure Cloud.

---

## 1. Experimental Overview

* **Target Model**: `Qwen/Qwen2.5-Math-7B-Instruct` (pinned revision: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`).
* **Evaluation Benchmark**: MATH-500 ($N = 100$ problems).
* **Experimental Conditions**:
  * **Condition A (Zero-Shot Baseline)**: Unscaffolded prompt ($64.0\%$ accuracy).
  * **Condition D (No-Intervention Control)**: Truncated chain without scaffold ($67.0\%$ accuracy).
  * **Condition E (Lemma Scaffold Control)**: Truncated chain + lemma anchors ($71.0\%$ accuracy).
  * **Condition F (Full State Restoration)**: Truncated chain + full state restoration ($73.0\%$ accuracy).
* **Data Provenance**: **Tier 1 (Generation-Level Execution)**. 400 authentic neural generations preserved in `data/study2/stateshift_primary_400_generations.jsonl`. Verified outcomes preserved in `data/study2/final_verified_outcomes.csv`.

---

## 2. Replication Commands

### 2.1 Empirical Accuracies & Exact McNemar Test
To reproduce the empirical accuracies, off-diagonal odds ratio, and exact discrete binomial McNemar p-values:

```bash
python experiments/study2_reasoning_recovery/reproduce_study2.py
```

### Expected Output Summary:
* Condition A: $64.00\%$ ($64/100$)
* Condition D: $67.00\%$ ($67/100$)
* Condition E: $71.00\%$ ($71/100$)
* Condition F: $73.00\%$ ($73/100$)
* **Primary Contrast ($\hat{\tau}_{F-D}$)**: $+6.00\text{ percentage points}$
* **Paired Contingency Matrix**: $a=65, b=8, c=2, d=25$
* **Off-Diagonal Odds Ratio**: $4:1$ ($b/c = 4.00$)
* **Exact McNemar Two-Sided p-value**: $0.109375$ (Under $\alpha=0.05$, not statistically significant)
* **Exact McNemar One-Sided p-value**: $0.054688$
* **Baseline Contrast ($\hat{\tau}_{F-A}$)**: $+9.00\text{ percentage points}$ ($p = 0.0117$, significant)

---

### 2.2 Exact Discrete Power & Sample Size Determination
To reproduce the unconditional discrete power modeling and sensitivity grid without asymptotic normal approximations:

```bash
python experiments/study2_reasoning_recovery/exact_power_analysis.py
```

### Expected Output Summary:
* Pilot Unconditional Power at $N=100$: **$36.20\%$** (Type II error rate $\beta = 63.80\%$)
* Required Sample Size for $80\%$ Power: **$N = 231$** ($80.07\%$)
* Required Sample Size for $90\%$ Power: **$N = 299$** ($90.02\%$)
* Winner's Curse Shrinkage (to $+5.0\%$ at $q=0.10$): **$N = 337$** for $80\%$ power.
