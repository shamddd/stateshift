# 10 Exact CLI Subprocess Operational Results

**Suite:** `research_mission_15_5/tests/test_cli_subprocess_15_scenarios.py`  
**Execution Status:** 15 Passed / 0 Failed (100% Pass Rate).

---

## 1. Scenario Results Log
1. **Scenario A (Valid 10-Request Simulation):** `PASSED` — Complete simulated lifecycle produced 10 rollouts, verified receipts, exit code 0.
2. **Scenario B (Controller SIGKILL Watchdog Survives):** `PASSED` — Killing controller with SIGKILL left watchdog running with independent PID.
3. **Scenario C (Embedded Test Key Rejected in Production):** `PASSED` — Authorization with test key seed rejected with fatal permission error.
4. **Scenario D (Pod ID Mismatch Rejected):** `PASSED` — Authorization bound to pod_1 rejected when CLI passed pod_2.
5. **Scenario E (Simulation Injection Rejected):** `PASSED` — Simulation flags rejected with exit code 2 when mode was CALIBRATION.
6. **Scenario F (Budget Mismatch Rejected):** `PASSED` — Authorization requesting 0.50 in calibration rejected against 0.35 ceiling.
7. **Scenario G (Provider API Failure Unconfirmed):** `PASSED` — HTTP 500 error during termination classified as UNCONFIRMED, alert logged.
8. **Scenario H (Financial Emergency Shutdown):** `PASSED` — Spend reaching 0.30 tripped emergency trigger at 0.25, dispatched immediate shutdown.
9. **Scenario I (Missing Calibration ID Fails):** `PASSED` — Incomplete manifest missing frozen IDs aborted during pre-flight validation.
10. **Scenario J (Valid Checkpoint Preserved):** `PASSED` — Transactional candidate promotion atomically updated dataset.
11. **Scenario K (Corrupted Checkpoint Rejected):** `PASSED` — Corrupted candidate rejected with rollback to last valid checkpoint.
12. **Scenario L (Resume Reattach Reconciled):** `PASSED` — Safe resume verified remote PID and prevented duplicate runner execution.
13. **Scenario M (Watchdog Crash Halts Controller):** `PASSED` — Simulated watchdog crash caused controller to halt scheduling immediately.
14. **Scenario N (Ambiguous Provider Response Never Confirmed):** `PASSED` — desiredStatus: STOPPED treated as active/unconfirmed.
15. **Scenario O (Complete Calibration Receipts):** `PASSED` — Generated cryptographic termination receipt with provider confirmation.
