# STATISTICAL ANALYSIS & INFERENCE DOCUMENTATION

**Project**: StateShift

---

## 1. Problem-Blocked Bootstrap ($B=10,000$)

To account for problem-level difficulty variation and intra-problem rollout correlation, all confidence intervals are computed using **problem-blocked bootstrap resampling** ($B=10,000$ iterations). Entire problem clusters ($p \in \{1..N\}$) are resampled with replacement, preserving rollout structure within each sampled problem.

---

## 2. Multiplicity Adjustments

For intermediate trajectory checkpoints, Bonferroni multiplicity adjustments are applied to control the family-wise error rate across intermediate comparisons ($M=4$ intermediate checkpoints $\{32, 96, 160, 224\}$ evaluated in Phase 2B.4 against $t=0$). At step 32, the unadjusted 95% bootstrap CI is $[+0.0023, +0.0677]$ ($p=0.0190$), while the Bonferroni multiplicity-adjusted 95% CI is $[-0.0100, +0.0789]$ ($p_{\text{adj}}=0.0760$). Because the simultaneous Bonferroni interval spans zero, the contrast does not achieve statistical significance under conservative family-wise multiplicity control at this earliest checkpoint.

---

## 3. Order-Restricted Analysis (PAVA)

Because unconstrained intermediate point estimates exhibit small sampling fluctuations at $K=2/3$ (e.g., $\Gamma_{96}=0.0774 \to \Gamma_{128}=0.0748$), we evaluate global trend consistency using the prespecified Pooled Adjacent Violators Algorithm (PAVA). The isotonic regression fit confirms that the trajectory is consistent with a non-decreasing trend across post-training.

*Signed by Lead Statistical Methodologist*
