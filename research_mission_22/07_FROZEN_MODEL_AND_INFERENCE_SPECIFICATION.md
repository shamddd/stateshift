# Phase F: Frozen Neural Model & Inference Specification

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22 — Confirmatory Trial Preflight  
**Date & Timestamp**: 2026-10-27T02:33:30+05:30  
**Target Venue**: NeurIPS 2027 Main Track  
**Freezing Status**: IMMUTABLE FOR CONFIRMATORY TRIAL  

---

## 1. Executive Summary

To ensure strict scientific reproducibility and eliminate model-drift or version-shift confounders between the pilot and confirmatory trials, the exact neural weights, tokenizer, inference parameters, precision, and environment configurations are permanently frozen. Any execution deviating from these frozen parameters is strictly invalid.

---

## 2. Neural Architecture and Weight Identification

- **Official Hugging Face Model Identifier**: `Qwen/Qwen2.5-Math-7B-Instruct`
- **Pinned Git Commit Revision (SHA-1)**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
- **Pinned Tokenizer Revision (SHA-1)**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
- **Base Architecture**: Qwen2ForCausalLM (7.61 billion parameters)
- **Attention Implementation**: FlashAttention-2 / SDPA (`torch.nn.functional.scaled_dot_product_attention`)
- **Weight Precision**: `torch.bfloat16` (16-bit brain floating point)
- **Device Map**: `auto` (single physical GPU allocation)

---

## 3. Decoding and Inference Hyperparameters

| Hyperparameter | Value | Scientific Rationale |
| :--- | :--- | :--- |
| **Decoding Strategy** | **Greedy Decoding** (`do_sample=False`) | Eliminates stochastic sampling variance; ensures deterministic replicability. |
| **Temperature** | **`0.0`** | Pure argmax token selection at each step. |
| **Top-$p$ (Nucleus Sampling)** | **`1.0`** (Unfiltered) | No probability mass truncation. |
| **Top-$k$** | **Disabled** (`-1` / `None`) | Full vocabulary evaluation. |
| **Max New Tokens** | **`768`** | Sufficient for long-horizon mathematical proofs while preventing runaway loops. |
| **Repetition Penalty** | **`1.0`** | No artificial distortion of mathematical notation frequency. |
| **Random Seed** | **`42`** | Synchronizes CUDA, PyTorch, and NumPy PRNG states. |
| **Stop Tokens** | `<|im_end|>`, `<|endoftext|>` | Standard Qwen chat template delimiters. |

---

## 4. Software and Driver Environment

- **Python Runtime**: `Python >= 3.10`
- **PyTorch Version**: `torch >= 2.4.0` with CUDA 12.1+ support
- **Transformers Version**: `transformers == 4.46.3` (or pinned container equivalent)
- **Accelerate Version**: `accelerate >= 0.34.0`
- **Flash Attention**: `flash-attn >= 2.6.3`
- **CUDA Capability**: Compute Capability 8.9 (Ada Lovelace, RTX 4090) or 8.0/9.0 (Ampere/Hopper).

---

## 5. Input Formatting and Chat Template

Inference prompts are passed to the model formatted via Qwen's official chat template:
```python
messages = [
    {"role": "system", "content": "Please reason step by step, and put your final answer within \\boxed{}."},
    {"role": "user", "content": prompt_text}
]
formatted_input = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
```
This guarantees exact alignment with the instruction post-training of `Qwen2.5-Math-7B-Instruct`.

---

## 6. Verification and Cryptographic Binding

Every generation request in `confirmatory_231_manifest.jsonl` contains explicit fields:
```json
{
  "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
  "model_revision": "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
  "temperature": 0.0,
  "max_tokens": 768,
  "seed": 42
}
```
The execution engine verifies that these fields match the runtime environment before submitting prompts to the GPU.
