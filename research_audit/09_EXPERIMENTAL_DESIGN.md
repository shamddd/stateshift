# StateShift Comprehensive Experimental Design & Protocol Audit

**Audit Date**: October 18, 2026  
**Auditor**: Lead ML Experimentalist & Causal Inference Auditor  
**Standard**: Full Reconstruction from Source Code, Data, and Pre-Registration Logs  

---

## 1. Experimental Hierarchy and Data Structure

The StateShift confirmatory experiment evaluates model rollouts under a multi-level blocked factorial design:

```
[Target Population: Mathematical Reasoning (MATH-500)]
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
Confirmatory Cohort (N = 454)        Strict Decontamination (N = 388)
       │
       ├───────────────────────────────────────────────┐
       ▼                                               ▼
State: Recovery Condition (R)                 State: Control Condition (C)
(Invalid Intermediate Step Injected)          (Matched Valid Intermediate Step)
       │                                               │
  ┌────┴────┐                                     ┌────┴────┐
  ▼         ▼                                     ▼         ▼
Ckpt 0   Ckpt 256                               Ckpt 0   Ckpt 256
(Base)   (DeepScaleR)                           (Base)   (DeepScaleR)
  │         │                                     │         │
K=16      K=16                                  K=16      K=16
Rollouts  Rollouts                              Rollouts  Rollouts
```

### Hierarchy Breakdown:
1. **Level 1 (Problem Level, $i \in \{1, \dots, 454\}$)**: Each problem consists of a question prompt $Q_i$, a ground-truth final numerical/symbolic target $A_i^*$, a validated solution prefix $P_{i,C}$, and an injected error prefix $P_{i,R}$.
2. **Level 2 (State Condition, $s \in \{R, C\}$)**:
   - **Recovery ($R$)**: The decoding trajectory is forced through prefix $P_{i,R}$, which terminates in a verifier-confirmed arithmetic, algebraic, or logical error.
   - **Control ($C$)**: The decoding trajectory begins from prefix $P_{i,C}$, matched for token length and preceding reasoning steps without error.
3. **Level 3 (Checkpoint Step, $t \in \{0, 256\}$ in Study A; $t \in \{0, 32, \dots, 256\}$ in Study A trajectory)**: Checkpoints from DeepScaleR-1.5B / Qwen-2.5-7B RL post-training.
4. **Level 4 (Rollout Replications, $k \in \{1, \dots, K\}$)**: Stochastically sampled continuations ($T=0.6$, top-$p=0.95$, max new tokens 4,096) evaluating whether the model reaches the correct final boxed answer $A_i^*$.
   - **Primary Endpoint**: $K = 16$ rollouts per cell $\implies 454 \times 2 \times 2 \times 16 = \mathbf{29,056}$ primary rollouts.
   - **Intermediate Checkpoints**: $K = 2$ or $K = 3$ rollouts per cell across steps $\{32, 64, 96, 128, 160, 192, 224\}$.

---

## 2. Injected Error Prefix Specification

To prevent trivial verifier exploits or syntactic crashes:
1. **Semantic Invalidity**: An error prefix is not mere random token corruptions. It represents a plausible reasoning deduction that introduces an invalid mathematical claim (e.g., $3x + 4 = 19 \implies 3x = 12$).
2. **Structural Recoverability**: The problem must remain mathematically solvable in principle from the point of error (i.e. the injected prefix has not asserted a contradiction that renders the original question impossible to answer).
3. **Length Matching**: Control prefixes $P_{i,C}$ are matched to within $\pm 10\%$ token length of $P_{i,R}$ to avoid length-bias confounding.

---

## 3. Evaluation Oracles and Verifier Behavior

The target transition metric is defined by:
$$Y_{i,s,t,k} = \mathbb{I}\left(\text{Verify}\left(\text{Extract}\left(C_{i,s,t,k}\right), A_i^*\right) = \text{True}\right)$$
where:
- $\text{Extract}(\cdot)$ parses the final answer from `\\boxed{{...}}`.
- $\text{Verify}(\cdot)$ runs a deterministic symbolic equivalence check (SymPy + math equivalence rules).
- No neural reward models or LLM judges are used as evaluators, preventing evaluator drift across checkpoints.
