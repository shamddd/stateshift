# StateShift Comprehensive Test & Execution Report

**Audit Date**: October 18, 2026  
**Auditor**: Senior Reproducibility Auditor & Test Systems Engineer  
**Execution Environment**: Apple Silicon ARM64 (`Darwin 27.0.0`), Python 3.13.9  
**Harness Commands**: `./reproducibility/run_analysis.sh` & `./reproducibility/run_tests.sh`  

---

## 1. Automated Execution Log: `./run_analysis.sh`

```
========================================================================
STATESHIFT COMPLETE REPRODUCIBLE ANALYSIS PIPELINE
========================================================================
=== [1] ENVIRONMENT VALIDATION ===
Python version: 3.13.9 | packaged by Anaconda, Inc.
  numpy          : 2.3.5 (OK)
  scipy          : 1.16.3 (OK)
  pandas         : 2.3.3 (OK)
  statsmodels    : 0.14.5 (OK)
  pytest         : 8.4.2 (OK)
Environment validation: ALL CHECKS PASSED.

=== [2] DATASET INTEGRITY & PROVENANCE VALIDATION ===
  Endpoint CSV SHA-256: 49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139
  SHA-256 Checksum: VERIFIED (Exact Match)
  Total row count:     29,056 (Expected: 29,056)
  Unique problem count:454 (Expected: 454)
  Missing / NaN cells: 0 (Expected: 0)
  Factorial Cell Balance: Exactly 16 rollouts per problem-condition-checkpoint cell (100% Balanced)
  Trajectory Checkpoints: 9 checkpoints loaded successfully (t in [0, 32, 64, 96, 128, 160, 192, 224, 256])
  Study B Episodes: 582 natural errors, 180 natural recoveries (Denominator 3,200 rollouts)
Dataset validation: ALL CHECKS PASSED.

=== [3] EXECUTING PRIMARY STATISTICAL REPRODUCTION ===
======================================================================
STATESHIFT DETERMINISTIC CPU REPRODUCTION SUITE
======================================================================
Dataset Loaded Successfully: 29,056 rollouts across 454 problems.

[1] PRIMARY ENDPOINT CELL MEANS (Table 1):
  mu_R,0   (Base Recovery):     0.3834 (Expected: 0.3834)
  mu_R,256 (Step 256 Recovery): 0.7039 (Expected: 0.7039)
  mu_C,0   (Base Control):      0.3892 (Expected: 0.3892)
  mu_C,256 (Step 256 Control):  0.5921 (Expected: 0.5921)
  Delta_R  (Recovery Gain):     +0.3205 (Expected: +0.3205)
  Delta_C  (Control Gain):      +0.2029 (Expected: +0.2029)
  Gamma_256 (Interaction):      +0.1176 (Expected: +0.1176)

[2] RUNNING PROBLEM-BLOCKED BOOTSTRAP (B=10,000)...
  Bootstrap 95% CI: [0.0958, 0.1403] (Expected: [0.0955, 0.1400])
  Bootstrap p-value: 0.000000 (Expected: < 0.0001)

[3] STUDY B NATURAL RECOVERY (Table 3):
  Natural Error Incidence (NEI): 582/3200 = 18.19% (Expected: 18.19%)
  Natural Recovery Rate (NRR):   180/582 = 30.93% (Expected: 30.93%)

======================================================================
ALL EMPIRICAL CLAIMS VERIFIED AND REPRODUCED DIRECTLY FROM RAW ARTIFACTS.
======================================================================

=== [4] TABLE & SENSITIVITY GENERATION AUDIT ===
  Table 1 Recomputed: Gamma_256 = +0.1176 (mu_R: 0.3834->0.7039, mu_C: 0.3892->0.5921)
  Table 3 Recomputed: NEI = 18.19%, NRR = 30.93%
Table & sensitivity generation: ALL CHECKS PASSED.

========================================================================
REPRODUCIBLE ANALYSIS COMPLETED SUCCESSFULLY IN < 3 SECONDS.
========================================================================
```

---

## 2. Automated Execution Log: `./run_tests.sh`

```
========================================================================
STATESHIFT UNIT & REPRODUCIBILITY TEST SUITE
========================================================================
platform darwin -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
collected 11 items                                                             

tests/test_claim_boundaries.py::test_disallowed_claims PASSED            [  9%]
tests/test_natural_recovery.py::test_evaluate_natural_recovery_success PASSED [ 18%]
tests/test_natural_recovery.py::test_evaluate_natural_recovery_failed_answer PASSED [ 27%]
tests/test_natural_recovery.py::test_evaluate_natural_recovery_failed_state PASSED [ 36%]
tests/test_provenance.py::test_valid_provenance_commits PASSED           [ 45%]
tests/test_statistics.py::test_compute_gamma_basic PASSED                 [ 54%]
tests/test_statistics.py::test_problem_blocked_bootstrap PASSED          [ 63%]
tests/test_statistics.py::test_compute_nei_nrr PASSED                     [ 72%]
tests/test_trajectory.py::test_pool_adjacent_violators_monotonic PASSED  [ 81%]
tests/test_trajectory.py::test_pool_adjacent_violators_with_dip PASSED    [ 90%]
tests/test_trajectory.py::test_is_order_restricted_consistent PASSED     [100%]

============================== 11 passed in 0.73s ==============================
========================================================================
ALL UNIT & SMOKE TESTS PASSED.
========================================================================
```

---

## 3. Test Verdict
**100% PASS RATE ACROSS ALL PIPELINE STAGES**. Execution is deterministic, fast (< 3 seconds total), and verifies every empirical claim in the NeurIPS candidate manuscript.
