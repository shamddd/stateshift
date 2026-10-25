# Research Mission 15.2: Defect Reproduction & Root Cause Analysis

**Principal Investigator**: Sham Satish Thakare  
**Repository**: `github.com/shamddd/stateshift`  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_2/01_DEFECT_REPRODUCTION_AND_ROOT_CAUSE.md`  
**Base Commit**: `75a5cda9e9633b6494459af039c810ea55f4c112`  
**Date**: October 25, 2026  
**Auditor**: Independent Cloud Reliability & Security Auditor  

---

## 1. Executive Summary

An independent code audit of StateShift Mission 15.1 (`75a5cda`) identified four remaining defects in cloud safety, financial controls, provider state verification, and dataset provenance.

All four defects have been reproduced programmatically with deterministic unit tests.

### Summary of Reproduced Defects:
1. **Defect 1 (FINANCIAL SAFETY HAZARD)**: In `RobustCostControllerV7`, a single boolean flag `self.emergency_shutdown_triggered = True` was flipped before calling the termination callback. An exception or failed attempt permanently suppressed future retries, leaving the cloud pod running indefinitely.
2. **Defect 2 (SHUTDOWN DELAY VULNERABILITY)**: In `RobustCloudOrchestratorV8.terminate_emergency()`, intermediate SFTP synchronization was attempted synchronously *before* dispatching the provider termination API call. An indefinite SSH/SFTP hang blocked financial termination.
3. **Defect 3 (FALSE TERMINATION CONFIRMATION)**: In `ProductionRunPodTransport.verify_pod_terminated()`, `STOPPED` was treated as equivalent to `TERMINATED`. On RunPod, stopped pods continue to incur storage fees and can be resumed; they are not destroyed.
4. **Defect 4 (SCIENTIFIC PROVENANCE GAP)**: `IndependentDatasetVerifier` checked only basic keys and did not enforce model revision, preregistered decoding configuration, explicit generation completion states (`COMPLETED`, `TRUNCATED`, `FAILED`), or structured provenance metadata.

---

## 2. Reproduction of Defect 1: Permanent Suppression of Financial Shutdown

### Affected Function:
[`research_mission_15_1/runner/robust_cost_controller_v7.py:102-126`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_15_1/runner/robust_cost_controller_v7.py#L102-L126):
```python
action_taken = "NONE"
if should_emergency_terminate and not self.emergency_shutdown_triggered:
    self.emergency_shutdown_triggered = True
    ...
    if self.emergency_shutdown_callback:
        self.emergency_shutdown_callback(emergency_reason)
        action_taken = "EMERGENCY_SHUTDOWN_CALLED"
```

### Failure Condition & Mechanism:
When `effective_spend >= emergency_shutdown_usd`, `self.emergency_shutdown_triggered` is set to `True`. If `self.emergency_shutdown_callback` encounters a transient network timeout, HTTP error, or local exception, the method exits. On subsequent ticks of the monitoring loop, `not self.emergency_shutdown_triggered` evaluates to `False`. The cost controller takes no action (`action_taken == "NONE"`), and no further termination attempt is ever made.

### Reproduction Evidence:
```
Defect 1 Reproduction: called_count=1, second tick action_taken=NONE, emergency_shutdown_triggered=True
Assertion: Shutdown permanently suppressed on second tick!
```

---

## 3. Reproduction of Defect 2: Emergency Termination Delayed by SFTP Sync

### Affected Function:
[`research_mission_15_1/runner/robust_cloud_orchestrator_v8.py:248-261`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_15_1/runner/robust_cloud_orchestrator_v8.py#L248-L261):
```python
def terminate_emergency(self, reason: str, emergency_sync: bool = True, remote_output_file: Optional[str] = None) -> bool:
    ...
    self.transition_to(OrchestratorStateV8.EMERGENCY_SHUTDOWN_REQUESTED)
    
    # Bounded final sync attempt
    if emergency_sync and remote_output_file:
        try:
            synced = self.sync_intermediate_snapshot(remote_output_file)
            ...
    
    # Immediate provider-level termination
    term_ok = False
    if self.transport ...
```

### Failure Condition & Mechanism:
The execution order executed `sync_intermediate_snapshot` *before* `terminate_pod`. If the remote SSH daemon or SFTP connection hangs or deadlocks, `sync_intermediate_snapshot` blocks execution, preventing the provider termination request from reaching RunPod.

### Reproduction Evidence:
```
Defect 2 Reproduction: call_order=['sftp_fetch', 'provider_terminate']
Assertion: SFTP was executed BEFORE provider termination!
```

---

## 4. Reproduction of Defect 3: Acceptance of `STOPPED` as Terminated

### Affected Function:
[`research_mission_15_1/transport/runpod_transport.py:168`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_15_1/transport/runpod_transport.py#L168):
```python
if not meta.get("exists") or meta.get("status") in ["TERMINATED", "TERMINATED_OR_NOT_FOUND", "STOPPED"]:
    return True
```

### Failure Condition & Mechanism:
RunPod pod lifecycles distinguish `STOPPED` (instance paused, disk storage actively billed) from `TERMINATED` / `DELETED` (pod removed from infrastructure, billing zeroed). Treating `STOPPED` as verified termination allows pods with billable storage to persist unnoticed.

### Reproduction Evidence:
```
Defect 3 Reproduction: verify_pod_terminated with STOPPED returned: True
Assertion: STOPPED accepted as terminated!
```

---

## 5. Reproduction of Defect 4: Missing Provenance & Decoding Controls in Dataset Verifier

### Affected Class:
[`research_mission_15_1/evaluation/dataset_verifier.py:25-28`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_15_1/evaluation/dataset_verifier.py#L25-L28):
```python
REQUIRED_KEYS = {
    "request_id", "problem_id", "condition_code",
    "prompt_sha256", "model_output", "gold_answer"
}
```

### Failure Condition & Mechanism:
The verifier only checked 6 keys. It failed to validate:
- Explicit model revision (`model_revision`).
- Pre-registered decoding parameters (`temperature`, `max_tokens`, `seed`).
- Completion state (`completion_status` in `['COMPLETED', 'TRUNCATED', 'FAILED', 'CANCELLED', 'TIMEOUT']`). A truncated output was treated as a valid completion.
- Structured provenance (`source_type = 'REAL_MODEL_INFERENCE'`).

### Reproduction Evidence:
```
Defect 4 Reproduction: verifier.REQUIRED_KEYS={'condition_code', 'prompt_sha256', 'model_output', 'problem_id', 'request_id', 'gold_answer'}
Assertion: temperature, source_type, completion_status missing from schema!
```

---

## 6. Corrective Engineering Plan for Mission 15.2

1. **Phase 2**: Implement durable, retryable shutdown lifecycle in `RobustCostControllerV8` (`NOT_REQUESTED`, `REQUESTED`, `DISPATCHING`, `DISPATCHED`, `PROVIDER_CONFIRMED`, `RETRY_PENDING`, `TERMINATION_UNCONFIRMED`).
2. **Phase 3**: Reorder emergency shutdown in `RobustCloudOrchestratorV9` so provider termination is dispatched **immediately first**. Local data preservation occurs only afterward.
3. **Phase 4**: Harden `ProductionRunPodTransportV2` to authoritatively distinguish `STOPPED` from `TERMINATED`/`DELETED`.
4. **Phase 5**: Upgrade `IndependentDatasetVerifierV2` to enforce model revision, decoding configuration, generation completion states, and structured provenance.
