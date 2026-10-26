# StateShift: Research Mission 18 — Causal Identification & Confounder Audit

**Audit Date:** October 26, 2026  
**Auditor Committee:** Independent Scientific Audit Committee (Causal Inference Directorate)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue:** NeurIPS 2027 Main Conference (Secondary: TMLR)  

---

## 1. Executive Summary: The Causal Identification Problem

The core scientific thesis of StateShift is that *reasoning recovery in post-trained language models is state-dependent*: preserving upstream reasoning state (Condition F) enables models to recover from errors where forced restarts (Condition D) fail.

As an independent causal inference review, we formally evaluate the structural causal model (SCM), treatment definitions, potential outcomes, and potential confounders underlying this claim.

**Causal Directorate Verdict: INTERVENTION PACKAGE EFFECT CONFIRMED; PURE LATENT STATE ISOLATION UNIDENTIFIED.**

The experimental contrast $\hat{\tau}_{F-D}$ does **not** isolate an unconfounded, latent neural state in isolation from token-level representations. In autoregressive Transformers, the "state" at step $t$ is mathematically and functionally identical to the key-value (KV) activations of the prompt and prefix tokens. Consequently, the observed $+6.00\%$ empirical effect is an **intervention package effect** consisting of:
1. Token-level lemma retention in the context window.
2. Amortized token budget toward the generation ceiling.
3. Natural language instruction framing differences.

To satisfy rigorous NeurIPS review standards, the revised manuscript must explicitly delineate this causal identification boundary and refrain from claiming unconfounded latent state discovery.

---

## 2. Formal Structural Causal Decomposition

Let each problem instance $i \in \{1, \dots, N\}$ have:
- $X_i$: The mathematical problem specification.
- $L_i^*$: The set of valid upstream lemmas required to reach intermediate cut-point $K$.
- $E_i$: An error introduced at step $K$.
- $Y_i \in \{0, 1\}$: Binary task success (correct final answer).

### Condition F (State-Preserving Recovery):
The input context presented to the model is:
$$C_F = [X_i, L_i^*, \text{Prompt}_F]$$
where $\text{Prompt}_F$ instructs the model: *"You must preserve all valid earlier steps and recover from the identified error. Continue the reasoning directly from the last valid step without restarting."*

### Condition D (Forced Restart Control):
The input context presented to the model is:
$$C_D = [X_i, L_i^*, E_i, \text{Prompt}_D]$$
where $\text{Prompt}_D$ instructs the model: *"Please disregard and discard the above attempt entirely. It contains errors. Start your solution completely from scratch from the beginning."*

### Condition A (Zero-Shot Baseline):
The input context is:
$$C_A = [X_i]$$

---

## 3. Threat Analysis: Four Major Confounders

```
                   +----------------------------------+
                   |    Treatment: Condition F vs D   |
                   +-----------------+----------------+
                                     |
         +---------------------------+---------------------------+
         |                           |                           |
         v                           v                           v
+------------------+       +-------------------+       +--------------------+
| 1. Token Budget  |       | 2. Information    |       | 3. Instruction     |
|    Amortization  |       |    Asymmetry      |       |    Pragmatics      |
| (F saves ~250 tok|       | (F has lemmas in  |       | (Restart directive |
|  before ceiling) |       |  KV context)      |       |  induces entropy)  |
+--------+---------+       +---------+---------+       +---------+----------+
         |                           |                           |
         +---------------------------+---------------------------+
                                     |
                                     v
                       +---------------------------+
                       | Outcome Y: Task Accuracy  |
                       +---------------------------+
```

### Confounder 1: Information Asymmetry (Lemma In-Context Presence)
- **Mechanism:** In Condition F, valid preliminary deductions $L_i^*$ are already written in the prompt. The attention mechanism can directly attend to these tokens as verified premises. In Condition D, although the erroneous derivation is present in the prompt history, the model is told to discard it and re-derive $L_i^*$.
- **Causal Implication:** Condition F's advantage could stem simply from *having intermediate lemmas provided in context* (in-context scaffolding) rather than an intrinsic capability of the neural network to recover internal computational states.

### Confounder 2: Token Budget Exhaustion (Effective Search Horizon)
- **Mechanism:** Both Condition D and Condition F operate under an identical maximum generation ceiling of 768 tokens.
  - In Condition F, the model begins generating at step $K$. It has all 768 tokens available for the *downstream* derivation.
  - In Condition D, the model must expend tokens re-writing steps $1$ through $K$. If re-deriving steps $1 \dots K$ takes 350 tokens, Condition D only has $768 - 350 = 418$ tokens remaining to solve the problem.
- **Empirical Evidence from Phase 4:**
  In 3 of the 8 Condition F wins (`math500_026`, `math500_092`, `math500_093`), Condition D failed specifically by hitting the token limit (`completion_status: TRUNCATED`), whereas Condition F completed within the budget.
- **Causal Implication:** A significant fraction of the $+6.00\%$ effect is directly mediated by token budget headroom rather than reasoning logic per se.

### Confounder 3: Instruction Pragmatics & Negative Constraint Overhead
- **Mechanism:** The negative directive in Condition D (*"disregard and discard the above attempt entirely"*) requires the model to actively suppress attention to the prefix tokens in its context window. Language models are known to struggle with negative constraints ("don't think of a pink elephant"), leading to attention interference.
- **Causal Implication:** Condition D might suffer an artificial penalty due to the difficulty of ignoring preceding tokens, exaggerating Condition F's relative advantage.

### Confounder 4: Context Window Compression vs Prefix Caching
- **Mechanism:** Modern inference servers cache KV-activations for shared prefixes. If Condition F benefits from pre-computed prefix activations, it is mathematically processing a conditioned subspace.

---

## 4. Methodological Defense & Scientific Framing

While the above confounders prevent claiming a pure, isolated latent activation effect, StateShift's design remains practically and scientifically valuable if framed correctly:

1. **The System-Level Intervention Package:**
   In real-world LLM deployments (e.g., agentic workflows, long-horizon math solvers, code generation), **state preservation IS implemented via prefix retention and token continuation**. An agent that preserves its valid scratchpad and resumes from an error is vastly more efficient and reliable than an agent that reboots its entire session.
2. **Comparison with Zero-Shot Baseline ($\hat{\tau}_{F-A} = +9.00\%$):**
   Condition F significantly outperforms Zero-Shot ($p = 0.0117$), proving that prefix conditioning provides a net benefit over an unconditioned model, even after accounting for the risk of error propagation.
3. **Manuscript Transparency Requirement:**
   The manuscript must dedicate an explicit subsection in Section 5 (Discussion / Limitations) to:
   - Defining the intervention as an **operational state-conditioning package**.
   - Decomposing the effect into lemma retention, token amortization, and search continuation.
   - Acknowledging that future work using activation patching (e.g., Interchange Intervention Training) or KV-cache manipulation is needed to isolate pure non-token representation states.
