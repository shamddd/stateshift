# StateShift Unresolved Scientific Questions & Empirical Boundary Conditions

**Audit Date**: October 18, 2026  
**Auditor**: Senior Reproducibility Auditor & Scientific Red-Team Lead  
**Purpose**: Rigorous Identification of Open Questions and Boundary Conditions for NeurIPS 2027  

---

## 1. Unresolved Empirical Questions

| Question ID | Scientific Question | Current Evidence Status | Why It Remains Unresolved | Impact on Paper & Recommended Action |
|:---|:---|:---:|:---|:---|
| **UQ-01** | **Cross-Architecture Generalization**: Does RLVR induce recovery in non-Qwen architectures (e.g., Llama-3-RL, DeepSeek-R1-Zero)? | **PARTIAL / CONJECTURAL** | Level 1 raw data is restricted to the DeepScaleR-1.5B (Qwen-2.5-Math base) lineage. | Explicitly bound claims: Frame StateShift as an evaluation benchmark and diagnostic methodology applied to DeepScaleR, calling for community evaluation across other model families. |
| **UQ-02** | **Cross-Domain Transfer**: Does mathematical error recovery transfer to Python code synthesis or general reasoning? | **UNRESOLVED** | Early code-gen pilot (+28.8 pp) was confounded and lacked matched control drift. | Do NOT make claims about code generation. Explicitly declare code generation as future work. |
| **UQ-03** | **Micro-Dynamics of Early Emergence (Steps 0..32)**: At what exact step does recovery emerge between 0 and 32? | **UNRESOLVED** | Intermediate checkpoints between steps 0 and 32 were not retained or evaluated during training. | Report that emergence is nominally observable by Step 32 ($\Gamma_{32} = +0.0333$), but exact micro-step localization is bounded by checkpoint availability. |
| **UQ-04** | **Mechanistic Circuit Basis**: What internal attention heads or residual stream mechanisms mediate recovery? | **UNRESOLVED** | StateShift measures behavioral and semantic input-output transitions; internal weight activations were not probed. | Acknowledge as an open mechanistic interpretability frontier. |
| **UQ-05** | **The Persistent Failure Regime (29.61%)**: Why do fully converged models fail to escape $29.61\%$ of corrupted states? | **PARTIALLY EXPLAINED** | Fraction flips (`OP_FRACTION_FLIP`) show attenuated recovery (+5.13 pp); severe dimensional shifts trap the policy. | Present the $29.61\%$ failure regime as a core empirical discovery and challenge for future post-training algorithms. |

---

## 2. Integrity Principle Regarding Missing Experiments

In strict adherence to research integrity:
1. We have NOT simulated or fabricated synthetic rollouts for Llama-3 or Code-generation to create an illusion of completeness.
2. The boundaries of the empirical data ($N=454$ MATH-500 problems, DeepScaleR-1.5B lineage, 29,056 rollouts) are stated transparently.
3. In machine learning scholarship, a deeply powered, cryptographically reproduced, statistically flawless study on a major benchmark and leading model lineage is far superior to a superficially broad study filled with unverified estimates.
