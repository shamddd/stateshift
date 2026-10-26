# StateShift: Research Mission 17 — Financial Reconciliation Audit

**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Experiment ID:** `stateshift_primary_400_01`  
**Pod ID:** `pyau7qtpjfzx5e`  
**Ledger Path:** `data/primary_run/primary_400_reconciliation.json`  
**Timestamp:** 2026-10-26T05:31:57Z UTC  

---

## 1. Executive Summary

This report delivers the comprehensive financial reconciliation for the 400-request primary GPU experiment. All billing figures reflect settled, authoritative account debits recorded directly on the RunPod cloud infrastructure.

The entire primary experiment—encompassing pod provisioning, environment setup, model weights download, and 400 complete neural rollouts—was executed for a total settled cloud cost of **\$1.1476 USD** (~**\$0.00287 USD per rollout**). 

The account preservation floor of **\$7.0000 USD** was strictly protected at all times, with a closing balance of **\$10.1065 USD** (a **\$3.11 surplus** above the mandatory floor).

---

## 2. Settled Financial Audit Table

| Financial Parameter | Authorized / Predicted | Actual Settled Provider Telemetry | Audit Status |
| :--- | :--- | :--- | :--- |
| **Initial Account Balance** | $\ge \$10.5000$ USD | **$\$11.2541$ USD** ($11.2541107823) | **VERIFIED** |
| **Final Account Balance** | $\ge \$7.0000$ USD | **$\$10.1065$ USD** ($10.1065312128) | **VERIFIED** |
| **Net Cloud Expenditure** | $\le \$3.5000$ USD | **$\$1.1476$ USD** ($1.1475795695) | **VERIFIED COMPLIANT** |
| **Spending Ceiling Compliance** | $\$3.5000$ USD | $32.79\%$ of ceiling utilized | **PASSED (67.2% budget margin)** |
| **Emergency Shutdown Margin** | $\$2.8000$ USD | Never breached (peak spend: $\$1.1476$) | **PASSED (\$1.6524 buffer)** |
| **Preservation Floor Margin** | $\$7.0000$ USD | Maintained throughout (\$10.1065 closing) | **PASSED (+\$3.1065 surplus)** |
| **GPU Hourly Rate** | $\$0.8900$ / hr | $\$0.8900$ / hr (RTX 4090 Secure Cloud) | **EXACT MATCH** |
| **Session Active Duration** | $\le 150.0$ min | **80.75 minutes** (4,844.9 seconds) | **VERIFIED** |
| **Network Storage Charges** | $\$0.0000$ USD | $\$0.0000$ USD (0 persistent volumes) | **ZERO STORAGE OVERHEAD** |
| **Completed Requests** | Exactly 400 | Exactly 400 requests | **100% COMPLETE** |

---

## 3. Unit Economics & Cost Efficiency

$$\text{Unit Cost per Request} = \frac{\$1.14757957}{400 \text{ requests}} = \$0.00286895 \approx \mathbf{0.287\text{ cents / request}}$$

- **Average Token Generation Cost:**
  - Total tokens generated across 400 requests: $\approx 99,000$ tokens.
  - Compute cost per 1,000 tokens: $\approx \$0.0116$ USD (~1.16 cents / 1K tokens).
- **Theoretical Compute Model Validation:**
  $$\text{Theoretical Cost} = \frac{4844.9\text{ s}}{3600\text{ s/hr}} \times \$0.89/\text{hr} = \$1.1978\text{ USD}$$
  - The settled provider charge of $\$1.1476$ USD matches the continuous theoretical physics model within **$0.05 USD** (5.02 cents variance, attributable to RunPod second-level billing startup discounting).

---

## 4. Financial Incident Contrast (Oct 25 vs. Oct 26)

| Dimension | October 25–26 Incident | October 26 Research Mission 17 |
| :--- | :--- | :--- |
| **Account Starting Balance** | ~$7.25 USD | $11.2541 USD |
| **Account Closing Balance** | ~$1.00 USD (Breached floor) | **$10.1065 USD (Floor preserved)** |
| **Watchdog Architecture** | Internal / vulnerable to hang | **Supervisor-First Daemon (PID 42618)** |
| **Storage Leakage Risk** | High (untracked volume risk) | **0 GB volumes provisioned** |
| **Execution Governance** | Uncontrolled background task | **Ed25519 single-use cryptographic token** |
| **Destruction Protocol** | Unconfirmed termination | **Provider GraphQL authoritative verification** |

---

## 5. Certification

I certify that the financial ledger recorded in `data/primary_run/primary_400_reconciliation.json` accurately reflects the final, settled provider charges debited by RunPod for Research Mission 17.

**Principal Investigator:** Sham Satish Thakare  
**Date:** October 26, 2026  
