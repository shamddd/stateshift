# StateShift Final Claim Boundary Register

**Audit Date**: October 18, 2026  
**Status**: Mandatory Wording Rules for Publication  

---

## 1. Permitted Claims (Fully Defensible)
- [x] *"Reinforcement learning from verifiable rewards induces an 11.76 percentage-point state-by-checkpoint interaction gain ($\Gamma_{256} = +0.1176, p < 0.0001$) conditional on invalid intermediate reasoning states on MATH-500."*
- [x] *"Under strict decontamination filtering ($N=388$), the interaction remains stable at $\Gamma_{256,\text{Strict}} = +0.1160$."*
- [x] *"In unperturbed rollouts, natural reasoning errors occur at an 18.19% rate, with 30.93% subsequent autonomous recovery to the correct final answer."*
- [x] *"Under order-restricted isotonic regression (PAVA), the post-training trajectory is consistent with a non-decreasing recovery profile."*
- [x] *"Conditioning on invalid intermediate prefixes at step 256 leaves a persistent 29.61% residual failure rate."*

---

## 2. Strictly Prohibited Claims (Indefensible or Overreaching)
- [ ] **NO**: *"Causal proof that RLVR teaches models intrinsic self-correction modules."*
- [ ] **NO**: *"Strict step-by-step monotonic recovery increases across all intermediate checkpoints."*
- [ ] **NO**: *"Generalization to code generation, web agents, or open-ended dialogue"* (untested in this confirmatory trial).
- [ ] **NO**: *"+28.8 pp DiD gain on code benchmarks"* (superseded precursor).
- [ ] **NO**: *"-6.2% DiD recovery impairment"* (refuted algebraic sign inversion).
