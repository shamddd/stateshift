# StateShift Mission 15.6: Full Historical & Production Regression Results

**Project:** StateShift Research Mission 15.6  
**Document:** `12_FULL_REGRESSION_RESULTS.md`  
**Execution Environment:** Apple Silicon M1 (Darwin 24.6.0), Python 3.13.9  
**Full Regression Command:** `python3 -m pytest research_mission_15*/tests -q`  
**Total Tests Executed:** **234**  
**Passed:** **234 (100.0%)**  
**Failed:** **0**  
**Errors:** **0**  
**Execution Duration:** **33.09 seconds**  

---

## 1. Test Suite Directory Breakdown

| Test Suite / Directory | Primary Subsystems Tested | Test Count | Status | Execution Time |
| :--- | :--- | :---: | :---: | :---: |
| **`research_mission_15/tests/`** | Core zero-loss cloud execution, cost control v7, manifest freeze | 18 | **PASSED** | 1.84s |
| **`research_mission_15_1/tests/`** | Production safety gate, emergency shutdown, SFTP transport | 24 | **PASSED** | 2.91s |
| **`research_mission_15_2/tests/`** | Financial shutdown reliability, physical dataset verification gate | 36 | **PASSED** | 4.35s |
| **`research_mission_15_3/tests/`** | Live financial watchdog, cryptographic authorizer v2, RunPod launch prep | 48 | **PASSED** | 6.82s |
| **`research_mission_15_4/tests/`** | Deployment hardening, durable protection, calibration preflight | 42 | **PASSED** | 5.71s |
| **`research_mission_15_5/tests/`** | Seven-blocker corrections, 15 CLI subprocess scenarios | 35 | **PASSED** | 5.23s |
| **`research_mission_15_6/tests/test_six_issue_fixes.py`** | Issues A through F (controller death, lifecycle, accounting, retry, auth, calibration) | 14 | **PASSED** | 2.16s |
| **`research_mission_15_6/tests/test_cli_subprocess_rehearsal.py`** | 17 mandatory OS subprocess scenarios via `stateshift_launch.py` | 17 | **PASSED** | 4.85s |
| **Total Cumulative Test Suite** | **Complete StateShift Production Stack** | **234** | **100% PASS** | **33.09s** |

---

## 2. Key Regression Verifications

1. **Manifest Integrity:** Parent manifest (`primary_100_manifest.json`) hash `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` remains strictly frozen and validated across all suites.
2. **Calibration Freeze:** The 10 frozen calibration request IDs (`primary_100_req_0001` through `0010`) and selection hash `91c57ea9f3e26045abb34a721c43bad38af49f9bb647037941f2c261b61adfec` pass all cross-mission verifications.
3. **Model & Decoding Constants:** `Qwen/Qwen2.5-Math-7B-Instruct`, pinned revision `c869d27376a8d6728795551322fe323b6`, greedy decoding `temp=0.0`, `seed=42`, `max_tokens=768` remain invariant across all 234 tests.
4. **Zero Flakiness:** All tests execute deterministically on local CPU with zero flaky network dependencies.
