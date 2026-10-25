# 01 Experiment Pre-Registration: Frontier 7B Mathematical Reasoning Recovery & Dependency Contamination

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Investigation**: Research Mission 13 — Primary 400 & Secondary 800 Cloud Replication  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Pre-Registration Date**: October 25, 2026 (Pre-Execution Freeze)  
**Primary Manifest**: [`manifests/primary_100_manifest.json`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_13/manifests/primary_100_manifest.json) (400 requests)  
**Replication Manifest**: [`manifests/replication_200_manifest.json`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_13/manifests/replication_200_manifest.json) (800 requests)  
**Status**: PRE-REGISTERED & CRYPTOGRAPHICALLY FROZEN  

---

## 1. Abstract & Scientific Scope

This pre-registration defines the confirmatory experimental protocol for StateShift Research Mission 13. We investigate the cognitive and computational mechanics of autoregressive mathematical reasoning models when confronted with corrupted intermediate derivation states. Specifically, we evaluate whether scaling model capacity to 7 billion parameters (`Qwen/Qwen2.5-Math-7B-Instruct`, native unquantized bfloat16) unlocks **genuine state-dependent local repair**, or whether models persist in **implicit restarting** and error cascading.

All hypotheses, experimental conditions, evaluation criteria, dependency contamination formulas, token economics metrics, and statistical analysis plans are frozen herein prior to any GPU execution.

---

## 2. Research Questions & Pre-Registered Hypotheses

### 2.1 Primary Scientific Question
When a 7B mathematical reasoning model encounters an incorrect intermediate reasoning state, does it recover by mathematically repairing that state while preserving valid antecedents, or by abandoning the state and recomputing the solution from scratch?

### 2.2 Pre-Registered Hypotheses
- **$H_1$ (Accuracy Equivalence / Superiority)**:
  Forced restarting (Condition D) achieves equal or superior final-answer accuracy compared to state-preserving repair prompting (Condition F):
  $$\text{Acc}(D) \ge \text{Acc}(F)$$
- **$H_2$ (Persistence of Implicit Restarts at 7B Scale)**:
  Under state-preserving repair prompting (Condition F), 7B models will continue to exhibit low or zero genuine in-place local repair ($\le 5\%$), predominantly resolving errors through implicit line-1 restarting.
- **$H_3$ (Dependency Contamination Effect)**:
  Higher downstream mathematical dependency contamination ($\text{contamination\_fraction}$) negatively correlates with genuine repair and increases the probability of restarting or derivation collapse:
  $$\rho(\text{contamination\_fraction}, \text{restart\_probability}) > 0$$
- **$H_4$ (Token Economy of State Preservation)**:
  Condition F reduces total generated tokens relative to Condition D ($\Delta_{\text{tokens}} = \text{tokens}_D - \text{tokens}_F > 0$), but this generated token reduction does not guarantee end-to-end wall-clock savings due to prompt prefill overhead.

---

## 3. Four-Condition Matched Within-Subject Design

Every problem in the cohort is evaluated across four strictly matched conditions:

1. **Condition A (Clean Baseline)**:
   The model solves the original problem statement step-by-step with zero injected corruption (`prefix_type = none`).
2. **Condition D (Forced Restart)**:
   The model is provided the problem statement and the corrupted prefix, but explicitly instructed to discard the previous attempt and solve again completely from scratch (`prefix_type = recovery`).
3. **Condition E (Explicit Local Repair)**:
   The model is provided the problem statement and corrupted prefix, informed that an error exists, and instructed to identify the error, surgically correct it, and continue to the final answer (`prefix_type = recovery`).
4. **Condition F (State-Preserving Repair)**:
   The model is provided the problem statement and corrupted prefix, and strictly instructed to preserve all valid earlier steps verbatim, correct only the flawed step, and continue to the final answer (`prefix_type = recovery`).

---

## 4. Evaluator v4 & Seven-Strategy Recovery Taxonomy

All generations are scored by **Mathematical Recovery Evaluator v4** ([`evaluation/strict_recovery_evaluator_v4.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_13/evaluation/strict_recovery_evaluator_v4.py)), which maps each trace into a mutually exclusive operational taxonomy:

1. **Genuine Local Mathematical Repair (`STATUS_CLEAN_RECOVERY`)**:
   Model preserves valid prefix lines, localizes the corrupted step, states a mathematically verified contradiction or replacement matching ground truth, connects the repair into the downstream DAG, and achieves the verified correct final answer.
2. **Explicit Restarting (`STATUS_RESTART` with explicit markers)**:
   Model outputs conversational phrases declaring a complete restart (e.g., *"Starting over"*, *"Let us re-solve from the beginning"*) and re-derives from Step 1.
3. **Implicit Restarting (`STATUS_RESTART` with implicit re-derivation)**:
   Model does not declare a restart, but silently discards the prefix state and re-executes the problem derivation from line 1.
4. **Partial Recomputation (`STATUS_PARTIAL_RECOMPUTE`)**:
   Model backtracks several steps prior to the error and re-derives an alternative intermediate trajectory.
5. **Blind Copying (`STATUS_UNRESOLVED_CONTAMINATED` with copying)**:
   Model copies the corrupted assertion without flagging it and propagates the mathematical error downstream.
6. **Correct Answer Without Verified Repair (`LUCKY_GUESS_OR_ALTERNATIVE_PATH`)**:
   Model arrives at the correct final answer via an alternative formula, circumvention, or fortunate guess while leaving the contaminated step unrepaired.
7. **Unverifiable Reasoning Behavior (`UNVERIFIED_OR_AMBIGUOUS`)**:
   Traces with malformed syntax, unparseable expressions, or ambiguous derivations.

---

## 5. Dependency Contamination Metric Specification

For each problem, we construct the step dependency DAG and compute:
$$\text{contamination\_fraction} = \begin{cases} 
\frac{\text{number\_of\_downstream\_dependent\_steps}}{\text{number\_of\_downstream\_steps}}, & \text{if downstream steps} > 0 \\ 
0.0, & \text{otherwise} 
\end{cases}$$

- **`downstream_steps_total`**: Number of reasoning steps following the corrupted step in the canonical reference derivation.
- **`downstream_dependent_steps`**: Count of downstream steps that topologically depend on the variable, equation, or assertion established in the corrupted step.
- **`dependency_depth`**: The length of the longest directed path from the corrupted step to the final conclusion node.

---

## 6. Repair Economics & Efficiency Metrics

1. **Paired Token Savings**:
   $$\Delta_{\text{tokens}, i} = \text{tokens}_{D, i} - \text{tokens}_{F, i}$$
2. **Accuracy-Adjusted Computational Efficiency**:
   $$\text{Efficiency} = \frac{\sum_{i=1}^N \mathbf{1}(\text{Correct}_i)}{\sum_{i=1}^N \text{tokens}_i} \times 100{,}000 \quad [\text{Correct Answers per } 100\text{k Generated Tokens}]$$

---

## 7. Statistical Inference & Multiple Testing Protocol

- **Primary Contrast**: McNemar's exact test on paired binary outcomes for Condition F vs. Condition D ($N=100$ in Primary; $N=300$ pooled).
- **Equivalence Testing**: Two One-Sided Tests (TOST) against an equivalence margin $\Delta_{\text{eq}} = \pm 10.0$ percentage points ($\alpha = 0.05$).
- **Token Differences**: 10,000-resample non-parametric bootstrap percentile 95% confidence intervals, complemented by paired $t$-test and Wilcoxon signed-rank tests.
- **Zero Observed Successes**: Exact Clopper-Pearson 95% binomial confidence bounds:
  $$p_U = 1 - 0.025^{1/N}$$
- **Operator-Level Heterogeneity**: Two-way ANOVA and Benjamini-Hochberg False Discovery Rate (FDR) control at $q = 0.05$ across all 10 error operators (`OP01`–`OP10`).

---

## 8. Financial and Hardware Boundaries

- **Target Hardware**: NVIDIA GeForce RTX 4090 (24 GB VRAM) on RunPod Secure Cloud ($0.89/hr) or RTX A5000 ($0.27/hr).
- **Target Spending**: **$2.00–$2.50 USD**.
- **Maximum Authorized Spending**: **$3.00 USD** (Hard ceiling enforced by external watchdog).
- **Pod Limit**: Strictly $\le 1$ GPU pod instance. Zero auto-restart. Zero secondary pods. Zero fine-tuning or training.
- **Preserved Balance**: $\ge \$7.00$ preserved on account balance.
