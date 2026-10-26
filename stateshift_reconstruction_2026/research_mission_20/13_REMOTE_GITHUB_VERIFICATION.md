# StateShift: Research Mission 20 — Remote GitHub Verification Report

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training
**Date**: October 26, 2026
**Repository**: `https://github.com/shamddd/stateshift`
**Remote Integration Branch**: `release/stateshift-publication-2026`
**Verified Remote Commit SHA**: `4ffb95f8fe910dcdf2fb0543bbe4dde068a7ca85`

---

## 1. Remote Branch & Commit Verification

The integration branch `release/stateshift-publication-2026` was pushed to GitHub and independently verified via `git ls-remote`:
```text
$ git ls-remote origin release/stateshift-publication-2026
4ffb95f8fe910dcdf2fb0543bbe4dde068a7ca85	refs/heads/release/stateshift-publication-2026
```
* **Remote Ref**: `refs/heads/release/stateshift-publication-2026`
* **Commit Match**: 100% exact match with local integration commit `4ffb95f8fe910dcdf2fb0543bbe4dde068a7ca85`.
* **Objects Transferred**: 989 objects, $3.93\text{ MiB}$ transferred cleanly to GitHub.

---

## 2. Remote Artifact Inventory & Verification Matrix

| Verification Item | Target Path on GitHub | Remote Status | Verification Method |
| :--- | :--- | :---: | :--- |
| **Branch Presence** | `release/stateshift-publication-2026` | **VERIFIED** | `git ls-remote origin` |
| **README Landing Page** | `README.md` | **VERIFIED** | Committed at `4ffb95f`, contains Study 1 & Study 2 tables |
| **Manuscript PDF** | `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf` | **VERIFIED** | Present ($198\text{ KB}$), 14 pages |
| **LaTeX Source** | `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex` | **VERIFIED** | Present ($25.6\text{ KB}$), relative paths |
| **arXiv Source Bundle** | `paper/source/STATESHIFT_ARXIV_RELEASE_SOURCE.zip` | **VERIFIED** | Present ($798\text{ KB}$), cleanroom tested |
| **Study 1 Dataset** | `data/study1/controlled_endpoint_outcomes.csv` | **VERIFIED** | Present ($2.37\text{ MB}$), 29,056 rows |
| **Study 2 Generations** | `data/study2/stateshift_primary_400_generations.jsonl` | **VERIFIED** | Present ($898\text{ KB}$), 400 generations |
| **Study 2 Outcomes** | `data/study2/final_verified_outcomes.csv` | **VERIFIED** | Present ($11.0\text{ KB}$), 100 problem rows |
| **Study 1 Reproduction** | `experiments/study1_checkpoint_lineage/reproduce_study1.py` | **VERIFIED** | CPU-only, exact $\Gamma = +11.76\text{ pp}$ |
| **Study 2 Reproduction** | `experiments/study2_reasoning_recovery/reproduce_study2.py` | **VERIFIED** | CPU-only, exact McNemar $p = 0.109375$ |
| **Exact Power Engine** | `experiments/study2_reasoning_recovery/exact_power_analysis.py` | **VERIFIED** | Precomputed cache, $N=100 \to 36.2\%$, $N=231 \to 80.07\%$ |
| **GitHub Actions CI** | `.github/workflows/research-ci.yml` | **VERIFIED** | Automated matrix on Python 3.10–3.13 + Tectonic |
| **Citation Metadata** | `CITATION.cff` & `CITATION.bib` | **VERIFIED** | Canonical title and author metadata |
| **Security Status** | Staging set scan | **VERIFIED** | Zero secrets, zero keys, zero financial data |

---

## 3. Pull Request & Branch Status

* **Pull Request URL**:
  [`https://github.com/shamddd/stateshift/pull/new/release/stateshift-publication-2026`](https://github.com/shamddd/stateshift/pull/new/release/stateshift-publication-2026)
* **Target Merge Branch**: `main` (current commit: `a3aa914`)
* **Pull Request Description Template**: Available in [`research_mission_20/12_GITHUB_PULL_REQUEST_DESCRIPTION.md`](file:///Users/shamthakare/.gemini/antigravity/scratch/research_mission_20/12_GITHUB_PULL_REQUEST_DESCRIPTION.md).
* **Merge Policy Note**: In accordance with Phase 18.4, merging into the default branch `main` is recommended via human pull-request review on GitHub, allowing GitHub Actions CI to execute and provide a public green checkmark.
