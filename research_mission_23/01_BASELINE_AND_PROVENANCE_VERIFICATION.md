# Research Mission 23 — Phase 1: Repository and Scientific Baseline Verification

## 1. Executive Summary & Audit Context
This audit establishes the pre-execution scientific, cryptographic, and repository baseline for **Research Mission 23: Final Scientific Remediation, Adversarial Engineering Audit, Controlled GPU Execution, and Definitive Confirmatory Statistical Analysis** for Project StateShift (*NeurIPS 2027 Main Track*).

- **Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
- **Git Repository Root**: `/Users/shamthakare/.gemini/antigravity/scratch/`
- **Starting Commit**: `ba2defd` (Verified from `research/stateshift-mission22-2-definitive-statistical-reconciliation`)
- **Active Working Branch**: `research/stateshift-mission23-controlled-confirmatory-execution`
- **Execution Mode**: **Stage I: Local CPU-Only Remediation and Audit ($0.00 Cloud Spend)**
- **Fail-Closed Hardware Lock**: `.cloud_execution_locked` **ACTIVE**.
- **Stage II GPU Authorization**: **PROHIBITED AT THIS STAGE** (Awaiting separate explicit Principal Investigator authorization).

---

## 2. Cryptographic Inventory of Baseline Assets

Every primary file, dataset, manifest, and script was hashed and verified directly on disk:

| File Description | Path | Size (Bytes) | SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| **Fail-Closed Cloud Lock** | `.cloud_execution_locked` | 640 | `11d51c86fd59639dd756f26487ce51a7051dfc3ea7b3372f88325ce2fe7bf11b` |
| **Original Pilot Outcomes** | `data/study2/final_verified_outcomes.csv` | 7,998 | `19a328a95dd25ec326fe824361386cc0ddf731f2bf1c392253be0aa19c2385ba` |
| **Authentic Pilot Generations** | `data/study2/stateshift_primary_400_generations.jsonl` | 898,204 | `bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2` |
| **Frozen Confirmatory Manifest** | `research_mission_22/data/confirmatory_231_manifest.jsonl` | 1,246,234 | `2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5` |
| **Candidate Problem Pool** | `research_mission_22/data/confirmatory_candidate_pool_manifest.jsonl` | 550,451 | `5a0ae79aa301d0e5dee51aa18d90a6dd3a0db96b0825e7ad0bb88b91456cb720` |
| **Confirmatory Runner Engine** | `research_mission_22/scripts/run_confirmatory_trial.py` | 16,846 | `05bca4587db8c8cb836a9926d1beee7bcf6891eb6a7c64c1cf6c2dd1bfaf713e` |
| **Exact Power Engine** | `research_mission_22/scripts/confirmatory_exact_power.py` | 7,372 | `f382a8843c08f400fb864b6ae20894fe8e3bf5d4822002362ef76e3d23192534` |
| **Power Sensitivity Artifact** | `research_mission_22/figures/confirmatory_power_sensitivity.pdf` | 37,324 | `3ba196a4fb6c12c75a40bb9bc6e1937eef5f874ab2e4bdae3ff7117326df0f8c` |

---

## 3. Independent Recomputation of Pilot Baseline Outcomes

The original pilot experimental outcomes were recomputed directly from the raw records without relying on pre-existing assertions:

- **Total Problem Count**: Exactly 100 unique MATH-500 problems.
- **Total Experimental Arms**: 4 conditions (`Condition_A_Zero_Shot`, `Condition_D_Forced_Restart`, `Condition_E_Explicit_Repair`, `Condition_F_State_Preserving`).
- **Total Physical GPU Forward Passes**: Exactly 400 genuine neural inference records (`REAL_MODEL_INFERENCE` with pinned model revision `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`).

### Canonical Contingency Table (Path A: Strict Evaluation)
Recomputed directly from `data/study2/final_verified_outcomes.csv`:
```
                       Condition F Correct    Condition F Incorrect    Total
Condition D Correct         a = 65                  c = 2               67
Condition D Incorrect       b = 8                   d = 25              33
Total                       73                      27                 100
```
- Condition D Accuracy: $67.00\%$
- Condition F Accuracy: $73.00\%$
- Paired Treatment Effect: $\hat{\tau}_{F-D} = \frac{b - c}{N} = \frac{8 - 2}{100} = \mathbf{+0.0600} \quad (\mathbf{+6.00\text{ pp}})$
- Total Discordant Pairs: $n_d = b + c = 10$ ($b=8, c=2$)
- Exact Two-Sided McNemar p-value:
  $$p_{\text{exact}} = 2 \times \sum_{k=8}^{10} \binom{10}{k} (0.5)^{10} = \mathbf{0.109375}$$

### Sensitivity Contingency Table (Path B: Unit-Flexible Normalization)
Recomputed with degree-symbol stripping:
```
                       Condition F Correct    Condition F Incorrect    Total
Condition D Correct         a = 66                  c = 2               68
Condition D Incorrect       b = 8                   d = 24              32
Total                       74                      26                 100
```
- Condition D Accuracy: $68.00\%$
- Condition F Accuracy: $74.00\%$
- Paired Treatment Effect: $\hat{\tau}_{F-D} = \mathbf{+0.0600} \quad (\mathbf{+6.00\text{ pp}})$
- Total Discordant Pairs: $b=8, c=2, n_d = 10$ (**Strictly Invariant**)
- Exact Two-Sided McNemar p-value: $p_{\text{exact}} = \mathbf{0.109375}$ (**Strictly Invariant**)

---

## 4. Verification Verdict
All pilot baseline metrics, file checksums, and cryptographic identifiers are 100% verified against raw on-disk artifacts. The working tree is clean on the new research branch `research/stateshift-mission23-controlled-confirmatory-execution`.
