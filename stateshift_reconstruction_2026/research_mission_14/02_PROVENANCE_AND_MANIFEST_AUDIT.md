# StateShift Research Mission 14 — Deliverable 02: Provenance and Manifest Audit

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Investigating Role**: Independent Forensic Recovery Auditor  
**Manifest Reference**: `manifests/primary_100_manifest.json` (SHA-256: `9fa3f44358ceeaee55ee0ee10787e9cf2911b3338876c12ad1849a37ad33b7a`)  
**Audit Ledger**: `research_mission_14/data/provenance_audit_ledger.json`  

---

## 1. Machine-Readable Provenance Ledger

All 6 recovered records were cross-checked against the frozen primary manifest `primary_100_manifest.json`.

| Request ID | Problem ID | Subject | Operator Code | Condition Code | Manifest Match | Gold Answer Match | Prompt SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `primary_100_req_0001` | `math500_001` | Intermediate Algebra | `OP01` | `Condition_A_Zero_Shot` | **VERIFIED** | `p - q` (MATCH) | `f0049e0b963e147ea41829037c862b509ef8cce8cbb3fb986bbf69ae40d7088b` |
| `primary_100_req_0002` | `math500_001` | Intermediate Algebra | `OP01` | `Condition_D_Forced_Restart` | **VERIFIED** | `p - q` (MATCH) | `e1f9a2bcae9fa7ff23086ebc03e6284fbe3d96fe846bf4fc3ea119857d4bdf73` |
| `primary_100_req_0003` | `math500_001` | Intermediate Algebra | `OP01` | `Condition_E_Explicit_Repair` | **VERIFIED** | `p - q` (MATCH) | `ec62e1281df6f1c42f0227189178ee9cf6cbeebc3c38661ec4d8f070cbdf44ae` |
| `primary_100_req_0004` | `math500_001` | Intermediate Algebra | `OP01` | `Condition_F_State_Preserving` | **VERIFIED** | `p - q` (MATCH) | `8f53a492576924b175ffdfb6920f6be83111b1fc897d1303e9112bc5c6d37df9` |
| `primary_100_req_0131` | `math500_026` | Counting & Probability | `OP04` | `Condition_E_Explicit_Repair` | **VERIFIED** | `144` (MATCH) | `a83e0e7a2b9ef1873105ea2ff03ee11333c5b59ea24d27572797ce32f8a5a415` |
| `primary_100_req_0143` | `math500_061` | Intermediate Algebra | `OP04` | `Condition_E_Explicit_Repair` | **VERIFIED** | `-256` (MATCH) | `61f18fb5f0967d718b53e839e55728a4ad662be0cf2e269c7ae8837e408ec200` |

---

## 2. Matched Block Completeness Separation

A fundamental requirement of paired statistical experimental design is distinguishing complete matched blocks from incomplete, partial observations:

### 2.1 Complete Four-Condition Matched Block
- **Problem `math500_001`**:
  - Conditions Observed: **A, D, E, F (All 4 present)**.
  - Status: **COMPLETE MATCHED BLOCK**.
  - Permitted Statistical Use: Valid for within-problem paired contrast ($\text{Acc}_F - \text{Acc}_D$, $\text{Tokens}_D - \text{Tokens}_F$).

### 2.2 Incomplete Partial Blocks
- **Problem `math500_026`**:
  - Conditions Observed: **Condition E only** (`primary_100_req_0131`).
  - Conditions Missing: A, D, F.
  - Status: **INCOMPLETE BLOCK**.
  - Restriction: Valid only as an independent single-trace observational point for Condition E; **strictly excluded from paired D-vs-F contrasts**.
- **Problem `math500_061`**:
  - Conditions Observed: **Condition E only** (`primary_100_req_0143`).
  - Conditions Missing: A, D, F.
  - Status: **INCOMPLETE BLOCK**.
  - Restriction: Valid only as an independent single-trace observational point for Condition E; **strictly excluded from paired D-vs-F contrasts**.

---

## 3. Provenance Conclusion

1. The 6 recovered records match the frozen manifest with 100% cryptographic precision.
2. Only 1 problem (`math500_001`) satisfies complete matched-block requirements across all 4 conditions.
3. The remaining two observations represent isolated Condition E traces. Any paired inference claiming $N > 1$ matched problem pairs cannot be reproduced from local evidence.
