# StateShift Research Mission 25: Equivalence Claim Correction Blueprint

**Author:** Multidisciplinary Independent Scientific Audit Committee  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Audit Target:** Replacement of Circular Post-Hoc Equivalence Claims with Frequentist Precision Bounds  
**Date:** October 27, 2026  
**Status:** Certified & Finalized  

---

## 1. Executive Summary of Equivalence Claim Corrections

Following the forensic audit in Document 07, the Audit Committee has established that the $\pm 3.85$ percentage point equivalence margin was computed post-hoc from the observed 90% confidence interval. Consequently, all statements asserting that the study "proves", "establishes", or "confirms" practical equivalence must be replaced with accurate statements regarding **estimation precision** and **failure to reject the null hypothesis**.

---

## 2. Line-by-Line Manuscript Replacement Ledger

### 2.1 Section 5.3 (Section Title & Text)
- **Original Title:**  
  `\subsection{Practical Equivalence (TOST)}`
- **Corrected Title:**  
  `\subsection{Estimation Precision and Compatibility Bounds}`
- **Original Text:**  
  `To test whether the true effect is practically negligible, we conduct Two One-Sided Tests (TOST) under an equivalence margin of $\Delta = \pm 0.0385$ ($\pm 3.85\text{ pp}$):`  
  `\begin{itemize}`  
  `    \item $H_{01}: \tau \le -0.0385 \implies z_1 = \frac{-0.0043 - (-0.0385)}{0.0208} = +1.6463 \implies p_1 = 0.0494$`  
  `    \item $H_{02}: \tau \ge +0.0385 \implies z_2 = \frac{-0.0043 - 0.0385}{0.0208} = -2.0632 \implies p_2 = 0.0195$`  
  `\end{itemize}`  
  `Because both $p_1, p_2 < 0.05$, the data are statistically compatible with practical equivalence within bounds of $\pm 3.85\text{ pp}$, demonstrating that any true difference between state-preserving continuation and forced restart is minimal.`
- **Defensible Replacement Text:**  
  `Under the preregistered frequentist testing protocol, the exact two-sided McNemar test yields $p = 1.000000$, failing to reject the null hypothesis of equal recovery rates ($H_0: \tau_{F-D} = 0$). We emphasize that failing to detect a statistically significant difference does not constitute confirmatory proof of exact or practical equivalence.`  
  `To characterize the precision of the trial, the paired Wald $95\%$ confidence interval $[-0.0450, +0.0364]$ (and Newcombe score interval $[-0.0451, +0.0365]$) defines the range of population differences statistically compatible with the observed data. These bounds strictly exclude the discovery pilot's point estimate of $+0.0600$, confirming that large positive continuation benefits are incompatible with the data. If an equivalence framework is applied post-hoc, the narrowest symmetric equivalence margin that would reject under two one-sided tests at $\alpha=0.05$ is $\Delta = \pm 3.85\text{ pp}$ (corresponding to the $90\%$ confidence bound $[-0.0385, +0.0298]$). However, because this threshold was derived from the observed data variance rather than prespecified on domain-substantive grounds, it is reported strictly as an exploratory diagnostic of estimation precision rather than confirmatory evidence of practical equivalence.`

### 2.2 Abstract & Conclusion
- Ensure that neither the Abstract nor the Conclusion states that continuation and restart are "equivalent".
- State clearly:
  > *"The primary preregistered contrast did not detect a statistically significant difference ($\hat{\tau}_{F-D} = -0.43\%, p = 1.000000$), strictly bounding the true effect within $[-4.50\%, +3.64\%]$ and excluding the pilot's $+6.0\text{ pp}$ advantage."*

---

## 3. Exit Criteria Verification for Issue M3

- [x] All claims of confirmatory practical equivalence removed.
- [x] Circular derivation of the $\pm 3.85\%$ margin explicitly disclosed as an exploratory precision diagnostic.
- [x] Clear distinction between "failure to reject null" and "proof of equivalence" enforced.
- [x] Major Issue M3 is scientifically resolved.
