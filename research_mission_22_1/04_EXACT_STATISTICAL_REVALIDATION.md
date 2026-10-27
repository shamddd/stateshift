# Phase 4: Independent Statistical Revalidation & Power Sensitivity

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22.1 — Final Confirmatory Scientific Audit  
**Date & Timestamp**: 2026-10-27T05:41:45+05:30  
**Target Publication Venue**: NeurIPS 2027 Main Track  

---

## 1. Executive Summary & Epistemic Framing

Statistical power is a pre-experimental planning metric, not a post-hoc guarantee of discovery. For the proposed StateShift confirmatory trial ($N = 231$), power calculations rely upon the observed empirical point estimates from the $N = 100$ physical pilot: total discordance rate $q = 0.10$ ($10\%$) and treatment effect $\delta = +0.06$ ($+6.00$ percentage points).

This report presents an independent re-verification of exact discrete McNemar power. We confirm that $N = 231$ provides **$80.07\%$ exact power** under the pilot planning assumption. We also provide an exhaustive sensitivity matrix demonstrating how power degrades if the true effect size is smaller or if discordance is higher. We formally state the scientific policy: **a nonsignificant confirmatory outcome is valid, publishable evidence; sample sizes will not be inflated post-hoc based on unblinded data.**

---

## 2. Pilot Contingency Table Re-computation

Evaluating the 400 authentic neural generations from Study 2 yields:

| Contingency Cell | Pilot Count (Flexible Cleanroom) | Pilot Count (Strict Degrees) | Mathematical Meaning |
| :--- | :---: | :---: | :--- |
| **$a$ ($Y_F = 1, Y_D = 1$)** | 66 | 65 | Both conditions correct |
| **$b$ ($Y_F = 1, Y_D = 0$)** | **8** | **8** | F correct, D failed (favoring StateShift) |
| **$c$ ($Y_F = 0, Y_D = 1$)** | **2** | **2** | D correct, F failed (favoring Restart) |
| **$d$ ($Y_F = 0, Y_D = 0$)** | 24 | 25 | Both conditions incorrect |
| **Total Discordant ($n_d = b + c$)** | **10** | **10** | Discordance rate $q = 10.0\%$ |

- **Treatment Effect Estimand**:
  $$\hat{\tau}_{F-D} = \frac{b - c}{N} = \frac{8 - 2}{100} = +0.0600\text{ (+6.00 percentage points)}$$
- **Exact Two-Sided McNemar p-value**:
  $$p_{\text{exact}} = 2 \times \sum_{k=8}^{10} \binom{10}{k} 0.5^{10} = 2 \times \frac{45 + 10 + 1}{1024} = 0.109375$$
- **Inference**: Under standard two-sided $\alpha = 0.05$, the pilot primary effect is **not statistically significant** ($p = 0.109375 > 0.05$).

---

## 3. Independent Verification of Discrete Power Benchmarks

All calculations were executed unconditionally across the full discrete binomial distribution $K \sim \text{Binomial}(N, q)$ without asymptotic Gaussian approximations:

| Planning Assumption | Discordance $q$ | Effect $\delta$ | Sample Size $N$ | Exact Discrete Power | Minimum $N$ for $\ge 80.0\%$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Pilot Baseline (Primary Target)** | **$0.10$** | **$+0.06$** | **$231$** | **$80.07\%$** | **$231$** |
| **High Power Target (90%)** | $0.10$ | $+0.06$ | $299$ | $90.02\%$ | $231$ (for 80%), $299$ (for 90%) |
| **Conservative Effect** | $0.10$ | $+0.05$ | $337$ | $80.07\%$ | $337$ |
| **Elevated Discordance (Old Claim)** | $0.14$ | $+0.06$ | $312$ | **$78.56\%$** | **$322$** |
| **Elevated Discordance (Corrected)** | **$0.14$** | **$+0.06$** | **$322$** | **$80.01\%$** | **$322$** |

### Independent Audit of Prior Discrepancy:
- The historical draft claim that $N = 312$ achieves $80\%$ power at $q = 0.14, \delta = 0.06$ is **definitively disproven**: at $N = 312$, power is exactly $78.56\%$.
- The corrected minimum sample size is **$N = 322$** ($80.01\%$).

---

## 4. Full Power Sensitivity Grid ($N = 231$)

Because pilot effect estimates can be inflated due to small-sample selection ("winner's curse"), we evaluate the exact discrete power of $N = 231$ across a comprehensive sensitivity grid of effect sizes $\delta \in [0.03, 0.08]$ and discordance rates $q \in [0.08, 0.16]$:

| Total Discordance ($q$) | $\delta = 3.0$ pp | $\delta = 4.0$ pp | $\delta = 5.0$ pp | $\delta = 6.0$ pp (Pilot) | $\delta = 7.0$ pp | $\delta = 8.0$ pp |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$8.0\%$** | $28.6\%$ | $50.5\%$ | $73.6\%$ | **$90.7\%$** | $98.4\%$ | $100.0\%$ |
| **$10.0\%$ (Pilot)** | $23.1\%$ | $40.7\%$ | $61.4\%$ | **$80.1\%$** | $92.6\%$ | $98.3\%$ |
| **$12.0\%$** | $19.7\%$ | $34.3\%$ | $52.4\%$ | **$70.5\%$** | $85.2\%$ | $94.3\%$ |
| **$14.0\%$** | $17.6\%$ | $30.1\%$ | $46.0\%$ | **$63.0\%$** | $78.2\%$ | $89.3\%$ |
| **$16.0\%$** | $16.2\%$ | $27.3\%$ | $41.5\%$ | **$57.2\%$** | $72.2\%$ | $84.3\%$ |

---

## 5. Preregistration Invariants & Anti-P-Hacking Commitments

1. **Assumption Dependency**: The planned sample size of $N = 231$ is powered at $80\%$ *if and only if* the true population effect matches or exceeds $+6.00$ pp at $q = 10\%$.
2. **Acceptance of Null / Inconclusive Findings**: If the true population effect is $\delta = +4.00$ pp, power is only $40.7\%$, and the test may yield $p \ge 0.05$. **A nonsignificant confirmatory finding will be reported transparently as evidence bounding the recovery effect**, without post-hoc rationalization.
3. **Strict Sample Size Freeze**: Under no circumstances will additional problems be added post-hoc after inspecting confirmatory outcomes to "nudge" p-values below $0.05$.

**Phase 4 Audit Verdict**: **PASS** (Statistical power independently verified; assumptions and sensitivity boundaries fully formalized).
