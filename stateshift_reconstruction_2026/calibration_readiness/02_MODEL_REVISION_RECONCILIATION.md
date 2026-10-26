# StateShift — Model Revision Reconciliation
## Calibration Readiness Phase 2
**Date:** 2026-10-26T06:02:49+05:30  
**Verifier:** Independent preflight auditor

---

## Executive Finding

**The frozen manifests specify `"main"` as the model revision — not a pinned commit hash.**  
**The runner and auth module hardcode `c869d27376a8d6728795551322fe323b6` — a 33-character string that is not a valid Git SHA-1.**  
**The canonical `main` branch HEAD commit for `Qwen/Qwen2.5-Math-7B-Instruct` on HuggingFace is `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` (40-character SHA-1).**

This creates a **three-way discrepancy** with reproducibility implications.

---

## Revision A: `c869d27376a8d6728795551322fe323b6`

**Source locations:**
- `research_mission_15_6/auth/session_authorizer_v2.py` line 27: `PINNED_MODEL_REVISION = "c869d27376a8d6728795551322fe323b6"`
- `research_mission_15_6/runner/stateshift_production_runner_v10.py` lines 627–628: output record schema

**Properties:**
```
Length: 33 characters
SHA-1 standard: 40 hex characters → INVALID
SHA-256 standard: 64 hex characters → INVALID
Git commit hash: NOT a valid Git object hash
Is valid hex: YES (all chars 0–9a–f)
```

**Conclusion:** Revision A is a **malformed or truncated hash**. It does not correspond to any known Git standard. It is 33 characters — one character longer than a 32-character MD5 hash (128-bit), but not 40 (SHA-1) or 64 (SHA-256). Most likely it resulted from a copy-paste or truncation error during an earlier mission where an actual HuggingFace commit hash was transcribed incorrectly.

**This string cannot be used to pin a HuggingFace model revision.** If passed to `from_pretrained(..., revision="c869d27376a8d6728795551322fe323b6")`, HuggingFace Hub will reject it or fall back to `main`.

---

## Revision B: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`

**Source locations:**
- Mission 15.5 brief and historical project records: described as "canonical commit for `Qwen/Qwen2.5-Math-7B-Instruct` main"

**Properties:**
```
Length: 40 characters
SHA-1 standard: 40 hex characters → VALID
Is valid hex: YES
```

**HuggingFace live API confirmation (read-only GET, no auth, no download):**
```
GET https://huggingface.co/api/models/Qwen/Qwen2.5-Math-7B-Instruct
Response: {"sha": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d", "modelId": "Qwen/Qwen2.5-Math-7B-Instruct"}
```

**Conclusion:** Revision B (`ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`) is the **current `main` HEAD commit** for the model. It is a valid 40-character SHA-1 Git hash. It matches what HuggingFace returns as the current `sha` for this model.

---

## Revision "main": Frozen Manifests

**All 10 calibration requests and all 400 primary requests specify:**
```json
"model_revision": "main"
```

This means the frozen experimental protocol intentionally uses the **symbolic branch name `main`** rather than a pinned commit hash.

**Implication:** Any execution using `revision="main"` will pull whatever commit `main` points to **at the time of download**. If HuggingFace updates the model repository after the calibration was designed but before physical execution, the exact weights used could differ from those used during the incident-era smoke tests.

---

## Resolution Analysis

### Question 1: Which revision is in the frozen manifest?
**Answer:** `"main"` — the symbolic branch pointer, not a pinned hash.

### Question 2: Which revision appears in historical execution records?
**Answer:** Historical `.jsonl` records (including `recovered_smoke_test_generations.jsonl`, `provenance_audit_ledger.json`, and all confirmed authentic generation records) specify `"model_revision": "main"`. The authentic generations recovered from the RunPod incident were made using `revision="main"` — they used whatever commit `main` pointed to at execution time.

### Question 3: Which revision is referenced by the current inference adapter?
**Answer:** The production runner (`stateshift_production_runner_v10.py` lines 627–628) hardcodes `c869d27376a8d6728795551322fe323b6` in **output record metadata** (the JSON written to disk to record what revision was used). The auth module hardcodes the same string as `PINNED_MODEL_REVISION` and enforces it in cryptographic authorization verification.

This means: if the runner executes and writes output records, it stamps them with the malformed string as the claimed `model_revision`. But the actual model loaded by vLLM/HuggingFace would use `"main"` (from the manifest) — or whatever the adapter passes to `from_pretrained`.

### Question 4: Are either revision truncated or invalid?
**Answer:**
- Revision A (`c869d27376a8d6728795551322fe323b6`): **INVALID — 33 chars, not a valid Git hash.**
- Revision B (`ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`): **VALID — 40-char SHA-1, confirmed as current HuggingFace main HEAD.**
- `"main"`: **VALID — symbolic branch name, but non-reproducible across time.**

### Question 5: Was the revision difference a deliberate protocol change?
**Answer:** No evidence of deliberate choice. Revision A most likely resulted from a copy-paste truncation error in Mission 15.5 or earlier. The manifest using `"main"` was created before any pinned hash was chosen. The auth module and runner were subsequently patched to enforce a pinned hash, but the hash chosen was already malformed.

### Question 6: Do model weights or tokenizer differ?
**Answer:** Since Revision A is invalid and will not resolve to a real Git object, any actual inference execution would use `"main"` (the HuggingFace fallback). As of 2026-10-26, `"main"` resolves to `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`. The 4 authentic smoke-test generations recovered from the incident used the same effective weights (they also used `revision="main"`).

If the `main` branch is updated before calibration execution, there is a small risk of weight divergence from the incident-era records.

### Question 7: Does the discrepancy affect reproducibility?
**Answer:** **Yes, in two ways:**

1. **Output record mismatch:** The runner stamps output records with `c869d27376a8d6728795551322fe323b6` (invalid) as the `model_revision`, but the actual model loaded uses `"main"` (resolved to a real commit). Reviewers inspecting the output JSON would see an invalid revision string that cannot be verified.

2. **Non-reproducibility over time:** Using `revision="main"` means future replication attempts may load different weights if the model repository is updated.

---

## Required Remediation (locally fixable, does not modify frozen manifests)

> [!IMPORTANT]
> The frozen manifests (`calibration_10_manifest.json`, `primary_100_manifest.json`) must **not** be modified. Their SHA-256 hashes are locked.

**The fix must be applied to the runner and auth module only:**

1. Replace `PINNED_MODEL_REVISION = "c869d27376a8d6728795551322fe323b6"` in `session_authorizer_v2.py` with `PINNED_MODEL_REVISION = "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"` (the verified valid 40-char SHA-1).

2. Replace the hardcoded `"model_revision": "c869d27376a8d6728795551322fe323b6"` in the output record schema in `stateshift_production_runner_v10.py` with `"model_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"`.

3. The manifests specify `"model_revision": "main"` — the inference call should pass `revision="main"` (matching the manifest protocol as designed), and the output record should record the **resolved** commit hash `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` as the actual loaded revision (retrieved from the model's config at runtime).

> [!WARNING]
> This remediation changes `PINNED_MODEL_REVISION` in `session_authorizer_v2.py`, which affects cryptographic authorization verification. Any existing signed authorization tokens that specify `"model_revision": "c869d27376a8d6728795551322fe323b6"` will be **rejected** after this fix. A fresh authorization token must be generated with the corrected revision. This is the correct security behavior.

---

## Calibration Gate Decision

| Condition | Status |
|---|---|
| Revision A valid | ❌ INVALID (33 chars, malformed) |
| Revision B valid | ✅ VALID (40-char SHA-1) |
| Revision B matches current HuggingFace main HEAD | ✅ CONFIRMED |
| Manifests use "main" (non-pinned) | ⚠️ ADVISORY (non-pinned, but consistent with historical execution) |
| Runner output records use correct hash | ❌ INCORRECT (uses malformed Revision A) |
| Auth enforces correct hash | ❌ INCORRECT (enforces malformed Revision A) |
| Fix locally executable without manifest modification | ✅ YES |

**Gate status: BLOCKED — pending local remediation of Revision A in runner and auth module.**

The remediation is straightforward and does not require modifying any frozen manifest. See Phase 4 (Safety Gate Verification) for the test protocol after remediation.

---

## Revision Reconciliation Summary

| Source | Revision Specified | Valid? | Consistent with History? |
|---|---|---|---|
| `calibration_10_manifest.json` | `"main"` | Symbolic (valid) | ✅ Yes |
| `primary_100_manifest.json` | `"main"` | Symbolic (valid) | ✅ Yes |
| Recovered authentic generation records | `"main"` | Symbolic (valid) | ✅ Yes |
| `session_authorizer_v2.py` PINNED_MODEL_REVISION | `c869d27376a8d6728795551322fe323b6` | ❌ MALFORMED | ❌ No |
| `stateshift_production_runner_v10.py` output record | `c869d27376a8d6728795551322fe323b6` | ❌ MALFORMED | ❌ No |
| HuggingFace current main HEAD | `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` | ✅ Valid SHA-1 | ✅ Matches authentic run context |

**Canonical correct revision for all non-manifest code:** `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
