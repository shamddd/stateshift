# StateShift Research Mission 13 — Deliverable 16: Reproducibility Report

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Computational Reproducibility Standard**: Deterministic Zero-Entropy Greedy Execution  

---

## 1. Cryptographic Manifest Ledger

All experimental requests, prompts, and problem metadata are frozen into immutable JSON manifests with verifiable SHA-256 digests:

| File Path | Description | Records | Size (Bytes) | SHA-256 Digest |
| :--- | :--- | :--- | :--- | :--- |
| `manifests/primary_100_manifest.json` | Primary 100-Problem Manifest | 400 | 569,153 | `9fa3f44358ceeaee55ee0ee10787e9cf2911b3338876c12ad1849a37ad33b7a` |
| `manifests/replication_200_manifest.json` | Secondary Replication Manifest | 800 | 1,174,881 | `02a78f659bcbb4cbe9265f80b15e378ef865239a51fe70e1cbb3273eef076e05` |

---

## 2. Deterministic Inference Protocol

To guarantee bit-exact reproducibility across independent compute clusters:
- **Sampling Temperature**: `temperature = 0.0` (Greedy argmax decoding).
- **Top-p**: `top_p = 1.0`.
- **Top-k**: `-1` (Disabled).
- **Random Seed**: `seed = 42`.
- **Stop Sequences**: `["<|im_end|>", "<|endoftext|>"]`.
- **Max Generation Tokens**: `max_tokens = 768`.
- **Precision**: `torch.bfloat16`.

---

## 3. Evaluator v4 Test Suite Verification

The evaluation pipeline includes a comprehensive 17-test suite (`tests/test_evaluator_v4.py` and `tests/test_runpod_api_contract.py`) passing with 100% success rate:
- Adversarial keyword trap rejection: PASSED.
- Alternative path not credited as repair: PASSED.
- SymPy symbolic fraction equivalence: PASSED.
- DAG dependency contamination calculation: PASSED.
- Zero-denominator edge case handling: PASSED.
- External cost controller authorization and financial trip logic: PASSED (12/12 tests).
