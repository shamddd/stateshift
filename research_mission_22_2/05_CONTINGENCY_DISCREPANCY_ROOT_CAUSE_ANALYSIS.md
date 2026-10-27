# Research Mission 22.2 — Contingency Discrepancy Root-Cause Analysis

## 1. Problem Statement & Audit Genesis
During Research Mission 22.1, an adversarial cross-check noted that while historical Mission 17–21 reports cited pilot accuracies of $F = 73.00\%$ and $D = 67.00\%$ ($a=65, b=8, c=2, d=25$), the cleanroom reproduction code cited $F = 74.00\%$ and $D = 68.00\%$ ($a=66, b=8, c=2, d=24$). 

Although both tables produced the identical effect size ($\hat{\tau} = +6.00\text{ pp}$) and exact McNemar p-value ($p = 0.109375$), scientific transparency demands an exact root-cause determination: why did this shift occur, which code introduced it, and how should it be governed in the NeurIPS 2027 submission package?

---

## 2. Root Cause Localization: `math500_007`

The root-cause analysis traced every generation across all 100 problems. Only a single problem exhibited evaluator divergence: `math500_007`.

### Problem Specification
- **Benchmark**: MATH-500
- **Problem ID**: `math500_007`
- **Subject**: Precalculus (Difficulty Level 1)
- **Problem Prompt**: Line $\ell_1$ has direction vector $\mathbf{d}_1 = \langle 1/2, 1/3, -1 \rangle$, and line $\ell_2$ has direction vector $\mathbf{d}_2 = \langle 2, -3, 0 \rangle$. Find the measure of the angle between $\ell_1$ and $\ell_2$, in degrees.
- **Official Ground Truth (`gold_answer`)**: `90^\circ`

### Model Generation Behavior
The model (`Qwen/Qwen2.5-Math-7B-Instruct`) correctly calculated the dot product:
$$\mathbf{d}_1 \cdot \mathbf{d}_2 = \left(\frac{1}{2}\right)(2) + \left(\frac{1}{3}\right)(-3) + (-1)(0) = 1 - 1 + 0 = 0$$
Recognizing that orthogonal vectors form a $90^\circ$ angle, the model outputted:
- Condition D: `...Therefore, the angle \theta is: \[\theta = \cos^{-1}(0) = 90^\circ.\] Thus, the angle between the two lines is \(\boxed{90}\).`
- Condition E: `...Therefore, the angle \theta between the two lines is \(90^\circ\). The final answer is: \[\boxed{90}.\]`
- Condition F: `...Therefore, the angle \theta between the two lines is \(90^\circ\). The answer is: \[\boxed{90}\]`

In all three conditions (D, E, F), the model placed `90` inside `\boxed{...}` while stating $90^\circ$ in the preceding prose.

---

## 3. Evaluator Implementation Divergence

### Historical Baseline Evaluator (Missions 17–21)
The original evaluation script that produced `data/study2/final_verified_outcomes.csv` evaluated answers strictly against the raw gold string:
- Gold: `90^\circ`
- Prediction: `90`
- Normalization: String stripped of outer delimiters, but the degree symbol `^\circ` was **not** removed.
- Match: `'90' != '90^\\circ'` $\implies$ Evaluated as `False`.
- Resulting State: Problem `math500_007` was recorded as `D=False, F=False` (cell $d$).
- Table Counts: $a=65, b=8, c=2, d=25 \implies F=73\%, D=67\%$.

### Cleanroom Evaluator (Mission 18 / Mission 22.1)
The independent cleanroom reproduction script `reproduce_confirmatory_results.py` included unit-flexible LaTeX normalization:
```python
s = re.sub(r"\\circ|\^\\circ|°", "", s)
```
- Gold: `90^\circ` $\to$ Normalized: `'90'`
- Prediction: `90` $\to$ Normalized: `'90'`
- Match: `'90' == '90'` $\implies$ Evaluated as `True`.
- Resulting State: Problem `math500_007` was recorded as `D=True, F=True` (cell $a$).
- Table Counts: $a=66, b=8, c=2, d=24 \implies F=74\%, D=68\%$.

---

## 4. Policy Decision and Governance for Publication

1. **Primary Baseline**: To preserve strict historical auditability and match `data/study2/final_verified_outcomes.csv`, all primary text in the manuscript will report the **Path A Canonical Baseline**:
   $$\text{Accuracy } F = 73.00\%, \quad D = 67.00\%, \quad E = 71.00\%, \quad A = 64.00\%$$
   $$\text{Contingency Table: } a=65, \quad b=8, \quad c=2, \quad d=25$$
2. **Sensitivity Analysis**: The manuscript Appendix will explicitly report the **Path B Cleanroom Sensitivity Analysis**:
   $$\text{Accuracy } F = 74.00\%, \quad D = 68.00\%, \quad E = 72.00\%, \quad A = 64.00\%$$
   $$\text{Contingency Table: } a=66, \quad b=8, \quad c=2, \quad d=24$$
3. **Core Conclusion**: Reviewers and area chairs can verify that under both strict and unit-flexible normalization, the estimated recovery advantage is exactly $+6.00$ percentage points ($b=8, c=2$) with exact McNemar $p = 0.109375$.
