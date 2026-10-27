# StateShift Research Mission 23 — Definitive Confirmatory Statistical Analysis Report

**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Target Publication:** NeurIPS 2027 Main Track (Preprint: arXiv, Secondary: TMLR)  
**Sample Specification:** $N = 231$ held-out MATH-500 problems ($4 \times 231 = 924$ genuine neural generations)  
**Hardware Target:** 1x physical NVIDIA GeForce RTX 4090 (RunPod Secure Cloud)  
**Evaluation Protocol:** Cleanroom mathematical extraction and SymPy evaluation (Path A strict degree matching)

---

## 1. Executive Statistical Verdict

| Empirical Metric | Confirmatory Result ($N=231$) | Pilot Benchmark ($N=100$) |
| :--- | :--- | :--- |
| **Condition F Accuracy (Continuation)** | **68.0%** | 73.0% |
| **Condition D Accuracy (Forced Restart)** | **68.4%** | 67.0% |
| **Observed Effect $\hat{\tau}_{F-D}$** | **-0.0043** (-0.43%) | +0.0600 (+6.00%) |
| **Paired Wald 95% CI** | **[-0.0450, +0.0364]** | [-0.0125, +0.1325] |
| **Exact Two-Sided McNemar $p$-value** | **$p = 1.000000$** | $p = 0.109375$ |
| **Statistical Decision ($\alpha=0.05$)** | **FAIL TO REJECT NULL** | FAIL TO REJECT NULL |

---

## 2. Primary 2x2 Paired Contingency Table (Condition F vs Condition D)

```
                            Condition F (Continuation)
                            Correct (+)      Incorrect (-)      Total
Condition D   Correct (+)       146          12           158     
(Restart)     Incorrect (-)     11           62           73      
              Total             157          74           231
```

- **Cell $a$ (Both Correct):** 146
- **Cell $b$ (D Incorrect, F Correct — Recovery Advantage):** 11
- **Cell $c$ (D Correct, F Incorrect — Restart Advantage):** 12
- **Cell $d$ (Both Incorrect):** 62
- **Discordant Pair Ratio ($b / c$):** 0.9167 (95% CI: [0.3665, 2.2693])

---

## 3. Secondary Hypothesis Contrasts (Holm-Bonferroni Corrected at $\alpha=0.05$)

| Contrast | Description | Accuracy 1 | Accuracy 2 | Effect $\hat{\tau}$ | Exact $p$ | Holm Threshold | Significant? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F vs A** | F vs A | 68.0% | 66.7% | +0.0130 | 0.735879 | 0.050000 | NO |
| **F vs E** | F vs E | 68.0% | 66.7% | +0.0130 | 0.677639 | 0.025000 | NO |
| **E vs D** | E vs D | 66.7% | 68.4% | -0.0173 | 0.596615 | 0.016667 | NO |
| **D vs A** | D vs A | 68.4% | 66.7% | +0.0173 | 0.541256 | 0.012500 | NO |

---

## 4. Headroom, Token Length, and Finish Reason Audit

| Condition | Description | Mean Tokens | Median Tokens | Std Tokens | Stop Finishes | Length Truncations | Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Condition A** | Standardized | 528.07 | 508.0 | 194.01 | 172 | 59 | 66.7% |
| **Condition D** | Standardized | 525.27 | 515.0 | 195.62 | 173 | 58 | 68.4% |
| **Condition E** | Standardized | 513.72 | 501.0 | 207.72 | 167 | 64 | 66.7% |
| **Condition F** | Standardized | 510.1 | 483.0 | 199.82 | 170 | 61 | 68.0% |

---

## 5. Subgroup Stratification by MATH-500 Difficulty Level

| Difficulty | Sample Size | F Acc | D Acc | $\hat{\tau}_{F-D}$ | Discordant ($b/c$) | Exact $p$-value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Level 1** | 47 | 63.8% | 66.0% | -0.0213 | 2/3 | 1.0000 |
| **Level 2** | 46 | 65.2% | 67.4% | -0.0217 | 1/2 | 1.0000 |
| **Level 3** | 46 | 80.4% | 73.9% | +0.0652 | 5/2 | 0.4531 |
| **Level 4** | 46 | 63.0% | 67.4% | -0.0435 | 1/3 | 0.6250 |
| **Level 5** | 46 | 67.4% | 67.4% | +0.0000 | 2/2 | 1.0000 |

---

## 6. Subgroup Stratification by Mathematical Subdiscipline

| Subject | Sample Size | F Acc | D Acc | $\hat{\tau}_{F-D}$ | Discordant ($b/c$) | Exact $p$-value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Algebra** | 59 | 86.4% | 84.8% | +0.0169 | 3/2 | 1.0000 |
| **Counting & Probability** | 17 | 58.8% | 58.8% | +0.0000 | 1/1 | 1.0000 |
| **Geometry** | 20 | 75.0% | 60.0% | +0.1500 | 3/0 | 0.2500 |
| **Intermediate Algebra** | 41 | 39.0% | 43.9% | -0.0488 | 1/3 | 0.6250 |
| **Number Theory** | 28 | 75.0% | 85.7% | -0.1071 | 0/3 | 0.2500 |
| **Prealgebra** | 42 | 81.0% | 85.7% | -0.0476 | 0/2 | 0.5000 |
| **Precalculus** | 24 | 41.7% | 33.3% | +0.0833 | 3/1 | 0.6250 |

---

## 7. Preregistration Fidelity & Causal Scope Compliance

1. **Preregistration Adherence:**
   - Sample size $N=231$ held-out problems strictly executed as preregistered.
   - Primary endpoint: Paired difference in accuracy between Condition F and Condition D.
   - Primary test: Exact two-sided McNemar test at $\alpha = 0.05$.
   - Missing data policy: Complete-case analysis verified (231/231 matched pairs).
2. **Causal Interpretation Boundary (Enforcing Major Issue M1):**
   - The primary contrast estimates the bundled effect of continuation (prompt context, continuation instruction, reasoning headroom) relative to forced restart.
   - It does not uniquely isolate internal neural state steering from prompt context preservation.
