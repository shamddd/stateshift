# StateShift Final Scientific Red-Team Review

**Audit Date**: October 18, 2026  
**Auditor**: Independent Skeptical Adversarial Reviewer  
**Standard**: Active Attempt to Falsify the Main Scientific Claim  

---

## 1. Falsification Stress Tests & Verdicts

### Challenge 1: "Could the recovery effect be completely explained by clean-accuracy improvements?"
- **Test**: If RLVR merely scales general capability, the probability gain from invalid states ($\Delta_R$) should equal the gain from valid states ($\Delta_C$).
- **Falsification Verdict**: **REFUTED BY DATA**.
  $$\Delta_R = +0.3205, \quad \Delta_C = +0.2029 \implies \Gamma_{256} = +0.1176$$
  The interaction contrast is positive with $z = 10.4, p < 0.0001$. Recovery improves by $11.76$ percentage points *beyond* clean accuracy scaling.

### Challenge 2: "Is the result driven by memorization of the MATH benchmark in DeepScaleR pre-training?"
- **Test**: Recompute the interaction on the strict decontaminated subset ($N=388$), excluding all problems with potential 10-gram or edit-distance overlap.
- **Falsification Verdict**: **REFUTED BY DATA**.
  $$\Gamma_{256,\text{Strict}} = +0.1160 \quad (95\%\text{ CI } [+0.0913, +0.1408])$$
  The effect size is virtually identical (difference is only $0.0016$).

### Challenge 3: "Does the model actually recover, or is it taking invalid shortcuts that happen to hit the final number?"
- **Test**: Examine the deterministic symbolic verification rules.
- **Falsification Verdict**: **PARTIALLY SOUND, BOUNDED BY DESIGN**.
  SymPy verifies algebraic equivalence of the final boxed answer. In Study B, intermediate steps were verifier-checked. However, the model is not claimed to 'reason introspectively'; it is claimed that the continuation trajectory successfully reaches the correct target. This distinction is explicitly maintained in the paper.
