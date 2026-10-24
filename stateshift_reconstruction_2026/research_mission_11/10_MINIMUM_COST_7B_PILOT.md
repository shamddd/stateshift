# 10. Minimum-Cost 7B Cloud Pilot Specification

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Status**: Prepared and Ready for Authorization (Zero Cloud Spend Incurred)  

---

## 1. Primary Model Provenance

- **Hugging Face Model ID**: `Qwen/Qwen2.5-Math-7B-Instruct`
- **Revision / Branch**: `main` (Locked commit hash: `c6517a0...`)
- **Parameters**: 7.61 Billion
- **Precision**: BF16 (16-bit Brain Floating Point)
- **VRAM Footprint**: ~15.2 GB (Weights) + ~3.5 GB (KV Cache under PagedAttention) $\approx$ **18.7 GB Peak VRAM** (Fits comfortably within 24 GB VRAM on NVIDIA RTX 4090 / RTX 3090 / A40).

---

## 2. Pilot Experimental Design ($N=40$ Rollouts)

Rather than risking an uncalibrated 100-problem execution, the research protocol mandates a **10-problem pilot** across all 4 experimental conditions:

```
[10 Held-Out MATH-500 Problems]
               │
               ├── Condition A: Zero-Shot Baseline           (10 Rollouts)
               ├── Condition D: Forced Restart               (10 Rollouts)
               ├── Condition E: Explicit Local Repair        (10 Rollouts)
               └── Condition F: State-Preserving Repair      (10 Rollouts)
               │
               ▼
     Total: 40 Model Generations (Max Tokens: 768, Temp: 0.0, Seed: 42)
```

### Measured Engineering Objectives:
1. **Container Startup & Download Latency**: Measure time to clone repo, pull weights from Hugging Face cache, and initialize vLLM engine.
2. **Empirical Throughput**: Measure tokens/second during multi-step mathematical reasoning on NVIDIA RTX 4090.
3. **Peak Memory Consumption**: Verify that KV cache allocation does not exceed 90% GPU memory.
4. **Actual Financial Burn**: Verify elapsed time and billing increments against the RunPod API.

---

## 3. Runtime & Cost Projections for 10-Problem Pilot

| Phase / Component | Estimated Duration | GPU Resource | Hourly Rate | Estimated Cost (USD) |
| :--- | :---: | :---: | :---: | :---: |
| **Model Weights Download** | 3.5 – 5.0 min | Network / Disk | $0.34 / hr | $0.02 – $0.03 |
| **vLLM Initialization** | 1.0 – 1.5 min | RTX 4090 (24 GB) | $0.34 / hr | $0.01 – $0.01 |
| **40 Rollouts Generation** | 7.0 – 9.0 min | RTX 4090 (~45 t/s) | $0.34 / hr | $0.04 – $0.05 |
| **Evaluator v3 Execution** | 0.5 – 1.0 min | CPU Core | $0.34 / hr | $0.00 – $0.01 |
| **Output Upload & Clean Termination** | 1.0 – 2.0 min | Pod API | $0.34 / hr | $0.01 – $0.01 |
| **Buffer / Setup Overhead** | 5.0 min | Pod Warmup | $0.34 / hr | $0.03 – $0.03 |
| **Total Estimated Pilot Cost** | **~18 – 23 minutes** | **1 $\times$ RTX 4090** | **$0.34 / hr** | **$0.11 – $0.15** |

> [!TIP]
> **Total Financial Exposure**: Even under conservative estimates with network delays, the total pilot cost is bounded at **less than \$0.25**.

---

## 4. Execution Readiness & Safety Lock

The pilot will NOT be launched until:
1. Sham Satish Thakare provides explicit written approval.
2. The user exports `RUNPOD_AUTHORIZED=TRUE` and valid credentials into the session.
3. The budget watchdog limit is set to `$0.50` maximum spend.
