#!/usr/bin/env python3
"""
Stage B Cloud Experiment Runner for RunPod (Mission 10)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Enforces:
- Resume from checkpoint (skip already evaluated problems)
- Real-time JSONL streaming
- Hard timeout shutdown mechanism
- Zero secret logging
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List

def parse_args():
    parser = argparse.ArgumentParser(description="RunPod 7B Experiment Runner")
    parser.add_argument("--model-id", type=str, default="Qwen/Qwen2.5-Math-7B-Instruct")
    parser.add_argument("--benchmark", type=str, required=True, help="Path to benchmark JSON")
    parser.add_argument("--output-jsonl", type=str, required=True, help="Path to output JSONL")
    parser.add_argument("--max-runtime-minutes", type=int, default=120, help="Max runtime in minutes")
    parser.add_argument("--max-tokens", type=int, default=768, help="Token budget per rollout")
    parser.add_argument("--max-problems", type=int, default=100, help="Max problems to evaluate")
    return parser.parse_args()

def run_cloud_experiment():
    args = parse_args()
    
    # Verify authorization environment variable
    if os.getenv("RUNPOD_AUTHORIZED", "FALSE").upper() != "TRUE":
        print("[ERROR] RUNPOD_AUTHORIZED!=TRUE. Execution aborted by security gate.")
        sys.exit(1)
        
    start_time = time.time()
    max_duration_sec = args.max_runtime_minutes * 60
    
    print("=" * 80)
    print(f" RUNPOD CLOUD EXPERIMENT: {args.model_id}")
    print(f" Max Runtime: {args.max_runtime_minutes} min | Max Problems: {args.max_problems}")
    print("=" * 80)
    
    # Resume-from-checkpoint logic
    evaluated_ids = set()
    if os.path.exists(args.output_jsonl):
        print(f"Checking existing outputs in {args.output_jsonl}...")
        with open(args.output_jsonl, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        r = json.loads(line)
                        evaluated_ids.add((r["problem_id"], r["condition_code"]))
                    except Exception:
                        pass
        print(f"Resuming run. Found {len(evaluated_ids)} already completed rollouts.")
        
    with open(args.benchmark, "r") as f:
        benchmark_data = json.load(f)
        
    # Load model via vLLM
    print(f"Loading {args.model_id} via vLLM (fp16/bfloat16)...")
    try:
        from vllm import LLM, SamplingParams
        llm = LLM(model=args.model_id, tensor_parallel_size=1, max_model_len=4096, trust_remote_code=True)
        sampling_params = SamplingParams(temperature=0.0, max_tokens=args.max_tokens)
        use_vllm = True
    except Exception as e:
        print(f"vLLM initialization fallback to Hugging Face transformers: {e}")
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(args.model_id, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True)
        use_vllm = False
        
    os.makedirs(os.path.dirname(os.path.abspath(args.output_jsonl)), exist_ok=True)
    out_file = open(args.output_jsonl, "a")
    
    conditions = [
        ("Condition_D_Forced_Restart", "explicit_restart"),
        ("Condition_F_State_Preserving", "state_preserving_repair"),
        ("Condition_A_Zero_Shot", "neutral")
    ]
    
    evaluated_count = 0
    for prob in benchmark_data:
        if evaluated_count >= args.max_problems:
            break
            
        prob_id = prob.get("problem_id", prob.get("bench_id"))
        
        # Hard timeout check
        if time.time() - start_time > max_duration_sec:
            print(f"[SECURITY TIMEOUT] Reached {args.max_runtime_minutes} min limit. Shutting down gracefully.")
            break
            
        for cond_code, cond_type in conditions:
            if (prob_id, cond_code) in evaluated_ids:
                continue
                
            prompt_text = f"Problem: {prob['problem_statement']}\n\n"
            if cond_code != "Condition_A_Zero_Shot":
                prompt_text += f"Derivation so far: {prob.get('recovery_prefix', '')}\n\n"
            if cond_code == "Condition_D_Forced_Restart":
                prompt_text += "Disregard the above attempt completely. Start over from scratch and solve the problem to reach the final answer in \\boxed{}."
            elif cond_code == "Condition_F_State_Preserving":
                prompt_text += "Preserve all valid earlier steps verbatim. Correct only the flawed assertion and proceed to the final answer in \\boxed{}."
            else:
                prompt_text += "Solve the problem step by step to reach the final answer in \\boxed{}."
                
            t0 = time.time()
            if use_vllm:
                outputs = llm.generate([prompt_text], sampling_params, use_tqdm=False)
                raw_out = outputs[0].outputs[0].text
                toks = len(outputs[0].outputs[0].token_ids)
            else:
                inputs = tokenizer(prompt_text, return_tensors="pt").to("cuda")
                with torch.no_grad():
                    gen_ids = model.generate(**inputs, max_new_tokens=args.max_tokens, do_sample=False)
                raw_out = tokenizer.decode(gen_ids[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
                toks = len(gen_ids[0]) - inputs.input_ids.shape[1]
            lat = time.time() - t0
            
            record = {
                "problem_id": prob_id,
                "model_id": args.model_id,
                "condition_code": cond_code,
                "prompt": prompt_text,
                "raw_output": raw_out,
                "generated_tokens": toks,
                "latency_seconds": round(lat, 3),
                "gold_answer": prob.get("gold_answer", ""),
                "timestamp": time.time()
            }
            out_file.write(json.dumps(record) + "\n")
            out_file.flush()
            evaluated_ids.add((prob_id, cond_code))
            print(f"  [{prob_id}] {cond_code}: {toks} toks ({lat:.2f}s)")
            
        evaluated_count += 1
        
    out_file.close()
    elapsed = time.time() - start_time
    print(f"\n[COMPLETE] Evaluated {evaluated_count} problems in {elapsed/60:.2f} min. Output: {args.output_jsonl}")

if __name__ == "__main__":
    run_cloud_experiment()
