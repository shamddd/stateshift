# Pull Request: StateShift Release Candidate v1.0.0-rc1

## Summary of Changes
This pull request merges the complete, audited, and publication-ready StateShift research package from `research/stateshift-final-publication-release` into `main`.

### 1. Scientific Integrity Corrections
- **Causal Mechanism**: Formalized Condition F as a bundled compound prompt intervention ($\text{do}(F) = \{\mathcal{S}\} \cup \{\Delta \mathcal{B}\} \cup \{\mathcal{I}\}$). Removed the heuristic pseudo-equation $\text{Net Effect} = \text{Headroom} - \text{Inertia}$. Categorized the 23 discordant cases ($b=11, c=12$) as exploratory qualitative observations.
- **Statistical Independence**: Disproved earlier claims that $r = 0.0794$ implies cognitive independence. Documented difference-score measurement unreliability ($\text{Rel} \approx 0.10 - 0.18$) and computed the disattenuated latent correlation ($r^* \approx 0.60, R^2 \approx 35.4\%$).
- **Equivalence Testing**: Demonstrated that $\pm 3.85\%$ was a post-hoc circular margin derived from the observed 90% confidence interval. Purged claims of proven equivalence, replacing them with honest frequentist estimation bounds ($[-4.50\%, +3.64\%]$).
- **Discordance Stability**: Purged the "Discordance Invariance Law". Computed exact uncertainty intervals on the difference between pilot and confirmatory discordance ($[-6.99\%, +7.08\%]$), demonstrating that the near-equality of sample proportions ($10.0\%$ vs $9.96\%$) is descriptive.

### 2. Computational & Evaluator Verification
- Complete independent recomputation via `final_release/reproducibility/reproduce_all_statistics.py`.
- Evaluator invariance audit: 0 discrepancies across 924 outputs between Path A (strict) and Path B (relaxed).
- Automated regression suite: 68/68 passing tests.

### 3. Publication Packaging
- Master LaTeX manuscripts (`final_main.tex`, `final_supplement.tex`) compiled via Tectonic to 11-page and 3-page PDFs.
- Dedicated packages for arXiv preprint and NeurIPS 2027 double-blind submission.

## Checklist
- [x] All 68 tests passing locally.
- [x] Zero cloud charges incurred ($0.00 USD).
- [x] Cloud lock active (`.cloud_execution_locked`).
- [x] Zero secrets committed.
- [x] Documentation synchronized.
