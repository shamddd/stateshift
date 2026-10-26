# StateShift: Research Mission 19 — Final Statistical Validation & Inference Audit

**Audit Date:** October 26, 2026  
**Auditor Committee:** Independent Scientific Review Panel (Statistical Methodology Directorate)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Preprint: arXiv)  
**Analysis Engine:** `research_mission_19/scripts/independent_final_statistics.py`  
**Data Artifact:** `research_mission_19/data/independent_final_statistics.json`  

---

## 1. Executive Statistical Verdict

The Statistical Methodology Directorate completed an exhaustive re-analysis of the paired inferential data across all four experimental conditions ($N=100$ matched problems).

**Methodological Summary:**
1. **Primary Contrast ($\hat{\tau}_{F-D} = +6.00\%$):**
   - Paired contingency counts: $a = 65, b = 8, c = 2, d = 25$ ($N = 100$, discordant $n_{\text{disc}} = 10$).
   - Exact two-sided McNemar $p$-value: **$p = 0.109375$**.
   - Exact one-sided McNemar $p$-value: **$p = 0.054688$**.
   - Paired sign-flip permutation test ($10,000$ iterations): **$p = 0.109900$**.
   - Asymptotic McNemar with Edwards continuity correction: $\chi^2 = 2.50, p = 0.113846$.
   - **Methodological Ruling:** Under standard two-sided Neyman-Pearson hypothesis testing at $\alpha = 0.05$, **$p = 0.1094 > 0.05$ fails to achieve statistical significance**.
   - Switching post-hoc to a one-sided test ($p = 0.0547$) to claim significance is statistically impermissible.
   - The result is an encouraging **positive directional trend** (discordant win-loss ratio $4:1$, odds ratio $4.00$, point estimate $+6.00\%$).
2. **Baseline Contrast ($\hat{\tau}_{F-A} = +9.00\%$):**
   - Paired contingency counts: $a = 63, b = 10, c = 1, d = 26$ ($n_{\text{disc}} = 11$).
   - Exact two-sided McNemar $p$-value: **$p = 0.011719$** ($p < 0.05$).
   - Survives Holm-Bonferroni family-wise error rate control ($p = 0.0117 < \alpha/3 = 0.0167$). State-preserving recovery significantly outperforms unassisted zero-shot reasoning.
3. **Secondary Contrast ($\hat{\tau}_{E-D} = +4.00\%$):**
   - Paired contingency counts: $a = 63, b = 8, c = 4, d = 25$ ($n_{\text{disc}} = 12$).
   - Exact two-sided McNemar $p$-value: **$p = 0.387695$** (non-significant).

---

## 2. Multi-Method Paired Confidence Interval Comparison

To eliminate method-selection bias, the committee evaluated six distinct confidence interval formulations for the primary estimand $\tau_{F-D}$:

| Estimation Method | Lower Bound (95%) | Upper Bound (95%) | Interval Width | Spans Zero? | Methodological Properties |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Percentile Bootstrap** ($B=10^4$) | **+0.00%** | **+12.00%** | 12.00 pp | Boundary at 0 | Simple empirical percentiles; subject to discrete boundary snapping on $N=100$. |
| **Basic Bootstrap** ($B=10^4$) | **-0.00%** | **+12.00%** | 12.00 pp | Boundary at 0 | Empirical pivotal inversion; agrees with percentile interval. |
| **BCa Bootstrap** ($B=10^4$) | **-1.00%** | **+12.00%** | 13.00 pp | **Yes** | Bias-corrected and accelerated; adjusts for skewness in discordant ratio. |
| **Newcombe Paired Score** | **-0.12%** | **+12.18%** | 12.30 pp | **Yes** | Recommended for paired proportions (Newcombe, 1998); strictly consistent with $p = 0.1094$. |
| **Agresti-Min Pseudo-Obs** | **-0.68%** | **+12.44%** | 13.12 pp | **Yes** | Adds pseudo-observations to off-diagonal cells; excellent coverage properties. |
| **Wald Asymptotic Interval** | **-0.09%** | **+12.09%** | 12.18 pp | **Yes** | Standard large-sample normal approximation based on empirical variance. |

**Key Methodological Finding:**
Every continuous confidence interval specifically derived for paired proportions (Newcombe Score: $[-0.12\%, +12.18\%]$; Agresti-Min: $[-0.68\%, +12.44\%]$; BCa: $[-1.00\%, +12.00\%]$) spans slightly below zero. This demonstrates complete mathematical consistency with the exact two-sided hypothesis test ($p = 0.1094$). The percentile bootstrap interval $[0.00\%, +12.00\%]$ landed at exactly zero due to integer rounding on $N=100$ problems.

---

## 3. Holm-Bonferroni Family-Wise Error Rate (FWER) Control

Evaluating the family of $m=3$ experimental hypotheses at nominal family-wise $\alpha = 0.05$:

| Rank ($k$) | Hypothesis Contrast | Observed Two-Sided $p$-value | Holm Threshold $\frac{\alpha}{m - k + 1}$ | FWER Statistical Decision |
| :---: | :--- | :---: | :---: | :---: |
| **1** | $H_3: \tau_{F-A} = 0$ (Baseline Recovery) | **0.011719** | $\frac{0.05}{3} \approx \mathbf{0.016667}$ | **REJECT $H_0$ (Confirmed Statistically Significant)** |
| **2** | $H_1: \tau_{F-D} = 0$ (Primary Estimand) | **0.109375** | $\frac{0.05}{2} = \mathbf{0.025000}$ | **FAIL TO REJECT $H_0$ (Not Significant)** |
| **3** | $H_2: \tau_{E-D} = 0$ (Secondary Contrast) | **0.387695** | $\frac{0.05}{1} = \mathbf{0.050000}$ | **FAIL TO REJECT $H_0$ (Not Significant)** |

**Conclusion on Multiplicity:**
The step-down procedure rejects $H_3$ at step 1 ($0.0117 < 0.0167$), establishing that Condition F provides statistically significant recovery over unassisted zero-shot reasoning. The testing sequence stops at step 2 because $p = 0.1094 > 0.0250$. Neither $\tau_{F-D}$ nor $\tau_{E-D}$ achieve family-wise statistical significance.
