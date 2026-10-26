# StateShift — Financial Safety Decision & Budget Analysis
## Calibration Readiness Phase 2 & 8
**Analysis Timestamp:** 2026-10-26T06:21:03+05:30  
**Status:** BLOCKED — INSUFFICIENT ACCOUNT BALANCE  
**Principal Investigator:** Sham Satish Thakare  

---

## 1. Parameters and Constraints

| Parameter | Specification | Purpose |
|---|---|---|
| **Account Preservation Floor** | **$7.0000 USD** | Non-negotiable minimum account balance; hard reserve floor. |
| **Proposed Calibration Ceiling** | **$0.6000 USD** | Maximum allowable expenditure for the 10-request calibration run. |
| **Emergency Shutdown Trigger** | **$0.2500 USD** | Early warning and proactive shutdown tripwire. **Not permission to spend to $0.60.** |
| **Verified Hourly Rate (RTX 4090 Secure)** | **$0.8900 USD / hr** | Verified live from RunPod GraphQL API ($0.01483 / min). |
| **Current Live Balance** | **$1.3174 USD** | Verified live from RunPod GraphQL API. |

---

## 2. Emergency Trigger Semantics

> [!IMPORTANT]
> The **$0.25 emergency trigger** is an early termination tripwire, NOT an authorization to spend up to $0.60 without restriction.
>
> If the independent financial watchdog observes incremental spending reaching or exceeding $0.25, it initiates proactive emergency teardown:
> 1. Controller process heartbeat transition to `CONTROLLER_SHUTDOWN_REQUESTED`.
> 2. Direct dispatch of `podTerminate` mutation to RunPod.
> 3. Transition to `TERMINATION_REQUESTED` -> `TERMINATION_UNCONFIRMED` -> `TERMINATION_CONFIRMED`.
>
> The $0.60 planned ceiling accounts for potential delayed telemetry, billing granularity, and bounded shutdown latency.

---

## 3. Account Balance Requirement Calculation

### 3.1 Arithmetic Minimum
$$\text{Minimum Balance} = \text{Preservation Floor } (\$7.00) + \text{Spending Ceiling } (\$0.60) = \mathbf{\$7.6000\text{ USD}}$$

### 3.2 Real-World Latency & Uncertainty Buffer
A balance of exactly $7.60 is an arithmetic minimum, but **does NOT guarantee preservation of the $7.00 floor** in production due to:
1. **Billing Granularity:** Provider billing updates can have 30 to 120-second aggregation latency.
2. **Termination Latency:** Pod destruction confirmation takes approximately 10 to 60 seconds after mutation dispatch.
3. **Storage Allocation Residuals:** Temporary container volume allocation during active runtime.

To maintain an uncompromised defense-in-depth safety margin, the recommended operational account balance before launch is:
$$\text{Recommended Operational Balance} = \mathbf{\$8.0000\text{ to }\$8.5000\text{ USD}}$$

### 3.3 Funding Gap Assessment
- Current Verified Balance: **$1.3174 USD**
- Minimum Required Balance: **$7.6000 USD**
- **Strict Minimum Funding Gap:** **$6.2826 USD**
- **Recommended Safe Funding Gap (to reach $8.00):** **$6.6826 USD**

**Decision:** Automated payment execution is STRICTLY PROHIBITED. The Principal Investigator must manually deposit funds via the RunPod console billing interface.

---

## 4. Technical Feasibility of the $0.60 Calibration Budget

At the verified Secure Cloud RTX 4090 rate of **$0.89 / hr** ($0.01483 / min):

| Phase | Estimated Duration | Estimated Cost ($0.89/hr) |
|---|---|---|
| **Container Initialization & Network Bringup** | 2.0 – 3.0 min | $0.0297 – $0.0445 |
| **Model Weight Staging (Qwen2.5-Math-7B, ~15GB)** | 8.0 – 15.0 min | $0.1187 – $0.2225 |
| **Inference Engine Init (vLLM / Transformers)** | 1.5 – 3.0 min | $0.0222 – $0.0445 |
| **Inference Execution (10 frozen requests @ ~40 tok/s)** | 1.5 – 3.0 min | $0.0222 – $0.0445 |
| **SFTP Dataset Retrieval & Verification** | 1.0 – 1.5 min | $0.0148 – $0.0222 |
| **Pod Teardown & Destruction Handshake** | 1.0 – 2.0 min | $0.0148 – $0.0297 |
| **TOTAL EXPECTED CALIBRATION SESSION** | **15.0 – 27.5 min** | **$0.2224 – $0.4079** |

### Budget Feasibility Verdict
- At $0.89/hr, **$0.60 provides up to 40.4 minutes of wall-clock GPU time**.
- The expected total duration is 15 to 27.5 minutes ($0.22 to $0.41).
- **The $0.60 ceiling is REALISTIC AND DEFICIT-RESILIENT.** Unlike the earlier $0.35 ceiling (which had virtually zero margin for model download variation), $0.60 allows a full 15-minute model download while still leaving sufficient budget for the 10 inference requests and clean termination.

---

## 5. Financial Safety Gate Determination

```
================================================================================
FINANCIAL SAFETY GATE: BLOCKED
================================================================================
Reason: Current balance of $1.3174 USD violates the $7.00 preservation floor.
Required Action: PI must manually deposit at least $6.29 USD (recommended: $7.00 deposit
                to achieve ~$8.32 USD balance) before authorization can be requested.
================================================================================
```
