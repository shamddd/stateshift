# StateShift Mission 15.6: End-to-End Subprocess Rehearsal & Fault Injection Results

**Project:** StateShift Research Mission 15.6  
**Document:** `11_END_TO_END_REHEARSAL_RESULTS.md`  
**Test Suite:** `research_mission_15_6/tests/test_cli_subprocess_rehearsal.py`  
**Execution Environment:** Apple Silicon M1 (Darwin 24.6.0), Python 3.13.9  
**Total Scenarios:** 17  
**Pass Rate:** **100% (17 / 17 Passed)**  

---

## 1. Rehearsal Execution Summary

Every scenario was executed as a live operating system subprocess invoking `python3 -m research_mission_15_6.runner.stateshift_launch [arguments]`, validating the true runtime integration, signal handling, process decoupling, and filesystem state transitions.

```
============================= test session starts ==============================
collected 17 items

research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_A_valid_10_request_simulation PASSED [  5%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_B_controller_sigkill_watchdog_terminates_pod PASSED [ 11%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_C_watchdog_sigkill_controller_halts PASSED [ 17%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_D_test_key_rejected_in_calibration PASSED [ 23%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_E_pod_id_mismatch_rejected PASSED [ 29%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_F_budget_mismatch_rejected PASSED [ 35%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_G_expired_authorization_rejected PASSED [ 41%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_H_replayed_nonce_rejected PASSED [ 47%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_I_ssh_transport_disconnect PASSED [ 52%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_J_sftp_sync_failure PASSED [ 58%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_K_provider_503_records_unconfirmed PASSED [ 64%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_L_financial_emergency_trigger PASSED [ 70%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_M_missing_calibration_id_fails PASSED [ 76%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_N_valid_checkpoint_promoted PASSED [ 82%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_O_corrupted_checkpoint_rejected PASSED [ 88%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_P_safe_resume_reattach PASSED [ 94%]
research_mission_15_6/tests/test_cli_subprocess_rehearsal.py::test_scenario_Q_ambiguous_provider_status_never_claims_destruction PASSED [100%]

============================== 17 passed in 4.85s ==============================
```

---

## 2. Detailed Scenario Breakdown & Forensic Evidence

| Scenario | Objective / Fault Injected | Expected Behavior | Actual Observed Result | Exit Code | Status |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **A** | Complete simulated calibration | 10 valid rollouts, receipts generated, clean teardown | Target 10 achieved; dataset & receipts written; confirmed termination | **0** | **PASSED** |
| **B** | Controller SIGKILL | Watchdog detects dead PID & terminates remote pod | Watchdog survives SIGKILL; detects `CONFIRMED_DEAD`; logs teardown | N/A | **PASSED** |
| **C** | Watchdog SIGKILL | Controller halts scheduling immediately | Controller detects watchdog death; halts loop; initiates teardown | **1** | **PASSED** |
| **D** | Dev test key used in calibration | Reject launch immediately | "Embedded repository test key cannot authorize paid execution" | **2** | **PASSED** |
| **E** | Pod ID mismatch | Reject launch before contacting cloud | "Pod ID mismatch: auth specifies pod_A, active is pod_B" | **2** | **PASSED** |
| **F** | Budget mismatch | Reject CLI budget exceeding auth limit | "CLI budget $1.50 exceeds signed authorized limit $0.35" | **2** | **PASSED** |
| **G** | Expired authorization token | Reject expired session token | "Authorization expired at ..." | **2** | **PASSED** |
| **H** | Replayed authorization nonce | Reject reuse of session nonce | "Authorization nonce '...' has already been used" | **2** | **PASSED** |
| **I** | Transient SSH drop | Reconnect or safely halt loop | Transient drop caught; loop halts cleanly without infinite hang | **1** | **PASSED** |
| **J** | SFTP connection timeout | Halt sync, preserve prior valid checkpoint | SFTP failure caught; prior valid checkpoint preserved | **1** | **PASSED** |
| **K** | Provider 503 during termination | Retries bounded, records UNCONFIRMED | 5 retries attempted; `TERMINATION_UNCONFIRMED`; alert file created | **1** | **PASSED** |
| **L** | Spend breaches emergency ($0.25) | Dispatches immediate emergency termination | Emergency trigger reached; emergency teardown dispatched | **1** | **PASSED** |
| **M** | Calibration manifest corrupted | Reject manifest missing frozen IDs | "CALIBRATION Manifest missing expected frozen IDs" | **2** | **PASSED** |
| **N** | Checkpoint promotion | Monotonic promotion of valid records | 10 records written; atomic promotion via `os.replace` verified | **0** | **PASSED** |
| **O** | Corrupted checkpoint candidate | Reject corrupted candidate, keep prior valid | Corrupt JSON candidate rejected; prior authoritative dataset preserved | **1** | **PASSED** |
| **P** | Safe resume reattachment | Reattach without duplicate generation | Runner reconciles state; resumes without double-counting | **0** | **PASSED** |
| **Q** | Provider reports status `STOPPED` | Never report confirmed destruction | Watchdog treats `STOPPED` as unconfirmed; persists `confirmed: false` | N/A | **PASSED** |

---

## 3. Rehearsal Certification Verdict

The canonical production entry point and decoupled financial watchdog have successfully passed all 17 fault-injection scenarios. Subprocess isolation, signal propagation, and exit code contracts are completely certified.
