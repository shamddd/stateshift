# Research Mission 23 — Phase 10: Execution Authorization Record

## 1. Authorization Status
- **Current Authorization State**: **PENDING EXPLICIT PI APPROVAL**
- **Stage I (Local CPU Audit & Remediation)**: **COMPLETED AND CERTIFIED ($0.00 USD spent)**
- **Stage II (Paid Physical GPU Execution)**: **LOCKED AND AWAITING SEPARATE AUTHORIZATION**
- **Hardware Fail-Closed Lock**: `.cloud_execution_locked` **ACTIVE ON DISK**

---

## 2. Formal Scope of Requested Authorization

Before any cloud infrastructure is provisioned or any paid forward pass is executed, the Principal Investigator must issue a separate, unambiguous approval specifying:

1. **Mission Identifier**: StateShift Research Mission 23.
2. **Experimental Design**: Option B (Four-condition confirmatory trial).
3. **Inference Volume**: Exactly 924 planned genuine neural generations across 231 disjoint held-out MATH-500 problems.
4. **Target Hardware**: Exactly one (1) physical NVIDIA RTX 4090 GPU (RunPod Secure Cloud tier).
5. **Spending Ceiling**: Maximum authorized expenditure of **$1.60 USD**.
6. **Explicit Provisioning Permission**: Clear authorization to unseal `.cloud_execution_locked` and provision the cloud pod.

---

## 3. Cryptographic and Model Binding

The requested authorization is cryptographically bound to the following fixed artifacts:
- **Manifest File**: `research_mission_22/data/confirmatory_231_manifest.jsonl`
- **Manifest SHA-256**: `2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5`
- **Model Hugging Face ID**: `Qwen/Qwen2.5-Math-7B-Instruct`
- **Pinned Model Revision**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
- **Decoding Configuration**: Greedy decoding (`temperature = 0.0`, `seed = 42`, `max_new_tokens = 768`)
- **Primary Estimator**: Difference in paired proportions $\hat{\tau}_{F-D} = \frac{b - c}{231}$ tested via exact two-sided McNemar test at $\alpha = 0.05$.

---

## 4. Financial and Risk Disclosure Checklist

| Checkpoint Item | Audit State | Verified Specification |
| :--- | :--- | :--- |
| **Account Balance** | Verified Intact | **$10.1065 USD** |
| **Hourly Rate** | Verified | $\sim \$0.74\text{ / hour}$ (NVIDIA RTX 4090, Secure Cloud) |
| **Expected Runtime** | Estimated | $\sim 46\text{ minutes}$ (Weights download + 924 generations + sync) |
| **Projected Cost** | Estimated | $\sim \mathbf{\$0.57\text{ USD}}$ |
| **Authorized Spend Cap** | Proposed Ceiling | **$1.60 USD** |
| **Residual Billing Risk** | Disclosed | RunPod does not provide an automated hardware dollar cap; ceiling is client-enforced by watchdog. Loss strictly capped by account balance. |
| **Termination Guarantee** | Verified | Watchdog auto-kill, idle 300s daemon, signal traps, and manual API script operational. |

---

## 5. Execution Decision
In strict compliance with Section 0 of the Mission Charter:
- **No cloud pod has been provisioned.**
- **No authorization token has been created or forged.**
- **No simulated generations have been labeled as real inference.**
- **Stage II execution is paused until explicit approval is received from the Principal Investigator.**
