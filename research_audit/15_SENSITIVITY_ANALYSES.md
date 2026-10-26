# StateShift Sensitivity & Alternative Modeling Audit

**Audit Date**: October 18, 2026  
**Auditor**: Senior Statistical Modeler  

---

## 1. Decontamination Sensitivity Analysis ($N=388$)

To ensure that $\Gamma_{256} = +0.1176$ is not an artifact of training data contamination:
- The DeepScaleR training set was screened against the 454 MATH-500 test problems using 10-gram overlap and edit distance filters.
- Exactly 66 problems exhibited non-zero potential similarity, leaving a strict decontaminated cohort of $N_{\text{Strict}} = 388$ problems ($24,832$ rollouts).
- **Result**:
  $$\Gamma_{256,\text{Strict}} = \mathbf{+0.1160} \quad (95\%\text{ CI } [+0.0913, +0.1408], p < 0.0001)$$
- **Conclusion**: The point estimate drops by a negligible $0.0016$ ($1.6\times 10^{-3}$), demonstrating that training set memorization does not explain the recovery gain.

---

## 2. Alternative Parametric Models: Generalized Estimating Equations (GEE)

Fitting a population-averaged logistic GEE model with exchangeable correlation within problems:
$$\text{logit}(P(Y_{iskt} = 1)) = \beta_0 + \beta_1 \mathbb{I}_{s=R} + \beta_2 \mathbb{I}_{t=256} + \beta_3 (\mathbb{I}_{s=R} \times \mathbb{I}_{t=256})$$

- **Interaction Odds Ratio**: $\text{OR}_{\text{interaction}} = \exp(\beta_3) = \mathbf{1.54}$ ($95\%$ CI $[1.36, 1.74], z = 6.84, p < 0.0001$).
- On both the additive probability scale ($+11.76\text{ pp}$) and the multiplicative odds scale ($1.54\times$), the state-selective recovery effect is highly robust.
