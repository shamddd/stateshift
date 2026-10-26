# StateShift: Complete Scientific Reproducibility Guide

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training

---

## 1. System Requirements & Environment

* **Supported Operating Systems**: Linux (Ubuntu 20.04+, Debian 11+), macOS (13.0+, Apple Silicon or Intel).
* **Python Runtime**: Python 3.10, 3.11, 3.12, or 3.13.
* **Core Dependencies**:
  * `numpy >= 1.24.0`
  * `pandas >= 2.0.0`
  * `scipy >= 1.10.0`
  * `pytest >= 8.0.0`
* **LaTeX Compiler (Optional for PDF generation)**:
  * `tectonic >= 0.15.0` (Recommended) or `xelatex` / `pdflatex`.

---

## 2. Installation & Quickstart

Clone the repository and install the reproduction dependencies in a virtual environment:

```bash
# Clone the repository
git clone https://github.com/shamddd/stateshift.git
cd stateshift

# Create and activate a clean virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required numerical and statistical packages
pip install --upgrade pip
pip install numpy pandas scipy pytest
```

---

## 3. Dataset Registry & Verification

Before running evaluations, verify the cryptographic integrity of the empirical datasets:

```bash
# Verify Study 1 dataset
shasum -a 256 data/study1/controlled_endpoint_outcomes.csv
# Expected: 49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139

# Verify Study 2 raw generations
shasum -a 256 data/study2/stateshift_primary_400_generations.jsonl
# Expected: bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2

# Verify Study 2 verified outcome matrix
shasum -a 256 data/study2/final_verified_outcomes.csv
# Expected: 19a328a95dd25ec326fe824361386cc0ddf731f2bf1c392253be0aa19c2385ba
```

---

## 4. Reproducing Empirical Results (CPU-Only)

All statistical estimands, p-values, contingency tables, and power analyses can be fully reproduced on a standard CPU within seconds. Zero GPU resources are required.

### 4.1 Reproduce Study 1 (Checkpoint-Lineage Analysis)
```bash
python experiments/study1_checkpoint_lineage/reproduce_study1.py
```
**Expected Output**:
* Checkpoint 0 Control: $38.92\%$, Recovery: $38.34\%$
* Checkpoint 256 Control: $59.21\%$, Recovery: $70.39\%$
* **Interaction Estimand ($\Gamma_{256}$)**: $+11.76\text{ percentage points}$
* **Clustered Standard Error**: $0.0114$ ($t = 10.34$, $p = 1.05 \times 10^{-22}$)
* **TOST Length Equivalence**: Confirmed equivalent at $[-5, +5]$ token margin ($p = 0.0256$)

---

### 4.2 Reproduce Study 2 (Physical GPU Experiment & Exact McNemar)
```bash
python experiments/study2_reasoning_recovery/reproduce_study2.py
```
**Expected Output**:
* Condition A (Zero-Shot Baseline): **$64.00\%$** ($64/100$)
* Condition D (No-Intervention Control): **$67.00\%$** ($67/100$)
* Condition E (Lemma Scaffold Control): **$71.00\%$** ($71/100$)
* Condition F (Full State Restoration): **$73.00\%$** ($73/100$)
* **Treatment Contrast ($\hat{\tau}_{F-D}$)**: **$+6.00\text{ percentage points}$**
* **Contingency Matrix**: $a=65, b=8, c=2, d=25$
* **Off-Diagonal Odds Ratio**: **$4:1$** ($b/c = 4.00$)
* **Exact Discrete McNemar Two-Sided p-value**: **$0.109375$** (Under $\alpha=0.05$, not statistically significant)
* **Exact Discrete McNemar One-Sided p-value**: **$0.054688$**
* **Baseline Contrast ($\hat{\tau}_{F-A}$)**: **$+9.00\text{ percentage points}$** ($p = 0.0117$, significant)

---

### 4.3 Reproduce Exact Discrete Power & Sample Size Grid
```bash
python experiments/study2_reasoning_recovery/exact_power_analysis.py
```
**Expected Output**:
* Pilot Power ($N=100$): **$36.20\%$** (Type II Error $\beta = 63.80\%$)
* Confirmatory Sample Size for $80\%$ Power: **$N = 231$** ($80.07\%$)
* Confirmatory Sample Size for $90\%$ Power: **$N = 299$** ($90.02\%$)
* Winner's Curse Shrinkage ($\delta = +0.05$ at $q=0.10$): **$N = 337$** for $80\%$ power

---

## 5. Paper Compilation

To compile the LaTeX source candidate into a PDF locally using Tectonic:

```bash
cd paper
tectonic STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex
```
* Generates: `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf` ($193.21\text{ KB}$, 14 pages).

---

## 6. Automated Testing

Execute the test suite to verify data schemas, regression equations, and hash consistency:

```bash
pytest -q
```
* Expected: All tests pass with zero failures.

---

## 7. Known Scientific & Provenance Limitations

1. **Study 1 Rollout Traces**: While the 29,056 outcome records are preserved in `data/study1/controlled_endpoint_outcomes.csv`, original free-form text completions are unavailable.
2. **Study 2 Sample Size**: The initial physical GPU trial ($N=100$) is powered at $36.20\%$ for $\delta = +0.06$. The primary comparison ($p = 0.1094$) is not statistically significant at $\alpha = 0.05$. An independent confirmatory trial ($N = 231$) is recommended.
3. **Model Specificity**: All physical experiments were executed on `Qwen/Qwen2.5-Math-7B-Instruct`. Cross-model generalizability requires further empirical validation.
