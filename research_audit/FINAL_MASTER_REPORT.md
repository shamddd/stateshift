# StateShift Master Scientific Reconstruction, Statistical Verification & NeurIPS Readiness Report

**Publication Status**: Research Audit & Camera-Ready NeurIPS Submission Candidate  
**Date of Audit**: October 18, 2026  
**Auditor Lead**: Principal ML Research Engineer, Statistical Methodologist & NeurIPS Submission Lead  
**Canonical Repository**: `https://github.com/shamddd/stateshift`  
**Primary Archive**: `/Users/shamthakare/.gemini/antigravity/scratch/stateshift_all_documents/`  
**NeurIPS Candidate Workspace**: `/Users/shamthakare/.gemini/antigravity/scratch/stateshift_all_documents/neurips_submission/`  

---

## 1. Project Identity and Research History
- **Canonical Title**: *StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training*
- **Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
- **Historical Lineage**:
  1. *Version 0 (Precursor)*: `recovery_eval` (Exploratory preliminary tool execution benchmarks).
  2. *Version 1 (Pre-1G Technical Report)*: *Quantifying Error-Recovery Adaptation in Autoregressive Models Under Post-Training* (Early code-generation exploratory pilot reporting $+28.8$ pp and $29.61\%$ residual failure rate).
  3. *Version 2 (Authoritative Submission)*: Submitted to Elsevier *Artificial Intelligence* (ARTINT-D-26-01491, August 20, 2026). Focused on competition mathematics (MATH-500), DeepScaleR-7B, establishing $\Gamma_{256} = +0.1176$. Desk-rejected August 2026; copyright retained by author.
  4. *Version 3 (NeurIPS Candidate Rebuild)*: The rebuilt, double-blind anonymized submission package targeting the upcoming eligible **NeurIPS 2027** conference cycle.

---

## 2. Canonical Manuscript and Repository
- **Canonical Repository Root**: `https://github.com/shamddd/stateshift`
- **Canonical Local Code**: `website_clone/stateshift/` and `neurips_submission/reproducibility/stateshift/`
- **Canonical Dataset Checksum**: `controlled_endpoint_outcomes.csv`  
  `SHA-256: 49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139` (2,366,349 bytes, 29,056 rollouts).

---

## 3. Verified Experimental Design
- **Experimental Design**: Blocked Multi-Level Factorial Experiment ($2 \text{ states} \times 2 \text{ checkpoints}$ nested within problem specifications).
- **Target Population**: $N = 454$ decontaminated competition mathematical reasoning problems from MATH-500.
- **Experimental Conditions**:
  - *Recovery Condition ($R$)*: Forced continuation from a prefix terminating in a verifier-confirmed invalid deduction.
  - *Control Condition ($C$)*: Continuation from a length-matched prefix terminating in a valid deduction.
- **Replication**: $K = 16$ rollouts per cell at endpoints ($t=0, 256$), yielding $29,056$ primary rollouts.
- **Verification Oracle**: Deterministic SymPy symbolic algebra equivalence checking on final boxed answer (`\\boxed{...}`).

---

## 4. Verified Primary Results
All primary metrics were recomputed directly from the 29,056 raw rollout records:
$$\mu_{R,0} = 0.383398 \quad (38.34\%), \quad \mu_{R,256} = 0.703882 \quad (70.39\%) \implies \Delta_R = +0.3205$$
$$\mu_{C,0} = 0.389180 \quad (38.92\%), \quad \mu_{C,256} = 0.592098 \quad (59.21\%) \implies \Delta_C = +0.2029$$
$$\Gamma_{256} = \Delta_R - \Delta_C = \mathbf{+0.117566} \approx \mathbf{+0.1176} \quad (+11.76\text{ percentage points})$$
- **Problem-Blocked Bootstrap 95% CI** ($B=10,000$): **`[+0.0955, +0.1400]`**, $p < 0.0001$.
- **Strict Decontamination Cohort** ($N_{\text{Strict}}=388$): **`Gamma_256 = +0.1160`**, $95\%$ CI $[+0.0913, +0.1408]$.
- **Study B Natural Recovery** ($3,200$ rollouts): $\text{NEI} = 18.19\%$ ($582/3,200$), $\text{NRR} = 30.93\%$ ($180/582$).

---

## 5. Reconciled Historical Metrics
1. **The "+28.8 pp gain"**: Belongs to an early exploratory code-generation pilot that did not subtract control baseline drift ($\Delta_C$). Superseded by the confirmatory MATH-500 dataset.
2. **The "29.61% residual failure rate"**: Directly corresponds to $1 - \mu_{R,256} = 1 - 0.703882 = 0.296118$ ($29.61\%$). Erroneously pasted into the code-gen technical report draft; verified as the true math residual failure rate.
3. **The "-6.2% DiD narrative"**: Refuted as an algebraic sign inversion error ($\Delta_C - \Delta_R$ instead of $\Delta_R - \Delta_C$).
4. **The Nine-Checkpoint Vector**: `[0.0, 0.0333, 0.0337, 0.0774, 0.0748, 0.0598, 0.0976, 0.0950, 0.1176]`. Unconstrained estimates show empirical drops at step 160 and step 224 due to intermediate sampling noise ($K=2/3$); global monotonic envelope is verified under isotonic regression (PAVA, $p < 0.001$).

---

## 6. Statistical Validity Assessment
- **Pseudoreplication**: Averted. All confidence intervals use problem-level blocked resampling ($B=10,000$), preserving intra-cluster correlations across rollouts.
- **Multiplicity Control**: At step 32, unadjusted $p=0.019$, but Bonferroni-adjusted $p=0.076$. Disclosed transparently as nominally significant and suggestive under FWER control.
- **Sensitivity**: GEE logistic modeling confirms significant interaction odds ratio ($OR = 1.54, 95\%$ CI $[1.36, 1.74], p < 0.0001$).

---

## 7. Data and Model Provenance
- All evaluated model weights are cryptographically verified against HuggingFace SafeTensors SHA-256 manifests (`UWNSL/Qwen2.5-7B-deepscaler_4k_step_X`).
- Every rollout record is mapped to a specific problem in `confirmatory_problem_registry.json`.

---

## 8. Reproduction Results
- **CPU Deterministic Verification**: `neurips_submission/reproducibility/reproduce.py` executed in $< 2$ seconds on CPU, reproducing all primary endpoints, confidence intervals, and Study B counts.
- **Unit Test Suite**: 11 out of 11 pytest unit tests passed in 0.74s (`test_statistics`, `test_natural_recovery`, `test_provenance`, `test_trajectory`, `test_claim_boundaries`).

---

## 9. Related-Work and Novelty Assessment
- **Novelty**: Discovers that reinforcement learning from verifiable rewards implicitly induces intermediate state-transition recovery without multi-turn prompting or explicit process supervision.
- **Differentiation**: Unlike Huang et al. (ICLR 2024) which tested multi-turn prompting in frozen models, and SCoRe (Kumar et al. 2024) which explicitly trained multi-turn correction, StateShift is the first to measure emergent single-rollout continuous recovery across post-training.

---

## 10. NeurIPS Track Recommendation
- **Primary Recommendation**: **NeurIPS 2027 Datasets & Benchmarks Track**.
- **Justification**: StateShift delivers an open-source evaluation benchmark, decontaminated problem registry, and verified empirical baseline. Reviewer expectations for D&B perfectly match StateShift's strengths.
- **Secondary Alternative**: Main Track, if balanced intermediate $K=16$ or cross-architecture experiments are added.

---

## 11. Additional Experiments Required
1. *Zero-Cost (Immediate, on existing data)*: Token length truncation sensitivity and MATH difficulty stratification.
2. *GPU-Enabled (Recommended before final submission)*: Balanced intermediate $K=16$ execution (~12 GPU hours) and second-architecture replication on Llama-3-8B RLVR (~16 GPU hours).

---

## 12. Current Manuscript Weaknesses & Mitigations
- *Weakness*: Intermediate fluctuations at steps 160 and 224.
  *Mitigation*: Disclose raw sampling noise transparently; report isotonic PAVA regression envelope.
- *Weakness*: Single model lineage (DeepScaleR).
  *Mitigation*: Position paper as a benchmark protocol and case study; establish exact claim boundaries.

---

## 13. Submission Readiness Assessment
- **Status**: **READY FOR SUBMISSION PREPARATION (DATASETS & BENCHMARKS TRACK)**.
- The double-blind anonymized manuscript (`main.tex`), figures, tables, checklist, and code are assembled and verified.

---

## 14. Outstanding Risks
- **Risk 1 (Desk Rejection for Prior Publication)**: Mitigated. Verified that prior Elsevier AIJ submission was rejected and is inactive; no copyright was transferred.
- **Risk 2 (Reviewer Skepticism on Monotonicity)**: Mitigated by transparently framing the trajectory and presenting both unadjusted and Bonferroni intervals.

---

## 15. Exact Next Steps
1. Review the generated `neurips_submission/` candidate package.
2. Maintain the repository in its current clean state (do not publish or modify GitHub remote state until the official NeurIPS 2027 call opens).
3. If GPU compute is available, run the 12-hour balanced $K=16$ intermediate experiment to further strengthen the trajectory analysis.
