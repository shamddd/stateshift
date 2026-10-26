# StateShift: Research Mission 19.1 — Statistical Reproduction of Checkpoint Lineage

**Date:** October 26, 2026  
**Auditor:** Statistical Methodology Directorate  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Data Source:** `controlled_endpoint_outcomes.csv` (SHA-256: `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139`)  

---

## 1. Mathematical Formulation of the Estimand

The State-Matched Interaction Contrast ($\Gamma_{256}$) is formally defined as a difference-in-differences estimand nested within matched problem pairs:
$$\Gamma_{256} = \left( \mathbb{E}[Y \mid \text{Recovery}, t=256] - \mathbb{E}[Y \mid \text{Recovery}, t=0] \right) - \left( \mathbb{E}[Y \mid \text{Control}, t=256] - \mathbb{E}[Y \mid \text{Control}, t=0] \right)$$
For each problem pair $i \in \{1, \dots, N\}$ ($N=454$), let $\bar{Y}_{S, t, i} = \frac{1}{K}\sum_{k=1}^K Y_{S, t, i, k}$ denote the mean success rate across $K=16$ rollouts. The pair-level contrast is:
$$D_i = (\bar{Y}_{\text{Recovery}, 256, i} - \bar{Y}_{\text{Recovery}, 0, i}) - (\bar{Y}_{\text{Control}, 256, i} - \bar{Y}_{\text{Control}, 0, i})$$
The sample estimator is $\hat{\Gamma}_{256} = \frac{1}{N}\sum_{i=1}^N D_i$, with clustered standard error:
$$\widehat{\text{SE}}_{\text{cluster}}(\hat{\Gamma}_{256}) = \sqrt{\frac{1}{N(N-1)}\sum_{i=1}^N (D_i - \hat{\Gamma}_{256})^2}$$

---

## 2. Independent Reproduction Results

| Statistic | Reported Value in Manuscript | Independently Recomputed | Discrepancy | Verification Status |
| :--- | :---: | :---: | :---: | :---: |
| $\mu_{R,0}$ (Recovery at Step 0) | $38.34\%$ | $38.3398\%$ ($2,785 / 7,264$) | $< 0.001\%$ | **EXACT MATCH** |
| $\mu_{R,256}$ (Recovery at Step 256) | $70.39\%$ | $70.3882\%$ ($5,113 / 7,264$) | $< 0.001\%$ | **EXACT MATCH** |
| $\mu_{C,0}$ (Control at Step 0) | $38.92\%$ | $38.9179\%$ ($2,827 / 7,264$) | $< 0.001\%$ | **EXACT MATCH** |
| $\mu_{C,256}$ (Control at Step 256) | $59.21\%$ | $59.2098\%$ ($4,301 / 7,264$) | $< 0.001\%$ | **EXACT MATCH** |
| $\Delta_R = \mu_{R,256} - \mu_{R,0}$ | $+32.05\text{ pp}$ | $+32.0485\text{ pp}$ | $0.00\text{ pp}$ | **EXACT MATCH** |
| $\Delta_C = \mu_{C,256} - \mu_{C,0}$ | $+20.29\text{ pp}$ | $+20.2918\text{ pp}$ | $0.00\text{ pp}$ | **EXACT MATCH** |
| **Primary Interaction $\Gamma_{256}$** | **$+11.76\text{ pp}$** | **$+11.7566\text{ pp}$ ($0.117566$)** | $0.00\text{ pp}$ | **EXACT MATCH** |
| Clustered Standard Error ($\text{SE}$) | $0.0114$ | $0.011368$ | $< 0.0001$ | **EXACT MATCH** |
| Analytical $t$-statistic ($df=453$) | $10.34$ | $10.3421$ | $< 0.01$ | **EXACT MATCH** |
| Clustered $p$-value | $p < 10^{-20}$ | $p = 1.05 \times 10^{-22}$ | -- | **EXACT MATCH** |
| Problem-Blocked Bootstrap 95% CI ($B=2,000$) | $[+9.61\text{ pp}, +13.96\text{ pp}]$ | $[+9.61\text{ pp}, +13.96\text{ pp}]$ | $0.00\text{ pp}$ | **EXACT MATCH** |
| Strict Decontamination $\Gamma_{256,\text{Strict}}$ ($N=388$) | **$+11.60\text{ pp}$** | **$+11.5979\text{ pp}$ ($0.115979$)** | $0.00\text{ pp}$ | **EXACT MATCH** |
| Generated Token Shift under Recovery ($\Delta$) | $+0.02\text{ tok}$ | $+0.0206\text{ tok}$ ($482.47 \to 482.50$) | $0.00\text{ tok}$ | **EXACT MATCH** |

---

## 3. Methodological Conclusions

1. **Statistical Authenticity:** All reported statistical values in Study 1 are derived directly and deterministically from `controlled_endpoint_outcomes.csv` without hand-waving, fabrication, or rounding errors.
2. **Correct Modeling Framework:** The clustered standard error correctly models the problem-level pairing ($df=453$), accounting for within-pair correlation across rollouts and checkpoints.
3. **Robustness to Leakage:** The strict subset analysis ($N=388$) isolates a virtually identical effect ($+11.60\text{ pp}$ vs $+11.76\text{ pp}$), confirming that recovery adaptation is not driven by benchmark contamination.
