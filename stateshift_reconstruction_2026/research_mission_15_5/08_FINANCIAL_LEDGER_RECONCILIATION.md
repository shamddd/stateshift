# 08 Financial Ledger Reconciliation & Audit

**Target:** Audit historical campaign expenditure, account balance, and remaining allocation.

---

## 1. Accounting Reconciliation Table
| Dimension | Amount (USD) | Source of Truth / Verification |
| :--- | :--- | :--- |
| **Initial Account Funding** | $10.0000 | RunPod Account Initialization |
| **Current Verified Balance** | $9.3220 | Live GraphQL Account Query (`Missions 13-15.4`) |
| **Historical Actual Spent** | $0.6780 | RunPod Billed Ledger (`$10.0000 - $9.3220`) |
| **Prior Controller Estimate** | $0.6425 | Mission 14 Forensic Reconstructed Estimate |
| **Variance (Under-estimate)**| +$0.0355 | Pod storage/network/overrun billing reconciliation |
| **Total Campaign Budget** | $3.0000 | PI Mandatory Expenditure Ceiling |
| **Cumulative Spent to Date**| $0.6780 | Recognized Reconciled Spending |
| **Remaining Campaign Budget**| **$2.3220** | Available for Calibration + Full Experiment |
| **Mandatory Floor Reserve** | $7.0000 | Absolute Preservation Floor (`$9.3220 - $2.3220 = $7.0000`) |
| **Calibration Authorized** | $0.3500 | Single Calibration Cap |
| **Emergency Shutdown Trigger**| $0.2500 | Watchdog Automatic Termination Trigger |

## 2. Audit Findings
- Historical spend is reconciled at **$0.6780 USD** based on exact account balance subtraction.
- The remaining authorized campaign ceiling is **$2.3220 USD**.
- Performing the $0.35 calibration run will consume at most 15.1% of the remaining campaign budget, leaving at least **$1.9720 USD** for the final 400-rollout experiment.
- The account balance after maximum calibration spend will be at least **$8.9720 USD**, comfortably above the $7.0000 USD mandatory preservation floor.
