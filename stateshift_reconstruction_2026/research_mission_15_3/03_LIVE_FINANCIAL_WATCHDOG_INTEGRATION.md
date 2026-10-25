# StateShift Mission 15.3: Live Financial Watchdog Integration

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_3/03_LIVE_FINANCIAL_WATCHDOG_INTEGRATION.md`  

---

## 1. Executive Problem Statement

In previous missions, the cost controller was tested in isolation inside standalone test fixtures. It was not integrated into the production runner loop, meaning real-time inference, model loading, SFTP socket hangs, or network disconnections were unmonitored.

---

## 2. Integrated Supervisor Architecture

In `StateshiftProductionRunner`, the financial watchdog (`RobustCostControllerV8`) is actively embedded into the master supervision loop:
- **Tick Interval**: Every 1.0–3.0 seconds during execution.
- **Monitoring Scope**: Evaluates effective spend, machine uptime charges, and live balance deductions across all stages:
  1. Container boot & model weights loading.
  2. Active remote GPU inference.
  3. Intermediate SFTP snapshot sync.
  4. Network disconnection and reconnection phases.
  5. Dataset verification and pod destruction.

---

## 3. Financial Baseline & Emergency Trigger Matrix

| Financial Metric | Planning Input (USD) | Verification Status |
|:---|:---:|:---|
| Total Authorized Campaign Budget | \$3.0000 | Hard historical ceiling |
| Historical Campaign Spending | \$0.6425 | Confirmed RunPod usage |
| Remaining Authorized Campaign Headroom | \$2.3575 | Max allowed incremental spend |
| Live RunPod Account Balance | \$9.3220 | Authoritative provider baseline |
| Mandatory Preservation Floor | \$7.0000 | Non-negotiable preserved funds |
| Experiment Spending Target | \$1.50 – \$2.00 | Planned 400-request replication budget |
| Internal Watchdog Emergency Trigger | **\$1.6500** | \$2.00 minus \$0.35 safety reserve |
| Account Balance Emergency Floor Trigger | **\$7.3500** | \$7.00 plus \$0.35 safety reserve |
| Max Session Runtime Watchdog | **160.0 min** | Safety ceiling against hung processes |

### Action Protocol Upon Threshold Breach
1. **Event Persistence**: Writes `audit_event` to `cost_controller_audit.jsonl` atomically.
2. **Immediate Provider Termination**: Directly calls RunPod GraphQL API `podTerminate(podId)`.
3. **Destruction Verification**: Authoritatively checks that status is `TERMINATED` / `DELETED` or pod is null.
4. **Retry Loop with Backoff**: Retries up to 3 times if network error or provider delay occurs.
5. **Durable Escalation**: If retries are exhausted without provider confirmation, emits `CRITICAL_ALERT_POD_<id>.txt` with manual termination instructions.
6. **Data Preservation**: Best-effort intermediate sync is executed *only after* termination dispatch.
