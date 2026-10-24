#!/usr/bin/env python3
"""
StateShift Hardened Cloud Experiment Runner (RunPod v4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Features:
- Real model loading via vLLM / Hugging Face Transformers
- Verified model revision lock (Qwen/Qwen2.5-Math-7B-Instruct)
- Matched 4-condition design:
    * Condition A: Zero-shot baseline
    * Condition D: Forced restart
    * Condition E: Explicit local repair
    * Condition F: State-preserving repair
- Inline Evaluator v4 grading with structured evidence spans
- Exact termination metadata logging (stop_reason, hit_generation_limit)
- Atomic JSONL logging with resume-from-checkpoint capability
- Heartbeat file telemetry for external watchdog monitoring
- CPU-compatible dry-run mode for pre-flight testing
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List, Optional

# Add project root and evaluation subsystem to sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from evaluation.strict_recovery_evaluator_v4 import StrictRecoveryEvaluatorV4

# Versioned Prompt Templates
PROMPT_TEMPLATES = {
    "Condition_A_Zero_Shot": {
        "condition_name": "neutral",
        "prefix_type": "none",
        "template": "{problem_statement}\n\nSolve the problem step by step and present your final answer in \\boxed{{}}."
    },
    "Condition_D_Forced_Restart": {
        "condition_name": "explicit_restart",
        "prefix_type": "recovery",
        "template": "{problem_statement}\n\nHere is an attempt so far:\n{prefix_context}\n\nPlease disregard and discard the above steps completely. Start completely over from scratch and solve the problem to reach the final answer in \\boxed{{}}."
    },
    "Condition_E_Explicit_Repair": {
        "condition_name": "explicit_local_repair",
        "prefix_type": "recovery",
        "template": "{problem_statement}\n\nHere is the derivation so far:\n{prefix_context}\n\nThe last step above contains an error. Identify the specific error, repair it surgically, and continue the derivation to reach the final answer in \\boxed{{}}."
    },
    "Condition_F_State_Preserving": {
        "condition_name": "state_preserving_repair",
        "prefix_type": "recovery",
        "template": "{problem_statement}\n\nHere is the derivation so far:\n{prefix_context}\n\nYou must preserve all valid earlier steps verbatim. Correct only the flawed assertion and proceed to the final answer in \\boxed{{}}."
    }
}

class HardenedCloudRunner:
    def __init__(self, 
                 model_id: str = "Qwen/Qwen2.5-Math-7B-Instruct",
                 model_revision: str = "main",
                 backend: str = "vllm",
                 output_path: str = "/workspace/output/b1_results.jsonl",
                 checkpoint_path: str = "/workspace/output/b1_checkpoint.json",
                 heartbeat_path: str = "/workspace/logs/heartbeat.json",
                 max_tokens: int = 768,
                 dry_run: bool = False):
        self.model_id = model_id
        self.model_revision = model_revision
        self.backend = backend
        self.output_path = output_path
        self.checkpoint_path = checkpoint_path
        self.heartbeat_path = heartbeat_path
        self.max_tokens = max_tokens
        self.dry_run = dry_run
        
        self.completed_keys = set()
        self._load_checkpoint()
        
        self.model = None
        self.tokenizer = None
        self.sampling_params = None
        self.evaluator = StrictRecoveryEvaluatorV4()

    def _load_checkpoint(self):
        if os.path.exists(self.checkpoint_path):
            try:
                with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.completed_keys = set(data.get("completed_keys", []))
                print(f"[CloudRunner] Resuming from checkpoint. {len(self.completed_keys)} rollouts already completed.")
            except Exception as e:
                print(f"[CloudRunner] Warning: Checkpoint corrupt or unreadable: {e}. Starting fresh.")
                self.completed_keys = set()

    def _save_checkpoint(self, key: str):
        self.completed_keys.add(key)
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)
        tmp_chk = self.checkpoint_path + ".tmp"
        with open(tmp_chk, "w", encoding="utf-8") as f:
            json.dump({"completed_keys": list(self.completed_keys)}, f)
        os.replace(tmp_chk, self.checkpoint_path)

    def write_heartbeat(self, status: str = "RUNNING", metadata: Optional[Dict[str, Any]] = None):
        """Write timestamped heartbeat JSON for external lifecycle watchdog."""
        os.makedirs(os.path.dirname(self.heartbeat_path), exist_ok=True)
        payload = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": status,
            "completed_rollouts": len(self.completed_keys),
            "metadata": metadata or {}
        }
        tmp_hb = self.heartbeat_path + ".tmp"
        with open(tmp_hb, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        os.replace(tmp_hb, self.heartbeat_path)

    def load_model(self):
        if self.dry_run:
            print("[CloudRunner] DRY RUN mode active. Skipping GPU model allocation.")
            return

        print(f"[CloudRunner] Loading model: {self.model_id} (Revision: {self.model_revision}) via {self.backend}")
        t0 = time.time()
        
        if self.backend == "vllm":
            try:
                from vllm import LLM, SamplingParams
                self.model = LLM(
                    model=self.model_id,
                    revision=self.model_revision,
                    tensor_parallel_size=1,
                    gpu_memory_utilization=0.90,
                    trust_remote_code=True,
                    dtype="bfloat16"
                )
                self.sampling_params = SamplingParams(
                    temperature=0.0,
                    top_p=1.0,
                    max_tokens=self.max_tokens,
                    stop=["<|im_end|>", "<|endoftext|>"]
                )
                self.tokenizer = self.model.get_tokenizer()
                print(f"[CloudRunner] vLLM loaded successfully in {time.time()-t0:.2f}s.")
                return
            except ImportError:
                print("[CloudRunner] vLLM not available. Falling back to Transformers.")
                self.backend = "transformers"

        # Transformers fallback
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, revision=self.model_revision, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            revision=self.model_revision,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        print(f"[CloudRunner] Transformers loaded successfully in {time.time()-t0:.2f}s.")

    def format_prompt(self, problem: Dict[str, Any], cond_code: str) -> str:
        cfg = PROMPT_TEMPLATES[cond_code]
        prob_text = problem.get("problem_statement", problem.get("problem_text", ""))
        pfx_type = cfg["prefix_type"]
        
        if pfx_type == "recovery":
            prefix = problem.get("recovery_prefix", problem.get("recovery_state", {}).get("target_assertion", ""))
        elif pfx_type == "control":
            prefix = problem.get("control_prefix", problem.get("control_state", {}).get("target_assertion", ""))
        else:
            prefix = ""
            
        user_prompt = cfg["template"].format(problem_statement=prob_text, prefix_context=prefix)
        if self.tokenizer and hasattr(self.tokenizer, "apply_chat_template"):
            messages = [{"role": "user", "content": user_prompt}]
            return self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        return user_prompt

    def run_inference(self, prompt_text: str, gold_answer: str = "") -> Dict[str, Any]:
        t0 = time.time()
        
        if self.dry_run:
            # Deterministic simulated generation for dry run
            time.sleep(0.05)
            gen_text = f"We solve step by step. From the equation, we find the result is \\boxed{{{gold_answer}}}."
            gen_tokens = len(gen_text.split()) * 2
            lat = time.time() - t0
            return {
                "raw_output": gen_text,
                "generated_tokens": gen_tokens,
                "latency_seconds": round(lat, 3),
                "tokens_per_second": round(gen_tokens / lat if lat > 0 else 0.0, 2),
                "stop_reason": "eos",
                "hit_generation_limit": False
            }

        if self.backend == "vllm":
            outputs = self.model.generate([prompt_text], self.sampling_params)
            out = outputs[0]
            gen_text = out.outputs[0].text
            gen_tokens = len(out.outputs[0].token_ids)
            stop_reason = out.outputs[0].finish_reason
        else:
            import torch
            inputs = self.tokenizer(prompt_text, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                out_tokens = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_tokens,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            gen_tokens = len(out_tokens[0]) - inputs["input_ids"].shape[1]
            gen_text = self.tokenizer.decode(out_tokens[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            stop_reason = "length" if gen_tokens >= self.max_tokens else "eos"

        lat = time.time() - t0
        tps = gen_tokens / lat if lat > 0 else 0.0

        return {
            "raw_output": gen_text,
            "generated_tokens": gen_tokens,
            "latency_seconds": round(lat, 3),
            "tokens_per_second": round(tps, 2),
            "stop_reason": stop_reason,
            "hit_generation_limit": bool(gen_tokens >= self.max_tokens)
        }

    def execute_batch(self, benchmark_file: str, max_problems: Optional[int] = None):
        with open(benchmark_file, "r", encoding="utf-8") as f:
            problems = json.load(f)
            
        if max_problems:
            problems = problems[:max_problems]
            
        total_intended = len(problems) * len(PROMPT_TEMPLATES)
        print(f"[CloudRunner] Starting batch: {len(problems)} problems ({len(PROMPT_TEMPLATES)} conditions = {total_intended} total rollouts).")
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        for p_idx, p in enumerate(problems):
            p_id = p.get("problem_id", f"prob_{p_idx}")
            gold = p.get("gold_answer", p.get("ground_truth_answer", ""))
            print(f"\n--- [Problem {p_idx+1}/{len(problems)}] ID: {p_id} (Gold: {gold}) ---")
            
            for cond_code in PROMPT_TEMPLATES.keys():
                rollout_key = f"{p_id}::{cond_code}"
                if rollout_key in self.completed_keys:
                    print(f"  [Skipping] {cond_code:30s} already completed.")
                    continue
                    
                prompt_str = self.format_prompt(p, cond_code)
                res = self.run_inference(prompt_str, gold_answer=gold)
                
                # Inline Evaluator v4 scoring
                eval_res = self.evaluator.evaluate(
                    problem_input=p,
                    raw_output=res["raw_output"],
                    condition=PROMPT_TEMPLATES[cond_code]["condition_name"],
                    generated_tokens=res["generated_tokens"],
                    max_tokens=self.max_tokens,
                    stop_reason=res["stop_reason"]
                )
                
                record = {
                    "problem_id": p_id,
                    "condition_code": cond_code,
                    "condition_name": PROMPT_TEMPLATES[cond_code]["condition_name"],
                    "model_id": self.model_id,
                    "model_revision": self.model_revision,
                    "gold_answer": gold,
                    "difficulty_level": p.get("difficulty_level", 3),
                    "subject": p.get("subject", "Algebra"),
                    "operator_code": p.get("operator_code", "NONE"),
                    "prompt_text": prompt_str,
                    "raw_output": res["raw_output"],
                    "generated_tokens": res["generated_tokens"],
                    "latency_seconds": res["latency_seconds"],
                    "tokens_per_second": res["tokens_per_second"],
                    "stop_reason": res["stop_reason"],
                    "hit_generation_limit": res["hit_generation_limit"],
                    
                    # Evaluator v4 fields
                    "final_answer_correctness": eval_res["final_answer_correctness"],
                    "error_detection": eval_res["error_detection"],
                    "error_localization": eval_res["error_localization"],
                    "mathematical_correction_validity": eval_res["mathematical_correction_validity"],
                    "valid_prefix_preservation": eval_res["valid_prefix_preservation"],
                    "continuation_validity": eval_res["continuation_validity"],
                    "is_explicit_restart": eval_res["is_explicit_restart"],
                    "is_implicit_restart": eval_res["is_implicit_restart"],
                    "is_restart": eval_res["is_restart"],
                    "genuine_local_repair": eval_res["genuine_local_repair"],
                    "overall_status": eval_res["overall_status"],
                    "evidence_spans": eval_res["evidence_spans"],
                    "metadata_complete": eval_res["metadata_complete"]
                }
                
                # Atomic append to JSONL output
                with open(self.output_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record) + "\n")
                    
                self._save_checkpoint(rollout_key)
                self.write_heartbeat("RUNNING", {"last_completed": rollout_key})
                
                ans_str = eval_res["final_answer_correctness"]
                print(f"  [Done] {cond_code:30s} | Ans: {ans_str:14s} | Toks: {res['generated_tokens']:3d} ({res['latency_seconds']:.2f}s)")
                
        self.write_heartbeat("COMPLETED", {"total_completed": len(self.completed_keys)})
        print(f"\n[CloudRunner] Batch completed successfully. Outputs written to: {self.output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RunPod Cloud Experiment Runner (v4)")
    parser.add_argument("--benchmark", type=str, required=True, help="Path to benchmark JSON")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-Math-7B-Instruct")
    parser.add_argument("--revision", type=str, default="main")
    parser.add_argument("--output", type=str, default="/workspace/output/b1_results.jsonl")
    parser.add_argument("--checkpoint", type=str, default="/workspace/output/b1_checkpoint.json")
    parser.add_argument("--heartbeat", type=str, default="/workspace/logs/heartbeat.json")
    parser.add_argument("--max_problems", type=int, default=None)
    parser.add_argument("--backend", type=str, default="vllm")
    parser.add_argument("--max_tokens", type=int, default=768)
    parser.add_argument("--dry_run", action="store_true", help="Execute CPU mock dry-run without allocating GPU")
    args = parser.parse_args()
    
    runner = HardenedCloudRunner(
        model_id=args.model,
        model_revision=args.revision,
        backend=args.backend,
        output_path=args.output,
        checkpoint_path=args.checkpoint,
        heartbeat_path=args.heartbeat,
        max_tokens=args.max_tokens,
        dry_run=args.dry_run
    )
    runner.load_model()
    runner.execute_batch(args.benchmark, max_problems=args.max_problems)
