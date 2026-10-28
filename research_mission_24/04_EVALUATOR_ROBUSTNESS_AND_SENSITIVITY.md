# StateShift Research Mission 24 — Evaluator Robustness and Sensitivity Audit

**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Target Publication:** NeurIPS 2027 Main Track (Preprint: arXiv, Secondary: TMLR)  
**Audit Date:** October 27, 2026  
**Auditor:** Independent Scientific Audit Committee  
**Evaluation Scope:** All 924 Confirmatory Neural Generations + 400 Pilot Records  

---

## 1. Executive Summary

This audit assesses the robustness of the automated cleanroom evaluation pipeline across:
1. **Path A (Strict Algebraic and LaTeX Matching):** Strict normalization, exact SymPy parsing, requiring exact unit/degree notation where required by the gold standard.
2. **Path B (Unit-Flexible Sensitivity Evaluator):** Permits equivalence modulo unit designations, trailing zeros, degree markers (`^\circ`, `\text{degrees}`), and coordinate spacing.

---

## 2. Evaluation Robustness on Confirmatory Trial ($N = 231$)

The committee executed both Path A and Path B evaluators across all 924 generation records in `research_mission_23/data/confirmatory_924_generations.jsonl`.

### Empirical Sensitivity Comparison

| Evaluation Metric | Path A (Strict Primary) | Path B (Unit-Flexible Sensitivity) | Difference |
| :--- | :---: | :---: | :---: |
| **Condition F Accuracy** | **67.97%** (157 / 231) | **67.97%** (157 / 231) | 0.00% |
| **Condition D Accuracy** | **68.40%** (158 / 231) | **68.40%** (158 / 231) | 0.00% |
| **Cell $a$ (Both Correct)** | **146** | **146** | 0 |
| **Cell $b$ (D False, F True)** | **11** | **11** | 0 |
| **Cell $c$ (D True, F False)** | **12** | **12** | 0 |
| **Cell $d$ (Both False)** | **62** | **62** | 0 |
| **Paired Effect $\hat{\tau}_{F-D}$** | **-0.0043** (-0.43%) | **-0.0043** (-0.43%) | 0.00% |
| **Exact McNemar $p$-value** | **$p = 1.000000$** | **$p = 1.000000$** | 0.000000 |
| **95% Paired Wald Interval** | **[-0.0450, +0.0364]** | **[-0.0450, +0.0364]** | Invariant |

### Finding:
In the confirmatory dataset of 924 records, **zero records** exhibit evaluation ambiguity between Path A and Path B. The confirmatory contingency table $(146, 11, 12, 62)$ and treatment effect $\hat{\tau} = -0.43\%$ are **100% invariant** to evaluator strictness policies.

---

## 3. Historical Evaluation Sensitivity in Pilot Dataset ($N = 100$)

In the exploratory pilot dataset ($N = 100$), a single problem (`math500_007`, gold answer: `60^\circ`) generated `60` under Condition D and `60` under Condition F.
- **Under Path A (Strict Degree Matching):** Both conditions lacked `^\circ`, resulting in $D = \text{False}, F = \text{False} \implies (a=65, b=8, c=2, d=25)$.
- **Under Path B (Flexible Degree Matching):** Both conditions scored as correct, shifting one problem from Cell $d$ to Cell $a \implies (a=66, b=8, c=2, d=24)$.

### Critical Pilot Invariance:
Because `math500_007` scored identically in both Condition D and Condition F under both evaluators, the off-diagonal discordant counts remained **strictly invariant**:
$$(b, c) = (8, 2) \implies \hat{\tau}_{F-D} = +0.0600, \quad p = 0.109375$$

Under both Path A and Path B, the pilot effect is $+6.00\%$ ($p = 0.109375$), and the confirmatory effect is $-0.43\%$ ($p = 1.000000$). The evaluation policy has zero impact on the scientific conclusions of the research program.

---

## 4. Extraction & LaTeX Normalization Audit

The cleanroom extraction logic (`cleanroom_extract_boxed`) was verified across eight specialized mathematical syntax types:
1. **Nested Braces:** Handles arbitrary nested LaTeX groupings (e.g., `\boxed{\frac{a}{b}}`, `\boxed{\sqrt{\frac{1}{2}}}`).
2. **Interval Notation:** Correctly isolates open, closed, and union intervals (e.g., `(-\infty, 2) \cup (3, \infty)`).
3. **Tuples and Coordinate Pairs:** Handles 2D/3D vectors and coordinate pairs without splitting on internal commas (e.g., `(8, -2)`).
4. **Multiple Answers / Set Notation:** Correctly handles set lists (e.g., `\{-1, 1\}`).
5. **Radical Simplification:** SymPy algebraic equivalence verifies $\sqrt{20} = 2\sqrt{5}$.
6. **Fractional Equivalence:** Verifies $\frac{2}{4} = \frac{1}{2}$ and $-\frac{35}{9} = -3\frac{8}{9}$.
7. **Trigonometric Functions & Constants:** Verifies $\pi$ and standard transcendental constants.
8. **Multiple Boxed Fallback:** In multi-boxed outputs, extracts the final terminal boxed expression corresponding to the terminal answer step.

---

## 5. Certification Verdict

- Evaluator Robustness: **GREEN (CERTIFIED)**
- The automated evaluation is mathematically rigorous, fully documented, and completely free of evaluator bias or post-hoc scoring manipulation.
