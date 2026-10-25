# StateShift Mission 15.2: Production Call Graph and Safety Audit

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_2/06_PRODUCTION_CALL_GRAPH_AUDIT.md`  

---

## 1. Executive Summary

This audit validates that the production entry point (`robust_cloud_orchestrator_v9.py`) cannot accidentally provision cloud resources, bypass security parameters, or execute paid GPU workloads without explicit, multi-layer authorization.

---

## 2. Production Call Graph

The static and dynamic call graph for production execution proceeds strictly as follows:

```
[CLI Entry Point: robust_cloud_orchestrator_v9.py]
                        │
                        ▼
            parse_production_args()
      - Default mode: DRY_RUN
      - If --mode PRODUCTION specified:
                        │
                        ▼
         _verify_production_prerequisites()
      - Checks --authorization-token (non-empty string required)
      - Checks RUNPOD_API_KEY in os.environ (required)
      - Checks --pod-id (non-empty string required)
      - Raises PermissionError / ValueError if any check fails
                        │
                        ▼
      RobustCloudOrchestratorV9.__init__()
      - Instantiates ProductionRunPodTransportV2
      - Instantiates IndependentDatasetVerifierV2(manifest_path)
      - Instantiates RobustCostControllerV8(state_dir, max_cost_usd)
      - Atomically persists orchestrator_state_<exp_id>.json
                        │
                        ▼
             Active Execution Loop
      - Cost Controller: check_and_enforce_budget() [Sub-second tick]
      - Intermediate snapshot sync: sync_intermediate_snapshot()
                        │
       ┌────────────────┴────────────────┐
       │                                 │
[Budget Breach / Error]        [Dataset Complete (400/400)]
       │                                 │
       ▼                                 ▼
terminate_emergency()              terminate_normal()
 1. Provider terminate_pod()        1. Verifier audits physical disk
 2. Provider verify_pod()           2. Provider terminate_pod()
 3. Best-effort SFTP sync           3. Provider verify_pod()
 4. Write termination receipt       4. Write integrity receipt
```

---

## 3. Production Prerequisites & Failure Defenses

| Prerequisite | Enforcing Code Location | Failure Behavior | Defense Against |
|:---|:---|:---|:---|
| **Default Mode** | `parse_production_args()` | Default is `DRY_RUN` | Accidental production runs when flags omitted |
| **Authorization Token** | `_verify_production_prerequisites()` | `PermissionError` | Unauthorized CLI script invocation |
| **API Key Presence** | `_verify_production_prerequisites()` | `ValueError` | Unauthenticated provider requests |
| **Explicit Pod ID** | `_verify_production_prerequisites()` | `ValueError` | Blind launches or orphaned resources |
| **Manifest Checksum** | `IndependentDatasetVerifierV2.__init__()` | `FileNotFoundError` / `JSONDecodeError` | Corrupted experimental manifests |

---

## 4. Architectural Verification

Static analysis and test suite execution confirm:
1. No unauthenticated path exists in `robust_cloud_orchestrator_v9.py` that can communicate with RunPod's GraphQL API.
2. In `DRY_RUN` mode (default), `transport` is either `None` or explicitly mocked; zero network sockets to RunPod are opened.
3. In `PRODUCTION` mode, all three required tokens (`authorization_token`, `RUNPOD_API_KEY`, and `pod_id`) must be present simultaneously, preventing automated accidental executions.
