# Research Mission 22.2 — Independent Answer Reconstruction Audit

## 1. Executive Summary
An exhaustive, row-by-row independent re-evaluation of all 400 neural outputs in `data/study2/stateshift_primary_400_generations.jsonl` was conducted on local CPU using SymPy-verified mathematical equivalence. 

The evaluation tested two formal operationalizations of answer equivalence:
1. **Path A (Canonical Primary Historical Baseline)**: Strict degree normalization matching the frozen baseline `data/study2/final_verified_outcomes.csv` (Missions 17–21). In this evaluation, $90 \ne 90^\circ$ because the degree symbol is preserved.
2. **Path B (Cleanroom Sensitivity)**: Unit-flexible degree normalization (Mission 18 cleanroom evaluator and Mission 22.1). In this evaluation, the degree symbol is treated as a cosmetic unit and stripped ($90 == 90^\circ$).

---

## 2. Definitive Reconstruction Results

Across all 100 problems and 4 experimental conditions (400 generations total), **exactly one problem diverges between Path A and Path B**: `math500_007`.

| Evaluation Path | Problem Count | Accuracy A (Zero-Shot) | Accuracy D (Forced Restart) | Accuracy E (Explicit Repair) | Accuracy F (State Preserving) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Path A (Canonical Primary)** | 100 | 64.00% | 67.00% | 71.00% | 73.00% |
| **Path B (Sensitivity)** | 100 | 64.00% | 68.00% | 72.00% | 74.00% |
| **Divergence** | 0 | 0.00 pp | +1.00 pp | +1.00 pp | +1.00 pp |

---

## 3. Disagreement Forensic Ledger: `math500_007`

The file `research_mission_22_2/data/evaluator_disagreement_ledger.csv` catalogs every divergence:

- **Problem ID**: `math500_007`
- **Subject**: Precalculus
- **Difficulty Level**: 1
- **Problem Statement**: Find the measure of the angle between two lines in three-dimensional space...
- **Gold Answer**: `90^\circ`
- **Condition A (Zero-Shot)**: Truncated at 768 tokens $\implies$ Scored `False` in both Path A and Path B.
- **Condition D (Forced Restart)**: Extracted prediction is `90` (from `\boxed{90}`).
  - Path A (Strict): `False` ($90 \ne 90^\circ$)
  - Path B (Flexible): `True` ($90 = 90^\circ$)
- **Condition E (Explicit Repair)**: Extracted prediction is `90` (from `\boxed{90}`).
  - Path A (Strict): `False`
  - Path B (Flexible): `True`
- **Condition F (State Preserving)**: Extracted prediction is `90` (from `\boxed{90}`).
  - Path A (Strict): `False`
  - Path B (Flexible): `True`

---

## 4. Invariance of the Treatment Effect & Discordant Pairs

Because `math500_007` is scored concordantly under both evaluation conventions:
- Under Path A: Condition D is `False` and Condition F is `False` $\implies$ cell $d$ ($D=0, F=0$).
- Under Path B: Condition D is `True` and Condition F is `True` $\implies$ cell $a$ ($D=1, F=1$).

Problem `math500_007` **never** shifts between discordant cells $b$ ($D=0, F=1$) and $c$ ($D=1, F=0$). Therefore:
$$b = 8, \quad c = 2, \quad n_d = b + c = 10$$
$$\hat{\tau}_{F-D} = \frac{b - c}{n} = \frac{8 - 2}{100} = +0.0600 \quad (+6.00\text{ pp})$$
$$p_{\text{McNemar}} = 2 \times \sum_{k=8}^{10} \binom{10}{k} (0.5)^{10} = \frac{112}{1024} = 0.109375$$

Both quantities are **mathematically invariant** across both evaluation paths.
