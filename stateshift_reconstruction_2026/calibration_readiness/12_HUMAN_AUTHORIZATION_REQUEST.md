# StateShift — Human Authorization Request Document
## Calibration Readiness Phase 7 & 8
**Document Type:** Formal Principal Investigator Authorization Protocol  
**Date:** 2026-10-26T06:21:03+05:30  
**Addressed To:** Sham Satish Thakare (Principal Investigator)  
**Status:** DRAFT — PENDING REQUISITE DEPOSIT & FORMAL PI SIGN-OFF  

---

> [!IMPORTANT]
> **NO EXECUTION PERMITTED UNDER THIS DOCUMENT.**
> This document does NOT authorize cloud deployment. It establishes the exact cryptographic and policy bounds that the Principal Investigator must explicitly sign and authorize once prerequisite funding is deposited.

---

## 1. Summary of Scope and Constraints

| Parameter | Mandated Value | Security & Scientific Enforcement |
|---|---|---|
| **Cloud Provider** | **RunPod** | Authenticated via isolated API transport. |
| **Cloud Tier** | **Secure Cloud ONLY** | Community Cloud strictly prohibited. |
| **GPU Target** | **1x NVIDIA GeForce RTX 4090** | 24 GB VRAM; verified at $0.8900 / hr. |
| **Maximum Pod Count** | **Exactly 1 Pod** | Enforced by single-attempt invariant (`max_attempts = 1`). |
| **Target Model** | `Qwen/Qwen2.5-Math-7B-Instruct` | Canonical instruction-tuned mathematical reasoning model. |
| **Pinned Model Revision** | `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` | Full 40-character SHA-1 confirmed on HuggingFace Hub. |
| **Experiment Scope** | **Exactly 10 Frozen Requests** | Manifest SHA-256: `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6`. |
| **Parent Manifest SHA-256** | `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` | Frozen primary benchmark dataset. |
| **Conditions Evaluated** | Conditions A, D, E, F | 3 Zero-Shot (A), 3 Forced Restart (D), 2 Explicit Repair (E), 2 State-Preserving (F). |
| **Decoding Configuration** | Greedy (T=0.0, top-p=1.0, seed=42) | Maximum new tokens: 768. |
| **Spending Ceiling** | **$0.6000 USD** | Maximum incremental budget allowance. |
| **Emergency Shutdown Trigger** | **$0.2500 USD** | Early termination tripwire monitored by independent daemon. |
| **Account Preservation Floor** | **$7.0000 USD** | Non-negotiable account balance reserve. |
| **Hard Wall-Clock Runtime Limit**| **25.0 Minutes** | Bounded runtime enforced locally and daemon-side. |
| **Automated Retries** | **STRICTLY PROHIBITED** | Zero replacement pods. On pod failure, fail-closed teardown. |
| **Primary 400-Request Experiment** | **STRICTLY PROHIBITED** | Execution stops permanently upon completion of request 10. |
| **Destruction Verification** | **MANDATORY PROVIDER CONFIRMATION** | Pod must reach `NOT_FOUND` or `TERMINATED`. `STOPPED` is rejected. |

---

## 2. Prerequisite Conditions Required Before Signature

Before signing this authorization request, the Principal Investigator must ensure that:

1. **Account Funding Completed:**
   - The Principal Investigator has manually deposited funds via [RunPod Console](https://www.runpod.io/console/billing).
   - The verified balance is **at least $7.60 USD** (recommended: **$8.00 to $8.50 USD**).
2. **Resource Hygiene Verified:**
   - There are **0 active pods** and **0 network volumes** in the RunPod console.
3. **Execution Lock Integrity:**
   - The local environment remains fail-closed (`STATE_SHIFT_CLOUD_EXECUTION_DISABLED=1` and `.cloud_execution_locked` present) until the moment of execution.

---

## 3. Canonical Human Authorization Statement

When the prerequisite funds are confirmed in the RunPod dashboard, the Principal Investigator should issue the following binding authorization statement:

```text
"I, Sham Satish Thakare, Principal Investigator, approve provisioning exactly one Secure Cloud RTX 4090 on RunPod for the StateShift 10-request calibration (Manifest SHA: f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6).

Authorized spending parameters:
- Spending Ceiling: $0.60 USD
- Emergency Teardown Tripwire: $0.25 USD
- Account Preservation Floor: $7.00 USD
- Maximum Runtime: 25 minutes
- Model: Qwen/Qwen2.5-Math-7B-Instruct (Revision: ef9926d75ab1d54532f6a30dd5e760355eb9aa4d)

Constraints:
- Exactly one pod; zero automatic replacement pods.
- Execution must stop after 10 requests; the 400-request primary experiment is STRICTLY PROHIBITED.
- Provider destruction verification is mandatory."
```

---

## 4. Cryptographic Authorization Generation Procedure

Following the deposit and verbal/written statement, the PI generates the Ed25519 cryptographic authorization token:

```bash
python3 -c "
import uuid, time, json
from research_mission_15_6.auth.session_authorizer_v2 import CryptographicAuthorizer

# Load PI Private Key (Never committed to git)
with open('/Users/shamthakare/.ssh/stateshift_pi_ed25519', 'rb') as f:
    priv_bytes = f.read()

payload = {
    'schema_version': '1.0',
    'experiment_id': 'stateshift_calib_20261026_01',
    'manifest_sha256': 'f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6',
    'model_id': 'Qwen/Qwen2.5-Math-7B-Instruct',
    'model_revision': 'ef9926d75ab1d54532f6a30dd5e760355eb9aa4d',
    'pod_id': 'PRE_PROVISION',
    'max_incremental_spend_usd': 0.60,
    'emergency_trigger_usd': 0.25,
    'minimum_account_balance_usd': 7.00,
    'maximum_runtime_minutes': 25.0,
    'nonce': uuid.uuid4().hex,
    'issued_at_utc': time.time(),
    'expiry_utc': time.time() + 1800.0
}

auth_doc = CryptographicAuthorizer.create_signed_authorization(
    payload=payload,
    private_key=priv_bytes,
    model_id=payload['model_id'],
    model_revision=payload['model_revision']
)

with open('data/primary_run/session_auth_calibration.json', 'w') as f:
    json.dump(auth_doc, f, indent=2)

print('Cryptographic session authorization generated successfully.')
"
```
