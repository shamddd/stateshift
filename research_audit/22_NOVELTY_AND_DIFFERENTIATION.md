# StateShift Scientific Novelty & Research Differentiation Memo

**Audit Date**: October 18, 2026  
**Auditor**: Lead Scientific Novelty Auditor  

---

## 1. What Makes StateShift Scientifically Distinct?

A common reviewer reflex is to dismiss error-recovery papers with: *"Huang et al. (ICLR 2024) already showed LLMs cannot self-correct, and SCoRe (Kumar et al. 2024) already trained self-correction."*

StateShift occupies a fundamentally different, unaddressed scientific niche:

```
                      [Multi-Turn Prompted]           [Single-Rollout Continuous]
                   ┌───────────────────────────────┬───────────────────────────────┐
 [Frozen Models]   │ Huang et al. (ICLR 2024)      │ Unprompted CoT Benchmarks     │
                   │ Stechly et al. (2024)         │ (Standard Pass@1 on MATH)     │
                   ├───────────────────────────────┼───────────────────────────────┤
 [Post-Trained]    │ SCoRe (Kumar et al. 2024)     │ ★ STATESHIFT (This Work) ★    │
                   │ (Explicit Multi-Turn RL)      │ (Emergent Recovery under RLVR)│
                   └───────────────────────────────┴───────────────────────────────┘
```

### The Three Core Contributions:
1. **The State-Matched Interaction Contrast ($\Gamma_t$)**:
   - Aggregate Pass@1 improvements confound general problem-solving gains with recovery adaptation.
   - StateShift introduces counterfactual baseline matching ($R$ vs $C$), proving that $+11.76$ pp of the post-training gain is specifically state-selective.
2. **Emergence Without Explicit Supervision**:
   - The evaluated DeepScaleR models were **never trained to recover from errors**; they were trained solely on final-answer outcome rewards.
   - StateShift proves that final-answer RLVR implicitly induces intermediate state-transition recovery capabilities.
3. **Trajectory & Boundary Characterization**:
   - Discovers that recovery emergence begins as early as step 32 ($\Gamma_{32} = +0.0333$).
   - Discloses that recovery does not scale monotonically (local dips at step 160 and 224).
   - Establishes a persistent terminal failure regime ($29.61\%$) where models cannot escape corrupted states even after full convergence.
