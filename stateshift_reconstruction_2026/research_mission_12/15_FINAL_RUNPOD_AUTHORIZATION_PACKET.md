# 15 Final RunPod Authorization Packet: Stage B1 7B Cloud Validation Gate

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Investigation**: Research Mission 12 — Cloud Authorization Protocol  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Security Gatekeeper**: [`runpod/authorization_validator.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/runpod/authorization_validator.py)  
**Status**: **BLOCKED — AWAITING EXPLICIT USER AUTHORIZATION TOKEN**  

---

## 1. Cloud Execution Specification

| Parameter | Specification | Verification Source |
| :--- | :--- | :--- |
| **Target Model** | `Qwen/Qwen2.5-Math-7B-Instruct` (Revision: `main`, bfloat16) | HuggingFace Hub revision lock |
| **Inference Framework** | `vLLM` (PagedAttention, Tensor Parallel = 1, Max Tokens = 768) | `runpod/cloud_experiment_runner.py` |
| **Target Hardware** | 1 $\times$ NVIDIA GeForce RTX 4090 (24 GB VRAM, 16 vCPU, 64 GB RAM) | RunPod Secure Cloud |
| **Hourly Compute Rate** | **$0.74 USD / hour** | `11_GPU_PRICE_AND_RUNTIME_COMPARISON.csv` |
| **Experimental Design** | 4-Condition Factorial (A: Zero-Shot, D: Restart, E: Repair, F: State-Preserve) | `manifests/runpod_b1_pilot_manifest.json` |
| **Problem Cohort** | 10 Matched Held-Out Problems spanning OP01 through OP10 | Evaluated locally on M1 in Phase VI |
| **Total Inference Requests** | **40 Requests** (10 Problems $\times$ 4 Conditions) | `runpod_b1_pilot_manifest.json` |
| **Estimated Wall-Clock Time** | **6.6 minutes** (3.0 min container/model boot + 3.6 min inference) | Benchmarked at 75.0 tokens/second |
| **Estimated Compute Spend** | **$0.081 USD** (Under 10 cents) | Hardware Pricing Model |
| **Hard Financial Ceiling** | **$3.00 USD** (External daemon auto-kill) | `runpod/external_cost_controller.py` |
| **Hard Temporal Ceiling** | **30.0 minutes** (External daemon auto-kill) | `runpod/pod_lifecycle_monitor.py` |
| **Heartbeat Timeout** | **300 seconds** (Emergency termination on network partition) | Contract test verified |

---

## 2. Safety and Cost Guarantee

> [!IMPORTANT]
> **Zero Risk of Runaway Billing**:
> 1. The external monitoring daemon runs on your local machine, completely detached from the remote GPU pod.
> 2. If the pod process hangs, crashes, or stalls for $> 300\text{ seconds}$, the local daemon immediately issues a GraphQL `podTerminate` mutation directly to RunPod's control plane.
> 3. Even in the worst-case scenario where the pod runs until the hard time ceiling (30 minutes), the total expenditure cannot exceed **$0.37 USD**, which is well below the hard cap of **$3.00 USD**.

---

## 3. Required User Action to Authorize Cloud Execution

No cloud compute will be launched until you explicitly authorize it. To grant authorization, reply to the agent with the exact case-sensitive token:

```
AUTHORIZE RUNPOD EXECUTION
```

Upon receiving this token, the agent will:
1. Verify the authorization gate via `runpod/authorization_validator.py`.
2. Launch the local lifecycle monitor daemon.
3. Dispatch the container to RunPod Secure Cloud.
4. Stream progress and heartbeat updates in real time.
5. Retrieve raw rollouts, score via Evaluator v4, and automatically terminate the pod.
