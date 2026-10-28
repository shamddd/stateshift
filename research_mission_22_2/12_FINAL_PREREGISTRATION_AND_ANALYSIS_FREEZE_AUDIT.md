# Research Mission 22.2 — Final Preregistration and Analysis Freeze Audit

## 1. Preregistration Governance & Freeze Protocol
To prevent $p$-hacking, outcome switching, and post-hoc data curation, the StateShift Confirmatory Trial analysis protocol is permanently locked under **Preregistration Freeze V2.2**.

---

## 2. Statistical Analysis Specifications

### Primary Confirmatory Hypothesis
- **Hypothesis $H_0$**: $\psi = 0.5 \iff p_{01} = p_{10}$ (Condition F does not differ from Condition D).
- **Hypothesis $H_1$**: $\psi \ne 0.5 \iff p_{01} \ne p_{10}$ (Condition F differs from Condition D).
- **Primary Estimator**: Difference in paired proportions:
  $$\hat{\tau}_{F-D} = \frac{b - c}{N} = \frac{1}{N} \sum_{i=1}^N (Y_{Fi} - Y_{Di})$$
- **Primary Statistical Test**: Finite-sample two-sided exact binomial McNemar test:
  $$p_{\text{exact}} = 2 \times \min\left( \sum_{j=b}^{n_d} \binom{n_d}{j} 0.5^{n_d}, \sum_{j=0}^b \binom{n_d}{j} 0.5^{n_d} \right)$$
- **Significance Level**: $\alpha = 0.05$ (two-sided).
- **Decision Rule**: Reject $H_0$ if and only if $p_{\text{exact}} \le 0.05$ and $\hat{\tau}_{F-D} > 0$.

### Secondary Hypotheses & Multiplicity Control
Secondary paired contrasts will be tested in hierarchical order:
1. Contrast 1: Explicit Repair (E) vs Forced Restart (D).
2. Contrast 2: State-Preserving Recovery (F) vs Explicit Repair (E).
3. Contrast 3: Forced Restart (D) vs Zero-Shot Baseline (A).
4. Contrast 4: State-Preserving Recovery (F) vs Zero-Shot Baseline (A).
- **Multiplicity Control**: Benjamini-Hochberg False Discovery Rate (FDR) adjustment at $q = 0.05$ across the family of secondary contrasts.

---

## 3. Missing Data, Truncation, and Extraction Policy

1. **No Data Imputation**: Zero synthetic or imputed data points are permitted under any circumstances.
2. **Truncation Protocol**: If an inference generation hits the 768-token ceiling (`finish_reason = length`), the partial generation string is retained verbatim in the record. The cleanroom boxed extractor will attempt extraction. If no valid mathematical answer is derived within the token budget, the observation is scored as `False`.
3. **Hardware or Transport Failures**: If a request encounters a physical transport drop or hardware timeout, the runner retry policy allows up to 3 automatic retries with exponential backoff. If all 3 fail, execution halts; no partial re-sampling is performed.

---

## 4. Stopping Rules & Interim Analysis Prohibition

- **Zero Interim Peeking**: No statistical significance tests or effect size estimates may be evaluated until all 924 neural inference requests have been executed and saved to disk.
- **Fixed Horizon**: The sample size is strictly fixed at $N = 231$ problems (924 requests).
- **Stopping Criteria**: Execution terminates only upon either (a) 100% completion of 924 requests, (b) emergency expenditure limit hit ($1.60 USD), or (c) unrecoverable hardware fault.
