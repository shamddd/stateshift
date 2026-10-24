# PHASE IX: UNIFIED STATISTICAL VALIDATION & INFERENCE PROTOCOL
## Formal Clustered Estimation, Multiplicity Correction, and Truncation Sensitivity Framework

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference  
**Date**: October 24, 2026  
**Methodologist**: Statistical Methodologist & Experimental Design Specialist  
**Deliverable**: [`09_UNIFIED_STATISTICAL_VALIDATION.md`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_10/09_UNIFIED_STATISTICAL_VALIDATION.md)

---

## 1. Unit of Analysis & Clustered Problem Design

In mathematical reasoning evaluations, presenting multiple prompt conditions (e.g., Zero-Shot, Control Prefix, Corrupted Recovery, Forced Restart, State-Preserving Repair) to the same underlying problem statement generates **statistically dependent observations within problem clusters**.

### Statistical Invariant 1: Problem-Level Clustering
Let $i \in \{1, \dots, N\}$ index unique mathematical problems, and let $j \in \{1, \dots, K\}$ index experimental conditions. The binary response $Y_{ij} \in \{0, 1\}$ exhibits within-problem correlation:
$$\text{Cov}(Y_{ij}, Y_{ij'}) > 0 \quad \text{for } j \neq j'$$
**Violation Warning**: Treating $N \times K$ rollouts as independent observations artificially inflates degrees of freedom, compresses standard errors by $\approx \sqrt{K}$, and yields spurious $p$-values.
**StateShift Standard**: All standard errors, confidence intervals, and hypothesis tests are computed using **clustered problem-level inference** (paired McNemar tests or cluster-robust GEE sandwich estimators).

---

## 2. Formal Statistical Estimators

### 2.1 Paired Risk Difference & Exact McNemar Test
For any two conditions $A$ and $B$ evaluated on the identical problem set $i = 1, \dots, N$:
$$\hat{\Delta}_{A - B} = \bar{Y}_A - \bar{Y}_B = \frac{n_{10} - n_{01}}{N}$$
where $n_{10}$ denotes problems solved under Condition $A$ but failed under $B$, and $n_{01}$ denotes problems solved under $B$ but failed under $A$.

- **Exact Binomial $p$-value**:
  $$p = 2 \cdot \sum_{k = \max(n_{10}, n_{01})}^{n_{10} + n_{01}} \binom{n_{10} + n_{01}}{k} 0.5^{n_{10} + n_{01}}$$
- **Cluster-Robust Standard Error**:
  $$\text{SE}(\hat{\Delta}) = \frac{1}{N} \sqrt{n_{10} + n_{01} - \frac{(n_{10} - n_{01})^2}{N}}$$
- **95% Confidence Interval**:
  $$\text{CI}_{95\%} = \hat{\Delta} \pm 1.96 \cdot \text{SE}(\hat{\Delta})$$

---

## 3. Multiplicity Correction (Benjamini-Hochberg FDR)

When testing hypotheses across $M = 10$ perturbation operators (OP01 through OP10), unadjusted hypothesis testing inflates family-wise Type I error to:
$$\alpha_{\text{family}} = 1 - (1 - 0.05)^{10} = 40.13\%$$

### Benjamini-Hochberg (BH) Procedure
1. Rank all $M$ raw $p$-values in ascending order: $p_{(1)} \le p_{(2)} \le \dots \le p_{(M)}$.
2. Find the largest rank $k$ satisfying:
   $$p_{(k)} \le \frac{k}{M} \cdot Q \quad (\text{with false discovery rate } Q = 0.05)$$
3. Declare all hypotheses $i \le k$ statistically significant.

---

## 4. Truncation Sensitivity Bounds

To account for incomplete responses hitting token limits, we specify dual sensitivity bounds for any performance estimator $\hat{\theta}$:

1. **Intention-to-Evaluate (Conservative Lower Bound, $\hat{\theta}_{\text{ITE}}$)**:
   All truncated rollouts ($Y_i$) are treated as failed attempts ($Y_i = 0$):
   $$\hat{\theta}_{\text{ITE}} = \frac{N_{\text{correct}}}{N_{\text{total}}}$$
2. **Completion-Conditioned (Optimistic Upper Bound, $\hat{\theta}_{\text{CC}}$)**:
   Evaluated solely on rollouts that successfully reached a terminal boxed conclusion:
   $$\hat{\theta}_{\text{CC}} = \frac{N_{\text{correct}}}{N_{\text{completed}}} = \frac{N_{\text{correct}}}{N_{\text{total}} - N_{\text{truncated}}}$$

**Mandatory Reporting Policy**: Every headline table in StateShift manuscripts must report both $\hat{\theta}_{\text{ITE}}$ and $\hat{\theta}_{\text{CC}}$, explicitly highlighting the truncation gap $\Delta_{\text{trunc}} = \hat{\theta}_{\text{CC}} - \hat{\theta}_{\text{ITE}}$.

---

## 5. Exploratory vs. Confirmatory Registry

To maintain research integrity and prevent p-hacking:

| Campaign | Experiment Range | Scientific Status | Hypotheses & Protocols |
| :--- | :--- | :---: | :--- |
| **Stage A (Mission 09)** | Experiments A01 – A20 | **Exploratory** | Unconstrained screening, prompt parameter exploration |
| **Mission 10 Phase II** | Token Budget Sweep | **Confirmatory** | Pre-specified budgets: 256, 512, 768, 1024 tokens |
| **Mission 10 Phase IV** | Recovery vs. Restart | **Confirmatory** | Pre-specified primary contrast: Condition F vs. D on common endpoint |
| **Stage B (RunPod)** | Frontier 7B Scale-Up | **Confirmatory** | Pre-registered 7B checkpoints, layer probe depths, budget $\le \$10.00$ |
