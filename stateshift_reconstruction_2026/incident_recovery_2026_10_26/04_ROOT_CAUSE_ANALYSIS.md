# StateShift Incident Recovery — Comprehensive Root Cause Analysis
**Project**: StateShift (NeurIPS 2027 / TMLR)  
**Principal Investigator**: Sham Satish Thakare  
**Incident Date**: October 25–26, 2026  
**Auditor**: Senior Distributed Systems Reliability & Security Auditor  
**Incident Classification**: Severity 1 (Financial Safety Invariant Violation)  

---

## 1. Executive Summary

On October 25, 2026, at 14:42 UTC (20:12 IST), StateShift launched execution attempt 4 to perform a 10-request physical calibration on a RunPod Secure Cloud RTX 4090 GPU. The session had strict human-authorized constraints: a spending limit of $0.35 USD, an emergency kill trigger of $0.25 USD, and an account preservation floor of $7.00 USD.

At 23:24 UTC (04:54 IST on October 26), the Principal Investigator discovered that the account balance had collapsed to **$1.3261 USD**, representing an unauthorized expenditure of **$7.7982 USD** on Attempt 4 ($7.9621 USD cumulative) and a breach of the preservation floor by **$5.6739 USD**.

The incident was caused by the compound interaction of two fundamental flaws:
1. **Deferred Watchdog Activation (Architectural Defect)**: The independent financial watchdog daemon was placed in Step 5 of the execution sequence, while compute pod provisioning occurred in Step 2.
2. **Paramiko Channel Deadlock (Implementation Defect)**: The remote model pre-caching command executed in Step 3 called `stdout.channel.recv_exit_status()` without a wall-clock deadline. When the remote download stalled, the orchestrator process hung indefinitely with zero financial supervision active.

---

## 2. Deep Dive: Architectural Failure Mechanics

```mermaid
flowchart TD
    subgraph Defective Pipeline (Attempt 4)
        A[Start Calibration] --> B[Step 1: Check Pre-Flight Balance $9.12]
        B --> C[Step 2: Provision RTX 4090 Pod wets1b0dsnpzif]
        C --> D[Pod Starts Billing @ $0.89/hr]
        D --> E[Step 3: Staging via SSH]
        E --> F["run_ssh('python3 cache_model.py')"]
        F --> G["stdout.channel.recv_exit_status() [NO TIMEOUT]"]
        G -.->|BLOCKED FOR 8.76 HOURS| H[DEADLOCK / HANG]
        H -.->|Never Reached| I[Step 4: Generate Ed25519 Auth]
        I -.->|Never Reached| J[Step 5: Spawn Independent Watchdog]
        J -.->|Never Reached| K[Step 6: Execute 10 Calibration Requests]
    end
```

### 2.1 Flaw 1: Deferred Watchdog Inversion (The Supervisor-First Violation)
In production distributed systems handling billable infrastructure, the supervising authority must be active, durable, and polling **before** any billable asset is provisioned.

In the calibration orchestration script (`execute_physical_calibration.py`):
- Line 122: `runpod.create_pod(...)` provisioned the pod on RunPod Secure Cloud. At this exact microsecond, cloud billing commenced at $0.89/hr.
- Line 167–262: The script performed extensive interactive network operations over SSH: testing GPU, querying workspace disk, running `pip install`, uploading manifest and runner scripts, and pre-caching 14GB of model weights.
- Line 323: The launcher `stateshift_launch.py`—the only component configured to spawn `IndependentFinancialWatchdog`—was scheduled to run in **Step 5**.

Because Step 5 was dependent on the synchronous success of Step 3, any hang or block in Step 3 guaranteed that the watchdog would never be spawned. The pod existed in cloud infrastructure with zero financial oversight.

### 2.2 Flaw 2: The Paramiko `recv_exit_status()` Timeout Fallacy
In `execute_physical_calibration.py`, the SSH execution helper was written as follows:

```python
def run_ssh(cmd, timeout=180):
  stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
  exit_code = stdout.channel.recv_exit_status()
  out_str = stdout.read().decode("utf-8").strip()
  err_str = stderr.read().decode("utf-8").strip()
  return exit_code, out_str, err_str
```

**The Fatal Flaw**:
In the Python `paramiko` library:
- The `timeout` parameter passed to `ssh.exec_command(cmd, timeout=timeout)` sets the timeout for **sending the exec request packet** over the TCP channel.
- `stdout.channel.recv_exit_status()` is a blocking method that waits until the remote SSH daemon transmits an exit code status message (`SSH_MSG_CHANNEL_REQUEST` with "exit-status").
- `recv_exit_status()` accepts **zero parameters** and does **not** inherit the socket timeout. It blocks indefinitely until the remote process terminates or the connection drops.
- When `python3 cache_model.py` stalled on the remote pod (waiting on network sockets from Hugging Face or hung in PyTorch initialization), the remote process never exited, the channel remained open, and the local Python orchestrator was trapped in an uninterruptible sleep state.

### 2.3 Flaw 3: Absence of Monotonic Wall-Clock Deadlines
The orchestrator script contained no outer deadline enforcement. There was no:
- Background watchdog thread checking elapsed time.
- `signal.alarm()` or OS timer.
- Heartbeat emission to an external supervisor.
- Watchdog ping mechanism during the staging phase.

### 2.4 Flaw 4: Insufficient Diagnostic Between Attempts
Prior to Attempt 4, three distinct failures occurred:
- Attempt 1 failed on `ModuleNotFoundError` in watchdog.
- Attempt 2 failed on truncated revision hash `c869d27376a8d6728795551322fe323b6` and PyTorch version mismatch.
- Attempt 3 failed on detached launch socket closure.

Rather than conducting a full offline architectural audit to unify provisioning and supervision under a single fail-closed controller, inline modifications were made and Attempt 4 was immediately triggered.

---

## 3. Systematic Failure Mode Matrix

| Failure Mode | Location | Expected Defense | What Actually Happened | Systemic Gap |
|--------------|----------|------------------|------------------------|--------------|
| **Remote Staging Stall** | Step 3 (`cache_model.py`) | Wall-clock abort after 300s | `recv_exit_status()` blocked forever | No wall-clock deadline on channel polling |
| **Financial Overrun** | RunPod Account | Emergency kill at $0.25 spend | No watchdog running; spend reached $7.79 | Watchdog spawned in Step 5 instead of Step 0 |
| **Account Floor Breach** | RunPod Account | Preserve $7.00 balance floor | Balance fell to $1.3261 | Supervision deferred until after staging |
| **Orchestrator Hang** | Local OS Process | Outer supervisor kills orchestrator | Subprocess ran silently for 8.76 hours | No decoupled system-level supervisor |
| **Unsupervised Cloud Asset** | RunPod Provider | Auto-terminate orphaned pods | Pod ran in `RUNNING` until user killed it | No TTL or container self-termination script |

---

## 4. Mandatory Remediation Directives

To guarantee that this class of failure is physically impossible in the future, the following non-negotiable architectural invariants must be implemented:

1. **The Supervisor-First Invariant**:
   No pod creation API call may ever be issued unless an independent watchdog process is already verified running, possessing valid credentials, polling the account balance, and holding the pod cancellation authority.
2. **Channel Polling with Monotonic Deadlines**:
   All SSH channel operations must replace `recv_exit_status()` with explicit polling loops governed by `time.monotonic()` deadlines. If the deadline expires, the channel must be forcibly closed, the remote process killed, and an immediate abort raised.
3. **Hard Staging Timeouts**:
   Model downloading and staging must have a hard, non-extendable timeout (maximum 180 seconds). Any stall triggers instant container destruction.
4. **Permanent Fail-Closed Execution Lock**:
   All provisioning pathways must be locked by default via persistent filesystem and environment locks. Execution cannot occur without multi-gate validation.
