# StateShift Deterministic Reproduction Runbook

This directory contains the self-contained reproduction harness for **StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training** (NeurIPS 2027 Evaluations & Datasets Track).

---

## 1. Distinction Between Reproduction Levels

To ensure transparent scientific reporting, we strictly distinguish four levels of reproduction:

| Level | Definition | Hardware Requirements | Execution Time | Scope in this Package |
|:---|:---|:---:|:---:|:---:|
| **Level A: Statistical Reproduction** | Recomputing all estimands ($\Gamma_t$), bootstrap CIs, cell means, $p$-values, tables, and figures from cryptographically checksummed raw rollout outcomes. | Any modern CPU (x86_64 or ARM64) | $< 3.0$ seconds | **Fully Executable & Automated** (`./run_analysis.sh`) |
| **Level B: Full Model Inference** | Generating the 29,056 raw text completions from scratch using Qwen-2.5-Math-7B and DeepScaleR-1.5B checkpoint weights. | 1x NVIDIA A100-80GB (vLLM engine) | ~5.0 hours (~$12 compute) | Protocol specified in `research_audit/31_EXPERIMENT_PROTOCOLS.md` |
| **Level C: Cached Model Completions** | Validating the generated token text and symbolic equivalence using the SymPy verifier harness. | Modern CPU | ~2 minutes | Automated in test suite |
| **Level D: Synthetic Test Fixtures** | Unit tests validating statistical estimators and PAVA functions against synthetic test vectors. | Modern CPU | $< 1.0$ second | Automated (`./run_tests.sh`) |

> **IMPORTANT**: Running `./run_analysis.sh` executes **Level A** (statistical reproduction from recorded data). It does not re-run 5 hours of GPU generation.

---

## 2. Quickstart Instructions

### Prerequisites:
- Python 3.8+ (tested on Python 3.9, 3.10, 3.13)
- Required packages: `numpy`, `scipy`, `pandas`, `statsmodels`, `pytest`

### Step 1: Install Dependencies
```bash
# Using conda:
conda env create -f environment.yml
conda activate stateshift-repro

# Or using pip:
pip install -r requirements.txt
```

### Step 2: Execute Analysis Pipeline
```bash
./run_analysis.sh
```
This script executes:
1. `validate_environment.py`: Verifies dependencies.
2. `validate_data.py`: Validates SHA-256 checksums and data integrity.
3. `reproduce.py`: Recomputes all headline numbers (Table 1, Table 2, Table 3).
4. `generate_tables_and_figures.py`: Re-verifies all LaTeX tables.

### Step 3: Run Unit Test Suite
```bash
./run_tests.sh
```
Runs 11 unit tests across statistical metrics, bootstrap clustering, natural recovery detection, and order-restricted isotonic regression.
