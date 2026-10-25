# StateShift Research Mission 13 — Deliverable 09: Repair Economics Analysis

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Research Question 3**: Does preserving valid reasoning prefixes provide computational token savings ($\text{tokens}_D - \text{tokens}_F$) without sacrificing accuracy?  

---

## 1. The Token Economics Hypothesis

A primary motivation for research into state-preserving reasoning recovery is computational cost:
- If a model encounters an error at step $k$ of an $M$-step derivation, discarding the entire prefix and restarting (Condition D) forces the model to regenerate steps $1, \dots, k-1$, incurring redundant inference compute.
- If the model surgically repairs step $k$ and preserves steps $1, \dots, k-1$ (Condition F), it should require fewer generated tokens:
  $$\Delta_{\text{tokens}} = \text{tokens}_D - \text{tokens}_F > 0$$
- If $\Delta_{\text{tokens}} > 0$ while $\text{Acc}_F \approx \text{Acc}_D$, state preservation would yield an efficiency gain in test-time compute.

---

## 2. Empirical Measurements on 7B Reasoning

Analyzing the 35 matched pairs completed in both Condition D and Condition F on `Qwen2.5-Math-7B-Instruct`:

| Parameter | Condition D (Forced Restart) | Condition F (State Preserving) | Observed Difference ($\Delta = D - F$) |
| :--- | :--- | :--- | :--- |
| **Mean Generated Tokens** | $521.8 \pm 23.4$ | $508.6 \pm 24.1$ | $+13.2\text{ tokens}$ ($+2.5\%$) |
| **Median Generated Tokens** | $512.0$ | $502.0$ | $+10.0\text{ tokens}$ |
| **Standard Deviation** | $138.5$ | $142.6$ | $74.2$ (paired diff SD) |
| **95% Bootstrap CI ($\Delta$)** | — | — | $[-11.4, +37.8]\text{ tokens}$ |
| **Paired t-statistic** | — | — | $t = 1.052, p = 0.299$ |
| **Wilcoxon Signed-Rank Test** | — | — | $W = 278.0, p = 0.384$ |

---

## 3. Accuracy-Adjusted Compute Efficiency

Raw token counts do not account for solution correctness. The true economic metric is **tokens per correct solution**:
$$\text{Tokens / Correct} = \frac{\sum_{i=1}^N \text{Generated Tokens}_i}{\sum_{i=1}^N \mathbf{1}[\text{Correct}_i]}$$

| Condition | Total Tokens Generated | Total Correct Solutions | Tokens per Correct Solution | Efficiency Delta |
| :--- | :--- | :--- | :--- | :--- |
| **Condition D (Forced Restart)** | 18,263 | 29 | **629.8** | Baseline |
| **Condition F (State Preserving)** | 17,801 | 29 | **613.8** | **+2.54% improvement** |

---

## 4. Why the Expected Token Savings Evaporated

The empirical evidence demonstrates that **Condition F does not provide meaningful token savings over Condition D** ($+13.2$ tokens, $p = 0.299$, 95% CI spans zero).

### The Architectural Explanation:
1. Because the 7B model is incapable of genuine local repair ($0.0\%$ repair rate), it does not actually preserve the earlier steps in memory.
2. In **91.4%** of Condition F rollouts, the model executes an implicit restart.
3. Because it restarts from the beginning, it regenerates the complete reasoning trajectory, consuming almost the exact same number of output tokens as the explicit restart condition.
4. Furthermore, prompting the model with a verbose state-preserving preamble increases prompt tokens without shortening output tokens, rendering the net compute cost equivalent.

**Conclusion**: In currently available 7B post-trained models, forcing state preservation does not generate computational efficiency gains because models lack the localized refactoring capability required to realize those savings.
