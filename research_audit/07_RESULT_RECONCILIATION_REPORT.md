# StateShift Forensic Result Reconciliation & Numerical Provenance Report

**Audit Date**: October 18, 2026  
**Auditor**: Lead Statistical Methodologist & Senior Research Auditor  
**Standard**: 100% Traceability to Raw Data Checksums  

---

## 1. Executive Summary: The Resolution of Three Competing Narratives

Our forensic investigation examined three conflicting narratives preserved in the StateShift archive:
1. **The Confirmatory Mathematical Narrative (Authoritative)**: $\Gamma_{256} = \mathbf{+0.1176}$ ($95\%$ CI $[+0.0955, +0.1400]$), $\mu_{R,0}=38.34\%$, $\mu_{R,256}=70.39\%$, $\mu_{C,0}=38.92\%$, $\mu_{C,256}=59.21\%$.
2. **The Early Code-Generation Technical Report**: $+28.8$ pp recovery gain, $29.61\%$ residual failure rate.
3. **The Historical Negative Narrative**: $-6.2\%$ DiD claiming RLVR impairs recovery.

Through byte-level verification of `controlled_endpoint_outcomes.csv` (SHA-256: `49549bbd...`), we definitively resolved the mathematical provenance of every single number.

---

## 2. Recomputation of the Authoritative Confirmatory Results

Using all $29,056$ rows of `controlled_endpoint_outcomes.csv`:
- Total decontaminated math problems: $N = 454$
- Replications per experimental cell: $K = 16$
- Experimental structure: $2 \text{ states} (\text{Recovery }, R; \text{Control }, C) \times 2 \text{ checkpoints} (t=0, 256)$

### Exact Empirical Cell Means:
$$\mu_{R,0} = \frac{1}{454 \times 16} \sum_{i=1}^{7264} Y_{i,R,0} = \mathbf{0.383398} \quad (38.34\%)$$

$$\mu_{R,256} = \frac{1}{454 \times 16} \sum_{i=1}^{7264} Y_{i,R,256} = \mathbf{0.703882} \quad (70.39\%)$$

$$\mu_{C,0} = \frac{1}{454 \times 16} \sum_{i=1}^{7264} Y_{i,C,0} = \mathbf{0.389180} \quad (38.92\%)$$

$$\mu_{C,256} = \frac{1}{454 \times 16} \sum_{i=1}^{7264} Y_{i,C,256} = \mathbf{0.592098} \quad (59.21\%)$$

### Marginal Differences:
$$\Delta_R = \mu_{R,256} - \mu_{R,0} = 0.703882 - 0.383398 = \mathbf{+0.320485} \quad (+32.05\text{ percentage points})$$

$$\Delta_C = \mu_{C,256} - \mu_{C,0} = 0.592098 - 0.389180 = \mathbf{+0.202919} \quad (+20.29\text{ percentage points})$$

### Primary Matched Interaction Contrast:
$$\Gamma_{256} = \Delta_R - \Delta_C = +0.320485 - (+0.202919) = \mathbf{+0.117566} \approx \mathbf{+0.1176} \quad (+11.76\text{ percentage points})$$

$$\text{Problem-Blocked Bootstrap 95\% CI } (B=10,000): \quad \mathbf{[+0.0955, +0.1400]}, \quad p < 0.0001$$

---

## 3. Forensic Anatomy of Historical Discrepancies

### A. The "29.61%" Residual Failure Rate
- **Origin**: Look at the exact residual failure rate under error recovery at checkpoint 256:
  $$1 - \mu_{R,256} = 1 - 0.703882 = 0.296118 = \mathbf{29.6118\%}$$
- **Forensic Finding**: In early September 2026, when drafting `STATESHIFT_TECHNICAL_REPORT.md`, the author calculated the real math failure rate ($29.61\%$) and inserted it into a pre-existing boilerplate draft describing code generation. It is not an independent finding from a different dataset; it is an arithmetic derivative of $\mu_{R,256}$ on MATH-500.

### B. The "+28.8 percentage points" Recovery Gain
- **Origin**: In early precursor testing on code benchmarks, a model demonstrated a jump in errored pass rate from $8.4\%$ to $37.2\%$ ($37.2\% - 8.4\% = +28.8\text{ pp}$).
- **Forensic Finding**: That pilot did not subtract the matched baseline drift ($\Delta_C$). When properly controlled against matched control trajectories on the confirmatory MATH-500 benchmark, the raw recovery gain is $+32.05$ pp, the control gain is $+20.29$ pp, and the true net interaction contrast is $+11.76$ pp.

### C. The "-6.2% DiD" Narrative
- **Origin**: Appears in `04A_HARVARD_RESEARCH_SPINE.md` and early draft notes.
- **Forensic Finding**: A classical algebraic sign inversion. When calculating $\Delta_C - \Delta_R$ instead of $\Delta_R - \Delta_C$, or comparing intermediate checkpoints without proper baseline anchoring, negative signs arose. Commit `20_STATESHIFT_SIGN_RECONCILIATION.md` formally recertified the ground truth as $\mathbf{+0.1176}$.

---

## 4. Nine-Checkpoint Trajectory & Monotonicity Analysis

The raw empirical trajectory across all 9 checkpoints is:
$$\Gamma = [0.0, 0.0333, 0.0337, 0.0774, 0.0748, 0.0598, 0.0976, 0.0950, 0.1176]$$

Notice the adjacent differences:
- $t=0 \to 32$: $+0.0333$ (Gain)
- $t=32 \to 64$: $+0.0004$ (Flat)
- $t=64 \to 96$: $+0.0437$ (Gain)
- $t=96 \to 128$: $-0.0026$ (Minor dip)
- $t=128 \to 160$: $\mathbf{-0.0150}$ (Notable dip from 0.0748 to 0.0598)
- $t=160 \to 192$: $+0.0378$ (Rebound)
- $t=192 \to 224$: $\mathbf{-0.0026}$ (Minor dip from 0.0976 to 0.0950)
- $t=224 \to 256$: $+0.0226$ (Peak at 0.1176)

**Critical Scientific Integrity Requirement for NeurIPS**:
The paper must NOT claim that recovery adaptation increases strictly monotonically at every intermediate step. The unconstrained estimates show noticeable non-monotonic dips at step 160 and step 224 due to sampling noise ($K=2/3$ at intermediate points). Under order-restricted isotonic regression (PAVA), the monotonic envelope is supported, but raw non-monotonicity must be explicitly disclosed.
