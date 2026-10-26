# 13. RunPod Cloud Authorization Checklist & Safety Gate

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Status**: **LOCKED — AWAITING EXPLICIT WRITTEN AUTHORIZATION**  

---

## 1. Zero-Spend Verification

As of the conclusion of Research Mission 11:
- **Total Paid Cloud Computing Executed**: **$0.00**
- **Active RunPod Pods**: **0**
- **Allocated Cloud Storage Volumes**: **0**
- **All experiments to date have executed strictly on the local Apple Silicon M1 workstation.**

---

## 2. Mandatory Pre-Flight Authorization Checklist

Before any cloud GPU instance is provisioned, Principal Investigator Sham Satish Thakare must review and approve each parameter below:

| Parameter | Recommended Specification | Status | Principal Investigator Approval |
| :--- | :--- | :---: | :---: |
| **Target GPU Model** | 1 $\times$ NVIDIA GeForce RTX 4090 (24 GB VRAM) | Verified | [ ] APPROVED |
| **Hourly Pricing Cap** | Maximum $0.34 / hour (Community/Secure Spot) | Verified | [ ] APPROVED |
| **Experiment Scope** | 10-Problem Pilot ($N=40$ Rollouts, 4 Conditions) | Frozen | [ ] APPROVED |
| **Model ID & Revision** | `Qwen/Qwen2.5-Math-7B-Instruct` (Revision `main`) | Locked | [ ] APPROVED |
| **Maximum Pod Runtime** | 45 minutes hard timeout (`MAX_RUNTIME_MINUTES=45`) | Enforced | [ ] APPROVED |
| **Maximum Spend Limit** | **$0.50 USD hard financial ceiling** (`MAX_BUDGET_USD=0.50`) | Enforced | [ ] APPROVED |
| **Output Destination** | Local Git workspace / Git branch | Configured | [ ] APPROVED |
| **Provider-Side Kill Trap**| Authenticated RunPod GraphQL `podTerminate` mutation | Tested | [ ] APPROVED |

---

## 3. Activation Command Sequence

When authorized, the Principal Investigator will supply the necessary environment variables in a single terminal session:

```bash
# STEP 1: Provide temporary runtime credentials (session only)
export RUNPOD_API_KEY="<YOUR_RUNPOD_API_KEY>"
export HF_TOKEN="<YOUR_HF_TOKEN>"

# STEP 2: Explicitly unlock the safety authorization gate
export RUNPOD_AUTHORIZED="TRUE"
export MAX_BUDGET_USD="0.50"
export MAX_RUNTIME_MINUTES="45"

# STEP 3: Dispatch single audited pod via RunPod CLI
runpodctl create pod \
  --name "stateshift-7b-pilot" \
  --gpu-type "NVIDIA GeForce RTX 4090" \
  --gpu-count 1 \
  --image "pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime" \
  --volume-in-gb 40 \
  --env HF_TOKEN="$HF_TOKEN" \
  --env RUNPOD_API_KEY="$RUNPOD_API_KEY" \
  --env RUNPOD_AUTHORIZED="TRUE" \
  --env MAX_BUDGET_USD="0.50" \
  --env MAX_RUNTIME_MINUTES="45" \
  --cmd "bash -c 'git clone https://github.com/shamddd/stateshift.git /workspace/stateshift && cd /workspace/stateshift && bash research_mission_11/runpod/secure_launcher.sh'"
```

> [!CAUTION]
> Under no circumstances will Antigravity execute the above command without explicit written instructions containing the phrase **"AUTHORIZE RUNPOD EXECUTION"**.
