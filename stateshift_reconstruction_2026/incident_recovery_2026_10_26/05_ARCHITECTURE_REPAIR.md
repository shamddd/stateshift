# StateShift Incident Recovery — Architecture Repair Specification
**Project**: StateShift (NeurIPS 2027 / TMLR)  
**Principal Investigator**: Sham Satish Thakare  
**Incident Date**: October 25–26, 2026  
**Auditor**: Senior Systems Architect & Distributed Reliability Engineer  
**Status**: APPROVED RECOVERY ARCHITECTURE  

---

## 1. Executive Summary

The October 25–26, 2026 incident demonstrated that partial, ad-hoc orchestration scripts cannot safely manage billable cloud accelerators. When pod provisioning was decoupled from the supervisor and placed ahead of it in procedural code, an SSH channel deadlock in the pre-caching phase left an RTX 4090 running completely unsupervised for 8.76 hours, depleting the account from $9.1243 to $1.3261 USD.

This specification details the formal, permanent repair of the StateShift execution architecture. It replaces procedural orchestration with five strictly enforced architectural invariants implemented in code, validated offline, and protected by fail-closed locks.

---

## 2. The Five Mandatory Architectural Invariants

### Invariant 1: The Supervisor-First Principle
```mermaid
flowchart TD
    subgraph Repaired Lifecycle (Supervisor-First)
        S0[Start Launch] --> S1[Phase 0: Generate Signed Authorization & Validate Policy]
        S1 --> S2[Phase 1: Spawn Independent Financial Watchdog in PRE_PROVISION State]
        S2 --> S3{Phase 2: Watchdog Pre-Provision Readiness Handshake Verified?}
        S3 -- NO (Timeout / Exit) --> S4[ABORT: Zero Cloud Spending Incurred]
        S3 -- YES (12-Point Receipt Valid) --> S5[Phase 3: Provision Single Cloud Pod]
        S5 --> S6[Register Pod ID with Watchdog via Atomic IPC]
        S6 --> S7{Watchdog Confirms Pod Monitoring?}
        S7 -- NO --> S8[Emergency Auto-Teardown of Pod & Abort]
        S7 -- YES --> S9[Phase 4: Bounded Staging & Health Audit]
        S9 --> S10[Phase 5: Execute Workload Under Continuous Supervision]
        S10 --> S11[Phase 6: Authoritative Pod Termination & Final Reconciliation]
    end
```

**Rule**: Under no circumstances may a cloud provisioning API request (`runpod.create_pod` or `transport.provision_pod`) be dispatched unless:
1. An independent OS supervisor process (`independent_financial_watchdog.py`) is already alive and running in a detached process group.
2. The supervisor has completed its initial GraphQL account balance query and verified the balance is above the $7.00 preservation floor.
3. The supervisor has written an atomic pre-provision readiness receipt (`watchdog_pre_provision_ready.json`) matching the exact session execution ID.
4. The orchestrator has cryptographically and structurally validated this receipt within a 15.0s monotonic deadline.

If the supervisor fails to write this receipt or exits prematurely, the pipeline aborts immediately. Zero cloud resources are provisioned. Zero spending occurs.

### Invariant 2: Bounded Staging & Channel Monotonic Deadlines
**Rule**: No SSH or transport operation may call `stdout.channel.recv_exit_status()` directly.

All remote command executions must route through `safe_channel_wait(channel, timeout_seconds)`:
```python
def safe_channel_wait(channel, timeout_seconds: float = 30.0) -> int:
  deadline = time.monotonic() + timeout_seconds
  while not channel.exit_status_ready():
    if time.monotonic() > deadline:
      try:
        channel.close()
      except Exception:
        pass
      raise TimeoutError(
          f"SSH command execution exceeded monotonic wall-clock deadline of"
          f" {timeout_seconds:.1f}s"
      )
    time.sleep(0.1)
  return channel.recv_exit_status()
```
If the deadline expires:
1. The channel is immediately closed locally to release socket resources.
2. A `TimeoutError` is raised.
3. The exception handler dispatches an immediate teardown signal to the supervisor.
4. The supervisor terminates the pod via `podTerminate`.

### Invariant 3: Bounded Remote Model Caching
**Rule**: Remote model caching (`AutoModelForCausalLM.from_pretrained`) is treated as an untrusted, network-dependent operation with a hard, non-extendable 180-second ceiling.

Implementation requirements:
- The remote command is executed wrapped with GNU `timeout 180`:
  `timeout 180 python3 /workspace/stateshift/cache_model.py`
- The local transport enforces a matching `timeout=185` via `safe_channel_wait`.
- If the remote download exceeds 180 seconds, the remote process is killed by `SIGKILL` from `timeout`, the channel closes, and local execution catches the exit code or timeout.
- The supervisor monitors the wall-clock staging window. If staging exceeds 300 seconds total, the supervisor issues a provider-side pod termination regardless of controller state.

### Invariant 4: Strict Single-Attempt Invariant (Zero Auto-Retry)
**Rule**: `max_provisioning_attempts = 1`.

Under no circumstances may the orchestrator loop, retry, or spawn replacement pods upon encountering a failure in pre-flight, staging, or execution.
- If attempt 1 fails for any reason (SSH timeout, revision 404, dependency error, network glitch), the system transitions to `STATE_TERMINAL_FAILED`.
- The pod is authoritatively terminated and destruction confirmed.
- The execution session closes, and the persistent execution lock remains engaged.
- A human operator must manually investigate and authorize any subsequent run.

### Invariant 5: Durable Multi-Pass Termination Verification
**Rule**: Termination is never assumed; it must be confirmed by the provider.

- Termination requests are issued via `podTerminate` GraphQL mutation.
- The verifier executes up to 10 verification queries with exponential backoff (2.0s to 10.0s).
- Termination is confirmed **only** if the provider returns `pod == null` or `desiredStatus in ["TERMINATED", "DELETED"]`.
- If the provider returns `STOPPED`, `RUNNING`, or times out, the status is flagged as `TERMINATION_UNCONFIRMED`, an emergency alert receipt is written to `data/primary_run/termination_alerts/`, and the incident is escalated to human operators.

---

## 3. Structural Component Allocation

| Component | File Path | Primary Responsibility Under Repaired Architecture |
|-----------|-----------|----------------------------------------------------|
| **Execution Lock** | `research_mission_15_6/auth/execution_lock.py` | Fail-closed gate rejecting cloud execution if lock active or spend revoked |
| **Supervisor-First Provisioner** | `research_mission_15_6/deployment/supervisor_first_provisioner.py` | Spawns watchdog before pod creation; coordinates registration & bounded staging |
| **Transport Adapter** | `research_mission_15_6/transport/runpod_transport_v2.py` | Enforces `safe_channel_wait` and blocks live GraphQL calls if locked |
| **Financial Watchdog** | `research_mission_15_6/supervision/independent_financial_watchdog.py` | Autonomous background process enforcing $0.25 trigger, $7.00 floor, and controller heartbeats |
| **Launch Orchestrator** | `research_mission_15_6/runner/stateshift_launch.py` | Canonical CLI entrypoint with single execution path and exit code discipline |
