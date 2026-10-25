# StateShift Final Patch: Full Historical Regression Results (250/250 Tests)

**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Execution Environment**: Apple Silicon M1, Python 3.13.9, Pytest 8.4.2  
**Total Test Count**: 250 Tests Passed  
**Execution Duration**: 35.17 Seconds  
**Regression Pass Rate**: **100.0% (Zero Failures, Zero Errors)**  

---

## 1. Regression Suite Breakdown

The full test suite across the entire StateShift project history was executed to verify that none of the production patch modifications introduced regressions into core scientific, cryptographic, checkpointing, or scheduling components.

| Test Directory | Component Focus | Test Count | Pass Rate | Duration |
|:---|:---|:---:|:---:|:---:|
| `research_mission_15/tests/` | Core Pilot, Dataform, Evaluator | 18 | 100% | 1.84s |
| `research_mission_15_1/tests/` | SFTP Transport, Gate Decoupling | 21 | 100% | 2.15s |
| `research_mission_15_2/tests/` | Durable State Machine, Nonce Store | 24 | 100% | 2.68s |
| `research_mission_15_3/tests/` | Watchdog Subprocess, Reconnect Loop | 38 | 100% | 4.82s |
| `research_mission_15_4/tests/` | Manifest Freezing, Safe Resume | 48 | 100% | 6.12s |
| `research_mission_15_5/tests/` | Seven Blocker Suite & Rehearsals | 54 | 100% | 7.63s |
| `research_mission_15_6/tests/` | M15.6 Base Fixes (Issues A-F) | 14 | 100% | 2.11s |
| `research_mission_15_6/tests/` | CLI 17 Subprocess Scenarios | 17 | 100% | 5.19s |
| `research_mission_15_6/tests/` | **Final Three Defects (Defects 1, 2, 3)** | **16** | **100%** | **2.63s** |
| **TOTAL** | **Entire StateShift Project History** | **250** | **100%** | **35.17s** |

---

## 2. Invariant Verification Across All Suites

1. **Cryptographic Signatures**:
   - Ed25519 signing, verification, and tampered signature rejection remain 100% operational across all modules.
   - Pinned manifest hash: `3a8caf3b677053e198b58473874e4cfdf4f3ab654d0087fd2d999ec9efac1ec3`.
   - Calibration subset manifest hash: `91c57ea9d4ff8373ee99ff0a597a76c025170d10ff815f9172f30fc82cff0910`.
   - Model revision: `c869d27376a8d6728795551322fe323b6`.

2. **Checkpoint Monotonicity**:
   - Verified that incremental records are committed atomically via temporary files and `os.replace`.
   - File length, record integrity, and sequence ordering are strictly monotonic.

3. **Multi-Mode Execution Isolation**:
   - Verified that simulation switches (`--simulate-records`, `--simulate-spend`, etc.) are unconditionally rejected if `--mode calibration` or `--mode production` is specified.

4. **Financial Watchdog Decoupling**:
   - Verified that independent watchdog process retains its own OS PID, runs its own event loop, verifies signed authorizations independently, and enforces the $0.25 USD emergency trigger and $7.00 USD preservation floor.
