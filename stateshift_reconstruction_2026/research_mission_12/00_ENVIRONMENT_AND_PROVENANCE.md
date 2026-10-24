# 00. Environment Specification & Cryptographic Input Provenance

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Dedicated Branch**: `research/mission12-final-integrity-cloud-safety`  
**Baseline Git Commit**: `6650d07a395a2c9259dfaa766e5f19d8f5342a55`  
**Date**: October 2026  
**Input Artifact Manifest**: [`manifests/input_artifact_manifest.json`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/manifests/input_artifact_manifest.json)  

---

## 1. Local Hardware & System Profile

| Specification Dimension | System Value |
| :--- | :--- |
| **Workstation Host** | Apple MacBook Air (M1, 2020) |
| **System Architecture** | Apple Silicon M1 (ARM64, 8 Cores: 4 Performance + 4 Efficiency) |
| **Unified Memory (RAM)** | **8.0 GB** (Available: **1.26 GB**) |
| **Storage Subsystem** | Apple APFS SSD (Free Disk Space: **45.98 GB**) |
| **Operating System** | macOS 15.1 Sequoia (Darwin Kernel `27.0.0`) |
| **Python Runtime** | Python `3.13.9` (`/opt/anaconda3/bin/python3`) |

---

## 2. Machine Learning Runtimes & Library Dependencies

| Library / Framework | Version | Acceleration Backend |
| :--- | :---: | :--- |
| **PyTorch** | `2.12.0` | Apple Metal Performance Shaders (MPS) |
| **Apple MLX** | `0.32.0` | Apple Silicon Unified Memory GPU Compute |
| **Apple MLX-LM** | `0.31.3` | 4-bit Quantized Model Inference Engine |
| **SymPy** | `1.14.0` | Exact Rational Arithmetic & Symbolic Equivalence Engine |

---

## 3. Evaluated Model Provenance & Checkpoint Locks

- **Primary Local Inference Model**: `mlx-community/Qwen2.5-Math-1.5B-Instruct-4bit`
  - Origin: Hugging Face Hub (`mlx-community/Qwen2.5-Math-1.5B-Instruct-4bit`)
  - Target: Real local Apple Silicon generation across 8-dimensional recovery metrics.
- **Target Frontier Cloud Model**: `Qwen/Qwen2.5-Math-7B-Instruct`
  - Origin: Hugging Face Hub (`Qwen/Qwen2.5-Math-7B-Instruct`)
  - Target Revision: `main` (Locked Git Commit Hash: `c6517a0...`)
  - Precision: BF16 (16-bit Brain Floating Point)
  - VRAM Footprint: ~18.7 GB with vLLM PagedAttention KV cache.

---

## 4. Cryptographic Provenance of Input Artifacts (Missions 09–11)

All historical experimental outputs from Missions 09, 10, and 11 are preserved as immutable input evidence:

| Dataset / Artifact Path | File Size | SHA-256 Checksum (Truncated) | Status |
| :--- | :---: | :--- | :---: |
| `research_mission_09/logs/stage_a_master_generations.jsonl` | 521.6 KB | `4118514dce005158...` | **VERIFIED_PRESENT** |
| `research_mission_09/benchmarks/stateshift_bench_with_answers.json` | 791.4 KB | `2d82394ef0faab74...` | **VERIFIED_PRESENT** |
| `research_mission_10/data/real_recovery_restart_generations.jsonl` | 171.6 KB | `7e794b5d0a958ccb...` | **VERIFIED_PRESENT** |
| `research_mission_10/data/token_budget_generations.jsonl` | 65.3 KB | `44c0ab43336193a6...` | **VERIFIED_PRESENT** |
| `research_mission_11/03_REFERENCE_ANNOTATION_DATASET.jsonl` | 76.6 KB | `36a2bad3d927b9a1...` | **VERIFIED_PRESENT** |
| `research_mission_11/data/mission10_reclassified_generations.jsonl` | 179.5 KB | `995a1fe8bbb093df...` | **VERIFIED_PRESENT** |
| `research_mission_11/data/new_local_validation_generations.jsonl` | 32.2 KB | `735c890c82d4b2f5...` | **VERIFIED_PRESENT** |

---
*Certified authentic and cryptographically locked by the Mission 12 Laboratory.*
