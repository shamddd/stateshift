# Phase I: Local CPU Smoke Test & Dry-Run Report

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22 — Confirmatory Trial Preflight  
**Date & Timestamp**: 2026-10-27T02:40:00+05:30  
**Target Venue**: NeurIPS 2027 Main Track  
**Execution Environment**: Local CPU Only (macOS Darwin, Python 3.13.9)  
**Cloud Spending Incurred**: **$0.00 USD**  

---

## 1. Executive Summary

In compliance with strict financial and scientific preflight gates, all confirmatory manifests, exact statistical routines, evaluator engines, and fail-closed safety barriers were subjected to an automated test suite executed entirely on local CPU resources ($0.00 cloud expenditure).

A total of **15 test cases** across three specialized test modules were executed via `pytest`. **All 15 tests passed with zero failures, zero warnings, and zero regressions (100% pass rate)**.

---

## 2. Test Execution Suite & Results Summary

```
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: /Users/shamthakare/.gemini/antigravity/scratch
collected 15 items

research_mission_22/tests/test_confirmatory_statistics.py::test_exact_mcnemar_p_values               PASSED [  6%]
research_mission_22/tests/test_confirmatory_statistics.py::test_exact_power_pilot_scenario           PASSED [ 13%]
research_mission_22/tests/test_confirmatory_statistics.py::test_exact_power_90_percent_target       PASSED [ 20%]
research_mission_22/tests/test_confirmatory_statistics.py::test_exact_power_conservative_effect      PASSED [ 26%]
research_mission_22/tests/test_confirmatory_statistics.py::test_correction_of_elevated_discordance  PASSED [ 33%]
research_mission_22/tests/test_confirmatory_trial.py::test_files_exist                               PASSED [ 40%]
research_mission_22/tests/test_confirmatory_trial.py::test_candidate_pool_size                       PASSED [ 46%]
research_mission_22/tests/test_confirmatory_trial.py::test_manifest_record_counts                    PASSED [ 53%]
research_mission_22/tests/test_confirmatory_trial.py::test_zero_overlap_with_pilot                  PASSED [ 60%]
research_mission_22/tests/test_confirmatory_trial.py::test_condition_structure_and_hashes           PASSED [ 66%]
research_mission_22/tests/test_confirmatory_trial.py::test_stratification_quotas                     PASSED [ 73%]
research_mission_22/tests/test_gpu_authorization_gate.py::test_lock_file_present_on_disk             PASSED [ 80%]
research_mission_22/tests/test_gpu_authorization_gate.py::test_runner_fails_closed_when_cloud_requested PASSED [ 86%]
research_mission_22/tests/test_gpu_authorization_gate.py::test_runner_dry_run_succeeds_with_zero_cloud_calls PASSED [ 93%]
research_mission_22/tests/test_gpu_authorization_gate.py::test_authorization_token_validation_logic PASSED [100%]

============================= 15 passed in 14.76s ==============================
```

---

## 3. Detailed Audit by Test Module

### 3.1 Module 1: Confirmatory Statistics & Power (`test_confirmatory_statistics.py`)
- **McNemar Invariants**: Verified that symmetric tables yield $p = 1.0$ and the pilot distribution ($b=8, c=2$) yields exact $p = 0.109375$. Verified that $b=12, c=3$ and $b=16, c=4$ correctly reject $H_0$ ($p < 0.05$).
- **Exact Power Verification**: Certified that $N = 231$ under $q = 0.10, \delta = 0.06$ yields $80.07\%$ power, and $N = 299$ yields $90.02\%$. Certified conservative effect $N = 337$ ($\delta = 0.05$) yields $80.07\%$.
- **Audit Correction**: Proven that under $q = 0.14$, $N = 312$ achieves only $78.56\%$ power, whereas the corrected minimum is $N = 322$ ($80.01\%$).

### 3.2 Module 2: Manifest & Problem Invariants (`test_confirmatory_trial.py`)
- **Candidate Pool Audit**: Verified exactly 354 candidate problems exist in `confirmatory_candidate_pool_manifest.jsonl`.
- **Confirmatory Manifest Audit**: Verified exactly 924 requests across 231 problems in `confirmatory_231_manifest.jsonl` and `confirmatory_231_manifest.json`.
- **Zero-Overlap Proof**: Certified $|S_{\text{pilot}} \cap S_{\text{confirmatory}}| = 0$ (zero problem collision against the 100 pilot problems).
- **Prompt Hash Integrity**: 100% of the 924 individual prompt hashes verified against runtime SHA-256 calculation.
- **Stratification Balance**: Verified exact difficulty profile (Level 1: 47, Levels 2–5: 46 each) and operator quotas (OP01: 24, OP02–OP10: 23 each).

### 3.3 Module 3: Fail-Closed Authorization Gate (`test_gpu_authorization_gate.py`)
- **Lock File Presence**: Confirmed `.cloud_execution_locked` exists on disk.
- **Fail-Closed Behavior**: Invoking runner in cloud mode immediately aborts with exit code 101.
- **Dry-Run Mode**: Verified `--dry-run` successfully processes all 924 requests on CPU with zero cloud calls.
- **Token Validation**: Verified rejection logic for missing tokens (code 102), excessive spending caps (code 103), and expired tokens (code 104).

---

## 4. Evaluator Reproduction Dry-Run

The independent cleanroom evaluator `reproduce_confirmatory_results.py` was executed directly on the authentic Study 2 pilot dataset (`stateshift_primary_400_generations.jsonl`):
- **Output Record Count**: 400 generations evaluated.
- **Accuracies**: Condition A: $64\%$, Condition D: $68\%$, Condition E: $72\%$, Condition F: $74\%$.
- **Primary Contrast**: $b = 8, c = 2, n_d = 10$, $\hat{\tau}_{F-D} = +6.00$ pp.
- **Exact McNemar p-value**: **$p = 0.109375$** (identical reproduction of historical audit).

---

## 5. Preflight Testing Verdict

**Verdict**: **PASS (15/15 TESTS, 100% PASS RATE)**  
The confirmatory trial software, statistical engines, manifests, and safety gates are fully validated and ready for authorized execution.
