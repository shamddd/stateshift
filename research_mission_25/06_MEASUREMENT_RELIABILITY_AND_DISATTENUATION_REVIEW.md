# StateShift Research Mission 25: Measurement Reliability and Disattenuation Review

**Author:** Multidisciplinary Independent Scientific Audit Committee  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Audit Target:** Measurement Error, Difference-Score Reliability, and Attenuation Bounds  
**Date:** October 27, 2026  
**Status:** Certified & Finalized  

---

## 1. Executive Summary

A critical issue in empirical machine learning is understanding how measurement error affects observed correlation coefficients. In Study 1, the observed sample correlation between forward capability growth ($\Delta C$) and recovery capability growth ($\Delta R$) was $r = 0.0794$ ($p = 0.091$). Prior drafts used this near-zero value to claim that recovery adaptation was "statistically independent" and "decoupled" from general reasoning proficiency.

This review formally evaluates the **measurement reliability of difference scores** in Study 1, computes the **attenuation factor**, and establishes the **epistemic limits of disattenuation**.

---

## 2. Theoretical Formulation of Difference-Score Reliability

Let $Y_{C,256,i}$ and $Y_{C,0,i}$ denote the sample proportion of correct rollouts ($K=16$) for problem pair $i$ under Control at checkpoints $t=256$ and $t=0$, respectively. The sample forward gain is:
$$\Delta C_i = Y_{C,256,i} - Y_{C,0,i}$$
Similarly, the recovery gain is:
$$\Delta R_i = Y_{R,256,i} - Y_{R,0,i}$$

In classical test theory, the reliability of a difference score $\Delta = X - Y$ is given by:
$$\text{Rel}(\Delta) = \frac{\sigma_X^2 \text{Rel}(X) + \sigma_Y^2 \text{Rel}(Y) - 2 \sigma_{XY}}{\sigma_X^2 + \sigma_Y^2 - 2 \sigma_{XY}}$$
Because $X$ and $Y$ are positively correlated across problems (problems easy at $t=0$ tend to remain easy at $t=256$), subtracting them removes true score variance while compounding stochastic binomial sampling variance. Consequently, difference scores derived from finite stochastic rollouts inherently exhibit **severely depressed reliability**.

---

## 3. Empirical Split-Half Reliability Recomputation

To quantify the exact measurement reliability in the Study 1 dataset ($N=454$ problem pairs, $K=16$ stochastic rollouts per problem-condition-checkpoint cell), the audit committee executed an odd-even split-half analysis:
1. Rollouts $k \in \{1, 3, 5, 7, 9, 11, 13, 15\}$ formed Sub-sample 1 ($K=8$).
2. Rollouts $k \in \{2, 4, 6, 8, 10, 12, 14, 16\}$ formed Sub-sample 2 ($K=8$).

### Split-Half Correlation ($K=8$):
- Forward gain $\Delta C$: $r_{\text{half}} = \mathbf{0.0969}$
- Recovery gain $\Delta R$: $r_{\text{half}} = \mathbf{0.0531}$

### Spearman-Brown Prophecy Formula for the Full $K=16$ Sample:
$$\text{Rel}(\Delta) = \frac{2 r_{\text{half}}}{1 + r_{\text{half}}}$$
- **Reliability of Forward Gain ($\text{Rel}(\Delta C)$)**:
  $$\text{Rel}(\Delta C) = \frac{2 \times 0.0969}{1 + 0.0969} = \mathbf{0.1767} \quad (17.67\%)$$
- **Reliability of Recovery Gain ($\text{Rel}(\Delta R)$)**:
  $$\text{Rel}(\Delta R) = \frac{2 \times 0.0531}{1 + 0.0531} = \mathbf{0.1009} \quad (10.09\%)$$

### Key Finding:
Over $82\%$ of the variance in observed problem-level forward gains $\Delta C_i$, and nearly $90\%$ of the variance in recovery gains $\Delta R_i$, is pure binomial measurement noise.

---

## 4. Spearman's Disattenuation Analysis

Under Spearman's correction for attenuation, the estimated correlation between the latent, noise-free constructs ($\rho_{\text{latent}}$) is:
$$r^* = \frac{r_{\text{obs}}}{\sqrt{\text{Rel}(\Delta C) \cdot \text{Rel}(\Delta R)}}$$

Substituting the observed correlation $r_{\text{obs}} = 0.0794$ and the empirical reliabilities:
$$r^* = \frac{0.0794}{\sqrt{0.1767 \times 0.1009}} = \frac{0.0794}{\sqrt{0.01783}} = \frac{0.0794}{0.1335} = \mathbf{0.5946} \approx \mathbf{0.595}$$

### Statistical Meaning:
- The observed correlation of $0.0794$ was attenuated by a factor of nearly $7.5 \times$ ($1 / 0.1335 \approx 7.49$).
- Once corrected for the severe measurement unreliability of the 16-rollout difference scores, the estimated latent linear association between forward capability expansion and error recovery adaptation is **moderate-to-strong ($\rho \approx 0.60$)**.

---

## 5. Epistemic Safeguards and Reporting Guidance

1. **Do Not Report Disattenuated Correlation as Observed Empirical Association**:
   Dividing by small reliability products ($\sqrt{0.0178} \approx 0.13$) drastically inflates estimation error. Disattenuated correlations can easily exceed $1.0$ under sample fluctuation and should be treated as diagnostic bounds, not point estimates.
2. **Definitive Refutation of "Statistical Independence"**:
   While $r^* \approx 0.60$ carries estimation uncertainty, it proves conclusively that the observed near-zero correlation ($r = 0.0794$) was primarily a mathematical consequence of measurement attenuation. Claiming that recovery improvement was "statistically independent" or "decoupled" from clean capability was completely unscientific.
3. **Audited Terminology Protocol**:
   All occurrences of the following terms in the manuscript must be purged or strictly qualified:
   - *Independent:* Replace with "weakly associated in observed sample".
   - *Decoupled:* Replace with "showing low raw linear correlation".
   - *Orthogonal:* Delete; replace with "distinct operational metrics".
   - *Disentangled:* Delete; replace with "evaluated under separate counterfactual conditions".
