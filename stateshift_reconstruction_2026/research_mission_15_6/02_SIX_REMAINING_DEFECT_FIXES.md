# StateShift Mission 15.6: Forensic Analysis of Six Defect Fixes (Issues A–F)

**Project:** StateShift Research Mission 15.6  
**Document:** `02_SIX_REMAINING_DEFECT_FIXES.md`  
**Author:** Autonomous Scientific Research & Engineering Laboratory  
**Status:** All Six Defect Fixes Fully Implemented, Unit-Tested, and Certified  

---

## Executive Summary of Defect Resolutions

Mission 15.5 left six critical defects that prevented safe production GPU deployment. Mission 15.6 resolved all six issues at the architectural root. Every fix is backed by dedicated, executable pytest regression suites.

| Issue | Vulnerability / Root Cause | Engineered Resolution | Verifying Tests |
| :--- | :--- | :--- | :--- |
| **A** | Watchdog waited for spend breach or timeout if controller was SIGKILLed | `evaluate_controller_status()` checks `os.kill(pid, 0)`. On `OSError`, detects `CONFIRMED_DEAD` and dispatches immediate termination on the next tick. | `test_issue_a_controller_confirmed_dead_triggers_emergency_termination`<br>`test_issue_a_controller_clean_exit_allows_graceful_watchdog_shutdown`<br>`test_issue_a_controller_stale_heartbeat_detection` |
| **B** | Ambiguous watchdog state tracking; no explicit lifecycle machine | Formal 8-state `WatchdogLifecycleState` enum with atomic transitions written to disk on every tick. | `test_issue_b_watchdog_lifecycle_states` |
| **C** | Clock restart at zero on runner crash; non-conservative spend baseline | `calculate_effective_spend()` incorporates `pre_existing_uptime_seconds` and computes `max(provider, balance_delta, elapsed_estimate)`. | `test_issue_c_pre_existing_uptime_spend_calculation`<br>`test_issue_c_max_effective_spend_reconciliation` |
| **D** | Unconfirmed termination logged as success or hanging indefinitely | Durable 5-state retry machine (`TERMINATION_REQUEST_ATTEMPTED` $\rightarrow$ `TERMINATION_ACKNOWLEDGED` $\rightarrow$ `TERMINATION_CONFIRMED`). On failure, logs `CRITICAL_UNCONFIRMED_TERMINATION_{pod_id}.json` without claiming destruction. | `test_issue_d_durable_termination_success`<br>`test_issue_d_durable_termination_unconfirmed_escalation` |
| **E** | Watchdog relied on controller memory for spend limits | Watchdog independently verifies Ed25519 signature, public key, and pod bindings directly inside its own OS process, clamping limits autonomously. | `test_issue_e_watchdog_verifies_valid_signed_authorization`<br>`test_issue_e_watchdog_rejects_tampered_authorization`<br>`test_issue_e_watchdog_rejects_pod_mismatch` |
| **F** | Verifier expected 400 records during calibration, failing valid runs | Mode-aware `is_calibration: bool` in `IndependentDatasetVerifierV2`. When True, expects exactly the 10 frozen IDs from `calibration_10_manifest.json` and outputs calibration subset hash. | `test_issue_f_calibration_exact_10_records_pass`<br>`test_issue_f_calibration_rejects_incomplete_dataset`<br>`test_issue_f_calibration_rejects_extra_unexpected_records` |

---

## Detailed Forensic Examination of Each Fix

### 1. Issue A: Controller Death Emergency Termination Policy
- **Vulnerability:** If the main controller process crashed, hung, or was terminated by an external `SIGKILL`, the watchdog process previously continued running in a sleep loop, only terminating the pod if the dollar budget or runtime ceiling was eventually breached. This allowed dead controller pods to burn unnecessary funds.
- **Root Cause:** Watchdog only inspected the filesystem heartbeat timestamp; it did not query the operating system process table for PID existence.
- **Architectural Solution:**
  In `research_mission_15_6/supervision/independent_financial_watchdog.py`:
  ```python
  def evaluate_controller_status(self, stale_seconds: float = 30.0) -> Tuple[str, str]:
      # 1. Clean exit check
      if self.main_controller_heartbeat_path and os.path.exists(self.main_controller_heartbeat_path):
          with open(self.main_controller_heartbeat_path, "r") as f:
              c_data = json.load(f)
              if c_data.get("state") in ["PROVIDER_TERMINATION_CONFIRMED", "FINISHED", "LOCAL_VERIFIED"]:
                  return "CLEAN_EXIT_CONFIRMED", "Controller completed normal termination"
      # 2. OS Process liveness check
      if self.main_controller_pid is not None:
          try:
              os.kill(self.main_controller_pid, 0)
          except OSError as e:
              return "CONFIRMED_DEAD", f"Controller process {self.main_controller_pid} is confirmed dead: {e}"
      # 3. Heartbeat freshness
      ...
  ```
  On `CONFIRMED_DEAD`, the watchdog transitions to `WatchdogLifecycleState.CONTROLLER_FAILED` and dispatches immediate provider termination on that very tick.

### 2. Issue B: Explicit Watchdog Lifecycle State Ownership
- **Vulnerability:** The watchdog lifecycle was previously implicit, relying on arbitrary boolean flags (`stop_requested`, `dispatched`), creating race conditions during process restarts and audits.
- **Architectural Solution:**
  Defined 8 formal lifecycle states:
  `NOT_STARTED`, `STARTING`, `ACTIVE`, `CONTROLLER_FAILED`, `TERMINATION_REQUESTED`, `TERMINATION_UNCONFIRMED`, `TERMINATION_CONFIRMED`, `WATCHDOG_EXITED`.
  Every transition is written atomically to `watchdog_state_{experiment_id}.json` using a temporary file and `os.replace()`.

### 3. Issue C: Reconciled, Conservative Financial Baseline Accounting
- **Vulnerability:** If an inference job was interrupted and resumed on an existing pod, or if the watchdog restarted, the elapsed time baseline would reset to zero, causing underestimation of actual spend.
- **Architectural Solution:**
  Incorporated `pre_existing_uptime_seconds` into the conservative elapsed time estimate:
  $$\text{effective\_spend} = \max(\text{provider\_spend},\; \Delta\text{balance},\; \text{conservative\_elapsed})$$
  Where:
  $$\text{conservative\_elapsed} = \left(\frac{t_{\text{pre\_existing}} + (t_{\text{mono\_now}} - t_{\text{mono\_start}})}{3600}\right) \times \text{gpu\_hourly\_rate}$$
  $$\Delta\text{balance} = \max(0.0,\; \text{initial\_account\_balance} - \text{current\_account\_balance})$$

### 4. Issue D: Durable Termination Retry State Machine
- **Vulnerability:** If the RunPod GraphQL mutation returned 200 but the pod took 15 seconds to transition to `TERMINATED`, the watchdog previously either assumed immediate destruction or threw an unhandled exception.
- **Architectural Solution:**
  Implemented bounded 5-attempt retry loop with exponential backoff ($1.0\text{s} \rightarrow 1.5\text{s} \rightarrow 2.25\text{s} \dots$).
  Transitions:
  $$\text{TERMINATION\_REQUEST\_ATTEMPTED} \rightarrow \text{TERMINATION\_ACKNOWLEDGED} \rightarrow \text{TERMINATION\_CONFIRMED}$$
  If unconfirmed after 5 attempts:
  Transitions to `TERMINATION_UNCONFIRMED`, writes `watchdog_termination_receipt_{exp_id}.json` with `confirmed_by_provider: false`, and outputs a critical operational escalation file: `CRITICAL_UNCONFIRMED_TERMINATION_{pod_id}.json`.

### 5. Issue E: Independent Authorization Verification Inside Watchdog
- **Vulnerability:** In Mission 15.5, the watchdog accepted CLI arguments (`--max-authorized`, `--emergency-trigger`) passed by the controller process, allowing a corrupted or rogue controller to pass inflated spend ceilings to the watchdog.
- **Architectural Solution:**
  The watchdog accepts `--authorization` and `--trusted-public-key`. In `IndependentFinancialWatchdog.__init__()`:
  - Re-reads physical authorization file from disk.
  - Instantiates `CryptographicAuthorizer` directly inside the watchdog process.
  - Validates the Ed25519 signature against the PI's trusted public key.
  - Validates that `payload.pod_id == self.pod_id` and `payload.experiment_id == self.experiment_id`.
  - Authoritatively clamps its internal `max_authorized_usd` and `emergency_trigger_usd` directly to the signed values.
  - Raises `PermissionError` and refuses to supervise if authorization is invalid or tampered.

### 6. Issue F: Exact Mode-Specific Completion Semantics
- **Vulnerability:** `IndependentDatasetVerifierV2` previously required 400 completed records regardless of whether the execution was in CALIBRATION (10 requests) or PRODUCTION (400 requests) mode.
- **Architectural Solution:**
  Added `is_calibration: bool = False` to `IndependentDatasetVerifierV2`. When True:
  - Validates against `FROZEN_CALIBRATION_REQUEST_IDS` (the exact 10 frozen requests).
  - Rejects if record count $\neq 10$.
  - Rejects if any record ID is outside the frozen 10 IDs.
  - Rejects if any of the frozen 10 IDs are missing.
  - Generates receipt with `is_calibration: true` and `calibration_subset_hash: 91c57ea9f3e26045abb34a721c43bad38af49f9bb647037941f2c261b61adfec`.
