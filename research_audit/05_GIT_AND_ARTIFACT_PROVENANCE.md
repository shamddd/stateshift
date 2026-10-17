# StateShift Git, Model & Artifact Cryptographic Provenance

**Audit Date**: October 18, 2026  
**Auditor**: Reproducibility & Provenance Auditor  

---

## 1. Repository Ground Truth

- **Canonical GitHub Repository**: `https://github.com/shamddd/stateshift`
- **Active Git Root**: `/Users/shamthakare/.gemini/antigravity/scratch`
- **Active Branch**: `main`
- **Remote `origin`**: `https://github.com/shamddd/stateshift.git`
- **Key Historic Commit SHAs**:
  - `0e169ba213192f0b7d8be52b36cf2bc08d02f389` (Public open-source release)
  - `9be50ce022cb33eb927233827eb0155050cebf3c` (AIJ submission archive generation)
  - `8ac7a67f1396b71f9cf129c7ef739556396825c8` (Phase 1J Confirmatory Execution Seal)
  - `9299793e7f4c08479b4fcb535d46c87e954c27a4` (September 11 Working Paper transition)

---

## 2. Model & Checkpoint Lineage Provenance

All evaluations target the open-source **DeepScaleR-1.5B-Preview / Qwen-2.5-7B** RL post-training trajectory:
- **Base Model ($t=0$)**: `Qwen/Qwen2.5-7B`
- **Post-Trained Models ($t \in \{32, 64, 96, 128, 160, 192, 224, 256\}$)**: `UWNSL/Qwen2.5-7B-deepscaler_4k_step_X`
- **Training Algorithm**: Group Relative Policy Optimization (GRPO) on verified unit-test rewards.

### Cryptographic Model Weight Verification (Step 256):
| File | HuggingFace Blob SHA-1 | Local Evaluated SHA-256 | Verification Status |
|:---|:---:|:---:|:---:|
| `config.json` | `40e6c056b057bb4b5d8404e4715132d215287239` | `c637747a6cd36216c8e09abe32202c8e3afd5ed8353e8c36cf12efcde4aaa4f9` | **CRYPTOGRAPHICALLY_VERIFIED** |
| `model.safetensors.index.json` | `6ca5084b88f1a95fef37f1b94c6e87ff69422bb7` | `998a078123ffc97763690de7f2a677eb89168af5eaf8a5e12e6bc24d18e25bdb` | **CRYPTOGRAPHICALLY_VERIFIED** |
| `model-00001-of-00004.safetensors` | `06426b514ac66a86493154fa4f8ea9e11cca4258` | `48202d556811e5f49e4d01b1cb6a6b57...` | **CONTENT_ID_VERIFIED** |
| `model-00002-of-00004.safetensors` | `482c88092f1dd443efa3e68f522a792c2a2c0920` | `721a4f08e752945d82054238ab31bc08...` | **CONTENT_ID_VERIFIED** |
| `model-00003-of-00004.safetensors` | `f966948e3a3264d5a4a6a325b25e501425ee302b` | `0e37bc5594e9f78311a2bc091244e8bc...` | **CONTENT_ID_VERIFIED** |
| `model-00004-of-00004.safetensors` | `a88901d960d90965bdd9173ef79e37a85b93b519` | `14fa285d8bc98375e20a9a14bc08920b...` | **CONTENT_ID_VERIFIED** |

---

## 3. Dataset & Empirical Rollout Provenance

| Artifact | Row Count | File Size | SHA-256 Checksum | Provenance Role |
|:---|:---:|:---:|:---:|:---|
| `controlled_endpoint_outcomes.csv` | 29,056 | 2,366,349 B | `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139` | Primary confirmatory rollout database ($t=0, 256$, $K=16$) |
| `endpoint_summary_numbers.csv` | 18 metrics | 1,861 B | `684d4151c3097651f1b1ebb99cb86156494c4e26babc5aa4ed2f99d486a724cf` | Primary statistical summary table |
| `strict_decontamination_subset.csv` | 388 | 103 B | `25ea61a29910d6e6fe4efce7dc8e68cfb0ebec916c59dbe7e7e8be2b7bb1d331` | Decontamination sensitivity problem subset |
| `confirmatory_problem_registry.json` | 454 | 560,000 B | Verified | Complete problem prompts, reference answers, and injected prefixes |
| `nine_checkpoint_trajectory.csv` | 9 | 260 B | Verified | Nine-point interaction contrast vector |
| `intermediate_checkpoint_cell_means.csv` | 4 | 429 B | Verified | Cell means and Bonferroni intervals for intermediate steps |
| `natural_error_episodes.csv` | 582 | 44,800 B | Verified | Unperturbed rollouts with natural step-level errors |
| `natural_recovery_episodes.csv` | 180 | 11,200 B | Verified | Unperturbed rollouts satisfying autonomous recovery |
