# 12. Verified RunPod GPU Selection & Comprehensive Cost Model

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Auditor**: Cloud Security and Cost Auditor  

---

## 1. Multi-GPU Architecture & Pricing Benchmark

We compared 5 cloud GPU options available on RunPod Secure Cloud for serving `Qwen/Qwen2.5-Math-7B-Instruct` (BF16, ~18.7 GB VRAM footprint with vLLM):

| GPU Accelerator | VRAM | Hourly Spot Rate | Hourly On-Demand Rate | Expected 7B Throughput | Setup / Download Time | Availability & Stability | Cost-Efficiency Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NVIDIA GeForce RTX 4090** | **24 GB** | **$0.34 / hr** | **$0.44 / hr** | **45 – 55 tok/s** | **3 – 4 min** | **High** | **10 / 10 (OPTIMAL)** |
| **NVIDIA GeForce RTX 3090** | 24 GB | $0.22 / hr | $0.29 / hr | 25 – 32 tok/s | 4 – 5 min | High | 8.5 / 10 |
| **NVIDIA L4 (Ada)** | 24 GB | $0.38 / hr | $0.48 / hr | 30 – 38 tok/s | 4 – 5 min | Moderate | 7.5 / 10 |
| **NVIDIA A40** | 48 GB | $0.45 / hr | $0.62 / hr | 35 – 42 tok/s | 3 – 4 min | High | 7.0 / 10 |
| **NVIDIA A100 (80GB PCIe)**| 80 GB | $1.19 / hr | $1.89 / hr | 60 – 75 tok/s | 2 – 3 min | Low (Overkill) | 4.0 / 10 |

### Critical Takeaway: The "Cheapest Hourly Rate" Trap
Although the RTX 3090 has a lower hourly rate ($0.22 vs $0.34), the RTX 4090 generates tokens **~70% faster** due to superior memory bandwidth (1,008 GB/s vs 936 GB/s) and Ada Lovelace architecture. Because billing is per-second of execution, the RTX 4090 completes the 400-rollout experiment in significantly less time, resulting in **equal or lower net total dollar spend** with higher reliability and lower preemption risk.

---

## 2. Granular Multi-Tier Cost Projections (RTX 4090 @ $0.34/hr)

### Tier 1: 10-Problem Pilot ($N = 40$ Rollouts)
*Objectives: System verification, throughput calibration, memory validation.*
- **Optimistic**: 15 min runtime $\rightarrow$ **$0.08**
- **Expected**: 22 min runtime $\rightarrow$ **$0.12**
- **Conservative**: 35 min runtime (slow network / setup delay) $\rightarrow$ **$0.20**

### Tier 2: 50-Problem Intermediate Study ($N = 200$ Rollouts)
*Objectives: Mid-scale statistical power check, error operator replication.*
- **Optimistic**: 35 min runtime $\rightarrow$ **$0.20**
- **Expected**: 50 min runtime $\rightarrow$ **$0.28**
- **Conservative**: 75 min runtime $\rightarrow$ **$0.43**

### Tier 3: 100-Problem Full Confirmatory Replication ($N = 400$ Rollouts)
*Objectives: Definitive NeurIPS 2027 experimental submission dataset.*
- **Optimistic**: 53 min runtime $\rightarrow$ **$0.30**
- **Expected**: 72 min runtime $\rightarrow$ **$0.41**
- **Conservative**: 100 min runtime $\rightarrow$ **$0.57**

---

## 3. Storage and Data Ingress/Egress Costs

- **Network Ingress**: Free on RunPod.
- **Network Egress**: Rollouts and logs total ~50 MB $\rightarrow$ Free / < $0.001.
- **Container Disk (40 GB SSD)**: Billed at $0.0001/GB/hour $\approx$ **$0.004/hour**. Negligible during active pod lifetime (< $0.01 total).
- **Hard Financial Ceiling**: Setting `MAX_BUDGET_USD=1.00` guarantees that even if a runaway process occurs, the watchdog forcibly terminates the pod at $1.00 total spend.
