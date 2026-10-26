# 10 Four-Condition Integrity Audit: Experimental Design & Pilot Manifest

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Investigation**: Research Mission 12 — Phase X Experimental Design Audit  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Pilot Manifest**: [`manifests/runpod_b1_pilot_manifest.json`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/manifests/runpod_b1_pilot_manifest.json)  
**Cohort**: 10 Problems $\times$ 4 Matched Conditions = **40 Intended Inference Requests**  
**Target Model**: `Qwen/Qwen2.5-Math-7B-Instruct` (Revision: `main`)  
**Status**: COMPLETE — 100% CANONICAL SHA-256 MANIFEST GENERATED  

---

## 1. Experimental Design & Causal Controls

To isolate whether frontier 7B models possess emergent reasoning recovery capabilities, the study adopts a strictly controlled **4-condition within-subject factorial design**:

```
                              [Problem Statement]
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
   [Zero-Shot Clean]                                   [Corrupted Derivation Prefix]
   (Condition A)                                       (10 Operators: OP01 - OP10)
   Baseline ceiling                                               │
                                       ┌──────────────────────────┼──────────────────────────┐
                                       ▼                          ▼                          ▼
                               [Forced Restart]          [Explicit Repair]         [State Preservation]
                               (Condition D)             (Condition E)             (Condition F)
                               Clean scratchpad          Targeted alert            Strict prefix hold
```

### 1.1 Condition Specifications

| Condition Code | Internal Name | Prefix Context | Invariance & Control Function |
| :--- | :--- | :--- | :--- |
| **`Condition_A_Zero_Shot`** | `neutral` | None | Baseline mathematical competence on unperturbed problems. |
| **`Condition_D_Forced_Restart`** | `explicit_restart` | Corrupted (Recovery) | Instructs the model to discard the corrupted prefix and restart. |
| **`Condition_E_Explicit_Repair`** | `explicit_local_repair` | Corrupted (Recovery) | Explicitly informs the model of the error and instructs surgical repair. |
| **`Condition_F_State_Preserving`** | `state_preserving_repair` | Corrupted (Recovery) | Forcibly mandates preserving valid prefix steps while correcting the flaw. |

---

## 2. Manifest Request Distribution

| Experimental Condition | Target Engine Name | Prefix Type | Allocated Requests |
| :--- | :--- | :--- | :---: |
| `Condition_A_Zero_Shot` | `neutral` | `none` | 10 |
| `Condition_D_Forced_Restart` | `explicit_restart` | `recovery` | 10 |
| `Condition_E_Explicit_Repair` | `explicit_local_repair` | `recovery` | 10 |
| `Condition_F_State_Preserving` | `state_preserving_repair` | `recovery` | 10 |
| **Total** | — | — | **40** |

---

## 3. Representative Manifest Requests (First 12 of 40)

| Request ID | Problem ID | Operator Code | Experimental Condition | Prompt SHA-256 |
| :--- | :--- | :--- | :--- | :--- |
| `b1_req_001` | `math500_113` | `OP01_ARITHMETIC_MISCALCULATION` | `Condition_A_Zero_Shot` | `62c4a68225...` |
| `b1_req_002` | `math500_113` | `OP01_ARITHMETIC_MISCALCULATION` | `Condition_D_Forced_Restart` | `c6941f7ef1...` |
| `b1_req_003` | `math500_113` | `OP01_ARITHMETIC_MISCALCULATION` | `Condition_E_Explicit_Repair` | `497a749854...` |
| `b1_req_004` | `math500_113` | `OP01_ARITHMETIC_MISCALCULATION` | `Condition_F_State_Preserving` | `632ef2a4af...` |
| `b1_req_005` | `math500_114` | `OP02_SIGN_FLIP` | `Condition_A_Zero_Shot` | `5c6d818190...` |
| `b1_req_006` | `math500_114` | `OP02_SIGN_FLIP` | `Condition_D_Forced_Restart` | `79de2e3852...` |
| `b1_req_007` | `math500_114` | `OP02_SIGN_FLIP` | `Condition_E_Explicit_Repair` | `fc6acedd52...` |
| `b1_req_008` | `math500_114` | `OP02_SIGN_FLIP` | `Condition_F_State_Preserving` | `3f3f05950e...` |
| `b1_req_009` | `math500_116` | `OP03_FRACTION_INVERSION` | `Condition_A_Zero_Shot` | `76f98e0944...` |
| `b1_req_010` | `math500_116` | `OP03_FRACTION_INVERSION` | `Condition_D_Forced_Restart` | `2cc271025d...` |
| `b1_req_011` | `math500_116` | `OP03_FRACTION_INVERSION` | `Condition_E_Explicit_Repair` | `38090f5d4a...` |
| `b1_req_012` | `math500_116` | `OP03_FRACTION_INVERSION` | `Condition_F_State_Preserving` | `c8b5ebbd0c...` |

---

## 4. Methodological Safeguards

1. **Exact Operator Balancing**:
   The 10 selected problems exactly span the 10 canonical StateShift error operators:
   - `OP01_ARITHMETIC_MISCALCULATION`
   - `OP02_SIGN_FLIP`
   - `OP03_FRACTION_INVERSION`
   - `OP04_INVALID_ASSUMPTION`
   - `OP05_INVALID_LOGICAL_DEDUCTION`
   - `OP06_MULTISTEP_DECOMPOSITION_ERROR`
   - `OP07_MISAPPLIED_IDENTITY`
   - `OP08_INCORRECT_TOOL_OUTPUT`
   - `OP09_PLAUSIBLE_FALSE_CONCLUSION`
   - `OP10_CONTRADICTORY_ABSORBING_STATE`
2. **Direct Cross-Scale Pairability**:
   These exact 10 problems were evaluated in Phase VI on `Qwen2.5-Math-1.5B-Instruct-4bit` on Apple Silicon M1 (`data/local_adversarial_generations.jsonl`). Executing these on `Qwen2.5-Math-7B-Instruct` on RunPod creates a **perfect 1:1 cross-scale comparative cohort**, isolating model scale while holding problem difficulty and error perturbation identical.
3. **Deterministic Generation Settings**:
   All requests enforce `temperature = 0.0`, `seed = 42`, and `max_tokens = 768`.

---

*This concludes Phase X of Research Mission 12. The full manifest is frozen in `manifests/runpod_b1_pilot_manifest.json`.*
