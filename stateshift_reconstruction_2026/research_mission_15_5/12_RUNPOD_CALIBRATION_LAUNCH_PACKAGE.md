# 12 RunPod Calibration Launch Package

**Target Execution:** 10-Rollout Calibration Gate  
**Model:** `Qwen/Qwen2.5-Math-7B-Instruct`  
**Revision:** `c869d27376a8d6728795551322fe323b6`  
**Max Spend:** $0.3500 USD | **Emergency Trigger:** $0.2500 USD  

---

## 1. Remote Environment Specification
- **Base Image:** `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
- **GPU Architecture:** NVIDIA RTX 4090 (24 GB VRAM)
- **Container Disk:** 40 GB | **Volume Disk:** 20 GB
- **Inference Engine:** `vllm==0.6.3` with fallback to `transformers==4.45.2`
- **Decoding Configuration:** Pinned greedy decoding (`temperature=0.0`, `seed=42`, `max_tokens=768`).

## 2. Launch Invocation Command (Template)
```bash
python3 research_mission_15_5/runner/stateshift_production_runner_v10.py \
  --mode CALIBRATION \
  --authorization research_mission_15_5/auth/calibration_auth_signed.json \
  --manifest research_mission_15_5/manifests/primary_100_manifest.json \
  --pod-id <PROVISIONED_POD_ID> \
  --ip <PROVISIONED_POD_IP> \
  --port <SSH_PORT> \
  --ssh-key-path ~/.ssh/id_ed25519 \
  --local-data-dir research_mission_15_5/data/calibration \
  --max-cost-usd 0.35 \
  --poll-interval 1.0
```
