# Research Mission 22.2 — Exact Power and Sample Size Revalidation

## 1. Executive Summary & Preregistered Power Equation
The confirmatory StateShift trial protocol freezes sample size determination at **Option B: $N = 231$ held-out disjoint MATH-500 problems** (924 total neural inference requests across 4 conditions).

This audit revalidates the exact finite-sample statistical power for the primary hypothesis test:
- $H_0: \psi = 0.5 \iff p_{01} = p_{10}$ (Condition F does not differ from Condition D)
- $H_1: \psi > 0.5 \iff p_{01} > p_{10}$ (Condition F improves recovery over Condition D)
- Significance level: $\alpha = 0.05$ (two-sided exact binomial McNemar test).

The exact power function under discordance rate $q = p_{01} + p_{10}$ and conditional success probability $\psi = \frac{p_{01}}{p_{01} + p_{10}}$ is given by:
$$\text{Power}(N, q, \psi) = \sum_{k=1}^N \binom{N}{k} q^k (1 - q)^{N-k} \left[ \sum_{b=0}^k \binom{k}{b} \psi^b (1 - \psi)^{k-b} \cdot \mathbb{I}\left( p_{\text{exact}}(b, k - b) \le \alpha \right) \right]$$
where $p_{\text{exact}}(b, c) = 2 \times \min\left( \sum_{j=b}^k \binom{k}{j} 0.5^k, \sum_{j=0}^b \binom{k}{j} 0.5^k \right)$.

---

## 2. Revalidation Under Pilot Experimental Parameters

In the pilot experiment ($N = 100$):
- Condition D Accuracy: $p_D = 0.67$
- Condition F Accuracy: $p_F = 0.73$
- Marginal Difference: $\Delta = p_F - p_D = +0.0600$
- Discordant Rate: $q = \frac{n_d}{N} = \frac{10}{100} = 0.1000$
- Conditional Odds Ratio: $\theta = \frac{8}{2} = 4.00$
- Conditional Parameter: $\psi = \frac{8}{10} = 0.8000$

Evaluating the exact binomial power equation at $N = 231$:
$$\text{Power}(N = 231, q = 0.10, \psi = 0.80) = \mathbf{80.07\%}$$

At $N = 231$, the experiment achieves the standard scientific benchmark of $80\%$ statistical power to reject the null hypothesis at $\alpha = 0.05$.

---

## 3. Elevated Discordance Sensitivity Analysis

If the held-out sample exhibits greater problem heterogeneity, the overall discordance rate $q$ may increase above the pilot estimate of $0.10$. A sensitivity grid was computed across alternative discordance regimes holding the effect size constant at $\Delta = +0.06$:

| Discordance Rate $q$ | Cell $p_{01}$ (F > D) | Cell $p_{10}$ (D > F) | Odds Ratio $\theta$ | $\psi = \frac{p_{01}}{q}$ | Power at $N=231$ | $N$ for 80% Power | $N$ for 90% Power |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0.08** | 0.0700 | 0.0100 | 7.00 | 0.8750 | 92.41% | 168 | 224 |
| **0.10 (Pilot)** | 0.0800 | 0.0200 | 4.00 | 0.8000 | **80.07%** | **231** | **308** |
| **0.12** | 0.0900 | 0.0300 | 3.00 | 0.7500 | 72.14% | 275 | 366 |
| **0.14** | 0.1000 | 0.0400 | 2.50 | 0.7143 | **65.86%** | **322** | **428** |
| **0.16** | 0.1100 | 0.0500 | 2.20 | 0.6875 | 60.72% | 369 | 490 |

### Key Methodological Findings
1. Under the pilot discordance rate ($q = 0.10$), $N = 231$ is exactly sufficient for $80.07\%$ power.
2. If discordance elevates to $q = 0.14$, power drops to $65.86\%$. Achieving $80\%$ power in this elevated discordance scenario would require $N \ge 322$ problems, and $90\%$ power would require $N \ge 428$ problems.
3. This sensitivity gradient is illustrated in `figures/confirmatory_power_sensitivity.pdf` and serves as a preregistered diagnostic in the event of an inconclusive confirmatory outcome.

---

## 4. Visual Artifact Verification
The high-resolution visualization `figures/confirmatory_power_sensitivity.pdf` (and accompanying `.png`) has been verified on disk. It plots:
- Curve 1: Exact power vs. sample size $N \in [50, 500]$ for $q \in \{0.08, 0.10, 0.12, 0.14\}$.
- Vertical Marker: Frozen Option B sample size $N = 231$.
- Horizontal Marker: $80\%$ and $90\%$ statistical power thresholds.
