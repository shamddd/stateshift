# StateShift Deliverable 12: GPU Execution Preflight Specifications

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (github.com/shamddd)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Target Hardware**: 1x NVIDIA RTX 4090 (24 GB VRAM), RunPod Secure Cloud  
**Engine**: vLLM Inference Engine (v0.6.0+)  
**Date**: October 26, 2026  

---

## 1. Executive Summary

This preflight specification defines the immutable runtime configuration, tokenizer mechanics, chat template structure, and container image environment required for physical GPU execution. Every parameter is pinned to guarantee zero-variance scientific reproducibility across runs.

---

## 2. Model & Checkpoint Provenance

- **Hugging Face Model ID**: `Qwen/Qwen2.5-Math-7B-Instruct`
- **Canonical Pinned Revision**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` (Full 40-character commit hash on `refs/heads/main`).
- **Revision Discrepancy Note**: The historical mission prompts referenced a 33-character string (`c869d27376a8d6728795551322fe323b6`), which is malformed. Hugging Face API confirms that `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` is the canonical immutable target. The launch runner will record both strings in the execution receipt to preserve provenance.
- **Precision**: `bfloat16` (native Tensor Core acceleration).
- **KV Cache Allocation**: `gpu_memory_utilization = 0.90` on 24 GB VRAM.

---

## 3. Tokenizer & Chat Template Formatting

Qwen2.5-Math uses the ChatML template. Every request is formatted into standard ChatML turns:

```jinja2
<|im_start|>system
Please reason step by step, and put your final answer within \boxed{}.<|im_end|>
<|im_start|>user
{{ prompt_text }}<|im_end|>
<|im_start|>assistant
```

### Deterministic Generation Parameters:
- `temperature`: `0.0` (Strict argmax greedy decoding)
- `top_p`: `1.0` (Unconstrained by nucleus sampling)
- `top_k`: `-1` (Full vocabulary consideration)
- `max_new_tokens`: `768` (Sufficient for full competition math derivations)
- `seed`: `42`
- `stop_tokens`: `["<|im_end|>", "<|endoftext|>"]`
- `repetition_penalty`: `1.0` (No distortion of mathematical repetition)

---

## 4. Remote Execution Container Environment

The RunPod pod must be provisioned with the official StateShift vLLM container:
- **Base Image**: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
- **Container Disk**: 50 GB (root container volume)
- **Volume Disk**: 0 GB (No persistent billable network storage volumes)
- **Ports**: 22 (SSH), 8000 (vLLM OpenAI-compatible server or direct script runner)
- **Environment Staging Timeout**: Strict 180-second monotonic wall-clock deadline (`safe_channel_wait`).

---

## 5. Preflight Checklist Matrix

| Preflight Check | Specification | Verification Method | Pass Criteria |
|:---|:---|:---|:---|
| **GPU Architecture** | NVIDIA Ada Lovelace (RTX 4090, 24 GB) | `nvidia-smi --query-gpu=name,memory.total` | `NVIDIA GeForce RTX 4090`, $\ge 24,000$ MiB |
| **CUDA Driver** | CUDA 12.4+ | `nvcc --version` | Major version 12 |
| **Model Checkpoint** | `Qwen/Qwen2.5-Math-7B-Instruct` | `git rev-parse HEAD` in cache | `ef9926d...` |
| **Manifest Immutability** | Calibration (10) / Primary (400) | SHA-256 hash check | Exact match against frozen hash |
| **Authorization Token** | Single-use signed Ed25519 token | `CryptographicAuthorizer.verify_authorization` | Valid signature, fresh timestamp, unused nonce |
| **Execution Lock** | Local lock file & env var | `is_cloud_execution_locked()` | Handshake unlocks ONLY for authorized run |
| **Supervisor Active** | Independent watchdog polling | `watchdog_readiness_*.json` | Receipt status `READY`, age $< 30$s |

## 6. Conclusion

The execution preflight specifications eliminate ambiguity and enforce strict hardware, software, and hyperparameter determinism for all future GPU inference runs.
