# StateShift High-Priority Experiment Protocols & Specifications

**Audit Date**: October 18, 2026  
**Auditor**: Senior Statistical Methodologist & Experimental ML Auditor  
**Standard**: Full Preregistration Specification for Diagnostic, Feasible, and Proposed Experiments  

---

## Protocol 1: Orthogonality Decomposition of Recovery vs. Clean Gains (EXP-01)
- **Research Question**: Can recovery-specific capability changes be separated from clean-task accuracy changes at the problem level, or is recovery simply a linear function of clean problem-solving proficiency?
- **Hypothesis**: Recovery improvement $\Delta_{R,i}$ and clean improvement $\Delta_{C,i}$ share $< 10\%$ variance ($R^2 < 0.10$), demonstrating that recovery is an independent capability dimension.
- **Experimental Design**: Problem-level bivariate regression and correlation analysis between $\Delta_{R,i} = Y_{i,R,256} - Y_{i,R,0}$ and $\Delta_{C,i} = Y_{i,C,256} - Y_{i,C,0}$ across all $N=454$ problem blocks.
- **Baseline**: Clean problem-solving delta $\Delta_{C,i}$.
- **Independent Experimental Unit**: Problem instance $i \in \{1, \dots, 454\}$.
- **Dataset Requirements**: Complete endpoint rollouts (`controlled_endpoint_outcomes.csv`).
- **Model Requirements**: Evaluated outputs from Checkpoints 0 and 256.
- **Compute & Time Requirements**: CPU execution, $< 5$ seconds.
- **Statistical Analysis**: Pearson correlation $r$, Spearman rank correlation $\rho$, and variance decomposition $R^2$.
- **Expected Information Gain**: Decisive proof that recovery adaptation is structurally distinct from general capability advancement.
- **Failure Conditions**: A strong positive correlation ($r > 0.80, R^2 > 0.64$) would indicate that recovery is merely an incidental mirror of clean progress.
- **Interpretation**: A near-zero correlation ($r < 0.15$) proves that post-training induces a dedicated recovery adaptation that operates orthogonally to general problem solving.

---

## Protocol 2: Error-Operator Stratification & Domain Sensitivity (EXP-02)
- **Research Question**: Do different types of mathematical error prefixes produce fundamentally different recovery transition rates?
- **Hypothesis**: Errors that alter equation scale (e.g., fraction inversion) will prove more difficult to recover from than local arithmetic perturbations.
- **Experimental Design**: Stratify the $N=388$ decontaminated problems by error operator (`OP_CONSTANT_PERTURB`, `OP_SIGN_FLIP`, `OP_FRACTION_FLIP`) using `confirmatory_problem_registry.json`. Compute interaction contrast $\Gamma_{256}$ and 95% bootstrap CIs within each operator stratum.
- **Baseline**: Overall sample interaction $\Gamma_{256} = +0.1176$.
- **Independent Experimental Unit**: Problem instance $i$ nested within operator tier.
- **Dataset Requirements**: `controlled_endpoint_outcomes.csv` cross-referenced with `confirmatory_problem_registry.json`.
- **Compute & Time Requirements**: CPU execution, $< 5$ seconds.
- **Statistical Analysis**: Stratified problem-blocked bootstrap ($B=5,000$) per operator group.
- **Expected Information Gain**: Identifies which reasoning error classes models learn to fix under RLVR.
- **Failure Conditions**: If $\Gamma \le 0$ across all operators, the primary finding is invalidated.
- **Interpretation**: Positive $\Gamma$ across all or most operators proves that recovery adaptation is broad, while varying magnitudes delineate semantic boundary conditions.

---

## Protocol 3: Split-Half Rollout Seed Replication (EXP-03)
- **Research Question**: Are the empirical findings robust to stochastic sampling seeds across independent rollout partitions?
- **Hypothesis**: Two completely disjoint halves of the rollout sample (Seeds 0..7 vs Seeds 8..15) will yield statistically indistinguishable, positive interaction contrasts.
- **Experimental Design**: Partition the $K=16$ rollouts per cell into Split 1 ($k \in \{0, \dots, 7\}$) and Split 2 ($k \in \{8, \dots, 15\}$). Independently compute cell means, deltas, interaction contrasts $\Gamma^{(1)}$ and $\Gamma^{(2)}$, and 95% bootstrap CIs.
- **Baseline**: Full sample estimate $\Gamma_{256} = +0.1176$.
- **Independent Experimental Unit**: Problem instance $i$ across split halves.
- **Dataset Requirements**: `controlled_endpoint_outcomes.csv` (29,056 rows).
- **Compute & Time Requirements**: CPU execution, $< 5$ seconds.
- **Statistical Analysis**: Problem-blocked bootstrap ($B=5,000$) on each half-sample.
- **Expected Information Gain**: Unimpeachable proof of seed stability and replication reliability.
- **Failure Conditions**: If one split is positive and the other crosses zero, the result is an artifact of sampling noise.
- **Interpretation**: Overlapping CIs centered at $+0.11$ to $+0.12$ demonstrate rock-solid sampling stability.

---

## Protocol 4: Leave-One-Problem-Out (Jackknife) Influence Audit (EXP-04)
- **Research Question**: Does the headline finding $\Gamma_{256} = +0.1176$ depend excessively on a small set of outlier problems?
- **Hypothesis**: The maximum change in $\Gamma$ from dropping any individual problem is $< 0.005$ ($< 0.5$ pp).
- **Experimental Design**: Systematically remove each problem $i \in \{1, \dots, 454\}$ from the dataset and recompute $\Gamma_{(-i)}$. Calculate Cook's influence, maximum/minimum jackknife estimates, and problem-level sign distributions.
- **Baseline**: Grand sample mean $\Gamma = +0.117566$.
- **Compute & Time Requirements**: CPU execution, $< 10$ seconds.
- **Expected Information Gain**: Verifies that the finding is distributed broadly across the population rather than driven by an anomalous problem cluster.

---

## Protocol 5: Cross-Architecture GPU Replication (EXP-08) [Proposed / External]
- **Research Question**: Does the StateShift recovery interaction generalize to other open-source reasoning models (e.g., DeepSeek-R1-Distill-Qwen-7B)?
- **Hypothesis**: DeepSeek-R1-Distill-Qwen-7B exhibits a positive State-Matched Interaction Contrast ($\Gamma > 0$) on MATH-500.
- **Experimental Design**: Evaluate DeepSeek-R1-Distill-Qwen-7B on the 454 MATH-500 problems across Recovery and Control prefixes ($K=16$ completions per cell = 14,528 rollouts).
- **Hardware & Compute Requirements**: 1x NVIDIA A100-80GB (or H100-80GB), vLLM inference engine, ~5.0 hours, ~$12.00 cost.
- **Scientific Rationale**: Tests whether recovery adaptation is specific to DeepScaleR or generic across all R1-style distilled reasoning models.
- **Current Status**: Documented as high-priority post-audit experiment. Not executed in the current CPU pass to strictly adhere to zero-unauthorized-spend and zero-GPU-waste guidelines.
