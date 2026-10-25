# StateShift Mission 15.3: Budget-Aware Experiment Scheduling

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_3/07_BUDGET_AWARE_SCHEDULER.md`  

---

## 1. Executive Summary

Scientific completeness must never compromise cloud financial safety. To prevent runaway billing, `BudgetAwareScheduler` evaluates remaining budget headroom before dispatching each batch of inference requests.

---

## 2. Predictive Cost Algorithm

Before dispatching a batch of size $B$ (default 4–8 requests):
1. **Estimate Batch Runtime**:
   $$\hat{T}_{\text{batch}} = \left\lceil \frac{B}{C} \right\rceil \times \bar{L}_{\text{req}}$$
   where $C$ is GPU concurrency and $\bar{L}_{\text{req}}$ is the rolling average observed request latency.
2. **Estimate Batch Cost**:
   $$\hat{C}_{\text{batch}} = \frac{\hat{T}_{\text{batch}}}{3600} \times R_{\text{GPU}}$$
   where $R_{\text{GPU}} = \$0.89/\text{hr}$.
3. **Evaluate Effective Headroom**:
   $$C_{\text{effective\_limit}} = C_{\text{max}} - R_{\text{safety}} - C_{\text{shutdown\_overhead}}$$
   where $C_{\text{max}} = \$2.00$, $R_{\text{safety}} = \$0.35$, and $C_{\text{shutdown\_overhead}} = \frac{90\text{ s}}{3600} \times \$0.89 = \$0.02225$.
   $$\text{Effective Limit} = \$1.62775 \text{ USD}$$
4. **Scheduling Decision**:
   - If $\text{current\_spend} + \hat{C}_{\text{batch}} \le C_{\text{effective\_limit}}$: Dispatch allowed (`CAN_SCHEDULE`).
   - If $\text{current\_spend} + \hat{C}_{\text{batch}} > C_{\text{effective\_limit}}$: Dispatch halted immediately (`PARTIAL_BUDGET_STOP`).

---

## 3. Initial Physical-Run Calibration Checkpoint

When live GPU execution is authorized in the future, the runner will execute an initial calibration batch of **10 requests** before committing to the remaining 390 requests:
- **Sample Size**: 10 rollouts (GSM8K problem 1 across all 4 conditions plus 6 additional problems).
- **Evaluated Metrics**:
  - Model loading latency ($T_{\text{load}}$).
  - Empirical generation throughput (tokens/second).
  - Empirical cost per generation ($\$C_{\text{gen}}$).
- **Go / No-Go Decision Gate**:
  - If projected 400-request total spend $\le \$1.60$: Proceed with full execution.
  - If projected spend $> \$1.60$: Downscale or halt with partial preserved dataset.
