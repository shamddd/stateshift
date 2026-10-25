# StateShift Mission 15.2: Scientific Protocol and Experimental Manifest Freeze

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_2/09_SCIENTIFIC_PROTOCOL_FREEZE.md`  

---

## 1. Executive Summary

To ensure scientific reproducibility and eliminate post-hoc experiment alteration, the experimental protocol, problem suite, intervention definitions, and generation parameters are permanently frozen prior to cloud GPU execution.

---

## 2. Experimental Manifest Cryptographic Freeze

| Manifest Attribute | Value / Specification |
|:---|:---|
| **Manifest Path** | `research_mission_15_2/manifests/primary_100_manifest.json` |
| **Manifest SHA-256** | `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` |
| **Total Experimental Problems** | 100 benchmark mathematical reasoning problems (GSM8K & MATH) |
| **Total Experimental Rollouts** | **400 distinct inference requests** |
| **Gold Answer Source** | Verified ground-truth symbolic and numerical solutions |

### Condition Stratification (4 $\times$ 100 Factorial Design)
1. **`Condition_A_Zero_Shot` ($N=100$)**:
   - Baseline standard zero-shot chain-of-thought generation.
   - Evaluates pure pre-trained / instruction-tuned reasoning accuracy without perturbation.
2. **`Condition_D_Forced_Restart` ($N=100$)**:
   - Truncation perturbation where reasoning is interrupted at step $k$, and the model is forced to restart solving from scratch without state memory.
   - Evaluates baseline recovery under catastrophic context loss.
3. **`Condition_E_Explicit_Repair` ($N=100$)**:
   - Truncation perturbation followed by an explicit diagnostic critique or repair prompt identifying the error location.
   - Evaluates external feedback sensitivity.
4. **`Condition_F_State_Preserving` ($N=100$)**:
   - Truncation perturbation where the valid prefix state is preserved with explicit state-checkpoint restoration.
   - Evaluates hypothesis $H_1$: State-preserving post-training enables monotonic reasoning trajectory recovery.

---

## 3. Frozen Model and Decoding Hyperparameters

| Hyperparameter | Value | Scientific Rationale |
|:---|:---:|:---|
| **Target Model** | `Qwen/Qwen2.5-Math-7B-Instruct` | State-of-the-art open-weights 7B mathematical reasoning model |
| **Model Weights SHA / Tag** | Upstream official release (`c869d27376a8d6728795551322fe323b6`) | Guarantees identical weight initialization |
| **Tokenizer Revision** | Matching model weights commit | Prevents tokenization drift |
| **Temperature** | `0.0` | Strictly deterministic greedy decoding for exact reproducibility |
| **Max Generation Tokens** | `768` | Accommodates complete step-by-step mathematical reasoning proofs |
| **Random Seed** | `42` | Deterministic initialization across random operations |
| **Sampling Mode** | `greedy` | Prevents stochastic sampling variance across runs |
| **Stop Sequences** | Standard EOS tokens (`<|im_end|>`, `<|endoftext|>`) | Clean termination at answer conclusion |

---

## 4. Verification Protocol

The orchestrator and dataset verifier (`IndependentDatasetVerifierV2`) enforce that:
1. Every received record matches an entry in `primary_100_manifest.json` by `request_id`, `problem_id`, `condition_code`, and `prompt_sha256`.
2. The `manifest_hash` recorded in each generation's provenance matches `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`.
3. Any discrepancy in model identity, decoding configuration, or condition codes triggers an immediate rejection.
