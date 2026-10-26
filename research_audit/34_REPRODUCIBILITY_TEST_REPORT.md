# StateShift Continuous Integration & Reproducibility Test Report

**Execution Date**: October 18, 2026  
**Auditor**: Lead Reproducibility & CI Test Engineer  
**Python Runtime**: Python 3.13.9  
**Pytest Version**: pytest 8.4.2  
**Test Suite Path**: `neurips_submission/reproducibility/tests`  

---

## 1. Test Suite Execution Summary

| Test Module | Test Case Name | Execution Status | Runtime | Tested Claim / Invariant |
|:---|:---|:---:|:---:|:---|
| `test_claim_boundaries.py` | `test_disallowed_claims` | **PASSED** | 0.02s | Prohibits unverified causal claims and unadjusted monotonicity assertions |
| `test_natural_recovery.py` | `test_evaluate_natural_recovery_success` | **PASSED** | 0.01s | Verifies autonomous transition out of endogenous error states |
| `test_natural_recovery.py` | `test_evaluate_natural_recovery_failed_answer` | **PASSED** | 0.01s | Validates terminal failure classification |
| `test_natural_recovery.py` | `test_evaluate_natural_recovery_failed_state` | **PASSED** | 0.01s | Validates non-recovery persistent error classification |
| `test_provenance.py` | `test_valid_provenance_commits` | **PASSED** | 0.05s | Validates SHA-256 and Git commit hash integrity |
| `test_statistics.py` | `test_compute_gamma_basic` | **PASSED** | 0.02s | Recomputes interaction contrast Gamma_t with exact arithmetic |
| `test_statistics.py` | `test_problem_blocked_bootstrap` | **PASSED** | 0.28s | Validates blocked resampling with intra-cluster variance preservation |
| `test_statistics.py` | `test_compute_nei_nrr` | **PASSED** | 0.03s | Verifies NEI=18.19% and NRR=30.93% exact ratios |
| `test_trajectory.py` | `test_pool_adjacent_violators_monotonic` | **PASSED** | 0.01s | Verifies isotonic regression on strictly increasing sequences |
| `test_trajectory.py` | `test_pool_adjacent_violators_with_dip` | **PASSED** | 0.02s | Verifies PAVA pooling over local empirical dips (steps 160 & 224) |
| `test_trajectory.py` | `test_is_order_restricted_consistent` | **PASSED** | 0.02s | Verifies global monotonicity envelope test (p < 0.001) |

**Overall Result**: **11 passed, 0 failed, 0 skipped in 0.74s (100% Pass Rate)**.
