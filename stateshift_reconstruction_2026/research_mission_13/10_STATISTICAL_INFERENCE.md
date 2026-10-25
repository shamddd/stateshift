# StateShift Research Mission 13 — Deliverable 10: Statistical Inference Report

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Statistical Methodology**: Clustered Bootstrap, Exact Clopper-Pearson, McNemar Paired Test, and Two One-Sided Tests (TOST)  

---

## 1. Methodology & Formal Hypotheses

### Primary Equivalence Hypothesis:
$$H_0: |\mu_{\text{Acc}_F} - \mu_{\text{Acc}_D}| \ge \delta \quad \text{vs.} \quad H_1: |\mu_{\text{Acc}_F} - \mu_{\text{Acc}_D}| < \delta$$
Where $\delta = 0.05$ (5 percentage points equivalence margin).

### Secondary Null Hypothesis (Repair Feasibility):
$$H_0: p_{\text{repair}} = 0 \quad \text{vs.} \quad H_1: p_{\text{repair}} > 0$$

---

## 2. Statistical Results Summary Table

| Test | Contrast / Metric | Point Estimate | Test Statistic | p-value | Decision / Conclusion |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **McNemar Test** | Acc(D) vs. Acc(F) | $\Delta = -0.0286$ | $\chi^2 = 0.0000$ (Edwards) | $p = 1.000$ | Fail to reject null of equal marginals |
| **TOST Equivalence** | Acc(D) vs. Acc(F) ($\pm 5\%$) | $\Delta = -2.86\%$ | $t_{\text{lower}} = +0.335$ | $p = 0.370$ | **Inconclusive** (Cannot reject non-equivalence) |
| **Clopper-Pearson** | Genuine Repair Rate (Cond E) | $0 / 36 = 0.0\%$ | Exact Binomial | $\alpha=0.05$ | **$[0.0\%, 8.0\%]$** (Upper bound $\le 8.0\%$) |
| **Clopper-Pearson** | Genuine Repair Rate (Cond F) | $0 / 35 = 0.0\%$ | Exact Binomial | $\alpha=0.05$ | **$[0.0\%, 8.2\%]$** (Upper bound $\le 8.2\%$) |
| **Clopper-Pearson** | Combined Repair Rate (E + F) | $0 / 71 = 0.0\%$ | Exact Binomial | $\alpha=0.05$ | **$[0.0\%, 5.06\%]$** (Upper bound $\le 5.1\%$) |
| **Bootstrap 95% CI** | Acc Difference ($\text{Acc}_F - \text{Acc}_D$) | $-2.86\%$ | 10,000 resamples | — | **$[-17.1\%, +11.4\%]$** |
| **Bootstrap 95% CI** | Token Difference ($\text{Tok}_D - \text{Tok}_F$) | $+13.2\text{ tok}$ | 10,000 resamples | — | **$[-11.4, +37.8]\text{ tok}$** |
| **Paired t-test** | Token Count (D vs. F) | $+13.2\text{ tok}$ | $t = 1.052, \text{df}=34$ | $p = 0.299$ | No statistically significant difference |

---

## 3. Methodological Rigor: Avoiding Negative Falsification Pitfalls

In strict accordance with TMLR and NeurIPS statistical guidelines:
1. **Absence of Evidence is Not Evidence of Absence**: We do NOT claim that Condition D and Condition F are "statistically equivalent" merely because the p-value is non-significant ($p = 1.000$). Instead, our formal TOST test reveals that with 35 matched pairs, the confidence interval $[-17.1\%, +11.4\%]$ extends beyond the $\pm 5\%$ margin, correctly reporting the equivalence test as **inconclusive** at current sample size.
2. **Zero-Event Binomial Bounding**: Because zero repairs were observed ($0/71$), computing normal-approximation standard errors is invalid ($\sqrt{p(1-p)/n} = 0$). We correctly report the exact Clopper-Pearson 95% upper confidence bound of **$5.06\%$**. We state with 95% confidence that the true underlying local repair rate on MATH-500 is strictly below $5.1\%$.
