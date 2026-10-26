# StateShift: Research Mission 19 — Causal Identification Final Review

**Audit Date:** October 26, 2026  
**Auditor Committee:** Independent Scientific Review Panel (Causal Inference Directorate)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Preprint: arXiv)  

---

## 1. Executive Summary: The Causal Identification Boundary

The central scientific question of StateShift is:
> *Does preserving valid intermediate reasoning context improve recovery from mathematical reasoning errors relative to forcing a complete restart?*

As an independent causal inference evaluation, we formally audit the causal estimands, DAG structure, potential outcomes, and identification assumptions.

**Causal Directorate Verdict: IDENTIFICATION OF OBSERVABLE INTERVENTION PACKAGE CONFIRMED; IDENTIFICATION OF UNCONFOUNDED LATENT NEURAL STATE REFUTED.**

The experimental contrast $\hat{\tau}_{F-D}$ identifies the causal effect of an **observable, composite intervention package**:
$$\text{Treatment } T = \{ \text{In-Context Lemma Retention} \;+\; \text{Token Budget Headroom} \;+\; \text{Continuation Instruction} \}$$
relative to a forced-restart control. Because autoregressive language models represent state exclusively through the sequence of conditioning tokens and their resulting key-value (KV) cache activations, the experiment does **not** isolate an internal, token-independent latent activation state.

To satisfy the highest standards of scientific integrity, the manuscript must define StateShift as an empirical evaluation of **preserving intermediate reasoning context**, strictly avoiding unsupported claims of internal neural-state discovery.

---

## 2. Exact Experimental Prompt Decomposition

To understand what is causally manipulated, we inspect the exact prompt templates across all four conditions:

```
[Problem Stem X_i] (Shared across all 4 conditions)
  |
  +--> Condition A (Zero-Shot):
  |      [X_i] + "\n\nSolve the problem step by step and present your final answer in \boxed{}."
  |
  +--> Condition D (Forced Restart Control):
  |      [X_i] + "\n\nHere is an attempt so far:\n" + [Prefix_Steps_1_to_k] + 
  |      "\n\nPlease disregard and discard the above attempt entirely. It contains errors. "
  |      "Start your solution completely from scratch from the beginning."
  |
  +--> Condition E (Explicit Repair):
  |      [X_i] + "\n\nHere is the derivation so far:\n" + [Prefix_Steps_1_to_k] +
  |      "\n\nThe last step above contains an error. Identify and correct the mistake, "
  |      "then finish the solution."
  |
  +--> Condition F (State-Preserving Recovery):
         [X_i] + "\n\nHere is the derivation so far:\n" + [Valid_Prefix_Steps_1_to_k_minus_1] +
         "\n\nYou must preserve all valid earlier steps and recover from the identified error. "
         "Continue the reasoning directly from the last valid step without restarting."
```

---

## 3. Structural Causal Model & Confounder Deconstruction

```
                      +---------------------------------------+
                      |     Intervention T (Cond F vs D)      |
                      +-------------------+-------------------+
                                          |
        +---------------------------------+---------------------------------+
        |                                 |                                 |
        v                                 v                                 v
+-----------------------+     +-----------------------+     +-----------------------+
|  Mechanism 1:         |     |  Mechanism 2:         |     |  Mechanism 3:         |
|  Lemma In-Context     |     |  Token Budget         |     |  Instruction          |
|  Presence             |     |  Amortization         |     |  Pragmatics           |
|  (Prefix tokens in    |     |  (F saves 250+ tokens |     |  (Positive directive  |
|   KV-cache attention) |     |   towards 768 limit)  |     |   vs negative erase)  |
+-----------+-----------+     +-----------+-----------+     +-----------+-----------+
            |                             |                             |
            +-----------------------------+-----------------------------+
                                          |
                                          v
                            +---------------------------+
                            |  Outcome Y: Task Success  |
                            +---------------------------+
```

### Mechanism 1: Lemma In-Context Presence (Information Scaffolding)
In Condition F, the valid derivation up to step $k-1$ is already written in the context window. The self-attention mechanism can directly retrieve intermediate constants, factored forms, or geometric relations without re-computing them. In Condition D, the model is commanded to discard this information, forcing it to spend probability mass re-generating these tokens.

### Mechanism 2: Token Budget Amortization (Effective Horizon)
Both Condition D and Condition F share the identical maximum generation ceiling: $\text{max\_tokens} = 768$.
- In Condition F, the model begins generating at step $k$. It has the entire 768-token budget available solely for the remaining derivation.
- In Condition D, the model begins generating at step 1. If re-deriving steps $1 \dots k$ consumes 300 tokens, Condition D has only $768 - 300 = 468$ tokens remaining.
- **Empirical Proof:** In 3 of the 8 Condition F wins (`math500_026`, `math500_092`, `math500_093`), Condition D failed specifically by hitting the 768-token limit (`status: TRUNCATED`), whereas Condition F completed within budget. This proves that token budget amortization is a primary physical mediator of the treatment effect.

### Mechanism 3: Instruction Pragmatics (Negative Constraints)
Condition D uses a negative constraint (*"disregard and discard the above attempt entirely"*). In autoregressive models, suppressing attention to tokens that remain physically present in the context window creates interference. Condition F provides a positive, constructive continuation directive.

---

## 4. Estimable vs Non-Estimable Quantities

| Causal Quantity | Estimable from Existing Data? | Evidence / Justification |
| :--- | :---: | :--- |
| **Complete Intervention Package Effect** ($\tau_{F-D}$) | **YES** | Directly identified by the paired within-problem randomized trial: $\hat{\tau}_{F-D} = +6.00\%$. |
| **Baseline Recovery Effect over Zero-Shot** ($\tau_{F-A}$) | **YES** | Directly identified: $\hat{\tau}_{F-A} = +9.00\%$ ($p = 0.0117$). |
| **Mediation by Token Budget Exhaustion** | **PARTIALLY** | Directly measurable: 3/8 F-wins were mediated by length truncation in D. |
| **Pure Latent Neural State Activation Effect** | **NO** | Cannot be identified because prompt tokens and latent activations are intrinsically co-manipulated. |

---

## 5. Mandatory Manuscript Phrasing Guidelines

To align the text with causal reality, the manuscript must adopt the following standardized terminology:

- **Approved Phrasing:**
  > *"StateShift evaluates the causal effect of preserving useful intermediate reasoning context during recovery from incorrect mathematical trajectories relative to forcing a complete restart."*
  > *"Our findings demonstrate that state preservation acts as an operational compute amortizer: retaining verified lemmas in context frees up token capacity and prevents deterministic attractor trapping."*

- **Prohibited Phrasing:**
  > ~*"StateShift proves that post-training induces an internal latent neural state recovery mechanism independent of context tokens."*~ (FALSIFIED: no internal activation interventions performed).
  > ~*"State preservation is proven to be universally causally superior."*~ (FALSIFIED: Condition D outperformed Condition F in 2 instances).
