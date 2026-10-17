#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "========================================================================"
echo "STATESHIFT UNIT & REPRODUCIBILITY TEST SUITE"
echo "========================================================================"

# Run test suite from tests/
if [ -d "${SCRIPT_DIR}/tests" ]; then
    pytest "${SCRIPT_DIR}/tests" -v
elif [ -d "${SCRIPT_DIR}/../tests" ]; then
    pytest "${SCRIPT_DIR}/../tests" -v
else
    pytest tests/ -v
fi

echo "========================================================================"
echo "ALL UNIT & SMOKE TESTS PASSED."
echo "========================================================================"
