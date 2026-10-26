# StateShift: Statistical Validity & Preregistration Protocol
## Deliverable 05 — Rigorous Calibration Estimation, Matched Contrasts & Primary Analysis Specification
**Document Version:** 1.0.0  
**Audit Date:** 2026-10-26  
**Principal Investigator:** Sham Satish Thakare  
**Target Venue:** NeurIPS 2027 Main Conference (Secondary: TMLR)  

---

## 1. Audit of Calibration Accuracy & Denominator Rectification

The calibration run comprises exactly 10 requests distributed across 3 distinct problems:
* `math500_001`: Evaluated under Conditions A, D, E, F (4 requests).
* `math500_012`: Evaluated under Conditions A, D, E, F (4 requests).
* `math500_023`: Evaluated under Conditions A, D only (2 requests).

### 1.1 Unmatched Aggregate Accuracies (Full Calibration Set)

| Condition | Sampled Problems | Raw Correct / Total | Sample Accuracy | 95% Wilson Score Interval |
| :--- | :--- | :---: | :---: | :---: |
| **Condition A (Zero-Shot)** | `001, 012, 023` | 2 / 3 | **66.67%** | $[20.77\%, 93.85\%]$ |
| **Condition D (Forced Restart)**| `001, 012, 023` | 2 / 3 | **66.67%** | $[20.77\%, 93.85\%]$ |
| **Condition E (Explicit Repair)**| `001, 012` | 2 / 2 | **100.00%** | $[34.24\%, 100.00\%]$ |
| **Condition F (State-Preserving)**| `001, 012` | 2 / 2 | **100.00%** | $[34.24\%, 100.00\%]$ |

> **Critical Statistical Invariant:**  
> Directly subtracting $66.67\%$ from $100.00\%$ to claim a $+33.33\text{ pp}$ treatment effect is **statistically invalid**. The sets of evaluated problems are unmatched: Conditions A and D include `math500_023`, while Conditions E and F do not. Valid causal contrasts require matched problem subsets.

---

### 1.2 Matched Within-Problem Contrasts ($N=2$ Problems: `001` and `012`)

Restricting the analysis to the subset of problems where all four conditions were observed:

| Condition | Matched Problems | Matched Correct / Total | Matched Accuracy | Contrast vs Baseline A | Contrast vs Restart D |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Condition A** | `001, 012` | 1 / 2 | **50.00%** | Baseline ($0.00\text{ pp}$) | $0.00\text{ pp}$ |
| **Condition D** | `001, 012` | 1 / 2 | **50.00%** | $0.00\text{ pp}$ | Baseline ($0.00\text{ pp}$) |
| **Condition E** | `001, 012` | 2 / 2 | **100.00%** | $\mathbf{+50.00\text{ pp}}$ | $\mathbf{+50.00\text{ pp}}$ |
| **Condition F** | `001, 012` | 2 / 2 | **100.00%** | $\mathbf{+50.00\text{ pp}}$ | $\mathbf{+50.00\text{ pp}}$ |

### 1.3 Statistical Significance & Uncertainty Warning
With only $N=2$ matched tasks:
* Exact McNemar Test: Contingency table has $b = 1$ (discordant pair: F=1, D=0) and $c = 0$ (F=0, D=1).
  $$\text{Two-sided Binomial } p\text{-value} = 2 \times (0.5)^1 = \mathbf{1.000}$$
* **Conclusion:** The calibration difference is **statistically non-significant** ($p = 1.000$). The small calibration cohort serves solely for systems engineering and verification, not for hypothesis confirmation.

---

## 2. Formal Statistical Preregistration for the 400-Request Primary Experiment

To guarantee publication-grade methodological rigor for NeurIPS 2027, the following statistical analysis plan is preregistered prior to executing the 400-request primary experiment:

### 2.1 Primary Estimand & Estimator
The primary estimand is the **Average Treatment Effect of State Preservation over Forced Restart**:
$$\tau_{\text{StateShift}} = \mathbb{E}\left[ Y_i(F) - Y_i(D) \right]$$
where $Y_i(c) \in \{0, 1\}$ denotes binary correctness of model generation on problem $i \in \{1, \dots, 100\}$ under condition $c \in \{A, D, E, F\}$.

The sample estimator is the paired difference in sample proportions:
$$\hat{\tau} = \hat{\mu}_F - \hat{\mu}_D = \frac{1}{N}\sum_{i=1}^N \left( Y_{i, F} - Y_{i, D} \right)$$

### 2.2 Statistical Inference & Hypothesis Testing
1. **Primary Hypothesis Test:** Exact McNemar's test on the $2 \times 2$ paired contingency table:
   $$H_0: P(Y_F = 1, Y_D = 0) = P(Y_F = 0, Y_D = 1) \quad \text{vs} \quad H_1: P(Y_F = 1, Y_D = 0) \ne P(Y_F = 0, Y_D = 1)$$
2. **Confidence Intervals:** Non-parametric problem-blocked bootstrap confidence intervals computed across $B = 10,000$ resamples (percentile and BCa intervals reported at $\alpha = 0.05$).
3. **Continuous Variance Decomposition:** Paired permutation tests ($100,000$ iterations) to evaluate robustness against distributional assumptions.

### 2.3 Multiple Comparison Corrections
The primary confirmatory family consists of three hypothesis tests:
1. $H_{0, 1}: \mu_F = \mu_D$ (Primary research question).
2. $H_{0, 2}: \mu_E = \mu_D$ (Effect of explicit feedback vs restart).
3. $H_{0, 3}: \mu_F = \mu_A$ (Effect of state preservation vs zero-shot).

Family-Wise Error Rate (FWER) will be strictly controlled at $\alpha = 0.05$ using the Holm-Bonferroni step-down procedure:
* Sort $p$-values: $p_{(1)} \le p_{(2)} \le p_{(3)}$.
* Reject $H_{0, (k)}$ if $p_{(k)} \le \frac{\alpha}{m - k + 1}$.

Secondary exploratory analyses across mathematical subdisciplines (Algebra, Number Theory, Geometry, Precalculus) will be controlled using the Benjamini-Hochberg False Discovery Rate (FDR) at $q = 0.05$.

### 2.4 Missing Data & Interrupted Run Rules
* **Intention-to-Treat (ITT) Rule:** Any request in the 400-request manifest that fails to produce a valid, parseable output (due to engine crashes, provider drops, or context exhaustion) is coded as $Y_{i, c} = 0$ in the primary ITT analysis.
* **Sensitivity Analysis:** A secondary Per-Protocol (PP) complete-case analysis will be reported alongside ITT to verify robustness.

### 2.5 Failure-Mode Qualitative Taxonomy
Every failed generation ($Y = 0$) will be independently categorized into:
1. **Attractor Trapping:** Model repeats an earlier failure path or outline heading circularly (as seen in `math500_012`).
2. **Extraneous Root Inclusion:** Model fails to check boundary constraints or domain conditions (e.g., radical/logarithmic equations).
3. **Arithmetic / Calculation Slip:** Reasoning structure is valid, but an arithmetic operation is incorrect.
4. **Structural Hallucination:** Model introduces non-existent mathematical theorems or ungrounded claims.
