# StateShift: Operator's Guide to Physical RunPod Calibration

**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Experiment**: 10-Request Physical Hardware Calibration (Qwen2.5-Math-7B-Instruct)  
**Hardware Target**: RunPod Community or Secure Cloud RTX 4090 ($0.89/hr or less)  
**Total Authorized Spending Envelope**: **$0.35 USD Max / $0.25 USD Emergency Trigger**  

---

## 1. Prerequisites Checklist

Before executing the launch command, verify the following prerequisites:

1. **Active RunPod Account Balance**:
   - Current balance must be **$\ge \$7.50\text{ USD}$** (to remain comfortably above the **$7.00 USD preservation floor**).
2. **Environment Variable**:
   ```bash
   export RUNPOD_API_KEY="your_runpod_api_key_here"
   ```
3. **SSH Key Pair**:
   - A valid ed25519 or RSA private key on local disk (e.g. `~/.ssh/id_ed25519`).
   - The corresponding public key configured in your RunPod account settings.
4. **Provisioned Pod Details**:
   - Rent a pod with template `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04` or similar vLLM-compatible image on an RTX 4090 GPU.
   - Note down:
     - `POD_ID` (e.g. `xydg2t4rzrx71d`)
     - `POD_IP` (e.g. `64.226.120.14`)
     - `SSH_PORT` (e.g. `22045`)

---

## 2. Step 1: Generate Cryptographically Signed Authorization Document

Run the authorizer utility to produce the signed authorization file:

```bash
python -c "
import json
from cryptography.hazmat.primitives.asymmetric import ed25519
from research_mission_15_6.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    FROZEN_MANIFEST_SHA256,
    PINNED_MODEL_ID,
    PINNED_MODEL_REVISION
)

# Load your operator private key or generate a designated session key:
priv = ed25519.Ed25519PrivateKey.generate()
pub_b64 = CryptographicAuthorizer(allow_test_key_for_testing=True)._serialize_public_key(priv.public_key())

doc = CryptographicAuthorizer.create_signed_authorization(
    private_key=priv,
    experiment_id='stateshift-calibration-10',
    manifest_sha256=FROZEN_MANIFEST_SHA256,
    model_id=PINNED_MODEL_ID,
    model_revision=PINNED_MODEL_REVISION,
    pod_id='YOUR_POD_ID',
    max_spend_usd=0.35,
    emergency_trigger_usd=0.25,
    min_balance_usd=7.00,
    authorized_mode='CALIBRATION',
    validity_seconds=3600.0
)

with open('data/primary_run/session_auth.json', 'w') as f:
    json.dump(doc, f, indent=2)

with open('data/primary_run/operator_pubkey.txt', 'w') as f:
    f.write(pub_b64)

print('Authorization document generated at data/primary_run/session_auth.json')
print('Public key stored at data/primary_run/operator_pubkey.txt')
"
```

---

## 3. Step 2: Launch the Canonical Runner

Execute the canonical entry point:

```bash
python -m research_mission_15_6.runner.stateshift_launch \
  --mode calibration \
  --experiment-id stateshift-calibration-10 \
  --pod-id YOUR_POD_ID \
  --ip YOUR_POD_IP \
  --port YOUR_SSH_PORT \
  --ssh-key ~/.ssh/id_ed25519 \
  --authorization data/primary_run/session_auth.json \
  --trusted-public-key data/primary_run/operator_pubkey.txt \
  --max-cost 0.35 \
  --max-runtime 15.0
```

---

## 4. Execution Sequence & Automatic Protections

When launched, the system will autonomously execute the following strictly gated lifecycle:

1. **Manifest Validation**: Verifies `calibration_10_manifest.json` matches frozen SHA-256 and contains all 10 frozen requests.
2. **Authorization Verification**: Verifies Ed25519 digital signature, pod ID binding, and enforces budget caps ($0.35 max, $0.25 trigger).
3. **Provider Handshake**: Queries RunPod API to verify pod `YOUR_POD_ID` is in `RUNNING` status and extracts pre-existing uptime.
4. **Independent Watchdog Spawn**: Launches decoupled OS process (PID distinct from controller).
5. **Mandatory 12-Point Startup Handshake**: Blocks until watchdog publishes verified readiness receipt and proves active aliveness.
6. **Remote Deployment**: Transfers `remote_experiment_runner.py` and calibration manifest to `/workspace/stateshift_run` via SFTP.
7. **Streaming Inference**: Runs Qwen2.5-Math-7B-Instruct across the 10 frozen requests. Checkpoints are synchronized incrementally.
8. **Independent Dataset Verification**: Checks all 10 records for non-emptiness, valid reasoning traces, parsed answers, and exact prompt alignment.
9. **Priority-1 Pod Destruction**: Dispatches pod termination to RunPod, polls for confirmed deletion, records final verified receipts, and cleanly terminates.

---

## 5. Contingency Operations & Emergency Handling

- **Spend Breach**: If spend hits **$0.25 USD**, watchdog immediately terminates the pod.
- **Balance Floor Breach**: If RunPod balance drops to **$\le \$7.00 USD**, watchdog immediately terminates the pod.
- **Unconfirmed Provider Termination**: If RunPod returns HTTP 500/503 during deletion, the runner transitions to `TERMINATION_UNCONFIRMED` and **leaves the watchdog running**.
  - To manually assume control: check RunPod web console to terminate pod, then create:
    ```bash
    echo '{"operator": "human", "action": "pod_destroyed_manually"}' > data/primary_run/watchdog/operator_handoff_YOUR_POD_ID.json
    ```
    The watchdog will detect this file and exit cleanly.
