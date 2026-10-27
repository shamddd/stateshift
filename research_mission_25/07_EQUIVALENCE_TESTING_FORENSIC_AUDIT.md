# StateShift Research Mission 25: Equivalence Testing Forensic Audit

**Author:** Multidisciplinary Independent Scientific Audit Committee  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Audit Target:** Major Scientific Issue M3 (Post-Hoc Equivalence Testing and Margin Origin)  
**Date:** October 27, 2026  
**Status:** Certified & Finalized  

---

## 1. The Core Scientific Defect (Issue M3)

In Mission 24 reporting and the release candidate manuscript (`paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex`, Section 5.3), the text stated:
> *"Practical Equivalence (TOST): To test whether the true effect is practically negligible, we conduct Two One-Sided Tests (TOST) under an equivalence margin of $\Delta = \pm 0.0385$ ($\pm 3.85\text{ pp}$)... Because both $p_1, p_2 < 0.05$, the data are statistically compatible with practical equivalence within bounds of $\pm 3.85\text{ pp}$, demonstrating that any true difference between state-preserving continuation and forced restart is minimal."*

The Audit Committee conducted a forensic examination into the origin, timing, and validity of this equivalence analysis.

---

## 2. Forensic Investigation of the $\pm 3.85\%$ Margin Origin

### 2.1 Search Across Preregistration Documents
The committee searched all preregistration manifests, scripts, and reports created prior to the 924-generation confirmatory GPU execution:
- `research_mission_22/01_CONFIRMATORY_PROTOCOL_SPECIFICATION.md`
- `research_mission_22_1/01_FINAL_PREFLIGHT_AUTHORIZATION.md`
- `research_mission_22_2/01_DEFINITIVE_STATISTICAL_RECONCILIATION.md`
- `research_mission_22/data/confirmatory_231_manifest.jsonl`

**Finding:** The value `0.0385`, `3.85%`, and the concept of a Two One-Sided Tests (TOST) equivalence margin **appear nowhere in any preregistered document**. The frozen confirmatory protocol prespecified ONLY:
1. Hypothesis test: Exact conditional two-sided McNemar test at $\alpha = 0.05$.
2. Null hypothesis: $H_0: \tau_{F-D} = 0$.
3. Sample size: $N = 231$ held-out problems.

### 2.2 Mathematical Origin of the $\Delta = 0.0385$ Threshold
How was $\Delta = 0.0385$ chosen in Mission 24?
In the confirmatory trial on $N=231$ problems:
- $\hat{\tau}_{F-D} = -0.004329$
- $\text{SE}_{\hat{\tau}} = \sqrt{\frac{11 + 12 - (11-12)^2/231}{231^2}} = 0.020757$

Computing a standard two-sided $90\%$ paired Wald confidence interval (the confidence interval corresponding to $\alpha = 0.05$ one-sided tests in the TOST procedure):
$$\text{CI}_{90\%} = \hat{\tau} \pm z_{0.95} \cdot \text{SE} = -0.004329 \pm 1.644853 \times 0.020757$$
$$\text{Lower Bound} = -0.004329 - 0.034142 = -0.03847 \approx \mathbf{-0.0385 \quad (-3.85\%)}$$
$$\text{Upper Bound} = -0.004329 + 0.034142 = +0.02981 \approx \mathbf{+0.0298 \quad (+2.98\%)}$$

### Forensic Conclusion:
The equivalence margin $\Delta = \pm 0.0385$ was **manufactured post-hoc by rounding the lower limit of the observed 90% confidence interval**. Setting the equivalence margin to the observed confidence limit guarantees by algebraic identity that $p_{\text{TOST}} \le 0.05$. 

This is circular reasoning: it chooses the goalpost after seeing where the ball landed, and presents the resulting $p < 0.05$ as if it were independent confirmatory evidence of equivalence.

---

## 3. Methodological Violations in the Claim

1. **Post-Hoc Claiming of Confirmatory Equivalence**:
   In Neyman-Pearson equivalence testing, the smallest effect size of interest (SESOI) $\Delta$ MUST be established independently of the data based on substantive domain considerations (e.g., what difference in competitive math benchmark accuracy is practically negligible). Selecting $\Delta$ to match the observed standard error turns an arbitrary precision limit into a purported substantive discovery.
2. **Conflating "Failure to Reject Null" with "Proven Equivalence"**:
   Under the preregistered McNemar test, $p = 1.000000$ indicates that the observed discordance ($b=11, c=12$) provides zero evidence against the null hypothesis $\tau = 0$. However, failing to reject $\tau = 0$ is NOT proof that $\tau = 0$. The data are equally compatible with true differences anywhere in the 95% confidence interval $[-0.0450, +0.0364]$.
3. **Absence of Domain Justification**:
   A margin of $\pm 3.85$ percentage points represents $\approx 9$ problems out of 231. In competitive mathematics benchmarks, a $\approx 4\%$ swing is substantial (often separating major model revisions). Calling $\pm 3.85\%$ "negligible" without domain justification is unsupported.

---

## 4. Remediation Decisions for Mission 25

1. **Remove Confirmatory Practical Equivalence Claims**:
   All text claiming that the experiment "establishes practical equivalence" or "proves equivalence within $\pm 3.85\%$" must be deleted from the Abstract, Section 5, and Conclusion.
2. **Accurate Standard Reporting**:
   The manuscript must state the standard, honest frequentist conclusion:
   > *"The confirmatory trial failed to detect a statistically significant difference between state-preserving continuation and forced restart ($\hat{\tau}_{F-D} = -0.43\%, \text{exact McNemar } p = 1.000000$). The paired 95% confidence interval $[-4.50\%, +3.64\%]$ strictly excludes the discovery pilot's point estimate of $+6.0\%$. However, because no equivalence margin was preregistered, this failure to reject the null cannot be interpreted as confirmatory evidence of practical or exact equivalence."*
3. **Optional Exploratory Sensitivity Context**:
   If equivalence margins are discussed in the Discussion or Appendix, they must be explicitly labeled as an unpreregistered exploratory sensitivity analysis, illustrating the minimum margin under which the current sample size would have been powered.
