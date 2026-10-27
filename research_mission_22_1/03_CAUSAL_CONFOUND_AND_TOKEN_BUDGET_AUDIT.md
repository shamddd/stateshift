# Phase 3: Causal Confound, Token Budget, and Context Audit

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22.1 — Final Confirmatory Scientific Audit  
**Date & Timestamp**: 2026-10-27T05:39:15+05:30  
**Target Publication Venue**: NeurIPS 2027 Main Track  

---

## 1. Executive Summary & Methodological Correction

In Research Mission 22, the observation that Condition D (Forced Restart) and Condition F (State Preservation) exhibited similar truncation rates ($24.0\%$ vs $22.0\%$) was described as *"empirically refuting"* token-budget confounding.

**This conclusion was methodologically unjustified.** Truncation-rate parity alone does not demonstrate the absence of token-budget or context confounding. Conditioning on post-treatment truncation (`finish_reason`) constitutes conditioning on a post-treatment collider, which can introduce selection bias.

Furthermore, Condition F does not directly manipulate internal neural weights or KV-cache tensors in hardware. Rather, Condition F is an **integrated prompt-level intervention package**. The confirmatory trial evaluates the total causal effect of this complete bundled package against the forced-restart baseline; it does not claim to isolate the orthogonal contribution of each constituent mechanism.

---

## 2. Descriptive Audit of Pilot Generation Dynamics

To understand the empirical dynamics of the $N = 100$ pilot without claiming definitive causal mediation, we computed full descriptive distributions across all 400 generations:

| Experimental Condition | Total $N$ | Completed Naturally (`stop`) | Truncated at Limit (`length`) | Mean Output Length (chars) | $P(\text{Correct} \mid \text{Stop})$ | $P(\text{Correct} \mid \text{Trunc})$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Condition A (Zero-Shot)** | 100 | 70 ($70\%$) | 30 ($30\%$) | $1385.7 \pm 42.1$ | $90.00\%$ ($63/70$) | $0.00\%$ ($0/30$) |
| **Condition D (Forced Restart)** | 100 | 76 ($76\%$) | 24 ($24\%$) | $1302.6 \pm 44.8$ | $86.84\%$ ($66/76$) | $0.00\%$ ($0/24$) |
| **Condition E (Explicit Repair)** | 100 | 76 ($76\%$) | 24 ($24\%$) | $1236.7 \pm 46.5$ | $88.16\%$ ($67/76$) | $12.50\%$ ($3/24$) |
| **Condition F (State Preservation)** | 100 | 78 ($78\%$) | 22 ($22\%$) | $1269.9 \pm 45.2$ | $91.03\%$ ($71/78$) | $9.09\%$ ($2/22$) |

### Key Empirical Observations:
1. **Zero-Correctness on Truncation in Baselines**: When Condition A or Condition D hits the $768$-token limit (`finish_reason: length`), accuracy is strictly $0.0\%$. In these conditions, hitting the token limit invariably cuts off the mathematical proof before the terminal `\boxed{}` answer can be stated.
2. **Marginal Completion Advantage**: Condition F produced terminal boxed answers on $2$ truncated generations where the final boxed expression happened to be emitted immediately prior to the token limit.
3. **Headroom Asymmetry**: In Condition D, the model must expend generation tokens re-deriving the entire solution from step 1. In Condition F, the valid antecedent steps reside in the prompt context, leaving the entirety of the $768$-token generation budget for the repair and subsequent derivation. Even if total truncation counts appear similar, Condition D faces tighter effective token headroom to reach the final answer.

---

## 3. Dissecting the "State-Preserving" Intervention Package

Condition F must be understood scientifically as a **compound intervention package** comprising four distinct components:

```
Condition F Intervention Package =
  [1. Retained Antecedent Context]   (Prompt includes valid derivation steps)
+ [2. Useful Intermediate Lemmas]    (Eliminates need to discover key intermediate proofs)
+ [3. Continuation Directive]        (Explicit instruction: "preserve valid earlier steps verbatim")
+ [4. Differential Token Headroom]   (Generation starts from step k rather than step 1)
```

### Critical Epistemic Boundary:
- The confirmatory experiment tests the **bundled contrast**:
  $$\tau_{F-D} = \mathbb{E}[Y_i(\text{Package } F) - Y_i(\text{Baseline } D)]$$
- The trial **does not** identify whether $\tau_{F-D}$ is driven primarily by the semantic presence of the lemmas (Component 1 & 2), the meta-prompt instruction to preserve them (Component 3), or the token headroom conservation (Component 4).
- The experiment **does not** claim direct intervention on the model's internal activations, latent cognitive states, or physical KV-cache representations. It evaluates prompt-mediated behavioral recovery under state preservation framing.

---

## 4. Revised Defensible Causal Claims

For all future publications and NeurIPS submissions, the causal claims must adhere to the following certified boundaries:

> **Certified Scientific Claim**:
> *"When presented with a failed derivation, prompting the model with the valid antecedent prefix and instructing it to preserve prior valid steps verbatim (Condition F) yields an observed accuracy improvement over prompting it to discard the attempt and restart from scratch (Condition D). This effect measures the composite benefit of the state-preservation prompt package under matched maximum output limits."*

> **Quarantined / Prohibited Claims**:
> - ❌ *"Token-budget confounding has been definitively ruled out by truncation rate parity."*
> - ❌ *"StateShift directly manipulates the internal neural reasoning state."*
> - ❌ *"The recovery effect is isolated purely to the instruction independently of lemma presence."*

**Phase 3 Audit Verdict**: **PASS WITH DOCUMENTED CORRECTIONS** (Token confounding acknowledged as a bundled component of the intervention package).
