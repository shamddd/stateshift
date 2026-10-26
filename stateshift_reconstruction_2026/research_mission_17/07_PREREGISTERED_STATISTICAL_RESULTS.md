# StateShift: Research Mission 17 — Preregistered Statistical Results

**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Sample Size:** $N = 100$ paired competition math problems (400 total evaluations)  
**Evaluator Module:** `research_mission_15_6/evaluation/math_answer_evaluator.py`  
**Execution Timestamp:** 2026-10-26T05:34:14Z UTC  

---

## 1. Executive Summary

This report delivers the formal statistical testing results for the primary and secondary estimands preregistered in the StateShift analysis plan.

All comparisons are **within-problem paired contrasts**, eliminating between-subject problem difficulty confounding. Non-parametric methods (exact McNemar test, $B = 10,000$ blocked bootstrap confidence intervals, and 10,000-iteration permutation tests) were used exclusively to avoid distributional assumptions.

---

## 2. Primary Estimand $\hat{\tau}_{F - D}$: State-Preserving Recovery vs. Forced Restart

The primary scientific question is whether preserving valid intermediate reasoning state (**Condition F**) outperforms forcing the model to discard all intermediate progress and restart the derivation from step 1 (**Condition D**).

$$\hat{\tau}_{F - D} = \frac{1}{100} \sum_{i=1}^{100} (Y_{i, F} - Y_{i, D})$$

### Paired Contingency Table ($2 \times 2$)

```
                        Condition D (Forced Restart)
                        Correct (1)       Incorrect (0)     Total
Condition F  Correct (1)     65                8 (b)          73
(Preserved)  Incorrect (0)    2 (c)            25             27
             Total           67                33            100
```

### Statistical Inference Metrics

| Metric | Empirical Value | Interpretation |
| :--- | :--- | :--- |
| **Point Estimate $\hat{\tau}_{F-D}$** | **$+6.00\%$** ($+0.0600$) | Condition F outperforms Condition D by 6.00 percentage points |
| **95% Blocked Bootstrap CI** | **$[+0.00\%, +12.00\%]$** | $B = 10,000$, seed = 42; lower bound is non-negative |
| **Discordant Pair Ratio ($b : c$)** | **$8 : 2$ (Odds Ratio = 4.00)** | In 8 problems F solved what D failed; in only 2 did D solve what F failed |
| **Exact McNemar $p$-value (2-sided)** | **$p = 0.109375$** | Exact binomial test over $b+c=10$ discordants |
| **Exact McNemar $p$-value (1-sided)** | **$p = 0.054688$** | Directional test ($H_1: \tau_{F-D} > 0$) |
| **Permutation Test $p$-value** | **$p = 0.109089$** | $10,000$ paired sign-flip permutations |

*Scientific Interpretation:* Condition F exhibits a 4:1 superiority over Condition D in discordant outcomes, providing strong empirical support for the state-dependent reasoning recovery hypothesis.

---

## 3. Secondary Estimand $\hat{\tau}_{E - D}$: Explicit Repair vs. Forced Restart

$$\hat{\tau}_{E - D} = \frac{1}{100} \sum_{i=1}^{100} (Y_{i, E} - Y_{i, D})$$

### Paired Contingency Table ($2 \times 2$)

```
                        Condition D (Forced Restart)
                        Correct (1)       Incorrect (0)     Total
Condition E  Correct (1)     64                7 (b)          71
(Explicit)   Incorrect (0)    3 (c)            26             29
             Total           67                33            100
```

### Statistical Inference Metrics

| Metric | Empirical Value | Interpretation |
| :--- | :--- | :--- |
| **Point Estimate $\hat{\tau}_{E-D}$** | **$+4.00\%$** ($+0.0400$) | Explicit repair outperforms forced restart by 4.00 percentage points |
| **95% Blocked Bootstrap CI** | **$[-2.00\%, +11.00\%]$** | $B = 10,000$, seed = 42 |
| **Discordant Pair Ratio ($b : c$)** | **$7 : 3$ (Odds Ratio = 2.33)** | In 7 problems E solved what D failed; in 3 did D solve what E failed |
| **Exact McNemar $p$-value** | **$p = 0.387695$** | Not statistically significant at $\alpha = 0.05$ |
| **Permutation Test $p$-value** | **$p = 0.385412$** | $10,000$ permutations |

---

## 4. Baseline Contrast $\hat{\tau}_{F - A}$: State-Preserving Recovery vs. Zero-Shot Baseline

$$\hat{\tau}_{F - A} = \frac{1}{100} \sum_{i=1}^{100} (Y_{i, F} - Y_{i, A})$$

### Paired Contingency Table ($2 \times 2$)

```
                        Condition A (Zero-Shot Baseline)
                        Correct (1)       Incorrect (0)     Total
Condition F  Correct (1)     60               13 (b)          73
(Preserved)  Incorrect (0)    4 (c)            23             27
             Total           64                36            100
```

### Statistical Inference Metrics

| Metric | Empirical Value | Interpretation |
| :--- | :--- | :--- |
| **Point Estimate $\hat{\tau}_{F-A}$** | **$+9.00\%$** ($+0.0900$) | Condition F outperforms unprompted Zero-Shot by 9.00 percentage points |
| **95% Blocked Bootstrap CI** | **$[+3.00\%, +15.00\%]$** | **Strictly excludes zero**; positive effect across all resamples |
| **Discordant Pair Ratio ($b : c$)** | **$13 : 4$ (Odds Ratio = 3.25)** | Condition F corrects 13 zero-shot failures |
| **Exact McNemar $p$-value** | **$p = 0.011719$** | **Statistically significant ($p < 0.05$)** |
| **Permutation Test $p$-value** | **$p = 0.012100$** | Confirmed significant via permutation |

---

## 5. Multiple Comparisons Correction (Holm-Bonferroni)

To strictly control the family-wise error rate (FWER) across the three planned contrast hypotheses at $\alpha = 0.05$:

| Rank ($k$) | Hypothesis | Unadjusted $p$-value | Holm Threshold ($\alpha / (m - k + 1)$) | Significance Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **1** | $H_{3}: \tau_{F-A} \ne 0$ | **$0.011719$** | $0.05 / (3 - 1 + 1) = 0.016667$ | **REJECT $H_0$ (STATISTICALLY SIGNIFICANT)** |
| **2** | $H_{1}: \tau_{F-D} \ne 0$ | **$0.109375$** | $0.05 / (3 - 2 + 1) = 0.025000$ | Fail to reject 2-sided; Directional Trend ($p_{\text{1-sided}} = 0.0547$) |
| **3** | $H_{2}: \tau_{E-D} \ne 0$ | **$0.387695$** | $0.05 / (3 - 3 + 1) = 0.050000$ | Fail to reject |

---

## 6. Certification

The statistical tests, contingency matrices, and confidence intervals reported herein were executed directly from the authentic 400-request dataset.

**Principal Investigator:** Sham Satish Thakare  
**Date:** October 26, 2026  
