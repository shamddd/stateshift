# StateShift Clustering, Pseudoreplication & Dependence Audit

**Audit Date**: October 18, 2026  
**Auditor**: Senior Statistical Methodologist  

---

## 1. The Risk of Pseudoreplication in Repeated LLM Rollouts

A frequent methodological error in LLM evaluation is treating multiple stochastic completions from the same prompt as independent and identically distributed (i.i.d.) observations. 

In StateShift:
- There are $N = 454$ distinct mathematical problem specifications.
- For each problem, $K = 16$ rollouts are generated per cell ($454 \times 16 \times 4 = 29,056$ observations).
- Rollouts sharing the same problem instance share:
  1. The underlying mathematical structure and intrinsic difficulty.
  2. The prompt wording and injected prefix text.
  3. The model checkpoint weights.

If an unblocked, naive bootstrap were applied (resampling all $29,056$ individual rows independently), the effective sample size would be inflated by up to $16\times$, leading to artificially narrow confidence intervals and severely deflated $p$-values.

---

## 2. Verification of Problem-Level Blocked Resampling

We verified the resampling algorithm implemented in `stateshift/statistics/bootstrap.py`:
1. **Resampling Unit**: The bootstrap resamples problem indices $i \in \{1, \dots, N\}$ with replacement ($B = 10,000$).
2. **Cluster Invariance**: When problem $i$ is selected in bootstrap replicate $b$, all $K=16$ associated rollouts across both states ($R, C$) and both checkpoints ($t=0, 256$) are included together.
3. **Mathematical Correctness**: This preserves the within-problem correlation structure, accounting for intra-cluster correlation (ICC) and problem-level heterogeneity.

The reported confidence interval $[+0.0955, +0.1400]$ rigorously reflects problem-level sampling uncertainty.
