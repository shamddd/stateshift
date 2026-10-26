# 03. Evaluator v4 Validation Report & Metric Integrity

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Evaluator**: [`evaluation/strict_recovery_evaluator_v4.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/evaluation/strict_recovery_evaluator_v4.py)  
**Human Packet**: [`03_HUMAN_ANNOTATION_PACKET.csv`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/03_HUMAN_ANNOTATION_PACKET.csv) ($N = 60$ Real Traces)  
**Status**: **HUMAN VALIDATION PENDING**  

---

## 1. Independent Human Annotation Status

In strict adherence to Research Mission 12 Section 4:
- We do **NOT** claim independent human validation.
- We do **NOT** present LLM self-evaluations as human ground truth.
- The 60-item blind annotation packet has been generated, blinded, randomized, and exported for external review.

---

## 2. Software Unit-Test Validation (Adversarial Fixtures Benchmark)

To verify the software implementation of Evaluator v4, we tested it against the 9 mandatory adversarial fixtures ([`tests/fixtures_evaluator_adversarial.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/tests/fixtures_evaluator_adversarial.py)):

| Fixture ID | Adversarial Scenario | Evaluator v3 Status | Evaluator v4 Status | Software Resolution |
| :--- | :--- | :---: | :---: | :--- |
| **`ADV_01`** | False error claim | **FAILED** (False Positive) | **PASS** (`VERIFIED_FALSE`) | Rejected superficial error keyword |
| **`ADV_02`** | Alternative derivation | **FAILED** (Missed Bypass) | **PASS** (`VERIFIED_FALSE`) | Flagged unrepaired corrupted step |
| **`ADV_03`** | Propagating invalid dependency | **FAILED** (Ambiguous) | **PASS** (`BLIND_COPYING`) | Detected downstream contamination |
| **`ADV_04`** | Silent implicit restart | **PASS** | **PASS** (`IMPLICIT_RESTART`) | Detected problem restatement |
| **`ADV_05`** | Surgical repair without keywords | **FAILED** (False Negative) | **PASS** (`VERIFIED_TRUE`) | Verified exact algebraic equality chain |
| **`ADV_06`** | Hybrid recomputation | **FAILED** (Ambiguous) | **PASS** (`PARTIAL_RECOMPUTE`)| Non-exclusive taxonomy captured hybrid |
| **`ADV_07`** | Equivalent non-trivial syntax | **PASS** | **PASS** (`VERIFIED_TRUE`) | SymPy verified equivalence |
| **`ADV_08`** | Lucky correct via false math | **FAILED** (Accepted Step) | **PASS** (`VERIFIED_FALSE`) | Rejected anomalous cancellation |
| **`ADV_09`** | Non-elementary theorem | **PASS** | **PASS** (`UNVERIFIED`) | Correctly returned UNVERIFIED fallback |

### Software Fixture Performance:
- **Accuracy on Adversarial Boundary Cases**: **9 / 9 (100.0%)**
- **Evaluator v3 Baseline Accuracy**: 4 / 9 (44.4%)
- **Improvement**: +55.6 percentage points on edge-case sensitivity.

---

## 3. Positive-Class Coverage & Empirical Denominator Disclosure

> [!IMPORTANT]
> **Positive-Class Recall Disclosure**: Across all 115 real model rollouts generated on Apple Silicon M1 (100 from Mission 10, 15 from Mission 11), **zero genuine local repairs were observed** (models uniformly restarted explicitly or implicitly).
> 
> Because the true empirical prevalence of genuine local repair in sub-2B models is $0$, **empirical positive-class recall cannot be calculated from real observations**. We explicitly refuse to fabricate synthetic positive cases to simulate a high recall score. Positive-class precision and recall can only be evaluated against constructed software fixtures until 7B experiments are executed.
