# StateShift: Research Mission 18 — Independent Statistical Reproduction & Significance Audit

**Audit Date:** October 26, 2026  
**Auditor Committee:** Independent Scientific Audit Committee (Statistical Methodology Directorate)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Analysis Script:** `research_mission_18/scripts/independent_statistics.py`  
**Output Data:** `research_mission_18/data/independent_statistical_results.json`  

---

## 1. Executive Summary & Core Statistical Verdict

The Statistical Methodology Directorate independently audited the preregistered inferential analyses of the StateShift primary experiment ($N=100$ paired MATH-500 problems evaluated across 4 experimental conditions).

**Independent Statistical Verdict:**
1. **Mathematical Accuracy of Estimators:** All point estimates, paired contingency counts, bootstrap distributions, and exact $p$-values computed in Mission 17 are **100% mathematically verified**.
2. **Critical Significance Interpretation for Primary Estimand ($\hat{\tau}_{F-D}$):**
   - The observed effect is $\hat{\tau}_{F-D} = +6.00\%$ ($73.00\%$ in Condition F vs $67.00\%$ in Condition D).
   - The exact two-sided McNemar $p$-value is **$p = 0.109375$** ($b=8$ vs $c=2$, $b+c=10$).
   - The two-sided paired permutation test $p$-value is **$p = 0.109900$**.
   - **CRITICAL METHODOLOGICAL FINDING:** Under standard Neyman-Pearson hypothesis testing at $\alpha = 0.05$, **$p = 0.1094 > 0.05$ fails to achieve statistical significance**.
   - It is an empirical error to claim that StateShift has "proven" or "statistically established" the causal superiority of Condition F over Condition D.
   - The empirical evidence represents a strong, encouraging **positive directional trend** (discordant odds ratio $4:1$, exact one-sided $p = 0.0547$, 95% bootstrap CI $[0.00\%, +12.00\%]$).
3. **Statistical Significance of Baseline Recovery ($\hat{\tau}_{F-A}$):**
   - The contrast against Zero-Shot (Condition A) is $\hat{\tau}_{F-A} = +9.00\%$ ($73.00\%$ vs $64.00\%$, $b=10, c=1$).
   - Exact two-sided McNemar $p$-value is **$p = 0.011719$** ($p < 0.05$), which survives Holm-Bonferroni family-wise error rate control ($p < \alpha/3 = 0.0167$).

---

## 2. Complete Paired Contingency Tables

Every problem was evaluated across identical inputs under greedy decoding (temperature 0, seed 42):

### Table 1: Primary Contrast — Condition F vs Condition D
*Condition F: State-Preserving Recovery; Condition D: Forced Restart Control*

| Contingency Cell | Definition | Count | Percentage |
| :--- | :--- | :--- | :--- |
| **Cell $a$** | Both F and D Correct | 65 | 65.0% |
| **Cell $b$** | F Correct, D Incorrect (F Wins) | 8 | 8.0% |
| **Cell $c$** | D Correct, F Incorrect (D Wins) | 2 | 2.0% |
| **Cell $d$** | Both F and D Incorrect | 25 | 25.0% |
| **Total ($N$)** | Paired Problem Items | 100 | 100.0% |

- Discordant Sample Size: $n_{\text{disc}} = b + c = 10$
- Point Estimand: $\hat{\tau}_{F-D} = \frac{b - c}{N} = \frac{8 - 2}{100} = \mathbf{+6.00\%}$
- Discordant Win-Loss Ratio: $\frac{b}{c} = \frac{8}{2} = \mathbf{4.00}$

---

### Table 2: Secondary Contrast — Condition E vs Condition D
*Condition E: Explicit Repair; Condition D: Forced Restart Control*

| Contingency Cell | Definition | Count | Percentage |
| :--- | :--- | :--- | :--- |
| **Cell $a$** | Both E and D Correct | 63 | 63.0% |
| **Cell $b$** | E Correct, D Incorrect (E Wins) | 8 | 8.0% |
| **Cell $c$** | D Correct, E Incorrect (D Wins) | 4 | 4.0% |
| **Cell $d$** | Both E and D Incorrect | 25 | 25.0% |
| **Total ($N$)** | Paired Problem Items | 100 | 100.0% |

- Point Estimand: $\hat{\tau}_{E-D} = \frac{8 - 4}{100} = \mathbf{+4.00\%}$
- Discordant Ratio: $\frac{b}{c} = \frac{8}{4} = \mathbf{2.00}$

---

### Table 3: Baseline Recovery — Condition F vs Condition A
*Condition F: State-Preserving Recovery; Condition A: Zero-Shot Baseline*

| Contingency Cell | Definition | Count | Percentage |
| :--- | :--- | :--- | :--- |
| **Cell $a$** | Both F and A Correct | 63 | 63.0% |
| **Cell $b$** | F Correct, A Incorrect (F Wins) | 10 | 10.0% |
| **Cell $c$** | A Correct, F Incorrect (A Wins) | 1 | 1.0% |
| **Cell $d$** | Both F and A Incorrect | 26 | 26.0% |
| **Total ($N$)** | Paired Problem Items | 100 | 100.0% |

- Point Estimand: $\hat{\tau}_{F-A} = \frac{10 - 1}{100} = \mathbf{+9.00\%}$
- Discordant Ratio: $\frac{b}{c} = \frac{10}{1} = \mathbf{10.00}$

---

## 3. Preregistered Inferential Statistics

| Contrast | Estimand ($\hat{\tau}$) | 95% Bootstrap CI ($B=10^4$) | Exact 2-Sided McNemar $p$ | Exact 1-Sided McNemar $p$ | Paired Permutation $p$ | Discordant Odds Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F vs D (Primary)** | **+6.00%** | **[0.00%, +12.00%]** | **0.109375** | **0.054688** | **0.109900** | **4.00** |
| **E vs D (Secondary)** | **+4.00%** | **[-3.00%, +11.00%]** | **0.387695** | **0.193848** | **0.389300** | **2.00** |
| **F vs A (Baseline)** | **+9.00%** | **[+3.00%, +16.00%]** | **0.011719** | **0.005859** | **0.011700** | **10.00** |

---

## 4. Family-Wise Error Rate (FWER) Control via Holm-Bonferroni

Evaluating the family of 3 pre-registered statistical hypotheses at nominal family $\alpha = 0.05$:

| Rank | Hypothesis / Contrast | Raw 2-Sided $p$-value | Holm Threshold $\frac{\alpha}{m - k + 1}$ | Decision |
| :--- | :--- | :--- | :--- | :--- |
| **1** | $H_3: \tau_{F-A} = 0$ | **0.011719** | $\frac{0.05}{3} \approx 0.016667$ | **REJECT $H_0$ (Significant)** |
| **2** | $H_1: \tau_{F-D} = 0$ | **0.109375** | $\frac{0.05}{2} = 0.025000$ | **FAIL TO REJECT $H_0$ (Not Significant)** |
| **3** | $H_2: \tau_{E-D} = 0$ | **0.387695** | $\frac{0.05}{1} = 0.050000$ | **FAIL TO REJECT $H_0$ (Not Significant)** |

**Conclusion on Multiplicity:**
Only the baseline recovery contrast ($F$ vs $A$) survives family-wise error rate control. The primary contrast ($F$ vs $D$) and secondary contrast ($E$ vs $D$) do not cross their respective Holm-adjusted significance barriers.

---

## 5. Methodological Audit: Why Claims of "Statistically Significant Proof" for $\tau_{F-D}$ Must Be Rejected

As an independent audit committee with expertise in statistical inference and NeurIPS reviewing:

1. **Two-Sided Preregistration Requirement:**
   In top-tier machine learning conferences (NeurIPS, ICML, ICLR), default hypothesis tests are two-sided unless an explicit directional asymmetry is formally justified *a priori* and preregistered without post-hoc rationalization. Under the two-sided test, $p = 0.1094$.
2. **The Nature of $p = 0.1094$:**
   $p = 0.1094$ indicates that if the true recovery difference between Condition F and Condition D were exactly zero, an asymmetry as extreme as 8 vs 2 would occur by random chance approximately $10.94\%$ of the time in a sample of 10 discordant pairs. This exceeds the universally accepted $5\%$ false-positive rate.
3. **The Directional Evidence:**
   The empirical evidence is undeniably positive:
   - 8 wins vs 2 losses (win rate 80.0% among discordant pairs).
   - One-sided exact $p = 0.0547$ is near the boundary.
   - The lower bound of the 95% bootstrap confidence interval rests at $0.00\%$, indicating non-inferiority.
4. **Mandatory Manuscript Calibrations:**
   - **Prohibited phrasing:** *"Our experiments demonstrate statistically significant proof that state preservation outperforms forced restart."*
   - **Required phrasing:** *"Under our $N=100$ preregistered evaluation, state-preserving recovery achieves a $+6.00\%$ empirical improvement over forced restart ($73\%$ vs $67\%$), with an $8:2$ win-to-loss ratio among discordant problems. While this directional trend is substantial (odds ratio 4.0, one-sided $p = 0.055$), it does not achieve two-sided statistical significance at $\alpha = 0.05$ ($p = 0.1094$), indicating that larger sample sizes ($N \ge 250$) are required for definitive statistical confirmation. Concurrently, state-preserving recovery provides a statistically significant $+9.00\%$ improvement over the zero-shot baseline ($p = 0.0117$, Holm-adjusted $p < 0.05$)."*
