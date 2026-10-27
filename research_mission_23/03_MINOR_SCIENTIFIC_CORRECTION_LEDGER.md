# Research Mission 23 — Phase 3: Minor Scientific Correction Ledger

## 1. Scope & Objective
This ledger itemizes all minor scientific, textual, typographical, and structural findings identified during the repository-wide audit, documenting their severity, root cause, exact corrective action, and verification status.

---

## 2. Repository-Wide Correction Ledger

| Finding ID | Severity | Affected Artifact | Original Claim / Text | Empirical Evidence | Corrected Formulation | Verification Mechanism | Remaining Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CORR-M01** | Minor | Pilot Contingency Citations | Early reports cited $F=74\%, D=68\%$ without qualification. | `final_verified_outcomes.csv` yields $F=73\%, D=67\%$ ($a=65, d=25$). Discrepancy is `math500_007`. | Primary text reports $F=73.00\%, D=67.00\%$ ($a=65, b=8, c=2, d=25$); Appendix reports $F=74.00\%, D=68.00\%$ as sensitivity. | Verified by `reconstruct_pilot_outcomes.py` and unit tests. | 1 problem (`math500_007`) sensitive to degree stripping. |
| **CORR-M02** | Minor | Causal Terminology | "Direct preservation of internal reasoning state". | StateShift is prompt-mediated; no internal activations are edited. | "Bundled prompt-level continuation intervention preserving valid prefix context". | Audited across manuscript and reports. | Cannot separate prompt text from activation induction. |
| **CORR-M03** | Minor | Dataset Description | "Decontaminated confirmatory benchmark". | MATH-500 test set; pretraining corpus is unknown. | "Disjoint held-out MATH-500 confirmatory sample ($N=231$)". | Set intersection $\mathcal{P}_{\text{pilot}} \cap \mathcal{P}_{\text{confirmatory}} = \emptyset$. | Does not rule out pretraining contamination. |
| **CORR-M04** | Minor | Statistical Power Text | "Experiment is powered to confirm significance". | Power is $80.07\%$ under pilot assumptions; fails if $q \ge 0.14$. | "Preregistered to achieve $80.07\%$ exact power under pilot parameters ($q=0.10, \delta=0.06$)". | `confirmatory_exact_power.py` exact calculation. | Sensitive to elevated sample discordance. |
| **CORR-M05** | Minor | Confidence Interval Reporting | Some text reported point estimates without intervals. | $\hat{\tau} = +0.0600$, $\text{SE} \approx 0.0310$. | Explicitly report asymptotic Wald 95% CI: $[-0.0009, +0.1209]$ and exact OR CI: $[0.80, 38.67]$. | Verified in `06_COMPLETE_PILOT_STATISTICAL_AUDIT.md`. | Asymptotic CI slightly exceeds bound near 0. |
| **CORR-M06** | Minor | Token Headroom Claims | "Truncation parity proves token budgets do not confound recovery". | Condition F starts closer to goal than Condition D derivation. | "Truncation rates are comparable, but effective reasoning headroom differs between conditions". | Generation length analysis in `02_MAJOR_SCIENTIFIC_REMEDIATION.md`. | Headroom asymmetry is inherent to continuation. |
| **CORR-M07** | Minor | GPU Cost Framing | "RunPod provider enforces a hard $1.60 ceiling". | RunPod charges by elapsed wall-clock seconds; client runner enforces ceiling. | "Client-side pre-execution budget ceiling enforced at $1.60 USD". | Runner architecture audit in `run_confirmatory_trial.py`. | Cloud billing carries residual network-disconnect risk. |
| **CORR-M08** | Minor | P-Value Precision | Variously cited as $p=0.11$ or $p=0.109$. | Exact binomial fraction is $\frac{112}{1024} = 0.109375$. | Standardized throughout as $p = 0.109375$ (or $p = 0.1094$ at 4 decimals). | Verified by `scipy.stats.binom`. | None. |
| **CORR-M09** | Minor | Regression Test Count | Earlier text cited 19 tests before Mission 22.2 additions. | Mission 22.2 added 5 definitive contingency tests, totaling 24 tests. | Updated all documents to cite 24 tests across 5 test suites. | Verified by `pytest` run in Phase 8. | None. |
| **CORR-M10** | Minor | Git Commit Hash Tracking | Commit discrepancies between release branches and local work. | Local work branched off `ba2defd` from Mission 22.2. | Explicitly catalog starting commit SHA `ba2defd` on `research/stateshift-mission23-controlled-confirmatory-execution`. | Git log verification in Phase 1. | None. |

---

## 3. Preservation of Historical Artifacts
In accordance with scientific audit protocols, immutable historical artifacts from previous missions (Missions 17–22.1) are preserved unchanged; all corrections are formally registered through superseding reports in `research_mission_23/` and explicit errata notices.
