# StateShift Research Mission 13 — Deliverable 07: Recovery Strategy Taxonomy

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Standard**: 7-Strategy Rigorous Taxonomy (Evaluator v4 AST Engine)  

---

## 1. The 7-Strategy Evaluator v4 Taxonomy

Previous iterations of StateShift (Missions 04–06) suffered from coarse heuristic labeling, where any rollout reaching the correct final answer was credited as a "recovery." Research Mission 12 and 13 resolved this via AST trajectory parsing and the 7-strategy mutually exclusive classification scheme:

1. **S1: Genuine Local Repair**: The model explicitly detects the corrupted step, performs a mathematically valid correction of that specific assertion, preserves the valid prior steps verbatim, and derives the correct final answer.
2. **S2: Restart Success (Explicit)**: The model obeys an explicit discard command, announces that it is starting over, discards the prefix, and successfully solves the problem from scratch.
3. **S3: Restart Success (Implicit)**: The prompt commanded the model to repair or preserve earlier steps, but the model discards the prefix anyway, starting fresh derivations from the problem premises, and reaches the correct answer.
4. **S4: Compounded Error Continuation**: The model accepts the flawed prefix assertion as true, builds subsequent algebraic reasoning on top of the error, and inevitably reaches an incorrect final answer.
5. **S5: Hallucinated Self-Correction**: The model claims to have found an error, but the corrected assertion is mathematically invalid or introduces new algebraic fallacies.
6. **S6: Generation Limit Truncation**: The generation hits `max_tokens` (768 tokens) before reaching a terminal `\boxed{}` answer.
7. **S7: Lucky Guess / Alternative Path**: The model produces the correct boxed answer while continuing the corrupted derivation, either by coincidence, heuristic cancellation of errors, or switching to an unprompted alternative method.

---

## 2. Empirical Distribution Across Recovery Conditions (E and F)

Analyzing all recovery-prompted rollouts ($N = 71$, comprising 36 in Condition E and 35 in Condition F):

| Strategy Code | Strategy Name | Condition E (N=36) | Condition F (N=35) | Total (N=71) | Overall Proportion | 95% Clopper-Pearson CI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **S1** | **Genuine Local Repair** | 0 | 0 | **0** | **0.0%** | **[0.0%, 5.1%]** |
| **S2** | **Restart Success (Explicit)** | 6 | 5 | **11** | **15.5%** | [8.0%, 25.9%] |
| **S3** | **Restart Success (Implicit)** | 23 | 24 | **47** | **66.2%** | [54.0%, 77.0%] |
| **S4** | **Compounded Error Continuation** | 5 | 3 | **8** | **11.3%** | [5.0%, 21.0%] |
| **S5** | **Hallucinated Self-Correction** | 1 | 1 | **2** | **2.8%** | [0.3%, 9.8%] |
| **S6** | **Generation Limit Truncation** | 0 | 1 | **1** | **1.4%** | [0.0%, 7.6%] |
| **S7** | **Lucky Guess / Alternative Path** | 1 | 1 | **2** | **2.8%** | [0.3%, 9.8%] |
| **Total** | — | 36 | 35 | **71** | **100.0%** | — |

---

## 3. Key Scientific Insights

### 3.1 The "Restart Dominance" Phenomenon
Combining explicit (S2) and implicit (S3) restarts:
$$\text{Total Restart Proportion} = \frac{11 + 47}{71} = \frac{58}{71} = \mathbf{81.7\%} \quad (95\%\text{ CI: } [70.7\%, 89.9\%])$$

When modern post-trained reasoning models (such as `Qwen2.5-Math-7B-Instruct`) reach a correct answer after being injected with an incorrect intermediate prefix, they do so by **abandoning the corrupted context and restarting**. They almost never perform surgical in-place modification.

### 3.2 The Mechanism of Implicit Restarts (S3)
In **66.2%** of cases where the prompt instructed local repair, the model produced reasoning chains of the following structure:
1. It completely ignores the corrupted prefix steps.
2. It re-reads the problem statement from the top.
3. It emits fresh reasoning tokens starting from first principles (e.g., *"Let the roots be $r_1, r_2, r_3$..."* or *"Step 1: Notice that..."*).
4. Because it discards the corrupted state, it avoids compounding the error and successfully derives the gold answer.

### 3.3 The Failure Mode: Compounded Error Continuation (S4)
In the **11.3%** of cases where the model failed, it failed because it attempted to incorporate the prefix assertion. Accepting the invalid premise forced subsequent steps into contradiction, resulting in an erroneous final answer.
