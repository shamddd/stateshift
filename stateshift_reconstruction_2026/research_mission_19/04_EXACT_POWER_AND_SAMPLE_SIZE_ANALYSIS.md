# StateShift: Research Mission 19 — Exact Paired Power & Sample Size Analysis

**Audit Date:** October 26, 2026  
**Auditor Committee:** Independent Scientific Review Panel (Statistical Methodology Directorate)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Preprint: arXiv)  
**Computation Engine:** `research_mission_19/scripts/exact_paired_power.py`  
**Data Artifact:** `research_mission_19/data/exact_power_analysis_results.json`  

---

## 1. Executive Summary: Power and Sample Size Truth

A central question in adversarial review is: *Was the failure to reject $H_0: \tau_{F-D} = 0$ ($p = 0.1094$) a consequence of a weak effect, or of an underpowered sample size?*

**Analytical Power Ruling:**
1. **Underpowered Pilot ($N=100$):**
   Under the empirical parameter values ($\delta = 10.0\%$ discordance rate, $\tau = +6.00\%$ effect size, conditional win probability $\psi = 0.80$):
   - **Exact Discrete Unconditional Power:** **$36.19\%$**
   - **Asymptotic Normal Approximation Power:** **$47.46\%$**
   - **Type II Error Rate ($\beta$):** **$63.81\%$**
   The $N=100$ experiment had nearly a two-thirds probability of failing to reject $H_0$ even under a true $+6.00\%$ advantage.
2. **Confirmatory Sample Size Requirements:**
   To detect $\tau = +6.00\%$ with standard statistical power:
   - **$80.0\%$ Power:** Requires **$N \ge 231$ paired problems** ($924$ total rollouts across 4 conditions; estimated GPU cost: **~$2.65 USD**). Asymptotic formula gives $N = 216$.
   - **$90.0\%$ Power:** Requires **$N \ge 299$ paired problems** ($1,196$ rollouts; estimated GPU cost: **~$3.43 USD**). Asymptotic formula gives $N = 288$.

---

## 2. Formal Exact Discrete vs Asymptotic Derivation

### The Random Discordance Problem
In paired binary experiments, only discordant pairs ($Y_F \neq Y_D$) provide information to test $H_0$. Let $N$ be the total number of paired problems. The number of discordant pairs $K$ is itself a binomial random variable:
$$K \sim \text{Binomial}(N, \delta)$$
where $\delta = p_{10} + p_{01} = 0.08 + 0.02 = 0.10$.

Conditional on observing $K = k$ discordant pairs, the number of Condition F wins $B$ follows:
$$B \mid (K = k) \sim \text{Binomial}(k, \psi), \quad \text{where } \psi = \frac{p_{10}}{\delta} = \frac{0.08}{0.10} = 0.80$$

Under $H_0$, $\psi = 0.50$. For a given $k$, a two-sided test at level $\alpha = 0.05$ rejects $H_0$ if $B \le c_k$ or $B \ge k - c_k$, where $c_k$ is the largest integer satisfying:
$$2 \sum_{j=0}^{c_k} \binom{k}{j} 0.5^k \le \alpha$$

### Exact Unconditional Power Formula
Because $K$ is stochastic, the true unconditional power is the expectation of conditional power over the distribution of $K$:
$$\text{Power}_{\text{Exact}}(N) = \sum_{k=1}^N \binom{N}{k} \delta^k (1 - \delta)^{N - k} \cdot \left[ P(B \le c_k \mid B \sim \text{Bin}(k, \psi)) + P(B \ge k - c_k \mid B \sim \text{Bin}(k, \psi)) \right]$$

### Why Discrete Power ($36.19\%$) is Lower than Asymptotic Power ($47.46\%$)
For small $k \le 5$:
$$2 \times 0.5^k \ge 2 \times 0.5^5 = \frac{2}{32} = 0.0625 > 0.05$$
Thus, for any trial where $k \le 5$, **the critical threshold $c_k = -1$**: it is mathematically impossible to reject $H_0$ at two-sided $\alpha = 0.05$, even if the model wins $100\%$ of discordant pairs ($B = k$).
At $N=100$ and $\delta = 0.10$, $P(K \le 5) = \sum_{k=0}^5 \binom{100}{k} 0.10^k 0.90^{100-k} \approx 6.25\%$. Furthermore, for $k \in [6, 10]$, the discrete thresholds are extremely conservative, depressing exact power to $36.19\%$.

---

## 3. Required Sample Size Scaling Table

| Target Statistical Power ($1 - \beta$) | Type II Error Rate ($\beta$) | Exact Discrete Sample Size ($N$) | Asymptotic Sample Size ($N$) | Total Rollouts (4 Conditions) | Estimated RunPod RTX 4090 Cost |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Current ($N=100$)** | **63.81%** | **100** | **100** | **400** | **$1.15 USD** (Settled) |
| **70.0% Power** | 30.00% | 188 | 171 | 752 | ~$2.16 USD |
| **80.0% Power** | **20.00%** | **231** | **216** | **924** | **~$2.65 USD** |
| **85.0% Power** | 15.00% | 260 | 247 | 1,040 | ~$2.98 USD |
| **90.0% Power** | **10.00%** | **299** | **288** | **1,196** | **~$3.43 USD** |
| **95.0% Power** | 5.00% | 360 | 356 | 1,440 | ~$4.13 USD |

---

## 4. Sensitivity Grid across Plausible Population Values

To assess robustness against estimation uncertainty in the pilot parameters, we computed exact required sample sizes across a grid of plausible discordance rates ($\delta \in [8\%, 14\%]$) and true effect sizes ($\tau \in [4\%, 8\%]$):

| Population Discordance ($\delta$) | True Effect Size ($\tau$) | Conditional Win Rate ($\psi$) | Required $N$ for 80% Exact Power | Required $N$ for 90% Exact Power |
| :---: | :---: | :---: | :---: | :---: |
| **8.0%** | +4.0 pp | 75.0% | 421 | 539 |
| **8.0%** | +6.0 pp | 87.5% | 180 | 227 |
| **10.0% (Empirical)** | +4.0 pp | 70.0% | 517 | 677 |
| **10.0% (Empirical)** | **+6.0 pp** | **80.0%** | **231** | **299** |
| **10.0% (Empirical)** | +8.0 pp | 90.0% | 125 | 157 |
| **12.0%** | +4.0 pp | 66.7% | 622 | 815 |
| **12.0%** | +6.0 pp | 75.0% | 281 | 359 |
| **12.0%** | +8.0 pp | 83.3% | 153 | 197 |
| **14.0%** | +4.0 pp | 64.3% | 723 | 949 |
| **14.0%** | +6.0 pp | 71.4% | 322 | 420 |
| **14.0%** | +8.0 pp | 78.6% | 183 | 236 |

---

## 5. Methodological Guidance for Future Work

1. **Independent Confirmatory Cohort vs Post-Hoc Extension:**
   If future compute funding becomes available, researchers must NOT simply add 131 problems to the existing 100 problems post-hoc. A scientifically valid confirmatory trial requires an **independent, preregistered cohort of $N=231$ new problems** with a frozen analysis plan to prevent sequential testing alpha inflation.
2. **Current Paper Positioning:**
   The $N=100$ experiment is honestly and constructively positioned as an **unbiased empirical pilot** that establishes the effect size ($\hat{\tau}_{F-D} = +6.00\%$, $\hat{\tau}_{F-A} = +9.00\%$) and provides the exact variance priors needed to power future confirmatory benchmarking.
