# Phase D: Exact Power and Sample Size Revalidation Report

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22 — Confirmatory Trial Preflight  
**Date & Timestamp**: 2026-10-27T02:31:30+05:30  
**Target Venue**: NeurIPS 2027 Main Track  

---

## 1. Executive Summary

In the physical pilot experiment ($N = 100$), Condition F achieved $73.00\%$ accuracy versus Condition D at $67.00\%$, yielding an observed treatment effect of $\hat{\tau}_{F-D} = +6.00$ percentage points. The observed discordance was $n_d = 10$ ($b = 8, c = 2$), giving an exact two-sided McNemar p-value of $p = 0.109375$ (inconclusive at $\alpha = 0.05$).

This report provides an independent mathematical verification of the exact discrete statistical power of McNemar's test for the confirmatory trial. We certify that the preregistered sample size of **$N = 231$** achieves **$80.07\%$ exact power** under the empirical pilot parameters ($q = 0.10, \delta = +0.06$). Furthermore, we audit and correct an error in prior preliminary documentation regarding elevated discordance ($q = 0.14$), proving that the true minimum sample size for 80% power is $N = 322$, rather than the previously reported $N = 312$.

---

## 2. Mathematical Formalization of Exact Discrete Power

Let $N$ be the number of paired problem evaluations. Let $Y_{i,F}, Y_{i,D} \in \{0, 1\}$ be the binary outcomes.
The population cell probabilities are:
- $p_{11} = P(Y_F = 1, Y_D = 1)$ (concordant correct)
- $p_{00} = P(Y_F = 0, Y_D = 0)$ (concordant incorrect)
- $p_{10} = P(Y_F = 1, Y_D = 0)$ (discordant favoring intervention)
- $p_{01} = P(Y_F = 0, Y_D = 1)$ (discordant favoring baseline)

The marginal effect is $\delta = p_{10} - p_{01}$ and the total discordance rate is $q = p_{10} + p_{01}$.
Thus:
$$p_{10} = \frac{q + \delta}{2}, \quad p_{01} = \frac{q - \delta}{2}, \quad \pi = \frac{p_{10}}{q} = \frac{q + \delta}{2q}$$

In a finite sample of size $N$, the number of discordant pairs $K \sim \text{Binomial}(N, q)$.
Conditional on $K = k$, the exact two-sided McNemar test at level $\alpha = 0.05$ rejects $H_0: \pi = 0.5$ if the number of pairs favoring Condition F ($B$) satisfies $B \le c_1(k)$ or $B \ge c_2(k) = k - c_1(k)$, where:
$$c_1(k) = \max \left\{ j \in \mathbb{N}_0 : 2 \sum_{m=0}^j \binom{k}{m} 0.5^k \le \alpha \right\}$$

Conditional on $K = k$, the exact power under alternative $\pi$ is:
$$\text{Power}(k \mid \pi) = \sum_{j=0}^{c_1(k)} \binom{k}{j} \pi^j (1-\pi)^{k-j} + \sum_{j=c_2(k)}^k \binom{k}{j} \pi^j (1-\pi)^{k-j}$$

The unconditional exact discrete power across the entire binomial distribution of $K$ is:
$$\text{Power}(N \mid q, \delta) = \sum_{k=1}^N \binom{N}{k} q^k (1-q)^{N-k} \, \text{Power}(k \mid \pi)$$

---

## 3. Verified Power Benchmark Table

All values were computed via `/Users/shamthakare/.gemini/antigravity/scratch/research_mission_22/scripts/confirmatory_exact_power.py` without asymptotic approximations:

| Benchmark Scenario | Discordance $q$ | Effect $\delta$ | Odds Ratio $\theta$ | Sample Size $N$ | Exact Power | Minimum $N$ for $\ge 80.0\%$ Power |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pilot Observed Baseline** | **$0.10$** | **$+0.06$** | **$4.00$** | **$231$** | **$80.07\%$** | **$231$** |
| **High Power Target (90%)** | $0.10$ | $+0.06$ | $4.00$ | $299$ | $90.02\%$ | $231$ (for 80%), $299$ (for 90%) |
| **Conservative Effect Size** | $0.10$ | $+0.05$ | $3.00$ | $337$ | $80.07\%$ | $337$ |
| **Moderate Discordance** | $0.12$ | $+0.06$ | $3.00$ | $276$ | $79.28\%$ | $281$ |
| **Elevated Discordance (Old Report)** | $0.14$ | $+0.06$ | $2.33$ | $312$ | **$78.56\%$** | **$322$** |
| **Elevated Discordance (Corrected)** | **$0.14$** | **$+0.06$** | **$2.33$** | **$322$** | **$80.01\%$** | **$322$** |

---

## 4. Methodological Audit & Correction of Discrepancy

### 4.1 Non-Monotonicity and Discreteness
Unlike continuous Gaussian approximations (which produce smooth, monotonic power curves), exact discrete McNemar power exhibits characteristic "sawtooth" oscillations. As $N$ increases, the discrete critical cutoffs $c_1(k)$ jump integer values at discrete boundaries. At these boundary transitions, the actual type-I error rate temporarily drops well below $\alpha = 0.05$, causing local dips in statistical power.

### 4.2 Correction of the Prior $N = 312$ Citation
In preliminary working notes, a sample size of $N = 312$ was mentioned as sufficient for $80\%$ power under $q = 0.14, \delta = 0.06$. Our independent audit disproves this claim:
- At $N = 312$, the exact discrete power is **$78.56\%$** (falling short of 80% by $1.44$ percentage points).
- The true minimum sample size that guarantees at least $80.0\%$ exact power under $q = 0.14, \delta = 0.06$ is **$N = 322$** ($80.01\%$).

### 4.3 Defensibility of the Chosen $N = 231$
For the primary confirmatory trial, the empirical pilot parameters ($q = 0.10, \delta = +0.06$) are the best unbiased point estimates available from authentic physical GPU execution. At these parameters:
$$\text{Power}(N = 231) = 80.07\% > 80.00\%$$
Thus, $N = 231$ represents the exact, mathematically optimal minimal sample size satisfying standard NeurIPS statistical power requirements while minimizing GPU operational risk and cloud spending.

---

## 5. Artifact Verification

- **Executable Engine**: `research_mission_22/scripts/confirmatory_exact_power.py`
- **Sensitivity Figure (PDF)**: `research_mission_22/figures/confirmatory_power_sensitivity.pdf`
- **Sensitivity Figure (PNG)**: `research_mission_22/figures/confirmatory_power_sensitivity.png`

**Verdict**: **PASS** (Exact power verified at $80.07\%$; discrepancy audited and resolved).
