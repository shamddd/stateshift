# StateShift Research Mission 14 — Deliverable 08: Dependency Contamination Reanalysis

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Investigating Role**: Independent Forensic Recovery Auditor  
**Date**: October 25, 2026  

---

## 1. Confounding Analysis of Dependency Contamination

In Mission 13, it was reported that downstream dependency contamination ($\text{contamination\_fraction}$) correlates with restart rate ($r_s = +0.264, p = 0.026$) and compounded error rate ($r_s = +0.221, p = 0.064$). 

An independent methodological audit reveals several potential confounds that must be disentangled before claiming a universal causal mechanism:

### 1.1 Potential Confounders:
1. **Error Step Position vs. Contamination**:
   - An error injected at Step 1 of a 4-step derivation inherently has more downstream steps than an error injected at Step 3.
   - Is the model restarting because the contamination fraction is high, or simply because the error occurred early in the sequence?
2. **Prefix Length**:
   - Shorter prefixes provide less mathematical context, which may naturally prompt the model to restart rather than build upon a fragmentary one-line premise.
3. **Problem Difficulty & Subject**:
   - Complex Intermediate Algebra and Precalculus problems often involve interdependent multi-variable systems (leading to high DAG connectivity), whereas simple arithmetic involves shallow chains.
4. **Corruption Operator Type**:
   - `OP04_INVALID_ASSUMPTION` (used in req 0131 and 0143) corrupts fundamental premises, forcing $c = 1.0$. In contrast, `OP01_ARITHMETIC_MISCALCULATION` often affects a single numerical constant, permitting parallel unaffected derivations ($c < 1.0$).

---

## 2. Minimal Intervention Required for Causal Identification

To establish true causality (rather than descriptive correlation), future experiments must employ a **matched counterfactual intervention**:

### The Decisive Causal Experiment:
- Take a single fixed problem with an $M$-step reference proof.
- **Intervention 1 (High Contamination Subtree)**: Inject an error into a lemma that is consumed by all subsequent steps ($c = 1.0$, holding prefix length and error position constant).
- **Intervention 2 (Low Contamination Subtree)**: Inject an error into an independent branch or parallel lemma that affects only 1 downstream step ($c \le 0.25$, holding prefix length and error position constant).
- By comparing recovery behavior across these counterfactual graphs while holding problem difficulty, error position, and prefix length invariant, any shift from local repair/continuation to implicit restarting can be unambiguously attributed to dependency contamination.

Until this controlled counterfactual experiment is executed, the relationship between contamination fraction and recovery strategy must be reported as a **promising observational correlation**, not a proven causal law.
