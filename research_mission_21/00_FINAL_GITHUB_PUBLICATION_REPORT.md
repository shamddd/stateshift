# Research Mission 21: Final GitHub Publication Report

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Target Conference**: NeurIPS 2027 Main Conference Track
**Preprint Destination**: arXiv
**Secondary Venue**: TMLR
**Official Repository**: [`https://github.com/shamddd/stateshift`](https://github.com/shamddd/stateshift)
**Date & Timestamp**: 2026-10-26T17:31:00+05:30

---

## 1. Final Verdict

### **VERDICT: GREEN — LIVE ON MAIN AND VERIFIED**

Every mandatory publication, verification, and scientific integrity condition has been fully satisfied:
1. **Intended Release Merged**: Pull Request #1 successfully merged into `main`.
2. **Remote Commit Verified**: Remote `main` branch confirmed at merge commit `aa49a81d4db5dd9fe68df95c32e07e43d36fd88f`.
3. **CI Checks Passing**: 14/14 GitHub Actions check runs passed with status `success`.
4. **Key Public Artifacts Accessible**: All datasets, preprint PDF, LaTeX source, and reproducibility scripts are publicly downloadable via HTTPS without authentication.
5. **Data & Manuscript Integrity**: Cryptographic SHA-256 hashes match 100% of preregistered expectations.
6. **Security & Financial Clear**: 0 leaked credentials; $0.00 spent on cloud; RunPod balance $10.1065 USD preserved intact.
7. **Fresh Clone Reproducibility**: 100% of replication scripts and test suites pass from a clean clone in an isolated temporary directory.

---

## 2. Official GitHub Verified URLs

- **Official Repository**: [`https://github.com/shamddd/stateshift`](https://github.com/shamddd/stateshift)
- **Main Branch**: [`https://github.com/shamddd/stateshift/tree/main`](https://github.com/shamddd/stateshift/tree/main)
- **Merged Pull Request**: [`https://github.com/shamddd/stateshift/pull/1`](https://github.com/shamddd/stateshift/pull/1)
- **Merge Commit**: [`https://github.com/shamddd/stateshift/commit/aa49a81d4db5dd9fe68df95c32e07e43d36fd88f`](https://github.com/shamddd/stateshift/commit/aa49a81d4db5dd9fe68df95c32e07e43d36fd88f)
- **Preprint Candidate PDF**: [`https://github.com/shamddd/stateshift/blob/main/paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf`](https://github.com/shamddd/stateshift/blob/main/paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf)
- **arXiv Source Archive (ZIP)**: [`https://raw.githubusercontent.com/shamddd/stateshift/main/paper/source/STATESHIFT_ARXIV_RELEASE_SOURCE.zip`](https://raw.githubusercontent.com/shamddd/stateshift/main/paper/source/STATESHIFT_ARXIV_RELEASE_SOURCE.zip)
- **Study 1 Dataset (CSV)**: [`https://raw.githubusercontent.com/shamddd/stateshift/main/data/study1/controlled_endpoint_outcomes.csv`](https://raw.githubusercontent.com/shamddd/stateshift/main/data/study1/controlled_endpoint_outcomes.csv)
- **Study 2 Raw Generations (JSONL)**: [`https://raw.githubusercontent.com/shamddd/stateshift/main/data/study2/stateshift_primary_400_generations.jsonl`](https://raw.githubusercontent.com/shamddd/stateshift/main/data/study2/stateshift_primary_400_generations.jsonl)
- **Study 2 Evaluated Outcomes (CSV)**: [`https://raw.githubusercontent.com/shamddd/stateshift/main/data/study2/final_verified_outcomes.csv`](https://raw.githubusercontent.com/shamddd/stateshift/main/data/study2/final_verified_outcomes.csv)
- **Reproducibility Documentation**: [`https://github.com/shamddd/stateshift/blob/main/docs/REPRODUCIBILITY.md`](https://github.com/shamddd/stateshift/blob/main/docs/REPRODUCIBILITY.md)
- **Successful CI Workflow Runs**:
  - Research CI (PR #1): [`https://github.com/shamddd/stateshift/actions/runs/40315871871`](https://github.com/shamddd/stateshift/actions/runs/40315871871)
  - Artifacts CI (PR #1): [`https://github.com/shamddd/stateshift/actions/runs/40315871912`](https://github.com/shamddd/stateshift/actions/runs/40315871912)

---

## 3. Commit Discrepancy Reconciliation

- **Identified Identifiers**: Commit `4ffb95f` vs. Commit `ed01fb0`.
- **Finding**: Commit `ed01fb0` is the direct descendant of `4ffb95f`. Commit `4ffb95f` integrated the research payload, and commit `ed01fb0` added the final Mission 20 QA reports. Both commits exist in a linear chain without divergence.
- **Subsequent Hardening Commits**:
  - `cc073a4`: Normalized dataset byte preservation in `.gitattributes`, added package discovery in `pyproject.toml`, and configured hermetic Tectonic compiler in CI.
  - `79e61ea`: Added `sympy>=1.10.0` dependency to support symbolic verification in CI.
  - `aa49a81`: Merge commit integrating PR #1 into `main`.

---

## 4. Public File Verification

Every core file is confirmed live and downloadable from the remote `main` branch:
1. `README.md` (10,158 bytes)
2. `LICENSE` (MIT)
3. `CITATION.cff` & `CITATION.bib`
4. `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf` (197,845 bytes, valid `%PDF-1.5`)
5. `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex` (25,606 bytes)
6. `paper/references.bib` (19 canonical citations)
7. `paper/source/STATESHIFT_ARXIV_RELEASE_SOURCE.zip` (797,847 bytes, SHA-256: `2706cc14...`)
8. `paper/figures/figure[1-5].{pdf,png}` (10 figure assets)
9. `data/study1/controlled_endpoint_outcomes.csv` (2,366,349 bytes, SHA-256: `49549bbd...`, 29,056 rows)
10. `data/study2/stateshift_primary_400_generations.jsonl` (898,204 bytes, SHA-256: `bb177455...`, 400 records)
11. `data/study2/final_verified_outcomes.csv` (7,998 bytes, SHA-256: `19a328a9...`, 100 problem pairs)
12. `experiments/study1_checkpoint_lineage/reproduce_study1.py`
13. `experiments/study2_reasoning_recovery/reproduce_study2.py`
14. `experiments/study2_reasoning_recovery/exact_power_analysis.py`
15. `tests/test_mission20_release_qa.py` (6/6 tests passing)

---

## 5. Summary of Empirical Test Results

- **Study 1 (Checkpoint-Lineage Analysis)**:
  - Step 0 Control: $38.92\%$, Step 0 Recovery: $38.34\%$
  - Step 256 Control: $59.21\%$, Step 256 Recovery: $70.39\%$
  - Interaction $\hat{\gamma}_{256}$: **$+11.76$ percentage points** ($t = 10.34, p < 0.001$).
  - Mean Token Difference: $-13.19$ tokens (TOST equivalence pass, $p = 0.0256$).
- **Study 2 (Physical GPU Validation on Qwen2.5-Math-7B-Instruct)**:
  - Condition A (Zero-Shot Baseline): **64.00%**
  - Condition D (No-Intervention Control): **67.00%**
  - Condition E (Lemma Scaffold Control): **71.00%**
  - Condition F (Full State Restoration): **73.00%**
  - Primary Contrast ($F - D$): **+6.00 percentage points** ($73\% - 67\%$).
  - Exact Two-Sided McNemar $p$-value: **$0.109375$** ($b=8, c=2$, odds ratio $4.00$).
  - Primary contrast is **not statistically significant** at $\alpha=0.05$.
  - Exact Discrete Unconditional Power ($N = 100$): **$36.20\%$**.
  - Confirmatory Trial Sample Size: **$N = 231$** ($80\%$ power), **$N = 299$** ($90\%$ power).
  - Baseline Recovery ($F - A = +9.00$ pp): **$p = 0.0117$** (statistically significant).

---

## 6. Security and Privacy Audit Summary

- Secret scans across the entire commit diff yielded zero active secrets, private keys, or API tokens.
- All dummy matches in test fixtures (`rpa_mock_key_xyz`, `SECRET_KEY_123456789`) confirmed offline only.
- Fail-closed lock file `.cloud_execution_locked` remains active on disk.
- Zero cloud GPU instances provisioned; zero API inferences executed.
- RunPod balance preserved at **$10.1065 USD** ($0.00 spent).

---

## 7. Remaining Human Actions

1. **Human Author Checklist Approval**:
   - The Principal Investigator (Sham Satish Thakare) may review the release candidate PDF (`paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf`) and check off the author verification boxes in `docs/REPRODUCIBILITY.md`.
2. **arXiv Submission**:
   - The verified source archive `paper/source/STATESHIFT_ARXIV_RELEASE_SOURCE.zip` is completely packaged and ready for manual upload to arXiv at the PI's discretion. No automated arXiv upload was performed.
