# StateShift: Research Mission 19 — Comprehensive Scientific Issue Register

**Date:** October 26, 2026  
**Auditor Committee:** Independent Multidisciplinary Scientific Review Panel  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Preprint: arXiv; Secondary: TMLR)  
**Branch:** `research/stateshift-mission19-final-publication`  

---

## 1. Issue Classification Taxonomy

Every issue identified across experimental logs, manuscript revisions, statistical tests, case studies, and reviewer audits is recorded here under strict classification:
- **CRITICAL:** Issues undermining data integrity, authentic provenance, scientific validity, or execution safety.
- **MAJOR:** Issues materially affecting contribution claims, causal identification, statistical inference, or experimental completeness.
- **MINOR:** Issues involving mathematical notation, presentation clarity, figure paths, bibliographic citations, and editorial quality.
- **LIMITATION:** Inherent scope constraints that cannot be resolved without new empirical experiments or broader multi-model allocations.

Allowed Statuses:
- `RESOLVED` (Fully corrected and independently verified)
- `PARTIALLY RESOLVED` (Addressed in manuscript, awaiting future confirmation)
- `OPEN — REQUIRES NEW EXPERIMENT` (Cannot be resolved with existing $N=100$ data)
- `OPEN — REQUIRES AUTHOR INPUT` (Requires PI decision or disclosure)
- `ACCEPTED LIMITATION` (Documented transparently in Section 7 of the manuscript)

---

## 2. Master Issue Register Table

| Issue ID | Severity | Source / Evidence | Affected Section | Proposed Resolution | Implemented Correction | Verification Method | Final Status |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **CRIT-01** | **CRITICAL** | RunPod cost control and runaway process incident (Oct 25). | Operational Architecture | Implement multi-tiered watchdog, cryptographic auth tokens, provider teardown confirmation, and fail-closed locks. | Robust Cost Controller v8, supervisor-first provisioner, `.cloud_execution_locked` fail-closed lock. | Verified $1.1476 settled spend, 0 active pods, 0 active volumes, active lock file. | **RESOLVED** |
| **CRIT-02** | **CRITICAL** | `math500_012` narrative in Mission 17 qualitative report described quadratic factoring $(x-14)(y-14)=196$, contradicting manifest. | Section 4.2 & Section 4.3 | Forensically inspect raw model outputs and manifests; purge any confabulated factoring narrative from the manuscript. | Verified raw generations: `math500_012` is proper divisor counting on 284/220. Purged factoring text in `STATESHIFT_REVISED_SUBMISSION.tex` and updated all case study texts. | Python regex search and manifest alignment audit in `verify_artifact_integrity.py`. | **RESOLVED** |
| **MAJ-01** | **MAJOR** | Primary contrast $\hat{\tau}_{F-D} = +6.00\%$ is not statistically significant at two-sided $\alpha = 0.05$ ($p = 0.109375$). | Abstract, Section 4.3, Section 5 | Cease claiming statistical proof or significant superiority. Accurately report as an empirical directional trend with $4:1$ odds ratio under $N=100$. | Updated Abstract, Section 4.3, and Discussion to state $p = 0.1094$ fails two-sided $\alpha=0.05$ threshold due to $N=100$ sample size power limits. | Recomputed exact binomial McNemar test in `independent_final_statistics.py`. | **RESOLVED** |
| **MAJ-02** | **MAJOR** | Statistical power of $N=100$ cohort was not analytically derived, obscuring why $p = 0.1094$ occurred. | Section 5 (Discussion / Limitations) | Derive exact analytical power for paired McNemar test under observed parameters ($\delta=0.10, \tau=+0.06$). | Implemented exact discrete paired power script; derived that $N=100$ has $47.46\%$ power, and specified $N \ge 216$ ($80\%$) and $N \ge 288$ ($90\%$) for confirmatory scaling. | Validated in `exact_paired_power.py` and `test_independent_audit.py`. | **RESOLVED** |
| **MAJ-03** | **MAJOR** | Causal identification ambiguity: confounding of state preservation by in-context lemma retention and token budget amortization. | Section 2, Section 5 | Acknowledge that Condition F tests an operational intervention package (lemmas in context + token headroom + continuation prompt) rather than pure latent neural state. | Formalized structural causal model in `05_CAUSAL_IDENTIFICATION_FINAL_REVIEW.md` and added explicit causal bounding in Section 5 of manuscript. | Reviewed prompt templates and audited 3 token-exhaustion F-wins (`026`, `092`, `093`). | **RESOLVED** |
| **MAJ-04** | **MAJOR** | Multiplicity control across the 3 experimental contrasts ($\tau_{F-D}, \tau_{E-D}, \tau_{F-A}$) not formally structured under FWER. | Section 4.3 Table 1 | Apply Holm-Bonferroni step-down correction to the 3-hypothesis family at nominal $\alpha = 0.05$. | Formally ranked hypotheses: $\tau_{F-A}$ ($p=0.0117 < 0.0167$, significant); $\tau_{F-D}$ ($p=0.1094 > 0.025$, non-significant); $\tau_{E-D}$ ($p=0.3877 > 0.05$, non-significant). | Scripted in `independent_statistics.py` and verified via pytest. | **RESOLVED** |
| **MAJ-05** | **MAJOR** | Asymmetric negative instances where Condition D won and Condition F failed (`math500_014`, `math500_052`) omitted from qualitative narrative. | Section 4.3 | Transparently document why Condition F failed in these 2 cases. | Detailed the mechanism: complex prefix retention biased model toward convoluted algebraic branches that hit the 768-token limit, whereas restart found a clean Pythagorean shortcut. | Audited in `04_CASE_STUDY_INTEGRITY_INVESTIGATION.md` and incorporated into Section 4.3. | **RESOLVED** |
| **MIN-01** | **MINOR** | Degree symbol normalization mismatch in `math500_007`: model output `\boxed{90}` vs gold `90^\circ`. | Evaluation Pipeline | Implement dual-mode evaluation (strict vs unit-flexible) and prove mathematical invariance of the primary contrast. | Independent evaluator supports both modes; proved that $\hat{\tau}_{F-D} = +6.00\%$ and $b=8, c=2$ are completely identical under both evaluations. | Verified in `test_math_evaluator_strict_concordance`. | **RESOLVED** |
| **MIN-02** | **MINOR** | Figure 1 filename mismatch in LaTeX manuscript (`figures/figure1_architecture.pdf` missing; actual file is `figures/figure1_framework.pdf`). | Manuscript Preamble / Section 1 | Fix figure file path to point to existing PDF vector graphic. | Corrected `\includegraphics` target in `STATESHIFT_REVISED_SUBMISSION.tex` and confirmed compilation compatibility. | Verified file existence on disk (`figures/figure1_framework.pdf`). | **RESOLVED** |
| **MIN-03** | **MINOR** | Discrepancies in bootstrap confidence interval bounds between basic, percentile, and BCa methods. | Table 1 | Recompute all bootstrap intervals with fixed random seed ($B=10^4$, seed 42) and report exact percentiles. | Percentile bootstrap CI $[0.00\%, +12.00\%]$ verified; paired proportion intervals documented in statistical report. | Verified in `test_statistical_metrics_and_exact_mcnemar`. | **RESOLVED** |
| **MIN-04** | **MINOR** | Lack of compiled standalone arXiv PDF package and verified source zip. | Distribution Package | Build complete arXiv package (`STATESHIFT_ARXIV_FINAL.tex`, `references.bib`, figures, source zip, compiled PDF). | Compile via `tectonic` and verify every page visually. | Standalone PDF generated and SHA-256 hashed. | **RESOLVED** |
| **LIM-01** | **LIMITATION** | Evaluation restricted to a single model family (`Qwen2.5-Math-7B-Instruct`) at 7B parameter scale. | Section 5 (Scope Boundaries) | Disclose as a model scope boundary; state that cross-architecture generalization requires future multi-GPU allocations. | Added explicit discussion of DeepSeek-Math and Llama-3-Instruct comparisons in Section 5. | Documented in `08_MINIMUM_DECISIVE_FUTURE_EXPERIMENT.md`. | **ACCEPTED LIMITATION** |
| **LIM-02** | **LIMITATION** | Benchmark restricted to formal competition mathematics (MATH-500). | Section 5 (Scope Boundaries) | Disclose as domain specificity; highlight future extension to open-ended code generation and interactive tool use. | Explicitly discussed in Section 5. | Documented in manuscript and review response. | **ACCEPTED LIMITATION** |
| **LIM-03** | **LIMITATION** | Lack of internal latent activation manipulation (e.g., activation patching / Interchange Intervention Training). | Section 5 (Mechanistic Limits) | Clarify that text-based prompt manipulation cannot isolate pure non-token hidden activations. | Formalized in Section 5 and `05_CAUSAL_IDENTIFICATION_FINAL_REVIEW.md`. | Documented in manuscript limitations. | **ACCEPTED LIMITATION** |

---

## 3. Committee Action Summary

- Total Issues Logged: **14**
- **CRITICAL Issues:** 2 (2 Resolved, 0 Open)
- **MAJOR Issues:** 5 (5 Resolved, 0 Open)
- **MINOR Issues:** 4 (4 Resolved, 0 Open)
- **LIMITATIONS:** 3 (3 Accepted and Documented, 0 Unacknowledged)
- **Overall Integrity Posture:** 100% of fixable engineering, statistical, narrative, and editorial issues are **RESOLVED**. All structural limitations are formally disclosed in the paper.
