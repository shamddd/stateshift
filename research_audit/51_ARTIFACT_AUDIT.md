# StateShift Cryptographic Artifact & Provenance Audit

**Audit Date**: October 18, 2026  
**Auditor**: Senior Research Librarian & Security Auditor  
**Standard**: Cryptographic Ground Truth · Zero Private Data Leakage  

---

## 1. Cryptographic Hash Registry of Primary Artifacts

| Artifact Name | Relative Path | Size (Bytes) | SHA-256 Checksum | Provenance Commit | Classification |
|:---|:---|:---:|:---|:---:|:---:|
| **Raw Confirmatory Rollouts** | `artifacts/endpoint/controlled_endpoint_outcomes.csv` | 2,366,349 | `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139` | `8ac7a67` | **LEVEL 1 PRIMARY DATA** |
| **Strict Decontamination Subset** | `artifacts/endpoint/strict_decontamination_subset.csv` | 74 | `d5ba3cbead36511ad3c5e2ec6f29633e9b1191ff79cb075c3db6f51cb7e4624b` | `8ac7a67` | **LEVEL 1 PRIMARY DATA** |
| **9-Checkpoint Trajectory** | `artifacts/trajectory/nine_checkpoint_trajectory.csv` | 260 | `232b62140bb6a8542c366e60b1385f8c85775440265005b4ba3c2aeb3df4400e` | `64476fc` | **LEVEL 1 PRIMARY DATA** |
| **Natural Error Episodes** | `artifacts/natural_recovery/natural_error_episodes.csv` | 42,752 | `ec9d58b736b4421d011110e54d89b02a2468165b6f7902ba14488b394156c4d7` | `8ac7a67` | **LEVEL 1 PRIMARY DATA** |
| **Natural Recovery Episodes** | `artifacts/natural_recovery/natural_recovery_episodes.csv` | 13,248 | `fcae4757c91fa58334863bcfe9717cb97cb4e893e17b81561f3be03d09a807d4` | `8ac7a67` | **LEVEL 1 PRIMARY DATA** |
| **Confirmatory Problem Registry** | `artifacts/provenance/confirmatory_problem_registry.json` | 382,419 | `7f7ba50c33a921d2e9700d8324f9e38d7283e387c12ff35b91507f352932c589` | `3304d0b` | **LEVEL 1 PRIMARY DATA** |
| **Candidate LaTeX Source** | `neurips_submission/main.tex` | 18,124 | Tracked locally | Current | **LEVEL 3 CANDIDATE** |
| **Supplementary Material** | `neurips_submission/supplement.tex` | 3,450 | Tracked locally | Current | **LEVEL 3 CANDIDATE** |
| **One-Click CPU Reproduction** | `neurips_submission/reproducibility/reproduce.py` | 3,339 | Tracked locally | Current | **LEVEL 2 REPRO SCRIPT** |

---

## 2. Privacy, Credentials & Information Security Audit
- **Zero API Keys**: No OpenAI, Anthropic, Gemini, or RunPod API keys are present.
- **Zero Restricted Weights**: Gigabyte model checkpoints are excluded from Git tracking.
- **Zero Personal Identifiers**: Author names, institutional affiliations, and personal email addresses are fully purged in all submission artifacts.
