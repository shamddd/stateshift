# Research Mission 15: Corrected Statistical Pre-Registration

**Principal Investigator**: Sham Satish Thakare  
**Repository**: `github.com/shamddd/stateshift`  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15/07_CORRECTED_STATISTICAL_PREREGISTRATION.md`  
**Status**: Formal Statistical Pre-Registration (Frozen Before Execution)  
**Date**: October 25, 2026  
**Auditor**: Independent Statistical Methodologist & Biostatistician  

---

## 1. Objective and Anti-Bias Commitment

Previous missions exhibited "outcome bias," framing hypothesis tests to validate predetermined conclusions (e.g. attempting to prove that StateShift post-training *enables* local repair).

In this pre-registration, all hypotheses and estimands are framed **neutrally**. The objective is strictly to measure the true empirical behavior of `Qwen2.5-Math-7B-Instruct` when confronted with state corruption, whether the model successfully performs local repair or universally relies on implicit restarts.

---

## 2. Experimental Design and Cohort Specification

- **Design**: Repeated-measures $100 \times 4$ balanced factorial design.
- **Population**: $N = 100$ mathematical reasoning problems from MATH-500 test split across 7 mathematics domains.
- **Factorial Conditions ($k = 4$)**:
  1. $A$: Clean Zero-Shot Baseline ($n = 100$)
  2. $D$: Forced Discard and Restart ($n = 100$)
  3. $E$: Explicit Local Repair Instruction ($n = 100$)
  4. $F$: Neutral Continuation / State-Preserving ($n = 100$)
- **Total Sample Size**: $N_{\text{total}} = 400$ generation requests.
- **Inference Parameters**: Locked to Greedy Decoding (`temperature = 0.0`, `seed = 42`, `max_tokens = 768`).

---

## 3. Primary Neutral Estimands

### Estimand 1: Frequency of Genuine Local Repair ($\theta_{\text{repair}}$)
- **Definition**: The proportion of rollouts in Condition E and Condition F meeting all formal predicates of Strategy S1:
  $$\theta_{\text{repair}}^{(E)} = \frac{1}{100} \sum_{i=1}^{100} \mathbb{I}(\text{Strategy}(i, E) = \text{S1}), \quad \theta_{\text{repair}}^{(F)} = \frac{1}{100} \sum_{i=1}^{100} \mathbb{I}(\text{Strategy}(i, F) = \text{S1})$$
- **Inference**: Reported with 95% Wilson score confidence intervals. If $\theta_{\text{repair}} = 0.0$, the exact upper 95% Rule of Three bound is reported: $\theta \le \frac{3}{100} = 0.030$ (3.0%).

### Estimand 2: Empirical Strategy Distribution Matrix
- **Definition**: The $4 \times 10$ categorical probability matrix representing the distribution over strategies $\{S1, \dots, S10\}$ across conditions $\{A, D, E, F\}$.
- **Statistical Test**: Chi-square test of homogeneity across conditions ($\alpha = 0.05$) to test whether prompt framing alters strategy distribution.

### Estimand 3: Paired Accuracy Differences ($\Delta$)
- **Definition**:
  $$\Delta_{E-A} = \text{Acc}(E) - \text{Acc}(A), \quad \Delta_{F-A} = \text{Acc}(F) - \text{Acc}(A), \quad \Delta_{E-D} = \text{Acc}(E) - \text{Acc}(D)$$
- **Statistical Test**: McNemar’s exact test on paired $2 \times 2$ contingency tables for each problem $i \in [1, 100]$.
- **Confidence Intervals**: 95% bootstrap confidence intervals (10,000 resamples with replacement).

### Estimand 4: Token Efficiency Ratio ($R_{\text{eff}}$)
- **Definition**: The ratio of average generated tokens per correct solution:
  $$R_{\text{eff}} = \frac{\bar{T}_E}{\bar{T}_D}$$
  Where $\bar{T}_C = \frac{1}{|K_C|} \sum_{i \in K_C} \text{tokens}(i, C)$, with $K_C$ denoting the subset of correctly solved problems in condition $C$.

### Estimand 5: Dependency Contamination Impact on Error Continuation
- **Definition**: Logistic regression modeling the log-odds of error continuation ($S4$) as a function of causal graph contamination fraction $C_f$:
  $$\text{logit}(P(S4 \mid C_f, d, k)) = \beta_0 + \beta_1 C_f + \beta_2 d + \beta_3 k$$
  Where $C_f$ is the downstream contamination fraction, $d$ is dependency depth, and $k$ is corruption injection index.
- **Null Hypothesis**: $H_0: \beta_1 = 0$ (Contamination fraction has no association with error continuation).

---

## 4. Multiple Testing Correction

To strictly control the Family-Wise Error Rate (FWER) across the family of primary hypothesis tests at $\alpha_{\text{family}} = 0.05$, we apply the **Holm-Bonferroni step-down procedure**:
1. Rank $p$-values in ascending order: $p_{(1)} \le p_{(2)} \le \dots \le p_{(m)}$ ($m = 5$).
2. Reject $H_{(k)}$ if $p_{(k)} \le \frac{\alpha}{m - k + 1}$.

---

## 5. Equivalence Testing Protocol (TOST)

If the difference in accuracy between Explicit Repair and Forced Restart ($\Delta_{E-D}$) fails to reach statistical significance, we strictly **refuse to claim equivalence from non-significance**.

Instead, we apply the Two One-Sided Tests (TOST) procedure with pre-registered equivalence bounds:
$$[-\delta, +\delta] = [-0.05, +0.05] \quad (\pm 5\%\text{ accuracy})$$
- Test 1: $H_{01}: \Delta_{E-D} \le -0.05$
- Test 2: $H_{02}: \Delta_{E-D} \ge +0.05$
Statistical equivalence between Explicit Repair and Forced Restart is claimed if and only if both null hypotheses are rejected at $\alpha = 0.05$.
