# PHASE III: RECOVERY EVALUATOR FORMAL SPECIFICATION

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference  
**Date**: October 24, 2026  
**Implementation**: [`evaluation/strict_recovery_evaluator.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_10/evaluation/strict_recovery_evaluator.py)

---

## 1. Formal Mathematical Definitions

Let:
- $q$: Problem statement
- $s^* = (s_1^*, \dots, s_k^*)$: Valid reasoning prefix
- $\tilde{s}_k$: Surgically corrupted intermediate step
- $y^*$: Gold ground-truth final answer
- $r$: Model generation rollout

The evaluator decomposes $r$ into eight orthogonal observables:

1. **Final Answer Correctness ($A(r) \in \{0, 1\}$)**:
   $$A(r) = \mathbb{I}[\text{SymPy}(\text{extract}(r)) \equiv y^*]$$

2. **Error Detection ($D(r) \in \{0, 1\}$)**:
   $$D(r) = \mathbb{I}[\text{contains}(r, \mathcal{C}_{\text{detect}})]$$
   where $\mathcal{C}_{\text{detect}} = \{\text{"error", "mistake", "incorrect", "actually", "flaw"}\}$.

3. **Error Localization ($L(r) \in \{0, 1\}$)**:
   $$L(r) = \mathbb{I}[\text{identifies\_step}(r, k)]$$

4. **Valid Prefix Preservation ($P(r) \in \{0, 1\}$)**:
   $$P(r) = \mathbb{I}[\neg \text{contains}(r, \mathcal{C}_{\text{restart}}) \wedge (r \text{ continues from } s_k^*)]$$

5. **Local Correction Validity ($C(r) \in \{0, 1\}$)**:
   $$C(r) = \mathbb{I}[D(r) = 1 \wedge \text{supplies\_corrected\_assertion}(r)]$$

6. **Continuation Validity ($V(r) \in \{0, 1\}$)**:
   $$V(r) = \mathbb{I}[\neg \text{truncated}(r) \wedge \text{has\_valid\_derivation}(r)]$$

7. **Restart Behavior ($R(r) \in \{0, 1\}$)**:
   $$R(r) = \mathbb{I}[\text{contains}(r, \mathcal{C}_{\text{restart}}) \vee (\text{condition} = \text{"forced\_restart"})]$$

8. **Verified Local Repair ($VLR(r) \in \{0, 1\}$)**:
   $$\mathbf{VLR}(r) = A(r) \wedge D(r) \wedge P(r) \wedge (\neg R(r)) \wedge C(r) \wedge V(r)$$

---

## 2. Invariant Rules for Experimental Reporting

1. **No Conflation of Correctness with Repair**: A rollout with $A(r) = 1$ but $D(r) = 0$ is classified as a *Lucky Continuation / Guess*, NOT a local repair.
2. **Explicit Restart Separation**: Any rollout with $R(r) = 1$ is strictly barred from $VLR(r) = 1$.
3. **Common Endpoint for Cross-Condition Contrasts**: When comparing Condition D (Forced Restart) against Condition F (State-Preserving Repair), the primary contrast MUST use $A(r)$ (Final Answer Correctness), with $VLR(r)$ reported as a mechanism-sensitive secondary metric.
