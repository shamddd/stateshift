# Phase N: Fresh Clone Reproducibility Report

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training
**Principal Investigator**: Sham Satish Thakare
**Date & Time**: 2026-10-26T17:30:00+05:30
**Repository**: `https://github.com/shamddd/stateshift`

---

## 1. Fresh Clone Execution Setup

To verify that an external researcher can reproduce the findings directly from the public repository without residual local artifacts, an isolated clean reproduction test was performed:

```bash
rm -rf /tmp/stateshift-public-verification
git clone https://github.com/shamddd/stateshift.git /tmp/stateshift-public-verification
cd /tmp/stateshift-public-verification
```

- **Cloned Commit**: `aa49a81d4db5dd9fe68df95c32e07e43d36fd88f` (Remote `main` HEAD).
- **Execution Mode**: Local CPU only; zero cloud dependencies; zero GPU provisioning.

---

## 2. Test Suite & Replication Results

### A. QA Release Test Suite
Executed `pytest tests/test_mission20_release_qa.py -v`:
- `test_public_dataset_hashes`: **PASSED**
- `test_paper_artifacts_exist`: **PASSED**
- `test_study1_reproduction_accuracy`: **PASSED**
- `test_study2_reproduction_accuracy`: **PASSED**
- `test_exact_power_bounds`: **PASSED**
- `test_documentation_and_governance_files`: **PASSED**
- **Result**: `6 passed in 2.02s` (100% pass rate).

### B. Study 1 Replication Script
Executed `python experiments/study1_checkpoint_lineage/reproduce_study1.py`:
- Dataset: `data/study1/controlled_endpoint_outcomes.csv` (SHA-256 verified)
- Unique problem pairs: 454; Total rows: 29,056
- Step 0 Control: $38.92\%$; Step 0 Recovery: $38.34\%$ (Diff: $-0.58$ pp)
- Step 256 Control: $59.21\%$; Step 256 Recovery: $70.39\%$ (Diff: $+11.18$ pp)
- Clustered interaction $\hat{\gamma}_{256}$: **$+11.76$ percentage points** ($t = 10.34, p < 0.001$).
- Mean token difference (Recovery - Control): $-13.19$ tokens.
- TOST Equivalence at $[-5, +5]$ token threshold: **PASS** ($p = 0.0256$).

### C. Study 2 Replication Script
Executed `python experiments/study2_reasoning_recovery/reproduce_study2.py`:
- Raw generations: 400 records (SHA-256 verified)
- Outcomes evaluated: 100 problem pairs (SHA-256 verified)
- Accuracies:
  - Condition A: **64.00%**
  - Condition D: **67.00%**
  - Condition E: **71.00%**
  - Condition F: **73.00%**
- Primary contrast ($F - D$): **+6.00 percentage points** ($73\% - 67\%$).
- Exact McNemar Contingency: $a=65, b=8, c=2, d=25$.
- Off-diagonal odds ratio: **4.00** ($4:1$ favorable recovery ratio).
- Exact two-sided McNemar $p$-value: **$0.109375$** (non-significant at $\alpha=0.05$).
- Baseline recovery contrast ($F - A = +9.00$ pp): **$p = 0.0117$** (significant at $\alpha=0.05$).

### D. Exact Discrete Power Engine
Executed `python experiments/study2_reasoning_recovery/exact_power_analysis.py`:
- Pilot sample ($N = 100$): Exact unconditional power = **$36.20\%$** (Type II error rate $\beta = 63.80\%$).
- Confirmatory sample size requirements (Scenario B):
  - $80\%$ target power: **$N = 231$** (achieved power $80.07\%$)
  - $90\%$ target power: **$N = 299$** (achieved power $90.02\%$)

---

## 3. Fresh Clone Reproducibility Verdict

**Verdict**: **PASS** (100% of replication scripts, statistical tests, and QA assertions execute cleanly and identically from a fresh clone).
