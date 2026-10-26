# StateShift Mission 15.6: Independent Financial Watchdog Verification

**Project:** StateShift Research Mission 15.6  
**Document:** `05_INDEPENDENT_WATCHDOG_VERIFICATION.md`  
**Subsystem:** `research_mission_15_6.supervision.independent_financial_watchdog`  
**Status:** Certified Decoupled & Verified via Subprocess Fault-Injection  

---

## 1. Architectural Independence & Isolation Design

The StateShift Financial Watchdog is architected as a truly independent OS daemon:
1. **Decoupled Process Group:** Spawned with `os.setpgrp()` (or `setpgid`) so that signals delivered to the controller process group (e.g. `Ctrl+C` or group `SIGKILL`) do NOT propagate to the watchdog.
2. **Dedicated CLI Executable:** Invoked as a separate `python3` process directly from the OS process table.
3. **Independent Cryptographic Authorization:** Does NOT inherit in-memory state from the controller; reads and verifies the signed authorization document directly from disk using its own instance of `CryptographicAuthorizer`.
4. **Autonomous Provider Access:** Queries RunPod GraphQL directly via standard library `urllib` (zero third-party dependencies that could crash or hang).

---

## 2. PID Tracking & Controller Liveness Evaluation

The watchdog tracks the orchestrating controller's OS process via `--controller-pid <PID>`:

```python
def evaluate_controller_status(self, stale_seconds: float = 30.0) -> Tuple[str, str]:
    # 1. Clean shutdown detection
    if self.main_controller_heartbeat_path and os.path.exists(self.main_controller_heartbeat_path):
        try:
            with open(self.main_controller_heartbeat_path, "r", encoding="utf-8") as f:
                c_data = json.load(f)
                c_state = str(c_data.get("state", "")).upper()
                if c_state in ["PROVIDER_TERMINATION_CONFIRMED", "FINISHED", "LOCAL_VERIFIED"]:
                    return "CLEAN_EXIT_CONFIRMED", f"Controller completed normal termination ({c_state})"
        except Exception:
            pass

    # 2. Kernel Process Table Probe (Issue A Fix)
    if self.main_controller_pid is not None:
        try:
            os.kill(self.main_controller_pid, 0)
        except OSError as e:
            # Process dead (e.g. SIGKILL, crash, unhandled exception)
            return "CONFIRMED_DEAD", f"Controller process {self.main_controller_pid} is confirmed dead: {e}"

    # 3. Heartbeat Freshness Evaluation
    if self.main_controller_heartbeat_path and os.path.exists(self.main_controller_heartbeat_path):
        try:
            with open(self.main_controller_heartbeat_path, "r", encoding="utf-8") as f:
                c_data = json.load(f)
                ts = c_data.get("timestamp_utc", 0.0)
                if (time.time() - ts) > stale_seconds:
                    return "STALE_HEARTBEAT", f"Controller heartbeat stale (>{stale_seconds}s)"
        except Exception:
            pass

    return "NORMAL", "Controller operational"
```

---

## 3. Verified Fault-Injection Test Scenarios

### Test 1: Controller SIGKILL Immediate Emergency Termination (Issue A)
- **Test:** `test_issue_a_controller_confirmed_dead_triggers_emergency_termination`
- **Mechanism:** Main controller PID is killed via `SIGKILL`. Watchdog runs tick with spend = $0.00 and runtime = 0.0m.
- **Verification:** Watchdog transitions to `WatchdogLifecycleState.CONTROLLER_FAILED`, detects `CONFIRMED_DEAD`, and dispatches immediate emergency termination.
- **Result:** **PASSED**.

### Test 2: Watchdog Survives Controller Death in Separate Subprocess
- **Test:** `test_scenario_B_controller_sigkill_watchdog_terminates_pod`
- **Mechanism:** Real OS subprocesses spawned: dummy controller and independent watchdog. Controller process killed with `signal.SIGKILL`.
- **Verification:** Watchdog process survives, inspects kernel table, confirms controller death, persists `CONTROLLER_FAILED` / `TERMINATION_REQUESTED`, and executes emergency teardown.
- **Result:** **PASSED**.

### Test 3: Watchdog SIGKILL Halts Controller Scheduling
- **Test:** `test_scenario_C_watchdog_sigkill_controller_halts`
- **Mechanism:** Watchdog process killed with `signal.SIGKILL`. Controller runs its supervision cycle.
- **Verification:** Controller checks `check_watchdog_alive()`, detects missing process, immediately transitions to `INTEGRITY_FAILURE`, and aborts execution to prevent unsupervised GPU burn.
- **Result:** **PASSED**.
