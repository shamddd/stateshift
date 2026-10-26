# Phase D: Final Scientific Integrity Gate

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training
**Principal Investigator**: Sham Satish Thakare
**Date & Time**: 2026-10-26T17:20:00+05:30
**Repository**: `https://github.com/shamddd/stateshift`

---

## 1. Study 1: Checkpoint-Lineage Analysis Boundaries

- **Sample Size**: 454 paired GSM8K problem instances, 29,056 outcome-level binary records across 16 rollouts per cell.
- **Model Progression**: DeepScaleR-7B post-training trajectory (Steps 0, 32, 64, 96, 128, 160, 192, 224, 256).
- **Core Empirical Estimate**:
  - Step 0 Control: $38.92\%$, Step 0 Recovery: $38.34\%$ (Difference: $-0.58$ pp)
  - Step 256 Control: $59.21\%$, Step 256 Recovery: $70.39\%$ (Difference: $+11.18$ pp)
  - Difference-in-Differences interaction $\hat{\gamma}_{256} = +11.76$ percentage points ($t = 10.34, p < 0.001$).
- **Strict Integrity Disclosures**:
  - The repository, README, and manuscript clearly state that Study 1 is an **outcome-level** dataset.
  - Original raw token generations from the October 2024–2025 lineage runs were not retained; therefore, Study 1 is **not** presented as a generation-level reproducible study.

---

## 2. Study 2: Physical GPU Reasoning Recovery Validation

- **Hardware & Model**: 1 physical NVIDIA RTX 4090 on RunPod Secure Cloud; model **Qwen2.5-Math-7B-Instruct** (pinned Git commit revision `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`).
- **Sample**: 100 paired MATH500 problems across 4 conditions ($N = 400$ neural generations).
- **Condition Accuracies**:
  - Condition A (Zero-Shot Baseline): **64.00%** (64/100)
  - Condition D (No-Intervention Control): **67.00%** (67/100)
  - Condition E (Lemma Scaffold Control): **71.00%** (71/100)
  - Condition F (Full State Restoration): **73.00%** (73/100)
- **Primary Treatment Effect**:
  $$\hat{\tau}_{F-D} = 73.00\% - 67.00\% = +6.00\text{ percentage points}$$
- **Exact Statistical Inferences**:
  - Contingency matrix: $a=65$ (both pass), $b=8$ ($F$ passes, $D$ fails), $c=2$ ($D$ passes, $F$ fails), $d=25$ (both fail).
  - Off-diagonal odds ratio: $\hat{\theta} = \frac{b}{c} = \frac{8}{2} = 4.00$ ($4:1$ favorable recovery ratio).
  - Exact two-sided McNemar $p$-value:
    $$p = 2 \times \sum_{k=8}^{10} \binom{10}{k} 0.5^{10} = 2 \times \frac{45 + 10 + 1}{1024} = 2 \times \frac{56}{1024} = 0.109375$$
  - Under the preregistered two-sided $\alpha = 0.05$ threshold, the primary contrast is **not statistically significant** ($p = 0.1094 > 0.05$).
  - One-sided exploratory $p$-value: $p = 0.054688$.
  - Exact unconditional power of the $N = 100$ pilot test is **$36.20\%$** (Type II error rate $\beta = 63.80\%$).
- **Secondary Contrast**:
  - Baseline recovery contrast ($F - A = +9.00$ pp) is statistically significant: exact two-sided McNemar $p = 0.0117 < 0.05$ ($b=12, c=3$).

---

## 3. Claim Boundaries and Overclaim Scrubbing

1. **No Overclaiming**: The repository, README, and manuscript strictly adhere to the non-significant pilot result ($p = 0.109375$) for the primary treatment effect. Neither statistical significance nor guaranteed publication acceptance is asserted.
2. **Confirmatory Power Planning**: The manuscript and replication documentation report exact discrete sample size requirements for a future confirmatory trial ($N = 231$ for $80\%$ power; $N = 299$ for $90\%$ power under Scenario B).
3. **No Synthetic Author Signatures**: The author checklist in `docs/REPRODUCIBILITY.md` and release materials remains un-checked `[ ]` pending human Principal Investigator review.
4. **Internal Review Demarcation**: All internal peer review artifacts within `docs/internal_review/` carry mandatory disclaimers establishing that they represent automated internal audits rather than external peer review.

---

## 4. Final Scientific Integrity Gate Status

**Verdict**: **PASS** (Zero overclaims; exact two-sided $p = 0.109375$ reported transparently; sample size bounds verified; all scientific claim boundaries upheld).
