# StateShift Identification, Causal Scope & Interpretation Audit

**Audit Date**: October 18, 2026  
**Auditor**: Senior Statistical Red-Team Auditor  

---

## 1. What the Experimental Design Scientifically Identifies

The StateShift framework cleanly identifies:
1. **State-Selective Performance Differential**: The difference in pass rate trajectory when conditioned on an invalid intermediate step versus a matched valid step.
2. **Post-Training Horizon Effect**: How the state-selective differential evolves from base model ($t=0$) through terminal RLVR checkpoint ($t=256$).
3. **Decontamination Robustness**: Invariance of the interaction contrast under strict filtering of potential training-set overlaps ($N=388$).
4. **Endogenous Error Recovery in Natural Decoding**: The base rate at which the post-trained model encounters natural step errors ($\text{NEI}=18.19\%$) and successfully recovers ($\text{NRR}=30.93\%$) without external intervention.

---

## 2. What the Experimental Design CANNOT Claim (Causal & Boundary Limitations)

Reviewers at NeurIPS will aggressively scrutinize overreaching causal claims. The manuscript must explicitly enforce the following claim boundaries:

1. **Not a Causal Proof of Intrinsic Self-Correction Mechanisms**:
   - Observing $\mu_{R,256} > \mu_{R,0}$ and $\Gamma_{256} > 0$ does *not* prove the model possesses an explicit introspective "error detection module".
   - The model could simply be generating longer continuations that happens to stumble upon the correct answer, or the RL policy may have higher baseline entropy that occasionally bypasses dead ends.
2. **Domain Specificity (MATH-500 Only)**:
   - All $29,056$ primary rollouts evaluate formal high-school competition mathematics (MATH-500).
   - It is scientifically invalid to assert that this $+11.76$ pp recovery gain generalizes to tool use, web browsing, natural language negotiation, or Python code generation without empirical evidence in those domains.
3. **Single Lineage (DeepScaleR Qwen-2.5-7B)**:
   - Evaluates only one post-training RL run (DeepScaleR).
   - Does not establish whether DPO, PPO, or other RLVR recipes (e.g. DeepSeek-R1-Zero) produce similar recovery dynamics.
4. **Natural vs Injected Error Equivalence**:
   - Injected error prefixes represent controlled synthetic perturbations.
   - While Study B assesses natural errors ($\text{NEI}=18.19\%$, $\text{NRR}=30.93\%$), the recovery mechanism from an injected counterfactual prefix may differ from organic recovery during autonomous generation.
