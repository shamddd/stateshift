# Research Mission 22.2 — Manuscript and Publication Correction Report

## 1. Scope & Objective
This report provides the formal errata, text adjustments, and presentation guidelines for the StateShift manuscript targeted for the **NeurIPS 2027 Main Track** (Preprint: arXiv; Secondary: TMLR).

---

## 2. Manuscript Text Updates & Errata

### Section 4.2: Main Results (Table 1 & Prose)
- **Current / Recommended Text**:
  > "Under our primary benchmark evaluation ($N = 100$ pilot problems), State-Preserving Recovery (Condition F) achieves $73.00\%$ accuracy, compared to $67.00\%$ for Forced Restart (Condition D), $71.00\%$ for Explicit Repair (Condition E), and $64.00\%$ for Zero-Shot Baseline (Condition A). In the matched within-item paired contrast ($F$ vs $D$), StateShift yields a paired recovery advantage of $+6.00$ percentage points ($b = 8, c = 2$, Odds Ratio $= 4.00$, exact two-sided McNemar $p = 0.109$). Under a unit-flexible degree normalization sensitivity check (Appendix C), marginal accuracies shift slightly to $F = 74.00\%$ and $D = 68.00\%$, while the paired discordant counts ($b = 8, c = 2$), effect size ($+6.00$ pp), and exact p-value ($p = 0.109375$) remain mathematically invariant."

### Table 1: Primary Experimental Outcomes
```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcccc}
\toprule
\textbf{Experimental Condition} & \textbf{Acc. (\%)} & \textbf{Discordant vs D} & \textbf{Odds Ratio} & \textbf{Exact $p$-value} \\
\midrule
Condition A: Zero-Shot Baseline & 64.00 & (1, 10) & 0.10 & 0.0117* \\
Condition D: Forced Restart & 67.00 & Ref. & 1.00 & Ref. \\
Condition E: Explicit Repair & 71.00 & (4, 8) & 2.00 & 0.3877 \\
Condition F: StateShift (Preserving) & \textbf{73.00} & \textbf{(8, 2)} & \textbf{4.00} & \textbf{0.1094} \\
\bottomrule
\end{tabular}
\caption{Pilot experimental results ($N = 100$ problems) on MATH-500 using Qwen/Qwen2.5-Math-7B-Instruct. Primary baseline evaluates exact degree matching ($90 \ne 90^\circ$). Sensitivity analysis with unit-flexible degree stripping yields $F=74.00\%, D=68.00\%$ with invariant discordant pairs ($b=8, c=2$) and $p=0.1094$.}
\label{tab:main_results}
\end{table}
```

### Section 5: Prospective Confirmatory Trial Preregistration
- **Standardized Text**:
  > "Because the pilot sample ($N = 100$) was exploratory and underpowered to achieve statistical significance at $\alpha = 0.05$ ($p = 0.109$), we preregistered a prospective confirmatory trial using Option B ($N = 231$ held-out problems, 924 inference requests). The confirmatory sample is completely disjoint from the pilot ($\emptyset$ overlap) and achieves $80.07\%$ finite-sample exact power to detect an effect size $\Delta \ge +0.06$ under the pilot discordance rate ($q = 0.10$)."

---

## 3. Repository README Synchronization

The top-level repository `README.md` will be updated to display:
1. Reconciled pilot contingency tables (Canonical Baseline Table A alongside Sensitivity Table B).
2. Explicit note explaining `math500_007` degree normalization.
3. Confirmatory Option B specification ($N = 231$, 924 requests, SHA-256 frozen manifest).
4. Direct instructions for local reproduction via `pytest` and `reconstruct_pilot_outcomes.py`.
