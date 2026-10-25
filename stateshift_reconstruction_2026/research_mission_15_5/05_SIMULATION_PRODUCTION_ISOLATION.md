# 05 Simulation / Production Isolation Architecture

**Module:** `research_mission_15_5/runner/stateshift_production_runner_v10.py`  
**Tests:** `test_blocker_4_simulation_flags_rejected_in_paid_modes`, `test_scenario_E_simulation_injection_rejected`.

---

## 1. Strict Isolation Enforcement
To prevent synthetic data or simulated behaviors from contaminating real experimental runs, the runner validates arguments during `__init__` before any network, state, or filesystem operations:
In paid modes (`CALIBRATION`, `PRODUCTION`), passing any simulation flag immediately aborts execution with exit code 2 before network or state mutation.

## 2. CLI Exit Code Contract
- Passing any simulation argument with `--mode CALIBRATION` or `--mode PRODUCTION` exits immediately with **code 2**.
- Output explicitly states the security violation, preventing accidental CI/CD misconfiguration.
