# Research Mission 23 — Phase 6: GPU Runner Engineering and Resume Safety Audit

## 1. Engine Architecture & Script Specification
The primary execution engine for the StateShift confirmatory experiment is implemented in:
- **Script Path**: `research_mission_22/scripts/run_confirmatory_trial.py`
- **File Size**: 16,846 bytes
- **SHA-256 Checksum**: `05bca4587db8c8cb836a9926d1beee7bcf6891eb6a7c64c1cf6c2dd1bfaf713e`

---

## 2. Neural Execution and Model Environment

The runner enforces strict model environment pinning:
1. **Model Hugging Face Identifier**: `Qwen/Qwen2.5-Math-7B-Instruct`
2. **Pinned Weights Revision**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` (Full 40-character Git commit hash)
3. **Tokenizer Revision**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
4. **Precision**: `torch.bfloat16` on physical GPU
5. **Deterministic Hyperparameters**:
   - `temperature`: `0.0`
   - `sampling_mode`: `greedy`
   - `seed`: `42`
   - `max_new_tokens`: `768`
6. **Execution Engine**: `vLLM` (version `0.6.3+`) or native `transformers` (`4.46.3+`) with PyTorch `2.4.0+cu124`.

---

## 3. Mandatory 23-Field Output Schema

Every generation record written to disk adheres to the frozen 23-field schema:
- Identification: `request_id`, `problem_id`, `condition_code`, `experiment_id`, `manifest_hash`
- Model Provenance: `model_id`, `model_revision`, `tokenizer_revision`, `inference_engine`, `inference_engine_version`
- Hyperparameters: `temperature`, `max_tokens`, `seed`, `sampling_mode`
- Runtime Telemetry: `prompt_tokens`, `completion_tokens`, `latency_ms`, `generation_timestamp`
- Outputs & Evaluation: `prompt_sha256`, `model_output`, `extracted_answer`, `is_correct`, `finish_reason`, `completion_status`, `source_type`

### Falsification Guard: `source_type` Partitioning
- Under local dry-run or mock execution, `source_type` is automatically hardcoded to:
  `"MOCK_LOCAL_TEST"`
- Under physical GPU cloud execution, `source_type` is set to:
  `"REAL_MODEL_INFERENCE"`
The production runner forbids setting `REAL_MODEL_INFERENCE` unless executed on a verified physical GPU with live forward passes.

---

## 4. Crash-Resilience, Atomic Writes, and Resume Architecture

1. **Atomic Flush and Sync**:
   Every individual record write executes:
   ```python
   with open(output_path, "a", encoding="utf-8") as f:
       f.write(json.dumps(record) + "\n")
       f.flush()
       os.fsync(f.fileno())
   ```
   This guarantees that records are physically committed to non-volatile storage immediately upon completion.
2. **Duplicate Suppression and Auto-Resume**:
   - The runner initializes `completed_ids = load_existing_checkpoint(output_path)`.
   - Before executing request $j$, the runner checks `if req_id in completed_ids: continue`.
   - If the pod disconnects or halts after 500 requests, re-running the runner automatically resumes from request 501 with zero duplicate inference calls or wasted funds.
3. **Local Failure Recovery Testing**:
   Tested in `test_mission_22_1_regressions.py::test_resume_behavior`. Confirmed that mock runs resume cleanly from existing output JSONL files.
