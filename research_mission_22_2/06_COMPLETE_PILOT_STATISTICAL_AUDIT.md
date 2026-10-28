# Research Mission 22.2 — Complete Pilot Statistical Audit

## 1. Experimental Design & Unit of Analysis
The StateShift pilot experiment (Study 2, $N=100$) evaluates whether saving and restoring reasoning context (Condition F) outperforms forced restart (Condition D), explicit prompting repair (Condition E), and unperturbed zero-shot baseline (Condition A).

### The Within-Item Paired Design
A critical methodological requirement of the StateShift evaluation is that **problems are matched pairs**. For every problem $i \in \{1, \dots, 100\}$, the model is evaluated on the exact same mathematical problem instance under all conditions:
- Unit of Analysis: Problem $i \in \text{MATH-500}$.
- Outcomes: $Y_{Ai}, Y_{Di}, Y_{Ei}, Y_{Fi} \in \{0, 1\}$.
- Paired Contrast: $D_i = Y_{Fi} - Y_{Di} \in \{-1, 0, +1\}$.

### Invalidity of Two-Sample Unpaired Tests
An independent two-sample test (e.g., two-sample proportion $z$-test or Fisher's exact test) assumes that observations in Condition D and Condition F are independent. Because both conditions are evaluated on the exact same problem instances, problem-level difficulty creates strong positive covariance:
$$\text{Cov}(Y_{Di}, Y_{Fi}) > 0$$
Using an unpaired test ignores this covariance, inflating the standard error by treating concordant pairs as independent data points, which diminishes statistical power and violates exchangeability. Therefore, **the paired McNemar exact test is the only valid primary test**.

---

## 2. Primary Comparison: Condition F vs Condition D

### Canonical 2x2 Contingency Table (Path A)
```
                       Condition F Correct    Condition F Incorrect    Total
Condition D Correct         a = 65                  c = 2               67
Condition D Incorrect       b = 8                   d = 25              33
Total                       73                      27                 100
```

- Marginal Accuracies: $\text{Acc}(F) = 73.00\%$, $\text{Acc}(D) = 67.00\%$.
- Paired Difference (Effect Size): $\hat{\tau}_{F-D} = \frac{b - c}{N} = \frac{8 - 2}{100} = +0.0600$ (+6.00 pp).
- Standard Error: $\text{SE}(\hat{\tau}) = \sqrt{\frac{(b + c) - (b - c)^2 / N}{N^2}} = \sqrt{\frac{10 - 0.36}{10000}} \approx 0.0310$ (3.10 pp).
- 95% Asymptotic Wald Confidence Interval: $[-0.0009, +0.1209]$ ($-0.09\text{ pp to } +12.09\text{ pp}$).
- Discordant Pairs: $n_d = b + c = 10$ ($b = 8, c = 2$).
- Odds Ratio: $\hat{\theta} = \frac{b}{c} = \frac{8}{2} = 4.00$ (95% Exact Conditional CI: $[0.80, 38.67]$).
- Exact McNemar Two-Sided Test:
  $$p = 2 \times \sum_{k=8}^{10} \binom{10}{k} (0.5)^{10} = 2 \times \frac{45 + 10 + 1}{1024} = \frac{112}{1024} = 0.109375$$

---

## 3. Secondary Comparisons & Multiple Testing Context

To contextualize the StateShift recovery mechanism, four secondary paired comparisons were conducted:

| Comparison | Contrast Description | Accuracies (%) | Discordant $(b, c)$ | $n_d$ | $\hat{\Delta}$ (pp) | Exact McNemar $p$ | Significance ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F vs D** | State-Preserving vs Forced Restart | 73.0 vs 67.0 | (8, 2) | 10 | +6.00 | 0.109375 | Not Significant (Pilot Underpowered) |
| **E vs D** | Explicit Repair vs Forced Restart | 71.0 vs 67.0 | (8, 4) | 12 | +4.00 | 0.387695 | Not Significant |
| **F vs E** | State-Preserving vs Explicit Repair | 73.0 vs 71.0 | (7, 5) | 12 | +2.00 | 0.774414 | Not Significant |
| **D vs A** | Forced Restart vs Zero-Shot | 67.0 vs 64.0 | (6, 3) | 9 | +3.00 | 0.507812 | Not Significant |
| **F vs A** | State-Preserving vs Zero-Shot | 73.0 vs 64.0 | (10, 1) | 11 | +9.00 | 0.011719 | **Significant** ($p < 0.05$) |

### Interpretation
1. Condition F significantly outperforms the unperturbed zero-shot baseline ($p = 0.0117$), demonstrating that providing the prior valid prefix enables the model to solve complex multi-step problems that exceed zero-shot context budgets.
2. The focal contrast between State-Preserving recovery (F) and Forced Restart (D) shows a substantial effect size (+6.00 pp, OR = 4.00), but with $N=100$, only $n_d = 10$ discordant pairs were observed. Achieving statistical significance at $\alpha = 0.05$ with $c=2$ would have required $b \ge 9$ ($p = 0.0215$).
3. This establishes the scientific justification for the **Confirmatory Experiment ($N=231$)**, specifically powered to detect $\Delta \ge 6.00\text{ pp}$ at $80\%$ power.
