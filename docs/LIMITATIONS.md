# Project StateShift: Scientific Limitations & Scope of Validity

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training

---

## 1. Experimental Sample Size & Statistical Power

* **Sample Size**: Study 2 evaluates $N = 100$ problems from the MATH-500 benchmark under 4 conditions (400 prompt-controlled generations).
* **Observed Effect**: Condition F ($73.0\%$) vs. Condition D ($67.0\%$) exhibits an effect of $\hat{\tau}_{F-D} = +6.00\text{ percentage points}$ with an off-diagonal recovery odds ratio of $4:1$ ($b=8, c=2$).
* **Exact Discrete P-Value**: The exact two-sided McNemar test yields $p = 0.109375$ (exact one-sided $p = 0.054688$). At the conventional significance threshold $\alpha = 0.05$, the null hypothesis cannot be rejected.
* **Power Constraint**: The unconditional statistical power at $N = 100$ for an effect of $+6.0\%$ with discordant rate $q = 0.10$ is **$36.20\%$** (Type II error rate = $63.80\%$). A sample size of $N = 231$ is required to attain $80.0\%$ power.
* **Scientific Verdict**: Study 2 is an exploratory discovery trial indicating promising directionality, rather than a definitive confirmatory demonstration. An adequately powered confirmatory trial ($N \ge 231$) is recommended before drawing definitive conclusions.

---

## 2. Data Provenance & Trace Availability in Study 1

* **Study 1 Data**: The historical 29,056-rollout dataset across DeepScaleR-7B checkpoints ($N=454$ problem pairs) is preserved as an outcome-level tabular dataset (`controlled_endpoint_outcomes.csv`).
* **Absent Text Generations**: The raw token-by-token generation logs for these 29,056 historical rollouts were not archived on disk. Consequently, while all summary statistics ($\Gamma_{256} = +11.76\text{ pp}$, $p = 1.05 \times 10^{-22}$), clustered standard errors, and token lengths are 100% reproducible, individual text responses cannot be inspected or reconstructed.

---

## 3. Model Architecture & Family Scope

* **Evaluated Model**: Physical GPU experiments in Study 2 were conducted exclusively on `Qwen/Qwen2.5-Math-7B-Instruct`. Study 1 analyzed the `DeepScaleR-7B` lineage (itself fine-tuned from DeepSeek-R1-Distill-Qwen-1.5B/7B).
* **Scope Bounding**: Findings cannot be directly extrapolated to non-Qwen architectures (e.g., Llama-3, Gemma-2, Claude, GPT-4o, OpenAI o1) without empirical cross-architecture replication.

---

## 4. Prompt Intervention vs. Latent Model Weight Modification

* **Nature of Intervention**: Condition F operates strictly at the prompt level:
  $$do(F) = \{\text{intermediate lemmas}\} \cup \{\text{contextual headroom}\} \cup \{\text{continuation scaffold}\}$$
* **Mechanistic Boundary**: While prompt scaffolding directs the model's attention to intermediate reasoning states, it does not directly modify internal transformer weights, attention biases, or KV cache activations.
