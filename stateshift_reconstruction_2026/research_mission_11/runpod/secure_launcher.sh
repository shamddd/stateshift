#!/bin/bash
# ==============================================================================
# StateShift Secure Cloud Launcher (v3)
# Author: Sham Satish Thakare (github.com/shamddd)
# Target: NeurIPS 2027 Main Conference
# ==============================================================================
set -eo pipefail

echo "================================================================================"
echo " STATESHIFT SECURE RUNPOD EXPERIMENT LAUNCHER"
echo "================================================================================"

# 1. Mandatory Explicit Authorization Gate
if [ "${RUNPOD_AUTHORIZED}" != "TRUE" ]; then
    echo "[-] FATAL ERROR: Unauthorized execution blocked."
    echo "    Environment variable RUNPOD_AUTHORIZED is not set to 'TRUE'."
    echo "    To prevent accidental billing, this script will NOT launch."
    exit 1
fi

if [ -z "${RUNPOD_API_KEY}" ]; then
    echo "[-] FATAL ERROR: RUNPOD_API_KEY is not defined in environment."
    echo "    Provider-side termination cannot be guaranteed."
    exit 1
fi

if [ -z "${RUNPOD_POD_ID}" ]; then
    echo "[-] WARNING: RUNPOD_POD_ID not defined. Attempting to detect from pod metadata..."
    export RUNPOD_POD_ID=$(curl -s http://169.254.169.254/pod_id || echo "")
fi

echo "[+] Authorization verified. Pod ID: ${RUNPOD_POD_ID:-UNRESOLVED}"

# 2. Launch Independent Watchdog in Background
export MAX_RUNTIME_MINUTES=${MAX_RUNTIME_MINUTES:-90}
export MAX_BUDGET_USD=${MAX_BUDGET_USD:-1.00}
python3 /workspace/termination_watchdog.py &
WATCHDOG_PID=$!
echo "[+] Background termination watchdog active (PID: ${WATCHDOG_PID}, Limit: ${MAX_RUNTIME_MINUTES}m / \$${MAX_BUDGET_USD})"

# Trap to guarantee termination request on any exit
cleanup() {
    echo "[+] Experiment exited. Triggering provider-side billable resource termination..."
    python3 -c "from cost_controller import RunPodCostController; RunPodCostController().request_pod_termination()" || true
    echo "[+] Fallback: shutting down container OS..."
    shutdown -h now || exit 0
}
trap cleanup EXIT INT TERM

# 3. Execute Experiment Runner
BENCHMARK_FILE=${BENCHMARK_FILE:-"/workspace/stateshift/research_mission_09/benchmarks/stateshift_bench_with_answers.json"}
OUTPUT_FILE=${OUTPUT_FILE:-"/workspace/output/b1_results.jsonl"}
CHECKPOINT_FILE=${CHECKPOINT_FILE:-"/workspace/output/b1_checkpoint.json"}
MAX_PROBLEMS=${MAX_PROBLEMS:-10}

echo "[+] Starting Hardened Cloud Runner across ${MAX_PROBLEMS} problems..."
python3 /workspace/cloud_experiment_runner.py \
    --benchmark "${BENCHMARK_FILE}" \
    --output "${OUTPUT_FILE}" \
    --checkpoint "${CHECKPOINT_FILE}" \
    --max_problems "${MAX_PROBLEMS}" \
    --backend "vllm"

echo "[+] Experiment run finished successfully."
# Trap triggers pod termination here
