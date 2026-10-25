# Phase 4: Remote Deployment & Artifact Verification Specification

**Module**: `research_mission_15_4/deployment/remote_deployment_verifier.py`  
**Test Suite**: `research_mission_15_4/tests/test_remote_deployment_and_resume.py` (3 Preflight Tests Passing)  

### Preflight Audit Checklist
1. **Interpreter**: Verifies remote `python3 --version` returns Python 3.10+.
2. **Storage**: Queries remote `df -k /workspace` to ensure $\ge 20$ GB available disk space.
3. **Manifest Integrity**: Executes remote `sha256sum manifests/primary_100_manifest.json` and verifies match against `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`.
4. **Runner Integrity**: Executes remote `sha256sum runner/remote_experiment_runner.py` and verifies match against approved local runner code SHA-256.
5. **Process Launch & Verification**: Launches detached process via `nohup ... > runner.log 2>&1 & echo $! > runner.pid`, reads OS PID, verifies PID in `ps -p <pid> -o pid,cmd`, and waits for authentic startup heartbeat in `logs/heartbeat.json`.
