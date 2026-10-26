# StateShift: Research Mission 19.1 — Final Qualitative Evidence & Case Study Audit

**Date:** October 26, 2026  
**Auditor:** Qualitative Evaluation & Model Behavior Directorate  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Data Source:** `data/primary_run/stateshift_primary_400_generations.jsonl` (SHA-256: `bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2`)  

---

## 1. Definitive Verification of `math500_012`

Problem `math500_012` was re-audited byte-for-byte against the physical GPU dataset:

- **Problem ID:** `math500_012` (MATH-500 Number Theory, Level 1)
- **Prompt:**
  > *"The proper divisors of 12 are 1, 2, 3, 4 and 6. A proper divisor of an integer $N$ is a positive divisor of $N$ that is less than $N$. What is the sum of the proper divisors of the sum of the proper divisors of 284?"*
- **Gold Answer:** `284`
- **Condition D (`primary_100_req_0006`, 768 tokens, finish: `stop`):**
  - *Model Output Summary:* Computes proper divisors of 284: $1, 2, 4, 71, 142$ (sum $= 220$). In step 4, the model loops back and re-sums the proper divisors of 284 rather than summing the proper divisors of 220:
    > `"...lated their sum in step 2: \[ 1 + 2 + 4 + 71 + 142 = 220 \] Thus, the sum of the proper divisors of the sum of the proper divisors of 284 is: \[ \boxed{220} \]"`
  - *Evaluation:* **INCORRECT** (`220` $\neq$ `284`).
- **Condition F (`primary_100_req_0008`, 452 tokens, finish: `stop`):**
  - *Model Output Summary:* Inherits the verified premise that the sum of the proper divisors of 284 is $220$. It directly computes the 11 proper divisors of 220 ($1, 2, 4, 5, 10, 11, 20, 22, 44, 55, 110$) and sums them to 284:
    > `"...1 + 2 + 4 + 5 + 10 + 11 + 20 + 22 + 44 + 55 + 110 = 284 \] Therefore, the sum of the proper divisors of the sum of the proper divisors of 284 is \(\boxed{284}\)."`
  - *Evaluation:* **CORRECT** (`284` = `284`).
- **Narrative Rectification Status:**
  The errant informal mention of quadratic factorizations $(x-14)(y-14)=196$ from earlier working notes is **completely absent**. The physical data unequivocally represents the amicable divisor sum on 284/220.

---

## 2. Forensic Audit of All Ten Discordant Problems

The 10 discordant pairs between Condition F and Condition D directly determine $\hat{\tau}_{F-D} = +6.00\%$:

### Group A: Condition F Successes / Condition D Failures ($b = 8$)

1. **`math500_012` (Number Theory, Level 1):**
   - *Gold:* `284`
   - *Condition D (`req_0006`):* Evaluates to `\boxed{220}` (Circular attractor failure).
   - *Condition F (`req_0008`):* Evaluates to `\boxed{284}` (Correct).
2. **`math500_026` (Counting & Probability, Level 4):**
   - *Prompt:* Round-table seating of 7 people where Pierre, Rosa, and Thomas cannot sit next to each other.
   - *Gold:* `144`
   - *Condition D (`req_0130`):* Expands circular permutations, reaches `720 - 576 = 144`, but truncates at token 768 before boxing (Token budget exhaustion).
   - *Condition F (`req_0132`):* Resumes from complement count, outputs `\boxed{144}` in 388 tokens (Correct).
3. **`math500_068` (Precalculus, Level 1):**
   - *Prompt:* Solve $\tan 53^\circ \tan 81^\circ \tan x^\circ = \tan 53^\circ + \tan 81^\circ + \tan x^\circ$.
   - *Gold:* `46`
   - *Condition D (`req_0026`):* Hallucinates $x = 45^\circ$, outputs `\boxed{45}` (Failed).
   - *Condition F (`req_0028`):* Preserves angle addition identity $180 - 134 = 46$, outputs `\boxed{46}` (Correct).
4. **`math500_071` (Number Theory, Level 4):**
   - *Prompt:* Convert binary $10101001110_2$ to base 8.
   - *Gold:* `2516_8`
   - *Condition D (`req_0146`):* Groups bits from left to right, outputs `\boxed{5236}` (Greedy directional error).
   - *Condition F (`req_0148`):* Preserves 3-bit clustering from the right ($010, 101, 001, 110_2$), outputs `\boxed{2516_8}` (Correct).
5. **`math500_078` (Intermediate Algebra, Level 1):**
   - *Prompt:* For $f(x) = x^3 + 3x^2 + 1$, find $(a,b)$ such that $f(x) - f(a) = (x-a)^2(x-b)$.
   - *Gold:* `(-2, 1)`
   - *Condition D (`req_0030`):* Polynomial sign error during restart, outputs `\boxed{\left(-\frac{6}{5}, \frac{1}{2}\right)}` (Failed).
   - *Condition F (`req_0032`):* Preserves $2a + b = -3$ and $a^2 + 2ab = 0$, outputs `\boxed{(-2, 1)}` (Correct).
6. **`math500_092` (Counting & Probability, Level 1):**
   - *Prompt:* Pirate searches 7 islands ($1/5$ probability each); probability exactly 4 contain treasure.
   - *Gold:* `\frac{448}{15625}`
   - *Condition D (`req_0034`):* Expands $35 \times 64 = 2240$ and $5^7 = 78125$, truncates at token 768 during simplification (Token budget exhaustion).
   - *Condition F (`req_0036`):* Directly boxes `\boxed{\frac{2240}{78125}}` in 276 tokens (Correct).
7. **`math500_093` (Algebra, Level 2):**
   - *Prompt:* Find $c$ such that $x^2 - 10x + y^2 + 6y + c = 0$ has radius 1.
   - *Gold:* `33`
   - *Condition D (`req_0074`):* Completes squares, calculates $c=33$, truncates at token 768 right before boxing (Token budget exhaustion).
   - *Condition F (`req_0076`):* Completes terminal isolation, outputs `\boxed{33}` in 245 tokens (Correct).
8. **`math500_112` (Algebra, Level 5):**
   - *Prompt:* Rationalize $\frac{1+\sqrt{2}}{2+\sqrt{3}} = A(1+\sqrt{B}) - (\sqrt{C}+\sqrt{D})$; find $A+B+C+D$.
   - *Gold:* `13`
   - *Condition D (`req_0398`):* Conjugate parameter mismatch, sets $D=0$, outputs `\boxed{6}` (Failed).
   - *Condition F (`req_0400`):* Correctly matches $A=2, B=2, C=3, D=6$, outputs `\boxed{13}` (Correct).

---

### Group B: Condition D Successes / Condition F Failures ($c = 2$)

1. **`math500_014` (Precalculus, Level 3):**
   - *Prompt:* Right triangle with $\sin D = 0.7$, hypotenuse 10, find adjacent side $DE$.
   - *Gold:* `\sqrt{51}`
   - *Condition D (`req_0086`):* Directly uses Pythagorean theorem $100 - 49 = 51 \rightarrow \sqrt{51}$, outputs `\boxed{\sqrt{51}}` (Correct).
   - *Condition F (`req_0088`):* Inherits a lengthy prefix exploring tangent identities, enters an infinite repetitive loop (`} } } } ...`), truncating at 768 tokens (Failed).
2. **`math500_052` (Prealgebra, Level 2):**
   - *Prompt:* Simplify $\frac{\sqrt{2.5^2 - 0.7^2}}{2.7 - 2.5}$.
   - *Gold:* `12`
   - *Condition D (`req_0258`):* Computes $\sqrt{5.76}/0.2 = 2.4/0.2 = 12$, outputs `\boxed{12}` (Correct).
   - *Condition F (`req_0260`):* Gets trapped in an algebraic difference-of-squares expansion loop, truncating at token 768 (Failed).

---

## 3. Qualitative Audit Conclusion

All 10 case studies are 100% faithful to the authentic raw tokens. The mechanisms of token budget amortization, attractor avoidance, and prefix repetition bias are fully verified.
