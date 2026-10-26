# 11 Full Regression Test Results

**Date:** 2026-10-25  
**Platform:** macOS Darwin (Apple Silicon M1, Python 3.13.9, pytest-8.4.2)  
**Total Tests Executed:** 203  
**Passing:** 203  
**Failing:** 0  
**Pass Rate:** 100.0%  

---

## Test Inventory by Mission Directory
- `research_mission_15/tests/`: 18 passed (Adversarial evaluator, failure injection, dry runs).
- `research_mission_15_1/tests/`: 36 passed (Dataset verifier, emergency termination, 16 end-to-end scenarios, production transport).
- `research_mission_15_2/tests/`: 43 passed (Nonblocking termination, destruction verification, strict provenance, financial retry).
- `research_mission_15_3/tests/`: 23 passed (Budget-aware scheduler, session authorizer, exact CLI scenarios).
- `research_mission_15_4/tests/`: 49 passed (Cryptographic authorizer, independent watchdog, remote deployment, transactional checkpoint, 20 CLI scenarios).
- `research_mission_15_5/tests/`: 34 passed:
  - `test_blocker_fixes.py`: 12 passed.
  - `test_blocker_reproductions.py`: 7 passed.
  - `test_cli_subprocess_15_scenarios.py`: 15 passed.

**Total Cumulative Test Coverage:** 203 tests across all modules.
