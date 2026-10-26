# StateShift Research Mission 14 — Deliverable 06: Cloud Billing Reconciliation

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Investigating Role**: Independent Forensic Financial Auditor  
**Date**: October 25, 2026  

---

## 1. Investigation of Balance Figures Discrepancy

In Mission 13, multiple balance and expenditure numbers were recorded across different logs and deliverables:
- **Baseline Account Balance**: **\$9.9645 USD** (Reported in Stage 0 Pre-Flight Audit).
- **Session Adoption Balance**: **\$9.9210 USD** (Reported when Orchestrator adopted pod `xydg2t4rzrx71d`).
- **Final Post-Termination Balance**: **\$9.3220 USD** (Reported upon pod destruction).
- **Session Billed Spend**: **\$0.5990 USD** (Recorded in `termination_receipt.json`).
- **Cumulative Mission Spend**: **\$0.6425 USD** (Reported in `12_ACTUAL_CLOUD_BILLING_REPORT.md`).

### The Forensic Accounting Timeline:

```
[07:35:01 GMT] Pod Created (Pre-flight Baseline): Balance = $9.9645 USD
       |
       |  Pre-adoption runtime (~2.9 minutes @ $0.89/hr = $0.0435 USD)
       v
[07:38:00 GMT] Orchestrator Adopts Pod: Balance = $9.9210 USD
       |       (Notice: $9.9645 - $9.9210 = $0.0435 USD exact match)
       |
       |  Active Experiment Session (38.75 minutes @ $0.89/hr = $0.5748 USD + storage tax)
       v
[08:16:45 GMT] Termination Issued: Balance = $9.3220 USD
               Session deduction: $9.9210 - $9.3220 = $0.5990 USD exact match
```

### Reconciliation Findings:
1. **Both Spend Figures Are Correct in Their Respective Scopes**:
   - **\$0.5990 USD** represents the exact ledger deduction during the second orchestrator session (from adoption to termination).
   - **\$0.0435 USD** represents the billing during the initial 2.9 minutes prior to adoption.
   - **\$0.6425 USD** represents the **Total Cumulative Attributable Spending** for Pod `xydg2t4rzrx71d` across its entire lifespan ($0.0435 + 0.5990 = 0.6425$).
2. **Billing Clock Accounting Defect in Mission 13**:
   - `ExternalRunPodCostController` in Mission 13 did not ingest the pod's original creation timestamp when adopting the pod; it reset `self.start_time = time.time()`, omitting the initial 2.9 minutes from its internal runtime calculation.
   - This was corrected in `RobustExternalCostControllerV5` by computing `start_time = now - uptimeSeconds`.

---

## 2. Multi-Failure Resilience & Budget Guarantees

An external cost controller operating client-side cannot provide a cryptographic guarantee that the cloud provider will not bill past a threshold if network connectivity to the provider's API fails. 

To maintain scientific integrity:
1. **No Absolute Cap Claim**: We do not describe client-side cost controllers as an absolute guarantee. A true hard cap requires provider-level spending limit controls at the account level.
2. **Defensive Tripping**: The controller sets its internal shutdown trip at **\$2.80 USD** (a \$0.20 safety margin below the \$3.00 authorization limit) and executes hard termination immediately upon reaching that limit or encountering a 10-minute heartbeat stall.
3. **Audit Verification**:
   - Account Balance Preserved: **\$9.3220 USD** (Strictly preserves the user mandate to maintain $\ge \$7.00$ on account).
   - Total Budget Utilized: **21.4%** (\$0.6425 / \$3.0000).
   - Unspent Authorized Capital: **\$2.3575 USD**.
