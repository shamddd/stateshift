# StateShift Final Patch: Mandatory Watchdog Startup Handshake & Verified Readiness (Defect 2)

**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Components**:  
- `research_mission_15_6.supervision.independent_financial_watchdog.py`  
- `research_mission_15_6.runner.stateshift_production_runner_v10.py`  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Audit Finding Addressed**: Defect 2 (Unverified Subprocess Readiness Before Inference Deployment)  

---

## 1. Problem Definition & Architectural Vulnerability

In previous architectures, the main production runner spawned the independent watchdog process as a decoupled background OS subprocess (`subprocess.Popen(..., stdout=DEVNULL, stderr=DEVNULL)`), but immediately proceeded to remote SSH deployment without verifying:

1. Whether the watchdog process actually started or immediately failed with a syntax error, bad interpreter path, or missing dependency.
2. Whether the watchdog passed its independent cryptographic Ed25519 authorization audit.
3. Whether the watchdog successfully verified RunPod credentials and established an account baseline.
4. Whether the watchdog process ID in the PID file belonged to an alive, distinct process in the operating system process table.
5. Whether the financial ceilings adopted by the watchdog matched or safely restricted the runner's CLI parameters.

**Consequence of Failure**: If the watchdog died during startup, the main runner would proceed with remote GPU inference completely unmonitored. If an infinite loop or unexpected compute cost occurred, financial limits would not be enforced.

---

## 2. Handshake Protocol Specification

To make unsupervised deployment mathematically impossible, a **mandatory 12-point synchronous startup handshake** was introduced:

```
[Main Controller]                                    [Independent Watchdog]
       |                                                        |
       |-- 1. Spawn Subprocess (PID_watchdog) ----------------->|
       |                                                        |-- Verify Ed25519 Auth
       |                                                        |-- Establish Balance Baseline
       |                                                        |-- Check Preservation Floor
       |                                                        |-- Write .tmp Receipt
       |                                                        |-- Atomic Rename to:
       |                                                        |   watchdog_readiness_{exp}_{sess}.json
       |                                                        |
       |-- 2. wait_for_watchdog_readiness() ------------------->|
       |      - Poll for receipt (15s timeout)                  |
       |      - Validate 12-Point Checklist                     |
       |                                                        |
   [VERIFIED]                                               [ACTIVE]
       |                                                        |
       |-- 3. Deploy and Launch Remote Inference -------------->|
```

### The 12-Point Readiness Checklist
When `wait_for_watchdog_readiness()` inspects `watchdog_readiness_{experiment_id}_{session_id}.json`, all 12 criteria must pass:

| # | Check | Validation Rule | Failure Consequence |
|---|:---|:---|:---|
| 1 | **Status** | Must strictly equal `"READY"` | Abort inference, emergency kill pod |
| 2 | **Lifecycle State** | Must equal `"ACTIVE"` or `"STARTING"` | Abort inference, emergency kill pod |
| 3 | **Process Decoupling** | `watchdog_pid != os.getpid()` (Must not be self) | Abort inference, emergency kill pod |
| 4 | **Process Aliveness** | `os.kill(watchdog_pid, 0)` must succeed (ESRCH = dead) | Abort inference, emergency kill pod |
| 5 | **Premature Death Check** | `subprocess.poll() is None` (No early exit code) | Abort inference, emergency kill pod |
| 6 | **Experiment Binding** | `receipt.experiment_id == runner.experiment_id` | Abort inference, emergency kill pod |
| 7 | **Session Binding** | `receipt.session_id == runner.execution_id` | Abort inference, emergency kill pod |
| 8 | **Pod ID Binding** | `receipt.pod_id == runner.pod_id` | Abort inference, emergency kill pod |
| 9 | **Max Authorized Spend** | `receipt.max_authorized_usd <= runner.effective_max_spend + 1e-4` | Abort inference, emergency kill pod |
| 10 | **Emergency Trigger** | `receipt.emergency_trigger_usd <= runner.effective_emergency_trigger + 1e-4` | Abort inference, emergency kill pod |
| 11 | **Receipt Freshness** | `abs(time.time() - receipt.timestamp_utc) <= timeout + 5.0s` | Abort inference, emergency kill pod |
| 12 | **Preservation Floor** | `receipt.account_preservation_floor_usd >= 7.00 - 1e-4` | Abort inference, emergency kill pod |

---

## 3. Implementation Details

### Watchdog Receipt Publishing
In `IndependentFinancialWatchdog.publish_readiness_receipt()`:
```python
def publish_readiness_receipt(self) -> str:
    receipt = {
        "status": "READY",
        "lifecycle_state": self.lifecycle_state.value,
        "watchdog_pid": os.getpid(),
        "experiment_id": self.experiment_id,
        "pod_id": self.pod_id,
        "session_id": self.session_id,
        "timestamp_utc": time.time(),
        "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "max_authorized_usd": self.max_authorized_usd,
        "emergency_trigger_usd": self.emergency_trigger_usd,
        "account_preservation_floor_usd": self.account_preservation_floor_usd,
        "initial_account_balance": self.initial_account_balance,
        "pre_existing_uptime_seconds": self.pre_existing_uptime_seconds,
        "gpu_hourly_rate": self.gpu_hourly_rate,
        "reported_gpu_hourly_rate": self.reported_gpu_hourly_rate
    }
    tmp = self.readiness_receipt_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, self.readiness_receipt_path)
    return self.readiness_receipt_path
```

### Main Runner Verification Gate
In `StateshiftProductionRunnerV10.execute_complete_lifecycle()`:
```python
# Spawn independent watchdog process
self.spawn_independent_watchdog()

# Mandatory Handshake Gate
if not self.wait_for_watchdog_readiness():
    self.transition_to(ProductionState.INTEGRITY_FAILURE)
    self.terminate_emergency("Watchdog startup handshake failed or timed out")
    return False

# Inference is only reached if handshake succeeded:
pid = self.deploy_and_launch_remote()
```

---

## 4. Test Verification & Proof of Resolution

The handshake logic was verified across 6 focused tests in `test_final_three_defects.py`:
1. `test_defect2_readiness_receipt_written_atomically`: Verified atomic write of valid receipt by watchdog.
2. `test_defect2_handshake_success`: Verified successful verification when live external subprocess receipt is present.
3. `test_defect2_handshake_rejects_matching_controller_pid`: Verified rejection when receipt contains runner's own PID.
4. `test_defect2_handshake_rejects_dead_pid`: Verified rejection when receipt contains a non-existent OS PID.
5. `test_defect2_handshake_rejects_stale_receipt`: Verified rejection when receipt timestamp is 5 minutes old.
6. `test_defect2_handshake_timeout_aborts_inference`: Verified that missing receipt times out and halts runner before launch.
