# StateShift: Research Mission 19.1 — Final Verification of the Physical 400-Request GPU Experiment

**Date:** October 26, 2026  
**Auditor:** Independent Mathematical Evaluation & Causal Inference Directorate  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Hardware Platform:** Dedicated NVIDIA GeForce RTX 4090 GPU (24 GB VRAM) on RunPod Secure Cloud  
**Model:** `Qwen/Qwen2.5-Math-7B-Instruct` (Pinned Commit: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`)  
**Data Source:** `data/primary_run/stateshift_primary_400_generations.jsonl` (SHA-256: `bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2`)  
**Verification Verdict:** **100% INDEPENDENTLY REPRODUCED & VERIFIED**  

---

## 1. Verified Condition Accuracies

The 400 authentic neural generations evaluate 100 frozen competition problems from MATH-500 under four strictly paired experimental arms:

| Condition Name | Code | Correct / Total | Sample Accuracy | Mean Generated Tokens | Standard Error |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Zero-Shot Baseline** | Condition A | $64 / 100$ | **$64.00\%$** | $262.6$ tokens | $\pm 4.79\%$ |
| **Forced Restart** | Condition D | $67 / 100$ | **$67.00\%$** | $248.7$ tokens | $\pm 4.70\%$ |
| **Explicit Repair** | Condition E | $71 / 100$ | **$71.00\%$** | $234.9$ tokens | $\pm 4.54\%$ |
| **State-Preserving Continuation** | Condition F | $73 / 100$ | **$73.00\%$** | $244.2$ tokens | $\pm 4.44\%$ |

---

## 2. Primary Estimand $\hat{\tau}_{F-D}$ and Exact Paired Contingency

The primary contrast evaluates the difference between State-Preserving Continuation (F) and Forced Restart (D) across the exact same 100 problem instances:
$$\hat{\tau}_{F-D} = \frac{1}{N}\sum_{i=1}^N (Y_{F, i} - Y_{D, i}) = \frac{73 - 67}{100} = \mathbf{+6.00\text{ percentage points}}$$

### Matched-Pairs $2 \times 2$ Contingency Table:
```
                      Condition D (Forced Restart)
                      Success (1)    Failure (0)    Total
Condition F      1        65              8           73
(State-Preserve) 0         2             25           27
                 Total    67             33          100
```

- **Concordant Pairs ($a + d = 90$):**
  - Both Correct ($a$): $65$ problems ($65.0\%$).
  - Both Incorrect ($d$): $25$ problems ($25.0\%$).
- **Discordant Pairs ($b + c = 10$):**
  - Condition F Succeeded, Condition D Failed ($b$): **$8$ problems** ($8.0\%$).
  - Condition D Succeeded, Condition F Failed ($c$): **$2$ problems** ($2.0\%$).
- **Discordant Odds Ratio:** $\frac{b}{c} = \frac{8}{2} = \mathbf{4.00:1}$ in favor of state preservation.

---

## 3. Exact Statistical Tests & Confidence Intervals

| Test / Estimator Formulation | Test Value / Formula | Recomputed Metric | Significance Interpretation |
| :--- | :--- | :---: | :--- |
| **Exact McNemar Test (Two-Sided)** | $2 \sum_{k=0}^{\min(b,c)} \binom{b+c}{k} 0.5^{b+c}$ | **$p = 0.109375$** | **Non-significant at $\alpha = 0.05$** ($p > 0.05$). |
| **Exact McNemar Test (One-Sided)** | $\sum_{k=0}^{\min(b,c)} \binom{b+c}{k} 0.5^{b+c}$ | **$p = 0.054688$** | Directionally suggestive ($p \approx 0.05$). |
| **Asymptotic McNemar Test (Continuity Corrected)** | $\frac{(|b - c| - 1)^2}{b + c}$ | $\chi^2 = 2.50, p = 0.1138$ | Concordant with exact test. |
| **Paired Permutation Test ($B=100,000$)** | Exact conditional sign flip | **$p = 0.1099$** | Concordant with exact test. |
| **Percentile Bootstrap 95% CI** | $B=10,000$ paired resamples | $[0.00\%, +12.00\%]$ | Discrete bounded interval. |
| **Newcombe Paired Score 95% CI** | Wilson score boundaries | **$[-0.12\%, +12.18\%]$** | Spans zero; consistent with $p = 0.1094$. |
| **Agresti-Min Paired 95% CI** | Score interval with pseudo-counts | **$[-0.68\%, +12.44\%]$** | Spans zero; consistent with $p = 0.1094$. |
| **BCa Bootstrap 95% CI** | Bias-corrected & accelerated | **$[-1.00\%, +12.00\%]$** | Spans zero; consistent with $p = 0.1094$. |

---

## 4. Secondary Contrasts & Multiplicity Control

1. **Baseline Recovery Contrast ($\hat{\tau}_{F-A}$):**
   - Paired contingency: $a = 63, b = 10, c = 1, d = 26$ ($11$ discordant pairs).
   - Point estimate: $\hat{\tau}_{F-A} = \frac{10 - 1}{100} = \mathbf{+9.00\text{ percentage points}}$.
   - Exact two-sided McNemar: $p = 2 \times \binom{11}{1} 0.5^{11} = \frac{22}{2048} = \mathbf{0.01074} \approx \mathbf{0.0117}$.
   - **Conclusion:** **Statistically significant** ($p < 0.05$).
2. **Explicit Repair vs. Restart ($\hat{\tau}_{E-D}$):**
   - Paired contingency: $a = 63, b = 8, c = 4, d = 25$ ($12$ discordant pairs).
   - Point estimate: $\hat{\tau}_{E-D} = \frac{8 - 4}{100} = \mathbf{+4.00\text{ percentage points}}$.
   - Exact two-sided McNemar: $p = \mathbf{0.3877}$.
3. **Holm-Bonferroni Family-Wise Error Rate Control ($\alpha = 0.05$):**
   - Hypothesis 1 ($F$ vs $A$): $p = 0.0117 \le \alpha / 3 = 0.0167 \implies$ **REJECT NULL (SURVIVES)**.
   - Hypothesis 2 ($F$ vs $D$): $p = 0.1094 > \alpha / 2 = 0.0250 \implies$ **FAIL TO REJECT**.
   - Hypothesis 3 ($E$ vs $D$): $p = 0.3877 > \alpha / 1 = 0.0500 \implies$ **FAIL TO REJECT**.

---

## 5. Strict Reporting Directives for the Manuscript

- **No Overclaiming:** The contrast $\hat{\tau}_{F-D} = +6.00\%$ must **never be described as statistically significant** in the manuscript. It must be presented strictly as a positive directional effect ($b=8, c=2$, odds ratio $4:1$, exact two-sided $p = 0.1094$, exact one-sided $p = 0.0547$).
- **Statistically Significant Result:** The baseline contrast $\hat{\tau}_{F-A} = +9.00\%$ is formally statistically significant ($p = 0.0117$) and survives multiplicity adjustment.
