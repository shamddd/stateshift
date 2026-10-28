# Phase C: Preregistered Statistical Analysis Plan (SAP)

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22 — Confirmatory Trial Preflight  
**Date & Timestamp**: 2026-10-27T02:27:00+05:30  
**Target Venue**: NeurIPS 2027 Main Track  
**Registration Status**: FROZEN PRIOR TO CLOUD EXECUTION  

---

## 1. Administrative Information & Trial Registration

- **Trial Identifier**: `STATESHIFT-CONFIRMATORY-2027-N231`
- **Protocol Version**: 1.0 (Frozen)
- **Principal Investigator**: Sham Satish Thakare
- **Sample Allocation**: $N = 231$ independent mathematical problems across 4 matched conditions ($924$ total requests).
- **Execution Target**: Single physical NVIDIA RTX 4090 GPU (RunPod Secure Cloud).

---

## 2. Scientific Objectives and Hypotheses

### 2.1 Primary Objective
To determine whether preserving valid antecedent reasoning states verbatim during error recovery (Condition F) yields superior mathematical problem-solving accuracy compared to forcing a complete restart from scratch (Condition D) on problems where an error occurred.

### 2.2 Primary Statistical Hypotheses
Let $Y_{i,F} \in \{0, 1\}$ denote the binary correctness of model generation on problem $i$ under Condition F, and $Y_{i,D} \in \{0, 1\}$ denote binary correctness on problem $i$ under Condition D.

The paired $2 \times 2$ contingency table across $N$ problems is defined as:

| | Condition D Correct ($Y_D = 1$) | Condition D Incorrect ($Y_D = 0$) | Total |
| :--- | :---: | :---: | :---: |
| **Condition F Correct ($Y_F = 1$)** | $a$ | $b$ | $a + b$ |
| **Condition F Incorrect ($Y_F = 0$)** | $c$ | $d$ | $c + d$ |
| **Total** | $a + c$ | $b + d$ | $N = 231$ |

- **Null Hypothesis ($H_{0,\text{primary}}$)**: The probability of discordant recovery favoring Condition F equals the probability of discordant recovery favoring Condition D:
  $$H_{0,\text{primary}}: P(Y_F = 1, Y_D = 0) = P(Y_F = 0, Y_D = 1) \iff b = c$$
- **Alternative Hypothesis ($H_{1,\text{primary}}$)**:
  $$H_{1,\text{primary}}: P(Y_F = 1, Y_D = 0) \neq P(Y_F = 0, Y_D = 1) \iff b \neq c$$

### 2.3 Primary Estimand
The marginal risk difference (accuracy difference):
$$\hat{\tau}_{F-D} = \frac{1}{N} \sum_{i=1}^N (Y_{i,F} - Y_{i,D}) = \frac{b - c}{N}$$
Reported with exact Clopper-Pearson or Wilson score 95% confidence intervals.

---

## 3. Primary Statistical Test

- **Test Statistic**: Exact two-sided McNemar test conditional on the total number of discordant pairs $n_d = b + c$.
- Under $H_0$, $b \sim \text{Binomial}(n_d, 0.5)$.
- The exact two-sided p-value is computed as:
  $$p_{\text{exact}} = 2 \times \min\left( \sum_{k=b}^{n_d} \binom{n_d}{k} 0.5^{n_d}, \sum_{k=0}^{b} \binom{n_d}{k} 0.5^{n_d} \right)$$
  (capped at 1.0 when $b = c$).
- **Significance Level**: $\alpha = 0.05$ (two-sided).
- **Decision Rule**: Reject $H_{0,\text{primary}}$ if $p_{\text{exact}} < 0.05$.

---

## 4. Secondary Hypotheses and Multiplicity Management

### 4.1 Secondary Hypotheses
1. **Secondary Contrast 1 (Intervention vs. Zero-Shot)**:
   - Contrast: Condition F vs. Condition A.
   - Estimand: $\hat{\tau}_{F-A} = \frac{b_{FA} - c_{FA}}{N}$.
   - Tests whether recovery intervention outperforms unprompted fresh reasoning.
2. **Secondary Contrast 2 (State-Preserving vs. Unconstrained Repair)**:
   - Contrast: Condition F vs. Condition E.
   - Estimand: $\hat{\tau}_{F-E} = \frac{b_{FE} - c_{FE}}{N}$.
   - Tests whether explicit state preservation outperforms generic instructions to identify and repair errors.

### 4.2 Error Control Architecture
To preserve the family-wise error rate (FWER) across confirmatory claims:
- **Hierarchical Gatekeeping**: Secondary hypotheses are evaluated for confirmatory significance **only if** the primary hypothesis ($F$ vs. $D$) rejects $H_0$ at $\alpha = 0.05$.
- If the primary test rejects, the two secondary tests are controlled via the **Holm-Bonferroni step-down procedure** at overall $\alpha = 0.05$:
  1. Sort secondary p-values: $p_{(1)} \le p_{(2)}$.
  2. Test $p_{(1)}$ at $\alpha / 2 = 0.025$. If rejected, test $p_{(2)}$ at $\alpha = 0.05$.

---

## 5. Outcome Assessment & Cleanroom Evaluation Engine

### 5.1 Extraction Protocol
1. Scan raw model output for `\boxed{...}` tags, supporting nested braces via recursive regex/stack parsing.
2. If multiple boxed expressions occur, the final boxed expression is designated as the terminal answer.
3. If no boxed expression is found, the generation is classified as an extraction failure ($Y = 0$).

### 5.2 Mathematical Equivalence Engine
The extracted candidate string $S_{\text{cand}}$ is compared against the ground truth $S_{\text{gold}}$ using:
1. Exact string match after canonical normalization (stripping outer whitespace, commas in large numbers, terminal periods, LaTeX display wrappers).
2. Symbolic algebraic equivalence via SymPy:
   $$\text{simplify}(E_{\text{cand}} - E_{\text{gold}}) == 0$$
3. Exact fraction and polynomial reduction (handling $\frac{1}{2}$ vs $0.5$, $\sqrt{12}$ vs $2\sqrt{3}$, factored polynomials vs expanded forms).

---

## 6. Data Integrity and Stopping Rules

1. **Fixed Sample Size Rule**: Exactly $N = 231$ problems will be processed.
2. **Zero Sequential Peeking**: No interim statistical testing or early stopping will be performed. P-values will be calculated only after all 924 generations are collected and verified.
3. **Handling of Failed Generations**:
   - Generation timeouts or CUDA OOM errors (if any): Coded as $Y = 0$.
   - Malformed completions: Coded as $Y = 0$.
   - Under no circumstances will a problem be dropped or replaced post-randomization.
4. **Preregistration Hash**:
   This SAP document and its companion test scripts are committed to Git with immutable commit hashes prior to GPU execution.
