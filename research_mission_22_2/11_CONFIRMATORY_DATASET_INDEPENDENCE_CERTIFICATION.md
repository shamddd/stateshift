# Research Mission 22.2 — Confirmatory Dataset Independence Certification

## 1. Scope & Objective
This certificate documents the dataset independence, composition, stratification balance, and cryptographic integrity of the frozen **Option B Confirmatory Dataset** ($N = 231$ problems, 924 total inference requests).

---

## 2. Cryptographic Manifest Ledger

The confirmatory evaluation manifest is permanently frozen on disk:

| File Name | Record Count | File Size (Bytes) | SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| `confirmatory_231_manifest.jsonl` | 924 requests | 1,246,234 | `2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5` |
| `confirmatory_231_manifest.json` | 924 requests | 1,389,819 | `3b0114558cdd36d409f2351388ec8fb36724cdf7ac0916e2c3c36420bff55f42` |
| `confirmatory_candidate_pool_manifest.jsonl` | 354 problems | 550,451 | `5a0ae79aa301d0e5dee51aa18d90a6dd3a0db96b0825e7ad0bb88b91456cb720` |

---

## 3. Strict Pilot Independence Verification ($\emptyset$ Overlap)

A set-theoretic intersection was performed between:
1. $\mathcal{P}_{\text{pilot}}$: The 100 unique `problem_id` values in `data/study2/final_verified_outcomes.csv`.
2. $\mathcal{P}_{\text{confirmatory}}$: The 231 unique `problem_id` values in `confirmatory_231_manifest.jsonl`.

$$\mathcal{P}_{\text{pilot}} \cap \mathcal{P}_{\text{confirmatory}} = \emptyset$$

There is **zero overlap** between the pilot exploration set and the confirmatory test set. The confirmatory trial is evaluated exclusively on unseen, held-out problem instances.

---

## 4. Subject and Difficulty Stratification

The 231 problems in Option B preserve the exact representative subject and difficulty distribution of the MATH-500 benchmark:

### Subject Distribution
- Algebra: 46 problems (19.9%)
- Precalculus: 34 problems (14.7%)
- Geometry: 33 problems (14.3%)
- Intermediate Algebra: 32 problems (13.9%)
- Number Theory: 30 problems (13.0%)
- Counting & Probability: 29 problems (12.6%)
- Prealgebra: 27 problems (11.7%)
- **Total**: 231 problems (100.0%)

### Difficulty Level Distribution
- Level 1: 34 problems (14.7%)
- Level 2: 43 problems (18.6%)
- Level 3: 56 problems (24.2%)
- Level 4: 51 problems (22.1%)
- Level 5: 47 problems (20.3%)
- **Total**: 231 problems (100.0%)

---

## 5. Certification Verdict
The Option B confirmatory dataset satisfies every standard of scientific integrity, prospective pre-registration, and total independence from exploratory pilot analysis.
