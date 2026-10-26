# StateShift Mission 15.6: RunPod GPU Execution Launch Package

**Project:** StateShift Research Mission 15.6  
**Document:** `14_RUNPOD_LAUNCH_PACKAGE.md`  
**Purpose:** Exact, reproducible command-line instructions for the human Principal Investigator to authorize, preflight, and execute the physical 10-request GPU calibration on RunPod.

---

## 1. Prerequisites & Environment Verification

Before executing any commands, ensure:
1. Active account balance verified: **~$9.32 USD** (minimum floor **$7.00 USD** must be preserved).
2. Environment variable configured:
   ```bash
   export RUNPOD_API_KEY="your_runpod_api_key_here"
   export PYTHONPATH="."
   ```
3. RunPod GPU Pod provisioned:
   - GPU: **NVIDIA RTX 4090 (24GB)**
   - Container Image: `runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04`
   - Volume: 50 GB container disk
   - Hourly Rate: **$0.89 USD/hour**

---

## 2. Step 1: Generate PI Cryptographic Keypair (One-Time)

Generate the Principal Investigator's Ed25519 signing keypair using Python:

```bash
python3 -c '
from cryptography.hazmat.primitives.asymmetric import ed25519
import base64

priv = ed25519.Ed25519PrivateKey.generate()
pub = priv.public_key()

priv_bytes = priv.private_bytes_raw()
pub_bytes = pub.public_bytes_raw()

with open("pi_private_key.bin", "wb") as f:
    f.write(priv_bytes)

pub_b64 = base64.b64encode(pub_bytes).decode("utf-8")
with open("pi_public_key.txt", "w") as f:
    f.write(pub_b64)

print("Generated PI Keypair!")
print("Public Key (Base64):", pub_b64)
'
```

Export the trusted public key:
```bash
export STATESHIFT_TRUSTED_PUBLIC_KEY=$(cat pi_public_key.txt)
```

---

## 3. Step 2: Sign Calibration Session Authorization

Sign a 30-minute session authorization bound to the active Pod ID:

```bash
python3 -c '
import json, base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from research_mission_15_6.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    FROZEN_MANIFEST_SHA256,
    PINNED_MODEL_ID,
    PINNED_MODEL_REVISION
)

with open("pi_private_key.bin", "rb") as f:
    priv = ed25519.Ed25519PrivateKey.from_private_bytes(f.read())

doc = CryptographicAuthorizer.create_signed_authorization(
    private_key=priv,
    experiment_id="stateshift-calib-real-10",
    manifest_sha256=FROZEN_MANIFEST_SHA256,
    model_id=PINNED_MODEL_ID,
    model_revision=PINNED_MODEL_REVISION,
    pod_id="REPLACE_WITH_YOUR_POD_ID",  # e.g. xydg2t4rzrx71d
    max_spend_usd=0.35,
    emergency_trigger_usd=0.25,
    min_balance_usd=7.00,
    max_runtime_minutes=30,
    authorized_mode="CALIBRATION"
)

with open("calibration_auth_signed.json", "w") as f:
    json.dump(doc, f, indent=2)

print("Cryptographic Authorization Signed Successfully: calibration_auth_signed.json")
'
```

---

## 4. Step 3: Run Free Preflight Verification (Spend: $0.00)

Run the zero-cost preflight check to verify SSH, GPU environment, and manifest validation without launching inference:

```bash
python3 -m research_mission_15_6.runner.stateshift_launch \
    --mode preflight \
    --experiment-id stateshift-calib-real-10 \
    --pod-id REPLACE_WITH_YOUR_POD_ID \
    --ip REPLACE_WITH_POD_IP \
    --port REPLACE_WITH_POD_SSH_PORT \
    --ssh-key ~/.ssh/id_ed25519 \
    --trusted-public-key $STATESHIFT_TRUSTED_PUBLIC_KEY
```

---

## 5. Step 4: Execute Physical 10-Request Calibration (Budget: $0.35)

Execute the physical calibration run via the canonical entry point:

```bash
python3 -m research_mission_15_6.runner.stateshift_launch \
    --mode calibration \
    --experiment-id stateshift-calib-real-10 \
    --pod-id REPLACE_WITH_YOUR_POD_ID \
    --ip REPLACE_WITH_POD_IP \
    --port REPLACE_WITH_POD_SSH_PORT \
    --ssh-key ~/.ssh/id_ed25519 \
    --authorization ./calibration_auth_signed.json \
    --trusted-public-key $STATESHIFT_TRUSTED_PUBLIC_KEY \
    --local-data-dir data/calibration_run \
    --max-cost 0.35 \
    --max-runtime 30.0
```

### What Happens Automatically:
1. Controller validates signed authorization and frozen calibration manifest.
2. Independent OS Financial Watchdog daemon is spawned in a separate process group.
3. Watchdog independently verifies cryptographic signature and clamps spending ceilings ($0.35 max, $0.25 emergency trigger).
4. Code is pushed to pod, environment audited, vLLM v0.6.3 launched with `Qwen2.5-Math-7B-Instruct`.
5. Checkpoints are fetched transactionally via SFTP and promoted monotonically.
6. Once 10 rollouts are achieved, `IndependentDatasetVerifierV2` verifies the physical JSONL dataset.
7. Verification receipt (`verification_receipt.json`) is generated and fsynced.
8. Pod is authoritatively terminated via GraphQL mutation; destruction confirmed.
9. Termination receipt (`termination_receipt.json`) is written.
10. Exit code `0` returned.

---

## 6. Emergency Manual Teardown Protocol

If unexpected network failure occurs or operator wishes to abort instantly:

```bash
python3 -c '
import os, urllib.request, json
api_key = os.environ.get("RUNPOD_API_KEY")
pod_id = "REPLACE_WITH_YOUR_POD_ID"
query = """mutation { podTerminate(input: {podId: \"%s\"}) }""" % pod_id
req = urllib.request.Request(
    f"https://api.runpod.io/graphql?api_key={api_key}",
    data=json.dumps({"query": query}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    print("Manual Termination Response:", resp.read().decode())
'
```
