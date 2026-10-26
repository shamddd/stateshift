# StateShift: Research Mission 19.1 — Final Causal and Mechanistic Boundaries

**Date:** October 26, 2026  
**Auditor:** Causal Inference & Methodology Directorate  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target:** Explicit Scientific Boundaries for arXiv Release Candidate  

---

## 1. What the Evidence Formally Identifies

To prevent misleading claims or over-interpretation of causal mechanisms, the Directorate evaluated the exact causal estimands identified by the StateShift experimental designs:

| Mechanism / Effect | Formally Identified by Evidence? | Empirical Grounding | Limitations & Non-Identified Dimensions |
| :--- | :---: | :--- | :--- |
| **1. Operational Intervention-Package Effect** | **YES (IDENTIFIED)** | Comparing Condition F (continuation from branch point) vs Condition D (restart from root) identifies the total causal effect of the composite operational policy: $do(F) - do(D) = +6.00\%$. | Represents an end-to-end inference policy; does not isolate pure latent activations from prompt text. |
| **2. Reasoning-Context Retention Effect** | **YES (IDENTIFIED)** | In Condition F, the model retains the pre-verified steps $1, \dots, K-1$ in its prompt context. This directly identifies the behavioral effect of prefix conditioning. | Because context is provided via tokens in the prompt, it bundles semantic premises with KV-cache states. |
| **3. Token Budget Amortization Effect** | **YES (IDENTIFIED)** | Trajectory audits prove that re-deriving preliminary steps consumes $300\text{--}500$ tokens, causing Condition D to truncate at 768 tokens in 3 of 8 discordant wins (`026`, `092`, `093`). | Confounded with problem difficulty; occurs specifically on deep multi-step derivations. |
| **4. Circular Attractor Avoidance Effect** | **YES (IDENTIFIED)** | Under greedy decoding ($T=0$), restarting from the prompt deterministically locks the model into prompt-level failure basins (`012`, `068`, `071`). State preservation breaks this basin. | Specific to low-temperature/greedy decoding; stochastic sampling ($T>0$) exhibits different attractor dynamics. |
| **5. Checkpoint-Dependent Interaction Gain** | **YES (IDENTIFIED in Study 1)** | The difference-in-differences contrast $\Gamma_{256} = +11.76\text{ pp}$ isolates excess recovery gains over baseline forward proficiency growth ($p < 10^{-20}$). | Derived from row-level outcome tables across checkpoints of DeepScaleR-7B. |
| **6. Latent Internal Neural-State Preservation** | **NO (NOT IDENTIFIED)** | StateShift manipulates prompt-level token context, not internal hidden states in isolation from input tokens. | **MUST NOT BE CLAIMED.** Proving latent activation manipulation requires internal intervention techniques (e.g., activation patching or IIT). |

---

## 2. Decomposition of the Operational Intervention Package

In autoregressive Transformer models, the mathematical state at generation step $k$ is fully determined by the sequence of conditioning tokens $x_{1:k}$:
$$P(x_{k+1} \mid x_{1:k}; \theta) = \text{Softmax}(W_u h_k)$$
where $h_k$ is the final hidden activation vector computed over the prompt and prefix tokens.

Therefore, Condition F represents a **bundled operational intervention**:
$$do(\text{Condition F}) = \underbrace{\{\mathcal{S}_{1:k-1}\}}_{\text{Valid Semantic Lemmas}} \;\cup\; \underbrace{\{\Delta \mathcal{B}_{\text{token}}\}}_{\text{Token Headroom Conservation}} \;\cup\; \underbrace{\{\mathcal{P}_{\text{continue}}\}}_{\text{Continuation Framing}}$$

### Distinguishing Behavioral Evidence from Internal Mechanistic Inference:
- **Behavioral Evidence (What we observe):** Condition F achieves a $73\%$ success rate vs $67\%$ for Condition D ($+6.00\%$, odds ratio $4:1$), and $+9.00\%$ over Zero-Shot ($73\%$ vs $64\%$, $p = 0.0117$).
- **Mechanistic Reality:** This advantage is mediated by prompt-level token conservation and prompt-induced basin displacement.
- **Scientific Guardrail:** The paper must **never claim** that StateShift proves "internal cognitive state retention" independent of prompt text. State preservation in standard LLM inference is achieved by providing the verified prefix in context.

---

## 3. Negative Regimes of State Preservation

A rigorous causal evaluation must report negative regimes where the intervention fails:
- In two problems (`math500_014` and `math500_052`), Condition D succeeded while Condition F failed ($c = 2$).
- **Mechanism of Failure:** Preserving a lengthy, verbose scratchpad biased the model into a degenerate repetitive loop (`math500_014`: `} } } } ...`) or overly complex decimal manipulations (`math500_052`), whereas wiping the context allowed Condition D to find an immediate Pythagorean shortcut.
- **Causal Conclusion:** State preservation is not uniformly optimal; it carries a distinct risk of **prefix bias and error entrenchment**.
