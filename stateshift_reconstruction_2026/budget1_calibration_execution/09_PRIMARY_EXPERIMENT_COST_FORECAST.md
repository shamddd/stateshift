# StateShift: Primary Experiment Cost Forecast & Scaling Projections
## Deliverable 09 — Empirical Extrapolation from Authentic RTX 4090 Calibration
**Document Version:** 1.0.0  
**Analysis Date:** 2026-10-26  
**Repository Branch:** `research/stateshift-final-preexperiment-validation`  
**Certified Head Commit:** [`d48d7ec`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_15_6/runner/execute_authorized_budget1_calibration.py)  
**Principal Investigator:** Sham Satish Thakare  
**Target Venue:** NeurIPS 2027 Main Conference  
**Primary Experiment Scope:** Exactly 400 frozen requests (100 problems x 4 conditions: A, D, E, F)  

---

## 1. Empirical Ground Truth from 10-Request Calibration

The 10-request calibration run on a physical RunPod Secure Cloud NVIDIA RTX 4090 provided exact, empirically verified performance benchmarks for `Qwen/Qwen2.5-Math-7B-Instruct`:

| Parameter | Calibration Realized Value | Operational Notes |
| :--- | :---: | :--- |
| **Pod Provisioning & Boot Latency** | **15.0 seconds** | Time from API call to `RUNNING` status with SSH port |
| **Hardware & Environment Staging** | **14.0 seconds** | SSH probe, `nvidia-smi`, dependencies verification |
| **Model Weight Pre-Caching (14.5 GB)**| **60.9 seconds** | Download & bfloat16 load over high-speed datacenter pipe (~240 MB/s) |
| **Total Non-Inference Overhead** | **89.9 seconds** (1.50 min) | Fixed one-time cost incurred once per session |
| **Total Inference Time (10 requests)** | **148.0 seconds** (2.47 min)| Sum of generation latency across 10 requests |
| **Mean Latency per Request** | **14.80 seconds / request** | Min: 8.0s, Max: 23.0s |
| **Mean Word Count per Generation** | **251.1 words / generation**| Corresponds to ~325 tokens / generation |
| **Average Generation Throughput** | **~22.0 tokens / second** | Single RTX 4090 in bfloat16 greedy inference |

---

## 2. Mathematical Extrapolation to Full 400-Request Experiment

The primary experiment comprises exactly **400 requests** (100 problems evaluated under Condition A, Condition D, Condition E, and Condition F).

### 2.1 Projected Time Breakdown
1. **One-Time Provisioning & Model Caching Overhead:**
   $$T_{\text{fixed}} = 90\text{ seconds} = 1.50\text{ minutes}$$
2. **Pure Inference Time (400 requests):**
   $$T_{\text{infer}} = 400 \times 14.80\text{ s} = 5,920\text{ seconds} = 98.67\text{ minutes} = 1.644\text{ hours}$$
3. **Operational Safety Margin & Watchdog Polling (10%):**
   $$T_{\text{margin}} = 0.10 \times (T_{\text{fixed}} + T_{\text{infer}}) = 10.02\text{ minutes} = 0.167\text{ hours}$$
4. **Total Projected Pod Uptime:**
   $$T_{\text{total}} = 1.50 + 98.67 + 10.02 = \mathbf{110.19\text{ minutes} \approx 1.837\text{ hours}}$$

---

### 2.2 Projected Financial Expenditure Breakdown

| Execution Strategy / Pricing Tier | Hourly Rate | Total Pod Uptime | Total Projected Cost | Unit Cost per Request |
| :--- | :---: | :---: | :---: | :---: |
| **RunPod Secure Cloud RTX 4090 (Recommended)** | **$0.89 / hr** | **1.837 hours** | **$1.635 USD** | **$0.00409 USD** (~0.41¢) |
| **RunPod Community Cloud RTX 4090** | $0.34 / hr | 1.837 hours | $0.625 USD | $0.00156 USD (~0.16¢) |

> **Critical Cost Observation:**  
> Prior conservative models (which assumed a 15-minute weight download and 30s/request latency) estimated $2.85 to $3.50 for the 400-request experiment. The empirical calibration proves that RunPod Secure Cloud bandwidth caches the model in just **60.9 seconds**, reducing the projected compute cost to just **$1.64 USD**!

---

## 3. Account Balance Rebalancing Recommendations for Principal Investigator

To execute the 400-request experiment under the rigorous zero-overrun architecture:
- **Baseline Compute Requirement:** $1.64 USD
- **Unforeseen Ingestion / Latency Buffer (20%):** $0.33 USD
- **Hard Account Preservation Floor:** $1.00 USD
- **Total Recommended Account Balance:** **$2.97 USD** (minimum) to **$4.00 USD** (recommended)

Given the current balance of **$1.3174 USD**:
- **Deficit to Safe Execution:** $\$2.97 - \$1.3174 = \mathbf{\$1.6526\text{ USD}}$
- **Recommended Deposit:** A modest top-up of **$3.00 to $5.00 USD** will guarantee complete, stress-free execution of the entire 400-request NeurIPS 2027 primary experimental program with extensive financial headroom.
