# 11 Minimum-Cost 7B Pilot Plan: Cloud GPU Hardware Selection & Execution Architecture

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Investigation**: Research Mission 12 — Phase XI Cloud Pilot Planning  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Target Model**: `Qwen/Qwen2.5-Math-7B-Instruct` (Revision: `main`, bfloat16)  
**Inference Engine**: `vLLM` with PagedAttention & Continuous Batching  
**Comparison Ledger**: [`11_GPU_PRICE_AND_RUNTIME_COMPARISON.csv`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/11_GPU_PRICE_AND_RUNTIME_COMPARISON.csv)  
**Date**: October 2026  
**Status**: COMPLETE — OPTIMAL CONFIGURATION IDENTIFIED ($0.081 PILOT ESTIMATE)  

---

## 1. Cloud Pilot Scope and Objective

The objective of the **Stage B1 Cloud Pilot** is to determine whether scaling model capacity from 1.5B (`Qwen2.5-Math-1.5B-Instruct-4bit`) to 7B (`Qwen2.5-Math-7B-Instruct` unquantized bfloat16) alters reasoning recovery dynamics across the 10 canonical error operators under Evaluator v4.

To minimize monetary expenditure and eliminate financial risk:
- **Sample Size**: 10 Problems $\times$ 4 Conditions = **40 Inference Requests**.
- **Model Size**: 7.61 billion parameters.
- **Precision**: `bfloat16` (native weights, no quantization artifacts).
- **Hard Cost Ceiling**: **$3.00 USD** (Monitored externally).
- **Hard Wall-Clock Ceiling**: **30.0 minutes** (Auto-termination watchdog).

---

## 2. VRAM Memory Budget for 7B Inference

A 7B parameter model in 16-bit precision requires:
$$\text{Model Weights} = 7.61 \times 10^9 \text{ parameters} \times 2 \text{ bytes} \approx 14.18 \text{ GB}$$
With vLLM's PagedAttention KV cache:
- Context length: $768\text{ tokens}$ prompt + $768\text{ tokens}$ generation = $1536\text{ max tokens}$.
- KV cache reservation for batch size 16: $\approx 2.5\text{ to }3.5\text{ GB}$.
- CUDA context and PyTorch overhead: $\approx 1.2\text{ GB}$.
- **Total Peak VRAM Required**: **$\approx 18.5\text{ to }19.0\text{ GB}$**.

Therefore, a **24 GB VRAM GPU** provides comfortable headroom ($\approx 5\text{ GB}$ reserve) to prevent Out-Of-Memory (OOM) faults without requiring expensive 48 GB (L40S) or 80 GB (A100/H100) enterprise accelerators.

---

## 3. GPU Hardware & Pricing Comparison

| Accelerator | VRAM | Cloud Provider Tier | Hourly Rate | Throughput (vLLM) | Pilot Runtime (40 reqs) | Est. Pilot Cost | Full Study Cost (400 reqs) | Recommendation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **NVIDIA RTX 4090** | **24 GB** | **Secure Cloud** | **$0.74/hr** | **75.0 tok/s** | **6.6 min** | **$0.081** | **$0.48** | **RECOMMENDED** |
| NVIDIA RTX A5000 | 24 GB | Secure Cloud | $0.49/hr | 45.0 tok/s | 8.9 min | $0.073 | $0.51 | Alternative |
| NVIDIA RTX 3090 | 24 GB | Community Cloud | $0.29/hr | 42.0 tok/s | 10.3 min | $0.050 | $0.33 | High network variance |
| NVIDIA L40S | 48 GB | Secure Cloud | $1.09/hr | 85.0 tok/s | 6.1 min | $0.111 | $0.63 | Unnecessary VRAM |
| NVIDIA A100-SXM4 | 80 GB | Secure Cloud | $1.89/hr | 110.0 tok/s | 5.4 min | $0.170 | $0.86 | Cost-inefficient |
| NVIDIA H100-SXM5 | 80 GB | Secure Cloud | $3.49/hr | 160.0 tok/s | 4.7 min | $0.273 | $1.15 | Prohibitive hourly rate |

---

## 4. Primary Recommendation: Secure Cloud RTX 4090

We recommend the **NVIDIA RTX 4090 (24 GB) on RunPod Secure Cloud**:
1. **Exceptional Generation Speed**: With Ada Lovelace architecture and 4th-gen Tensor Cores, the RTX 4090 achieves $>75\text{ tokens/second}$ in vLLM for 7B models.
2. **Minimal Wall-Clock Duration**: The entire 40-request pilot finishes in **$6.6\text{ minutes}$** total (including $3.0\text{ min}$ container and checkpoint setup).
3. **Negligible Spend**: The estimated compute cost for the 40-request pilot is **$0.081 USD** (less than $0.10).
4. **Enormous Safety Margin**: Against our hard ceiling of $3.00 USD, the pilot consumes only $2.7\%$ of the authorized safety cap, providing a $>35\times$ safety margin.
5. **Full Replication Feasibility**: Even scaling to the complete 400-request benchmark ($N=100$ problems $\times$ 4 conditions) costs only **$0.48 USD**, completing in under 40 minutes.

---

## 5. Execution Protocol

```
1. Client boots local daemon: runpod/pod_lifecycle_monitor.py
2. Researcher reviews Authorization Checklist (Phase XII)
3. Upon receiving explicit written token: "AUTHORIZE RUNPOD EXECUTION"
4. Host issues pod creation mutation with container image shamddd/stateshift:mission12
5. Host streams heartbeat.json telemetry every 15 seconds
6. Runner executes 40 requests, scores with Evaluator v4, outputs results.jsonl
7. Daemon detects COMPLETED heartbeat, immediately sends podTerminate mutation
8. Pod is destroyed, billing stops, results synced to local data/ directory
```
