# StateShift Research Mission 25: Causal Identification and Mechanism Audit

**Author:** Multidisciplinary Independent Scientific Audit Committee  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Audit Target:** Major Scientific Issue M1 (Causal Mechanism Overclaim)  
**Date:** October 27, 2026  
**Status:** Certified & Finalized  

---

## 1. The Core Scientific Defect (Issue M1)

In Mission 24 reporting and the release candidate manuscript draft, the primary confirmatory trial outcome ($\hat{\tau}_{F-D} = -0.43\%, p = 1.000000$) was interpreted as:
> *"an exact dynamical cancellation between two powerful, opposing autoregressive forces: a Reasoning Headroom Advantage (+11 problems where prefix retention prevents 768-token truncation) and a Cognitive Inertia / Deliberation Trap (-12 problems where corrupted prefixes induce recursive verification loops and error propagation)... Net Treatment Effect = Headroom Advantage (+11) - Cognitive Inertia Trap (-12) = -1 \approx 0."*

The Audit Committee finds that this framing constitutes a **severe causal mechanism overclaim**. It confuses **descriptive outcome counts in a $2 \times 2$ contingency table** with **identified causal parameters**.

---

## 2. Formal Causal Identification Framework

### 2.1 The Actual Experimental Estimand
In the confirmatory experiment on $N=231$ held-out MATH-500 problems, each problem $i$ is evaluated under four distinct prompt conditions:
- **Condition A (Zero-Shot Baseline)**: Raw problem prompt $x_i$ decoded greedily from scratch.
- **Condition D (Forced Restart)**: Raw problem prompt $x_i$ decoded greedily from scratch following an intermediate error event.
- **Condition E (Explicit Repair / Neutral Continuation)**: Appending the flawed prefix trajectory $\tau_{i, \text{flawed}}$ followed by neutral continuation instruction.
- **Condition F (State-Preserving Continuation)**: Appending the prefix trajectory $\tau_{i, \text{flawed}}$ up to the error step followed by explicit recovery prompting.

The primary estimand specified in the preregistration protocol is:
$$\tau_{F-D} = \mathbb{E}[Y_i(F) - Y_i(D)]$$
estimated by:
$$\hat{\tau}_{F-D} = \frac{1}{N} \sum_{i=1}^N (Y_{i,F} - Y_{i,D}) = \frac{b - c}{N} = \frac{11 - 12}{231} = -0.004329 \quad (-0.43\%)$$
where $Y_{i,\cdot} \in \{0, 1\}$ represents solution correctness verified against the ground-truth benchmark.

### 2.2 The Bundled Nature of the Intervention
Condition F is an **operational intervention package**:
$$do(\text{Condition F}) = \{\mathcal{S}_{\text{prefix}}\} \;\cup\; \{\mathcal{P}_{\text{recovery}}\} \;\cup\; \{\Delta \mathcal{B}_{\text{token}}\}$$
It simultaneously introduces:
1. **Contextual History ($\mathcal{S}_{\text{prefix}}$)**: Upstream lemmas and the presence of prior reasoning steps.
2. **Prompt Instruction ($\mathcal{P}_{\text{recovery}}$)**: Explicit directive to continue from the specified reasoning stage.
3. **Effective Token Headroom ($\Delta \mathcal{B}_{\text{token}}$)**: Since the prefix occupies prompt tokens rather than generation tokens, the remaining budget within the 768-token ceiling differs from generating the entire proof from scratch.
4. **Attention Anchoring**: The conditioning key-value cache contains the prefix tokens, which autoregressive attention mechanisms attend to during all downstream decoding steps.

Conversely, Condition D provides only the clean prompt $x_i$, requiring all reasoning to be generated within the 768-token output window without any prior context.

### 2.3 The Failure of Factorial Separation
Because the experiment did NOT independently randomize:
- Token budget ($B \in \{768, 2048\}$),
- Prefix validity (sound vs. flawed), and
- Prompt framing (continuation vs. restart),

the experiment identifies **ONLY the net total effect** of the bundled intervention package ($\hat{\tau}_{F-D}$). It **CANNOT** identify the isolated causal contributions of "token headroom" or "cognitive inertia."

---

## 3. The Conflation of Outcome Counts and Causal Mechanisms

In the observed $2 \times 2$ table:
$$\begin{pmatrix} a & c \\ b & d \end{pmatrix} = \begin{pmatrix} 146 & 12 \\ 11 & 62 \end{pmatrix}$$
- **Cell $b = 11$** is simply the count of problems where $Y_{i,D} = 0$ and $Y_{i,F} = 1$.
- **Cell $c = 12$** is simply the count of problems where $Y_{i,D} = 1$ and $Y_{i,F} = 0$.

### 3.1 Why Equating $b=11$ to "Headroom Advantage" is Scientifically Invalid
1. While 8 of the 11 problems in Cell $b$ truncated in Condition D (`finish_reason == 'length'`), 3 problems completed normally (`finish_reason == 'stop'`) and failed due to arithmetic slips during re-derivation.
2. Even among the 8 truncated problems, we cannot claim that Condition F succeeded *solely* because of headroom; Condition F also had access to the valid lemmas in the prefix, which could have provided semantic steering independent of length.
3. Therefore, $b=11$ is an empirical count of discordant successes, NOT a measurement of a "Headroom Force = +11".

### 3.2 Why Equating $c=12$ to "Cognitive Inertia Trap" is Scientifically Invalid
1. While 6 of the 12 problems in Cell $c$ truncated in Condition F (`finish_reason == 'length'`), 5 problems completed normally with wrong answers, and 1 problem truncated after generating an answer.
2. Truncation in Condition F could arise from verbosity induced by the prompt instructions, not necessarily "recursive deliberation loops" or "cognitive inertia."
3. Attributing all 12 failures to an anthropomorphic "Cognitive Inertia" construct labels diverse model generation behaviors with a single unmeasured latent psychological trait.

### 3.3 The Fallacy of the Pseudo-Decomposition Equation
The equation:
$$\text{Net Effect} = \text{Headroom Advantage } (+11) - \text{Cognitive Inertia Trap } (-12) = -1 \approx 0$$
is mathematically circular. Since $b - c = 11 - 12 = -1$ by definition of McNemar's contrast, relabeling $b$ as "Headroom" and $c$ as "Cognitive Inertia" manufactures the appearance of a structural physical law where none was identified.

---

## 4. Remediation Directives for Mission 25

1. **Remove the Pseudo-Equation**: Delete any mathematical representation claiming that the treatment effect is the algebraic difference of two identified mechanism parameters.
2. **Reframe as Exploratory Qualitative Hypotheses**:
   - Present "token headroom savings" and "prefix persistence / attention anchoring" strictly as **plausible explanatory hypotheses** suggested by post-hoc qualitative error analysis.
   - Explicitly disclose that because headroom and prefix content were not independently manipulated, the confirmatory trial does not identify their separate causal contributions.
3. **Use Non-Anthropomorphic, Descriptive Terminology**:
   - Replace "Cognitive Inertia" with "apparent prefix anchoring", "error persistence", or "contextual bias".
   - Replace "Deliberation Trap" with "repetitive verification loops" or "token-budget exhaustion during error correction".
   - Replace "Proven Causal Mechanisms" with "Exploratory Reasoning-Pattern Annotations".
4. **Preserve Objective Trace Re-analysis**: Present the 23 discordant problems with their empirical token counts, finish reasons, and verbatim extracts, clearly separated from speculative interpretations.
