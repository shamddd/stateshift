# Research Mission 23 — Phase 2: Major Scientific Remediation Report

## 1. Scope & Objective
This report addresses and formally closes the five Major Scientific Issues (M1–M5) identified across the StateShift research record to ensure that all claims, interpretations, and statistical statements meet the standard of NeurIPS 2027 peer review.

---

## 2. Major Issue M1 — Causal Mechanism Boundary and Overclaim Remediation

### Remediation Directive
All overreaching descriptions of causal mechanisms—including past assertions that context-length confounding was "decisively refuted", that semantic validity was "proven to be the sole causal mechanism", or that StateShift performs "hidden-state steering" or "KV-cache tensor editing"—are explicitly retracted and quarantined.

### Mandatory Standardized Formulation
Across all active reports, manuscript sections, and documentation, the causal scope of StateShift is defined by the following standardized text:

> **"The primary experiment estimates the effect of a bundled prompt-level continuation intervention relative to forced restart. The intervention combines retained reasoning context, continuation instructions, and potentially different effective reasoning budgets. Existing controls are consistent with a contribution from semantically valid context but do not uniquely isolate the causal mechanism."**

### Explicit Boundary Disclaimers
1. **No Internal State Manipulation**: StateShift operates exclusively at the autoregressive prompt boundary. It does not manipulate hidden vectors, edit KV-cache tensors, apply activation patches, or update model weights.
2. **Bundled Intervention Complexity**: Because Condition F introduces both the valid reasoning prefix up to the corruption point ($x_{1:k-1}$) and specific recovery turn phrasing, the treatment contrast represents a package intervention. While ablations show that corrupt prefixes degrade performance, this evidence is consistent with a contribution from valid context but cannot rule out joint interaction effects.

---

## 3. Major Issue M2 — Token-Budget and Context-Length Confounding Analysis

### Empirical Recomputation of Pilot Generation Budgets ($N=100$)
An exhaustive accounting of output lengths, finish reasons, and truncation rates was conducted across the 400 pilot generations:

| Condition | Prompt Length (Chars / Words) | Output Length (Mean Chars / Words) | Completion Status (`COMPLETED` vs `TRUNCATED`) | Finish Reason (`stop` vs `length`) | Accuracy on `stop` (Natural Finish) | Accuracy on `length` (Truncated) | Overall Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A: Zero-Shot** | 282.1 / 44.7 | 1385.7 / 262.6 | 70 / 30 | 70 `stop` / 30 `length` | 64 / 70 (91.4%) | 0 / 30 (0.0%) | 64.00% |
| **D: Forced Restart** | 607.3 / 96.3 | 1302.6 / 248.7 | 76 / 24 | 76 `stop` / 24 `length` | 67 / 76 (88.2%) | 0 / 24 (0.0%) | 67.00% |
| **E: Explicit Repair**| 615.3 / 97.3 | 1236.7 / 234.9 | 76 / 24 | 76 `stop` / 24 `length` | 68 / 76 (89.5%) | 3 / 24 (12.5%) | 71.00% |
| **F: State-Preserving**| 589.3 / 93.3 | 1269.9 / 244.2 | 78 / 22 | 78 `stop` / 22 `length` | 71 / 78 (91.0%) | 2 / 22 (9.1%) | 73.00% |

### Methodological Evaluation of Token-Budget Confounding
1. **Condition E Evidence Interpretation**:
   - Condition E has a slightly longer mean prompt length than Condition F (615.3 vs 589.3 characters in confirmatory prompts).
   - In pilot outputs, Condition E exhibited an identical truncation count to Condition D (24 truncated), while Condition F had 22 truncated.
   - However, **we do not conclude that longer prompts necessarily produce less effective output headroom**, nor do we claim that small differences in truncation parity eliminate token-budget confounding.
2. **Intermediate Reasoning Headroom**:
   - Because Condition F supplies $x_{1:k-1}$ as part of the prompt, the model starts its new generation closer to the final conclusion. In contrast, Condition D must re-generate the entire multi-step reasoning derivation from scratch within the same 768-token ceiling.
   - Therefore, the effective reasoning budget available for completing the problem is structurally asymmetric between Condition F and Condition D. This asymmetry is an inherent component of the bundled continuation intervention and is explicitly acknowledged as an unisolated factor.

---

## 4. Major Issue M3 — Confirmatory Sample Independence and Generalization Limits

### Standardized Sample Description
The confirmatory evaluation dataset ($N = 231$ problems) is strictly designated across all research materials as:

> **"Disjoint held-out MATH-500 confirmatory sample selected without reference to confirmatory model outcomes."**

### Prohibited Overclaims
- **No Cross-Benchmark Generalization**: The confirmatory trial is drawn from MATH-500; findings cannot be generalized to Olympiad-level benchmarks (e.g., Putnam, AIME) or non-mathematical planning domains without future evaluation.
- **No Guaranteed Pretraining Independence**: Because MATH-500 is a widely circulated open benchmark derived from the MATH dataset, pretraining data decontamination cannot be mathematically guaranteed across proprietary or open pretraining corpora.
- **No Benchmark Contamination Immunity**: The audit certifies that the confirmatory sample is disjoint from the pilot exploration set ($\mathcal{P}_{\text{pilot}} \cap \mathcal{P}_{\text{confirmatory}} = \emptyset$), but makes no claim of pretraining corpus decontamination.

---

## 5. Major Issue M4 — Assumption-Dependent Power Interpretation

### Exact Power Calculation Under Alternative Regimes
The finite-sample exact power equation for the two-sided exact McNemar test at $\alpha = 0.05$ was re-evaluated under alternative parameter assumptions:

| Discordance Rate $q = p_{01} + p_{10}$ | Treatment Effect $\delta = p_{01} - p_{10}$ | Conditional Probability $\psi = \frac{p_{01}}{q}$ | Sample Size $N$ | Exact Power (%) | Sample Size for 80% Power | Sample Size for 90% Power |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0.10 (Pilot Estimate)** | **+0.06** | **0.8000** | **231** | **80.07%** | **231** | **308** |
| 0.12 | +0.06 | 0.7500 | 231 | 72.14% | 275 | 366 |
| **0.14 (Elevated Discordance)**| **+0.06** | **0.7143** | **231** | **65.86%** | **322** | **428** |
| 0.16 | +0.06 | 0.6875 | 231 | 60.72% | 369 | 490 |

### Scientific Governance Directive
1. **Power is an Assumption-Dependent Estimate**: Power is strictly a function of assumed population parameters ($q=0.10, \delta=0.06$).
2. **No Guaranteed Significance**: Achieving $80.07\%$ power means there remains an approximate $\sim 20\%$ probability of failing to reject the null hypothesis even if the true population effect is $+0.06$. If discordance elevates to $q=0.14$, the probability of a false negative increases to $34.14\%$.
3. **Equivalence Disclaimer**: A nonsignificant confirmatory test ($p \ge 0.05$) will be reported as failing to reject the null hypothesis, and will not be conflated with a proof of equivalence or zero effect.

---

## 6. Major Issue M5 — Evaluator Consistency & Pre-Execution Freeze

### Pilot Reconciliation Preservation
The Mission 22.2 forensic reconciliation is permanently maintained:
- **Canonical Primary Baseline**: $a=65, b=8, c=2, d=25 \implies \text{Acc}(F)=73.00\%, \text{Acc}(D)=67.00\%$ (`final_verified_outcomes.csv`, strict degree normalization $90 \ne 90^\circ$).
- **Unit-Flexible Sensitivity**: $a=66, b=8, c=2, d=24 \implies \text{Acc}(F)=74.00\%, \text{Acc}(D)=68.00\%$ (degree symbol stripped $90 == 90^\circ$).
- Discrepancy localized 100% to problem `math500_007`.

### Pre-Execution Confirmatory Evaluator Freeze
The primary confirmatory evaluation is **permanently frozen prior to execution**:
- The primary confirmatory analysis will execute `cleanroom_is_mathematically_equivalent` with **canonical degree normalization (Path A: strict matching)** as the primary preregistered endpoint, alongside **Path B (unit-flexible normalization)** as a pre-declared sensitivity analysis.
- The evaluator selection cannot be altered after inspecting confirmatory generations.
