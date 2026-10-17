# StateShift Complete Experimental Design & Protocol Reconstruction

**Audit Date**: October 18, 2026  
**Auditor**: Independent Statistical Methodologist & Experimental ML Auditor  
**Standard**: Full Reconstruction from Source Code, Git History, and Raw Rollout Artifacts  
**Evidence Source**: `website_clone/artifacts/endpoint/controlled_endpoint_outcomes.csv` (SHA-256: `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139`)

---

## 1. Research Question & Formal Hypotheses

### Primary Research Question:
Does reinforcement learning from verifiable rewards (RLVR) induce a *state-dependent* error-recovery capability in autoregressive reasoning models, or are observed post-error successes merely the incidental reflection of general problem-solving advancement?

### Formal Hypotheses:
- **Null Hypothesis ($H_0$)**: Post-training improvement in solution correctness conditional on being in an invalid intermediate reasoning state ($\Delta_R$) equals post-training improvement conditional on being in a matched valid reasoning state ($\Delta_C$).
  $$H_0: \Gamma_t = \Delta_{R,t} - \Delta_{C,t} = 0$$
- **Alternative Hypothesis ($H_1$)**: Post-training selectively enhances an agent's ability to recover from invalid intermediate reasoning states beyond its general capability gain from clean states.
  $$H_1: \Gamma_t = \Delta_{R,t} - \Delta_{C,t} > 0$$

---

## 2. Experimental Structure & Multi-Level Factorial Design

The confirmatory experiment is structured as a **within-subject blocked factorial design** ($2 \times 2$ factorial nested within problem blocks):

```
Target Population: MATH-500 (Decontaminated Mathematical Reasoning)
                          │
       ┌──────────────────┴──────────────────┐
       ▼                                     ▼
Confirmatory Cohort (N = 454)      Strict Decontamination (N = 388)
       │
       ├─────────────────────────────────────────────┐
       ▼                                             ▼
Condition: Recovery State (R)               Condition: Control State (C)
(Verifier-confirmed invalid step prefix)    (Matched valid step prefix)
       │                                             │
  ┌────┴────┐                                   ┌────┴────┐
  ▼         ▼                                   ▼         ▼
Step 0    Step 256                            Step 0    Step 256
(Base)    (RLVR Post-Trained)                 (Base)    (RLVR Post-Trained)
  │         │                                   │         │
 K=16      K=16                                K=16      K=16
Rollouts  Rollouts                            Rollouts  Rollouts
```

### Experimental Unit:
The experimental unit is the **Problem Instance** $i \in \{1, \dots, 454\}$. Each problem provides the common context for both experimental conditions ($R$ and $C$) across both evaluation checkpoints ($t=0$ and $t=256$), blocking out between-problem difficulty variance.

### Rollout Structure:
- **Primary Endpoint Trial (Study A)**:
  - Problems: $N = 454$
  - Conditions: $2$ ($R$: Injected Error Prefix, $C$: Matched Clean Prefix)
  - Timepoints: $2$ (Step $0$: Base model, Step $256$: Final post-trained checkpoint)
  - Replications: $K = 16$ stochastic completions per cell
  - **Total Primary Rollouts**: $454 \times 2 \times 2 \times 16 = \mathbf{29,056}$ empirical rollouts.
- **Longitudinal Trajectory Trial (Study A Secondary)**:
  - Checkpoints: $t \in \{0, 32, 64, 96, 128, 160, 192, 224, 256\}$ (9 discrete checkpoints)
  - Replications: $K = 2$ or $K = 3$ per intermediate cell to trace trajectory dynamics under resource constraints.
- **Autonomous Natural Recovery Trial (Study B)**:
  - 3,200 unperturbed rollouts across MATH-500 identifying organic decoding errors ($N_{\text{err}} = 582$) and tracking spontaneous self-correction ($N_{\text{rec}} = 180$).

---

## 3. Dataset Generation, Error Injection & Decontamination

### Problem Selection & Filtering:
1. **Source Benchmark**: MATH-500 (challenging high-school and Olympiad mathematics competition problems across Algebra, Precalculus, Geometry, Number Theory, and Counting & Probability).
2. **Decontamination Protocol (Phase 1G)**:
   - Full 8-gram and embedding similarity scan against RL training corpora.
   - Removal of trivial formatting duplicates.
   - Yielded $N = 454$ confirmatory problems and a secondary strict decontamination cohort of $N_{\text{Strict}} = 388$ problems (removing 66 borderline/adversarial cases).

### Prefix Specifications:
- **Recovery Prefix ($P_{i,R}$)**: A plausible multi-step mathematical derivation terminating in an explicit arithmetic, sign, or algebraic error that renders the step invalid while leaving the original problem solvable in principle.
- **Control Prefix ($P_{i,C}$)**: A valid derivation matched for step count and token length ($482.5$ vs $495.8$ tokens) without mathematical error.

---

## 4. Outcome Definitions & Verification Oracles

For rollout $k$ of problem $i$ under condition $s$ at checkpoint $t$:
$$Y_{i,s,t,k} = \mathbb{I}\left(\text{Verify}\left(\text{Extract}(C_{i,s,t,k}), A_i^*\right) = \text{True}\right)$$
- $\text{Extract}(\cdot)$: Strict parser extracting the final LaTeX answer within `\\boxed{...}`.
- $\text{Verify}(\cdot)$: Formal symbolic verifier executing SymPy algebraic equivalence checking against ground truth $A_i^*$.
- **Zero LLM Judge Drift**: No neural reward models or LLM evaluators were used, eliminating evaluator drift across training checkpoints.

---

## 5. Randomization, Seeds & Execution Parameters

- **Decoding Temperature**: $T = 0.6$
- **Nucleus Sampling**: top-$p = 0.95$
- **Max Generation Tokens**: 4,096 tokens
- **Seed Procedure**: Deterministic base seed offset by `(problem_idx * 1000 + rollout_k)` ensuring identical sampling streams across checkpoints.
