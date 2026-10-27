# Research Mission 23 — Phase 7: Financial Safety and Cloud Lifecycle Audit

## 1. Financial Ledger & Expenditure Caps

- **Account Status**: RunPod Secure Cloud.
- **Current Verified Balance**: **$10.1065 USD**.
- **Stage I Authorization**: **$0.00 USD** (Strictly Local CPU Audit).
- **Proposed Stage II Expenditure Ceiling**: **$1.60 USD**.
- **Projected Inference Cost**:
  - Hardware: One (1) NVIDIA RTX 4090 (24GB VRAM, Secure Cloud tier).
  - Rate: $\sim \$0.74\text{ per hour}$.
  - Expected Runtime: Model weight download ($\sim 4\text{ min}$) + 924 inference requests ($\sim 40\text{ min}$) + artifact transfer ($\sim 2\text{ min}$) $\approx \mathbf{46\text{ minutes}}$.
  - Projected Cost: $\frac{46}{60} \times \$0.74 \approx \mathbf{\$0.57\text{ USD}}$ (Well beneath the $\$1.60$ ceiling).

---

## 2. Frank Disclosure of Residual Billing Risk

### Why $1.60 USD is Not a Provider-Level Hard Cap
RunPod's cloud infrastructure operates on a continuous, per-second meter for active running pods. **The cloud provider itself does not enforce an automatic dollar-level circuit breaker at $1.60 USD**. 

The $1.60 USD ceiling is enforced entirely **client-side** by the StateShift runner script. If:
1. The local workstation experiences a sudden power loss, kernel panic, or network disconnect while the remote pod is running, and
2. The remote pod continues running without receiving a client termination signal,

charges would continue to accrue at $\$0.74/\text{hr}$ until the account balance ($10.1065 USD) is depleted, which would take approximately $\sim 13.6$ hours.

### Mitigation: Defense-in-Depth Lifecycle Safeguards
To eliminate this residual billing risk, StateShift deploys four concurrent layers of protection:
1. **Runner Wall-Clock Watchdog**: An internal thread that triggers auto-termination if runtime reaches 55 minutes ($0.916\text{ hr} \times \$0.74 = \$0.68\text{ USD}$).
2. **Idle Auto-Termination Daemon**: A remote supervisor container process that automatically runs `runpod.terminate_pod()` if no GPU forward pass occurs for 300 seconds.
3. **Signal Trapping**: Intercepts `SIGINT`, `SIGTERM`, and `SIGHUP` in Python, executing synchronous API pod deletion before exiting.
4. **Independent Workstation Supervisor**: A decoupled background script monitoring the pod via RunPod REST API, programmed to terminate the pod if the runner process exits.

---

## 3. Strict Fail-Closed Authorization Requirements

In strict adherence to Section 0 of Research Mission 23, Stage II GPU execution is **fail-closed** and cannot begin without explicit authorization from the Principal Investigator.

An authorization is valid if and only if it explicitly binds:
- **Mission Reference**: StateShift Mission 23.
- **Experimental Protocol**: Option B (Four-condition confirmatory trial).
- **Generation Horizon**: Exactly 924 planned neural generations (231 problems $\times$ 4 conditions).
- **Hardware Target**: One (1) NVIDIA RTX 4090 on RunPod Secure Cloud.
- **Maximum Spending Limit**: Exactly $1.60 USD.
- **Manifest SHA-256**: `2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5`.
- **Model Revision**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`.

Without this approval:
- `.cloud_execution_locked` remains permanently in place.
- No network requests to the RunPod provisioning API will be dispatched.
- Zero cloud dollars will be expended.
