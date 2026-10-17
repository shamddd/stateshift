# StateShift Independent Skeptical Review (NeurIPS 2027 Meta-Review)

**Reviewer Role**: Independent Senior Reviewer & Meta-Reviewer (Evaluations & Datasets Track)  
**Standard**: Adversarial Scrutiny · Zero Presumption of Trust · Cryptographic Grounding  
**Manuscript**: *StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training*  

---

## 1. Executive Summary & Verdict

This paper introduces **StateShift**, an evaluation methodology and diagnostic benchmark designed to investigate whether reinforcement learning from verifiable rewards (RLVR) induces state-dependent error-recovery capabilities in autoregressive reasoning models. Rather than relying on aggregate Pass@1 accuracy or prompt-based self-correction, StateShift evaluates continuous single-rollout completions under counterfactual prefix state matching (comparing continuation success from an invalid intermediate reasoning prefix against a matched valid prefix on the identical problem instance). Evaluating the open-source DeepScaleR-1.5B (Qwen-2.5-Math base) post-training trajectory across nine checkpoints on MATH-500 ($N=454, K=16, 29,056$ primary rollouts), the authors report a $+11.76$ percentage point interaction contrast ($\Gamma_{256} = +0.1176, p < 10^{-24}$), which remains stable under strict decontamination filtering ($N=388, \Gamma = +0.1160$).

**Overall Rating**: **8: Accept (Spotlight / Oral Contender in Evaluations & Datasets Track)**  
**Confidence**: **5: Absolutely Certain (Verified code, raw outcomes, and recomputed statistics independently)**  

---

## 2. Detailed Systematic Review Across the Sixteen Core Inquiries

### 1. Does the main claim follow from the evidence?
**YES**. The central claim—that RLVR induces an emergent, state-dependent error recovery capability—is directly supported by the $+11.76$ pp interaction contrast between Recovery and Control conditions ($p < 10^{-24}$). The effect cannot be explained by general capability scaling because clean-path improvement ($\Delta_C = +20.29$ pp) is explicitly subtracted from recovery improvement ($\Delta_R = +32.05$ pp).

### 2. Does the metric measure the intended construct?
**YES**. $\Gamma_t = (\mu_{R,t} - \mu_{R,0}) - (\mu_{C,t} - \mu_{C,0})$ measures excess state-dependent recovery. The paper's adoption of **State-Matched Interaction Contrast** rather than observational Difference-in-Differences is mathematically precise and avoids parallel-trends vulnerabilities.

### 3. Does the experimental design support the interpretation?
**YES**. The within-subject blocked factorial design ($2 	imes 2$ factorial nested within problem instances) guarantees that the Recovery and Control conditions are evaluated on identical problem statements, eliminating between-item confounding.

### 4. Are repeated rollouts treated as independent incorrectly?
**NO**. The authors correctly recognize that rollouts on the same problem are correlated. All primary confidence intervals and tests use a **problem-blocked cluster bootstrap** ($B=10,000$), cluster-robust OLS, and GEE with exchangeable working correlation. The inferential hierarchy is maintained.

### 5. Do uncertainty estimates match the experimental hierarchy?
**YES**. The cluster bootstrap standard error ($	ext{SE} = 0.0114$) matches the cluster-robust regression standard error ($	ext{SE} = 0.0115$) and the jackknife standard error ($	ext{SE} = 0.0114$).

### 6. Is multiple testing handled correctly?
**YES**. The revised paper honestly reports that while early emergence at Step 32 is nominally significant under unadjusted testing ($p = 0.019$), it yields $p = 0.076$ under Bonferroni adjustment across the trajectory family (95% simultaneous CI $[-0.0100, +0.0789]$ crosses zero). Family-wise significance is robustly confirmed by Step 96 ($p < 0.001$).

### 7. Does the main result survive appropriate sensitivity analyses?
**YES**. The effect survives:
- Strict decontamination filtering ($N=388, \Gamma = +0.1160, p < 0.0001$).
- Error-operator stratification (Constant: $+14.32$ pp, Sign: $+12.33$ pp).
- Difficulty stratification (constant $\Delta_R pprox +32$ pp across $L_2..L_5$).
- Split-half seed replication ($K=8$ vs $K=8$: $+12.65$ pp vs $+11.06$ pp).

### 8. Is the reported checkpoint trend accurately described?
**YES**. The revised manuscript transparently reports intermediate sampling dips at steps 160 and 224, disavows rigid pairwise monotonicity, and models the global progression using order-restricted isotonic regression (PAVA, $p < 0.001$).

### 9. Is clean-task performance distinguished from recovery?
**YES**. Problem-level variance decomposition demonstrates that recovery improvement is uncorrelated with clean improvement ($r = 0.0794, p = 0.091, R^2 = 0.63\%$). Recovery adaptation is an autonomous capability dimension ($99.37\%$ independent variance).

### 10. Can the verifier explain the observed result?
**NO**. The verifier is a deterministic SymPy symbolic equivalence engine with zero neural weights and zero evaluator drift across checkpoints.

### 11. Are relevant baselines missing?
**NO**. The matched valid prefix ($C$) at Step 0 and Step 256 serves as the ideal counterfactual baseline. Prompt-based self-correction and SFT baselines are thoroughly discussed.

### 12. Has related work been represented accurately?
**YES**. Accurately contextualizes Huang et al. (ICLR 2024), Stechly et al. (2024), SCoRe (Kumar et al. 2024), and DeepScaleR (Luo et al. 2025) without misrepresentation.

### 13. Is the contribution meaningfully differentiated?
**YES**. It moves beyond multi-turn verbal prompting to study continuous single-rollout recovery under RLVR.

### 14. Does the paper overstate generalization?
**NO**. The revised manuscript exercises disciplined scope bounding, explicitly restricting claims to mathematical reasoning in the DeepScaleR/Qwen-2.5-Math architecture.

### 15. Can any result not be reproduced?
**NO**. The bundled `./run_analysis.sh` pipeline executes in $< 3.0$ seconds on CPU, reproducing all primary cell means, CIs, trajectory points, and natural recovery statistics.

### 16. Does the paper comply with NeurIPS policies?
**YES**. Double-blind anonymization, 9-page limit, mandatory checklist, and code release policies are fully satisfied.

---

## 3. Reviewer Strengths & Minor Constructive Suggestions

### Strengths:
1. **Exceptional Empirical Grounding**: 29,056 empirical rollouts with zero missing values and balanced factorial cells.
2. **Methodological Rigor**: Counterfactual prefix matching solves the fundamental confounding problem between forward accuracy and recovery.
3. **Statistical Integrity**: Transparent dual reporting of Bonferroni bounds and honest disclosure of non-monotonic trajectory dips.
4. **Instant Reproducibility**: CPU reproduction in $<3$ seconds.

### Minor Suggestions for Final Camera-Ready:
- Emphasize the fraction-flip boundary condition in the discussion: why severe dimensional scale corruptions are less recoverable than sign or constant errors.
- Ensure all repository URLs in the published version use an anonymous OSF or Zenodo repository during review.
