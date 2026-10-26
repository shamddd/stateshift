# StateShift Mission 15.6: Next Action Protocol for Principal Investigator

**Project:** StateShift Research Mission 15.6  
**Document:** `16_NEXT_ACTION.md`  
**Audience:** Sham Satish Thakare, Principal Investigator  
**Action Status:** Ready for Manual Calibration Execution  

---

## 1. Current State of the Codebase

All local production closure tasks for Mission 15.6 are **100% complete**:
- Six critical blockers (Issues A through F) are resolved at the root.
- Canonical production launcher `research_mission_15_6.runner.stateshift_launch` is operational.
- Full regression suite of 234 tests (100% passing in 33.09s) is certified.
- Zero paid cloud execution was conducted ($0.00 spent; account balance intact at $9.3220 USD).
- Deliverables sealed in `research_mission_15_6/`.

---

## 2. Immediate Next Actions for the Principal Investigator

To conduct the first real 10-request GPU calibration on RunPod:

### Step 1: Provision an On-Demand RTX 4090 Pod
1. Log into RunPod console: `https://www.runpod.io/console/pods`.
2. Deploy an On-Demand RTX 4090 ($0.89/hr).
3. Image: `runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04`.
4. Disk: 50GB container disk.
5. Note down:
   - **Pod ID** (e.g. `xydg2t4rzrx71d`)
   - **IP Address** and **Port** (Forwarded SSH port)

### Step 2: Generate Keypair & Sign Calibration Authorization
Follow the exact script in `research_mission_15_6/14_RUNPOD_LAUNCH_PACKAGE.md`:
```bash
# 1. Generate PI keypair
python3 -c '... (see Section 2 of 14_RUNPOD_LAUNCH_PACKAGE.md)'

# 2. Export trusted key
export STATESHIFT_TRUSTED_PUBLIC_KEY=$(cat pi_public_key.txt)

# 3. Sign authorization bound to active pod ID
python3 -c '... (see Section 3 of 14_RUNPOD_LAUNCH_PACKAGE.md)'
```

### Step 3: Run Free Preflight Verification
```bash
python3 -m research_mission_15_6.runner.stateshift_launch \
    --mode preflight \
    --experiment-id stateshift-calib-real-10 \
    --pod-id <POD_ID> \
    --ip <IP> \
    --port <PORT> \
    --ssh-key ~/.ssh/id_ed25519 \
    --trusted-public-key $STATESHIFT_TRUSTED_PUBLIC_KEY
```

### Step 4: Launch Physical Calibration (Budget: $0.35)
```bash
python3 -m research_mission_15_6.runner.stateshift_launch \
    --mode calibration \
    --experiment-id stateshift-calib-real-10 \
    --pod-id <POD_ID> \
    --ip <IP> \
    --port <PORT> \
    --ssh-key ~/.ssh/id_ed25519 \
    --authorization ./calibration_auth_signed.json \
    --trusted-public-key $STATESHIFT_TRUSTED_PUBLIC_KEY \
    --local-data-dir data/calibration_run \
    --max-cost 0.35
```

---

## 3. What to Expect Upon Completion

1. The experiment will run for approximately 8–12 minutes.
2. The independent watchdog will enforce the strict $0.25 emergency trigger and $0.35 ceiling.
3. Upon completing 10 rollouts, the pod will be destroyed authoritatively and confirmed via GraphQL.
4. Final verified dataset and receipts will be stored in `data/calibration_run/`.
5. Expected spend will be $\approx \$0.15\text{--}\$0.20$ USD, leaving $\approx \$9.12\text{--}\$9.17$ USD in your account (well above the $7.00 preservation floor).
