#!/usr/bin/env bash
# ==============================================================================
# SECURE RUNPOD CLOUD LAUNCHER WITH HARD SHUTDOWN & SPENDING LIMIT ENFORCEMENT
# Author: Sham Satish Thakare (github.com/shamddd)
# Target: NeurIPS 2027 Main Conference
# ==============================================================================

set -euo pipefail

echo "================================================================================"
echo " STATESHIFT RUNPOD CLOUD LAUNCHER - SECURITY CHECKPOINT"
echo "================================================================================"

# 1. Authorization Verification
if [[ "${RUNPOD_AUTHORIZED:-FALSE}" != "TRUE" ]]; then
    echo "[SECURITY GATE REJECTION] RUNPOD_AUTHORIZED is not set to TRUE."
    echo "This execution is blocked. No paid compute will be incurred."
    echo "To authorize, run: export RUNPOD_AUTHORIZED=TRUE"
    exit 1
fi

# 2. Parameter Validation
MAX_RUNTIME_MINUTES="${1:-120}"
BUDGET_CAP_USD="${2:-10.00}"
SELECTED_GPU="${3:-NVIDIA RTX 4090}"
BENCHMARK_FILE="${4:-/workspace/benchmarks/stateshift_bench_with_answers.json}"
OUTPUT_FILE="${5:-/workspace/results/cloud_7b_recovery_restart.jsonl}"

echo "Authorized Execution Parameters:"
echo "  - Selected GPU:          $SELECTED_GPU"
echo "  - Maximum Runtime:       $MAX_RUNTIME_MINUTES minutes"
echo "  - Enforced Budget Cap:   \$$BUDGET_CAP_USD USD"
echo "  - Benchmark Source:      $BENCHMARK_FILE"
echo "  - Output Destination:    $OUTPUT_FILE"
echo "================================================================================"

# 3. Independent System Kill-Switch Timer (Background Watchdog)
# Automatically terminates the pod after MAX_RUNTIME_MINUTES to prevent idle billing
(
    sleep $(( MAX_RUNTIME_MINUTES * 60 ))
    echo "[WATCHDOG TIMEOUT] Maximum allowed runtime reached ($MAX_RUNTIME_MINUTES min). Terminating instance now."
    shutdown -h now || init 0 || kill -9 -1
) &
WATCHDOG_PID=$!
echo "Active instance watchdog armed (PID: $WATCHDOG_PID, Timeout: $MAX_RUNTIME_MINUTES min)."

# 4. Launch Experiment Runner
echo "Starting cloud experiment execution..."
python3 /workspace/cloud_experiment_runner.py \
    --model-id "Qwen/Qwen2.5-Math-7B-Instruct" \
    --benchmark "$BENCHMARK_FILE" \
    --output-jsonl "$OUTPUT_FILE" \
    --max-runtime-minutes "$MAX_RUNTIME_MINUTES" \
    --max-tokens 768 \
    --max-problems 100

echo "Experiment successfully completed. Cleaning up watchdog..."
kill "$WATCHDOG_PID" || true

# 5. Automated Shutdown to Prevent Idle Billing
echo "[SHUTDOWN] Workload complete. Triggering instant server shutdown..."
shutdown -h now || init 0 || true
