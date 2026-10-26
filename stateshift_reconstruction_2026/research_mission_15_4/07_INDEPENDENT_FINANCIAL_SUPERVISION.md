# Phase 7: Independent Financial Supervision Specification

**Module**: `research_mission_15_4/supervision/independent_financial_watchdog.py`  
**Test Suite**: `research_mission_15_4/tests/test_independent_financial_watchdog.py` (4 Tests Passing)  

### Independent Architecture
- **Process Isolation**: Spawns as an independent background process (`subprocess.Popen` or daemon) decoupled from orchestrator Python threads.
- **Monotonic Clock**: Evaluates time via `time.monotonic()` to protect against wall-clock skew or NTP adjustments.
- **Dedicated HTTPS Connection**: Uses an independent `urllib` HTTPS client with a strict 5-second socket timeout to query the RunPod GraphQL endpoint.
- **Autonomous Termination Authority**:
  - Triggers immediate pod termination if calculated spend breaches `$1.6500 USD`.
  - Triggers termination if billable runtime exceeds 160 minutes.
  - Triggers termination if the main controller heartbeat file is not updated for $> 120.0$ seconds (hang detection).
  - Emits local durable escalation files if provider API calls fail.
