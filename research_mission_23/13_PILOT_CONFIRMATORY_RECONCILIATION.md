# Research Mission 23 — Pilot vs. Confirmatory Forensic Reconciliation

**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Target Publication:** NeurIPS 2027 Main Track (Preprint: arXiv, Secondary: TMLR)  
**Date:** October 27, 2026  

---

## 1. Executive Summary of Reconciliation

Research Mission 23 has executed the definitive, preregistered Option B confirmatory trial ($N = 231$ held-out MATH-500 problems; 924 genuine neural generations on physical NVIDIA GeForce RTX 4090 hardware on RunPod Secure Cloud).

This forensic document reconciles the exploratory/pilot benchmark ($N = 100$) with the preregistered confirmatory trial ($N = 231$).

| Parameter | Pilot Benchmark ($N = 100$) | Confirmatory Trial ($N = 231$) | Joint / Reconciled Verdict |
| :--- | :--- | :--- | :--- |
| **Sample Universe** | MATH-500 (Problems 001–100) | MATH-500 (Disjoint held-out 231) | Zero overlap ($\mathcal{P}_{\text{pilot}} \cap \mathcal{P}_{\text{conf}} = \emptyset$) |
| **Model Evaluated** | `Qwen2.5-Math-7B-Instruct` | `Qwen2.5-Math-7B-Instruct` | Exact commit match (`ef9926d75ab1...`) |
| **Condition F Accuracy** | 73.0% (73/100) | 68.0% (157/231) | Baseline consistent with held-out difficulty |
| **Condition D Accuracy** | 67.0% (67/100) | 68.4% (158/231) | Stable restart performance |
| **Observed Effect $\hat{\tau}_{F-D}$** | **+0.0600 (+6.00%)** | **-0.0043 (-0.43%)** | **Effect contracts to 0** |
| **Contingency Table $(a, b, c, d)$** | $(65, 8, 2, 25)$ | $(146, 11, 12, 62)$ | Concordance: 90.0% pilot vs 90.0% confirmatory |
| **Total Discordant Pairs** | 10 ($q = 10.0\%$) | 23 ($q = 9.96\%$) | **Discordant noise rate identical** ($\approx 10\%$) |
| **Discordant Split ($b : c$)** | 8 : 2 (80% F-favoring) | 11 : 12 (47.8% F-favoring) | **Even binomial split** |
| **Exact McNemar $p$-value** | $p = 0.109375$ | $p = 1.000000$ | **Null hypothesis cannot be rejected** |
| **95% Confidence Interval** | [-0.0125, +0.1325] | [-0.0450, +0.0364] | Pilot estimate (+0.06) excluded by Conf. CI |

---

## 2. Forensic Statistical Decomposition

### A. Stability of the Discordant Noise Parameter $q$
In the preregistration power calculations (Mission 22 / 22.1 / 22.2), finite-sample power was shown to depend crucially on the total discordance probability $q = P(Y_F \neq Y_D)$.
- In Pilot: $q_{\text{pilot}} = \frac{8 + 2}{100} = 0.1000$ (10.00%).
- In Confirmatory: $q_{\text{conf}} = \frac{11 + 12}{231} = 0.09957$ (9.96%).
The empirical discordance between Condition F and Condition D is an extraordinarily stable parameter ($\approx 10\%$). In 90% of all problems, continuation and forced restart produce identical outcomes (146 both correct, 62 both incorrect).

### B. Resolution of the Asymmetric Split (Regression to the Mean)
In the pilot sample of 100 problems, among the 10 discordant cases, 8 were favorable to Condition F and 2 were favorable to Condition D:
$$\text{Binomial}(10, 0.5): \quad P(X \ge 8) = \binom{10}{8} 0.5^{10} + \binom{10}{9} 0.5^{10} + \binom{10}{10} 0.5^{10} = \frac{45 + 10 + 1}{1024} = 0.0546875$$
Two-sided exact $p = 0.109375$.
The pilot result was already non-significant at $\alpha = 0.05$, representing a suggestive exploratory signal.

In the confirmatory trial on 231 held-out problems, the 23 discordant pairs split virtually 50/50:
- $b = 11$ (Condition F correct, Condition D incorrect)
- $c = 12$ (Condition D correct, Condition F incorrect)
$$\text{Binomial}(23, 0.5): \quad P(X \ge 12) = 0.5000 \implies p = 1.000000$$

This is a textbook demonstration of the **Winner's Curse** and statistical regression to the mean. The apparent +6.0% point estimate in the pilot was an artifact of small-sample variance in 10 discordant cases.

---

## 3. Exclusion of the Pilot Effect Estimate

The confirmatory trial's 95% paired Wald confidence interval for $\tau_{F-D}$ is:
$$\hat{\tau} \pm 1.96 \cdot \text{SE} = -0.0043 \pm 1.96 \cdot 0.0208 = [-0.0450, +0.0364]$$

Because the upper bound of this 95% confidence interval is **+3.64%**, the pilot point estimate of **+6.00% is strictly excluded by the confirmatory data**. We can reject with >95% confidence that the true population recovery advantage of Condition F over Condition D is $\ge +3.64\%$.

---

## 4. Scientific Implications for NeurIPS 2027

1. **Defensible Scientific Stance:**
   StateShift must NOT claim that prompt-level state-preserving recovery provides a general, statistically significant accuracy advantage over forced restart on mathematical reasoning in Qwen2.5-Math-7B.
2. **Value of the Preregistered Confirmatory Paradigm:**
   This paper exemplifies the gold standard of open, reproducible science:
   - Formulating an exploratory hypothesis on pilot data.
   - Pregistering exact analysis pipelines and sample freezes.
   - Conducting a high-powered confirmatory trial on held-out data.
   - Reporting the true, unvarnished empirical reality.
   This transforms the paper into a landmark methodology study on reasoning recovery, warning the field against premature causal claims based on small-sample exploratory continuation benchmarks.
