# Changelog — Project StateShift

All notable changes, scientific milestones, and defect corrections in Project StateShift are documented in this file.

---

## [1.0.0] — 2026-10-26 (Release Candidate & Publication Integration)

### Added
* Integrated canonical publication manuscript candidate (`paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex` and `.pdf`).
* Cleanroom-verified source upload bundle (`paper/source/STATESHIFT_ARXIV_RELEASE_SOURCE.zip`).
* Authentic physical GPU dataset for Study 2 (`data/study2/stateshift_primary_400_generations.jsonl` and `data/study2/final_verified_outcomes.csv`).
* Checkpoint-lineage dataset for Study 1 (`data/study1/controlled_endpoint_outcomes.csv`).
* CPU-only reproduction scripts for Study 1 (`experiments/study1_checkpoint_lineage/reproduce_study1.py`) and Study 2 (`experiments/study2_reasoning_recovery/reproduce_study2.py`).
* Exact discrete unconditional binomial McNemar power engine (`experiments/study2_reasoning_recovery/exact_power_analysis.py`).
* Comprehensive scientific documentation suite under `docs/` (`RESEARCH_HISTORY.md`, `SCIENTIFIC_CLAIMS.md`, `STATISTICAL_METHODS.md`, `LIMITATIONS.md`, etc.).
* Automated GitHub Actions CI workflow (`.github/workflows/research-ci.yml`).

### Corrected
* Separated research into two distinct studies: Study 1 (exploratory checkpoint lineage, outcome-level data) and Study 2 (physical GPU experiment on RTX 4090, generation-level data).
* Eradicated all terminology claiming "guaranteed significance" or "100% confirmation".
* Replaced asymptotic normal approximations with exact discrete binomial McNemar tests ($p = 0.109375$ two-sided, $p = 0.054688$ one-sided).
* Purged all automated pre-filled author approval signatures, establishing human author sovereignty via `AUTHOR_FINAL_APPROVAL_CHECKLIST.md`.
* Bounded Condition F causally as a compound prompt intervention package ($do(F)$).
* Corrected case study analysis for problem `math500_012` to reflect proper divisor counting on amicable pair $(220, 284)$.

---

## [0.2.0] — 2026-10-26 (Physical GPU Calibration & Primary Experiment)

### Added
* Authorized physical GPU calibration on RunPod Secure Cloud NVIDIA RTX 4090 ($10/10$ requests, $\$0.2110$ spend).
* Primary 400-request GPU inference run on `Qwen/Qwen2.5-Math-7B-Instruct` across conditions A, D, E, F ($N=100$).
* Independent financial watchdog processes with fail-closed teardown.

---

## [0.1.0] — 2026-10-18 (Historical Pre-Reconstruction Baseline)

### Initial
* Exploratory checkpoint-lineage analysis across DeepScaleR-7B checkpoints ($N=454$, 29,056 rollout evaluations).
* Initial working paper draft and preliminary evaluation code.
