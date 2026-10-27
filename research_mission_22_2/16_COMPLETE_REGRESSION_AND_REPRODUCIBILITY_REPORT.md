# Research Mission 22.2 — Complete Regression and Reproducibility Report

## 1. Test Session Overview
- **Execution Date**: 2026-10-27 (IST)
- **Test Runner**: `pytest 8.4.2` with `pluggy 1.5.0`
- **Runtime Environment**: Darwin (macOS) / Python 3.13.9
- **Root Directory**: `/Users/shamthakare/.gemini/antigravity/scratch`
- **Configuration File**: `pyproject.toml`
- **Total Test Suites**: 4 test files across 3 research mission packages
- **Total Tests Executed**: 24 tests
- **Total Tests Passed**: 24 tests (100% pass rate)
- **Failures / Errors / Skips**: 0 / 0 / 0
- **Execution Wall Time**: 27.88 seconds
- **Exit Code**: 0 (Full Success)

---

## 2. Test Suite Breakdown

### Suite 1: `research_mission_22/tests/test_confirmatory_statistics.py` (5 tests)
1. `test_exact_mcnemar_p_values`: PASSED (Validates binomial exact distribution against scipy)
2. `test_exact_power_pilot_scenario`: PASSED (Validates 80.07% exact power at $N=231, q=0.10, \psi=0.80$)
3. `test_exact_power_90_percent_target`: PASSED (Validates sample size for 90% power)
4. `test_exact_power_conservative_effect`: PASSED (Validates power under small effect size $\Delta = +0.04$)
5. `test_correction_of_elevated_discordance`: PASSED (Validates that power drops to 65.86% when $q=0.14$)

### Suite 2: `research_mission_22/tests/test_confirmatory_trial.py` (6 tests)
6. `test_files_exist`: PASSED (Verifies manifest files and runner scripts on disk)
7. `test_candidate_pool_size`: PASSED (Verifies 354 candidate pool problems)
8. `test_manifest_record_counts`: PASSED (Verifies exactly 924 records across 231 problems)
9. `test_zero_overlap_with_pilot`: PASSED (Verifies $\mathcal{P}_{\text{pilot}} \cap \mathcal{P}_{\text{confirmatory}} = \emptyset$)
10. `test_condition_structure_and_hashes`: PASSED (Verifies conditions A, D, E, F and prompt SHA-256)
11. `test_stratification_quotas`: PASSED (Verifies subject and difficulty level distributions)

### Suite 3: `research_mission_22/tests/test_gpu_authorization_gate.py` (4 tests)
12. `test_lock_file_present_on_disk`: PASSED (Verifies `.cloud_execution_locked` exists)
13. `test_runner_fails_closed_when_cloud_requested`: PASSED (Verifies exit code 1 when cloud requested while locked)
14. `test_runner_dry_run_succeeds_with_zero_cloud_calls`: PASSED (Verifies local dry-run succeeds on CPU)
15. `test_authorization_token_validation_logic`: PASSED (Verifies pre-shared cryptographic token validation)

### Suite 4: `research_mission_22_1/tests/test_mission_22_1_regressions.py` (4 tests)
16. `test_resume_behavior`: PASSED (Verifies skipping already-completed request IDs in output jsonl)
17. `test_record_serialization_schema`: PASSED (Verifies 23-field JSON serialization and types)
18. `test_elevated_discordance_power_regression`: PASSED (Verifies $N=322$ requirement for $q=0.14$)
19. `test_terminology_governance_in_reports`: PASSED (Verifies adherence to standardized terminology)

### Suite 5: `research_mission_22_2/tests/test_definitive_contingency_reconciliation.py` (5 tests)
20. `test_canonical_csv_contingency`: PASSED (Verifies `final_verified_outcomes.csv` yields $a=65, b=8, c=2, d=25$)
21. `test_reconstructed_pilot_outcomes`: PASSED (Verifies Path A and Path B contingency tables)
22. `test_disagreement_ledger_localization`: PASSED (Verifies divergence is 100% localized to `math500_007`)
23. `test_verified_json_structure_and_invariance`: PASSED (Verifies invariant $b=8, c=2$, $\tau=+0.06$, $p=0.109375$)
24. `test_tri_method_cross_check`: PASSED (Verifies concordance across Pure Python, NumPy, and Pandas)

---

## 3. Regression Verdict
The test suite confirms zero regressions, 100% computational reproducibility, and total consistency across all statistical, structural, and safety specifications.
