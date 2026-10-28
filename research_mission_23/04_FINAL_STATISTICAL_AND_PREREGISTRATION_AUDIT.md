# Research Mission 23 — Phase 4: Final Statistical and Preregistration Audit

## 1. Primary Estimand & Paired Outcome Formulation
The primary statistical objective of StateShift is to evaluate the causal treatment effect of Condition F (State-Preserving Recovery) relative to Condition D (Forced Restart) in mathematical problem solving.

- **Unit of Observation**: Matched problem item $i \in \{1, \dots, N\}$.
- **Binary Outcomes**: $Y_{Di} \in \{0, 1\}$ and $Y_{Fi} \in \{0, 1\}$.
- **Within-Item Contrast**: $D_i = Y_{Fi} - Y_{Di} \in \{-1, 0, +1\}$.
- **Sample Estimand**: Difference in paired marginal proportions:
  $$\hat{\tau}_{F-D} = \frac{1}{N} \sum_{i=1}^N (Y_{Fi} - Y_{Di}) = \frac{b - c}{N}$$
  where:
  - $b = \sum_{i=1}^N \mathbb{I}(Y_{Di} = 0, Y_{Fi} = 1)$ (Discordant pairs favoring F)
  - $c = \sum_{i=1}^N \mathbb{I}(Y_{Di} = 1, Y_{Fi} = 0)$ (Discordant pairs favoring D)

---

## 2. Hypothesis Testing & Exact McNemar Inference

- **Null Hypothesis ($H_0$)**: $P(Y_{Di} = 0, Y_{Fi} = 1) = P(Y_{Di} = 1, Y_{Fi} = 0) \iff \psi = 0.5$
- **Alternative Hypothesis ($H_1$)**: $P(Y_{Di} = 0, Y_{Fi} = 1) \ne P(Y_{Di} = 1, Y_{Fi} = 0) \iff \psi \ne 0.5$ (Two-Sided)
- **Primary Test Statistic**: Conditioning on the total number of discordant pairs $n_d = b + c$:
  $$b \mid n_d \sim \text{Binomial}(n_d, 0.5)$$
- **Exact Finite-Sample Two-Sided p-value**:
  $$p_{\text{exact}} = 2 \times \min\left( \sum_{k=b}^{n_d} \binom{n_d}{k} (0.5)^{n_d}, \sum_{k=0}^b \binom{n_d}{k} (0.5)^{n_d} \right)$$
- **Decision Rule**: Reject $H_0$ if and only if $p_{\text{exact}} \le 0.05$ and $\hat{\tau}_{F-D} > 0$.

---

## 3. Preregistered Confidence Intervals

1. **Paired Difference Confidence Interval**:
   $$\text{SE}(\hat{\tau}_{F-D}) = \sqrt{\frac{(b + c) - (b - c)^2 / N}{N^2}}$$
   $$\text{95\% Asymptotic Wald CI} = \hat{\tau}_{F-D} \pm 1.95996 \times \text{SE}(\hat{\tau}_{F-D})$$
2. **Conditional Odds Ratio Confidence Interval**:
   $$\hat{\theta} = \frac{b}{c}$$
   Exact Clopper-Pearson confidence limits on the binomial parameter $\psi = \frac{b}{n_d}$ are inverted:
   $$\theta_{\text{lower}} = \frac{\psi_{\text{lower}}}{1 - \psi_{\text{lower}}}, \quad \theta_{\text{upper}} = \frac{\psi_{\text{upper}}}{1 - \psi_{\text{upper}}}$$

---

## 4. Preregistration Governance Rules

1. **Fixed Sample Size ($N = 231$)**:
   - The sample size of 231 problems (924 total inference requests) is cryptographically frozen.
   - **Zero Optional Stopping**: No interim hypothesis testing, effect size evaluations, or conditional early stopping are permitted while the trial is running.
   - **No Sample Size Expansion**: The sample size will not be expanded post-hoc in response to a nonsignificant outcome.
2. **Missing Data & Truncation Policy**:
   - Complete-case evaluation with zero synthetic data imputation.
   - Generations that truncate at the 768-token ceiling are evaluated via the cleanroom extractor. If no boxed answer is found, they are scored `False`.
3. **Multiplicity Control for Secondary Analyses**:
   - Secondary comparisons (E vs D, F vs E, D vs A, F vs A) will be corrected using the Benjamini-Hochberg False Discovery Rate (FDR) procedure at $q = 0.05$.
   - Any subgroup analyses (by subject or difficulty level) are explicitly designated as exploratory and underpowered.
4. **Scientific Validity of Nonsignificant Results**:
   - **A nonsignificant confirmatory result ($p \ge 0.05$) is a completely valid scientific finding**. If the null hypothesis cannot be rejected, it will be transparently documented with its confidence interval and discussed without spin or post-hoc reframing.
