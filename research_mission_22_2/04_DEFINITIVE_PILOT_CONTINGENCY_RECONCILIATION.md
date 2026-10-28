# Research Mission 22.2 — Definitive Pilot Contingency Reconciliation

## 1. Executive Summary & Problem Resolution
In earlier audit reports across the StateShift research trajectory, two distinct 2x2 paired contingency tables for Condition F (State-Preserving Recovery) versus Condition D (Forced Restart) were reported:

- **Historical Baseline Table (Missions 17–21)**:
  $$a = 65, \quad b = 8, \quad c = 2, \quad d = 25 \implies \text{Accuracy } F = 73.00\%, \quad D = 67.00\%$$
- **Cleanroom Sensitivity Table (Mission 18 / Mission 22.1)**:
  $$a = 66, \quad b = 8, \quad c = 2, \quad d = 24 \implies \text{Accuracy } F = 74.00\%, \quad D = 68.00\%$$

This forensic reconciliation conclusively proves:
1. Both tables represent genuine evaluations of the exact same 400 neural outputs in `data/study2/stateshift_primary_400_generations.jsonl`.
2. The discrepancy between $a=65, d=25$ and $a=66, d=24$ is localized to a single problem out of 100: `math500_007`.
3. In both tables, the discordant pair counts ($b=8, c=2$), total discordant pairs ($n_d = 10$), paired intervention effect size ($\hat{\tau}_{F-D} = +6.00\text{ pp}$), and two-sided exact McNemar p-value ($p = 0.109375$) are **strictly identical**.
4. Per Rule 1 and Rule 2 of the StateShift forensic charter, **Table A ($a=65, b=8, c=2, d=25$) is the canonical primary historical baseline** because it strictly matches the frozen primary outcome matrix `data/study2/final_verified_outcomes.csv`. Table B ($a=66, b=8, c=2, d=24$) is retained as the unit-flexible degree sensitivity analysis.

---

## 2. Side-by-Side Contingency Comparison

```
TABLE A: Canonical Historical Baseline (Missions 17-21)
Degree Policy: Strict degrees (90 != 90^\circ)
Source: data/study2/final_verified_outcomes.csv

                       Condition F Correct    Condition F Incorrect    Total
Condition D Correct         a = 65                  c = 2               67
Condition D Incorrect       b = 8                   d = 25              33
Total                       73                      27                 100

TABLE B: Cleanroom Sensitivity Analysis (Mission 18 / 22.1)
Degree Policy: Flexible degrees (90 == 90^\circ)
Source: cleanroom_normalize_latex(strip_degree=True)

                       Condition F Correct    Condition F Incorrect    Total
Condition D Correct         a = 66                  c = 2               68
Condition D Incorrect       b = 8                   d = 24              32
Total                       74                      26                 100
```

---

## 3. Tri-Method Verification

The contingency cell counts were calculated independently via three separate computational libraries:
1. **Pure Python Reference Implementation**: Iteration through CSV dictionaries with conditional sums.
2. **NumPy Boolean Vector Algebra**: Logical bitwise operations on boolean ndarrays (`d & f`, `~d & f`, `d & ~f`, `~d & ~f`).
3. **Pandas Crosstabulation**: Contingency aggregation via `pd.crosstab(df['Path_D'], df['Path_F'])`.

All three methods produced identical results ($a=65, b=8, c=2, d=25$ for Path A; $a=66, b=8, c=2, d=24$ for Path B).

---

## 4. Formal Proof of Treatment Effect Invariance

Let $Y_{Di} \in \{0, 1\}$ and $Y_{Fi} \in \{0, 1\}$ denote the binary correctness indicators for problem $i$ under Condition D and Condition F. The sample treatment effect is defined as:
$$\hat{\tau}_{F-D} = \frac{1}{N} \sum_{i=1}^N (Y_{Fi} - Y_{Di})$$

Partitioning the sum across the four disjoint cells of the 2x2 contingency table:
$$\hat{\tau}_{F-D} = \frac{1}{N} \left[ \sum_{i \in a} (1 - 1) + \sum_{i \in b} (1 - 0) + \sum_{i \in c} (0 - 1) + \sum_{i \in d} (0 - 0) \right] = \frac{b - c}{N}$$

For problem `math500_007`:
- Under Path A: $Y_{D, 007} = 0$ and $Y_{F, 007} = 0 \implies i \in d$. Contribution to $(Y_{Fi} - Y_{Di}) = 0 - 0 = 0$.
- Under Path B: $Y_{D, 007} = 1$ and $Y_{F, 007} = 1 \implies i \in a$. Contribution to $(Y_{Fi} - Y_{Di}) = 1 - 1 = 0$.

Because the problem transitions purely between the concordant cells ($d \leftrightarrow a$), its net contribution to $(Y_{Fi} - Y_{Di})$ is identically zero under both evaluators. Consequently:
$$b_{\text{Path A}} = b_{\text{Path B}} = 8$$
$$c_{\text{Path A}} = c_{\text{Path B}} = 2$$
$$\hat{\tau}_{F-D} = \frac{8 - 2}{100} = +0.0600 \quad (+6.00\text{ pp})$$
$$p_{\text{McNemar}} = 2 \times \sum_{k=8}^{10} \binom{10}{k} (0.5)^{10} = \frac{112}{1024} = 0.109375$$

The central statistical finding of the StateShift pilot is entirely robust and invariant to the degree evaluation convention.
