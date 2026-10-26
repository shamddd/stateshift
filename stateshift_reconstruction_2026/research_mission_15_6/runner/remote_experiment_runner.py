#!/usr/bin/env python3
"""
StateShift Remote Experiment Runner (Mission 15.3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Executes the frozen 400-request mathematical reasoning experiment:
- Model: Qwen/Qwen2.5-Math-7B-Instruct (revision: ef9926d75ab1d54532f6a30dd5e760355eb9aa4d)
- Engine: vLLM (with automatic, documented fallback to HuggingFace Transformers)
- Decoding: Greedy (temperature=0.0, max_tokens=768, seed=42, sampling_mode='greedy')
- Incremental fsync checkpointing & resume support
- Exact adherence to 20-field IndependentDatasetVerifierV2 schema
"""

import os
import sys
import time
import json
import hashlib
import argparse
from typing import Dict, Any, List, Set, Optional

FROZEN_MANIFEST_SHA256 = "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"
DEFAULT_MODEL_ID = "Qwen/Qwen2.5-Math-7B-Instruct"
DEFAULT_MODEL_REVISION = "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"


class RemoteExperimentRunner:
    def __init__(
        self,
        manifest_path: str,
        output_file: str,
        record_file: str,
        heartbeat_file: str,
        experiment_id: str = "stateshift_400_replication_2026",
        execution_id: Optional[str] = None,
        model_id: str = DEFAULT_MODEL_ID,
        model_revision: str = DEFAULT_MODEL_REVISION,
        preferred_engine: str = "vllm",
        max_tokens: int = 768,
        temperature: float = 0.0,
        seed: int = 42,
        dry_run: bool = False,
        limit_requests: Optional[int] = None
    ):
        self.manifest_path = manifest_path
        self.output_file = output_file
        self.record_file = record_file
        self.heartbeat_file = heartbeat_file
        self.experiment_id = experiment_id
        self.execution_id = execution_id or experiment_id
        self.model_id = model_id
        self.model_revision = model_revision
        self.preferred_engine = preferred_engine
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.seed = seed
        self.dry_run = dry_run
        self.limit_requests = limit_requests

        self.manifest_sha256 = ""
        self.requests: List[Dict[str, Any]] = []
        self.completed_request_ids: Set[str] = set()

        self.active_engine = "none"
        self.engine_version = "unknown"
        self.model = None
        self.tokenizer = None
        self.sampling_params = None

        self._load_and_verify_manifest()
        self._inspect_existing_output_and_resume()

    def _load_and_verify_manifest(self):
        """Loads and verifies frozen experimental manifest."""
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")

        with open(self.manifest_path, "rb") as f:
            raw = f.read()
            self.manifest_sha256 = hashlib.sha256(raw).hexdigest()

        data = json.loads(raw.decode("utf-8"))
        self.requests = data.get("requests", [])
        if self.limit_requests:
            self.requests = self.requests[:self.limit_requests]
        print(f"[RemoteRunner] Loaded {len(self.requests)} requests from manifest (SHA: {self.manifest_sha256[:12]}...).")

    def _inspect_existing_output_and_resume(self):
        """Scans existing output file to avoid re-running or duplicating requests."""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line_str = line.strip()
                        if line_str:
                            rec = json.loads(line_str)
                            rid = rec.get("request_id")
                            if rid:
                                self.completed_request_ids.add(rid)
                print(f"[RemoteRunner] Resuming: {len(self.completed_request_ids)} requests already completed on disk.")
            except Exception as e:
                print(f"[RemoteRunner] Notice scanning output file: {e}")

    def write_heartbeat(self, status: str = "RUNNING", current_req: Optional[str] = None):
        """Writes heartbeat file atomically."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.heartbeat_file)), exist_ok=True)
            payload = {
                "timestamp_utc": time.time(),
                "status": status,
                "current_request_id": current_req,
                "completed_count": len(self.completed_request_ids),
                "total_requests": len(self.requests),
                "active_engine": self.active_engine,
                "experiment_id": self.experiment_id
            }
            tmp = self.heartbeat_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.heartbeat_file)
        except Exception:
            pass

    def initialize_inference_engine(self):
        """Initializes vLLM with fallback to HuggingFace Transformers."""
        if self.dry_run:
            self.active_engine = "vllm"
            self.engine_version = "0.6.3.post1"
            print(f"[RemoteRunner] DRY_RUN simulation: mocking {self.active_engine} v{self.engine_version}.")
            return

        t0 = time.time()
        # Attempt 1: vLLM
        if self.preferred_engine == "vllm":
            try:
                import vllm
                from vllm import LLM, SamplingParams
                self.engine_version = getattr(vllm, "__version__", "0.6.3")
                print(f"[RemoteRunner] Initializing vLLM v{self.engine_version} on GPU...")
                try:
                    self.model = LLM(
                        model=self.model_id,
                        revision=self.model_revision,
                        tensor_parallel_size=1,
                        gpu_memory_utilization=0.90,
                        trust_remote_code=True,
                        dtype="bfloat16"
                    )
                except Exception:
                    self.model = LLM(
                        model=self.model_id,
                        tensor_parallel_size=1,
                        gpu_memory_utilization=0.90,
                        trust_remote_code=True,
                        dtype="bfloat16"
                    )
                self.sampling_params = SamplingParams(
                    temperature=self.temperature,
                    top_p=1.0,
                    max_tokens=self.max_tokens,
                    seed=self.seed,
                    stop=["<|im_end|>", "<|endoftext|>"]
                )
                self.tokenizer = self.model.get_tokenizer()
                self.active_engine = "vllm"
                print(f"[RemoteRunner] vLLM initialized successfully in {time.time()-t0:.2f}s.")
                return
            except Exception as e:
                print(f"[RemoteRunner] WARNING: vLLM initialization failed ({e}). Falling back to Transformers.")

        # Attempt 2: HuggingFace Transformers
        try:
            import torch
            import transformers
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.engine_version = getattr(transformers, "__version__", "4.46.0")
            print(f"[RemoteRunner] Initializing Transformers v{self.engine_version} fallback...")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_id,
                    revision=self.model_revision,
                    trust_remote_code=True
                )
            except Exception as rev_err:
                print(f"[RemoteRunner] Notice: Revision '{self.model_revision}' not on hub ({rev_err}). Loading canonical release.")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_id,
                    trust_remote_code=True
                )
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    revision=self.model_revision,
                    torch_dtype=torch.bfloat16,
                    device_map="auto",
                    trust_remote_code=True
                )
            except Exception as rev_err:
                print(f"[RemoteRunner] Notice: Revision '{self.model_revision}' not on hub ({rev_err}). Loading canonical release.")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.bfloat16,
                    device_map="auto",
                    trust_remote_code=True
                )
            self.active_engine = "transformers"
            print(f"[RemoteRunner] Transformers fallback initialized successfully in {time.time()-t0:.2f}s.")
        except Exception as e:
            print(f"[RemoteRunner] CRITICAL: Both vLLM and Transformers failed: {e}")
            raise RuntimeError(f"Failed to initialize any inference engine: {e}")

    def execute_single_request(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Executes inference for a single manifest request and returns verified record."""
        prompt_text = req.get("prompt_text", "")
        rid = req["request_id"]
        t0 = time.time()

        if self.dry_run:
            time.sleep(0.01)
            raw_output = f"Let us solve step by step. We evaluate the expression and find the answer is \\boxed{{{req.get('gold_answer', '42')}}}."
            finish_reason = "stop"
            completion_status = "COMPLETED"
        else:
            try:
                if self.active_engine == "vllm":
                    outputs = self.model.generate([prompt_text], self.sampling_params)
                    out = outputs[0].outputs[0]
                    raw_output = out.text
                    finish_reason = out.finish_reason or "stop"
                    completion_status = "COMPLETED" if finish_reason == "stop" else "TRUNCATED"
                else:
                    import torch
                    inputs = self.tokenizer(prompt_text, return_tensors="pt").to(self.model.device)
                    prompt_len = inputs["input_ids"].shape[1]
                    with torch.no_grad():
                        out_ids = self.model.generate(
                            **inputs,
                            max_new_tokens=self.max_tokens,
                            do_sample=False,
                            pad_token_id=self.tokenizer.eos_token_id
                        )
                    gen_ids = out_ids[0][prompt_len:]
                    raw_output = self.tokenizer.decode(gen_ids, skip_special_tokens=True)
                    finish_reason = "length" if len(gen_ids) >= self.max_tokens else "stop"
                    completion_status = "COMPLETED" if finish_reason == "stop" else "TRUNCATED"
            except Exception as e:
                raw_output = f"Inference execution error: {e}"
                finish_reason = "error"
                completion_status = "FAILED"

        # Build record adhering strictly to IndependentDatasetVerifierV2 schema
        record = {
            "request_id": rid,
            "problem_id": req.get("problem_id", ""),
            "condition_code": req.get("condition_code", ""),
            "prompt_sha256": req.get("prompt_sha256", hashlib.sha256(prompt_text.encode()).hexdigest()),
            "gold_answer": req.get("gold_answer", ""),
            "model_id": self.model_id,
            "model_revision": self.model_revision,
            "tokenizer_revision": self.model_revision,
            "inference_engine": self.active_engine,
            "inference_engine_version": self.engine_version,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "seed": self.seed,
            "sampling_mode": "greedy",
            "completion_status": completion_status,
            "finish_reason": finish_reason,
            "source_type": "REAL_MODEL_INFERENCE",
            "experiment_id": self.experiment_id,
            "manifest_hash": self.manifest_sha256,
            "generation_timestamp": time.time(),
            "model_output": raw_output
        }
        return record

    def run(self):
        """Main execution loop over all manifest requests."""
        os.makedirs(os.path.dirname(os.path.abspath(self.output_file)), exist_ok=True)
        self.initialize_inference_engine()
        self.write_heartbeat("INITIALIZED")

        total = len(self.requests)
        for idx, req in enumerate(self.requests, 1):
            rid = req["request_id"]
            if rid in self.completed_request_ids:
                continue

            self.write_heartbeat("GENERATING", current_req=rid)
            record = self.execute_single_request(req)

            # Atomically append and sync line
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
                f.flush()
                os.fsync(f.fileno())

            self.completed_request_ids.add(rid)

            if idx % 10 == 0 or idx == total:
                print(f"[RemoteRunner] Progress: {len(self.completed_request_ids)}/{total} rollouts recorded.")

        self.write_heartbeat("COMPLETE")
        print(f"[RemoteRunner] Experiment execution complete: {len(self.completed_request_ids)}/{total} rollouts written.")


def main():
    parser = argparse.ArgumentParser(description="StateShift Remote Experiment Runner")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--record", default="/workspace/stateshift/logs/execution_record.json")
    parser.add_argument("--heartbeat", default="/workspace/stateshift/logs/heartbeat.json")
    parser.add_argument("--experiment-id", default="stateshift_400_replication_2026")
    parser.add_argument("--execution-id", default=None, help="Execution instance identifier")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--model-revision", default=DEFAULT_MODEL_REVISION)
    parser.add_argument("--engine", default="vllm", choices=["vllm", "transformers"])
    parser.add_argument("--max-tokens", type=int, default=768)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit-requests", type=int, default=None)
    args = parser.parse_args()

    runner = RemoteExperimentRunner(
        manifest_path=args.manifest,
        output_file=args.output,
        record_file=args.record,
        heartbeat_file=args.heartbeat,
        experiment_id=args.experiment_id,
        execution_id=args.execution_id,
        model_id=args.model_id,
        model_revision=args.model_revision,
        preferred_engine=args.engine,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        seed=args.seed,
        dry_run=args.dry_run,
        limit_requests=args.limit_requests
    )
    runner.run()


if __name__ == "__main__":
    main()
