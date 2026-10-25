#!/usr/bin/env bash
# StateShift Secure Cloud Container Launcher (Mission 12)
# Author: Sham Satish Thakare (github.com/shamddd)
# Target: NeurIPS 2027 Main Conference

set -euo pipefail

echo "=========================================================="
echo " StateShift Secure Cloud Execution Engine (Mission 12)"
echo " Model: Qwen/Qwen2.5-Math-7B-Instruct (bfloat16 vLLM)"
echo " Evaluator: Mathematical Recovery Evaluator v4"
echo "=========================================================="

# Check for explicit user authorization
if [[ "${RUNPOD_AUTHORIZED:-FALSE}" != "TRUE" ]]; then
    echo "FATAL: RUNPOD_AUTHORIZED environment variable is not 'TRUE'."
    echo "Refusing to execute unattended cloud inference."
    exit 1
fi

echo "[Launcher] Authorization confirmed. Initializing execution environment..."
mkdir -p /workspace/output /workspace/checkpoints /workspace/logs

# Execute Cloud Experiment Runner
python3 /workspace/cloud_experiment_runner.py \
    --benchmark "${BENCHMARK_PATH:-/workspace/benchmarks/stateshift_bench_with_answers.json}" \
    --model "${MODEL_ID:-Qwen/Qwen2.5-Math-7B-Instruct}" \
    --revision "${MODEL_REVISION:-main}" \
    --output "/workspace/output/b1_results.jsonl" \
    --checkpoint "/workspace/checkpoints/b1_checkpoint.json" \
    --backend "${BACKEND:-vllm}"

echo "[Launcher] Experiment execution completed successfully."
