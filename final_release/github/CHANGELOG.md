# Changelog

All notable changes to the StateShift research project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-rc1] - 2026-10-27

### Added
- Pre-registered confirmatory evaluation across 231 held-out MATH-500 problems ($924$ neural inferences on NVIDIA RTX 4090).
- Independent cleanroom CPU-only statistical reproduction script (`final_release/reproducibility/reproduce_all_statistics.py`).
- 68-test automated regression suite verifying cryptographic checksums, sample counts, and paired statistical bounds.
- Dual-path mathematical evaluation sensitivity audit (Path A strict vs Path B flexible: 0 discrepancies across 924 outputs).
- Full qualitative accounting of all 23 discordant problems between continuation and forced restart.
- Comprehensive NeurIPS 2027 and arXiv publication packages with compiled PDFs.

### Changed
- Refactored primary manuscript: rewritten from first principles to document the confirmatory null result ($\hat{\tau}_{F-D} = -0.43\text{ pp}, p = 1.000000$).
- Remedied causal mechanism overclaims: formalized Condition F as a bundled compound intervention; deleted the heuristic formula $\text{Net Effect} = \text{Headroom} - \text{Inertia}$.
- Remedied statistical independence overclaims: proved that difference scores suffer from severe measurement error ($\text{Rel} \approx 0.10 - 0.18$), explaining that weak sample correlation ($r = 0.0794$) is compatible with substantial latent association ($r^* \approx 0.60$).
- Remedied equivalence testing overclaims: purged claims of proven practical equivalence within post-hoc $\pm 3.85\%$ margins.
- Remedied discordance invariance overclaims: eliminated the "Discordance Invariance Law"; demonstrated wide confidence bounds ($[-6.99\%, +7.08\%]$) on discordance rate differences.

### Security
- Verified fail-closed cloud execution lock (`.cloud_execution_locked`).
- Zero active cloud resources; confirmed 100% cloud teardown and zero API keys committed.
