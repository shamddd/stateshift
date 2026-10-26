# StateShift Mission 15.2: Financial Reconciliation and Cloud Cost Modeling

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_2/08_FINANCIAL_RECONCILIATION.md`  

---

## 1. Authoritative Financial Baseline

| Parameter | Value (USD) | Status / Enforcement Mechanism |
|:---|:---:|:---|
| **Initial RunPod Account Balance** | \$9.9645 | Historical balance before Mission 13 |
| **Historical Mission 13 Spend** | \$0.6425 | Confirmed historical pod usage (43 min runtime) |
| **Current Live Account Balance** | **\$9.3220** | Verified provider balance |
| **Strict Account Preservation Floor** | **\$7.0000** | Non-negotiable floor reserved for other projects |
| **Max Allowable Lifetime Spend** | **\$3.0000** | Total authorized campaign expenditure limit |
| **Remaining Campaign Budget** | **\$2.3575** | \$3.0000 - \$0.6425 |
| **Experiment Spending Target** | **\$1.50 – \$2.00** | Budget for 400-request replication campaign |
| **Mission 15.2 Incurred Spend** | **\$0.0000** | 100% CPU-only execution; 0 cloud pods provisioned |

---

## 2. Software Watchdog vs. Provider Spend Limits

A critical distinction enforced in Mission 15.2 is the separation of **internal software watchdog monitoring** from **cloud provider-side financial controls**:

```
                               ┌──────────────────────────────────────────────┐
                               │       RUNPOD ACCOUNT BALANCE: $9.3220        │
                               └──────────────────────┬───────────────────────┘
                                                      │
         ┌────────────────────────────────────────────┴────────────────────────────────────────────┐
         ▼                                                                                         ▼
┌──────────────────────────────────────────┐                             ┌──────────────────────────────────────────┐
│        INTERNAL SOFTWARE WATCHDOG        │                             │         EXTERNAL PROVIDER LIMITS         │
│        (RobustCostControllerV8)          │                             │             (RunPod Controls)            │
├──────────────────────────────────────────┤                             ├──────────────────────────────────────────┤
│ • Evaluates every heartbeat tick (2–5s)  │                             │ • Max pod runtime parameter (if supported│
│ • Calculates machine spend from uptime   │                             │ • Account spending alert/hard limit      │
│ • Evaluates delta from initial balance   │                             │ • Prepaid balance exhaustion floor       │
│ • Hard Trigger: Spend >= $1.65 (reserve) │                             │ • Automatic instance stop if prepaid     │
│ • Hard Trigger: Runtime >= 160 minutes   │                             │   balance hits zero                      │
│ • Hard Trigger: Balance <= $7.35 ($7+$0.35)                               │                                          │
│ • Dispatches retryable terminate_pod()   │                             │                                          │
└──────────────────────────────────────────┘                             └──────────────────────────────────────────┘
```

---

## 3. Cost Modeling for 400-Request Replication Campaign

Hardware Target: **NVIDIA RTX 4090 (24 GB VRAM)** on RunPod Secure Cloud  
Billing Rate: **\$0.89 / hour** (\$0.01483 / minute)  
Inference Engine: **vLLM v0.6.3+** with PagedAttention and FP16 weights (`Qwen/Qwen2.5-Math-7B-Instruct`)  
Measured Throughput: **~40–65 tokens/sec** per generation (or ~2.5–5.0 seconds per request at batch size 4–8)  
Fixed Setup Overhead: **~6 minutes** (container boot, weights verification, vLLM engine warm-up) = **\$0.089**

### Parametric Scenarios Across Token Lengths

| Scenario | Average Tokens / Rollout | Total Generated Tokens | Effective Inference Time | Total Session Runtime (incl. setup) | Projected Cost (USD) | Margin to $2.00 Target | Margin to $3.00 Ceiling |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A. Compact CoT** | 400 tokens | 160,000 | 22 min | 28 min | **\$0.415** | +\$1.585 | +\$1.942 |
| **B. Baseline CoT** | 550 tokens | 220,000 | 30 min | 36 min | **\$0.534** | +\$1.466 | +\$1.823 |
| **C. Extended CoT** | 700 tokens | 280,000 | 38 min | 44 min | **\$0.653** | +\$1.347 | +\$1.704 |
| **D. Maximum CoT** | 900 tokens | 360,000 | 49 min | 55 min | **\$0.816** | +\$1.184 | +\$1.541 |
| **E. Conservative Fallback** | 768 max tokens (Transformers engine) | 307,200 | 95 min | 101 min | **\$1.498** | +\$0.502 | +\$0.859 |

### Key Financial Takeaways
1. Even under the slowest generation regime (Scenario E: Transformers engine fallback at 768 max tokens), the total projected spend is **\$1.498**, comfortably below the **\$2.00** experiment target and well within the **\$2.3575** remaining campaign budget.
2. Under optimized vLLM execution (Scenarios A–C), the entire 400-request replication will cost between **\$0.42 and \$0.65**, preserving more than **\$8.65** of the account balance (far exceeding the \$7.00 preservation requirement).
3. The watchdog limit of **\$2.00** provides a 100%–300% safety margin above expected execution time while guaranteeing that the \$7.00 floor is never breached.
