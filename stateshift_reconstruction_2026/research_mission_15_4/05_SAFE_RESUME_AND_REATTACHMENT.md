# Phase 5: Safe Resume & Process Reattachment Specification

**Module**: `research_mission_15_4/deployment/safe_resume_reconciler.py`  
**Test Suite**: `research_mission_15_4/tests/test_remote_deployment_and_resume.py` (3 Reattachment Tests Passing)  

### Reattachment Decision Logic
- When `--resume` is invoked, the reconciler inspects:
  1. `logs/execution_record.json`: Verifies matching `experiment_id` and `manifest_sha256`. Mismatches halt execution for operator safety (`HALT_FOR_OPERATOR`).
  2. `logs/runner.pid`: Retrieves authentic remote PID.
  3. Process Table: Executes `ps -p <pid>` to verify the process is alive and executing `remote_experiment_runner.py`.
  4. Heartbeat Table: Audits `logs/heartbeat.json` timestamp freshness.
- **Outcomes**:
  - If process is alive: Decides `REATTACH`, tracking existing PID without launching new processes.
  - If process is dead and no other runners exist: Decides `SAFE_RESTART`.
  - If unexpected/untracked runner processes are active: Decides `HALT_FOR_OPERATOR`.
