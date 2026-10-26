# StateShift Research Mission 14 — Deliverable 05: Orchestrator Timeout Architecture Repair

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Investigating Role**: Independent Forensic Recovery Auditor  
**Component Repaired**: `runner/robust_cloud_orchestrator_v6.py`  
**Test Suite**: `tests/test_robust_orchestrator.py` (4/4 CPU-Only Tests Passing)  
**Date**: October 25, 2026  

---

## 1. Analysis of Mission 13 Architectural Defect

In Mission 13, the orchestrator attempted to execute the entire 400-rollout primary experiment as a single synchronous foreground SSH command:
```python
# Flawed Architecture in Mission 13 (orchestrator_mission13.py line 309):
exit_code, _ = self.execute_remote_cmd(cmd, timeout=1800)
```
### Why This Failed:
1. **Socket Timeout**: Paramiko's `exec_command(..., timeout=1800)` sets a socket-level read timeout on the local client machine. When inference elapsed past 1,800 seconds (30 minutes), the local TCP socket raised `paramiko.buffered_pipe.PipeTimeout` followed by `socket.timeout`.
2. **Premature Termination**: The orchestrator's exception handling jumped immediately to `finally: orch.terminate_pod_and_verify()`.
3. **Catastrophic Premature Erasure**: Because the SFTP download was placed *after* the blocking command, the pod was destroyed before results could be retrieved from the ephemeral container filesystem (`/workspace/stateshift/data/primary_7b_results.jsonl`).

---

## 2. Re-Engineered Asynchronous Architecture (Orchestrator v6)

The corrected `RobustCloudOrchestratorV6` completely eliminates the dependency on continuous, synchronous SSH connectivity:

```
[Local Host Orchestrator v6]                    [Remote GPU Pod]
           |                                           |
           |---- (1) Launch Detached (nohup) --------->| Starts background Python process
           |                                           | Writes PID to runner.pid
           |<--- (2) Return PID (e.g. 782) ------------| Writes logs to runner.log
           |                                           |
     [Poll Loop]                                       |
           |---- (3) Check PID (kill -0) ------------->| Running (Code 0)
           |---- (4) Read Heartbeat (cat json) ------->| Completed: 15 / 400
           |---- (5) SFTP Pull Incremental File ------>| Syncs primary_7b_results.jsonl
           |         (Saved locally to disk)           | (Appends to local file)
           |                                           |
  (Network Drop?)                                      |
           |-- X (Transient SSH reset)                 | [GPU Continues Computing!]
           |-- (Retry connect w/ backoff) ------------>| Reconnected!
           |                                           |
           |---- (6) Read Heartbeat ------------------>| Status: "COMPLETED"
           |---- (7) FINAL SFTP Pull Verified -------->| All 400 records local
           |                                           |
           |---- (8) Provider Pod Termination -------->| Safely Destroy Pod
```

### Key Engineering Features:
1. **Detached Process Execution**: The experiment runs detached under `nohup ... > runner.log 2>&1 & echo $! > runner.pid`.
2. **Periodic Incremental SFTP Synchronization**: Every polling cycle (e.g., every 15–30 seconds), the orchestrator checks `heartbeat.json` and pulls the latest `results.jsonl` using atomic temporary file staging (`tmp_dest` $\to$ `local_dest`). If the connection drops or the pod crashes, all rollouts completed prior to the interruption are already safe on the researcher's local machine.
3. **Resilient SSH Reconnection**: If SSH connectivity drops, the orchestrator reconnects with exponential backoff without aborting the background job.
4. **Guaranteed Pre-Termination Pull**: On any interruption or error, the orchestrator triggers an immediate final SFTP pull *before* issuing any termination command.

---

## 3. CPU-Only Test Suite Verification

The new architecture was verified with 4 passing unit and integration tests (`tests/test_robust_orchestrator.py`):
1. `test_launch_detached_experiment_format`: Confirms detached command formatting, nohup execution, and PID extraction.
2. `test_ssh_transient_failure_recovery`: Confirms automatic retry and reconnection on simulated socket resets.
3. `test_atomic_incremental_sync`: Confirms atomic local file writing during active remote streaming.
4. `test_monitoring_loop_exits_on_interruption_and_syncs`: Confirms fail-safe artifact pull on SIGINT / interruption.
