# StateShift: Pre-Spend Readiness & Physical Calibration Plan (Gate A)

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Verification Date**: October 25, 2026 (18:35 IST)  
**Execution Phase**: **Gate A — Zero-Spend Live Readiness**  
**Authorized Expenditure Incurred So Far**: **$0.00 USD (Zero Cloud Leakage)**  

---

## 1. Verified Repository State

- **Branch**: `research/mission15-6-final-production-closure`
- **Expected & Confirmed Head Commit**: `069caaaaa6f5bfffec54cdcf2bfed01e7b42adc8` (short: `069caaa`)
- **Working Tree**: Completely clean across `research_mission_15*` and core modules.
- **Canonical Launcher Entry Point**:
  ```bash
  python3 -m research_mission_15_6.runner.stateshift_launch [arguments]
  ```
- **CLI Parameter Audit**: Verified against the live `argparse` definition in `stateshift_launch.py`. Supports:
  - `--mode {preflight,calibration,production,simulation}`
  - `--experiment-id <ID>`
  - `--manifest <PATH>`
  - `--authorization <PATH>`
  - `--trusted-public-key <KEY_OR_PATH>`
  - `--pod-id <POD_ID>`
  - `--ip <IP>`
  - `--port <PORT>`
  - `--ssh-key <PATH>`
  - `--max-cost <USD>`
  - `--max-runtime <MINUTES>`
  - `--gpu-rate <USD_PER_HOUR>`

---

## 2. Scientific Artifact & Manifest Verification

- **Primary 400-Request Manifest**:
  - Path: `research_mission_15_6/manifests/primary_100_manifest.json`
  - SHA-256 Hash: `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`
  - Verified: Exactly matches frozen primary manifest specification.
- **Calibration 10-Request Manifest**:
  - Path: `research_mission_15_6/manifests/calibration_10_manifest.json`
  - File SHA-256 Hash: `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6`
  - Parent Manifest Reference: `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`
  - Selection Hash: `91c57ea9f3e26045abb34a721c43bad38af49f9bb647037941f2c261b61adfec`
- **The Exact Ten Frozen Request IDs**:
  1. `primary_100_req_0001` (Problem: `math500_001`, Condition: `None`)
  2. `primary_100_req_0002` (Problem: `math500_001`, Condition: `None`)
  3. `primary_100_req_0003` (Problem: `math500_001`, Condition: `None`)
  4. `primary_100_req_0004` (Problem: `math500_001`, Condition: `None`)
  5. `primary_100_req_0005` (Problem: `math500_012`, Condition: `None`)
  6. `primary_100_req_0006` (Problem: `math500_012`, Condition: `None`)
  7. `primary_100_req_0007` (Problem: `math500_012`, Condition: `None`)
  8. `primary_100_req_0008` (Problem: `math500_012`, Condition: `None`)
  9. `primary_100_req_0009` (Problem: `math500_023`, Condition: `None`)
  10. `primary_100_req_0010` (Problem: `math500_023`, Condition: `None`)
- **Immutability Assurance**: Prompts, condition assignments, seeds, and metadata are frozen and unmodified.

---

## 3. Live RunPod Account Audit (Read-Only)

Executed via direct authenticated GraphQL queries against `https://api.runpod.io/graphql`:

- **Account User ID**: `user_3I6YRPDHqf2wE2KnD9pT9cq8iFm`
- **Current Live Balance**: **$9.2882 USD** ($9.2882232391)
- **Active Pods Count**: **0** (Zero active running pods)
- **Stopped Pods Count**: **0** (Zero stopped pods)
- **Network Volumes Count**: **0** (Zero persistent volumes)
- **Storage Billing Incurred**: **$0.00**
- **Live GPU Pricing for RTX 4090 (24 GB VRAM)**:
  - Secure Cloud Price: **$0.89/hr**
  - Community Cloud Price: **$0.34/hr**
  - Lowest Uninterruptable Price: **$0.34/hr**
- **SSH Key Registration**: Confirmed. Local `~/.ssh/id_ed25519.pub` perfectly matches the registered public key in the RunPod user account profile.

---

## 4. Affordability & Budget Feasibility Analysis

### Preservation Floor Calculation
$$\text{current\_balance} = \$9.2882\text{ USD}$$
$$\text{preservation\_floor} = \$7.0000\text{ USD}$$
$$\text{available\_above\_floor} = \$9.2882 - \$7.0000 = \mathbf{\$2.2882\text{ USD}}$$

The proposed calibration planned ceiling is **$0.35 USD**, with an autonomous emergency shutdown trigger at **$0.25 USD**.  
$$\$0.3500 \ll \$2.2882\text{ USD (Available Headroom: 6.5x budget)}$$

### Itemized Cost Projections (Conservative Secure Cloud @ $0.89/hr)
Rate: $\frac{\$0.89}{60} \approx \$0.01483/\text{min} \approx \$0.000247/\text{sec}$.

| Lifecycle Phase | Conservative Duration | Estimated Cost (USD) | Cumulative Spend |
|:---|:---:|:---:|:---:|
| 1. Pod Provisioning & Container Startup | 60–90 seconds | $0.022 | $0.022 |
| 2. Dependency Check & SSH Connection | 30 seconds | $0.007 | $0.029 |
| 3. Model Download (14GB weights) | 90–120 seconds | $0.030 | $0.059 |
| 4. Model Loading into VRAM | 20–30 seconds | $0.007 | $0.066 |
| 5. 10 Inference Requests (4,000 tokens) | 40–60 seconds | $0.015 | $0.081 |
| 6. Checkpoint Sync & Local Verification | 10–15 seconds | $0.003 | $0.084 |
| 7. Priority-1 Pod Destruction & Confirm | 15–30 seconds | $0.005 | **$0.089** |

- **Expected Nominal Spend**: **$\approx \$0.089\text{ USD}$**
- **Conservative Upper Bound (10 min runtime)**: **$\approx \$0.148\text{ USD}$**
- **Community Cloud Execution ($0.34/hr)**: **$\approx \$0.034\text{ USD}$**
- **Safety Margin**: Both nominal ($0.089) and upper bound ($0.148) are well below the **$0.250 USD emergency trigger** and the **$0.350 USD ceiling**.
- **Post-Execution Estimated Balance**:
  $$\$9.2882 - \$0.089 \approx \mathbf{\$9.199\text{ USD}} \gg \$7.0000\text{ USD}$$

---

## 5. Model & Hardware Compatibility

- **Model**: `Qwen/Qwen2.5-Math-7B-Instruct`
- **Revision**: `c869d27376a8d6728795551322fe323b6`
- **Hardware**: NVIDIA GeForce RTX 4090 (24 GB VRAM)
- **VRAM Allocation**:
  - Model weights (bfloat16): ~15.22 GB
  - KV Cache & Activation buffer: ~3.50 GB
  - Total VRAM utilized: ~18.72 GB (within 24.0 GB VRAM capacity; 5.28 GB headroom)
- **Decoding Configuration**:
  - `do_sample`: `False` (Greedy decoding)
  - `temperature`: `0.0`
  - `top_p`: `1.0`
  - `seed`: `42`
  - `max_new_tokens`: `768`
- **Inference Engine**: vLLM with `enforce_eager=True`, `gpu_memory_utilization=0.90`.
- **Fallback Policy**: If vLLM experiences environment incompatibilities on the remote container, a Hugging Face Transformers fallback (`AutoModelForCausalLM`, `torch_dtype=torch.bfloat16`, `do_sample=False`) is available, preserving exact mathematical decoding equivalence.

---

## 6. Pre-Spend Prerequisites Summary

- [x] Repository commit verified (`069caaa`).
- [x] Working tree clean.
- [x] Primary manifest verified (`3a8caf3b...`).
- [x] Calibration manifest verified (`f6c2ed07...`).
- [x] 10 request IDs confirmed (`primary_100_req_0001` through `req_0010`).
- [x] RunPod API key loaded and validated.
- [x] Live balance verified ($9.2882 USD).
- [x] Zero existing pods or attached volumes confirmed.
- [x] Local SSH key matches RunPod account key.
- [x] Watchdog startup handshake and non-terminating unconfirmed policy verified in local tests.
- [x] Affordability confirmed ($2.2882 above floor vs $0.35 max budget).

---

## 7. Pre-Spend Decision & Formal Stop

The preparation phase (**Gate A**) is complete. No paid resources have been created. Zero cloud expenditure has been incurred.

In strict compliance with user instructions:
> *"Stop at Gate B and obtain explicit authorization before creating, starting, or modifying a billable cloud resource."*
> *"Never infer spending approval from the existence of this prompt."*

The system is now paused and awaiting human authorization.
