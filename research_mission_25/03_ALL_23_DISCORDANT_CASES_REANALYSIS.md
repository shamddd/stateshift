# StateShift Research Mission 25: Forensic Re-analysis of All 23 Discordant Problems

**Author:** Multidisciplinary Independent Scientific Audit Committee  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Audit Target:** Objective, Non-Overclaiming Audit of Discordant Confirmatory Cases  
**Date:** October 27, 2026  
**Status:** Certified & Finalized  

---

## 1. Methodological Principles for Discordant Analysis

In paired binary classification, discordant pairs ($b$ and $c$) represent problems where the two conditions disagree:
- **Cell $b$ ($D=0, F=1$, $N=11$)**: Condition D (forced restart) failed; Condition F (state-preserving continuation) succeeded.
- **Cell $c$ ($D=1, F=0$, $N=12$)**: Condition D (forced restart) succeeded; Condition F (state-preserving continuation) failed.

To maintain strict scientific integrity:
1. **No Causal Mechanism Conflation**: Outcomes are classified by observable generation characteristics (token counts, finish reasons, extraction strings, mathematical errors), NOT by speculative causal entities.
2. **Descriptive Labels**: Categories like "length truncation" or "derivation error" describe observable attributes of the output string, not unmeasured latent cognitive states.
3. **Exploratory Status**: All case annotations are strictly exploratory qualitative observations.

---

## 2. Cell $b$: Condition D Incorrect ($0$), Condition F Correct ($1$) [$N = 11$]

| Problem ID | Subject | Level | Gold Answer | Condition D Output (Extracted, Reason, Tokens) | Condition F Output (Extracted, Reason, Tokens) | Observable Qualitative Pattern |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **`math500_138`** | Counting & Prob | 4 | `\frac{1}{3}` | `\frac{1}{6}` (`stop`, 288 tokens) | `\frac{1}{3}` (`stop`, 319 tokens) | **Derivation Difference**: D completed normally but miscalculated the joint probability of identical bag contents. F completed normally with correct case enumeration. |
| **`math500_156`** | Geometry | 4 | `30^\circ` | `None` (`length`, 768 tokens) | `30` (`stop`, 696 tokens) | **Truncation in D**: D exhausted the 768-token ceiling while computing derivatives of $\tan \angle APB$. F utilized prefix context and solved for $\tan = \sqrt{3}/3$ within 696 tokens. |
| **`math500_173`** | Algebra | 3 | `4` | `None` (`length`, 768 tokens) | `4` (`stop`, 649 tokens) | **Truncation in D**: D exhausted the token ceiling while testing divisibility of geometric series parameters. F evaluated the square condition within 649 tokens. |
| **`math500_231`** | Algebra | 3 | `10` | `None` (`length`, 768 tokens) | `10` (`stop`, 475 tokens) | **Truncation in D**: D exhausted 768 tokens attempting to expand nested equations from scratch. F completed the derivation in 475 tokens. |
| **`math500_296`** | Intermediate Alg | 5 | `\text{(B)}` | `None` (`length`, 768 tokens) | `\text{B}` (`stop`, 381 tokens) | **Truncation in D**: D ran out of tokens during polynomial case analysis. F resolved the functional equation in 381 tokens. |
| **`math500_303`** | Algebra | 3 | `28` | `33.6` (`stop`, 609 tokens) | `28` (`stop`, 340 tokens) | **Derivation Difference**: D completed within 609 tokens but made an arithmetic scaling error. F used prefix equations and solved for $x=28$ in 340 tokens. |
| **`math500_326`** | Precalculus | 3 | `\frac{9}{100}` | `None` (`length`, 768 tokens) | `\frac{9}{100}` (`stop`, 632 tokens) | **Truncation in D**: D exhausted 768 tokens performing vector dot-product expansions from scratch. F completed the geometric expansion in 632 tokens. |
| **`math500_376`** | Geometry | 1 | `(8,-2)` | `(\frac{22}{3}, -\frac{4}{3})` (`stop`, 722 tokens) | `(8, -2)` (`stop`, 562 tokens) | **Derivation Difference**: D completed within 722 tokens but made an algebraic slip in coordinate sectioning. F verified the ratio and output $(8, -2)$ in 562 tokens. |
| **`math500_400`** | Geometry | 3 | `\frac{14}{3}` | `None` (`length`, 768 tokens) | `\frac{14}{3}` (`stop`, 631 tokens) | **Truncation in D**: D exhausted 768 tokens computing tangent radii from scratch. F completed the radius calculation in 631 tokens. |
| **`math500_435`** | Intermediate Alg | 1 | `(-\infty, 2) \cup (3, \infty)` | `None` (`length`, 768 tokens) | `(-\infty, 2) \cup (3, \infty)` (`stop`, 749 tokens) | **Truncation in D**: D exhausted 768 tokens combining domain sign charts. F finalized the interval at token 749. |
| **`math500_466`** | Precalculus | 5 | `8 \pi` | `None` (`length`, 768 tokens) | `8\pi` (`stop`, 608 tokens) | **Truncation in D**: D ran out of tokens while expanding cyclotomic roots of unity. F summed angles to $8\pi$ in 608 tokens. |

### Summary of Cell $b$:
- **Length Truncation in Condition D:** 8 of 11 problems ($72.7\%$) failed in Condition D because the generation reached the 768-token limit without emitting a final answer (`math500_156`, `math500_173`, `math500_231`, `math500_296`, `math500_326`, `math500_400`, `math500_435`, `math500_466`). In all 8 cases, Condition F completed under the ceiling.
- **Arithmetic / Algebraic Slips in Condition D:** 3 of 11 problems ($27.3\%$) completed normally in Condition D but produced an incorrect answer (`math500_138`, `math500_303`, `math500_376`).

---

## 3. Cell $c$: Condition D Correct ($1$), Condition F Incorrect ($0$) [$N = 12$]

| Problem ID | Subject | Level | Gold Answer | Condition D Output (Extracted, Reason, Tokens) | Condition F Output (Extracted, Reason, Tokens) | Observable Qualitative Pattern |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **`math500_139`** | Intermediate Alg | 2 | `1` | `1` (`stop`, 432 tokens) | `None` (`length`, 768 tokens) | **Truncation in F**: D solved cleanly via trigonometric substitution in 432 tokens. F entered algebraic partial-derivative expansions and hit the 768-token ceiling. |
| **`math500_163`** | Intermediate Alg | 4 | `-\frac{35}{9}` | `-\frac{35}{9}` (`stop`, 518 tokens) | `-\frac{31}{9}` (`stop`, 532 tokens) | **Derivation Difference**: D completed in 518 tokens with correct quadratic bound. F completed in 532 tokens but made an algebraic calculation slip ($-\frac{31}{9}$). |
| **`math500_219`** | Precalculus | 4 | `\frac{1}{2}` | `\frac{1}{2}` (`stop`, 449 tokens) | `None` (`length`, 768 tokens) | **Truncation in F**: D solved cleanly via symmetry in 449 tokens. F attempted extensive modular remainder case checking and hit the 768-token ceiling. |
| **`math500_252`** | Prealgebra | 2 | `81` | `81` (`stop`, 627 tokens) | `77` (`stop`, 655 tokens) | **Derivation Difference**: D completed in 627 tokens with exact exponent evaluation. F completed in 655 tokens but made an arithmetic subtraction error ($77$). |
| **`math500_272`** | Prealgebra | 1 | `1030` | `1030` (`stop`, 745 tokens) | `None` (`length`, 768 tokens) | **Truncation in F**: D solved in 745 tokens. F spent tokens re-verifying earlier place-value conversions and hit the 768-token limit without emitting an answer. |
| **`math500_304`** | Intermediate Alg | 4 | `9` | `9` (`stop`, 690 tokens) | `None` (`length`, 768 tokens) | **Truncation in F**: D solved the logarithmic system in 690 tokens. F engaged in repetitive algebraic re-expansion and truncated at token 768. |
| **`math500_385`** | Number Theory | 1 | `22` | `22` (`stop`, 498 tokens) | `3` (`stop`, 451 tokens) | **Derivation Difference / Prefix Anchoring**: D factored cleanly. F followed prefix modular steps to an incorrect terminal residue of 3. |
| **`math500_398`** | Counting & Prob | 5 | `\text{Navin}` | `\text{Navin}` (`stop`, 484 tokens) | `\text{Ian}` (`stop`, 470 tokens) | **Derivation Difference**: D performed logical elimination correctly. F misattributed the winner to Ian within 470 tokens. |
| **`math500_403`** | Number Theory | 4 | `3` | `3` (`length`, 768 tokens) | `4` (`stop`, 585 tokens) | **Repetitive Truncation vs. Counting Slip**: D found digit count 3, then engaged in repetitive looping until token 768. F stopped normally at 585 tokens but miscounted distinct digits as 4. |
| **`math500_409`** | Precalculus | 1 | `2 \sqrt{5}` | `2\sqrt{5}` (`stop`, 715 tokens) | `10` (`length`, 768 tokens) | **Prefixed Hallucination & Truncation**: D solved hyperbolic foci distance cleanly in 715 tokens. F pre-stated a hallucinatory answer (10) at token 1, re-derived the true value ($2\sqrt{5}$) at the end, but truncated before boxing it. |
| **`math500_416`** | Precalculus | 4 | `\frac{1}{8}` | `\frac{1}{8}` (`stop`, 569 tokens) | `None` (`length`, 768 tokens) | **Truncation in F**: D factored $\sin^3 18^\circ + \sin^2 18^\circ$ cleanly in 569 tokens. F expanded multiple trigonometric product-to-sum identities and truncated at token 768. |
| **`math500_462`** | Number Theory | 2 | `59` | `59` (`stop`, 509 tokens) | `None` (`length`, 768 tokens) | **Truncation in F**: D converted coin sums modulo 100 in 509 tokens. F re-summed coin values repeatedly and truncated at token 768. |

### Summary of Cell $c$:
- **Length Truncation in Condition F:** 7 of 12 problems ($58.3\%$) reached the 768-token ceiling in Condition F without emitting a validated answer (`math500_139`, `math500_219`, `math500_272`, `math500_304`, `math500_409`, `math500_416`, `math500_462`).
- **Incorrect Deductions / Arithmetic Errors in Condition F:** 5 of 12 problems ($41.7\%$) completed normally but produced an erroneous answer (`math500_163`, `math500_252`, `math500_385`, `math500_398`, `math500_403`).

---

## 4. Synthesis of Findings

1. **Both Conditions Suffer From Truncation Under Fixed Ceilings**:
   - Condition D truncated on 8 problems where F succeeded.
   - Condition F truncated on 7 problems where D succeeded.
   - Neither condition eliminates truncation; rather, they experience truncation on different subsets of problems.
2. **Rejection of Monolithic Causal Labels**:
   - Labeling Cell $b$ as "Headroom = 11" obscures the fact that 3 cases were simple arithmetic slips in D.
   - Labeling Cell $c$ as "Cognitive Inertia = 12" obscures the fact that 5 cases were standard derivation errors in F and 7 were length truncations resulting from verbosity or re-checking.
3. **Conclusion for Manuscript Reporting**:
   - These 23 cases must be presented as **empirical qualitative case studies**, with explicit disclosure of both truncation and derivation error frequencies.
   - Any mechanistic inference must be clearly designated as an unproven exploratory hypothesis.
