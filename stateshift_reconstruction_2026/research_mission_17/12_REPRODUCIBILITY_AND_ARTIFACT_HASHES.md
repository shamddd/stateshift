# StateShift: Research Mission 17 — Reproducibility & Cryptographic Artifact Ledger

**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Execution Timestamp:** 2026-10-26T05:39:04Z UTC  

---

## 1. Executive Summary

This document establishes the immutable cryptographic ledger of all primary research artifacts, datasets, execution logs, evaluation results, and manuscript sources produced during Research Mission 17.

All files are preserved locally, verified via SHA-256 hashes, and structured for deterministic 1-command reproduction.

---

## 2. Cryptographic Artifacts Hash Ledger

| Artifact Category | Relative File Path | Size | SHA-256 Checksum | Forensic Status |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Problem Manifest** | `research_mission_15_6/manifests/primary_100_manifest.json` | 569,153 B | `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` | **FROZEN SCIENTIFIC BASELINE** |
| **Calibration Manifest** | `research_mission_15_6/manifests/calibration_10_manifest.json` | 13,662 B | `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6` | **FROZEN SCIENTIFIC BASELINE** |
| **Primary Neural Generations** | `data/primary_run/stateshift_primary_400_generations.jsonl` | 898,204 B | `bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2` | **VERIFIED PRIMARY DATASET** |
| **Cryptographic Session Token** | `data/primary_run/session_auth_primary_400.json` | 901 B | `1f97305aefe80147f5e51bf675e6b50d8efc6f719e70b8c4f7ac0fe4fd5b299f` | **SIGNED AUTHORIZATION TOKEN** |
| **Trusted Public Key** | `data/primary_run/operator_pubkey.txt` | 44 B | `0a85ca1b6cf1f9ff7a73d4155743fb583573bba51a7a13d1ad47379492ad1cae` | **OPERATOR PUBLIC KEY** |
| **Financial Reconciliation** | `data/primary_run/primary_400_reconciliation.json` | 907 B | `ac1c016304e7121d6b18094cec8a276cf003e23943db7e2ac8c7673e072d4951` | **SETTLED BILLING RECEIPT** |
| **Execution Timeline Log** | `data/primary_run/primary_400_timeline_events.jsonl` | 30,246 B | `ffa83f617dad8db5cf7d9e35bd9dab1222f6090a55e0a656c5faf1d33dec6b83` | **DETERMINISTIC EVENT LOG** |
| **Evaluation & Stats Results**| `data/primary_run/primary_400_evaluation_results.json` | 1,012,996 B | `7961629a31633cafe5211fd44ab4848ce222979e5e022ba2abd3cc44d1b0c73e` | **STATISTICAL EVALUATION** |
| **Reconciled LaTeX Manuscript**| `08_REVISED_STATESHIFT.tex` | 31,420 B | `e094dd01b9d3ea3cfac088a898d4645c930ec010706086ddd78f5009f4170007` | **FINAL MANUSCRIPT SOURCE** |
| **Primary Execution Launcher**| `research_mission_15_6/runner/execute_authorized_primary_400.py` | 28,907 B | `9326ff97843423f0f1e0fb289fd32246788e156a1afbeedd50eab35096c3f67f` | **PRODUCTION LAUNCH SCRIPT** |
| **Remote Inference Runner** | `research_mission_15_6/runner/remote_experiment_runner.py` | 15,546 B | `1f5d76b7e95327630f2f02afdccb4ac2a867c3fe5ea5dc36c879c14f21048380` | **REMOTE INFERENCE ENGINE** |
| **Evaluation Driver Script** | `research_mission_17/scripts/evaluate_primary_400.py` | 9,961 B | `23c8b0af867fc15205cb816cebc1eaa563f0a43f20fee59d19ff19f715eb2054` | **REPRODUCIBLE EVAL SCRIPT** |

---

## 3. One-Command Reproduction Instructions

To independently reproduce the evaluation and statistical inference tables from the verified raw generations:

```bash
# From the repository root
python3 research_mission_17/scripts/evaluate_primary_400.py
```

Expected output:
```
================================================================================
  STATESHIFT: PRIMARY 400-REQUEST INDEPENDENT SCIENTIFIC EVALUATION
================================================================================
Loaded 400 authentic inference records from data/primary_run/stateshift_primary_400_generations.jsonl
Independent Dataset Verification: Valid=True, Record Count=400, Errors=0

--- Empirical Accuracy by Experimental Condition ---
  Condition A (Zero-Shot Baseline):       64/100 (64.00%)
  Condition D (Forced Restart Control):   67/100 (67.00%)
  Condition E (Explicit Repair):          71/100 (71.00%)
  Condition F (State-Preserving Recovery):73/100 (73.00%)

--- Preregistered Statistical Inference Results ---
  Primary Estimand tau_{F-D}:   +6.00 percentage points (95% CI: [+0.00%, +12.00%], exact McNemar p = 0.109375)
  Baseline Comparison tau_{F-A}: +9.00 percentage points (95% CI: [+3.00%, +15.00%], exact McNemar p = 0.011719)
```

---

## 4. Certification

The cryptographic checksums recorded in this ledger are immutable and correspond exactly to the physical bytes preserved on disk.

**Principal Investigator:** Sham Satish Thakare  
**Date:** October 26, 2026  
