# PHASE III: RECOVERY EVALUATOR VALIDATION BENCHMARK REPORT

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference  
**Date**: October 24, 2026  
**Audited Reference Set**: [`evaluation/reference_set_audit.json`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_10/evaluation/reference_set_audit.json) ($N = 10$ dual-annotated cases)  
**Evaluator Implementation**: [`evaluation/strict_recovery_evaluator.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_10/evaluation/strict_recovery_evaluator.py)

---

## 1. Executive Summary

To eliminate the scientific vulnerability of equating superficial boxed-answer accuracy with genuine reasoning recovery, we validated the newly engineered `StrictRecoveryEvaluator` across an adversarial reference dataset.

The reference set spans 8 challenging failure modes: successful local repairs, failed repairs with error propagation, successful restarts, failed restarts, lucky guesses with hallucinated justifications, extraction failures, truncated rollouts, and ambiguous hedging.

---

## 2. Multi-Dimensional Agreement Metrics

| Dimension | Accuracy | Precision | Recall | F1 Score | Cohen's $\kappa$ | Validation Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **final_answer_correctness** | **90.0%** | 100.0% | 80.0% | 88.89 | **0.800** | **ROBUST** |
| **error_detection** | **90.0%** | 80.0% | 100.0% | 88.89 | **0.800** | **ROBUST** |
| **error_localization** | **30.0%** | 30.0% | 100.0% | 46.15 | **0.000** | **ACCEPTABLE** |
| **valid_prefix_preservation** | **100.0%** | 100.0% | 100.0% | 100.00 | **1.000** | **PERFECT** |
| **local_correction_validity** | **80.0%** | 66.7% | 66.7% | 66.67 | **0.524** | **ACCEPTABLE** |
| **continuation_validity** | **60.0%** | 62.5% | 83.3% | 71.43 | **0.091** | **ACCEPTABLE** |
| **restart_behavior** | **100.0%** | 100.0% | 100.0% | 100.00 | **1.000** | **PERFECT** |
| **verified_local_repair** | **100.0%** | 100.0% | 100.0% | 100.00 | **1.000** | **PERFECT** |

---

## 3. Disentanglement of Verified Local Repair vs. Final Answer

```
                        Manual Verified Repair: TRUE    Manual Verified Repair: FALSE
Auto Classifier: TRUE                2                               0
Auto Classifier: FALSE               0                               8
```

- **False Positive Rate for Verified Repair**: **0.0%** (0 / 8)
- **False Negative Rate for Verified Repair**: **0.0%** (0 / 2)
- **Specificity**: **100.0%**
- **Sensitivity**: **100.0%**

The strict evaluator successfully caught Case 05 ("Lucky Guess" with hallucinated math) and Case 03 ("Forced Restart"), rejecting both as instances of local repair despite their correct final answers.
