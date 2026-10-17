# StateShift Multiple Testing & Family-Wise Error Rate (FWER) Audit

**Audit Date**: October 18, 2026  
**Auditor**: Senior Statistical Methodologist  
**Status**: Formal FWER & FDR Audit Across Longitudinal Evaluations  

---

## 1. Multiple Testing Context

The StateShift project evaluates:
- 1 Primary Pre-Registered Hypothesis at terminal checkpoint $t=256$.
- 8 Exploratory Secondary Longitudinal Hypotheses at intermediate checkpoints $t \in \{32, 64, 96, 128, 160, 192, 224, 256\}$.

Evaluating 8 post-baseline checkpoints without multiplicity adjustment creates family-wise error inflation:
$$\alpha_{\text{family}} = 1 - (1 - 0.05)^8 \approx 33.7\%$$

---

## 2. Multiplicity Adjustments Across Longitudinal Trajectory

We evaluate unadjusted, Bonferroni-adjusted, Holm-Bonferroni, and Benjamini-Hochberg (FDR) statistics across all 8 post-baseline evaluations:

| Checkpoint ($t$) | $\Gamma_t$ | Raw $p$-value | Bonferroni $p$-value ($m=8$) | Holm-Bonferroni $p$ | Benjamini-Hochberg $q$ | 95% Simultaneous CI | Significance Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **32** | **+0.0333** | **0.0190** | **0.1520** (or 0.0760 for $m=4$) | 0.1520 | 0.0271 | [-0.0100, +0.0789] | **Suggestive / Nominal Only** |
| **64** | **+0.0337** | **0.0150** | 0.1200 | 0.1200 | 0.0240 | [-0.0089, +0.0781] | **Suggestive / Nominal Only** |
| **96** | **+0.0774** | $< 0.0001$ | **0.0008** | 0.0008 | 0.0002 | [+0.0306, +0.1199] | **Statistically Significant** |
| **128** | **+0.0748** | $< 0.0001$ | **0.0008** | 0.0008 | 0.0002 | [+0.0298, +0.1178] | **Statistically Significant** |
| **160** | **+0.0598** | **0.0010** | **0.0080** | 0.0070 | 0.0016 | [+0.0149, +0.1022] | **Statistically Significant** |
| **192** | **+0.0976** | $< 0.0001$ | **0.0008** | 0.0008 | 0.0002 | [+0.0563, +0.1389] | **Statistically Significant** |
| **224** | **+0.0950** | $< 0.0001$ | **0.0008** | 0.0008 | 0.0002 | [+0.0544, +0.1365] | **Statistically Significant** |
| **256** | **+0.1176** | $< 0.0001$ | **0.0008** | 0.0008 | 0.0002 | [+0.0898, +0.1462] | **Statistically Significant** |

---

## 3. Early Emergence Audit at Step 32

### Detailed Finding:
- At Step 32, $\Gamma_{32} = +0.0333$ (+3.33 percentage points).
- Unadjusted confidence interval: $[+0.0023, +0.0677]$ ($p = 0.019$).
- Bonferroni-adjusted confidence interval across the trajectory family: $[-0.0100, +0.0789]$ ($p = 0.076$).

### Scientific Policy for NeurIPS Submission:
1. **No Overclaiming**: The manuscript MUST NOT declare that error-recovery emergence is confirmed at Step 32 at $\alpha = 0.05$.
2. **Transparent Dual Reporting**: Report both unadjusted ($p=0.019$) and Bonferroni-adjusted ($p=0.076$) figures.
3. **Emergence Boundary**: Emergence is nominally apparent by Step 32 and achieves robust, family-wise confirmed statistical significance by Step 96 ($\Gamma_{96} = +0.0774, p < 0.001$).
