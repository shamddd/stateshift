# StateShift Final Patch: End-to-End Integration & CLI Rehearsal Results

**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Test Suite**: `research_mission_15_6/tests/test_cli_subprocess_rehearsal.py`  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Execution Environment**: Apple Silicon M1, Python 3.13.9  
**Execution Date**: October 25, 2026  

---

## 1. Executive Summary of Subprocess Rehearsal

All **17 mandatory end-to-end rehearsal scenarios** were executed using genuine operating system subprocesses invoked via the canonical entry point:
```bash
python -m research_mission_15_6.runner.stateshift_launch [arguments]
```

Every scenario validated real OS process interactions, file locking, atomic renames, cryptographic signature evaluations, subprocess lifecycles, and exit code standards:
- **Exit Code 0**: Verified success (dataset valid, receipts signed, pod destroyed).
- **Exit Code 1**: Execution failure (SSH disconnect, SFTP hang, unconfirmed termination).
- **Exit Code 2**: Security or configuration rejection (unauthorized, invalid signature, budget mismatch).

---

## 2. 17 Rehearsal Scenarios: Complete Matrix

| Scenario ID | Name & Description | CLI Parameters / Stimulus | Expected Behavior | Observed Result | Status |
|:---|:---|:---|:---|:---|:---|
| **Scenario A** | Valid 10-Request Calibration | `--mode simulation --simulate-records 10` | Full lifecycle, verified dataset & receipts | Exit Code 0, receipts confirmed | **PASSED** |
| **Scenario B** | Controller SIGKILL | OS `kill -9` on controller PID | Watchdog detects dead PID & terminates pod | Exit Code 0, termination confirmed | **PASSED** |
| **Scenario C** | Watchdog SIGKILL | `--simulate-watchdog-crash` | Handshake detects dead watchdog & aborts | Exit Code 1, inference halted | **PASSED** |
| **Scenario D** | Embedded Test Key Rejection | `--mode calibration` (no `--allow-test-key`) | Cryptographic rejection of test key | Exit Code 2, launch aborted | **PASSED** |
| **Scenario E** | Pod ID Mismatch | Auth pod `pod_A` vs CLI `pod_B` | Exact binding check fails | Exit Code 2, authorization rejected | **PASSED** |
| **Scenario F** | Budget Ceiling Mismatch | Auth `$0.35` vs CLI `$1.00` | Budget cap tampering rejected | Exit Code 2, budget rejected | **PASSED** |
| **Scenario G** | Expired Authorization | Token `validity_seconds: -10` | Timestamp expiration check fails | Exit Code 2, expired token rejected | **PASSED** |
| **Scenario H** | Replayed Nonce Rejection | Replay of previously consumed nonce | Nonce store detects reuse | Exit Code 2, replay attack blocked | **PASSED** |
| **Scenario I** | SSH Transport Disconnect | `--simulate-ssh-disconnect` | Emergency shutdown triggered | Exit Code 1, partial dataset preserved | **PASSED** |
| **Scenario J** | SFTP Synchronization Failure| `--simulate-sftp-failure` | Sync deferred, prior checkpoint safe | Exit Code 1, partial dataset preserved | **PASSED** |
| **Scenario K** | Provider 503 Server Error | `--simulate-unconfirmed-termination` | Retries bounded, watchdog preserved | Exit Code 1, UNCONFIRMED logged | **PASSED** |
| **Scenario L** | Financial Emergency Trigger | `--simulate-spend 0.30` (Trigger: $0.25) | Immediate emergency shutdown | Exit Code 1, emergency shutdown ok | **PASSED** |
| **Scenario M** | Missing Calibration Frozen IDs| Manifest with missing request ID | Manifest verification fails | Exit Code 2, launch aborted | **PASSED** |
| **Scenario N** | Checkpoint Monotonic Promotion| Monotonic append of valid records | Atomic rename, valid promotion | Exit Code 0, 10 records verified | **PASSED** |
| **Scenario O** | Corrupted Checkpoint Rejection| `--simulate-corrupt-checkpoint` | Bad record rejected, backup intact | Exit Code 1/2, bad record dropped | **PASSED** |
| **Scenario P** | Safe Resume Re-attachment | `--resume` with pre-existing dataset | Reattaches without re-executing | Exit Code 0, deduplicated resume | **PASSED** |
| **Scenario Q** | Ambiguous STOPPED Status | RunPod returns `status: STOPPED` | Never falsely reports destruction | Exit Code 0, UNCONFIRMED logged | **PASSED** |

---

## 3. Key Observations & Invariant Validations

1. **Subprocess Isolation**: In all scenarios, controller and watchdog ran with distinct process IDs (`pid_watchdog != pid_controller`).
2. **Process Group Safety**: Processes spawned via `setpgrp` remained detached from terminal signals, preventing inadvertent cascading termination.
3. **Data Preservation Under Failure**: Under catastrophic simulated failures (Scenarios B, C, I, J, L), previously committed records were never corrupted or overwritten. Checkpoint promotion remained strictly monotonic.
4. **Zero Cloud Leakage**: Throughout all 17 scenarios, zero RunPod API calls were made that could provision physical hardware or incur billing.
