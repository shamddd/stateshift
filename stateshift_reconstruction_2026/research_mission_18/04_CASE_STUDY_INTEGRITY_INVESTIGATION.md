# StateShift: Research Mission 18 — Forensic Case Study Integrity & Contradiction Audit

**Audit Date:** October 26, 2026  
**Auditor Committee:** Independent Scientific Audit Committee (Forensic Integrity & Language Model Reasoning Directorate)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Investigation Target:** The `math500_012` Narrative Discrepancy & Verification of All 10 Discordant Pairs  

---

## 1. Executive Summary: The `math500_012` Investigation

The committee conducted a line-by-line, byte-level investigation into the apparent contradiction between two different descriptions of `math500_012` across earlier project documents:
- **Narrative A (Manuscript Section 4.2, line 240):** Described `math500_012` as *Divisor Counting & Attractor Trapping* on the amicable pair 284/220 (gold answer: `284`), returning `220` under Condition D versus `284` under Condition F.
- **Narrative B (Mission 17 Report `08_CAUSAL_AND_MECHANISTIC_ANALYSIS.md`, line 45):** Described `math500_012` as *Sub-Goal Abandonment: Solve a system of quadratic constraints requiring modular factoring $(x - 14)(y - 14) = 196$*.

### Forensic Findings:
1. **The Physical Ground Truth:**
   In the frozen problem manifest (`primary_100_manifest.json`) and raw dataset (`stateshift_primary_400_generations.jsonl`), `math500_012` is unequivocally:
   - **Subject:** Number Theory (MATH-500)
   - **Prompt:** *"The proper divisors of 12 are 1, 2, 3, 4 and 6. A proper divisor of an integer $N$ is a positive divisor of $N$ that is less than $N$. What is the sum of the proper divisors of the sum of the proper divisors of 284?"*
   - **Gold Answer:** `284`
   - **Condition D Model Output (`primary_100_req_0006`):** The model lists divisors of 284 (sum = 220), but in step 4 circularizes, re-sums the proper divisors of 284, and outputs `\boxed{220}` (**INCORRECT**).
   - **Condition F Model Output (`primary_100_req_0008`):** The model preserves the pre-verified cut-point (sum = 220), correctly enumerates the 11 proper divisors of 220 (1, 2, 4, 5, 10, 11, 20, 22, 44, 55, 110), sums them to 284, and outputs `\boxed{284}` (**CORRECT**).
2. **Origin of Narrative B:**
   The phrase *"system of quadratic constraints $(x-14)(y-14)=196$"* in Mission 17's markdown report was an accidental narrative confabulation by the qualitative report author, who conflated a classic Simon's Favorite Factoring Trick problem with `math500_012`.
3. **Data Integrity Impact: ZERO.**
   The underlying neural generations in `stateshift_primary_400_generations.jsonl` are 100% authentic, unmodified, and strictly correspond to the amicable divisor problem. The numerical results (`220` vs `284`) and evaluation outcomes (D=False, F=True) were entirely real; only the qualitative commentary in the informal markdown report was misattributed.

---

## 2. Complete Forensic Audit of All 10 Discordant Problems

The 10 discordant problems between Condition F (State-Preserving) and Condition D (Forced Restart) determine the entire primary effect size $\hat{\tau}_{F-D} = \frac{8 - 2}{100} = +6.00\%$. The committee verified the actual prompt, gold answer, and model output for each:

### Group A: Condition F Wins ($b = 8$)

1. **`math500_012` (Number Theory, Level 1)**
   - *Prompt:* Sum of proper divisors of the sum of proper divisors of 284.
   - *Gold:* `284`
   - *Condition D (`req_0006`):* Evaluates to `\boxed{220}` (Failed; fell into circular attractor).
   - *Condition F (`req_0008`):* Evaluates to `\boxed{284}` (Correct; successfully summed divisors of 220).
2. **`math500_026` (Counting & Probability, Level 4)**
   - *Prompt:* Round-table seating of 7 people where Pierre, Rosa, and Thomas cannot sit next to each other.
   - *Gold:* `144`
   - *Condition D (`req_0130`):* Truncated at 768 tokens while re-deriving circular permutations from scratch (Failed).
   - *Condition F (`req_0132`):* Resumed from the complement count, calculated $720 - 576 = 144$, output `\boxed{144}` (Correct).
3. **`math500_068` (Precalculus, Level 1)**
   - *Prompt:* Solve $\tan 53^\circ \tan 81^\circ \tan x^\circ = \tan 53^\circ + \tan 81^\circ + \tan x^\circ$ for $0 < x < 180$.
   - *Gold:* `46`
   - *Condition D (`req_0026`):* Miscalculated angle sum identity $180 - 53 - 81 = 46$ as $45$, output `\boxed{45}` (Failed).
   - *Condition F (`req_0028`):* Maintained established tangent identity, correctly evaluated $180 - 134 = 46$, output `\boxed{46}` (Correct).
4. **`math500_071` (Number Theory, Level 4)**
   - *Prompt:* Convert binary $10101001110_2$ to base 8.
   - *Gold:* `2516_8`
   - *Condition D (`req_0146`):* Grouped bits from left to right instead of right to left, output `\boxed{5236}` (Failed).
   - *Condition F (`req_0148`):* Preserved the 3-bit partition from the right ($010, 101, 001, 110 \rightarrow 2, 5, 1, 6$), output `\boxed{2516_8}` (Correct).
5. **`math500_078` (Intermediate Algebra, Level 1)**
   - *Prompt:* For $f(x) = x^3 + 3x^2 + 1$, find $(a,b)$ such that $f(x) - f(a) = (x-a)^2(x-b)$.
   - *Gold:* `(-2, 1)`
   - *Condition D (`req_0030`):* Re-expanded with algebraic sign error, output `\boxed{\left(-\frac{6}{5}, \frac{1}{2}\right)}` (Failed).
   - *Condition F (`req_0032`):* Preserved coefficient comparison $2a + b = -3$ and $a^2 + 2ab = 0$, correctly solved $a = -2, b = 1$, output `\boxed{(-2, 1)}` (Correct).
6. **`math500_092` (Counting & Probability, Level 1)**
   - *Prompt:* Pirate searches 7 islands, each with $1/5$ treasure probability. Find probability exactly 4 have treasure.
   - *Gold:* `\frac{448}{15625}`
   - *Condition D (`req_0034`):* Re-derived Bernoulli formula, ran out of tokens during arithmetic, truncated (Failed).
   - *Condition F (`req_0036`):* Resumed from binomial coefficient $\binom{7}{4} = 35$, calculated $35 \times 4^3 / 5^7 = 2240 / 78125$, output `\boxed{\frac{2240}{78125}}` (Correct, equivalent to $\frac{448}{15625}$).
7. **`math500_093` (Algebra, Level 2)**
   - *Prompt:* Find $c$ such that $x^2 - 10x + y^2 + 6y + c = 0$ has radius 1.
   - *Gold:* `33`
   - *Condition D (`req_0074`):* Re-wrote full square completion from scratch, truncated at 768 tokens (Failed).
   - *Condition F (`req_0076`):* Resumed with completed squares $(x-5)^2 + (y+3)^2 = 34 - c$, solved $34 - c = 1 \rightarrow c = 33$, output `\boxed{33}` (Correct).
8. **`math500_112` (Algebra, Level 5)**
   - *Prompt:* Simplify $\frac{1+\sqrt{2}}{2+\sqrt{3}}$ into $A(1+\sqrt{B}) - (\sqrt{C}+\sqrt{D})$, find $A+B+C+D$.
   - *Gold:* `13`
   - *Condition D (`req_0398`):* Conjugate multiplication error during reboot, output `\boxed{6}` (Failed).
   - *Condition F (`req_0400`):* Preserved rationalized denominator $(2+\sqrt{3})(2-\sqrt{3}) = 1$, correctly matched $A=2, B=2, C=3, D=6 \rightarrow 2+2+3+6 = 13$, output `\boxed{13}` (Correct).

---

### Group B: Condition D Wins ($c = 2$)

1. **`math500_014` (Precalculus, Level 3)**
   - *Prompt:* Right triangle with $\sin D = 0.7$, hypotenuse 10, find adjacent side $DE$.
   - *Gold:* `\sqrt{51}`
   - *Condition D (`req_0086`):* Solved cleanly via Pythagorean theorem $100 - 49 = 51 \rightarrow \sqrt{51}$, output `\boxed{\sqrt{51}}` (Correct).
   - *Condition F (`req_0088`):* Explored redundant trigonometric angle-addition identities, ran out of tokens, truncated (Failed).
2. **`math500_052` (Prealgebra, Level 2)**
   - *Prompt:* Simplify $\frac{\sqrt{2.5^2 - 0.7^2}}{2.7 - 2.5}$.
   - *Gold:* `12`
   - *Condition D (`req_0258`):* Evaluated numerator $\sqrt{6.25 - 0.49} = \sqrt{5.76} = 2.4$, denominator $0.2$, $2.4 / 0.2 = 12$, output `\boxed{12}` (Correct).
   - *Condition F (`req_0260`):* Attempted fractional expansion with large intermediate denominators, truncated at 768 tokens (Failed).

---

## 3. Causal Mechanics Revealed by the Audit

The audit of the 10 discordant pairs reveals three clear causal mechanisms:
1. **Token Budget Amortization (3 cases: `026`, `092`, `093`):**
   In multi-step problems, forcing a complete restart forces the model to expend hundreds of tokens re-deriving already solved lemmas, causing it to hit the 768-token ceiling before reaching the answer. State preservation saves these tokens, allowing completion.
2. **Attractor Trapping & Circular Loops (3 cases: `012`, `068`, `071`):**
   Under greedy decoding ($T=0$), restarting from the prompt often causes the model to fall back into the exact same deterministic basin of attraction (e.g., re-summing 284 in `012` or grouping bits incorrectly in `071`). State preservation breaks this basin by initializing inference from a novel context state.
3. **Algebraic Re-Derivation Errors (2 cases: `078`, `112`):**
   Re-executing complex algebraic manipulations introduces fresh opportunities for sign and arithmetic errors.
4. **State-Preserving Over-Complexity (The 2 Condition D Wins: `014`, `052`):**
   Occasionally, preserving a lengthy prompt prefix biases the model toward continuing an unnecessarily complex derivation branch rather than seeing a direct, simple shortcut (as Condition D did on reboot).

---

## 4. Manuscript Correction Action Plan

1. In `STATESHIFT_REVISED_SUBMISSION.tex`:
   - Replace any lingering informal reference to "Simon's Favorite Factoring" or "quadratic factorizations" in connection with `math500_012`.
   - Maintain the precise description of `math500_012` as the amicable divisor sum attractor trap on 284/220.
   - Fully cite all 8 recovery cases and both 2 failure cases with transparent token and mechanistic accounting.
