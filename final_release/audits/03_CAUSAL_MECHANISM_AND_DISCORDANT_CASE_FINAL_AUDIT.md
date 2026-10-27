# Deliverable 03: Causal Mechanism and Discordant Case Final Audit

**Mission**: StateShift Research Mission 26 (Final Consolidated Release)  
**Date**: October 27, 2026  
**Auditor**: Causal Inference Specialist & Mathematical Reasoning Audit Team  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Status**: AUDITED & CERTIFIED

---

## 1. Formal Definition of the Causal Estimand

In StateShift Study 3, the primary preregistered contrast evaluates the difference in accuracy between Condition F (StateShift prompt-level recovery) and Condition D (Forced Restart):
$$\hat{\tau}_{F-D} = \mathbb{E}[Y \mid \text{do}(\text{Condition F})] - \mathbb{E}[Y \mid \text{do}(\text{Condition D})] = \frac{b - c}{N} = \frac{11 - 12}{231} = \mathbf{-0.004329 \quad (-0.43\text{ pp})}$$

### 1.1. Bundled Compound Treatment Nature
Under the Neyman-Rubin causal model and Pearl's structural causal framework, Condition F is **not an isolated single-factor manipulation**. Rather, it constitutes a compound treatment bundle:
$$\text{do}(\text{Condition F}) = \{\mathcal{S}_{1:k-1}\} \;\cup\; \{\Delta \mathcal{B}_{\text{token}}\} \;\cup\; \{\mathcal{I}_{\text{re-derive}}\}$$
where:
1. $\mathcal{S}_{1:k-1}$: Injected prefix containing preliminary reasoning tokens prior to error onset.
2. $\Delta \mathcal{B}_{\text{token}}$: Reduced generation token budget ($768 - |\mathcal{S}_{1:k-1}|$ remaining tokens) compared to the full 768-token budget granted to Condition D.
3. $\mathcal{I}_{\text{re-derive}}$: Natural language continuation prompt instructing the model to review the prefix and continue reasoning.

Because these three factors were manipulated simultaneously without factorial controls, **the separate causal effects of token headroom, cognitive inertia, prefix anchoring, verification overhead, and fallacy inheritance are formally unidentifiable**. The observed contrast $\hat{\tau}_{F-D}$ identifies strictly the net, end-to-end effect of the operational prompt bundle.

---

## 2. Forensic Audit of All 23 Discordant Problems

The 23 discordant problems ($b=11$ Condition F wins; $c=12$ Condition D wins) were audited from raw token traces in `research_mission_23/data/confirmatory_924_generations.jsonl`.

### 2.1. Operational Category Definitions
To ensure objective classification, qualitative failure modes were governed by the following strict operational rules:
- **Category 1: Token Budget Truncation (`finish_reason=length`)**: The generation reached the 768-token ceiling without emitting a terminal `\boxed{...}` answer.
- **Category 2: Derivation / Arithmetic Slips (`finish_reason=stop`)**: The generation emitted a terminal answer, but contained an algebraic, arithmetic, or logical deduction error in downstream tokens.
- **Category 3: Verification Loops (`finish_reason=length` under F)**: The model emitted repetitive re-derivation or sanity-checking steps analyzing the provided prefix until token exhaustion.
- **Category 4: Fallacy Inheritance (`finish_reason=stop` under F)**: The model explicitly adopted an erroneous premise from the provided prefix, propagating that error to the final answer.

*Disclosure*: These qualitative categories were coded via automated trace inspection and single-investigator behavioral audit. Because multi-annotator blind coding was not conducted during the original run, inter-annotator agreement metrics (e.g., Cohen's $\kappa$) are not claimed. The counts are presented as exploratory behavioral diagnostics, not confirmatory parameters.

---

### 2.2. Cell $b$: Condition F Correct, Condition D Incorrect ($b = 11$ Problems)

In all 11 problems, Condition F emitted the correct final boxed answer while Condition D failed.

| Problem ID | Subject | Level | Condition D Failure Mode | D Tokens / Finish | Condition F Success | F Tokens / Finish | Overlap Notes |
| :--- | :--- | :---: | :--- | :---: | :--- | :---: | :--- |
| `math500_138` | Prealgebra | 5 | Derivation Slip | 288 / `stop` | Completed correctly | 319 / `stop` | Arithmetic slip in D |
| `math500_156` | Intermediate Algebra | 5 | Token Truncation | 768 / `length` | Completed correctly | 696 / `stop` | Length-intensive proof |
| `math500_173` | Intermediate Algebra | 5 | Token Truncation | 768 / `length` | Completed correctly | 649 / `stop` | Length-intensive proof |
| `math500_231` | Intermediate Algebra | 5 | Token Truncation | 768 / `length` | Completed correctly | 475 / `stop` | Budget exhaustion in D |
| `math500_296` | Algebra | 5 | Token Truncation | 768 / `length` | Completed correctly | 381 / `stop` | Long polynomial division |
| `math500_303` | Intermediate Algebra | 5 | Derivation Slip | 609 / `stop` | Completed correctly | 340 / `stop` | Factoring slip in D |
| `math500_326` | Intermediate Algebra | 5 | Token Truncation | 768 / `length` | Completed correctly | 632 / `stop` | Complex algebra in D |
| `math500_376` | Precalculus | 5 | Derivation Slip | 722 / `stop` | Completed correctly | 562 / `stop` | Sign error in matrix D |
| `math500_400` | Intermediate Algebra | 5 | Token Truncation | 768 / `length` | Completed correctly | 631 / `stop` | Series expansion in D |
| `math500_435` | Intermediate Algebra | 5 | Token Truncation | 768 / `length` | Completed correctly | 749 / `stop` | Close to ceiling in F |
| `math500_466` | Intermediate Algebra | 5 | Token Truncation | 768 / `length` | Completed correctly | 608 / `stop` | Radical simplification |

**Cell $b$ Breakdown**:
- **Token Budget Truncation in D**: **8 of 11 problems** ($72.7\%$). In these cases, Forced Restart had to regenerate all preliminary lemmas from scratch, running out of tokens before emitting an answer. Condition F completed the derivations within budget, consistent with the hypothesis that retaining verified prefixes provides token headroom.
- **Derivation Errors in D**: **3 of 11 problems** ($27.3\%$). Clean restart made intermediate arithmetic mistakes that the continuation condition avoided.

---

### 2.3. Cell $c$: Condition D Correct, Condition F Incorrect ($c = 12$ Problems)

In all 12 problems, Condition D emitted the correct final boxed answer while Condition F failed.

| Problem ID | Subject | Level | Condition F Failure Mode | F Tokens / Finish | Condition D Success | D Tokens / Finish | Overlap Notes |
| :--- | :--- | :---: | :--- | :---: | :--- | :---: | :--- |
| `math500_139` | Geometry | 5 | Verification Loop / Truncation | 768 / `length` | Completed correctly | 432 / `stop` | F cycled re-verifying |
| `math500_163` | Intermediate Algebra | 5 | Fallacy Inheritance | 532 / `stop` | Completed correctly | 518 / `stop` | Accepted flawed prefix |
| `math500_219` | Precalculus | 5 | Verification Loop / Truncation | 768 / `length` | Completed correctly | 449 / `stop` | F looped on trig check |
| `math500_252` | Intermediate Algebra | 4 | Fallacy Inheritance | 655 / `stop` | Completed correctly | 627 / `stop` | Propagated invalid step |
| `math500_272` | Intermediate Algebra | 5 | Verification Loop / Truncation | 768 / `length` | Completed correctly | 745 / `stop` | F re-derived from scratch |
| `math500_304` | Algebra | 5 | Verification Loop / Truncation | 768 / `length` | Completed correctly | 690 / `stop` | F stalled on quadratic |
| `math500_385` | Intermediate Algebra | 4 | Fallacy Inheritance | 451 / `stop` | Completed correctly | 498 / `stop` | Anchored to flawed root |
| `math500_398` | Geometry | 5 | Fallacy Inheritance | 470 / `stop` | Completed correctly | 484 / `stop` | Used invalid angle value |
| `math500_403` | Intermediate Algebra | 5 | Fallacy Inheritance | 585 / `stop` | Completed correctly | 768 / `length`* | D correct despite len |
| `math500_409` | Geometry | 5 | Verification Loop / Truncation | 768 / `length` | Completed correctly | 715 / `stop` | F timed out on proof |
| `math500_416` | Intermediate Algebra | 5 | Verification Loop / Truncation | 768 / `length` | Completed correctly | 569 / `stop` | F re-verified lemmas |
| `math500_462` | Geometry | 5 | Verification Loop / Truncation | 768 / `length` | Completed correctly | 509 / `stop` | F stalled in circle proof |

*\*Note on `math500_403`: Condition D emitted the correct boxed answer on token 760 just prior to the 768-token ceiling.*

**Cell $c$ Breakdown**:
- **Verification Loops & Truncation under F**: **7 of 12 problems** ($58.3\%$). Condition F engaged in recursive verification, consuming its remaining token budget without reaching a boxed conclusion.
- **Fallacy Inheritance & Prefix Anchoring under F**: **5 of 12 problems** ($41.7\%$). Condition F completed normally, but treated invalid preliminary assertions in the prefix as established truth, generating a flawed final answer. Clean restart (Condition D) was immune to these invalid premises.

---

## 3. Remediation of Mechanistic Overclaims

### 3.1. Purging the "Headroom vs. Inertia" Cancellation Pseudo-Equation
Previous drafts contained the assertion:
$$\text{Net Effect} = \text{Headroom (+8)} - \text{Inertia (-7)} \approx 0$$
This formulation is **statistically and causally invalid**:
1. Cell counts $b=11$ and $c=12$ are sample realizations of a multinomial paired distribution, not additive physical constants.
2. Truncation and verification loops are observational outcomes of the bundled treatment, not orthogonal causal primitives.
3. Summing observational counts across categories that share underlying prompt factors creates an illusion of causal balance.

### 3.2. Correct Scientific Formulation
The manuscript text now reads:
> *"The discordant cases exhibit heterogeneous failure patterns, including truncation-associated restart failures and apparent continuation-specific reasoning loops. These observations motivate mechanistic hypotheses, but the existing bundled intervention does not identify their separate causal effects."*

---

## 4. Preservation of the Factorial Design as Future Work

To formally identify separate mechanisms, future research must implement a $2 \times 2 \times 2$ factorial experiment:
1. **Factor 1: Prefix Validity** (Ground-truth verified prefix vs. Flawed prefix).
2. **Factor 2: Continuation Instruction** (Neutral continuation vs. Explicit audit prompt vs. Independent scratchpad).
3. **Factor 3: Effective Token Budget** (Equalized remaining budget vs. Proportional budget vs. Unconstrained budget).

This design is preserved strictly as a blueprint for future confirmatory science. It has not been executed in the current work, and no claims regarding its results are made.
