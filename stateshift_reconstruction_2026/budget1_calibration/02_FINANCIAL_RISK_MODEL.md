# StateShift — Financial Risk Model ($1 Budget Calibration)
## Deliverable 02 — Comprehensive Compute Cost & Latency Risk Analysis
**Model Target:** `Qwen/Qwen2.5-Math-7B-Instruct` (SafeTensors, ~15.2 GB total weights)  
**Hardware Profile:** 1x NVIDIA GeForce RTX 4090 (24 GB VRAM) on RunPod Secure Cloud  
**Provider Rate:** $0.8900 USD / hour ($0.014833 USD / minute; $0.0002472 USD / second)  

---

## 1. Deconstructed Runtime & Cost Model

The physical execution of the 10-request calibration decomposes into six distinct phases:

| Phase | Description | Conservative Duration | Expected Cost ($0.89/hr) | Primary Variance Drivers |
|---|---|---|---|---|
| **Phase 1: Pod Provisioning & Container Boot** | RunPod scheduling, Docker image pull (`runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`), SSH daemon initialization. | 2.0 – 4.0 min | $0.0297 – $0.0593 | Provider host allocation queue; container layer caching. |
| **Phase 2: Model Weight Staging (Qwen-7B)** | Downloading ~15.2 GB of SafeTensors weights and tokenizer files from HuggingFace Hub. | 7.0 – 16.0 min | $0.1038 – $0.2373 | Network peering bandwidth between RunPod datacenter and HuggingFace CDN (15 MB/s to 45 MB/s). |
| **Phase 3: Inference Engine Initialization** | Loading model weights into VRAM (bf16), compiling KV-cache, initializing vLLM v0.6.3 / PyTorch CUDA context. | 1.5 – 3.0 min | $0.0222 – $0.0445 | PCIe host-to-device transfer rate; vLLM memory profiling. |
| **Phase 4: Calibration Inference Execution** | Sequential greedy generation of 10 frozen requests (max 768 tokens each, observed speed ~40 tokens/sec). | 1.5 – 3.5 min | $0.0222 – $0.0519 | Reasoning chain length per problem; math derivation complexity. |
| **Phase 5: SFTP Synchronization & Verification** | Pulling `.jsonl` generation records to local machine, verifying JSON integrity, prompt hashes, and request IDs. | 1.0 – 1.5 min | $0.0148 – $0.0222 | SFTP transfer latency; local SHA-256 computation. |
| **Phase 6: Pod Teardown & Destruction Verification** | Dispatching `podTerminate` mutation, polling provider API until pod state reaches `NOT_FOUND` or `TERMINATED`. | 1.0 – 2.5 min | $0.0148 – $0.0371 | RunPod GraphQL API queue latency; host hypervisor cleanup. |
| **TOTALS** | **End-to-End Calibration Session** | **14.0 – 30.5 min** | **$0.2075 – $0.4523** | **Cumulative operational jitter.** |

---

## 2. Failure Analysis of Historical $0.25 Threshold

In StateShift Mission 15.5, an emergency shutdown tripwire of **$0.25 USD** was established.

At $0.89/hr, $0.25 represents exactly:
$$\text{Runtime at \$0.25} = \frac{\$0.25}{\$0.89/\text{hr}} \times 60\text{ min} = \mathbf{16.85\text{ minutes}}$$

### Why $0.25 Was Structurally Flawed:
- If container provisioning (3 min) and model weight staging (14 min) consumed 17 minutes total, the $0.25 tripwire was breached **before a single inference request was ever dispatched**!
- This created an engineering paradox: the safety system correctly killed the pod because spend reached $0.25, but zero scientific work was obtained.
- Raising the planned ceiling to **$1.00 USD** removes this artificial choke point while preserving an absolute spending bound.

---

## 3. Financial Thresholds Under Policy V2 Exception

To ensure both scientific completion and guaranteed preservation of the $0.32 reserve floor, the following parameters are established:

```text
+-------------------------------------------------------------------------------+
| ACCOUNT BALANCE: $1.3174 USD                                                  |
|                                                                               |
| [ 0.00 USD ] -------------------------------------------------> [ 0.70 USD ] |
|   Normal Operation & Model Staging (Expected: $0.21 - $0.45)        ^         |
|                                                                     |         |
|                                                    EMERGENCY TRIPWIRE: $0.70  |
|                                                                               |
| [ 0.70 USD ] -------------------------------------------------> [ 1.00 USD ] |
|   Teardown & Verification Buffer ($0.30 buffer = 20.2 min headroom) ^         |
|                                                                     |         |
|                                                    MAXIMUM CEILING: $1.00     |
|                                                                               |
| [ 1.00 USD ] -------------------------------------------------> [ 1.32 USD ] |
|   Target Reserve Floor ($0.3174 -> $0.3200 USD)                     ^         |
|                                                                     |         |
|                                                    PRESERVATION FLOOR: $0.32  |
+-------------------------------------------------------------------------------+
```

### 3.1 Parameter Justifications:
1. **Planned Spending Ceiling: $1.0000 USD**
   - Corresponds to **67.4 minutes** of continuous RTX 4090 compute.
   - More than double the upper-bound expected runtime (30.5 minutes), absorbing heavy network congestion or slow HuggingFace mirror responses.
2. **Emergency Shutdown Tripwire: $0.7000 USD**
   - Corresponds to **47.2 minutes** of compute.
   - If model download or initialization exceeds 45 minutes, the independent watchdog daemon halts the run and terminates the pod.
3. **Safety Buffer: $0.3000 USD ($1.00 − $0.70)**
   - Corresponds to **20.2 minutes** of billing headroom.
   - Even if RunPod billing updates lag by 2 minutes and API teardown takes 3 minutes, the total charges incurred cannot exceed $0.75 – $0.80, leaving the **$0.32 reserve floor intact**.
4. **Hard Wall-Clock Runtime Deadline: 45.0 Minutes**
   - Local runner monotonic timer triggers emergency termination at $T + 45$ minutes regardless of provider telemetry.
   - At $0.89/hr, 45 minutes costs exactly **$0.6675 USD**.

---

## 4. Residual Financial Risk & Disclosure

> [!WARNING]
> **Residual Risk of Account Balance Loss:**
> While defense-in-depth safety controls (local wall-clock deadline, independent daemon, multi-pass termination) are in place, cloud billing cannot be 100% hard-capped by client-side software.
>
> If RunPod experiences a severe datacenter infrastructure failure where the hypervisor ignores termination mutations and API queries fail, charges could theoretically continue until the remaining account balance ($1.3174) is fully exhausted to $0.00.
>
> **Maximum possible financial loss under any catastrophe:** Exactly **$1.3174 USD**.
>
> Because RunPod prepaid accounts do not allow negative balances without a credit line, no debt or surprise external card charges can occur. The Principal Investigator explicitly accepts the risk of losing the entire $1.3174 balance in exchange for obtaining authentic GPU calibration evidence without depositing additional funds today.
