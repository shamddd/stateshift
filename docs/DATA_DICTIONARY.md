# DATA DICTIONARY & FIELD SPECIFICATION

**Project**: StateShift

---

## 1. Primary Rollout JSONL Fields (`04_RAW_RESULTS.jsonl`)

* `rollout_id` (string): Unique identifier for each rollout episode (e.g., `rollout_step32_p001_Recovery_k1`).
* `checkpoint_step` (int): RL training step $t \in \{0, 32, 64, 96, 128, 160, 192, 224, 256\}$.
* `problem_id` (string): Mathematical problem identifier (e.g., `prob_001`).
* `condition` (string): Evaluation state condition (`Recovery` or `Control`).
* `k_index` (int): Rollout repetition index $k \in \{1..K\}$.
* `target_transition_success` (int): Binary indicator ($1$ for success, $0$ for failure).
* `model_repo` (string): Hugging Face repository ID (`UWNSL/Qwen2.5-7B-deepscaler_4k_step_X`).

---

## 2. Trajectory Contrast CSV Fields (`07_FULL_NINE_POINT_TRAJECTORY.csv`)

* `checkpoint` (int): Checkpoint step $t$.
* `gamma_t` (float): State-by-checkpoint interaction contrast $\Gamma_t$.
* `source` (string): Empirical study phase (`Primary Frozen`, `Phase 2B.1 Frozen`, `Phase 2B.4 New`).

*Signed by Data Curator & Reproducibility Auditor*
