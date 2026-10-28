# Phase 8: Comprehensive Local CPU Test Execution Report

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22.1 — Final Confirmatory Scientific Audit  
**Date & Timestamp**: 2026-10-27T05:55:30+05:30  
**Target Publication Venue**: NeurIPS 2027 Main Track  
**Execution Environment**: macOS Darwin, Python 3.13.9, pytest 8.4.2  
**Cloud Spending Incurred**: **$0.00 USD**  

---

## 1. Executive Summary

A comprehensive automated test suite comprising **19 test cases** across four test modules was executed exclusively on local CPU resources. The test battery validated cryptographic manifest integrity, zero-overlap invariants, discrete power calculations, regression fixes, resume capabilities, standardized 23-field schema serialization, and fail-closed authorization barriers.

**All 19 test cases passed with zero failures and zero regressions (100% pass rate).**

---

## 2. Test Execution Log

```
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- /opt/anaconda3/bin/python3
cachedir: .pytest_cache
rootdir: /Users/shamthakare/.gemini/antigravity/scratch
plugins: cov-7.1.0, anyio-4.10.0, hydra-core-1.3.5
collected 19 items

research_mission_22/tests/test_confirmatory_statistics.py::test_exact_mcnemar_p_values               PASSED [  5%]
research_mission_22/tests/test_confirmatory_statistics.py::test_exact_power_pilot_scenario           PASSED [ 10%]
research_mission_22/tests/test_confirmatory_statistics.py::test_exact_power_90_percent_target       PASSED [ 15%]
research_mission_22/tests/test_confirmatory_statistics.py::test_exact_power_conservative_effect      PASSED [ 21%]
research_mission_22/tests/test_confirmatory_statistics.py::test_correction_of_elevated_discordance  PASSED [ 26%]
research_mission_22/tests/test_confirmatory_trial.py::test_files_exist                               PASSED [ 31%]
research_mission_22/tests/test_confirmatory_trial.py::test_candidate_pool_size                       PASSED [ 36%]
research_mission_22/tests/test_confirmatory_trial.py::test_manifest_record_counts                    PASSED [ 42%]
research_mission_22/tests/test_confirmatory_trial.py::test_zero_overlap_with_pilot                  PASSED [ 47%]
research_mission_22/tests/test_confirmatory_trial.py::test_condition_structure_and_hashes           PASSED [ 52%]
research_mission_22/tests/test_confirmatory_trial.py::test_stratification_quotas                     PASSED [ 57%]
research_mission_22/tests/test_gpu_authorization_gate.py::test_lock_file_present_on_disk             PASSED [ 63%]
research_mission_22/tests/test_gpu_authorization_gate.py::test_runner_fails_closed_when_cloud_requested PASSED [ 68%]
research_mission_22/tests/test_gpu_authorization_gate.py::test_runner_dry_run_succeeds_with_zero_cloud_calls PASSED [ 73%]
research_mission_22/tests/test_gpu_authorization_gate.py::test_authorization_token_validation_logic PASSED [ 78%]
research_mission_22_1/tests/test_mission_22_1_regressions.py::test_resume_behavior                  PASSED [ 84%]
research_mission_22_1/tests/test_mission_22_1_regressions.py::test_record_serialization_schema       PASSED [ 89%]
research_mission_22_1/tests/test_mission_22_1_regressions.py::test_elevated_discordance_power_regression PASSED [ 94%]
research_mission_22_1/tests/test_mission_22_1_regressions.py::test_terminology_governance_in_reports PASSED [100%]

============================= 19 passed in 28.14s ==============================
```

---

## 3. Detailed Audit by Capability

### 3.1 Mathematical & Statistical Engine
- `test_exact_mcnemar_p_values`: Revalidated symmetric tables ($p = 1.0$), pilot baseline ($b=8, c=2 \implies p = 0.109375$), and rejection thresholds ($b=12, c=3 \implies p = 0.035156$).
- `test_exact_power_pilot_scenario`: Revalidated $N = 231$ achieves $80.07\%$ exact discrete power at $q = 0.10, \delta = 0.06$.
- `test_exact_power_90_percent_target`: Revalidated $N = 299$ achieves $90.02\%$ power.
- `test_correction_of_elevated_discordance`: Independently verified that $N = 312$ achieves only $78.56\%$ and that $N = 322$ is the true minimum for $80\%$ power at $q = 0.14$.

### 3.2 Manifest Integrity & Sample Disjointness
- `test_files_exist`: Verified all manifest and outcome files present.
- `test_candidate_pool_size`: Exactly 354 unprompted problems in candidate pool.
- `test_manifest_record_counts`: Exactly 924 requests across 231 problems.
- `test_zero_overlap_with_pilot`: Cryptographically proved $|S_{\text{pilot}} \cap S_{\text{conf}}| = 0$.
- `test_condition_structure_and_hashes`: 100% of individual prompt hashes match runtime SHA-256.
- `test_stratification_quotas`: Verified uniform difficulty (47, 46, 46, 46, 46) and operator quotas (OP01: 24, OP02–OP10: 23 each).

### 3.3 Execution Security & Fail-Closed Gates
- `test_lock_file_present_on_disk`: `.cloud_execution_locked` active.
- `test_runner_fails_closed_when_cloud_requested`: Aborts with exit code 101 on cloud request.
- `test_runner_dry_run_succeeds_with_zero_cloud_calls`: Successfully validates 924 requests on CPU.
- `test_authorization_token_validation_logic`: Rejects missing tokens (102), high caps (103), and expired tokens (104).

### 3.4 Mission 22.1 Specific Regressions
- `test_resume_behavior`: Correctly reads and resumes from previously completed `request_id`s.
- `test_record_serialization_schema`: Validated all 23 required fields in output JSON records.
- `test_elevated_discordance_power_regression`: Direct regression test enforcing $N=322$ minimum.
- `test_terminology_governance_in_reports`: Verifies compliant terminology in audit documents.

---

## 4. Test Suite Verdict

**Verdict**: **PASS (19/19 TESTS, 100% PASS RATE)**  
All software modules and regression barriers are certified on CPU ($0.00 spend).
