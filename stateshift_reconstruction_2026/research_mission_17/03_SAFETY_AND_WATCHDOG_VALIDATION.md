# StateShift: Research Mission 17 — Safety Architecture & Watchdog Daemon Validation

**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Daemon PID:** 42618  
**Experiment ID:** `stateshift_primary_400_01`  
**Timestamp:** 2026-10-26T04:10:47Z UTC  

---

## 1. Supervisor-First Architectural Invariant

A fundamental finding of the October 25–26 financial incident was that financial monitors integrated inside the runner process cannot protect the account if the runner hangs, encounters unhandled exceptions, or suffers network stalls.

In Research Mission 17, the **Supervisor-First Principle** was strictly enforced:
1. **Pre-Provisioning Spawning:** The independent financial watchdog daemon (`research_mission_15_6/supervision/independent_financial_watchdog.py`) was spawned as an autonomous OS process (PID 42618) **prior** to unsealing the cloud execution lock or making any pod creation API request.
2. **Atomic Readiness Handshake:** The provisioner blocked execution until the supervisor daemon independently connected to RunPod, verified account solvency, verified the cryptographic authorization token, and wrote its signed readiness receipt (`watchdog_readiness_stateshift_primary_400_01_sess_primary_1792987837.json`).
3. **Execution Unsealing:** Only after the supervisor published `status: READY` did the provisioner temporarily unlock the local execution guard to dispatch the single pod creation request.

---

## 2. Watchdog Parameter Specification

```
+-----------------------------------------------------------------------------+
|                     INDEPENDENT SUPERVISOR DAEMON (PID 42618)               |
+-----------------------------------------------------------------------------+
|  Supervised Pod ID:             pyau7qtpjfzx5e                              |
|  Assigned Experiment ID:         stateshift_primary_400_01                   |
|  Monitored Controller PID:       42598 (execute_authorized_primary_400.py)   |
|  Internal Poll Interval:         1.0 second                                  |
|  Authorized Spending Ceiling:    $3.5000 USD                                 |
|  Emergency Shutdown Trigger:     $2.8000 USD                                 |
|  Account Preservation Floor:     $7.0000 USD                                 |
|  Maximum Monotonic Runtime:      150.0 minutes (9000 seconds)                |
|  Direct Provider Endpoint:       https://api.runpod.io/graphql               |
+-----------------------------------------------------------------------------+
```

---

## 3. Active Safeguard Enforcement Protocols

1. **Dead-Man's Switch (Issue A):**
   - The watchdog monitors the runner process (`PID 42598`) and its local heartbeat ledger.
   - If the main runner process terminates unexpectedly, the watchdog immediately assumes ownership and issues an authoritative pod deletion request to RunPod within 1.0 second.

2. **Conservative Billing Estimation (Issue C):**
   - Billing calculation uses:
     $$\text{Effective Spend} = \max\left(\text{Provider Billed Spend},\, \text{Balance Delta},\, \frac{\text{Elapsed Monotonic Sec}}{3600} \times \$0.89\right)$$
   - This ensures that API reporting delays or stale balance caches cannot mask in-flight compute costs.

3. **Multi-Pass Destruction Verification (Issue D):**
   - Termination is never treated as confirmed upon merely dispatching the mutation.
   - The supervisor queries the provider API repeatedly until the status transitions to `TERMINATED`, `DELETED`, or returns an authoritative `NOT_FOUND` / 404 response.
   - Any intermediate status such as `STOPPED` (which still bills for disk storage) is immediately escalated and re-terminated.

4. **Cryptographic Authorization (Issue E):**
   - The supervisor independently loaded and validated the signed authorization document (`session_auth_primary_400.json`) using the PI's trusted Ed25519 public key.
   - The supervisor verified the experiment ID binding, model revision binding, manifest SHA-256 binding, and non-replayed nonce.

---

## 4. Certification

The supervisor daemon is actively running and independently protecting the Principal Investigator's account throughout the execution of the 400-request experiment.

**Principal Investigator:** Sham Satish Thakare  
**Date:** October 26, 2026  
