# Research Mission 15.1: Scientific Protocol & Preregistration Integrity Audit

**Principal Investigator**: Sham Satish Thakare  
**Repository**: `github.com/shamddd/stateshift`  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_1/08_SCIENTIFIC_PROTOCOL_INTEGRITY.md`  
**Date**: October 25, 2026  
**Auditor**: Independent Scientific Methodology & Preregistration Auditor  

---

## 1. Executive Summary

A critical danger during infrastructure refactoring is "protocol drift"—where bug fixes inadvertently alter the prompt templates, decoding hyperparameters, or statistical hypotheses of the pre-registered experiment.

This audit certifies that **zero scientific or experimental parameters were modified** during Mission 15.1. The experiment manifest, mathematical problem cohort, causal annotations, and statistical estimands remain 100% identical to the frozen pre-registration.

---

## 2. Cryptographic Protocol Freeze Verification

| Scientific Component | Verification Standard | Checksum / Value | Audit Status |
| :--- | :--- | :--- | :---: |
| **Primary Manifest** | `primary_100_manifest.json` | `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` | **UNALTERED (FROZEN)** |
| **Problem Selection** | 100 MATH-500 test problems | `math500_001` through `math500_100` | **UNALTERED** |
| **Condition Balancing** | 4 balanced conditions | 100 A, 100 D, 100 E, 100 F (Total: 400) | **UNALTERED** |
| **Target Model** | `Qwen/Qwen2.5-Math-7B-Instruct` | Revision `main` | **UNALTERED** |
| **Decoding Parameters**| Greedy decoding | `temperature = 0.0`, `seed = 42`, `max_tokens = 768` | **UNALTERED** |
| **Corruption Operators**| 7 deterministic operators | Arithmetic, sign, rounding, formula confusion, etc. | **UNALTERED** |
| **Statistical Estimands**| 5 neutral estimands | $\theta_{\text{repair}}$, Strategy Matrix, $\Delta$, $R_{\text{eff}}$, $C_f$ Logistic | **UNALTERED** |
| **FWER Control** | Holm-Bonferroni correction | $\alpha_{\text{family}} = 0.05$ | **UNALTERED** |
| **Equivalence Bounds** | TOST protocol | $[-\delta, +\delta] = [-0.05, +0.05]$ | **UNALTERED** |

---

## 3. Evaluator v5.1 Epistemic Status

We reiterate with complete scientific transparency:
- **Automated Symbolic Verification**: Evaluator v5.1 incorporates SymPy algebraic equivalence and heuristic conflict resolution, which have been validated across edge-case fixtures.
- **Human Calibration**: The 140-trace double-blind human validation study (`06_HUMAN_VALIDATION_PROTOCOL.md`) remains **PENDING**. 
- **Epistemic Commitment**: No claims of human-level evaluator reliability or definitive ground truth will be made in the manuscript until this human calibration study is physically executed and inter-rater agreement ($\kappa_{\text{Fleiss}} \ge 0.85$) is formally measured.

---

## 4. Causal Discovery Boundaries

The findings of Missions 08–14 demonstrated a strong statistical correlation between dependency graph contamination fraction ($C_f$) and reasoning failure. 
In accordance with non-negotiable scientific integrity rules:
- Correlation is **not** reported as established causality.
- The direct causal effect of branch contamination will only be claimed after executing the matched counterfactual DAG intervention designed in `08_DECISIVE_CAUSAL_EXPERIMENT_DESIGN.md`.

---

## 5. Audit Conclusion

The scientific integrity of the StateShift experimental protocol is fully preserved. The engineering repairs executed in Mission 15.1 exclusively hardened cloud safety, termination reliability, and file verification.
