# StateShift Mission 15.3: RunPod Execution Package & Deployment Guide

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_3/10_RUNPOD_EXECUTION_PACKAGE.md`  

---

## 1. Cloud Environment Specification

| Component | Target Specification | Minimum Version / Requirement |
|:---|:---|:---|
| **GPU Hardware** | NVIDIA GeForce RTX 4090 (24 GB VRAM) | Minimum 24 GB VRAM (FP16/BF16 weights) |
| **Cloud Provider** | RunPod Secure Cloud (or Community Cloud with High Availability) | Hourly rate: \$0.89 / hour |
| **Container Image** | `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04` | Pre-configured CUDA 12.4 and PyTorch |
| **Python Runtime** | Python 3.10 or 3.11 | Python >= 3.10 |
| **PyTorch & CUDA** | `torch >= 2.4.0` with CUDA 12.1+ support | Native bfloat16 capability |
| **Inference Engines** | `vllm >= 0.6.3.post1` with fallback to `transformers >= 4.46.0` | FlashAttention / PagedAttention |
| **Container Storage** | 40 GB Container Disk + 20 GB Volume Disk | Sufficient for 14.5 GB model weights |
| **Network Egress** | Minimum 500 Mbps connection | Fast HuggingFace weight downloading |

---

## 2. Step-by-Step Cloud Deployment Protocol

### Step 1: Provision the Cloud Pod
1. Log in to [RunPod Console](https://www.runpod.io/console/pods).
2. Select **RTX 4090 (24 GB VRAM)**. Verify on-demand rate is **\$0.89/hr** or lower.
3. Select Container Image: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`.
4. Set Container Disk: `40 GB`, Volume Disk: `20 GB` (Mount path: `/workspace`).
5. Ensure your public SSH key (`~/.ssh/id_ed25519.pub`) is registered in your RunPod account settings.
6. Note the assigned **Pod ID** (e.g. `xydg2t4rzrx71d`), **Public IP**, and **SSH Port**.

### Step 2: Establish Secure SSH Connectivity
Test connectivity from local terminal:
```bash
ssh -i ~/.ssh/id_ed25519 root@<POD_PUBLIC_IP> -p <POD_SSH_PORT> "nvidia-smi"
```

### Step 3: Upload Experiment Code & Manifest
Upload the self-contained Mission 15.3 directory:
```bash
rsync -avz -e "ssh -i ~/.ssh/id_ed25519 -p <POD_SSH_PORT>" \
  research_mission_15_3/ \
  root@<POD_PUBLIC_IP>:/workspace/stateshift/
```

### Step 4: Run Read-Only Cloud Preflight
Execute the preflight mode on local Mac to test all provider APIs without launching GPU inference:
```bash
export RUNPOD_API_KEY="<YOUR_RUNPOD_API_KEY>"

python3 research_mission_15_3/runner/stateshift_production_runner.py \
  --mode PREFLIGHT \
  --authorization path/to/signed_session_authorization.json \
  --manifest research_mission_15_3/manifests/primary_100_manifest.json \
  --pod-id "<POD_ID>" \
  --ip "<POD_PUBLIC_IP>" \
  --port <POD_SSH_PORT> \
  --ssh-key-path ~/.ssh/id_ed25519
```

---

## 3. Production Execution Commands

### A. Local CPU Dry Run (No Cloud Action, $0.00 Spend)
```bash
python3 research_mission_15_3/runner/stateshift_production_runner.py \
  --mode DRY_RUN \
  --manifest research_mission_15_3/manifests/primary_100_manifest.json \
  --local-data-dir research_mission_15_3/data/primary_run \
  --simulate-records 400
```

### B. Authorized Live Cloud Production Launch
*(Execute only after explicit PI authorization)*
```bash
export RUNPOD_API_KEY="<YOUR_RUNPOD_API_KEY>"

python3 research_mission_15_3/runner/stateshift_production_runner.py \
  --mode PRODUCTION \
  --authorization research_mission_15_3/auth/signed_session_authorization.json \
  --manifest research_mission_15_3/manifests/primary_100_manifest.json \
  --pod-id "<RUNPOD_POD_ID>" \
  --ip "<POD_PUBLIC_IP>" \
  --port <POD_SSH_PORT> \
  --ssh-key-path ~/.ssh/id_ed25519 \
  --local-data-dir research_mission_15_3/data/primary_run \
  --remote-work-dir /workspace/stateshift \
  --max-cost-usd 2.00 \
  --max-runtime-minutes 160.0 \
  --gpu-hourly-rate 0.89
```

### C. Live Progress Monitoring
```bash
# Monitor runner progress from local machine
tail -f research_mission_15_3/data/primary_run/runner_state_stateshift_400_replication_2026.json

# Check remote process log via SSH
ssh -i ~/.ssh/id_ed25519 root@<IP> -p <PORT> "tail -f /workspace/stateshift/logs/runner.log"
```

### D. Manual Emergency Pod Termination
```bash
# Via GraphQL Curl
curl -X POST https://api.runpod.io/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -d '{"query": "mutation { podTerminate(input: {podId: \"<RUNPOD_POD_ID>\"}) }"}'
```

---

## 4. Recovery Procedures

- **SSH Disconnection**: The remote runner runs inside `nohup` in the background. The local supervisor automatically reconnects on the next polling tick and resumes intermediate syncing.
- **Local Mac Sleep or Terminal Closure**: Upon reopening terminal, run the runner command with `--resume`. The runner reads `runner_state_*.json`, re-attaches to the remote PID, and resumes without duplicating rollouts.
- **Provider Outage**: If the provider cannot confirm termination, `DurableEscalationManager` writes `CRITICAL_ALERT_POD_<id>.txt` with manual instructions. Use the RunPod web UI or CLI to terminate the pod manually.

---

## 5. Pre-Launch Verification Checklist

Before issuing the production launch command, verify:
- [ ] Account balance re-checked: Live balance $\ge \$9.00$ USD.
- [ ] Account preservation floor confirmed: $\$7.00$ USD intact.
- [ ] Session authorization document signed by PI Sham Satish Thakare.
- [ ] Authorization document parameters match active pod ID, manifest hash, and budget.
- [ ] Preflight check passed with zero errors.
- [ ] SSH key tested and working.
