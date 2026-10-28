# Research Mission 23 — Phase 5: Final Frozen Confirmatory Manifest

## 1. Manifest Cryptographic Identification
The confirmatory evaluation manifest for the StateShift Option B experiment is permanently frozen on disk:

- **Manifest File (JSONL)**: `research_mission_22/data/confirmatory_231_manifest.jsonl`
- **File Size**: 1,246,234 bytes
- **SHA-256 Checksum**: `2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5`
- **Formatted JSON**: `research_mission_22/data/confirmatory_231_manifest.json` (SHA-256: `3b0114558cdd36d409f2351388ec8fb36724cdf7ac0916e2c3c36420bff55f42`)
- **Total Requests**: Exactly 924 inference requests.
- **Unique Problems**: Exactly 231 held-out MATH-500 problems.
- **Conditions per Problem**: Exactly 4 requests per problem (Conditions A, D, E, F).

---

## 2. Sample Independence & Decontamination Verification

1. **Zero Pilot Overlap ($\emptyset$)**:
   - $\mathcal{P}_{\text{pilot}}$ ($N = 100$ problems from Study 2).
   - $\mathcal{P}_{\text{confirmatory}}$ ($N = 231$ problems from Option B).
   - Set-theoretic intersection:
     $$\mathcal{P}_{\text{pilot}} \cap \mathcal{P}_{\text{confirmatory}} = \emptyset$$
2. **Candidate Problem Pool Selection**:
   - The candidate pool comprises 354 held-out MATH-500 problems after excluding the 100 pilot problems and 46 structural test instances.
   - The 231 problems were selected via stratified random sampling under fixed seed `42`.
3. **No Prior Outcome Inspection**:
   - Zero confirmatory model outputs have been generated, inspected, or scored. The evaluation is strictly prospective.

---

## 3. Stratified Quota Fulfillment

The frozen sample matches the exact proportional distribution of the MATH-500 benchmark:

### Subject Representation
- Algebra: 46 problems (19.9%)
- Precalculus: 34 problems (14.7%)
- Geometry: 33 problems (14.3%)
- Intermediate Algebra: 32 problems (13.9%)
- Number Theory: 30 problems (13.0%)
- Counting & Probability: 29 problems (12.6%)
- Prealgebra: 27 problems (11.7%)
- **Total**: 231 problems (100.0%)

### Difficulty Level Representation
- Level 1: 34 problems (14.7%)
- Level 2: 43 problems (18.6%)
- Level 3: 56 problems (24.2%)
- Level 4: 51 problems (22.1%)
- Level 5: 47 problems (20.3%)
- **Total**: 231 problems (100.0%)

---

## 4. Manifest Record Specification

Every request record in `confirmatory_231_manifest.jsonl` contains the following frozen fields:
- `request_id`: Deterministic unique identifier (`conf_231_req_0001` through `conf_231_req_0924`).
- `problem_id`: MATH-500 identifier (`math500_002`, etc.).
- `condition_code`: `Condition_A_Zero_Shot`, `Condition_D_Forced_Restart`, `Condition_E_Explicit_Repair`, or `Condition_F_State_Preserving`.
- `prompt_text`: Full constructed prompt text.
- `prompt_sha256`: Cryptographic hash of the exact prompt text.
- `gold_answer`: Ground truth mathematical answer string.
- `subject`: Mathematical domain category.
- `difficulty_level`: Benchmark difficulty rating (1 to 5).
- `corruption_metadata`: Step index, corrupted reasoning statement, and error operator type.

The manifest is cryptographically sealed and cannot be modified.
