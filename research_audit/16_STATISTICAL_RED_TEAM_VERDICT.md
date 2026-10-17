# StateShift Statistical Red-Team Final Verdict

**Audit Date**: October 18, 2026  
**Verdict**: **STATISTICALLY RIGOROUS WITH PRECISE BOUNDARY REFINEMENTS**  

---

## 1. Summary of Verified Strengths
1. **Zero Raw Discrepancy on Endpoint**: $\Gamma_{256} = +0.1176$ is 100% verified from $29,056$ raw rollout records.
2. **Proper Blocked Bootstrap**: The bootstrap resamples problem specifications, avoiding pseudoreplication.
3. **Decontamination Invariance**: Strict filtering leaves the effect unchanged ($+0.1160$).
4. **Natural Recovery Grounding**: Study B ($3,200$ rollouts, $\text{NEI}=18.19\%$, $\text{NRR}=30.93\%$) provides orthogonal confirmation.

---

## 2. Mandatory Statistical Refinements for NeurIPS
1. **Acknowledge Intermediate Sampling Heterogeneity**:
   - Endpoints ($t=0, 256$) were evaluated at $K=16$ ($14,528$ rollouts each).
   - Intermediate checkpoints were evaluated at $K=2/3$ per problem.
   - Disclose that intermediate point estimates carry higher variance ($SE \approx 0.017$ vs $0.011$).
2. **Purge "Strict Monotonicity"**:
   - The empirical dips at step 160 and 224 must be presented directly.
   - Frame the trajectory as "consistent with an increasing trend under isotonic regression (PAVA), while exhibiting local sampling variation".
3. **Disclose Step-32 Bonferroni Borderline**:
   - Present both raw $p=0.019$ and Bonferroni $p=0.076$.
