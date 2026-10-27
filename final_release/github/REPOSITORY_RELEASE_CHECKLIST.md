# StateShift Repository Release Checklist

This checklist must be verified before the Principal Investigator authorizes any external release action.

## 1. Scientific Integrity Verification
- [x] All empirical numbers match frozen raw records ($a=146, b=11, c=12, d=62, \hat{\tau}=-0.43\%, p=1.000000$).
- [x] Unsupported "Discordance Invariance Law" permanently deleted.
- [x] Unsupported causal mechanism equations deleted.
- [x] Post-hoc equivalence margins clearly identified as unpreregistered exploratory bounds.
- [x] Statistical independence overclaims purged and disattenuation analysis reported.

## 2. Code & Test Verification
- [x] Automated regression suite passes 100% (68/68 tests).
- [x] Cleanroom reproduction script (`reproduce_all_statistics.py`) runs in < 10s on CPU.
- [x] Dynamic relative paths used in all active scripts (no hardcoded `/Users/shamthakare/...`).
- [x] Evaluation pipelines validated with 0 discrepancies across 924 confirmatory outputs.

## 3. Publication Artifacts
- [x] Main preprint PDF compiled cleanly via Tectonic (11 pages).
- [x] Supplement PDF compiled cleanly via Tectonic (3 pages).
- [x] Anonymous submission candidate prepared for NeurIPS 2027.
- [x] Non-anonymous package prepared for arXiv.

## 4. Security & Compliance
- [x] Cloud lock active on disk (`.cloud_execution_locked`).
- [x] RunPod pods, volumes, and API keys completely purged.
- [x] Current cloud spending rate is $0.00/hr.
- [x] No unauthorized external git push performed.
