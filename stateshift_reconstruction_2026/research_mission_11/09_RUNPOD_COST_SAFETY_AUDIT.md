# 09. RunPod Cost Safety & Lifecycle Audit

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Audited Modules**: [`runpod/cost_controller.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_11/runpod/cost_controller.py), [`runpod/termination_watchdog.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_11/runpod/termination_watchdog.py)  
**Software Test Suite**: [`tests/test_cloud_deployment_and_cost.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_11/tests/test_cloud_deployment_and_cost.py) (Tests 09–16)  

---

## 1. Executive Summary & Critical Architectural Distinction

A major finding of the Mission 11 audit is that **operating system shutdown (`shutdown -h now`) inside a RunPod instance does NOT stop billing**.
On cloud platforms:
1. **Stopping a Process**: Frees local GPU memory; billing continues.
2. **Stopping a Container**: Exits container; host instance remains allocated; billing continues.
3. **Stopping a Pod**: Stops compute; pod storage continues to be billed.
4. **Terminating a Pod**: Issues a provider-side API call that completely deallocates the instance and disk, **halting billing permanently**.

---

## 2. Real Cost-Control Implementation

[`runpod/cost_controller.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_11/runpod/cost_controller.py) implements direct GraphQL API integration:

```graphql
mutation TerminatePod($input: PodTerminateInput!) {
    podTerminate(input: $input)
}
```

### Safety Controls Enforced:
- **Authorization Gate**: Exits immediately unless `RUNPOD_AUTHORIZED=TRUE`, `RUNPOD_API_KEY`, and `RUNPOD_POD_ID` are present.
- **Maximum Runtime Watchdog**: Forcibly triggers termination if runtime exceeds `MAX_RUNTIME_MINUTES` (default: 90 min).
- **Maximum Financial Exposure**: Forcibly triggers termination if estimated spend exceeds `MAX_BUDGET_USD` (default: $1.00).
- **Automatic Exit Trap**: Bash `trap cleanup EXIT INT TERM` in `secure_launcher.sh` ensures pod termination is requested regardless of whether the experiment succeeds, fails, or crashes.

---

## 3. Simulated Failure Test Results (Software Test Suite)

All failure handling mechanisms were verified using unit tests in `tests/test_cloud_deployment_and_cost.py`:

| Test ID | Scenario Description | Simulated Condition | Result & Behavior |
| :---: | :--- | :--- | :---: |
| **TEST-09** | Normal Execution | Elapsed runtime < limit, spend < limit | Normal execution permitted |
| **TEST-10** | Experiment Timeout | Runtime crosses 60m threshold | `budget_exceeded = True`, termination triggered |
| **TEST-11** | Cost Cap Breach | Spend exceeds $0.50 | `budget_exceeded = True`, termination triggered |
| **TEST-12** | API Termination Success | HTTP 200 GraphQL response | `podTerminate` confirmed, status `POD_TERMINATED` |
| **TEST-13** | Provider API 500 Error | Server error returned | Automated retry (up to 3 attempts) |
| **TEST-14** | Network Disconnection | Timeout / Connection Refused | Handled gracefully, attempts retry, triggers OS fallback |
| **TEST-15** | Missing Credentials | Empty API key / pod ID | Blocks execution with explicit error message |
| **TEST-16** | Credential Isolation | Git repo code scan | Zero hardcoded keys or tokens detected |

> [!WARNING]
> **Financial Disclosure**: If a catastrophic network partition occurs between the RunPod container and `api.runpod.io`, provider-side termination could fail. In that extreme event, the container falls back to OS shutdown. Principal Investigators should always verify pod status in the RunPod Web Console after any cloud run.
