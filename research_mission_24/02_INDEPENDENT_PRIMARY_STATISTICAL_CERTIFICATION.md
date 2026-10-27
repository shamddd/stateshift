# StateShift Research Mission 24 — Independent Primary Statistical Certification

**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Target Publication:** NeurIPS 2027 Main Track (Preprint: arXiv, Secondary: TMLR)  
**Audit Date:** October 27, 2026  
**Auditor:** Independent Scientific Audit Committee  
**Evaluation Scope:** Option B Preregistered Confirmatory Trial ($N = 231$ held-out MATH-500 problems; 924 genuine neural generations)  
**Hardware & Model:** 1x physical NVIDIA GeForce RTX 4090; `Qwen/Qwen2.5-Math-7B-Instruct` @ commit `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`  

---

## 1. Executive Statistical Certification

The independent audit committee has independently parsed all 924 generation records from `research_mission_23/data/confirmatory_924_generations.jsonl` (SHA-256: `aaba3bd5e4c95c8ab07f137b634c191d5d5ba7361427ca95ccb84103824f9448`) and verified the primary contingency table across four distinct mathematical and software implementations:
1. **Pure Python** (dictionary accumulation and loop arithmetic)
2. **NumPy** (vectorized boolean masking and sum operators)
3. **Pandas** (`pd.crosstab` contingency formulation)
4. **Independent Exact Binomial Inference** (`scipy.stats.binom`)

### Confirmatory Paired Contingency Table ($N = 231$)

```
                            Condition F (Continuation)
                            Correct (+)      Incorrect (-)      Total
Condition D   Correct (+)       146              12              158 (68.40%)
(Restart)     Incorrect (-)      11              62               73 (31.60%)
              Total             157 (67.97%)     74 (32.03%)     231
```

- **Cell $a$ (Both Correct):** 146
- **Cell $b$ (D Incorrect, F Correct):** 11
- **Cell $c$ (D Correct, F Incorrect):** 12
- **Cell $d$ (Both Incorrect):** 62
- **Total Discordant Pairs ($b + c$):** 23 ($9.96\%$ of total sample)
- **Primary Estimator $\hat{\tau}_{F-D}$:** $\frac{b - c}{N} = \frac{11 - 12}{231} = \mathbf{-0.004329}$ ($-0.4329$ percentage points)
- **Exact Two-Sided McNemar Test $p$-value:** **$p = 1.000000$**
- **Statistical Decision at $\alpha = 0.05$:** **FAIL TO REJECT NULL HYPOTHESIS** ($H_0: \tau_{F-D} = 0$)

All four independent implementations yield identical cell counts, identical treatment effect estimates, and identical exact $p$-values. The primary confirmatory result is certified **GREEN**.

---

## 2. Multi-Method Confidence Interval Verification

The committee recomputed the paired confidence interval under three distinct statistical methodologies:

| Method | Estimator | Standard Error | 95% Confidence Interval | Interval Width | Excludes Pilot (+6.0%)? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Preregistered Paired Wald** | $\hat{\tau} = \frac{b - c}{N}$ | $\frac{\sqrt{b + c - (b - c)^2 / N}}{N} = 0.020759$ | **$[-0.0450, +0.0364]$** | $0.0814$ | **YES** |
| **Newcombe Paired Wilson Score (Method 10)** | Marginal score diff with $\phi = 0.7706$ | Non-asymptotic Wilson bounds | **$[-0.0451, +0.0365]$** | $0.0816$ | **YES** |
| **Agresti-Min Adjusted Score (Bonett-Price)** | Cell adjustment $+0.5$ ($N = 233$) | Adjusted standard error | **$[-0.0455, +0.0369]$** | $0.0824$ | **YES** |

### Statistical Assessment of Interval Behavior:
1. **Invariance:** The interval bounds across asymptotic Wald, Newcombe score, and Agresti-Min adjustment differ by less than $0.0005$ ($0.05$ percentage points).
2. **Pilot Exclusion:** All three intervals place the upper bound strictly below $+0.0370$ ($+3.7\%$). The pilot study point estimate of $+0.0600$ ($+6.0\%$) is decisively excluded with greater than 95% confidence.

---

## 3. Two One-Sided Tests (TOST) & Practical Equivalence Analysis

To assess whether the data are compatible with practical equivalence, the committee conducted an exploratory Two One-Sided Tests (TOST) analysis against varying hypothesized equivalence margins $\Delta$:

- Two-sided $90\%$ Confidence Interval: $\hat{\tau} \pm 1.644853 \cdot \text{SE} = \mathbf{[-0.0385, +0.0298]}$ ($-3.85\%$ to $+2.98\%$).

| Equivalence Margin $\Delta$ | Lower Bound Test ($H_{01}: \tau \le -\Delta$) | Upper Bound Test ($H_{02}: \tau \ge +\Delta$) | TOST $p$-value | Equivalence Concluded at $\alpha = 0.05$? |
| :---: | :---: | :---: | :---: | :---: |
| **$\pm 10.0\%$ ($\Delta = 0.10$)** | $Z = +4.61, p < 0.0001$ | $Z = -5.03, p < 0.0001$ | $p < 0.0001$ | **YES** |
| **$\pm 5.0\%$ ($\Delta = 0.05$)** | $Z = +2.20, p = 0.0139$ | $Z = -2.62, p = 0.0044$ | $p = 0.0139$ | **YES** |
| **$\pm 4.0\%$ ($\Delta = 0.04$)** | $Z = +1.72, p = 0.0428$ | $Z = -2.14, p = 0.0163$ | $p = 0.0428$ | **YES** |
| **$\pm 3.0\%$ ($\Delta = 0.03$)** | $Z = +1.24, p = 0.1082$ | $Z = -1.65, p = 0.0491$ | $p = 0.1082$ | **NO** |

### Crucial Methodological Distinction:
Because a specific equivalence margin was **not preregistered**, the Principal Investigator must **not retrospectively claim confirmatory equivalence**. However, reporting that the observed data are compatible with practical equivalence under any margin $\Delta \ge \pm 3.85\%$ is scientifically sound and informative for future meta-analyses.

---

## 4. Final Verification Verdict

- **Category 1 (Statistical Interpretation - Primary Result):** **GREEN (CERTIFIED)**
- The primary dataset contains zero missing records, zero duplicate IDs, and zero mathematical extraction errors.
- The null result $\hat{\tau}_{F-D} = -0.43\%$, exact McNemar $p = 1.000000$, is certified as immutable scientific fact.
