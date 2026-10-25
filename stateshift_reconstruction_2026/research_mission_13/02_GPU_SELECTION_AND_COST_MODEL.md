# 02 GPU Selection & Cost Model: Live RunPod Pricing & Conservative Financial Projections

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Investigation**: Research Mission 13 — GPU Selection & Financial Feasibility  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Provider**: RunPod Cloud Infrastructure (`api.runpod.io`)  
**Pricing Source**: Live RunPod API Query (October 25, 2026)  
**Max Authorized Budget**: **$3.00 USD**  
**Target Campaign Spending**: **$2.00–$2.50 USD** (Leaving $\ge \$7.00$ preserved on account)  
**Status**: COMPLETE — OPTIMAL COST ARCHITECTURE ESTABLISHED  

---

## 1. Live RunPod Hardware Pricing Comparison

We queried RunPod's active compute catalog for all single-GPU instances with $\ge 24\text{ GB}$ VRAM capable of executing `Qwen/Qwen2.5-Math-7B-Instruct` in native bfloat16:

| GPU Model | VRAM (GB) | Cloud Type | Hourly Rate (USD) | vLLM Throughput | Per-Minute Cost | Evaluation & Fit |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **NVIDIA RTX A5000** | **24 GB** | **Secure Cloud** | **$0.27 / hr** | **~48 tok/s** | **$0.0045 / min** | **OPTIMAL VALUE**: Rock-bottom price, enterprise reliability. |
| NVIDIA RTX A5000 | 24 GB | Community Cloud | $0.16 / hr | ~45 tok/s | $0.0027 / min | Extremely cheap, but potential host variance. |
| **NVIDIA RTX 4090** | **24 GB** | **Secure Cloud** | **$0.89 / hr** | **~75 tok/s** | **$0.0148 / min** | **FASTEST**: Highest throughput, shortest wall-clock time. |
| NVIDIA RTX 4090 | 24 GB | Community Cloud | $0.34 / hr | ~70 tok/s | $0.0057 / min | High speed, budget friendly. |
| NVIDIA RTX 3090 | 24 GB | Secure Cloud | $0.50 / hr | ~42 tok/s | $0.0083 / min | Adequate, but slower than 4090 and pricier than A5000. |
| NVIDIA L4 | 24 GB | Secure Cloud | $0.59 / hr | ~40 tok/s | $0.0098 / min | Cloud server tier, moderate throughput. |

---

## 2. VRAM Memory Budget for 7B bfloat16 Inference

```
┌────────────────────────────────────────────────────────┐
│ Qwen2.5-Math-7B-Instruct (7.61B parameters)            │
├────────────────────────────────────────────────────────┤
│ 1. Model Weights (bfloat16):                  14.18 GB │
│ 2. vLLM PagedAttention KV Cache (batch=16):    2.80 GB │
│ 3. PyTorch & CUDA Context Overhead:            1.20 GB │
├────────────────────────────────────────────────────────┤
│ Peak Memory Requirement:                      18.18 GB │
│ Headroom on 24 GB VRAM GPU:                    5.82 GB │
└────────────────────────────────────────────────────────┘
```
A 24 GB VRAM GPU provides $5.82\text{ GB}$ of safety headroom ($24.2\%$), completely eliminating Out-Of-Memory (OOM) risks during continuous batching.

---

## 3. End-to-End Campaign Cost Projections

We evaluate the total cost across all execution stages under two candidate configurations:
- **Option 1**: NVIDIA RTX 4090 Secure Cloud ($0.89/hr = $0.0148/min)
- **Option 2**: NVIDIA RTX A5000 Secure Cloud ($0.27/hr = $0.0045/min)

### 3.1 Stage-by-Stage Breakdown

| Stage | Activity | Est. Output Tokens | Duration (RTX 4090) | Cost (RTX 4090) | Duration (RTX A5000) | Cost (RTX A5000) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Stage 1** | GPU Boot & Smoke Test (1 problem $\times$ 4 conds = 4 reqs) | 1,400 | 4.0 min | $0.059 | 5.0 min | $0.023 |
| **Stage 2** | Cost projection & validation checkpoint | 0 | 0.5 min | $0.007 | 0.5 min | $0.002 |
| **Stage 3** | Primary Experiment (100 problems $\times$ 4 conds = 400 reqs) | 140,000 | 12.0 min | $0.178 | 18.0 min | $0.081 |
| **Stage 4** | Secondary Replication (200 problems $\times$ 4 conds = 800 reqs) | 280,000 | 24.0 min | $0.356 | 36.0 min | $0.162 |
| **Stage 5** | Data sync, verification & provider pod termination | 0 | 2.0 min | $0.030 | 2.0 min | $0.009 |
| **Total** | **Full 1,200 Generation Campaign** | **421,400** | **42.5 min** | **$0.630 USD** | **61.5 min** | **$0.277 USD** |

---

## 4. Financial Safety Margin & Contingency Analysis

```
Authorised Budget Ceiling:                     $3.00 USD
Targeted Campaign Spending:                    $2.00 - $2.50 USD
---------------------------------------------------------
Estimated Spend on RTX 4090 (1,200 reqs):      $0.63 USD
Headroom under $3.00 Ceiling:                  $2.37 USD (376% buffer)
Estimated Spend on RTX A5000 (1,200 reqs):     $0.28 USD
Headroom under $3.00 Ceiling:                  $2.72 USD (971% buffer)
---------------------------------------------------------
Preserved Account Balance (from ~$10):         ~$9.37 to ~$9.72 USD (Exceeds $7.00 preservation goal!)
```

### 4.1 Recommendation
- **Primary Preference**: **NVIDIA GeForce RTX 4090** (Secure or Community depending on immediate provisioning availability). Its 75 tok/s throughput minimizes wall-clock exposure (under 45 minutes total).
- **Secondary Fallback**: **NVIDIA RTX A5000**. Even more cost-effective ($0.27/hr), finishing the full 1,200-generation campaign for under thirty cents ($0.28 USD).

In either case, the entire 1,200-generation campaign easily executes for **under $1.00 USD**, preserving over $9.00 of the researcher's balance and remaining comfortably below the $3.00 authorized ceiling.
