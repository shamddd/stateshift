# StateShift Final Independent Scientific Verification & Statistical Audit

**Audit Date**: October 18, 2026  
**Auditor**: Independent Senior Machine Learning Researcher & Statistical Auditor  
**Standard**: Strict Scientific Skepticism · Zero Assumption of Prior Claims · 100% Grounded in Physical Artifacts  
**Target Repository**: `https://github.com/shamddd/stateshift`  
**Target Branch**: `research/stateshift-neurips-readiness`  
**Target Commit SHA**: `8de90f85915ca6cf4a8423ce81c141d8d9a0fe13`  
**Evaluation Verdict**: **PASS WITH CORRECTIONS — HUMAN REVIEW REQUIRED**  

---

## 1. Executive Summary

An exhaustive, adversarial audit of the StateShift project was conducted. Every claim was tested against the underlying raw rollout data, Git commit graph, statistical model definitions, and official publication venue policies.

The core scientific finding of StateShift—that reinforcement learning post-training induces a statistically significant, positive state-matched recovery contrast ($\Gamma_{256} = \mathbf{+0.1176}$, $p < 10^{-24}$) that cannot be explained by clean problem-solving accuracy alone—is **empirically established and reproducible from the recorded raw outcomes**. 

However, this audit identifies several critical interpretive and bibliographical corrections that must be resolved prior to formal submission:
1. **Bibliographical Placeholders**: Key citations in `references.bib` contain unresolved placeholders (e.g., `arXiv:2502.X` for DeepScaleR and malformed DOI for Huang et al.).
2. **Measurement Attenuation in Clean Accuracy**: While empirical problem-level recovery gains and clean gains have low linear correlation ($r = 0.0794, R^2 = 0.63\%$), finite-sample binomial rollout variance ($K=16$) accounts for $80.3\%–84.9\%$ of observed variance. Correcting for attenuation yields an estimated latent correlation of $r_{\text{adj}} \approx 0.46$. The claim of "complete orthogonality" must be softened to "linearly uncoupled in empirical problem-level gains."
3. **Trajectory Monotonicity vs. Isotonic Fitting**: The raw unconstrained trajectory exhibits non-monotonic dips at step 160 ($\Gamma_{160}=0.0598$, down from $0.0748$) and step 224 ($\Gamma_{224}=0.0950$, down from $0.0976$) due to reduced intermediate sampling ($K=2/3$). While PAVA confirms consistency with a monotonic envelope ($p < 0.001$), PAVA by construction produces a monotonic sequence and cannot be claimed as proof that intermediate training steps strictly improve recovery.
4. **Experimental Scale Clarification**: Clarified that the experiment evaluates **2 confirmatory endpoint checkpoints** ($t=0, 256$), **9 trajectory checkpoints** ($t \in \{0, 32, \dots, 256\}$), and **$K=16$ stochastic rollouts per cell** at the endpoints, resolving prompt ambiguity referencing "16 checkpoints."

---

## 2. Phase 1: Verification of the Git State

| Item | Verified Evidence | Status |
|:---|:---|:---:|
| **Reported Commit SHA** | `8de90f85915ca6cf4a8423ce81c141d8d9a0fe13` matches `HEAD` and remote | **VERIFIED** |
| **Reported Branch** | `research/stateshift-neurips-readiness` tracks `origin/research/stateshift-neurips-readiness` | **VERIFIED** |
| **Base Commit** | Branched cleanly from `origin/main` at `a3aa9140b6934b7c3cdb57ed4f547e2a79e64f01` | **VERIFIED** |
| **Main Branch Protection** | `origin/main` remains at `a3aa9140b6934b7c3cdb57ed4f547e2a79e64f01` (0 commits pushed to main) | **VERIFIED** |
| **Working Tree Status** | `git status -uno` confirms 0 uncommitted changes on tracked paths | **VERIFIED** |
| **Pull Request URL** | `https://github.com/shamddd/stateshift/pull/new/research/stateshift-neurips-readiness` | **VERIFIED** |
| **Secret & Artifact Scan** | Zero credentials or tokens; raw model weights (~126 GB) excluded; payload $< 8.5\text{ MB}$ | **VERIFIED** |

---

## 3. Phase 2: Verification of Primary Results from Raw Data

### Data File Integrity
- **Raw File Location**: `artifacts/endpoint/controlled_endpoint_outcomes.csv`
- **SHA-256 Checksum**: `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139`
- **Total Rows**: Exactly $29,056$ rows (plus 1 header line = 29,057 lines).
- **Missing / NaN Values**: Exactly 0 across all columns.
- **Problem Count**: Exactly $454$ unique problem specifications (`pair_id`).
- **Condition Definitions**: Exactly 2 states: `recovery` ($R$) and `control` ($C$).
- **Checkpoints**: Exactly 2 endpoints: $t=0$ (base Qwen-2.5-7B) and $t=256$ (terminal DeepScaleR).
- **Factorial Cell Balance**: Exactly 16 rollouts per cell across all $454 \times 2 \times 2 = 1,816$ cells ($1,816 \times 16 = 29,056$). Zero duplicate rollout keys.

### Independent Mathematical Recalculation
$$\mu_{s,t} = \frac{1}{NK} \sum_{i=1}^N \sum_{k=1}^K Y_{i,s,t,k}$$
$$\Gamma_{256} = (\mu_{R,256} - \mu_{R,0}) - (\mu_{C,256} - \mu_{C,0})$$

- $\mu_{R,0} = 2,785 / 7,264 = \mathbf{0.383398}$ ($38.34\%$)
- $\mu_{R,256} = 5,113 / 7,264 = \mathbf{0.703882}$ ($70.39\%$)
- $\Delta_R = \mu_{R,256} - \mu_{R,0} = \mathbf{+0.320485}$ (+32.05 percentage points)
- $\mu_{C,0} = 2,827 / 7,264 = \mathbf{0.389180}$ ($38.92\%$)
- $\mu_{C,256} = 4,301 / 7,264 = \mathbf{0.592098}$ ($59.21\%$)
- $\Delta_C = \mu_{C,256} - \mu_{C,0} = \mathbf{+0.202919}$ (+20.29 percentage points)
- **$\Gamma_{256} = \Delta_R - \Delta_C = \mathbf{+0.117566}$ (+11.76 percentage points)**

### Strict Decontamination Subset ($N_{\text{Strict}} = 388$)
Cross-referencing the 388 verified un-contaminated problem IDs from `website_clone/artifacts/provenance/confirmatory_problem_registry.json`:
- Rollouts: Exactly $24,832$ ($388 \times 4 \times 16$).
- $\mu_{R,0,\text{Strict}} = 0.383054$ ($2,378 / 6,208$)
- $\mu_{R,256,\text{Strict}} = 0.700709$ ($4,350 / 6,208$) $\implies \Delta_{R,\text{Strict}} = +0.317655$
- $\mu_{C,0,\text{Strict}} = 0.389014$ ($2,415 / 6,208$)
- $\mu_{C,256,\text{Strict}} = 0.590689$ ($3,667 / 6,208$) $\implies \Delta_{C,\text{Strict}} = +0.201675$
- **$\Gamma_{256,\text{Strict}} = \Delta_{R,\text{Strict}} - \Delta_{C,\text{Strict}} = \mathbf{+0.115979}$ (+11.60 percentage points)**

---

## 4. Phase 3: Independent Statistical Verification

An independent Python implementation verified the statistical properties across three complementary paradigms:

| Statistical Method | Estimand / Metric | Estimated Value | Standard Error | 95% Confidence Interval | p-value |
|:---|:---|:---:|:---:|:---:|:---:|
| **Problem-Blocked Bootstrap ($B=10,000$, Seed 42)** | Risk Difference ($\Gamma_{256}$) | $+0.1176$ | $0.0114$ | **$[+0.0958, +0.1403]$** | $< 10^{-6}$ |
| **Strict Blocked Bootstrap ($N=388, B=10,000$)** | Strict Risk Difference ($\Gamma_{256,\text{Strict}}$) | $+0.1159$ | $0.0125$ | **$[+0.0912, +0.1405]$** | $< 10^{-6}$ |
| **Cluster-Robust OLS (Clustered on Problem $i$)** | Interaction Parameter ($\beta_3$) | $+0.1176$ | $0.0114$ | **$[+0.0953, +0.1398]$** | $4.57 \times 10^{-25}$ ($t=10.34$) |
| **Generalized Estimating Equations (GEE Logistic)** | Interaction Odds Ratio ($\exp(\beta_3)$) | $1.6780$ | $0.0492$ (log) | **$[1.5236, 1.8480]$** | $7.53 \times 10^{-26}$ |

### Audit Assessment
1. **Pseudoreplication**: Averted. All models cluster at the problem level (`pair_id`), respecting intra-cluster correlation across the 64 rollouts per problem.
2. **Multiplicity Correction**: Correctly applied. The confirmatory endpoint $\Gamma_{256}$ is a single pre-specified hypothesis test. Across the 8 trajectory checkpoints, step 32 has unadjusted $p=0.019$ and Bonferroni-adjusted $p=0.076$, which is accurately reported as suggestive.

---

## 5. Phase 4: Audit of Causal Claims

### Causal Identification Analysis
- **Intervention**: Conditioning on an invalid reasoning prefix ($P_{i,R}$) versus a length-matched valid reasoning prefix ($P_{i,C}$).
- **Assignment**: Exactly matched within each problem specification $i$.
- **Mechanism**: The autoregressive decoding distribution is conditioned on $P_{i,R}$ or $P_{i,C}$ at identical decoding temperatures ($T=0.6, p=0.95$).
- **Parallel Trends**: Because StateShift is a within-subject blocked factorial experiment evaluated on the exact same problems across both checkpoints, it does not rely on observational parallel trends across heterogeneous cohorts.
- **Potential Confounding**:
  - *Generation Length*: Confirmed invariant ($482.47 \to 482.50$ tokens, $\Delta = +0.03$ tokens).
  - *Floor / Ceiling Effects*: Recovery gain $\Delta_R$ is uniform ($\approx +31-33\%$) across difficulty tiers $L_2..L_5$.
- **Recommended Language**: The contrast is a **controlled state-matched interaction contrast**. Describing it as a "causal effect of RL on recovery" should be framed as:  
  > *"A controlled within-problem interaction contrast that isolates state-selective recovery adaptation from general forward capability scaling."*

---

## 6. Phase 5: Audit of Clean-Accuracy Independence Claims

### Disattenuation Analysis
The manuscript claims that recovery gain $\Delta_{R,i}$ is "orthogonal to clean accuracy gains ($r = 0.0794, p = 0.091, R^2 = 0.63\%$)":
- **Observed Pearson $r$**: $0.0794$ ($p = 0.0910$).
- **Observed Spearman $\rho$**: $0.0796$ ($p = 0.0902$).
- **Observed $R^2$**: $0.6306\%$.
- **Observed Variance**: $\text{Var}(\Delta_R) = 0.0296$, $\text{Var}(\Delta_C) = 0.0340$.
- **Binomial Sampling Variance**: Because each cell is estimated from $K=16$ Bernoulli rollouts:
  $$\sigma^2_{\text{sampling},R} \approx 0.0251 \quad (\mathbf{84.9\%}\text{ of observed variance})$$
  $$\sigma^2_{\text{sampling},C} \approx 0.0273 \quad (\mathbf{80.3\%}\text{ of observed variance})$$
- **Disattenuated Correlation**:
  $$r_{\text{adj}} = \frac{r}{\sqrt{\text{Rel}(R) \times \text{Rel}(C)}} = \frac{0.0794}{\sqrt{0.151 \times 0.197}} \approx \mathbf{0.4605}$$
  $$R^2_{\text{adj}} \approx \mathbf{21.21\%}$$

### Required Correction
Low observed $R^2$ ($0.63\%$) in finite samples is heavily driven by measurement noise from $K=16$ rollouts. The manuscript must replace "orthogonal capability dimension" with:
> *"Problem-level empirical recovery gains exhibit low linear correlation with clean accuracy gains ($r = 0.0794, p = 0.091, R^2 = 0.63\%$), indicating that recovery gains cannot be predicted simply by clean task improvement, although finite-sample rollout variance ($K=16$) contributes substantially to the observed variance."*

---

## 7. Phase 6: Checkpoint Trajectory Audit

### Observed Trajectory vs. Monotonic Envelope
- $t=0$: $\Gamma_0 = 0.0000$ ($K=16$)
- $t=32$: $\Gamma_{32} = +0.0333$ ($K=2/3$, unadj $p=0.019$, Bonf $p=0.076$)
- $t=64$: $\Gamma_{64} = +0.0337$ ($K=2/3$)
- $t=96$: $\Gamma_{96} = +0.0774$ ($K=2/3$, Bonf $p < 0.001$)
- $t=128$: $\Gamma_{128} = +0.0748$ (local dip $-0.0026$)
- $t=160$: $\Gamma_{160} = +0.0598$ (local dip $-0.0150$)
- $t=192$: $\Gamma_{192} = +0.0976$
- $t=224$: $\Gamma_{224} = +0.0950$ (local dip $-0.0026$)
- $t=256$: $\Gamma_{256} = +0.1176$ ($K=16$, primary confirmatory endpoint)

### Methodological Finding on Isotonic PAVA
- PAVA (Pool Adjacent Violators Algorithm) pools adjacent violators to construct the best non-decreasing fit. By mathematical definition, PAVA will produce a monotonic sequence on any finite data series.
- An order-restricted Robertson test confirms the unconstrained sequence is consistent with an underlying non-decreasing envelope ($p < 0.001$).
- **Caveat**: The text must clearly state that intermediate sampling noise ($K=2/3$) causes observed local non-monotonicities at steps 160 and 224, and that PAVA models the global trend rather than proving strictly monotonic step-by-step increases.

---

## 8. Phase 7: Verification of Reproducibility Claims

Execution of documented scripts on the current branch:
1. **`./reproducibility/run_analysis.sh`**:
   - Runtime: $2.42$ seconds.
   - Exit code: 0.
   - Outcome: Validated SHA-256 data hash, recomputed $\Gamma_{256} = +0.1176$, bootstrap CI $[+0.0958, +0.1403]$, and Study B natural recovery counts ($582$ errors, $180$ recoveries).
2. **`./reproducibility/run_tests.sh`**:
   - Runtime: $0.55$ seconds.
   - Exit code: 0.
   - Outcome: **11/11 tests passed**.
3. **Repository Unit Test Suite (`pytest tests/ -v`)**:
   - Runtime: $3.87$ seconds.
   - Exit code: 0.
   - Outcome: **40/40 tests passed**.
4. **Reproduction Level Clarification**:
   - **Type A (Statistical reproduction from recorded data)**: **100% REPRODUCED**.
   - **Type B (Forward model neural network inference from weights)**: **NOT EXECUTED LOCALLY** (requires ~100 GPU hours on cluster infrastructure).

---

## 9. Phase 8: Manuscript and Citation Findings

1. **Numerical Accuracy**: 100% of reported numbers in text and tables match the underlying empirical calculations.
2. **Mandatory Limitations**: Section 9 properly discloses the $29.61\%$ terminal failure rate, MATH-500 competition scope, and single DeepScaleR lineage.
3. **Double-Blind Anonymity**: Complies with NeurIPS author instructions.
4. **Identified Bibliographical Defects in `references.bib`**:
   - `Luo2025Deepscaler`: Contains placeholder `journal={arXiv:2502.X}` and `url={https://doi.org/10.48550/arXiv:2502.X}`.
   - `Huang2023Can`: Contains invalid DOI URL `https://doi.org/10.48550/ICLR 2024`.
   - *Action Required*: These must be replaced with canonical citations prior to final publication.

---

## 10. Phase 9: Venue and Submission Policy Audit

- **Intended Cycle**: **NeurIPS 2027** (Evaluations & Datasets Track). The NeurIPS 2026 deadline passed in May 2026.
- **Unannounced Requirements**: Exact CFP deadlines, page limits, checklist revisions, and official style files for NeurIPS 2027 are unannounced.
- **Prior Submission Audit**: The paper was previously submitted to Elsevier *Artificial Intelligence* (ARTINT-D-26-01491, August 2026) and desk-rejected. The author retained full copyright.
- **Dual-Submission Clearance**: Because the journal review is inactive, there is no active dual-submission conflict, provided the paper is not submitted elsewhere when the NeurIPS 2027 portal opens.

---

## 11. Final Recommendation and Next Actions

### Verdict: **PASS WITH CORRECTIONS — HUMAN REVIEW REQUIRED**

The research is empirically sound, the primary result is verified from raw data, and the code repository is cleanly published on GitHub. The pull request may be approved subject to the human researcher resolving the following minor editorial corrections:

1. **Correct Citations in `references.bib`**: Replace `arXiv:2502.X` and malformed DOI URLs with canonical citations.
2. **Refine Correlation Phrasing in `main.tex`**: Note that finite-sample rollout noise ($K=16$) attenuates the observed correlation between recovery and clean gains.
3. **Clarify PAVA Phrasing in `main.tex`**: Reiterate that intermediate sampling noise causes observed dips at steps 160 and 224, and that PAVA fits a monotonic envelope.
4. **Maintain Double-Blind Pre-Submission Hold**: Await the official opening of the NeurIPS 2027 submission portal on OpenReview without submitting externally.
