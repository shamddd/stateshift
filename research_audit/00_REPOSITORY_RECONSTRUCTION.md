# StateShift Complete Repository Reconstruction & Environment Discovery

**Audit Date**: October 18, 2026  
**Auditor**: Senior ML Research Engineer, Statistical Methodologist & Reproducibility Auditor  
**Standard**: 100% Cryptographic Traceability · Evidence Before Claims  
**Repository Scope**: `https://github.com/shamddd/stateshift`  

---

## 1. Local Environment & Workspace Discovery

A comprehensive read-only audit of the local development environment was conducted:

| Environment Attribute | Discovered Value | Verification Method |
|:---|:---|:---|
| **Local Workspace Root** | `/Users/shamthakare/.gemini/antigravity/scratch` | `pwd` |
| **Git Working Tree Root** | `/Users/shamthakare/.gemini/antigravity/scratch` | `git rev-parse --show-toplevel` |
| **Origin Remote URL** | `https://github.com/shamddd/stateshift.git` | `git remote -v` |
| **Website Remote URL** | `https://github.com/shamddd/shamthakare.github.io.git` | `git remote -v` |
| **Active Branch** | `main` | `git branch --show-current` |
| **Default Branch** | `main` | `git symbolic-ref refs/remotes/origin/HEAD` |
| **Current Baseline Commit** | `d4d68b2` | `git rev-parse HEAD` |
| **Working-Tree Status** | Clean on tracked files; untracked scratch/portfolio directories present | `git status --porcelain` |
| **Host Architecture** | Apple Silicon ARM64 (`Darwin 27.0.0 arm64`) | `uname -sm` |
| **Python Environment** | Python 3.9+ / Virtual Environment (`scratch/venv`) | `python3 --version` |
| **Primary Dependencies** | `numpy`, `scipy`, `pandas`, `pytest` | `python3 -m pip list` |
| **Test Suite Location** | `/Users/shamthakare/.gemini/antigravity/scratch/website_clone/tests/` | Passed 11/11 tests in 0.77s |

---

## 2. Repository Architecture & Reconstruction Map

The StateShift codebase has undergone multiple historical phases. An audit of Git history reveals that commit `8d20d8d` (October 12, 2026) reorganized personal website tracking in the root repository. However, all research artifacts, raw rollout outcomes, and Python modules were fully preserved across multiple independent locations:

```
/Users/shamthakare/.gemini/antigravity/scratch/
│
├── stateshift/                        # Local Python package tree (evaluation, statistics, natural_recovery)
│   ├── statistics/bootstrap.py        # Problem-blocked bootstrap (B=10,000)
│   ├── statistics/metrics.py          # State-Matched Interaction Contrast (Gamma_t)
│   ├── trajectory/order_restricted.py # Isotonic regression PAVA & global envelope
│   └── natural_recovery/detector.py   # Multi-condition natural error/recovery detector
│
├── website_clone/                     # Full snapshot of commit 0e169ba / 9be50ce
│   ├── artifacts/
│   │   ├── endpoint/
│   │   │   ├── controlled_endpoint_outcomes.csv (29,056 empirical rollouts; SHA-256 verified)
│   │   │   ├── endpoint_summary_numbers.csv
│   │   │   └── strict_decontamination_subset.csv (388 problems)
│   │   ├── trajectory/
│   │   │   ├── nine_checkpoint_trajectory.csv (t in {0, 32, ..., 256})
│   │   │   ├── intermediate_checkpoint_cell_means.csv
│   │   │   └── intermediate_rollouts.jsonl (1.6 MB)
│   │   └── natural_recovery/
│   │       ├── natural_error_episodes.csv (582 error episodes from 3,200 rollouts)
│   │       └── natural_recovery_episodes.csv (180 recovery episodes; 30.93% NRR)
│   ├── stateshift/                    # Production Python package source
│   ├── tests/                         # Pytest test suite (11/11 passing)
│   ├── StateShift_AIJ_Final_Submission.zip # Submitted camera-ready package (Elsevier AIJ ARTINT-D-26-01491)
│   └── tectonic                       # Historical x86_64 Tectonic binary (incompatible with ARM64 host)
│
├── stateshift_all_documents/          # Consolidated master research archive
│   ├── 00_INDEX_AND_MANIFEST.md       # Master index of 128 research documents
│   ├── 01_MANUSCRIPT_AND_PUBLICATIONS # Elsevier AIJ manuscript, IEEE drafts, camera-ready PDFs
│   ├── 02_CHAT_RESEARCH_DOSSIERS      # Historical dossiers across research conversations
│   ├── 03_AUDITS_AND_RED_TEAMING      # Statistical red-team audits & sign reconciliations
│   ├── 04_PROJECT_REPORTS_AND_CLAIM_BOUNDARIES # Claim boundary registers & freeze certificates
│   ├── 05_VIVA_DEFENSE_AND_METRICS    # Viva defense sheets & metric crosswalks
│   ├── 06_PHASE1G_DATASET_FORENSICS   # Decontamination logs & semantic adjudication records
│   ├── 07_PORTFOLIO_AND_APPLICATION_AUDITS # Cross-project governance documents
│   ├── research_audit/                # 40+ formal audit reports, registries, and checklists
│   └── neurips_submission/            # Rebuilt double-blind NeurIPS 2027 package
│
└── stateshift-manuscript-source/      # Pristine original LaTeX submission source
    ├── 01_Main_Manuscript.tex
    ├── references.bib
    └── figures/
```

---

## 3. Preservation & Security Verification

In accordance with strict research integrity protocols:
1. **Zero Remote Modification**: No git pushes, no force pushes, no branch deletions on remote `origin` or `website`.
2. **Immutable Raw Data**: Raw empirical CSVs have verified SHA-256 checksums and remain read-only.
3. **Pristine Manuscript Sources**: Original LaTeX sources in `stateshift-manuscript-source/` remain unmodified.
4. **Isolated Candidate Working Tree**: All NeurIPS 2027 candidate files are constructed in an isolated directory (`neurips_submission/`).
5. **No Token or Credential Leakage**: No API keys, passwords, or personal credentials are exposed.
