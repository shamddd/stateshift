# StateShift: Conservative 400-Request Cost Modeling & Funding Requirements
## Deliverable 08 — Parametric Scenario Analysis, Failure-and-Resume Modeling & Budget Bounds
**Document Version:** 1.0.0  
**Audit Date:** 2026-10-26  
**Principal Investigator:** Sham Satish Thakare  
**Target Venue:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Primary Experiment Scope:** Exactly 400 requests (100 problems x 4 conditions: A, D, E, F)  
**Target Hardware:** 1x NVIDIA RTX 4090 (24 GB VRAM) on RunPod Secure Cloud ($0.89 / hour)  
**Current Live Settled Balance:** `$1.2541107823 USD`  

---

## 1. Parametric Cost Scenarios for Full 400-Request Execution

Rather than assuming a static multiplier, three comprehensive operational scenarios plus a failure-recovery scenario are modeled using empirical calibration parameters:

| Cost & Operational Parameter | Scenario A: Optimistic | Scenario B: Expected | Scenario C: Conservative | Scenario D: Crash & Resume |
| :--- | :---: | :---: | :---: | :---: |
| **Model Staging & SSH Latency** | 90 seconds (1.5 min) | 105 seconds (1.75 min)| 180 seconds (3.0 min) | 2x Staging (3.5 min total)|
| **Mean Inference Latency / Req**| 12.0 seconds | 14.5 seconds | 20.0 seconds | 14.5 seconds (split) |
| **Total Inference Time** | 80.0 minutes | 96.67 minutes | 133.33 minutes | 96.67 minutes |
| **Operational & Watchdog Buffer**| 2.0 minutes (2.5%) | 5.0 minutes (5.0%) | 20.0 minutes (15.0%) | 10.0 minutes |
| **Teardown & Verification Lag** | 0.5 minutes (30s) | 0.5 minutes (30s) | 1.0 minute (60s) | 1.0 minute |
| **Total Projected Pod Uptime** | **84.0 minutes (1.40 h)**| **103.9 minutes (1.73 h)**| **157.3 minutes (2.62 h)**| **111.2 minutes (1.85 h)**|
| **Projected Compute Expenditure**| **$1.246 USD** | **$1.540 USD** | **$2.332 USD** | **$1.647 USD** |
| **Effective Cost per Request** | **$0.00312 USD** (~0.31¢)| **$0.00385 USD** (~0.39¢)| **$0.00583 USD** (~0.58¢)| **$0.00412 USD** (~0.41¢)|
| **Emergency Tripwire Setting** | $1.50 USD | $1.90 USD | $2.80 USD | $2.00 USD |
| **Max Wall-Clock Hard Limit** | 120.0 minutes | 150.0 minutes | 210.0 minutes | 180.0 minutes |

---

## 2. In-Depth Failure-and-Restart Recovery Modeling (Scenario D)

Because physical cloud sessions can encounter transient network disconnects or container restarts, the execution architecture incorporates atomic incremental ingestion via [`SafeResumeReconciler`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_15_6/runner/remote_experiment_runner.py).

### Failure Simulation Dynamics:
1. **Mid-Run Interruption:** Session 1 crashes unexpectedly after completing 200 of 400 requests (approx. 50 minutes of elapsed uptime).
   - Accrued compute liability in Session 1: $50.0\text{ min} \times (\$0.89 / 60) = \mathbf{\$0.742\text{ USD}}$.
   - Watchdog / orchestrator initiates immediate emergency teardown of faulty pod.
2. **Atomic Recovery:** `SafeResumeReconciler` parses `data/primary_run/stateshift_primary_400_generations.jsonl`, verifies SHA-256 integrity of the first 200 records, and deduplicates the manifest.
3. **Resumed Execution:** Session 2 provisions a replacement pod, pre-caches model weights (60.9s), and launches inference directly at Request 201:
   - Remaining inference: $200 \times 14.5\text{ s} = 48.33\text{ minutes}$.
   - Staging & teardown: 2.5 minutes.
   - Accrued compute liability in Session 2: $51.0\text{ min} \times (\$0.89 / 60) = \mathbf{\$0.757\text{ USD}}$.
4. **Total Combined Liability:** $\$0.742 + \$0.757 = \mathbf{\$1.499\text{ USD}}$.
   - **Conclusion:** Mid-run failure introduces less than **$0.15 USD** of financial penalty thanks to atomic zero-loss resumption.

---

## 3. Account Balance Rebalancing & Policy Decision Framework

The current settled RunPod balance is **`$1.2541107823 USD`**. Two distinct financial policy pathways exist for Principal Investigator authorization:

```
[Current Settled Balance: $1.2541 USD]
         │
         ├──► Policy Option A: Standard Production Policy (Preservation Floor = $7.00 USD)
         │       • Required Account Balance: $2.34 (Conservative Compute) + $1.00 (Buffer) + $7.00 (Floor) = $10.34 USD
         │       • Required Net Deposit: $10.34 - $1.25 = $9.09 USD (~$10.00 USD Top-up)
         │       • Protection: Maximum enterprise-grade balance preservation.
         │
         └──► Policy Option B: Authorized Budget-Limited Exception (Preservation Floor = $1.00 USD)
                 • Required Account Balance: $2.34 (Conservative Compute) + $1.00 (Buffer) + $1.00 (Floor) = $4.34 USD
                 • Required Net Deposit: $4.34 - $1.25 = $3.09 USD (~$3.50 to $5.00 USD Top-up)
                 • Protection: Bounded exposure capped at $3.50 total spend.
```

### Recommendation for Principal Investigator:
* To maintain the historical **$7.00 account preservation floor**, a top-up of **$10.00 USD** is recommended.
* If a temporary budget-limited authorization (similar to Mission 15) is approved with a **$1.00 preservation floor**, a top-up of **$3.50 to $5.00 USD** is fully sufficient to execute all 400 requests with zero risk of mid-run budget depletion.
