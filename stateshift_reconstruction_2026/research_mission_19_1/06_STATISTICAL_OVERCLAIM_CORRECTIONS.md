# StateShift: Research Mission 19.1 — Statistical Overclaim Corrections & Language Disinfection

**Date:** October 26, 2026  
**Auditor:** Independent Statistical Methodology & Scientific Integrity Directorate  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Investigation Target:** Eradication of All Claims Implying "Guaranteed Significance" or "Guaranteed Publication Acceptance"  

---

## 1. Executive Summary: The Defect of "Guaranteed Significance"

In previous working documents (specifically `research_mission_19/11_FINAL_PUBLICATION_READINESS_GATE.md` and `research_mission_19/08_MINIMUM_DECISIVE_FUTURE_EXPERIMENT.md`), wording inadvertently appeared asserting that expanding the sample size to $N=231$ offered a:
> *"100% guaranteed two-sided $p < 0.05$ confirmation"* or *"guaranteed two-sided statistical significance"*.

### Scientific Correction:
This statement is mathematically and methodologically false:
1. **Definition of Statistical Power:** Statistical power ($1 - \beta = 0.80$) represents the **probability of rejecting the null hypothesis** at $\alpha = 0.05$ *if and only if* the true data-generating process strictly satisfies the specified alternative hypothesis ($p_{10} = 0.08, p_{01} = 0.02$).
2. **Type II Error Rate ($\beta = 20\%$):** Even if the true effect size is exactly $+6.00\%$, an experiment designed for $80\%$ power carries an inherent **$20\%$ probability of failing to reject the null** (yielding $p > 0.05$) purely due to stochastic binomial sampling noise.
3. **Winner's Curse & Effect-Size Shrinkage:** The pilot estimate of $\hat{\tau}_{F-D} = +6.00\%$ is derived from $N=100$. Due to the "winner's curse", empirical effect sizes observed in small discovery cohorts frequently shrink when evaluated in larger confirmatory samples. If the true effect size is $+4.0\%$ or $+3.0\%$, the power at $N=231$ will be substantially lower than $80\%$.
4. **Possibility of Null or Negative Outcomes:** A larger sample can empirically yield a non-significant result, a smaller delta, a null outcome, or an effect in the reverse direction.

---

## 2. Inventory of Eradicated Language & Mandatory Replacements

| Document & Line | Errant Overclaim Phrase | Corrected Scientific Statement | Reason for Correction |
| :--- | :--- | :--- | :--- |
| `11_FINAL_PUBLICATION_READINESS_GATE.md` (Line 49) | *"If the PI desires a 100% guaranteed two-sided $p < 0.05$ confirmation..."* | *"If the PI desires a pre-registered confirmatory trial powered at $80\%$ ($1 - \beta = 0.80$) under pilot parameters..."* | No sample size guarantees $p < 0.05$; power is a probability, not a certainty. |
| `08_MINIMUM_DECISIVE_FUTURE_EXPERIMENT.md` (Line 94) | *"Scenario B offers an optional path to guaranteed two-sided statistical significance."* | *"Scenario B specifies a pre-registered confirmatory trial designed to achieve $80\%$ statistical power under pilot assumptions."* | Eradicates "guarantee" of rejection. |
| `10_ADVERSARIAL_REVIEW_RESPONSE_MATRIX.md` | *"leaves zero statistical objections"* | *"transparently addresses sample size power bounds and specifies confirmatory sample requirements"* | Eliminates hyperbolic dismissal of reviewer scrutiny. |

---

## 3. Strict Guidelines for Manuscript and Reports

All project documents must strictly observe the following rules:
- **Never use "guarantee", "certain rejection", or "100% confirmation"** in connection with statistical hypotheses or future experiments.
- **Always report the assumed alternative explicitly:** e.g., *"Under the assumption that the true discordant rate is $q = 0.10$ and success bias is $\theta = 0.80$, an $N=231$ cohort provides an estimated $80\%$ probability of rejecting $H_0$ at $\alpha = 0.05$."*
- **Explicitly discuss winner's curse and shrinkage:** Note that true effect sizes in confirmatory cohorts may be attenuated relative to discovery estimates.
- **Frame $N=100$ as an exploratory discovery study:** Transparently report exact two-sided $p = 0.1094$, one-sided $p = 0.0547$, and Newcombe 95% CI $[-0.12\%, +12.18\%]$.
