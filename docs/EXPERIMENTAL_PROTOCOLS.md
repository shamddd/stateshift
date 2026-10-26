# Project StateShift: Experimental Protocols & Execution Runbooks

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training

---

## 1. Study 1: Checkpoint-Lineage Protocol

* **Benchmark**: 454 mathematical problem pairs drawn from AIME, Olympiad, and MATH-500.
* **Checkpoint Selection**:
  * Step 0: Base initialization prior to RL reasoning alignment.
  * Step 256: Post-trained checkpoint following reinforcement learning with rule-based reward verifiers.
* **Sampling Protocol**:
  * Temperature: 0.7
  * Top-p: 0.95
  * Rollouts per cell: $K = 32$
  * Conditions: `control` (unassisted reasoning rollout) vs. `recovery` (prompt-seeded intermediate lemma trajectory).
* **Evaluation Objective**: Measure target transition success (correct final answer) and generated token counts to determine whether RL amplifies recovery capability independent of verbosity.

---

## 2. Study 2: Physical GPU Reasoning-Recovery Protocol

* **Benchmark**: MATH-500 ($N = 100$ problems).
* **Hardware Environment**:
  * Provider: RunPod Secure Cloud.
  * GPU: Single NVIDIA RTX 4090 ($24\text{ GB}$ GDDR6X VRAM).
  * Host: Linux 6.8 / CUDA 12.4.
* **Model Configuration**:
  * Hugging Face Model: `Qwen/Qwen2.5-Math-7B-Instruct`
  * Pinned Git Revision: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
  * Precision: `bfloat16`
* **Inference Parameters (Frozen Pre-registration)**:
  * Sampling: Greedy decoding (`do_sample = False`, `temperature = 0.0`, `top_p = 1.0`).
  * Max New Tokens: 768.
  * Random Seed: 42.
* **Prompt Conditions**:
  1. **Condition A (Zero-Shot Baseline)**: Problem statement only.
  2. **Condition D (No-Intervention Control)**: Problem statement + truncated reasoning chain (first $50\%$ of reasoning tokens) + unassisted prompt continuation.
  3. **Condition E (Lemma Scaffold Control)**: Problem statement + truncated reasoning chain + isolated intermediate lemmas + unassisted continuation.
  4. **Condition F (Full State Restoration)**: Problem statement + truncated reasoning chain + structured state restoration template with verified lemma anchors and execution budget.

---

## 3. Financial & Operational Safety Guardrails

All cloud execution experiments in Project StateShift are bounded by fail-closed safety systems:
* **Fail-Closed Execution Gate**: `.cloud_execution_locked` prevents unauthorized cloud orchestration.
* **Cost Watchdog Process**: An independent supervisor monitors cumulative RunPod API charges, enforcing a strict hard-stop spending ceiling.
* **Transactional State Sync**: Outputs are committed to local JSONL ledgers incrementally, preventing data loss on unexpected container interruption.
