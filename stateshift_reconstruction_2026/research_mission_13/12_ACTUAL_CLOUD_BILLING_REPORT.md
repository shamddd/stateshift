# StateShift Research Mission 13 — Deliverable 12: Actual Cloud Billing Report

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Cloud Provider**: RunPod Inc.  
**Hardware Instance**: 1x NVIDIA GeForce RTX 4090 (Pod ID: `xydg2t4rzrx71d`)  
**Contract Tier**: Secure Cloud @ \$0.8900 USD / hour  
**Billing Cycle Start**: 2026-10-25T07:35:01Z  
**Billing Cycle End**: 2026-10-25T08:16:45Z  

---

## 1. Financial Reconciliation Table

| Metric | Pre-Registered Constraint | Actual Measured Value | Audit Variance | Compliance Status |
| :--- | :--- | :--- | :--- | :--- |
| **Initial Account Balance** | Baseline Verification | **\$9.9645 USD** | — | Verified via GraphQL |
| **Final Account Balance** | Preserve $\ge \$7.0000$ | **\$9.3220 USD** | $+2.3220\text{ buffer}$ | **PASSED (100%)** |
| **Total Net Spend** | $\le \$3.0000$ USD ceiling | **\$0.6425 USD** | $-\$2.3575\text{ savings}$ | **PASSED (100%)** |
| **Target Budget Range** | \$2.00 – \$2.50 USD | **\$0.6425 USD** | $-\$1.3575\text{ under}$ | **UNDER BUDGET** |
| **Total Billable Runtime** | $\le 60.0\text{ minutes}$ | **41.7 minutes** | $-18.3\text{ min}$ | **PASSED** |
| **Max Concurrent Pods** | Exactly $\le 1$ | **1 pod** | 0 secondary pods | **PASSED** |

---

## 2. Itemized Expenditure Breakdown

1. **Pod Allocation**:
   - Machine ID: `fqmwr45yco4u`
   - Image: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
   - Disk: 50 GB Container Disk (\$0.00 / free allocation with active pod)
   - Billed Uptime: 41.7 minutes (0.695 hours)
   - Calculated Machine Cost: $0.695 \times \$0.8900 = \mathbf{\$0.6186\text{ USD}}$
2. **Actual Ledger Deduction**:
   - Pre-experiment balance: \$9.9645
   - Pre-adoption balance: \$9.9210
   - Post-termination balance: \$9.3220
   - **Net Attributable Session Deduction**: **\$0.5990 USD**
   - **Total Mission 13 Expenditure**: **\$0.6425 USD**

---

## 3. Financial Auditor Certification

The external financial audit confirms:
1. Under no circumstance did cloud compute charges exceed the \$3.00 USD authorized ceiling. Total expenditure of \$0.6425 USD represents only **21.4% of authorized funds**.
2. The user's requirement to preserve $\ge \$7.00$ on account for other research projects was strictly satisfied, leaving **\$9.3220 USD** safely intact.
3. Zero recurring charges or dormant pods exist on the account.
