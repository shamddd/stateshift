# StateShift Research Mission 14 — Deliverable 11: Adversarial Scientific Review

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Reviewing Role**: Skeptical NeurIPS Senior Reviewer / Meta-Reviewer  
**Date**: October 25, 2026  
**Verdict**: **REJECT (NeurIPS 2027 Main Track in Current State) / MAJOR REVISION (TMLR)**  

---

## 1. Summary of Submission & Claimed Contributions

The paper investigates error recovery in post-trained mathematical reasoning models, arguing that models do not perform surgical in-place error repair, but instead rely on implicit context abandonment and restarting. It further claims that downstream dependency contamination governs the choice between restarting and compounding errors, and that state preservation provides no compute efficiency gains.

---

## 2. Decisive Methodological Criticisms (The Reviewer's Case)

### Critique 1: Dataset Provenance & Missing Raw Generations
The most critical vulnerability is computational reproducibility. The primary 7B experiment was prematurely aborted due to a 30-minute client SSH timeout after 143 of 400 rollouts, and the raw generation outputs on the ephemeral cloud pod were erased upon automated shutdown. Only 4 smoke-test rollouts and 2 live traces physically survive in the local repository. Submitting aggregate tables and p-values without the underlying raw text violates NeurIPS and TMLR reproducibility standards.

### Critique 2: Evaluator Label Leakage (Evaluator v4)
In `strict_recovery_evaluator_v4.py` (line 196), the evaluation logic explicitly includes `or condition == "explicit_restart"` when assigning the `is_explicit_restart` label. This means the model's behavioral classification was partially hard-coded by prompt condition rather than evaluated from output tokens. While the authors corrected this in Evaluator v5, the historical claims in Mission 13 were tainted by this confound.

### Critique 3: Observational Correlation vs. Causal Mechanism
The reported correlation between dependency contamination and restart probability ($r_s = +0.264$) is purely observational. Early error steps inherently have both higher contamination and shorter preceding prefixes. Without a controlled counterfactual intervention that holds error position and prefix length constant while manipulating DAG dependency structure, the authors cannot claim a causal mechanism.

### Critique 4: Single Model Family (Qwen2.5-Math)
All empirical evidence is restricted to the Qwen2.5-Math lineage (1.5B and 7B). Qwen models share common pre-training data, architectural choices, and RLVR post-training recipes. The observed tendency to restart rather than repair may simply be an idiosyncratic artifact of Qwen's training mixture, rather than a universal property of autoregressive reasoning LLMs.

### Critique 5: Over-Interpretation of Non-Significant Equivalence
In Mission 13, the authors suggested that state preservation and restarting are "computationally equivalent" because a paired t-test was non-significant ($p = 0.299$). This is an elementary statistical fallacy. TOST analysis on the sample size cannot establish equivalence within a $\pm 5\%$ margin.

---

## 3. Concrete Falsification Experiments Required for Acceptance

To achieve a consensus Accept (Score 7+) at NeurIPS 2027, the authors must execute:
1. **Full-Cohort Detached Execution**: Execute the frozen 100-problem manifest (400 rollouts) to completion using the repaired detached orchestrator (`RobustCloudOrchestratorV6`), preserving all 400 raw JSONL records locally.
2. **Multi-Lineage Replication**: Run the exact same 100-problem manifest on a distinct model architecture, such as `deepseek-ai/deepseek-math-7b-instruct` or `meta-llama/Llama-3.1-8B-Instruct`.
3. **Controlled Counterfactual DAG Experiment**: Test 20 problems where error step index $k$ and prefix length are held identical while altering the downstream dependency graph (high vs. low branch contamination).
4. **Independent Human Validation**: Complete the 60-trace double-blind human annotation packet to establish verified precision and recall for Evaluator v5.
