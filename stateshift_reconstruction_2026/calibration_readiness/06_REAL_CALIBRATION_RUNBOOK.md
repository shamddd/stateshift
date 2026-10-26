# StateShift — Real Calibration Runbook
## Calibration Readiness Phase 6
**Date:** 2026-10-26T06:02:49+05:30  
**Status:** PREPARED — NOT YET AUTHORIZED  
**Next action required: Separate human authorization from Principal Investigator**

> [!CAUTION]
> This document is a preparation artifact only. Execution of any step in "During Provisioning" or beyond requires explicit separate PI authorization. The cloud execution lock must not be removed until all pre-provisioning checks pass and fresh authorization tokens are generated.

---

## Experiment Parameters (Frozen)

| Parameter | Value |
|---|---|
| Provider | RunPod |
| Cloud tier | **Secure Cloud ONLY** |
| GPU type | NVIDIA RTX 4090, 24 GB VRAM |
| Maximum pods | **1** |
| Model | `Qwen/Qwen2.5-Math-7B-Instruct` |
| Model revision (to load) | `main` (resolve to `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`) |
| Calibration requests | **10 exactly** |
| Manifest | `calibration_10_manifest.json` |
| Manifest SHA-256 | `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6` |
| Temperature | `0.0` |
| Top-p | `1.0` |
| Max new tokens | `768` |
| Seed | `42` |
| Full 400-request experiment | **STRICTLY PROHIBITED** |

---

## Phase A: Pre-Provisioning Checklist (Blocking Gates)

Every item must be CONFIRMED before the lock is removed.

### A1. Account and Financial Verification
- [ ] Log in to RunPod dashboard via web browser.
- [ ] Record exact account balance to 4 decimal places.
- [ ] Confirm balance ≥ $8.00 (minimum recommended: $7.75 floor + $0.25 immediate buffer). If balance is below $8.00, top up before proceeding.
- [ ] Confirm zero active pods.
- [ ] Confirm zero stopped pods.
- [ ] Confirm zero network volumes.
- [ ] Record current RTX 4090 Secure Cloud price per hour.
- [ ] Verify estimated calibration cost ≤ agreed ceiling using current GPU price.
- [ ] Document: balance, price, pod count, volume count in a dated note.

### A2. Environment Verification
- [ ] Verify `RUNPOD_API_KEY` is set in the execution shell.
- [ ] Verify `RUNPOD_SSH_KEY_PATH` points to the PI's SSH private key for RunPod access.
- [ ] Verify local Python 3.13 + required packages available: `cryptography`, `paramiko`, `vllm`-client-equivalent (for remote vLLM API calls).
- [ ] Set `export STATE_SHIFT_CLOUD_EXECUTION_DISABLED=1` (belt-and-suspenders even though code defaults to locked).
- [ ] Verify `python -m pytest research_mission_15_6/tests/ -q` still returns 101/101 PASS.

### A3. Repository Integrity
- [ ] `git log --oneline -1` shows the preflight commit (Phase 8 commit hash).
- [ ] `openssl dgst -sha256 research_mission_15_6/manifests/calibration_10_manifest.json` returns `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6`.
- [ ] `.cloud_execution_locked` file is present.
- [ ] No staged or modified tracked files (clean working tree).

### A4. Cryptographic Authorization Generation
**This step must occur immediately before execution (tokens expire).**

The PI must use their Ed25519 **private key** (not the test seed key) to sign a new authorization document containing:
```json
{
  "schema_version": "1.0",
  "experiment_id": "<chosen_unique_experiment_id>",
  "manifest_sha256": "f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6",
  "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
  "model_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "pod_id": "PRE_PROVISION",
  "max_incremental_spend_usd": 0.35,
  "emergency_trigger_usd": 0.25,
  "minimum_account_balance_usd": 7.00,
  "maximum_runtime_minutes": 15,
  "nonce": "<unique_uuid4>",
  "issued_at_utc": <current_unix_timestamp>,
  "expiry_utc": <current_unix_timestamp + 900>
}
```
- [ ] Generate authorization token with PI private key.
- [ ] Write token to `authorization_CALIBRATION_<experiment_id>.json`.
- [ ] Verify token with: `python -m research_mission_15_6.auth.session_authorizer_v2 --verify <token_path>`.

### A5. Independent Supervisor Launch
- [ ] Start the independent watchdog in a separate terminal **before** removing the execution lock:
```bash
cd /Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026
python -m research_mission_15_6.supervision.independent_financial_watchdog \
    --experiment-id <experiment_id> \
    --api-key $RUNPOD_API_KEY \
    --balance-floor 7.00 \
    --emergency-threshold 0.25 \
    --max-runtime-minutes 15 \
    --local-data-dir research_mission_15_6/data/watchdog_state/
```
- [ ] Confirm watchdog writes readiness receipt: `watchdog_readiness_<experiment_id>_*.json` with `"status": "READY"`.
- [ ] Confirm watchdog process is still running (check PID).

### A6. Remove Execution Lock (Final Step Before Launch)
- [ ] All A1–A5 gates confirmed.
- [ ] Record the exact time of lock removal.
- [ ] Remove `.cloud_execution_locked` (rename, do not delete, for audit trail): `mv .cloud_execution_locked .cloud_execution_locked.pre_calibration_backup`
- [ ] Set `export STATE_SHIFT_CLOUD_EXECUTION_DISABLED=0` in the execution shell only.

**Hard wall-clock deadline:** Set a physical 20-minute timer starting from lock removal. If execution is not complete by T+20 minutes, proceed immediately to Emergency Termination.

---

## Phase B: During Execution

### B1. Launch
```bash
cd /Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026
python -m research_mission_15_6.runner.stateshift_launch \
    --mode calibration \
    --experiment-id <experiment_id> \
    --manifest research_mission_15_6/manifests/calibration_10_manifest.json \
    --authorization authorization_CALIBRATION_<experiment_id>.json \
    2>&1 | tee calibration_session_<experiment_id>.log
```

### B2. Continuous Monitoring (Human)
Every 2 minutes during execution:
- [ ] Check watchdog terminal: no `EMERGENCY_SHUTDOWN_DISPATCHED` or `CONTROLLER_FAILED` messages.
- [ ] Check RunPod dashboard: exactly 1 pod, status RUNNING, not STOPPED.
- [ ] Check running log: progress through request IDs.
- [ ] Check current spend in dashboard.

If any of the following occur, proceed immediately to Emergency Termination:
- Dashboard balance drops below $7.25.
- Pod count exceeds 1.
- Runner log shows no progress for more than 5 minutes.
- Watchdog reports emergency shutdown.
- Wall-clock timer reaches T+20 minutes.

### B3. No Automatic Pod Replacement
- The runner must never create a second pod. If the first pod terminates unexpectedly, the runner should fail with an error — NOT create a replacement.
- If a replacement pod appears in the dashboard that was not manually created, immediately terminate ALL pods and escalate.

### B4. No Automatic Start of Full Experiment
- After all 10 requests complete, the runner will write a calibration receipt and exit.
- The runner **must not** automatically begin loading `primary_100_manifest.json` or dispatching any further requests.
- Verify: runner process exits with code 0 after exactly 10 requests.

---

## Phase C: Post-Execution Verification

### C1. Verify 10 Authentic Generations
- [ ] `wc -l research_mission_15_6/data/<experiment_id>_generations.jsonl` returns exactly 10.
- [ ] All 10 records have `"source_type": "REAL_MODEL_INFERENCE"`.
- [ ] All 10 records have `"completion_status": "COMPLETED"`.
- [ ] All 10 request IDs match the calibration manifest.
- [ ] No duplicate request IDs.

### C2. Verify Model Provenance
- [ ] All 10 records have `"model_id": "Qwen/Qwen2.5-Math-7B-Instruct"`.
- [ ] All 10 records have `"model_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"`.

### C3. Verify Decoding Parameters
- [ ] All 10 records: `"temperature": 0.0`, `"max_tokens": 768`, `"seed": 42`, `"sampling_mode": "greedy"`.

### C4. Record Actual Runtime and Cost
- [ ] Note wall-clock start time (lock removal) and end time (runner exit).
- [ ] Record actual duration in minutes.
- [ ] Check RunPod billing page for actual charge.
- [ ] Record actual charge to 4 decimal places.
- [ ] Verify actual charge ≤ $0.35.

### C5. Verify Pod Destruction
- [ ] RunPod dashboard: pod count = 0.
- [ ] Pod status: TERMINATED or NOT_FOUND (not STOPPED).
- [ ] No network volumes.
- [ ] Watchdog log: `TERMINATION_CONFIRMED`.

### C6. Restore Execution Lock
- [ ] **Immediately** restore: `mv .cloud_execution_locked.pre_calibration_backup .cloud_execution_locked`
- [ ] Set `export STATE_SHIFT_CLOUD_EXECUTION_DISABLED=1`.
- [ ] Verify `python -c "from research_mission_15_6.auth.execution_lock import is_cloud_execution_locked; print(is_cloud_execution_locked())"` returns `(True, ...)`.

### C7. Run Evaluator
```bash
python -m research_mission_15_6.evaluation.math_answer_evaluator \
    --input research_mission_15_6/data/<experiment_id>_generations.jsonl \
    --output calibration_results_<experiment_id>.json
```
- [ ] Record per-condition accuracy.
- [ ] Record per-condition 95% bootstrap CI.
- [ ] Record calibration metrics for primary experiment cost estimation.

### C8. Reconcile Financial Records
- [ ] Check RunPod balance post-execution.
- [ ] Compute: balance_pre - balance_post = actual_charge.
- [ ] Verify actual_charge matches RunPod billing page.
- [ ] Update `calibration_financial_reconciliation.json` with all figures.

### C9. Git Commit Calibration Results
```bash
git add research_mission_15_6/data/<experiment_id>_generations.jsonl
git add calibration_results_<experiment_id>.json
git add calibration_financial_reconciliation.json
git commit -m "data: Authentic 10-request Qwen-7B calibration — experiment_id=<experiment_id>"
```

---

## Emergency Termination Procedure (Manual Fallback)

If the runner is unresponsive or the watchdog fails:

**Step 1 — API termination:**
```bash
curl -X POST https://api.runpod.io/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -d '{"query": "mutation { podTerminate(input: {podId: \"<POD_ID>\"}) }"}'
```

**Step 2 — Verify:**
```bash
curl -X POST https://api.runpod.io/graphql \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ pod(input: {podId: \"<POD_ID>\"}) { id desiredStatus } }"}'
```
Expected: `"desiredStatus": "TERMINATED"` or null response (pod not found).

**Step 3 — Dashboard verification:**  
Log in to `https://www.runpod.io/console/pods` and visually confirm zero pods.

**Step 4 — If API fails:**  
Click "Terminate" on the RunPod web dashboard for the specific pod. Do not use "Stop" (STOPPED ≠ TERMINATED).

**Step 5 — Restore lock regardless of outcome:**
```bash
mv .cloud_execution_locked.pre_calibration_backup .cloud_execution_locked
export STATE_SHIFT_CLOUD_EXECUTION_DISABLED=1
```

---

## What This Calibration Does NOT Authorize

- ❌ More than 10 inference requests.
- ❌ More than 1 pod at any time.
- ❌ Community Cloud (any tier other than Secure Cloud).
- ❌ Any network volume creation.
- ❌ Any GPU tier other than RTX 4090.
- ❌ Automatic start of the 400-request primary experiment.
- ❌ Any spending above the agreed ceiling.
- ❌ Any re-provisioning if the first pod fails.

The 400-request primary experiment requires a completely separate, independent human authorization after calibration results are reviewed.
