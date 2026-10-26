# 13 Final GPU Authorization Gate

**Status:** AWAITING EXPLICIT PRINCIPAL INVESTIGATOR AUTHORIZATION  
**Cloud Spend to Date:** Strictly $0.0000 USD in Mission 15.5.

---

## 1. Authorization Requirements
Before any physical RunPod instance is provisioned or started:
1. **PI Key Generation:** The Principal Investigator must hold an Ed25519 private key outside the codebase.
2. **Pod Provisioning:** A single RTX 4090 on-demand pod must be provisioned via RunPod console or API.
3. **Payload Signature:** The PI must generate and sign the calibration authorization document binding the exact `target_pod_id`.
4. **Execution Gate:** The signed document must be placed at `research_mission_15_5/auth/calibration_auth_signed.json`.

## 2. Hard Execution Constraints
- No background workers, subagents, or automated scripts may start a pod without this signed artifact.
- Any attempt to bypass the gate or use simulation flags will abort with exit code 2.
