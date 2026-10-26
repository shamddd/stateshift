# StateShift: Research Mission 19 — Defensible Scientific Novelty & Literature Architecture

**Date:** October 26, 2026  
**Auditor Committee:** Independent Literature & Senior NeurIPS Review Directorate  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Preprint: arXiv, Secondary: TMLR)  
**Document Status:** Complete Literature Synthesis  

---

## 1. Executive Summary: The Scientific Niche of StateShift

The rapid scaling of post-training paradigms (RLHF, DPO, PPO, STaR) and test-time search algorithms has placed language model reasoning at the forefront of machine learning research. A central debate in the recent literature (2023–2026) concerns **error correction**:
1. Can language models recognize when they make a mistake?
2. If an error is recognized or pointed out, how should the inference engine orchestrate recovery?

While substantial literature has investigated the *first* question—demonstrating that models cannot reliably self-diagnose reasoning errors without external verification (Huang et al., 2024; Stechly et al., 2024) and introducing Process Reward Models (PRMs) to score individual steps (Lightman et al., 2023; Wang et al., 2024)—the *second* question has remained largely unformalized and treated as an engineering heuristic. When an error is detected at step $K$, existing inference-time search algorithms (e.g., Tree of Thoughts, Monte Carlo Tree Search) face a fundamental architectural choice:
- **Strategy D (Forced Restart / Root Backtracking):** Discard the failed generation and resample a rollout entirely from the root problem prompt.
- **Strategy F (State-Preserving Continuation / Branch Point Recovery):** Retain the pre-verified prefix containing steps $1, \dots, K-1$, prune the erroneous step $K$, and resume rollout generation conditioned on the verified intermediate lemmas.

**The StateShift Contribution:** StateShift provides the first rigorous, pre-registered, matched-cohort causal analysis comparing these two foundational recovery strategies. By evaluating 100 MATH-500 problems across four paired conditions ($A$: Zero-Shot, $D$: Forced Restart, $E$: Explicit Repair, $F$: State-Preserving) using physical GPU inference on `Qwen2.5-Math-7B-Instruct`, StateShift empirically isolates the exact trade-offs of state preservation:
- State preservation achieves an empirical **$+6.00\%$** accuracy advantage over forced restart ($46.0\%$ vs $40.0\%$, with an off-diagonal win/loss odds ratio of $4:1$, $b=8, c=2$).
- State preservation achieves a statistically significant **$+9.00\%$** accuracy advantage over zero-shot baseline ($46.0\%$ vs $37.0\%$, $p = 0.0117$).
- The primary causal drivers of this delta are **Token Budget Amortization** (preventing premature truncation on deep multi-step derivations) and **Attractor Basin Escape** (breaking out of deterministic greedy failure loops).

---

## 2. Comprehensive Comparison with Closest Prior Art (2023–2026)

| Dimension | Self-Correction Literature (Huang et al., 2024; Stechly et al., 2024) | Process Verification Literature (Lightman et al., 2023; Wang et al., 2024) | Test-Time Compute & Search (Snell et al., 2024; Kumar et al., 2024) | **StateShift (This Work)** |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Question** | Can LLMs detect their own errors without external oracle/verifier feedback? | How can models be trained to predict step-by-step correctness probabilities? | How should compute be scaled at test time (Best-of-$N$, MCTS, beam search)? | **Given an error at step $K$, what is the causal impact of state preservation vs restart?** |
| **Error Localization** | Model must self-diagnose from scratch. | PRM scores steps $s_1, \dots, s_t$. | Search policy picks node with highest Q/value. | **Explicitly isolated at step $K$ to study recovery dynamics directly.** |
| **Inference Intervention** | Re-prompt: *"Review your answer and correct errors."* | Ranks rollouts or weights nodes during search. | Expands search tree via resampling or rollout expansion. | **Direct contrast between branch continuation (F) and root restart (D).** |
| **Experimental Design** | Unpaired accuracy comparison across prompts. | Precision/recall on step labels; Best-of-$N$ accuracy. | Aggregate scaling curves vs compute FLOPs. | **Strictly pre-registered within-subject paired cohort ($N=100$, 400 rollouts).** |
| **Key Finding** | Intrinsic self-correction degrades without verifiers ($p < 0.05$ drop). | Step supervision improves search guidance over outcome supervision. | Optimal test-time compute beats parameter scaling. | **Preserving verified prefixes yields $+6.0\%$ over restart via token savings and attractor escape.** |

---

## 3. Deep-Dive Literature Deconstruction

### 1. Huang et al. (ICLR 2024) & Stechly et al. (2024): The Self-Correction Fallacy
- **Prior Finding:** Huang et al. (2024) definitively showed in *"Large Language Models Cannot Self-Correct Reasoning Yet"* that prompting an LLM to find and fix its own errors without ground-truth feedback hurts performance because the model's self-evaluation suffers from the same cognitive blind spots as its initial generation. Stechly et al. (2024) further showed that models hallucinate corrections when prompted repeatedly.
- **StateShift Distinction:** StateShift completely circumvents this fallacy by decoupling *error detection* from *error recovery*. StateShift does not ask the model to guess whether it is wrong; instead, an external cut-point isolates the error, allowing StateShift to measure the pure recovery capacity of the model conditioned on differing historical context states.

### 2. Lightman et al. (NeurIPS 2023) & Wang et al. (ACL 2024): PRMs and Step Supervision
- **Prior Finding:** Lightman et al. (2023) (*PRM800K*) and Wang et al. (2024) (*Math-Shepherd*) demonstrated that process-supervised reward models (PRMs) provide superior credit assignment compared to outcome reward models (ORMs). They demonstrated that PRMs can identify the exact token or step where a derivation goes astray.
- **StateShift Distinction:** While PRM800K established *how to identify* the failing step $K$, it left open the question of *what an agent should do next*. In PRM-guided tree search, implementations often prune the failing node and sample a new path from the parent or restart entirely. StateShift provides the missing empirical foundation for this decision: systematically measuring the performance, token cost, and failure modes of resuming from parent step $K-1$ versus resetting to step $0$.

### 3. Snell et al. (Dec 2024) & Kumar et al. (2024): Test-Time Compute Scaling
- **Prior Finding:** Snell et al. (2024) (*Scaling LLM Test-Time Compute Optimally*) demonstrated that trading compute at inference time—via adaptive search, revision, and verifier scoring—can outperform a $14\times$ larger model. Kumar et al. (2024) trained models via RL to execute multi-turn self-correction trajectories.
- **StateShift Distinction:** StateShift provides a precise mechanistic explanation for *why* test-time compute is efficient when state is preserved:
  - **Token Amortization:** Preserving validated lemmas saves hundreds of generation tokens that would otherwise be wasted re-proving known facts, allowing the model to stay within generation bounds on complex problems.
  - **Basin Hopping:** Forcing a restart from scratch often locks the model into the exact same greedy basin of attraction ($T=0$), whereas injecting the validated prefix re-anchors the hidden state in a trajectory that skirts the error attractor.

---

## 4. Defensible Scope & Boundary of Claims

To withstand the most adversarial peer review at NeurIPS 2027, the manuscript strictly bounds its claims:

1. **What StateShift Claims:**
   - On MATH-500 with `Qwen2.5-Math-7B-Instruct`, preserving intermediate verified lemmas yields a $+6.00\%$ empirical point improvement over forced restart, winning 8 out of 10 discordant problems (odds ratio $4:1$).
   - State preservation is a compound operational intervention: it supplies verified semantic premises, conserves token budget headroom, and alters the initial decoding context.
   - Forcing full restarts carries demonstrable risks: premature truncation due to token budget exhaustion (3 cases) and deterministic recurrence of circular attractor loops (3 cases).
   - State preservation is not uniformly advantageous: preserving long, verbose prefixes can occasionally bias the model into degenerate token repetition loops or over-complicated algebra (2 cases).

2. **What StateShift Does NOT Claim:**
   - StateShift does *not* claim that $+6.00\%$ achieves two-sided statistical significance at $N=100$ ($p = 0.109375 > 0.05$). We explicitly report the exact discrete power ($36.19\%$) and state that $N=100$ is underpowered for a two-sided test of a $+6\%$ delta.
   - StateShift does *not* claim an intrinsic self-correction capability without external verification; all interventions assume external error localization.
   - StateShift does *not* claim that the model's internal weights contain an active recovery planner; the recovery is an emergent consequence of autoregressive continuation conditioned on pruned prefix state.

---
**Summary:** StateShift has a clear, defensible, and unique literature positioning that bridges process verification and inference-time search, providing empirical clarity to a ubiquitous but previously unmeasured search heuristic.
