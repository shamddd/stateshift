# Phase G: GPU Cost & Financial Safety Analysis

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22 — Confirmatory Trial Preflight  
**Date & Timestamp**: 2026-10-27T02:34:00+05:30  
**Target Venue**: NeurIPS 2027 Main Track  

---

## 1. Executive Summary

Following the October 25 incident and the rigorous financial controls established in Missions 15 through 21, all cloud GPU activities operate under strict fail-closed accounting. For Mission 22, authorized cloud expenditure is **$0.00 USD**.

This analysis provides the definitive cost and runtime engineering projections for a future, separately authorized GPU execution of the confirmatory trial. We model two execution options: (1) Primary Contrast Only ($462$ requests), and (2) Full Confirmatory Battery ($924$ requests). Under RunPod Secure Cloud RTX 4090 pricing, both options require less than **$0.55 USD** in actual cloud compute, comfortably within the verified balance of **$10.1065 USD** with a $>18\times$ financial reserve margin.

---

## 2. Baseline Empirical Benchmarks (Mission 17 Audit)

The Study 2 pilot ($400$ requests on `Qwen/Qwen2.5-Math-7B-Instruct` in `bfloat16`) provides empirical ground truth:
- **Cloud Provider**: RunPod Secure Cloud (US/EU Data Center)
- **Hardware Instance**: 1x NVIDIA GeForce RTX 4090 (24GB VRAM, 16 vCPUs, 62GB System RAM)
- **Hourly Base Rate**: $\$0.740 / \text{hour}$ (Compute) + $\$0.050 / \text{hour}$ (Container Volume) = $\$0.790 / \text{hour}$ ($\$0.01317 / \text{minute}$)
- **Container Setup & Weight Cache Load**: $7.5$ minutes
- **400-Request Inference Time**: $12.5$ minutes ($1.875$ seconds / request)
- **Teardown & Verification**: $2.0$ minutes
- **Total Pod Lifetime**: $22.0$ minutes
- **Actual Billed Cost**: **$0.34 USD**

---

## 3. Confirmatory Execution Cost Projections

### 3.1 Option 1: Primary Contrast Only (Conditions D & F)
- **Problem Count**: $N = 231$ problems
- **Evaluated Conditions**: Condition D (Forced Restart) + Condition F (State-Preserving Recovery)
- **Total Requests**: $231 \times 2 = 462$ requests
- **Runtime Breakdown**:
  - Container Initialization & Hugging Face Cache: $8.0$ minutes
  - 462 Neural Generations ($1.875$s / req): $14.4$ minutes
  - Result Hashing & Checkpoint Upload: $2.0$ minutes
  - Total Elapsed Time: $24.4$ minutes ($0.407$ hours)
- **Expected Cloud Cost**: $0.407 \text{ hr} \times \$0.790/\text{hr} = \mathbf{\$0.322\text{ USD}}$
- **Recommended Hard Spending Cap**: **$1.00 USD** ($3.1\times$ buffer)

### 3.2 Option 2: Full 4-Condition Confirmatory Battery (Conditions A, D, E, F)
- **Problem Count**: $N = 231$ problems
- **Evaluated Conditions**: Conditions A, D, E, F
- **Total Requests**: $231 \times 4 = 924$ requests
- **Runtime Breakdown**:
  - Container Initialization & Hugging Face Cache: $8.0$ minutes
  - 924 Neural Generations ($1.875$s / req): $28.9$ minutes
  - Result Hashing & Checkpoint Upload: $3.0$ minutes
  - Total Elapsed Time: $39.9$ minutes ($0.665$ hours)
- **Expected Cloud Cost**: $0.665 \text{ hr} \times \$0.790/\text{hr} = \mathbf{\$0.525\text{ USD}}$
- **Recommended Hard Spending Cap**: **$1.60 USD** ($3.0\times$ buffer)

---

## 4. RunPod Balance Reconcilation & Reserve Margins

| Metric | Option 1 (462 Requests) | Option 2 (924 Requests) |
| :--- | :--- | :--- |
| **Current RunPod Balance** | **$10.1065 USD** | **$10.1065 USD** |
| **Expected Compute Cost** | $\$0.322 \text{ USD}$ | $\$0.525 \text{ USD}$ |
| **Hard Spending Limit** | $\$1.000 \text{ USD}$ | $\$1.600 \text{ USD}$ |
| **Projected Remaining Balance** | **$9.7845 USD** | **$9.5815 USD** |
| **Financial Reserve Ratio** | **$31.4\times$ coverage** | **$19.2\times$ coverage** |
| **Post-Execution Reserve %** | **$96.8\%$ intact** | **$94.8\%$ intact** |

---

## 5. Fail-Closed Financial Safeguards

To prevent any possibility of runaway spend:
1. **Pre-Spend Authorization Gate**: GPU creation commands abort immediately unless unlocked by an authentic cryptographic PI signature token.
2. **Watchdog Timeout**: The runner script incorporates a non-bypassable 50-minute wall-clock timeout (`timeout 3000`). If the pod remains active past 50 minutes for any reason, the watchdog forcibly calls `runpod.terminate_pod()`.
3. **Cost Accrual Monitor**: After each batch of 20 requests, the runner queries the RunPod billing API. If total accrued session charges exceed the approved cap, execution halts and the pod is immediately terminated.
4. **Local Dry-Run Verification**: All manifest loading, prompt rendering, model tokenization length checks, and evaluation scripts must be verified locally on CPU ($0 spend) before any cloud provisioning.
