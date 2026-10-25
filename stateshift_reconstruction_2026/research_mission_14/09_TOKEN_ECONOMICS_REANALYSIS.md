# StateShift Research Mission 14 — Deliverable 09: Token Economics Reanalysis

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Investigating Role**: Independent Forensic Recovery Auditor  
**Date**: October 25, 2026  

---

## 1. Audit of Mission 13 Token Economics Claims

Mission 13 claimed:
> *"Preserving valid reasoning prefixes yields an insignificant token saving ($+13.2$ tokens, $p = 0.299$, 95% CI $[-11.4, +37.8]$) because models implicitly restart."*

### Methodological Audit Findings:
1. **Unverifiable Aggregate Sample**: Because the 143-rollout JSONL was not persisted to disk, the aggregate mean of $521.8$ tokens (Condition D) vs. $508.6$ tokens (Condition F) cannot be independently reproduced from physical files.
2. **The Risk of False Equivalence**: Claiming that Condition D and Condition F are "equivalent" in compute cost based solely on a non-significant paired difference ($p = 0.299$) violates fundamental statistical methodology. A non-significant p-value indicates insufficient evidence to reject the null hypothesis of equal means; it does *not* prove that the means are equal.
3. **Physical Observation on `math500_001`**:
   - In the single complete matched pair physically surviving (`math500_001`):
     - Condition D Generated Tokens: **553 tokens** (Prompt tokens: 180, Total: 733).
     - Condition F Generated Tokens: **558 tokens** (Prompt tokens: 178, Total: 736).
     - Observed Delta ($\text{Tokens}_D - \text{Tokens}_F$): **$-5\text{ tokens}$**.
   - Condition F actually generated **5 more tokens** than Condition D.

---

## 2. Theoretical Breakdown: When COULD Local Repair Be Cheaper?

For local state repair to achieve computational savings over restarting, the following mathematical inequality must hold:
$$\text{Tokens}_{\text{repair}} = \text{Tokens}_{\text{loc}} + \text{Tokens}_{\text{corr}} + \text{Tokens}_{\text{cont}} < \text{Tokens}_{\text{restart}} = \sum_{i=1}^M \text{Tokens}(\text{Step}_i)$$

Where:
- $\text{Tokens}_{\text{loc}}$: Tokens required to localize and explain the error.
- $\text{Tokens}_{\text{corr}}$: Tokens required to write the corrected assertion.
- $\text{Tokens}_{\text{cont}}$: Tokens required to complete the remaining $M - k$ steps.

### Why Savings Evaporate in Current Models:
1. When models restart implicitly, $\text{Tokens}_{\text{cont}} \approx \text{Tokens}_{\text{restart}}$.
2. If the model attempts local repair but must emit verbose explanations of the error ($\text{Tokens}_{\text{loc}} > 50\text{ tokens}$), the overhead of explanation exceeds the cost of re-generating early arithmetic steps.
3. Therefore, local repair can only be economically advantageous for **very deep reasoning chains ($M \gg 15\text{ steps}$)** where the error occurs late in the derivation ($k > 10$). On short 3-to-5 step MATH problems, context regeneration is computationally competitive with or cheaper than surgical repair.
