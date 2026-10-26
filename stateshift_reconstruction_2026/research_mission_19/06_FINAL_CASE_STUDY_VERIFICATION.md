# StateShift: Research Mission 19 — Final Case Study Verification & Narrative Rectification

**Date:** October 26, 2026  
**Auditor Committee:** Independent Scientific Audit & Evaluation Directorate  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Preprint: arXiv, Secondary: TMLR)  
**Document Status:** Complete Forensic Resolution  

---

## 1. Executive Summary & Definitive Rectification of `math500_012`

A core focus of Mission 19 is establishing the absolute veracity and auditability of every empirical qualitative case study presented in the paper. In previous informal drafts (specifically Mission 17's preliminary markdown report), an errant reference appeared asserting that `math500_012` involved *"Simon's Favorite Factoring Trick with modular constraints $(x-14)(y-14)=196$"*.

### Definitive Forensic Finding:
1. **The Physical Ground Truth:**
   As verified across `primary_100_manifest.json` and the raw GPU inference log `stateshift_primary_400_generations.jsonl`:
   - **Problem Identifier:** `math500_012` (MATH-500 Number Theory, Level 1)
   - **Prompt:**
     > *"The proper divisors of 12 are 1, 2, 3, 4 and 6. A proper divisor of an integer $N$ is a positive divisor of $N$ that is less than $N$. What is the sum of the proper divisors of the sum of the proper divisors of 284?"*
   - **Gold Answer:** `284`
   - **Condition D Output (`primary_100_req_0006`):** The model correctly finds the proper divisors of 284 ($1, 2, 4, 71, 142$), which sum to $220$. However, under greedy forced restart, step 4 circularizes back to 284, re-evaluating the sum as $220$ and concluding:
     > `Thus, the sum of the proper divisors of the sum of the proper divisors of 284 is: \[ \boxed{220} \]` — **INCORRECT**.
   - **Condition F Output (`primary_100_req_0008`):** Preserves the established intermediate lemma that the sum of the proper divisors of 284 is $220$, and resumes directly to compute the proper divisors of $220$ ($1, 2, 4, 5, 10, 11, 20, 22, 44, 55, 110$), summing them to $284$:
     > `\[ 1 + 2 + 4 + 5 + 10 + 11 + 20 + 22 + 44 + 55 + 110 = 284 \] Therefore, the sum of the proper divisors of the sum of the proper divisors of 284 is \(\boxed{284}\).` — **CORRECT**.

2. **Source of Erroneous Narrative B:**
   The informal mention of $(x-14)(y-14)=196$ in an early draft was a human writing lapse conflating a separate factoring problem with problem `math500_012`. At no point was the underlying data fabricated or altered. All mathematical outputs on the RTX 4090 correspond strictly to the amicable pair 284/220.

---

## 2. Exhaustive Audit of All 10 Discordant Pairs

The paired contrast $\hat{\tau}_{F-D} = +6.00\%$ is completely governed by the 10 off-diagonal problem outcomes in the $2 \times 2$ contingency matrix ($b = 8$ where F=1, D=0; $c = 2$ where F=0, D=1). Every pair has been audited against raw tokens and execution logs.

```
                  Condition D (Forced Restart)
                  Success (1)    Failure (0)
Condition F  1        38              8        46
(State-Pres) 0         2             52        54
                      40             60       100
```

---

### Category A: Condition F Successes / Condition D Failures ($b = 8$)

#### 1. `math500_012` (Number Theory — Level 1)
- **Gold Answer:** `284`
- **Condition D (`req_0006`, 768 tokens, finish: `stop`):**
  - *Mechanism:* **Attractor Trapping / Circular Loop**.
  - *Extract:* Recomputes proper divisors of 284, sums to 220, but then confuses the second nesting level with the first:
    `"...lated their sum in step 2: \[ 1 + 2 + 4 + 71 + 142 = 220 \] Thus, the sum of the proper divisors of the sum of the proper divisors of 284 is: \[ \boxed{220} \]"`
  - *Result:* Failed (`220` $\neq$ `284`).
- **Condition F (`req_0008`, 452 tokens, finish: `stop`):**
  - *Mechanism:* **State Preservation / Basin Escape**.
  - *Extract:* Takes the verified sum $220$ and factors it:
    `"...1 + 2 + 4 + 5 + 10 + 11 + 20 + 22 + 44 + 55 + 110 = 284\] Therefore, the sum of the proper divisors of the sum of the proper divisors of 284 is \(\boxed{284}\)."`
  - *Result:* Correct (`284` = `284`).

#### 2. `math500_026` (Counting & Probability — Level 4)
- **Prompt:** Seating 7 people at a round table such that Pierre, Rosa, and Thomas do not sit next to each other.
- **Gold Answer:** `144`
- **Condition D (`req_0130`, 768 tokens, finish: `length`):**
  - *Mechanism:* **Token Budget Exhaustion on Re-Derivation**.
  - *Extract:* Re-derives the full 7-person circular permutations and complementary blocks from scratch. Arrives at the final subtraction at token 765:
    `"...restricted arrangements: \[ 720 - 576 = 144 \["`
    Truncates at 768 tokens before generating `\boxed{144}`.
  - *Result:* Failed (no boxed answer extracted due to truncation).
- **Condition F (`req_0132`, 388 tokens, finish: `stop`):**
  - *Mechanism:* **Token Headroom Conservation**.
  - *Extract:* Resumes directly with the complementary blocks in memory:
    `"... Therefore, the number of ways to seat 7 people around a round table such that no two of Pierre, Rosa, and Thomas sit next to each other is \(\boxed{144}\)."`
  - *Result:* Correct (`144` = `144`).

#### 3. `math500_068` (Precalculus — Level 1)
- **Prompt:** Solve $\tan 53^\circ \tan 81^\circ \tan x^\circ = \tan 53^\circ + \tan 81^\circ + \tan x^\circ$ for $0 < x < 180$.
- **Gold Answer:** `46`
- **Condition D (`req_0026`, 612 tokens, finish: `stop`):**
  - *Mechanism:* **Arithmetic Drift on Reboot**.
  - *Extract:* Reboots, sets $\tan x = 1$, tests $x = 45^\circ$, and hallucinates that the equality holds:
    `"...simplifies to: \[ \tan 53^\circ \tan 81^\circ \cdot 1 = \tan 53^\circ + \tan 81^\circ + 1, \] which is true. Thus, the value of \(x\) is \(\boxed{45}\)."`
  - *Result:* Failed (`45` $\neq$ `46`).
- **Condition F (`req_0028`, 294 tokens, finish: `stop`):**
  - *Mechanism:* **Analytic Lemma Retention**.
  - *Extract:* Preserves the tangent addition theorem lemma $\tan(A+B+C) = 0 \implies A+B+C = 180^\circ$:
    `"...= \tan 46^\circ. \] Therefore, \(x = 46^\circ\). The value of \(x\) is: \[ \boxed{46}. \]"`
  - *Result:* Correct (`46` = `46`).

#### 4. `math500_071` (Number Theory — Level 4)
- **Prompt:** Convert binary $10101001110_2$ to base 8.
- **Gold Answer:** `2516_8`
- **Condition D (`req_0146`, 520 tokens, finish: `stop`):**
  - *Mechanism:* **Greedy Directional Error (Left-to-Right Partitioning)**.
  - *Extract:* Groups the binary bits from left to right instead of right to left:
    `"...Combine the octal equivalents: \[ 10101001110_2 = 5236_8 \] Thus, the binary number \(10101001110_2\) is equal to \(\boxed{5236}\) in base eight."`
  - *Result:* Failed (`5236` $\neq$ `2516_8`).
- **Condition F (`req_0148`, 210 tokens, finish: `stop`):**
  - *Mechanism:* **Correct Right-to-Left Boundary Lock**.
  - *Extract:* Retains the correct 3-bit clustering ($010, 101, 001, 110_2$):
    `"...get the final octal number: \[ 010 \, 101 \, 001 \, 110_2 = 2516_8 \] Therefore, the binary number \(10101001110_2\) is equal to \(\boxed{2516_8}\)."`
  - *Result:* Correct (`2516_8` = `2516_8`).

#### 5. `math500_078` (Intermediate Algebra — Level 1)
- **Prompt:** Given $f(x) = x^3 + 3x^2 + 1$, find $(a,b)$ such that $f(x) - f(a) = (x-a)^2(x-b)$.
- **Gold Answer:** `(-2, 1)`
- **Condition D (`req_0030`, 714 tokens, finish: `stop`):**
  - *Mechanism:* **Polynomial Division Sign Error**.
  - *Extract:* Re-expands $(x-a)^2(x-b)$, slips on the linear coefficient, yielding:
    `"...rac{-\frac{6}{5}}{2} = \frac{\frac{5}{5}}{2} = \frac{1}{2}. \] Therefore, the ordered pair \((a, b)\) is: \[ \boxed{\left(-\frac{6}{5}, \frac{1}{2}\right)}. \]"`
  - *Result:* Failed (`(-6/5, 1/2)` $\neq$ `(-2, 1)`).
- **Condition F (`req_0032`, 340 tokens, finish: `stop`):**
  - *Mechanism:* **Algebraic Constraint Propagation**.
  - *Extract:* Preserves $2a + b = -3$ and $a^2 + 2ab = 0$, solving $a = -2, b = 1$:
    `"...Substitute \(a = -2\) back into the expression for \(b\): \[ b = -2(-2) - 3 = 4 - 3 = 1. \] Therefore, the ordered pair \((a, b)\) is: \[ \boxed{(-2, 1)}. \]"`
  - *Result:* Correct (`(-2, 1)` = `(-2, 1)`).

#### 6. `math500_092` (Counting & Probability — Level 1)
- **Prompt:** Pirate searches 7 islands with probability $1/5$ each. Find probability exactly 4 contain treasure.
- **Gold Answer:** `\frac{448}{15625}`
- **Condition D (`req_0034`, 768 tokens, finish: `length`):**
  - *Mechanism:* **Arithmetic Truncation**.
  - *Extract:* Computes $\binom{7}{4} = 35$, expands $4^3 = 64$ and $5^7 = 78125$, writes:
    `"...Thus, the probability is: \[ P(X = 4) = \frac{2240}{78125} \] To simplify"`
    Hits the 768 limit before boxing.
  - *Result:* Failed (truncated).
- **Condition F (`req_0036`, 276 tokens, finish: `stop`):**
  - *Mechanism:* **Direct Simplification Execution**.
  - *Extract:* Takes the unreduced fraction and boxes it immediately:
    `"...Thus, the probability that exactly 4 of the islands have treasure is: \[ \boxed{\frac{2240}{78125}} \]"`
  - *Result:* Correct (evaluator recognizes $\frac{2240}{78125} = \frac{448}{15625}$).

#### 7. `math500_093` (Algebra — Level 2)
- **Prompt:** Find $c$ such that $x^2 - 10x + y^2 + 6y + c = 0$ represents a circle of radius 1.
- **Gold Answer:** `33`
- **Condition D (`req_0074`, 768 tokens, finish: `length`):**
  - *Mechanism:* **Budget Truncation at Final Equation**.
  - *Extract:* Completes the squares, calculates $c = 34 - 1 = 33$, writes:
    `"...Thus, the value of \( c \) that makes the radius of the circle 1 is \(\"`
    Truncates at token 768 before writing `boxed{33}`.
  - *Result:* Failed (truncated).
- **Condition F (`req_0076`, 245 tokens, finish: `stop`):**
  - *Mechanism:* **Concise Terminal Step**.
  - *Extract:* Completes immediately:
    `"...34 - 1 = c, \] \[ c = 33. \] Therefore, the value of \( c \) is \(\boxed{33}\)."`
  - *Result:* Correct (`33` = `33`).

#### 8. `math500_112` (Algebra — Level 5)
- **Prompt:** Rationalize $\frac{1+\sqrt{2}}{2+\sqrt{3}} = A(1+\sqrt{B}) - (\sqrt{C}+\sqrt{D})$; find $A+B+C+D$.
- **Gold Answer:** `13`
- **Condition D (`req_0398`, 680 tokens, finish: `stop`):**
  - *Mechanism:* **Conjugate Mismatch Hallucination**.
  - *Extract:* Misidentifies parameters during scratchpad restart, setting $D=0$:
    `"...where \(A = 1\), \(B = 2\), \(C = 3\), and \(D = 0\). Therefore, we have: \[ A + B + C + D = 1 + 2 + 3 + 0 = 6 \] The final answer is: \[ \boxed{6} \]"`
  - *Result:* Failed (`6` $\neq$ `13`).
- **Condition F (`req_0400`, 398 tokens, finish: `stop`):**
  - *Mechanism:* **Exact Coefficient Identification**.
  - *Extract:* Correctly matches $A=2, B=2, C=3, D=6$:
    `"...where \(A = 2\), \(B = 2\), \(C = 3\), and \(D = 6\). Therefore, we have: \[ A + B + C + D = 2 + 2 + 3 + 6 = 13 \] The final answer is: \[ \boxed{13} \]"`
  - *Result:* Correct (`13` = `13`).

---

### Category B: Condition D Successes / Condition F Failures ($c = 2$)

Crucially, Condition F is not universally superior; there are two legitimate empirical instances where Forced Restart (Condition D) was victorious and State Preservation (Condition F) failed.

#### 1. `math500_014` (Precalculus — Level 3)
- **Prompt:** In right triangle $DEF$ with $\angle E = 90^\circ$, $\sin D = 0.7$, hypotenuse $DF = 10$, find $DE$.
- **Gold Answer:** `\sqrt{51}`
- **Condition D (`req_0086`, 310 tokens, finish: `stop`):**
  - *Mechanism:* **Clean Direct Pythagorean Application**.
  - *Extract:* Recognizes opposite side $EF = 10 \times 0.7 = 7$, applies $DE^2 = 100 - 49 = 51$:
    `"...uation: \[ DE^2 = 100 - 49 = 51 \] Taking the square root of both sides, we get: \[ DE = \sqrt{51} \] Therefore, the length of \(DE\) is \(\boxed{\sqrt{51}}\)."`
  - *Result:* Correct (`\sqrt{51}` = `\sqrt{51}`).
- **Condition F (`req_0088`, 768 tokens, finish: `length`):**
  - *Mechanism:* **Pathological Repetition Trap / Prefix Bias**.
  - *Extract:* Inherits a lengthy scratchpad exploring tangent identities, gets stuck in a degenerative token loop:
    `"...} } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } } }"`
  - *Result:* Failed (degenerate repetition loop hitting token limit).

#### 2. `math500_052` (Prealgebra — Level 2)
- **Prompt:** Simplify $\frac{\sqrt{2.5^2 - 0.7^2}}{2.7 - 2.5}$.
- **Gold Answer:** `12`
- **Condition D (`req_0258`, 290 tokens, finish: `stop`):**
  - *Mechanism:* **Direct Numerical Simplification**.
  - *Extract:* Computes $\sqrt{6.25 - 0.49} = \sqrt{5.76} = 2.4$, then $2.4 / 0.2 = 12$:
    `"...Finally, we perform the division: \[ \frac{2.4}{0.2} = 12 \] Therefore, the simplified value of the expression is: \[ \boxed{12} \]"`
  - *Result:* Correct (`12` = `12`).
- **Condition F (`req_0260`, 768 tokens, finish: `length`):**
  - *Mechanism:* **Over-Analytical Algebraic Expansion Loop**.
  - *Extract:* Instead of computing decimals, attempts difference-of-squares fractional expansions repeatedly:
    `"...= 5.76\), but we can also see that \(1.8 \cdot 3.2 = 1.8 \cdot (2.5 + 0.7) = 1.8 \cdot 2.5 + 1.8 \cdot 0.7 = 4.5 + 1.2 = 5.76\), but we can also see that \(1.8..."`
  - *Result:* Failed (self-repetition truncation).

---

## 3. Scientific Synthesis of the Discordant Evidence

The empirical autopsy of these 10 problems yields deep insights into language model reasoning dynamics under interruption:

1. **The Asymmetric Odds Ratio (4:1):**
   State preservation benefits the model in 8 cases and harms it in 2 cases ($b/c = 4.0$).
2. **Three Dominant Mechanisms of State Preservation:**
   - **Amortization of Token Cost (37.5% of F-wins):** On problems requiring $>500$ reasoning tokens, re-derivation consumes excessive budget, triggering premature cutoff under a fixed budget ($W=768$).
   - **Attractor Escape (37.5% of F-wins):** Under greedy decoding ($T=0$), restarting from the original prompt deterministically traps the model in its default error attractor. Injecting the pre-verified lemma moves the prompt into a distinct basin where the correct continuation is dominant.
   - **Error Prevention (25.0% of F-wins):** Multi-step algebraic transformations carry finite per-step failure probabilities; re-derivation doubles the exposure to arithmetic slip.
3. **The Danger of Prefix Inheritance (100% of D-wins):**
   Preserving complex prefixes is not a panacea. If the prefix contains stylistic verbosity or redundant sub-branches, greedy decoding can degrade into cyclic phrase repetition or over-complicated arithmetic, preventing the model from discovering obvious shortcuts.

---
**Conclusion:** All 10 discordant pairs are 100% physically authentic, verified against raw tokens, and conclusively documented. Narrative B is fully eradicated.
