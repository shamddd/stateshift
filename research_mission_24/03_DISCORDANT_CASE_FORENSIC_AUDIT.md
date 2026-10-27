# StateShift Research Mission 24 — Forensic Audit of the 23 Discordant Problems

**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Target Publication:** NeurIPS 2027 Main Track (Preprint: arXiv, Secondary: TMLR)  
**Audit Date:** October 27, 2026  
**Auditor:** Independent Scientific Audit Committee  
**Dataset:** `research_mission_23/data/confirmatory_924_generations.jsonl`  

---

## 1. Executive Summary of the Discordant Cohort

In the preregistered confirmatory trial ($N = 231$ held-out MATH-500 problems), exactly **23 problems** ($9.96\%$) exhibited discordant outcomes between Condition F (State-Preserving Recovery) and Condition D (Forced Restart):
- **Cell $b$ ($D = \text{Incorrect}, F = \text{Correct}$):** **11 problems** ($47.8\%$ of discordant pairs)
- **Cell $c$ ($D = \text{Correct}, F = \text{Incorrect}$):** **12 problems** ($52.2\%$ of discordant pairs)

This audit documents each of the 23 discordant problems at the row level, verifying gold answers, model completions, extraction fidelity, and underlying failure modes.

---

## 2. Row-Level Audit: Cell $b$ (Condition D Incorrect, Condition F Correct — $N = 11$)

| Problem ID | Subject | Level | Operator Code | Gold Answer | D Extracted | F Extracted | D Finish | F Finish | Primary Failure Mode for Condition D |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| `math500_138` | Count & Prob | 3 | `OP03` | `\frac{1}{3}` | `\frac{1}{6}` | `\frac{1}{3}` | `stop` | `stop` | Arithmetic / counting error during scratch restart |
| `math500_156` | Precalculus | 5 | `OP10` | `30^\circ` | `None` | `30` | `length` | `stop` | Budget truncation: D ran out of 768 tokens restarting |
| `math500_173` | Algebra | 1 | `OP06` | `4` | `None` | `4` | `length` | `stop` | Budget truncation: D ran out of 768 tokens restarting |
| `math500_231` | Algebra | 3 | `OP08` | `10` | `None` | `10` | `length` | `stop` | Budget truncation: D ran out of 768 tokens restarting |
| `math500_296` | Inter Algebra | 1 | `OP06` | `\text{(B)}` | `None` | `\text{B}` | `length` | `stop` | Budget truncation: D ran out of 768 tokens restarting |
| `math500_303` | Geometry | 3 | `OP03` | `28` | `33.6` | `28` | `stop` | `stop` | Inversion error during fresh scratch derivation |
| `math500_326` | Precalculus | 4 | `OP04` | `\frac{9}{100}` | `None` | `\frac{9}{100}` | `length` | `stop` | Budget truncation: D ran out of 768 tokens restarting |
| `math500_376` | Geometry | 5 | `OP10` | `(8,-2)` | `\left( \frac{22}{3}, -\frac{4}{3} \right)` | `(8, -2)` | `stop` | `stop` | Complex algebraic sign error during scratch restart |
| `math500_400` | Geometry | 2 | `OP02` | `\frac{14}{3}` | `None` | `\frac{14}{3}` | `length` | `stop` | Budget truncation: D ran out of 768 tokens restarting |
| `math500_435` | Algebra | 3 | `OP03` | `(-\infty, 2) \cup (3, \infty)` | `None` | `(-\infty, 2) \cup (3, \infty)` | `length` | `stop` | Budget truncation: D ran out of 768 tokens restarting |
| `math500_466` | Precalculus | 3 | `OP03` | `8 \pi` | `None` | `8\pi` | `length` | `stop` | Budget truncation: D ran out of 768 tokens restarting |

### Mechanistic Pattern in Cell $b$:
In **8 of the 11 Cell $b$ cases** ($72.7\%$), Condition D failed specifically because it exhausted the 768-token budget (`finish_reason = length`) while re-solving the entire problem from scratch. Condition F succeeded because the preserved intermediate reasoning context provided sufficient token headroom to finish within the budget.

---

## 3. Row-Level Audit: Cell $c$ (Condition D Correct, Condition F Incorrect — $N = 12$)

| Problem ID | Subject | Level | Operator Code | Gold Answer | D Extracted | F Extracted | D Finish | F Finish | Primary Failure Mode for Condition F |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| `math500_139` | Inter Algebra | 4 | `OP04` | `1` | `1` | `None` | `stop` | `length` | Deliberation loop: F got stuck analyzing prefix and truncated |
| `math500_163` | Algebra | 2 | `OP07` | `-\frac{35}{9}` | `-\frac{35}{9}` | `-\frac{31}{9}` | `stop` | `stop` | Cognitive inertia: F propagated arithmetic miscalculation |
| `math500_219` | Count & Prob | 3 | `OP08` | `\frac{1}{2}` | `\frac{1}{2}` | `None` | `stop` | `length` | Deliberation loop: F exhausted 768 tokens defending prefix |
| `math500_252` | Algebra | 2 | `OP07` | `81` | `81` | `77` | `stop` | `stop` | Cognitive inertia: F anchored on flawed intermediate step |
| `math500_272` | Number Theory | 1 | `OP06` | `1030` | `1030` | `None` | `stop` | `length` | Deliberation loop: F looped on prefix verification |
| `math500_304` | Inter Algebra | 4 | `OP04` | `9` | `9` | `None` | `stop` | `length` | Deliberation loop: F exhausted budget attempting repair |
| `math500_385` | Prealgebra | 3 | `OP08` | `22` | `22` | `3` | `stop` | `stop` | Anchoring error: F adopted incorrect tool output |
| `math500_398` | Prealgebra | 5 | `OP10` | `\text{Navin}` | `\text{ Navin}` | `\text{Ian}` | `stop` | `stop` | Absorbing state: F confirmed flawed name assignment |
| `math500_403` | Number Theory | 5 | `OP05` | `3` | `3` | `4` | `length` | `stop` | Flawed deduction: F completed deduction using corrupt logic |
| `math500_409` | Inter Algebra | 1 | `OP01` | `2 \sqrt{5}` | `2\sqrt{5}` | `10` | `stop` | `length` | Truncation + False conclusion: F produced flawed boxed |
| `math500_416` | Precalculus | 1 | `OP06` | `\frac{1}{8}` | `\frac{1}{8}` | `None` | `stop` | `length` | Deliberation loop: F exhausted 768 tokens on repair |
| `math500_462` | Number Theory | 4 | `OP09` | `59` | `59` | `None` | `stop` | `length` | Deliberation loop: F exhausted budget trying to salvage state |

### Mechanistic Pattern in Cell $c$:
In **6 of the 12 Cell $c$ cases** ($50.0\%$), Condition F failed by token exhaustion (`finish_reason = length`), as the model spent excessive tokens attempting to reconcile or verify the corrupted prefix. In the remaining **6 cases** ($50.0\%$), Condition F suffered from **cognitive inertia / prefix anchoring**, inheriting or rationalizing the mathematical corruption. Meanwhile, Condition D cleanly solved all 12 problems by restarting from scratch.

---

## 4. Synthesis: The Two Opposing Causal Forces

The audit committee's forensic examination reveals why Condition F and Condition D achieve near-identical overall accuracy ($67.97\%$ vs $68.40\%$):

$$\underbrace{\text{Reasoning Headroom Gain}}_{\text{Cell } b: +8 \text{ problems saved by token economy}} \quad \approx \quad \underbrace{\text{Cognitive Inertia / Deliberation Trap}}_{\text{Cell } c: -6 \text{ truncation loops} + (-6) \text{ anchoring errors} = -12 \text{ lost}}$$

1. **When Continuation Helps (Cell $b$, 11 problems):** On multi-step problems where full scratch derivation exceeds 768 tokens, preserving valid prefix steps provides the critical headroom needed to reach the final answer.
2. **When Restart Helps (Cell $c$, 12 problems):** On problems where corrupted prefixes introduce subtle contradictions, attempting to "recover" or "repair" causes the model to either enter verbose rationalization loops (exhausting tokens) or anchor to the mathematical flaw. A clean restart avoids this cognitive debt.
3. **Net Empirical Result:** The two forces cancel each other almost perfectly ($11 \text{ vs } 12 \implies \hat{\tau} = -0.43\%$).
