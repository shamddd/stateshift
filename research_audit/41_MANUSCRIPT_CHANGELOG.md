# StateShift Complete Manuscript Changelog (AIJ Submission to NeurIPS Candidate)

**Audit Date**: October 18, 2026  
**Auditor**: Lead ML Methodologist & Scientific Red-Team Lead  
**Document Evolution**: `01_Main_Manuscript.tex` (AIJ 2026) $\longrightarrow$ `neurips_submission/main.tex` (NeurIPS 2027)  

---

## 1. Detailed Section-by-Section Changelog

| Section / Dimension | Original Manuscript (AIJ 2026) | Revised Manuscript (NeurIPS 2027 Candidate) | Scientific Rationale |
|:---|:---|:---|:---|
| **Authors & Affiliations** | Single-author named submission (Sham Satish Thakare). | Fully anonymized (`Anonymous Authors`, double-blind review). | Strict compliance with NeurIPS double-blind review policy. |
| **Core Estimand Terminology** | "Difference-in-Differences (DiD) Estimand". | **"State-Matched Interaction Contrast" ($\Gamma_t$)**. | Eliminates econometric reviewer objections regarding observational parallel trends assumptions. Grounded in experimental fixed-effects factorial design. |
| **Step 32 Early Emergence** | Claimed confirmed emergence at step 32 ($p=0.019$). | **Dual reporting**: Unadjusted $p=0.019$, Bonferroni-adjusted $p=0.076$ (CI crosses zero). | Prevents overclaiming under Family-Wise Error Rate (FWER) across 8 trajectory evaluations. |
| **Trajectory Monotonicity** | Claimed monotonic scaling across all checkpoints. | **Isotonic modeling (PAVA)**; explicit reporting of dips at steps 160 and 224. | Transparent reporting of intermediate sampling variance ($K=2/3$) without concealing empirical dips. |
| **Orthogonality Proof** | Omitted in original draft. | **Added Section 5.1**: $r=0.0794, R^2=0.63\%$, $99.37\%$ independent recovery variance. | Proves recovery adaptation is an autonomous capability dimension decoupled from clean accuracy gains. |
| **Error-Operator Stratification** | Omitted in original draft. | **Added Section 7.1 / Table 4**: Constant ($+14.32$ pp), Sign ($+12.33$ pp), Fraction ($+5.13$ pp). | Establishes domain boundaries and reveals why fraction inversions are difficult to recover from. |
| **Difficulty Stratification** | Omitted in original draft. | **Added Section 7.2 / Table 5**: Constant recovery gain across $L_2..L_5$ ($\Delta_R pprox +32$ pp). | Refutes skeptic objection that $\Gamma$ is an artifact of easy-problem ceiling effects. |
| **Test-Time Compute Parity** | Omitted in original draft. | **Added Section 7.3**: Generated token length invariance ($482.47 	o 482.50$ tokens). | Proves recovery is not an artifact of longer reasoning traces or test-time search expansion. |
| **Scope & Generalization** | Unbounded general claims about LLMs. | **Disciplined scope bounding**: Restricted to RLVR mathematical reasoning models (DeepScaleR/Qwen-2.5-Math). | Protects against reviewer critique of single-model / single-domain overclaiming. |
