# Phase 2: Dataset Independence and Sample Disjointness Audit

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22.1 — Final Confirmatory Scientific Audit  
**Date & Timestamp**: 2026-10-27T05:36:00+05:30  
**Target Publication Venue**: NeurIPS 2027 Main Track  

---

## 1. Executive Summary & Mandatory Terminology Correction

A critical scientific audit was conducted to scrutinize and correct the dataset independence claims made in preliminary preflight reports.

### 1.1 Mandatory Terminology Corrections
In earlier drafts, colloquial phrases such as *"completely independent benchmark"*, *"pristine unseen problems"*, *"proven contamination-free dataset"*, and *"guaranteed out-of-distribution validation"* were occasionally used. These descriptions are scientifically imprecise and overstate what has been established.

**We formally replace all such phrasing with the exact, scientifically defensible specification**:
> **"A disjoint held-out MATH-500 confirmatory sample ($N = 231$), selected without reference to confirmatory model outcomes."**

### 1.2 Tripartite Epistemic Taxonomy
To adhere to the strictest standards of research integrity, we explicitly distinguish three distinct levels of independence:

1. **Sample Disjointness (ESTABLISHED & VERIFIED)**:
   - The $231$ confirmatory problems share exactly zero problem IDs and zero identical problem texts with the $100$ pilot problems ($|S_{\text{pilot}} \cap S_{\text{confirmatory}}| = 0$).
   - The selection was conducted deterministically with seed `2027` prior to running any confirmatory model inference.
2. **Benchmark Independence (NOT CLAIMED / NOT ESTABLISHED)**:
   - Both the pilot sample ($N = 100$) and the confirmatory sample ($N = 231$) originate from the same underlying distribution: the standardized MATH-500 benchmark.
   - The confirmatory trial evaluates within-benchmark held-out replication, not cross-benchmark transfer to novel tasks (e.g., GSM8K or OlympiadBench).
3. **Pretraining Independence (NOT CLAIMED / UNVERIFIABLE)**:
   - Because MATH-500 is a widely circulated open-source benchmark, it cannot be guaranteed that the pretraining or post-training corpora of `Qwen/Qwen2.5-Math-7B-Instruct` did not contain these problems.
   - The confirmatory trial measures comparative intervention recovery relative to baseline controls under identical pretraining exposure, not zero-shot memorization boundaries.

---

## 2. Ten-Point Forensic Verification of Sample Disjointness

An automated forensic verification script was executed across the pilot outcomes (`data/study2/final_verified_outcomes.csv`) and the confirmatory manifest (`research_mission_22/data/confirmatory_231_manifest.jsonl`):

| Check # | Audit Scope | Empirical Result | Scientific Verdict |
| :--- | :--- | :--- | :---: |
| **Check 1** | **Exact Problem ID Overlap** | $|S_{\text{pilot}} \cap S_{\text{conf}}| = 0$ ($0/100$ shared IDs) | **PASS (Disjoint)** |
| **Check 2** | **Exact Normalized Text Overlap** | $0/23,100$ pairwise collisions ($0.0\%$) | **PASS (Disjoint)** |
| **Check 3** | **Near-Duplicate Statement Scan** | Maximum Jaccard similarity across cross-pairs = $0.7333$ (`math500_051` vs `math500_439`) | **PASS (Distinct Tasks)** |
| **Check 4** | **Altered Constants Scan** | Identified shared template phrasing in standard algebra (e.g., polynomial division), but expressions and mathematical roots are strictly distinct. | **PASS** |
| **Check 5** | **Answer Pattern Diversity** | 153 unique gold answers across 231 confirmatory problems (no degenerate absorbing solutions). | **PASS** |
| **Check 6** | **Duplicate Record Check** | 924 total requests; 924 unique `request_id`s ($100\%$ unique). | **PASS** |
| **Check 7** | **Dataset Revision Consistency** | All records consistently reference MATH-500 source and pinned schema. | **PASS** |
| **Check 8** | **Problem-Answer Integrity** | Exactly $0$ empty or malformed gold answers ($231/231$ valid LaTeX strings). | **PASS** |
| **Check 9** | **Selection Reproducibility** | Deterministic PRNG `random.Random(2027)` reproduces identical 231 problem IDs bitwise. | **PASS** |
| **Check 10** | **Stratification Reproducibility** | Exactly 47 Level 1, 46 Level 2, 46 Level 3, 46 Level 4, 46 Level 5 problems; OP01 has 24, OP02–OP10 have 23 each. | **PASS** |

### Inspection of Highest Similarity Pair:
- **Pilot Problem `math500_051`**:
  `Find the quotient when $x^6 - 3$ is divided by $x + 1.$` $\implies$ Gold: `x^5 - x^4 + x^3 - x^2 + x - 1`
- **Confirmatory Problem `math500_439`**:
  `Find the quotient when $x^9 + 1$ is divided by $x - 1.$` $\implies$ Gold: `x^8 + x^7 + x^6 + x^5 + x^4 + x^3 + x^2 + x + 1`
- **Audit Conclusion**: Both problems share standard English phrasing for algebraic division, but define completely different dividend degrees ($6$ vs $9$), divisors ($x+1$ vs $x-1$), remainders, and quotient polynomials.

---

## 3. Preserved Selection Verdict

The frozen selection of $N = 231$ held-out problems in `research_mission_22/data/confirmatory_231_manifest.jsonl` exhibits zero leakage and 100% sample disjointness from the pilot. The selection is preserved intact without amendment.
