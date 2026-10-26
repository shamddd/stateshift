# StateShift — Execution Runbook ($1 Budget Calibration)
## Deliverable 06 — Step-by-Step Operator Procedures & Safety Runbook
**Status:** DRAFT / AUDITED — PENDING HUMAN AUTHORIZATION  
**Execution Target:** Exactly ONE RunPod Secure Cloud NVIDIA GeForce RTX 4090  
**Model:** `Qwen/Qwen2.5-Math-7B-Instruct` @ `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`  
**Manifest:** `calibration_10_manifest.json` (SHA-256: `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6`)  

---

> [!CAUTION]
> **READ-ONLY AUDIT NOTICE:**
> Do NOT run these execution steps until the Principal Investigator provides the signed cryptographic authorization token and issues verbal/written approval.

---

## 1. Operational Invariants & Budgets

```text
================================================================================
FINANCIAL & SAFETY INVARIANTS:
1. Provider: RunPod Secure Cloud ONLY (Community Cloud strictly forbidden).
2. Compute: Exactly ONE RTX 4090 (24 GB VRAM). Zero replacement pods.
3. Max Planned Expenditure: $1.0000 USD (Ceiling).
4. Early Shutdown Trigger: $0.7000 USD (Monitored by independent watchdog).
5. Target Reserve Floor: $0.3200 USD (Target reserve; provider billing delays or failed termination may reduce or eliminate it).
6. Hard Runtime Deadline: 45.0 Minutes (Local wall-clock monotonic timeout).
7. Single-Attempt Invariant: Exactly one provisioning attempt; zero automated retries.
8. Protocol Limitation: Exactly 10 requests. Primary experiment STRICTLY PROHIBITED.
================================================================================
```

---

## 2. Pre-Execution Verification (Step 0)

Before removing the execution lock or generating tokens:

1. **Verify Balance:**
   Execute read-only GraphQL query to confirm balance $\ge \$1.3174$ USD.
2. **Verify Resources:**
   Confirm active pods = 0, stopped pods = 0, network volumes = 0.
3. **Verify Git Tree:**
   Confirm HEAD commit matches current authorized commit and working tree is clean.
4. **Verify Manifest Hash:**
   ```bash
   openssl dgst -sha256 research_mission_15_6/manifests/calibration_10_manifest.json
   # MUST return: f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6
   ```

---

## 3. Cryptographic Token Generation (Step 1)

The Principal Investigator runs the following Python snippet to sign the session approval:

```bash
python3 -c "
import uuid, time, json
from research_mission_15_6.auth.session_authorizer_v2 import CryptographicAuthorizer

with open('/Users/shamthakare/.ssh/stateshift_pi_ed25519', 'rb') as f:
    priv_bytes = f.read()

payload = {
    'schema_version': '1.0',
    'experiment_id': 'stateshift_calib_b1_01',
    'manifest_sha256': 'f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6',
    'model_id': 'Qwen/Qwen2.5-Math-7B-Instruct',
    'model_revision': 'ef9926d75ab1d54532f6a30dd5e760355eb9aa4d',
    'pod_id': 'PRE_PROVISION',
    'max_incremental_spend_usd': 1.00,
    'emergency_trigger_usd': 0.70,
    'minimum_account_balance_usd': 0.32,
    'maximum_runtime_minutes': 45.0,
    'authorized_mode': 'CALIBRATION',
    'financial_policy_version': 'POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION',
    'nonce': uuid.uuid4().hex,
    'issued_at_utc': time.time(),
    'expiry_utc': time.time() + 2700.0
}

auth_doc = CryptographicAuthorizer.create_signed_authorization(
    payload=payload,
    private_key=priv_bytes,
    model_id=payload['model_id'],
    model_revision=payload['model_revision']
)

with open('data/primary_run/session_auth_calib_b1.json', 'w') as f:
    json.dump(auth_doc, f, indent=2)

print('Authorized session token minted successfully.')
"
```

---

## 4. Execution Launch Sequence (Step 2)

```bash
# 1. Unlock cloud execution for this session only
export STATE_SHIFT_CLOUD_EXECUTION_DISABLED=0

# 2. Execute canonical launcher
python -m research_mission_15_6.runner.stateshift_launch \
    --mode calibration \
    --experiment-id stateshift_calib_b1_01 \
    --manifest research_mission_15_6/manifests/calibration_10_manifest.json \
    --authorization data/primary_run/session_auth_calib_b1.json \
    --trusted-public-key /Users/shamthakare/.ssh/stateshift_pi_ed25519.pub \
    --local-data-dir data/primary_run \
    --remote-work-dir /workspace/stateshift_run \
    --max-cost 1.00 \
    --max-runtime 45.0 \
    --gpu-rate 0.89 \
    --poll-interval 1.0 \
    2>&1 | tee stateshift_calibration_b1_execution.log
```

---

## 5. Live Supervision & In-Flight Monitoring (Step 3)

During execution, the operator monitors three concurrent streams:

1. **Watchdog Heartbeat:**
   Watchdog daemon continuously writes `data/primary_run/watchdog/watchdog_heartbeat_stateshift_calib_b1_01.json`.
   - Verify `effective_spend_usd` < $0.70.
   - Verify `elapsed_minutes` < 45.0.
   - Verify `pod_status` is `RUNNING`.
2. **Incremental Dataset Checkpointing:**
   `data/primary_run/stateshift_calib_b1_01_generations.jsonl` appends one record per completed request.
   - Inspect generation timestamps and response lengths.
3. **Provider Console Dashboard:**
   Confirm exactly 1 pod is active. If any unexpected second pod appears, immediately dispatch emergency shutdown.

---

## 6. Teardown & Destruction Verification (Step 4)

Immediately upon completion of the 10th request (or upon emergency tripwire breach):

1. **Mutation Dispatched:** Orchestrator calls `podTerminate(podId)`.
2. **Multi-Pass Destruction Verification:**
   - Transport queries provider up to 5 times (2.0s delay).
   - Confirms state is `NOT_FOUND` or `TERMINATED`.
   - **`STOPPED` status is strictly rejected.**
3. **Supervisor Process Exit:**
   - Watchdog daemon exits only after confirmed destruction.
4. **Execution Lock Re-Engagement:**
   ```bash
   export STATE_SHIFT_CLOUD_EXECUTION_DISABLED=1
   python3 -c "
   import json, datetime
   with open('.cloud_execution_locked', 'w') as f:
       json.dump({
           'locked': True,
           'reason': 'Post-calibration routine lock re-engagement.',
           'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()
       }, f, indent=2)
   "
   ```

---

## 7. Post-Run Forensic Audit & Scientific Completion Criteria (Step 5)

Calibration is certified **COMPLETE** only if all 10 criteria pass:

| # | Scientific Completion Criterion | Verification Command / Check | Result Requirement |
|---|---|---|---|
| **1** | Exactly 10 Records | `wc -l data/primary_run/stateshift_calib_b1_01_generations.jsonl` | Exactly `10` lines. |
| **2** | Request ID Match | Check all IDs vs `calibration_10_manifest.json` | 100% matched; 0 duplicates. |
| **3** | Model Provenance | `grep '"model_id"' ...` | All records specify `Qwen/Qwen2.5-Math-7B-Instruct`. |
| **4** | Revision SHA Match | `grep '"model_revision"' ...` | All records specify `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`. |
| **5** | Decoding Parameters | Verify `temperature=0.0`, `seed=42`, `top_p=1.0` | 100% compliant. |
| **6** | No Output Truncation | Check `finish_reason` in records | `finish_reason == "stop"` (no length truncation). |
| **7** | Evaluation Scored | Run `math_answer_evaluator.py` | Generates per-condition accuracy & LaTeX traces. |
| **8** | Actual Runtime Measured | Inspect `termination_receipt_*.json` | Duration recorded in seconds. |
| **9** | Actual Spend Reconciled | Inspect `financial_reconciliation_*.json` | Total spend $\le \$1.0000$ USD; reserve $\ge \$0.3200$. |
| **10** | Pod Destruction Confirmed | RunPod API returns `pod == null` | Exactly 0 pods remaining. |

---

## 8. Partial Output Preservation Protocol

If the run is interrupted by network drop, provider timeout, or emergency tripwire before all 10 requests complete:

1. **Preserve Authentic Traces:** All completed `.jsonl` lines remain permanently on disk.
2. **Mark Incomplete:** Reconciler logs `CALIBRATION_INTERRUPTED_PARTIAL`.
3. **No False Completion:** The session is explicitly marked as partial; partial data is never represented as a complete 10-request dataset.
4. **Resume Ready:** The next session can re-attach or resume from the exact uncompleted request ID without repeating work.
