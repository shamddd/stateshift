# StateShift Deliverable 17: Reproducibility Rehearsal & Verification Protocol

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (github.com/shamddd)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Date**: October 26, 2026  

---

## 1. Executive Summary

Scientific reproducibility is the core invariant of the StateShift project. This document provides an executable step-by-step reproduction guide that allows any independent auditor, reviewer, or researcher to replicate all local engineering, statistical, evaluation, and manuscript artifacts on CPU without spending a single cloud dollar ($0.00).

---

## 2. Environment Setup & Dependency Installation

### 2.1. System Requirements
- OS: macOS (Apple Silicon or Intel) or Linux (Ubuntu 22.04+).
- Python: Version 3.10+ (tested and certified on Python 3.13.9).
- TeX Engine: `tectonic` v0.15.0+ (or standard `pdflatex` / `xelatex`).

### 2.2. Python Environment Installation
```bash
# Clone repository
git clone https://github.com/shamddd/stateshift.git
cd stateshift
git checkout research/stateshift-final-preexperiment-validation

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install pytest pytest-cov cryptography sympy numpy scipy paramiko requests
```

---

## 3. Step-by-Step Rehearsal Execution

### Step 1: Manifest Integrity & Cryptographic Hash Audit
Verify that the frozen experimental manifests match the official cryptographic hashes:
```bash
python3 -c "
import hashlib, json
def verify_hash(path, expected):
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    assert h == expected, f'MISMATCH: {h} != {expected}'
    print(f'OK: {path} -> {h}')

verify_hash('research_mission_15_6/manifests/primary_100_manifest.json',
            '3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d')
verify_hash('research_mission_15_6/manifests/calibration_10_manifest.json',
            'f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6')
print('ALL MANIFESTS CRYPTOGRAPHICALLY VERIFIED.')
"
```

### Step 2: Complete Automated Test Battery Rehearsal
Execute the full suite of 82 automated regression, recovery, defect fix, adversarial, simulation, and evaluation tests:
```bash
python3 -m pytest -v research_mission_15_6/tests/
```
**Expected Outcome**: **82 passed in ~20 seconds** (0 failures, 0 warnings).

### Step 3: Math Evaluation Pipeline Rehearsal
Verify that the mathematical answer extractor, LaTeX normalizer, SymPy algebraic checker, and statistical bootstrap engine operate deterministically:
```bash
python3 -c "
from research_mission_15_6.evaluation.math_answer_evaluator import (
    extract_boxed_answer, is_answer_correct, paired_bootstrap_ci, mcnemar_test
)
# Test extraction
ans = extract_boxed_answer('Therefore, \\boxed{\\frac{3\\sqrt{2}}{5}}.')
assert ans == '\\frac{3\\sqrt{2}}{5}'

# Test equivalence
assert is_answer_correct('0.5', '\\frac{1}{2}') is True
assert is_answer_correct('x + y', 'y + x') is True

# Test McNemar
res = mcnemar_test([1]*25 + [0]*5, [0]*25 + [1]*5)
assert res['p_value'] < 0.001
print('EVALUATION ENGINE FULLY OPERATIONAL.')
"
```

### Step 4: Deterministic Incident Replay Rehearsal
Verify that the repaired architecture intervenes at $\le \$0.045$ and preserves the $\$7.00$ account floor:
```bash
python3 -m pytest -v research_mission_15_6/tests/test_incident_replay_deterministic.py
```
**Expected Outcome**: **3 passed in ~1.5 seconds**.

### Step 5: Manuscript PDF Compilation Rehearsal
Compile the LaTeX manuscript using `tectonic`:
```bash
tectonic 08_REVISED_STATESHIFT.tex
```
**Expected Outcome**: Generates `08_REVISED_STATESHIFT.pdf` (~170 KiB) with complete BibTeX references and zero fatal errors.

---

## 4. Zero-Cloud-Cost Guarantee

All steps above execute locally on CPU using offline mocks, discrete-event time counters, and synthetic fixtures. Cloud execution remains fail-closed under `.cloud_execution_locked`. The total financial expenditure for running this reproduction protocol is **$0.00 USD**.

## 5. Conclusion

The StateShift codebase and scientific artifacts are 100% reproducible and verifiable on local hardware.
