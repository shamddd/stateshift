# StateShift: Research Mission 19 — Comprehensive Reproducibility Guide

**Date:** October 26, 2026  
**Auditor Committee:** Reproducibility & Research Integrity Directorate  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference / arXiv  
**Document Status:** 100% Cryptographically Audited  

---

## 1. Complete Artifact SHA-256 Ledger

Every empirical artifact used in this research is permanently hashed and recorded below. Any third-party researcher can verify data integrity by computing standard SHA-256 sums.

| Artifact Path | Description | SHA-256 Checksum |
| :--- | :--- | :--- |
| `data/primary_run/primary_100_manifest.json` | Frozen 100-Problem Manifest | `3a8caf3b26b6efae3c7499dca2066f289456e729fc9f6ee4f806ffeb6d649931` |
| `data/primary_run/stateshift_primary_400_generations.jsonl` | Raw GPU Generations (400 outputs) | `6c18f3a8bce06716a13d711d9600a75c1c04f9810168b4ce0e1d88db09a36544` |
| `research_mission_19/data/final_verified_outcomes.csv` | Cleanroom Evaluation Outcomes ($100 \times 4$) | `5f0d57e03403a7a9776f8ebaa4b7cefc801fc78df253a9926fae2dc9eaeb1bb2` |
| `research_mission_19/data/independent_final_statistics.json` | Preregistered Statistical Results | `0d8e2ea5b2cb6dfa99c905b76fc3487c5cf79a8368593d18c21a1be0fa6bc50e` |
| `research_mission_19/data/exact_power_analysis_results.json` | Exact Binomial Discrete Power Results | `a90c58e79870be81137c688325d97f5f903ce8fa6ec7a810b1a0cb8b44917631` |
| `research_mission_19/STATESHIFT_ARXIV_FINAL.tex` | Master LaTeX Manuscript Source | Verified in Git HEAD |
| `research_mission_19/STATESHIFT_ARXIV_FINAL.pdf` | Master Compiled Publication PDF | Verified in Git HEAD |

---

## 2. Experimental Hardware & Software Specifications

### Physical GPU Hardware Environment (RunPod Secure Cloud)
- **GPU:** $1 \times$ NVIDIA GeForce RTX 4090 (24 GB GDDR6X VRAM)
- **Host CPU:** AMD EPYC 7543 32-Core Processor (16 vCPUs allocated)
- **System RAM:** 62 GB System Memory
- **Operating System:** Ubuntu 22.04.4 LTS (Linux 5.15.0-107-generic x86_64)
- **NVIDIA Driver:** 550.90.07 (CUDA 12.4)

### Model & Inference Pipeline
- **Target Foundation Model:** `Qwen/Qwen2.5-Math-7B-Instruct`
- **Pinned Git Revision:** `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
- **Inference Engine:** vLLM `v0.6.3.post1`
- **Decoding Hyperparameters:**
  - Temperature: $T = 0.0$ (Strict greedy decoding)
  - Top-$p$: $1.0$
  - Max New Tokens: $768$
  - Random Seed: $42$

---

## 3. Local One-Click Reproduction Instructions

To reproduce all evaluations, statistical contrasts, exact power curves, and compile the final publication PDF on any local workstation (zero GPU and zero cloud spending required):

### Step 1: Clone Repository & Set Python Environment
```bash
git clone https://github.com/shamddd/stateshift.git
cd stateshift
git checkout research/stateshift-mission19-final-publication
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Re-Run Cleanroom Evaluation Audit
```bash
python3 research_mission_19/scripts/final_evaluation_audit.py
# Outputs:
# - research_mission_19/data/final_verified_outcomes.csv
# - research_mission_19/data/final_evaluation_discrepancies.json
```

### Step 3: Re-Run Exhaustive Paired Statistics & CIs
```bash
python3 research_mission_19/scripts/independent_final_statistics.py
# Recomputes:
# - Exact McNemar p-values
# - Percentile, Basic, BCa, Newcombe, Agresti-Min, and Wald CIs
# - Holm-Bonferroni family-wise control
```

### Step 4: Re-Run Exact Discrete Power Analysis
```bash
python3 research_mission_19/scripts/exact_paired_power.py
# Computes exact discrete binomial power (36.19% at N=100) and sample size requirements (N=231 for 80% power)
```

### Step 5: Re-Generate Figure 5 Vector Graphics
```bash
python3 research_mission_19/scripts/generate_figure5.py
# Generates research_mission_19/figures/figure5_results.pdf and .png
```

### Step 6: Compile arXiv-Ready LaTeX Manuscript
```bash
cd research_mission_19
tectonic STATESHIFT_ARXIV_FINAL.tex
# Compiles STATESHIFT_ARXIV_FINAL.pdf
```

---

## 4. Verification of Fail-Closed Cloud Lock

The repository is permanently locked against unintended cloud expenditures via `.cloud_execution_locked`. Any automated execution script inspects this lock file and aborts with code 1 before initializing any remote API or GPU container.
