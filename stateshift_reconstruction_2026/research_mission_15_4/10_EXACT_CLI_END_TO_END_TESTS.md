# Phase 10: Exact CLI Subprocess End-to-End Tests

**Test Script**: `research_mission_15_4/tests/test_cli_subprocess_20_scenarios.py`  
**Runner Executable**: `research_mission_15_4/runner/stateshift_production_runner_v10.py`  

### Tested Operational Scenarios
1. **Scenario 13: Unauthorized Session Rejection**: Invoking CLI without authorization doc immediately halts with code `1` and outputs `AUTHORIZATION ABORT`.
2. **Scenario 14: Tampered Signature Rejection**: Modifying signature bytes causes immediate rejection via `Ed25519 cryptographic signature verification FAILED`.
3. **Scenario 19: Calibration Bounded Completion**: Running in `CALIBRATION` mode completes strictly after 10 requests, transitioning to `REMOTE_COMPLETE` and `FINISHED` without launching full 400-request production.
4. **Scenario 20: Normal Production Completion**: Running full 400-request simulation completes, verifies dataset, and persists durable termination receipt.
5. **Scenario 02: Financial Emergency Stop**: Simulating `$1.70 USD` spend breaches the `$1.65 USD` emergency threshold, triggering immediate emergency shutdown and receipt persistence.
6. **Scenario 11: Remote Deployment Failure**: Injected remote deployment failure halts execution with `DEPLOYMENT VERIFICATION ABORT`.
