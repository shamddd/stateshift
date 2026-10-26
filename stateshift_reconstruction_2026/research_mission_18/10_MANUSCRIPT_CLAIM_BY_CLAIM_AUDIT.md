# StateShift: Research Mission 18 — Manuscript Claim-by-Claim Audit

**Audit Date:** October 26, 2026  
**Auditor Committee:** Independent Scientific Audit Committee (Manuscript Integrity & Editorial Directorate)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Target Manuscript:** `08_REVISED_STATESHIFT.tex`  

---

## 1. Executive Summary & Audit Overview

The Manuscript Integrity Directorate conducted a comprehensive, line-by-line editorial and scientific audit of `08_REVISED_STATESHIFT.tex` to ensure full compliance with NeurIPS 2027 review criteria.

**Directorate Overall Verdict: HIGHLY COMPETENT DRAFT REQUIRING 4 SURGICAL REVISIONS BEFORE SUBMISSION.**

The manuscript is structurally sound, mathematically sophisticated, and presents authentic empirical findings. However, to withstand top-tier adversarial peer review, four specific corrections are mandatory:
1. **Statistical Calibration of Primary Contrast:** Clarify that while $\hat{\tau}_{F-D} = +6.00\%$ is an empirical directional trend with an 8:2 win ratio (odds ratio 4:1), it does **not** achieve two-sided statistical significance at $\alpha = 0.05$ ($p = 0.1094$) due to sample size power constraints ($N=100$, power $47.5\%$).
2. **Correction of `math500_012` Mechanistic Wording:** Line 275 erroneously attributes a *"non-convex factorization"* to `math500_012`. This must be corrected to reflect its actual mechanism: proper divisor summation and circular semantic attractor trapping.
3. **Incorporation of the Causal Identification Boundary:** Add a dedicated discussion acknowledging that Condition F functions as an *intervention package* (lemma retention in context + token budget amortization + continuation prompt) rather than pure latent activation isolation.
4. **Transparent Inclusion of Negative Instances:** Explicitly discuss the 2 instances where forced restart outperformed state preservation (`math500_014` and `math500_052`).

---

## 2. Line-by-Line Claim Audit

### Section 4.3: Table 1 & Results Narrative (Lines 250–276)

- **Line 260–264 (Table 1):**
  - *Current Text:* Lists $\tau_{F-D} = +6.00\text{ pp}$, 95% CI $[+0.00\%, +12.00\%]$, $p = 0.1094$.
  - *Audit Finding:* Accurate. However, the table should explicitly label $p = 0.1094$ as two-sided and include the exact one-sided directional $p = 0.0547$ and discordant counts ($b=8, c=2$) for maximum transparency.
  - *Recommendation:* Update bootstrap CIs to match the verified independent simulation ($\tau_{E-D}$: $[-3.00\%, +11.00\%]$, $\tau_{F-A}$: $[+3.00\%, +16.00\%]$).

- **Line 271–274 (Empirical Monotonicity):**
  - *Current Text:* Notes $p_{\text{exact, 2-sided}} = 0.1094$, but immediately emphasizes that $\hat{\tau}_{F-A} = +9.00\text{ pp}$ is statistically significant.
  - *Audit Finding:* Reviewers may perceive this as attempting to minimize the non-significance of the primary contrast.
  - *Recommendation:* Directly state that under standard two-sided $\alpha = 0.05$, the primary contrast does not achieve statistical significance, explain the power constraint ($N=100$), and present $\tau_{F-D}$ as a promising directional trend.

- **Line 275 (Mechanistic Explanation of Recovery Dynamics):**
  - *Current Text:* *"frequently abandon valid non-convex factorizations (e.g., \texttt{math500\_012}) or exhaust the 768-token ceiling re-deriving preliminary lemmas (e.g., \texttt{math500\_092})."*
  - *Audit Finding:* **FACTUAL ERROR IN NARRATIVE.** `math500_012` is the amicable divisor counting problem (284/220), not a non-convex factorization.
  - *Recommendation:* Replace with: *"frequently fall into circular semantic attractors or abandon valid intermediate deductions (e.g., divisor re-summation in \texttt{math500\_012}) or exhaust the 768-token ceiling re-deriving preliminary lemmas (e.g., \texttt{math500\_092})."*

---

### Section 5: Discussion & Limitations (Lines 278–294)

- **Line 285–292 (Threats to Validity & Scope Boundaries):**
  - *Current Text:* Mentions only *Model Lineage* (DeepScaleR/Qwen) and *Domain Specificity* (MATH-500).
  - *Audit Finding:* Incomplete. Lacks discussion of:
    1. Statistical power limitations ($N=100$ powered at $47.5\%$; $N \ge 216$ needed for $80\%$).
    2. Causal confounders (token budget amortization and in-context lemma presence).
    3. Failure modes of state preservation (the 2 Condition D wins where long prefixes led to truncation).
  - *Recommendation:* Expand into four structured paragraphs: (1) Sample Size & Statistical Power; (2) Causal Identification & Intervention Decomposition; (3) Negative Regimes of State Preservation; (4) Model Scale & Architecture Generalizability.

---

## 3. Revised Manuscript Production Strategy (Phase 11)

The committee will author a revised submission file:
`research_mission_18/STATESHIFT_REVISED_SUBMISSION.tex`
which implements all corrections, provides complete LaTeX compilation compatibility, and embodies the highest standard of scientific humility, transparency, and rigor.
