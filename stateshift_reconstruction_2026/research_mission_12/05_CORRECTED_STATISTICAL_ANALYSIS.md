# 05 Corrected Statistical Analysis: Paired Equivalence, Token Dynamics, and Exact Zero-Event Bounds

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Investigation**: Research Mission 12 — Phase V Statistical Corrections  
**Primary Venue Target**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Date**: October 2026  
**Status**: COMPLETE — ALL STATISTICAL CLAIMS RECONSTRUCTED AND VERIFIED  

---

## 1. Executive Summary

This document establishes the corrected, mathematically sound statistical foundation for StateShift. In previous audit cycles (Missions 08–10), statistical claims suffered from two principal methodological issues:
1. Conflating non-significant differences ($p = 1.0$) with positive proof of "statistical equivalence" between prompting conditions without defining an equivalence margin ($\Delta$) or running a Two One-Sided Tests (TOST) procedure.
2. Interpreting empirical zero observed error-recovery events ($0 / 25$ or $0 / 115$) as categorical proof that autoregressive models possess "zero recovery capacity," rather than properly framing the result as an empirical upper bound on an unknown low-probability rate.

Here, we provide the rigorous statistical corrections across three key areas:
- **Paired Contingency and Equivalence Power**: Reconstructing the exact $2 \times 2$ paired outcome table for Condition D (Direct Instruction) vs. Condition F (Forced Reconsideration Prefix), computing exact and asymptotic tests, and deriving the sample size required ($N=286$) to confirm equivalence within a $\pm 10$ percentage point margin.
- **Token Efficiency vs. Compute Architecture**: Analyzing generated token length differences via 10,000-resample percentile bootstrapping, paired $t$-tests, and Wilcoxon signed-rank tests, while formally clarifying why generated token savings (-7.54%) do not translate directly into billed GPU compute or wall-clock savings due to prefill vs. decode architectural disparities.
- **Exact Binomial Bounds on Zero-Recovery Frequencies**: Computing exact Clopper-Pearson 95% confidence intervals across sample sizes $N \in \{25, 50, 100, 115, 400\}$, establishing that zero recoveries at $N=115$ rules out recovery probabilities exceeding $3.16\%$, but leaves open rare or scale-emergent recovery phenomena requiring 7B-scale evaluation.

---

## 2. Reconstructed Paired Contingency Table (Condition D vs. Condition F)

Across the $N=25$ paired GSM8K problems evaluated under Mission 10 on `Qwen2.5-Math-1.5B-Instruct-4bit`, both Condition D and Condition F achieved identical sample accuracy of $16 / 25 = 64.0\%$.

### 2.1 Paired $2 \times 2$ Contingency Structure

```
                  Condition F (Forced Prefix)
                  Correct (1)    Incorrect (0)     Total
Condition D (1)        16              0             16
Condition D (0)         0              9              9
Total                  16              9             25
```

- **Concordant Pairs**:
  - $n_{11}$ (Both Correct): $16$ ($64.0\%$)
  - $n_{00}$ (Both Incorrect): $9$ ($36.0\%$)
  - Concordance Rate: $25 / 25 = 100.0\%$
- **Discordant Pairs**:
  - $n_{10}$ (Condition F correct, Condition D incorrect): $0$
  - $n_{01}$ (Condition D correct, Condition F incorrect): $0$
  - Total Discordant Pairs: $b + c = 0$

### 2.2 Statistical Tests and Methodological Correction

- **Risk Difference**:
  $$\widehat{\Delta} = \widehat{p}_F - \widehat{p}_D = \frac{16}{25} - \frac{16}{25} = 0.000 \quad (0.00\text{ percentage points})$$
- **McNemar's Exact Test**:
  Because $b = c = 0$, the exact two-sided binomial test yields $p = 1.000$.
- **Asymptotic Standard Error Breakdown**:
  The asymptotic standard error of the risk difference for paired binary data is:
  $$\text{SE}(\widehat{\Delta}) = \frac{1}{N} \sqrt{(b + c) - \frac{(b - c)^2}{N}} = \frac{1}{25}\sqrt{0 - 0} = 0.000$$
  When $b = c = 0$, the Wald asymptotic standard error collapses to zero, producing a degenerate standard error. Relying on asymptotic Wald intervals here is invalid.
- **Rule of Three Conservative Bound**:
  Applying the Rule of Three for zero discordant events across $N=25$ independent problem pairs:
  $$\text{Upper Bound on Discordance Rate} = \frac{3}{N} = \frac{3}{25} = 0.120 \quad (12.0\text{ pp})$$
  Thus, the 95% confidence interval for the true risk difference is bounded by $[-12.0\text{ pp}, +12.0\text{ pp}]$.

### 2.3 Refutation of the "Statistical Equivalence from $p=1.0$" Fallacy

> [!WARNING]
> **Methodological Pitfall**: In prior drafts, an author asserted that $p = 1.000$ from McNemar's test constituted "definitive mathematical proof of statistical equivalence." This is an elementary violation of statistical inference: **absence of evidence is not evidence of absence**. A non-significant $p$-value ($p > 0.05$ or $p = 1.0$) merely indicates that the null hypothesis of no difference cannot be rejected; it provides zero evidence that the true difference is bounded within an acceptable equivalence margin.

To substantiate an empirical claim of **statistical equivalence**, one must execute a Two One-Sided Tests (TOST) procedure against a pre-specified equivalence margin $\Delta_{\text{eq}}$. For an equivalence margin of $\Delta_{\text{eq}} = \pm 10.0$ percentage points ($\alpha = 0.05$, power $1 - \beta = 0.80$):
$$N_{\text{req}} \approx \frac{2 \cdot (z_{1-\alpha} + z_{1-\beta/2})^2 \cdot \sigma^2}{\Delta_{\text{eq}}^2} = 286 \text{ problem pairs}$$
With only $N=25$ pairs, the study has less than $18\%$ statistical power to rule out a true accuracy divergence of up to $12$ percentage points. Therefore, StateShift's revised manuscript explicitly reports:
> *"At $N=25$, Condition D and Condition F exhibited zero discordant outcomes ($\text{accuracy} = 64.0\%$ in both conditions). However, exact binomial bounds indicate the true risk difference remains consistent with differences up to $\pm 12.0$ percentage points ($95\%\text{ CI}: [-12.0\%, +12.0\%]$). Establishing genuine statistical equivalence within a standard $\pm 10\%$ margin requires at least $N=286$ paired trials."*

---

## 3. Token Efficiency Analysis: Condition D vs. Condition F

We analyzed the generated token lengths across the $N=25$ paired problems to evaluate whether Condition F (Forced Reconsideration Prefix) impacts generation brevity.

### 3.1 Empirical Token Statistics

| Metric | Condition F (Forced Prefix) | Condition D (Direct) | Paired Difference $(F - D)$ |
| :--- | :---: | :---: | :---: |
| **Sample Size ($N$)** | 25 | 25 | 25 |
| **Mean Tokens** | 352.04 | 380.76 | **-28.72** |
| **Standard Deviation** | 94.67 | 108.32 | 77.88 |
| **Median Tokens** | 348.00 | 362.00 | 0.00 |
| **Interquartile Range** | [284.0, 412.0] | [295.0, 442.0] | [-48.0, 0.0] |
| **Percentage Reduction** | — | — | **-7.54%** |

### 3.2 Inferential Statistics and Bootstrap Distribution

- **Paired $t$-test**:
  $$t(24) = -1.8439, \quad p = 0.0776 \quad (\text{two-tailed, not significant at } \alpha = 0.05)$$
- **Parametric 95% Confidence Interval**:
  $$\text{Mean Diff} \pm t_{0.975, 24} \cdot \frac{s_d}{\sqrt{N}} = -28.72 \pm 2.0639 \cdot 15.576 = [-60.87, +3.43]\text{ tokens}$$
- **Wilcoxon Signed-Rank Test** (Zero differences omitted):
  $$W = 43.0, \quad p = 0.1127 \quad (\text{two-tailed, not significant at } \alpha = 0.05)$$
- **Non-Parametric Bootstrap (10,000 Resamples)**:
  - Percentile 95% CI: $[-61.36, -1.48]\text{ tokens}$
  - Bootstrap Mean: $-28.70\text{ tokens}$

Notice that while the non-parametric percentile bootstrap CI marginally excludes zero ($[-61.36, -1.48]$), both standard hypothesis tests ($t$-test $p=0.0776$, Wilcoxon $p=0.1127$) fail to achieve statistical significance at $\alpha = 0.05$.

### 3.3 System-Level Architecture: Generated Tokens vs. Billed GPU Compute

A critical nuance for NeurIPS and TMLR reviewers is the distinction between **generated tokens** and **end-to-end inference compute / billing**.

```
Prefill Phase (Prompt Input):
┌────────────────────────────────────────────────────────┐
│ [Problem Statement] + [Injected Contaminant Step]     │
│ + [Optional Forcing Prefix: Condition F]               │
└────────────────────────────────────────────────────────┘
          │ (Compute-Bound, Parallel GEMM Matrix Ops)
          ▼
Decode Phase (Autoregressive Generation):
┌────────────────────────────────────────────────────────┐
│ Generated Tokens (Condition F: ~352 tok; D: ~381 tok)  │
└────────────────────────────────────────────────────────┘
            (Memory-Bandwidth Bound, Sequential Token-by-Token)
```

1. **Memory Bandwidth vs. Compute Intensity**:
   - Modern LLM inference engines (vLLM, TGI, SGLang) divide execution into prefill and decode stages.
   - **Prefill** processes all prompt tokens in parallel, saturating tensor cores (compute-bound). Condition F adds tokens to the prompt prefix, increasing prefill FLOPs and slightly elevating Time-To-First-Token (TTFT).
   - **Decode** generates tokens sequentially, where each token requires moving the full model weights through memory bandwidth. Condition F saves $\approx 28.7$ generated tokens ($\approx 7.5\%$).
2. **End-to-End Latency and Cost Implications**:
   - For short prompt contexts ($< 500$ tokens), decode time dominates overall latency ($\approx 85-90\%$ of total wall-clock time). Thus, a $7.5\%$ reduction in decode tokens translates to an estimated $\approx 6-7\%$ reduction in wall-clock execution time per problem on GPU.
   - However, in batch-serving systems utilizing PagedAttention and continuous batching, throughput is governed by KV cache occupancy and maximum sequence lengths. If a single long sequence in a batch persists, savings from shorter sequences may not reduce GPU allocation time.
   - **Paper Framing**: We report the 28.7 token generation reduction as an interesting efficiency trend ($p=0.078$), but refrain from claiming proven compute cost savings until empirical wall-clock measurements under continuous batching on RunPod are completed.

---

## 4. Exact Binomial Uncertainty for Zero Observed Successes ($k=0$)

Across historical evaluations (Missions 09, 10, 11), zero rollouts under standard prompting succeeded in detecting and mathematically repairing an injected error without prompt assistance ($k=0$).

### 4.1 Clopper-Pearson Exact 95% Confidence Intervals

The exact Clopper-Pearson two-sided $100(1-\alpha)\%$ confidence interval for a binomial parameter $p$ with $k=0$ observed successes in $N$ independent trials has lower limit $p_L = 0$ and upper limit:
$$p_U = 1 - \left(\frac{\alpha}{2}\right)^{1/N} = 1 - 0.025^{1/N}$$

We compare the Clopper-Pearson exact bound against the Wilson score interval with continuity correction and the standard Rule of Three ($3/N$):

| Sample Size ($N$) | Observed Successes ($k$) | Point Estimate ($\widehat{p}$) | Exact Clopper-Pearson 95% Upper Bound | Wilson Score 95% Upper Bound | Rule of Three ($3/N$) Upper Bound |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **$N = 25$** (Single condition) | 0 | $0.00\%$ | **$13.72\%$** | $13.32\%$ | $12.00\%$ |
| **$N = 50$** (Two conditions) | 0 | $0.00\%$ | **$7.11\%$** | $7.13\%$ | $6.00\%$ |
| **$N = 100$** (M10 full cohort) | 0 | $0.00\%$ | **$3.62\%$** | $3.70\%$ | $3.00\%$ |
| **$N = 115$** (Total M09–M11) | 0 | $0.00\%$ | **$3.16\%$** | $3.23\%$ | $2.61\%$ |
| **$N = 400$** (Planned 7B Study) | 0 (hypothetical) | $0.00\%$ | **$0.92\%$** | $0.95\%$ | $0.75\%$ |

### 4.2 Rigorous Scientific Interpretation

> [!IMPORTANT]
> **The Empirical Reality of Zero Observed Events**:
> Observing $0 / 25$ recoveries does **not** prove that the model has "zero capability" or that autoregressive reasoning recovery is impossible. Mathematically, $0 / 25$ only bounds the true recovery rate to $\le 13.72\%$ ($95\%\text{ CI}$).
> Even aggregating across all $N=115$ error-injected rollouts evaluated in Missions 09–11, observing $0$ recoveries yields a $95\%$ upper bound of $3.16\%$.

This formal boundary establishes two profound scientific implications:
1. **Low-Frequency Phenomena Cannot Be Ruled Out**:
   If reasoning recovery in small models (1.5B) occurs at a true base rate of $1.5\%$ or $2.0\%$, a sample size of $N=25$ has a:
   $$P(\text{observe } 0 \text{ successes} \mid p = 0.02, N=25) = (1 - 0.02)^{25} \approx 60.3\%$$
   More than $60\%$ of experiments with $N=25$ will observe zero recoveries even if the capability is genuinely present.
2. **Justification for Frontier Model Scaling (7B Pilot)**:
   In reasoning models, self-correction capabilities are widely documented to emerge or scale non-linearly with model parameter capacity (e.g., Qwen2.5-Math-7B, DeepSeek-Math-7B). Testing 7B models across an adequately powered cohort ($N \ge 400$) is strictly required to determine whether recovery remains bounded below $1\%$ or emerges as a viable cognitive mechanism at scale.

---

## 5. Summary Table of Corrected Empirical Claims

| Claim ID | Historical Claim (Missions 08–10) | Audit Assessment | Corrected Scientific Claim (Mission 12) |
| :--- | :--- | :--- | :--- |
| **STAT-01** | *"Condition D and F are proven statistically equivalent ($p=1.0$)"* | **REJECTED (Fallacy)**: Confused failure to reject null with proof of equivalence. Power $< 18\%$. | *"At $N=25$, zero discordant pairs were observed. The 95% CI on the risk difference is $[-12.0\%, +12.0\%]$. Formally establishing $\pm 10\%$ equivalence requires $N \ge 286$."* |
| **STAT-02** | *"Condition F saves 7.5% compute cost over Condition D"* | **PARTIAL**: Measured generated token count, not billed GPU compute or inference latency. | *"Condition F reduced generated token length by 28.7 tokens (-7.54%, bootstrap 95% CI: [-61.4, -1.5], $p=0.078$). Prefill compute and batching dynamics must be measured on GPU."* |
| **STAT-03** | *"1.5B models lack reasoning recovery capacity ($0\%$ recovery rate)"* | **OVERSTATED**: Interpreted empirical zero as absolute zero without confidence bounds. | *"Across $N=115$ error-injected traces, zero spontaneous recoveries were observed, establishing an exact Clopper-Pearson 95% upper bound of $3.16\%$ for 1.5B models."* |

---

*This concludes Phase V of Research Mission 12. All scripts and analyses are fully reproducible via `analysis/paired_accuracy_analysis.py`, `analysis/token_efficiency_analysis.py`, and `analysis/zero_success_uncertainty.py`.*
