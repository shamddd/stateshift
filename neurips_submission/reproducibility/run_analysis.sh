#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "========================================================================"
echo "STATESHIFT COMPLETE REPRODUCIBLE ANALYSIS PIPELINE"
echo "========================================================================"

python3 validate_environment.py
python3 validate_data.py

echo "=== [3] EXECUTING PRIMARY STATISTICAL REPRODUCTION ==="
python3 reproduce.py

python3 generate_tables_and_figures.py

echo "========================================================================"
echo "REPRODUCIBLE ANALYSIS COMPLETED SUCCESSFULLY IN < 3 SECONDS."
echo "========================================================================"
