# StateShift — Live RunPod Account Verification
## Calibration Readiness Phase 1 & 8
**Verification Timestamp:** 2026-10-26T06:21:03+05:30  
**Audit Protocol:** Strictly read-only query via RunPod GraphQL API (`https://api.runpod.io/graphql`).  
**Credentials Handling:** Utilized pre-existing local configuration (`~/.runpod/config.toml`). Zero credential exposure in reports, logs, or chat. Zero mutations, provisioning, or teardown calls executed.

---

## 1. Live Account Status Summary

| Item | Live Verified Value | Verification Method | Status |
|---|---|---|---|
| **Account Identifier** | `user_3I6YRPDHqf2wE2KnD9pT9cq8iFm` | RunPod GraphQL `myself { id }` | ✅ VERIFIED |
| **Current Account Balance** | **$1.317414 USD** ($1.3174) | RunPod GraphQL `myself { clientBalance }` | ✅ VERIFIED |
| **Current Hourly Spending** | **$0.00 / hr** | RunPod GraphQL `myself { currentSpendPerHr }` | ✅ VERIFIED |
| **Active Pods** | **0** (`[]`) | RunPod GraphQL `myself { pods { ... } }` | ✅ VERIFIED |
| **Stopped / Paused Pods** | **0** | RunPod GraphQL `myself { pods { ... } }` | ✅ VERIFIED |
| **Network Volumes** | **0** (`[]`) | RunPod GraphQL `myself { networkVolumes { ... } }` | ✅ VERIFIED |
| **Active Billable Resources** | **0** | Aggregated resource inspection | ✅ VERIFIED |
| **RTX 4090 Secure Cloud Price** | **$0.89 / hr** | RunPod GraphQL `gpuTypes` | ✅ VERIFIED |
| **RTX 4090 Community Price** | **$0.34 / hr** (Not Authorized) | RunPod GraphQL `gpuTypes` | ✅ VERIFIED |

---

## 2. Resource Verification Details

### 2.1 Compute Resources (Pods)
- Live query `query GetPods { myself { pods { id name desiredStatus costPerHr } } }` returned an empty list (`[]`).
- There are **zero running pods** and **zero stopped pods**.
- No dangling compute instances exist from the October 25–26 incident or previous runs.

### 2.2 Storage Resources (Network Volumes)
- Live query `query GetVolumes { myself { networkVolumes { id name size } } }` returned an empty list (`[]`).
- There are **zero persistent network volumes** incurring ongoing hourly storage costs.

### 2.3 Pricing Verification
- Query `query GpuTypes { gpuTypes { id displayName securePrice communityPrice } }` authoritatively confirms:
  - GPU ID: `NVIDIA GeForce RTX 4090`
  - Display Name: `RTX 4090`
  - **Secure Cloud Price:** `$0.89 / hr`
  - Community Cloud Price: `$0.34 / hr` (Protocol strictly restricts calibration to Secure Cloud)

---

## 3. Account Solvency & Funding Evaluation

- **Preservation Floor:** $7.0000 USD
- **Proposed Calibration Spending Ceiling:** $0.6000 USD
- **Arithmetic Minimum Balance Required:** $7.6000 USD
- **Recommended Balance Buffer (accounting for latency/uncertainty):** $8.0000 to $8.5000 USD
- **Current Live Balance:** **$1.3174 USD**
- **Solvency Status:** **INSUFFICIENT FUNDS — CRITICAL DEFICIT**

### Funding Gap Calculation
$$\text{Deficit to Minimum Floor Preservation} = \$7.6000 - \$1.3174 = \mathbf{\$6.2826\text{ USD}}$$
$$\text{Deficit to Recommended Safe Buffer} = \$8.0000 - \$1.3174 = \mathbf{\$6.6826\text{ USD}}$$

The account balance is currently **$5.6826 below the $7.00 preservation floor itself**. Launching any paid cloud operations under this state is mathematically prohibited by the financial safety specification.

---

## 4. Manual Verification Instructions for Principal Investigator

To independently verify these values via the RunPod Web Console:

1. **Log In:** Navigate to [https://www.runpod.io/console](https://www.runpod.io/console).
2. **Verify Pods:** Click on **"Pods"** in the left sidebar. Confirm that the list is empty (0 Pods).
3. **Verify Storage:** Click on **"Storage"** in the left sidebar. Confirm that there are 0 Network Volumes.
4. **Verify Balance & Rate:** Click on **"Billing"** in the left navigation. Confirm:
   - Account Balance matches approximately `$1.32`.
   - Current Spend Rate displays `$0.00 / hr`.
5. **Verify GPU Pricing:** Navigate to **"Deploy"** -> **"Secure Cloud"** -> filter for **RTX 4090**. Confirm rate is `$0.89 / hr`.

---

## 5. Phase 1 Conclusion

Live account verification is **COMPLETE AND VERIFIED**. Zero dangling resources or continuing charges exist. However, due to the verified balance of **$1.3174 USD**, the financial safety gate is **BLOCKED** until funds are replenished.
