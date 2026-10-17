# StateShift Manuscript Version Map & Cross-Version Audit

**Audit Date**: October 18, 2026  
**Auditor**: Lead Scientific Red-Team Reviewer  

---

## 1. Lineage of Manuscript Iterations

Across the project's evolution, three distinct textual and experimental iterations were produced. They must not be conflated.

| Iteration | Identifier & Title | Target Venue | Benchmark & Domain | Sample Size | Primary Estimand | Key Results | Status |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **Version 0 (Precursor)** | `recovery_eval` / *State-Matched Evaluation of Error Recovery* | IEEE BigData 2026 (Proposed) | Synthetic Python Tool Execution & Micro-benchmarks | Exploratory ($N < 100$) | Unadjusted accuracy difference | Preliminary recovery gap observed | **SUPERSEDED** (Lineage predecessor) |
| **Version 1 (Pre-1G Technical Report)** | `STATESHIFT_TECHNICAL_REPORT.md` / *Quantifying Error-Recovery Adaptation in Autoregressive Models Under Post-Training* | Open Science Preprint Draft | Algorithmic Code Generation (HumanEval / MBPP) | Reported $N=29,056$ | DiD on Pass@1: $\tau_{\text{DiD}}$ | Reported $+28.8$ pp gain, $29.61\%$ residual failure rate | **SUPERSEDED / INCONSISTENT** (Draft template conflating code gen with math outcome numbers) |
| **Version 2 (Authoritative Submission)** | `01_Main_Manuscript.tex` / *StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training* | Elsevier *Artificial Intelligence* (ARTINT-D-26-01491) | MATH-500 (Decontaminated mathematical reasoning) | Confirmatory $N=454, K=16$ ($29,056$ rollouts) + Study B ($3,200$ rollouts) | Matched Interaction Contrast $\Gamma_t = (\mu_{R,t} - \mu_{R,0}) - (\mu_{C,t} - \mu_{C,0})$ | $\Gamma_{256} = +0.1176$ ($p < 0.0001$), 9-point trajectory, $\text{NEI}=18.19\%$, $\text{NRR}=30.93\%$ | **AUTHORITATIVE HISTORICAL SUBMISSION** (Base for NeurIPS reconstruction) |

---

## 2. In-Depth Dissection of Version 1 vs Version 2 Discrepancies

### A. The "29.61%" Residual Failure Rate Mystery Resolved
- In Version 1 (`STATESHIFT_TECHNICAL_REPORT.md`), Section 3 states:
  > *"with an aggregate residual failure regime of 29.61% across all evaluated templates."*
- In Version 2 (`01_Main_Manuscript.tex` & `controlled_endpoint_outcomes.csv`):
  $$\mu_{R,256} = 0.703882 \implies 1 - \mu_{R,256} = 0.296118 = \mathbf{29.61\%}$$
- **Root Cause**: The author computed $100\% - 70.39\% = 29.61\%$ from the real MATH-500 step-256 recovery success rate, but pasted it into an earlier text template describing code-generation benchmarks!

### B. The "+28.8 percentage points" Mystery Resolved
- Version 1 claimed: $\Delta \text{Pass@1} = 37.2\% - 8.4\% = +28.8\text{ pp}$ under error prefixes.
- Version 2 actual empirical data shows:
  $$\Delta_R = \mu_{R,256} - \mu_{R,0} = 0.7039 - 0.3834 = +0.3205 = \mathbf{+32.05\text{ pp}}$$
  $$\Delta_C = \mu_{C,256} - \mu_{C,0} = 0.5921 - 0.3892 = +0.2029 = \mathbf{+20.29\text{ pp}}$$
  $$\Gamma_{256} = +32.05 - 20.29 = \mathbf{+11.76\text{ pp}}$$
- The $+28.8$ pp was an unadjusted marginal difference from an earlier exploratory code-generation pilot that did not control for matched baseline drift ($\Delta_C$).

---

## 3. Mandatory Changes for the NeurIPS Submission Version (Version 3)
1. **Purge all remnants of Version 1 narrative**: No claims of code generation benchmarks unless newly evaluated.
2. **Title Alignment**: Maintain the verified title: *StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training* (or track-tailored variant).
3. **Estimand Rigor**: Explicitly term the metric a **Matched Interaction Contrast** rather than pure Difference-in-Differences to satisfy econometrics/statistical reviewers.
4. **Disclose Non-Monotonicity**: Full transparency regarding intermediate checkpoint fluctuations ($t=160$ and $t=224$).
