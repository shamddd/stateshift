# PUBLIC REPOSITORY PRE-AUDIT REPORT

**Project**: StateShift
**Author**: Sham Satish Thakare (Independent Researcher, Pune, Maharashtra, India)
**Research Status**: Working Paper / Ongoing Manuscript Revision (Historical Submission: *Artificial Intelligence*, Elsevier)
**Pre-Audit Timestamp**: `2026-08-20 12:45 UTC`
**Git Branch**: `main`
**HEAD SHA**: `9be50ceeda7dbea20feeb9a915d88852b706a57c`

---

## 1. Repository Inventory

### A. Code & Scripts
* `research-next/stateshift/`: Core experimental data, registry reconciliations, and milestone execution results.
* `submission/aij/`: Elsevier `elsarticle.cls` single-column submission package, BibTeX bibliography, cover letter, figures, and visual audit logs.

### B. Empirical Datasets (Frozen)
1. **Primary Confirmatory Study A**: $N=454, K=16, 29,056$ rollouts ($t \in \{0, 256\}$), $\Gamma_{256} = +0.1176$ ($95\%$ problem-blocked bootstrap CI $[+0.0955, +0.1400]$). Strict decontamination $N_{\text{Strict}}=388, \Gamma_{256,\text{Strict}} = +0.1160$ ($95\%$ CI $[+0.0913, +0.1408]$).
2. **Complete Nine-Checkpoint Trajectory**: $t \in \{0, 32, 64, 96, 128, 160, 192, 224, 256\}$, $8,172$ intermediate rollouts, $\mathbf{\Gamma} = [0.0000, +0.0333, +0.0337, +0.0774, +0.0748, +0.0598, +0.0976, +0.0950, +0.1176]$. Early contrast at $t=32$ ($\Gamma_{32} = +0.0333$, unadjusted 95% CI $[+0.0023, +0.0677]$, $p=0.019$; Bonferroni 95% CI $[-0.0100, +0.0789]$, $p_{\text{adj}}=0.076$).
3. **Unprompted Natural Post-Error Recovery Study B**: $N=200, K=16, 3,200$ unperturbed rollouts, $\text{NEI} = 18.19\%$ ($582/3200$), $\text{NRR} = 30.93\%$ ($180/582$, 95% CI $[27.19\%, 34.82\%]$).

### C. Security & Integrity Verification
* **GPU Spend Ceiling**: $\$0$ additional GPU spend required.
* **Credentials & Secrets**: 0 API keys, credentials, or private paths found.
* **Prohibited Claims Scan**: 0 banned phrase violations in public text.

*Signed by Senior Open-Source Maintainer & Reproducibility Auditor*
