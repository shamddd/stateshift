# StateShift Mission 15.3: Session-Specific Authorization Protocol

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_3/04_SESSION_SPECIFIC_AUTHORIZATION.md`  

---

## 1. Vulnerability of Static Authorization Tokens

In Mission 15.2 and earlier iterations, production execution authorization was verified by checking if `--authorization-token` was present as a non-empty string:
```python
# DEFECTIVE IN 15.2:
if not self.authorization_token:
    raise PermissionError("PRODUCTION mode requires an explicit non-empty authorization_token.")
```
This check had three fatal security and operational flaws:
1. **Arbitrary Token Acceptance**: Any random string (e.g. `foo`, `test`, `yes`) satisfied the condition and allowed production execution.
2. **Reusability & Leakage Risk**: The documented sample string `STATESHIFT_AUTH_PI_SHAM_THAKARE_2026` was published in reports and shell scripts, turning it into a static, permanently valid bypass token.
3. **Unbound Scope**: The token was completely disconnected from the actual pod ID, manifest cryptographic hash, model revision, spending limits, and expiration time.

---

## 2. Session-Specific Cryptographic Approval Architecture

Mission 15.3 replaces static strings with an immutable, session-bound JSON authorization document enforced by `SessionAuthorizer` (`research_mission_15_3/auth/session_authorizer.py`).

### Mandatory Authorization Schema
```json
{
  "approval_status": "APPROVED",
  "experiment_id": "stateshift_400_replication_2026",
  "principal_investigator": "Sham Satish Thakare",
  "created_at_utc": 1774329600.0,
  "expires_at_utc": 1774336800.0,
  "authorized_execution_modes": ["PRODUCTION"],
  "manifest_sha256": "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
  "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
  "model_revision": "c869d27376a8d6728795551322fe323b6",
  "pod_id": "xydg2t4rzrx71d",
  "max_authorized_incremental_usd": 2.00,
  "min_account_balance_floor_usd": 7.00,
  "max_runtime_minutes": 160.0,
  "pi_signature_digest": "HMAC_OR_SHA256_AUTHENTICATION_DIGEST"
}
```

---

## 3. Mandatory Security Verification Gates

Before the production runner opens any socket to RunPod or dispatches any command, `SessionAuthorizer.validate_authorization()` executes 10 strict checks:

1. **Explicit Approval Status**: Must equal `"APPROVED"`. Any template, draft, or unsigned status immediately halts execution.
2. **Time-to-Live (TTL) Expiration**: Current UTC timestamp must be $\le \text{expires\_at\_utc}$. Expired authorizations are rejected.
3. **Experiment ID Binding**: Must strictly match the runner's configured `--experiment-id`.
4. **Pod ID Binding**: In `PRODUCTION` mode, must strictly match the provisioned `--pod-id`. Prevents reusing an authorization for another or accidental pod.
5. **Manifest Cryptographic Binding**: Must match both the constant frozen manifest hash (`3a8caf3b...4307d`) and the active manifest file hash.
6. **Model & Weights Revision Binding**: Must match `Qwen/Qwen2.5-Math-7B-Instruct` and git commit revision `c869d27376a8d6728795551322fe323b6`.
7. **Incremental Financial Ceiling**: Max spend must not exceed the runner limit (\$2.00) or remaining campaign headroom (\$2.3575).
8. **Preservation Floor Enforcement**: The minimum balance floor must be $\ge \$7.0000$.
9. **Execution Mode Whitelisting**: Active mode (`PRODUCTION`, `PREFLIGHT`, or `DRY_RUN`) must be explicitly present in `authorized_execution_modes`.
10. **Principal Investigator Identity**: Must match `"Sham Satish Thakare"`.

---

## 4. Unsigned Example Template

In compliance with the mission instructions:
- The committed file `research_mission_15_3/auth/example_session_authorization.json` has `approval_status = "UNSIGNED_TEMPLATE_NOT_VALID_FOR_EXECUTION"`.
- It explicitly fails validation and cannot be used to run a cloud GPU.
- Genuine execution requires the Principal Investigator to sign and issue a real session document immediately prior to pod launch.
