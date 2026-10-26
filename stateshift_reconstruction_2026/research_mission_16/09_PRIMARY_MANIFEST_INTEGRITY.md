# StateShift: Primary Experiment Manifest Integrity & Overlap Audit
## Deliverable 09 — 400-Request Cryptographic Invariant Audit, Balance & Calibration Separation Rules
**Document Version:** 1.0.0  
**Audit Date:** 2026-10-26  
**Principal Investigator:** Sham Satish Thakare  
**Target Venue:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Primary Manifest Path:** [`research_mission_15_6/manifests/primary_100_manifest.json`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_15_6/manifests/primary_100_manifest.json)  
**Expected SHA-256 Hash:** `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`  

---

## 1. Master Integrity Scorecard: 100% PASS

Every request in the frozen 400-request primary experiment manifest was cryptographically audited:

| Integrity Check | Protocol Requirement | Verified Observation | Status |
| :--- | :--- | :--- | :---: |
| **Manifest SHA-256 Hash** | `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` | Bit-exact match (557,212 bytes) | **PASS** |
| **Total Request Cardinality** | Exactly 400 requests | Exactly 400 request objects | **PASS** |
| **Unique Request IDs** | 400 unique IDs (`req_0001` to `req_0400`) | Zero duplicate request IDs | **PASS** |
| **Unique Experimental Units** | Unique `(problem_id, condition_code)` | 400 unique paired tuples | **PASS** |
| **Condition Balance** | 100 per condition (A, D, E, F) | 100 A, 100 D, 100 E, 100 F | **PASS** |
| **Problem Coverage** | 100 distinct competition problems | 100 problems (`001` to `100`) | **PASS** |
| **Prompt Cryptographic Hash** | `prompt_sha256 == sha256(prompt_text)` | 400 / 400 exact matches (0 mismatch)| **PASS** |
| **Model Specification** | `Qwen/Qwen2.5-Math-7B-Instruct` | 400 / 400 bound to Qwen-7B | **PASS** |
| **Decoding Configuration** | Greedy ($\tau=0.0$, max=768, seed=42) | $\tau=0.0$, max=768, seed=42 (400/400)| **PASS** |
| **Gold Answer Integrity** | Ground-truth answers present | 400 / 400 populated with gold LaTeX | **PASS** |

---

## 2. Experimental Condition Distribution & Counterbalancing

```
[400 Total Experimental Requests]
├─ Condition A: Zero-Shot Standard CoT            (100 requests, 25.0%)
├─ Condition D: Naive Forced Restart              (100 requests, 25.0%)
├─ Condition E: Explicit Targeted Repair          (100 requests, 25.0%)
└─ Condition F: State-Preserving Continuation     (100 requests, 25.0%)
```

* **Paired Within-Subject Design:** Every single problem $i \in \{1, \dots, 100\}$ appears exactly once under each of the four conditions, enabling exact paired contrasts with zero across-problem confounding.
* **Prompt Text Length Statistics:**
  - Minimum Prompt Length: 97 characters
  - Maximum Prompt Length: 1,322 characters
  - Mean Prompt Length: 486.6 characters

---

## 3. Calibration Overlap Audit & Scientific Separation Rules

### 3.1 Observed Overlap
A set intersection query between `calibration_10_manifest.json` and `primary_100_manifest.json` revealed:
* **Overlap Cardinality:** Exactly 10 requests.
* **Overlapping Request IDs:** `primary_100_req_0001` through `primary_100_req_0010`.
* **Overlapping Tasks:**
  - `math500_001` (Requests 0001–0004, Conditions A, D, E, F).
  - `math500_012` (Requests 0005–0008, Conditions A, D, E, F).
  - `math500_023` (Requests 0009–0010, Conditions A, D).

### 3.2 Formal Protocol for Dataset Independence
To uphold the highest standards of scientific reproducibility and eliminate post-hoc data contamination:
1. **Rule of Clean Confirmatory Execution (Default):**  
   When the 400-request experiment is authorized, all 400 requests will be executed afresh in a single dedicated GPU session. This ensures absolute temporal, hardware, and runtime homogeneity across all 400 observations.
2. **Strict Prohibition on Silent Merging:**  
   Calibration records from `stateshift_calib_b1_01` **will NOT be silently reused** to substitute for requests 1–10 in the primary dataset.
3. **Archival & Sensitivity Reporting:**  
   The 10 calibration records will remain archived in `data/primary_run/stateshift_calib_b1_01_generations.jsonl`. A sensitivity analysis comparing Request 1–10 fresh generations against calibration generations will be reported in the supplementary materials to verify deterministic run-to-run stability.
