# 06 Calibration Budget Enforcement Specification

**Module:** `research_mission_15_5/calibration/calibration_config.py`  
**Tests:** `test_blocker_5_calibration_budget_bounds_enforced`, `test_scenario_F_budget_mismatch_rejected`.

---

## 1. Budget Bounds for Calibration
- **Maximum Authorized Spend (`max_authorized_usd`):** Strictly capped at `$0.3500` USD.
- **Emergency Termination Trigger (`emergency_trigger_usd`):** Strictly capped at `$0.2500` USD.
- **Safety Reserve Floor:** `$0.1000` USD headroom maintained at all times.
- **Hourly GPU Rate:** `$0.8900` USD/hour (RTX 4090 standard secure cloud).
- **Maximum Calibration Runtime:** 15.0 minutes (900 seconds).

## 2. Watchdog Limits Derivation
The watchdog does not rely on hardcoded defaults or unverified CLI arguments. It extracts `max_authorized_usd` and `emergency_trigger_usd` directly from the validated cryptographic authorization payload. If CLI parameters disagree with the authorization document, the runner aborts before spawning the watchdog.
