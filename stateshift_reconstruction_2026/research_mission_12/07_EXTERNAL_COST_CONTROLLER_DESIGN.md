# 07 External Cost Controller Design: Decoupled Cloud Financial Safety & Pod Lifecycle Management

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Investigation**: Research Mission 12 — Phase VII Cost Safety Architecture  
**Primary Venue Target**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Date**: October 2026  
**Status**: COMPLETE — FULLY IMPLEMENTED AND DECOUPLED FROM GPU RUNTIME  

---

## 1. Threat Model & Design Motivation

In cloud-based AI experimentation, runaway compute spending typically arises from container-level failure modes:
1. **Internal Watchdog Crash**: An internal monitoring thread running inside the container dies or is suppressed when the main worker crashes or deadlocks, leaving the GPU allocated and continuously billed at cloud rates.
2. **Infinite Generation / CUDA Deadlock**: A hung inference engine (e.g., deadlock in token generation or unhandled exception during checkpoint download) prevents the python process from reaching exit hooks.
3. **Container Stop vs. Pod Termination Discrepancy**: On cloud providers like RunPod, executing `docker stop` or exiting the container process merely transitions the pod to `STOPPED` (or `EXITED`). The underlying physical storage and network volume remain attached, and without explicit provider-level pod termination, monthly storage and hourly reservation fees continue to accumulate.

To guarantee **zero financial risk** and strictly adhere to the project's zero-unauthorized-spend mandate, StateShift implements an **External Cost Controller** (`runpod/external_cost_controller.py`) and **Pod Lifecycle Monitor Daemon** (`runpod/pod_lifecycle_monitor.py`).

---

## 2. Decoupled Architecture Overview

```
                      LOCAL WORKSTATION (MacBook / Host)
   ┌────────────────────────────────────────────────────────────────────────┐
   │  pod_lifecycle_monitor.py (Local Daemon)                               │
   │  ┌──────────────────────────────────────────────────────────────────┐  │
   │  │ ExternalRunPodCostController                                     │  │
   │  │  - Hard Budget Ceiling: $3.00 (Pilot) / $15.00 (Replication)     │  │
   │  │  - Hard Wall-Clock Ceiling: 30 min (Pilot) / 120 min (Replication)│  │
   │  │  - Heartbeat Stall Threshold: 300 seconds (5 min)                │  │
   │  │  - Local Audit Ledger: runpod/cost_controller_audit.jsonl        │  │
   │  └──────────────────────────────────────────────────────────────────┘  │
   └────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    │ Authenticated HTTPS (GraphQL)
                                    │ (Query status / Mutation: podTerminate)
                                    ▼
                     RUNPOD CLOUD PROVIDER (api.runpod.io)
   ┌────────────────────────────────────────────────────────────────────────┐
   │ RunPod Control Plane                                                   │
   │  - Maintains billing timer & resource allocations                      │
   │  - Receives `podTerminate(input: {podId})`                             │
   │  - Instantly frees GPU, halts billing clock, deletes container         │
   └────────────────────────────────┬───────────────────────────────────────┘
                                    │ Releases
                                    ▼
                            REMOTE GPU POD
                 ┌───────────────────────────────────┐
                 │ [RTX 4090 / A5000 Pod Container]  │
                 │ cloud_experiment_runner.py        │
                 └───────────────────────────────────┘
```

---

## 3. Core Operational Invariants

1. **Host-Side Execution**:
   - The cost controller runs completely detached from the remote GPU instance. Even if the pod suffers a kernel panic, out-of-memory crash, or networking partition, the external daemon continues tracking elapsed time and issues termination directly to RunPod's control plane.
2. **Multi-Tier Ceilings**:
   - **Pilot Experimentation Tier**:
     - Hard Cost Ceiling: **$3.00 USD**
     - Maximum Wall-Clock Runtime: **30.0 minutes**
     - Target Hardware: Secure Cloud RTX 4090 ($0.74/hr) or RTX A5000 ($0.49/hr)
   - **Full Confirmatory Replication Tier**:
     - Hard Cost Ceiling: **$15.00 USD**
     - Maximum Wall-Clock Runtime: **120.0 minutes**
3. **Heartbeat Stall Detection**:
   - The monitor requires affirmative status updates or health pings from the pod. If communication or poll success ceases for $> 300\text{ seconds}$ (5 minutes) or exceeds 5 consecutive failed polling attempts, the monitor triggers emergency termination.
4. **Append-Only Tamper-Evident Audit Ledger**:
   - Every lifecycle event (`SESSION_START`, `HEARTBEAT`, `POLL_STATUS`, `POD_TERMINATION_EXECUTED`) is recorded to an append-only JSONL file (`runpod/cost_controller_audit.jsonl`) with ISO-8601 UTC timestamps, exact elapsed seconds, and estimated expenditure.

---

## 4. Provider-Level Termination Mutation

To permanently halt billing, the controller sends the official RunPod GraphQL mutation:

```graphql
mutation TerminatePod($input: PodTerminateInput!) {
    podTerminate(input: $input)
}
```

With variables:
```json
{
  "input": {
    "podId": "YOUR_POD_ID"
  }
}
```

Upon receipt, the RunPod infrastructure deletes the pod, detaches all ephemeral volumes, and releases the physical GPU to the public pool, ensuring no trailing storage or reservation charges.

---

## 5. Verification and Integration

The external cost controller code is located at:
- [`runpod/external_cost_controller.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/runpod/external_cost_controller.py)
- [`runpod/pod_lifecycle_monitor.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/runpod/pod_lifecycle_monitor.py)

Unit and contract test coverage is provided in Phase VIII via [`tests/test_runpod_api_contract.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/tests/test_runpod_api_contract.py).
