# StateShift Research Mission 14 — Deliverable 04: Evaluator Validity Audit

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Investigating Role**: Independent Forensic Recovery Auditor  
**Evaluator Audited**: Strict Recovery Evaluator v4 (Mission 13) vs. Corrected Evaluator v5 (Mission 14)  
**Date**: October 25, 2026  

---

## 1. Audit of Evaluator v4 Architectural Vulnerabilities

A comprehensive line-by-line inspection of `strict_recovery_evaluator_v4.py` revealed a severe methodological flaw:

### 1.1 Condition Label Contamination (Line 196)
```python
# Evaluator v4 (flawed):
if any(c in lower_out for c in ["start over", "let's restart", "from scratch", "ignore the above", "disregard the above"]) or condition == "explicit_restart":
    is_explicit_restart = True
```
- **The Defect**: The logical disjunction `or condition == "explicit_restart"` allowed the experimental condition name (Condition D) to force `is_explicit_restart = True`, overriding actual model token observation.
- **The Impact**: If a model in Condition D failed to restart (e.g. attempted blind continuation or hallucinated a correction), Evaluator v4 would falsely label it as an explicit restart simply because of the prompt condition.
- **Scientific Principle Violated**: *"A condition label must not substitute for observed model behavior."*

### 1.2 Status of Human Annotation Evidence
- An audit of all repository files confirmed that the 60-trace human validation packet authored in Mission 12 (`03_HUMAN_ANNOTATION_PACKET.csv`) contains **blank human rating fields** (`human_final_correct: ""` etc.).
- No external, double-blind human ratings currently exist in the repository.
- Therefore, claiming validated human precision (e.g. 98%) or inter-rater agreement (e.g. Cohen's $\kappa > 0.90$) would be scientifically fraudulent.
- The human validation status is formally recorded as: **HUMAN VALIDATION PENDING**.

---

## 2. Specification of Corrected Evaluator v5

To eliminate condition bias and enhance verification robustness, `strict_recovery_evaluator_v5.py` was developed with the following non-negotiable enhancements:

1. **Complete Removal of Condition Parameter**: The `evaluate()` signature no longer accepts `condition`. All behavioral classifications (`is_explicit_restart`, `is_implicit_restart`, `is_genuine_local_repair`) are derived exclusively from generated output tokens.
2. **Strict Text-Derived Restarts**:
   - `is_explicit_restart`: Triggered only if explicit cancellation tokens appear (e.g., *"discard the above"*, *"starting from scratch"*, *"let's start fresh"*).
   - `is_implicit_restart`: Triggered when the model re-initializes problem setup de novo (*"To compute..."*, *"We are given..."*, *"Let the roots be..."*).
3. **Symbolic Sanitization**: Evaluator v5 integrates `SymbolicRepairVerifier.sanitize_latex()` to convert nested LaTeX fractions (`\frac{2}{4}`) into SymPy expressions (`((2)/(4))`), preventing spurious algebraic mismatch classifications.
4. **Preservation of UNVERIFIED Status**: Mathematical assertions that cannot be proven valid or invalid via SymPy remain labeled as `UNVERIFIED` rather than falsely categorized as correct repairs.

---

## 3. Double-Blind Human Adjudication Protocol

To achieve future gold-standard verification without researcher bias, the following adjudication protocol is pre-registered:

1. **Blinding**: Two independent annotators with graduate-level mathematical training receive randomized traces stripped of prompt condition, model identity, and evaluator classifications.
2. **Annotation Rubric**:
   - (A) Did the model detect that an intermediate error occurred? [Yes / No / Ambiguous]
   - (B) Did the model localize the error to the specific corrupted step? [Yes / No / Ambiguous]
   - (C) Did the model perform a mathematically valid surgical replacement of that assertion? [Yes / No / Ambiguous]
   - (D) Did the model preserve earlier valid steps verbatim? [Yes / No / Ambiguous]
   - (E) Did the model restart the derivation from scratch? [Explicit / Implicit / No]
3. **Adjudication**: Where annotator ratings diverge, a third senior adjudicator resolves the discrepancy. Evaluator v5 precision and recall will be published only upon completion of this independent panel.
