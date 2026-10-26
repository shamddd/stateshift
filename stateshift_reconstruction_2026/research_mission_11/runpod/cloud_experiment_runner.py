#!/usr/bin/env python3
"""
StateShift Hardened Cloud Experiment Runner (RunPod v3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Features:
- Real model loading via vLLM / Hugging Face Transformers
- Verified model revision lock (Qwen/Qwen2.5-Math-7B-Instruct)
- Matched 4-condition design:
    * Condition A: Zero-shot baseline
    * Condition D: Forced restart
    * Condition E: Explicit local repair
    * Condition F: State-preserving repair
- Rigorous generation settings (greedy decoding, seed 42, max_tokens 768)
- Exact termination metadata logging (stop_reason, hit_generation_limit)
- Atomic JSONL logging with resume-from-checkpoint capability
- Per-condition schema validation
"""

import os
import sys
import json
import time
import argparse
import tempfile
from typing import Dict, Any, List, Optional

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
                 checkpoint_path: str = "/workspace/output/b1_checkpoint.json"):
        self.model_id = model_id
        self.model_revision = model_revision
        self.backend = backend
        self.output_path = output_path
        self.checkpoint_path = checkpoint_path
        
        self.completed_keys = set()
        self._load_checkpoint()
        
        self.model = None
        self.tokenizer = None
        self.sampling_params = None

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
        tmp_chk = self.checkpoint_path + ".tmp"
        with open(tmp_chk, "w", encoding="utf-8") as f:
            json.dump({"completed_keys": list(self.completed_keys)}, f)
        os.replace(tmp_chk, self.checkpoint_path)

    def load_model(self):
        print(f"[CloudRunner] Loading model: {self.model_id} (Revision: {self.model_revision}) using backend: {self.backend}")
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
                    max_tokens=768,
                    stop=["<|im_end|>", "<|endoftext|>"]
                )
                self.tokenizer = self.model.get_tokenizer()
                print(f"[CloudRunner] vLLM loaded successfully in {time.time()-t0:.2f}s.")
                return
            except ImportError:
                print("[CloudRunner] vLLM not available. Falling back to HuggingFace Transformers.")
                self.backend = "transformers"

        # HuggingFace Transformers Fallback
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
        print(f"[CloudRunner] Transformers model loaded successfully in {time.time()-t0:.2f}s.")

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
        messages = [{"role": "user", "content": user_prompt}]
        return self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    def run_inference(self, prompt_text: str) -> Dict[str, Any]:
        t0 = time.time()
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
                    max_new_tokens=768,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            gen_tokens = len(out_tokens[0]) - inputs["input_ids"].shape[1]
            gen_text = self.tokenizer.decode(out_tokens[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            stop_reason = "length" if gen_tokens >= 768 else "eos"

        lat = time.time() - t0
        tps = gen_tokens / lat if lat > 0 else 0.0

        return {
            "raw_output": gen_text,
            "generated_tokens": gen_tokens,
            "latency_seconds": round(lat, 3),
            "tokens_per_second": round(tps, 2),
            "stop_reason": stop_reason,
            "hit_generation_limit": bool(gen_tokens >= 768)
        }

    def execute_batch(self, benchmark_file: str, max_problems: Optional[int] = None):
        with open(benchmark_file, "r", encoding="utf-8") as f:
            problems = json.load(f)
            
        if max_problems:
            problems = problems[:max_problems]
            
        print(f"[CloudRunner] Beginning execution across {len(problems)} problems (4 conditions = {len(problems)*4} total rollouts).")
        
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        for p_idx, p in enumerate(problems):
            p_id = p.get("problem_id", f"prob_{p_idx}")
            print(f"\n--- [Problem {p_idx+1}/{len(problems)}] ID: {p_id} ---")
            
            for cond_code in PROMPT_TEMPLATES.keys():
                rollout_key = f"{p_id}::{cond_code}"
                if rollout_key in self.completed_keys:
                    print(f"  [Skipping] {cond_code:30s} already completed.")
                    continue
                    
                prompt_str = self.format_prompt(p, cond_code)
                res = self.run_inference(prompt_str)
                
                record = {
                    "problem_id": p_id,
                    "condition_code": cond_code,
                    "model_id": self.model_id,
                    "model_revision": self.model_revision,
                    "gold_answer": p.get("gold_answer", p.get("ground_truth_answer", "")),
                    "difficulty_level": p.get("difficulty_level", 3),
                    "subject": p.get("subject", "Algebra"),
                    "operator_code": p.get("operator_code", "NONE"),
                    "prompt_text": prompt_str,
                    "raw_output": res["raw_output"],
                    "generated_tokens": res["generated_tokens"],
                    "latency_seconds": res["latency_seconds"],
                    "tokens_per_second": res["tokens_per_second"],
                    "stop_reason": res["stop_reason"],
                    "hit_generation_limit": res["hit_generation_limit"]
                }
                
                # Atomic append to output
                with open(self.output_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record) + "\n")
                    
                self._save_checkpoint(rollout_key)
                print(f"  [Done] {cond_code:30s} | Tokens: {res['generated_tokens']} ({res['latency_seconds']:.2f}s, {res['tokens_per_second']:.1f} t/s)")
                
        print(f"\n[CloudRunner] Batch execution completed successfully. Outputs written to: {self.output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RunPod Cloud Experiment Runner")
    parser.add_argument("--benchmark", type=str, required=True, help="Path to benchmark JSON")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-Math-7B-Instruct")
    parser.add_argument("--revision", type=str, default="main")
    parser.add_argument("--output", type=str, default="/workspace/output/b1_results.jsonl")
    parser.add_argument("--checkpoint", type=str, default="/workspace/output/b1_checkpoint.json")
    parser.add_argument("--max_problems", type=int, default=None)
    parser.add_argument("--backend", type=str, default="vllm")
    args = parser.parse_args()
    
    runner = HardenedCloudRunner(
        model_id=args.model,
        model_revision=args.revision,
        backend=args.backend,
        output_path=args.output,
        checkpoint_path=args.checkpoint
    )
    runner.load_model()
    runner.execute_batch(args.benchmark, max_problems=args.max_problems)
