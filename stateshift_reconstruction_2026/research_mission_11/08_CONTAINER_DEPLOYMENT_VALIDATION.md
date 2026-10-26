# 08. Container and Deployment Validation Specification

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Containerfile**: [`runpod/Dockerfile`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_11/runpod/Dockerfile)  
**Launcher**: [`runpod/secure_launcher.sh`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_11/runpod/secure_launcher.sh)  
**Test Suite**: [`tests/test_cloud_deployment_and_cost.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_11/tests/test_cloud_deployment_and_cost.py) (16/16 Passing)  

---

## 1. Container Architecture & CUDA Environment

The deployment container builds upon the official PyTorch runtime:
- **Base Image**: `pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime`
- **Linux Distribution**: Ubuntu 22.04 LTS (x86_64)
- **CUDA Runtime**: Version 12.4 with cuDNN 9 acceleration
- **Inference Backends**:
  - Primary: `vLLM >= 0.6.2` (PagedAttention, continuous batching, BF16 tensor parallel)
  - Secondary / Fallback: Hugging Face `transformers >= 4.45.0` + `accelerate >= 0.34.0`
- **Evaluation Stack**: SymPy 1.13, Pandas 2.2, SciPy 1.14

---

## 2. Directory Layout & Persistence Mapping

```
/workspace/
├── cloud_experiment_runner.py       # Main batch execution engine
├── cost_controller.py               # Provider-side lifecycle & spending enforcement
├── termination_watchdog.py          # Independent supervisor daemon
├── secure_launcher.sh               # Root entrypoint with authorization gate
├── benchmark.json                   # Mounted or cloned MATH-500 test set
├── output/
│   ├── b1_results.jsonl             # Atomic rollout persistence
│   └── b1_checkpoint.json           # Resume-state dictionary
└── logs/
    ├── runner.log
    └── watchdog.log
```

---

## 3. Mandatory Local Validation Test Suite

In accordance with Section 10 instructions, all deployment configurations were audited via automated unit tests:

| Test ID | Test Category | Validation Method | Result |
| :---: | :--- | :--- | :---: |
| **TEST-01** | Shell Syntax | `bash -n runpod/secure_launcher.sh` | **PASS** |
| **TEST-02** | Python Imports | Direct import of all runner and controller classes | **PASS** |
| **TEST-03** | Condition Templates | Verified all 4 condition templates (A, D, E, F) | **PASS** |
| **TEST-04** | Benchmark Path | Checked valid JSON on 100 benchmark problems | **PASS** |
| **TEST-05** | Dockerfile Syntax | Verified base image, paths, and entrypoint declarations | **PASS** |
| **TEST-06** | Requirements Check | Verified PyTorch, transformers, vllm, and sympy declarations | **PASS** |
| **TEST-07** | Checkpoint Resume | Created mock rollouts, interrupted, and verified atomic resume | **PASS** |
| **TEST-08** | Environment Isolation| Verified execution blocks when `RUNPOD_AUTHORIZED != TRUE` | **PASS** |

> [!IMPORTANT]
> **Docker Execution Notice**: Because this validation was conducted on an Apple Silicon M1 (arm64) workstation, the x86_64 CUDA container was not built or executed locally. All shell, import, path, and checkpoint logic was verified through local Python and Bash simulation tests. We do NOT claim that the Docker container was built on an actual remote GPU.
