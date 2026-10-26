# Phase 12: Production RunPod Experiment Package

This directory contains the self-contained experiment package ready for controlled physical deployment.

### Package Manifest
- `runner/stateshift_production_runner_v10.py`: Master orchestrator.
- `auth/session_authorizer_v2.py`: Ed25519 cryptographic authorizer.
- `checkpoint/transactional_checkpoint_manager.py`: Atomic and monotonic checkpoint manager.
- `deployment/remote_deployment_verifier.py`: Preflight artifact & process verifier.
- `deployment/safe_resume_reconciler.py`: Safe resume and reattachment reconciler.
- `supervision/independent_financial_watchdog.py`: Decoupled background financial watchdog daemon.
- `calibration/calibration_config.py`: 10-request physical calibration configuration.
- `manifests/primary_100_manifest.json`: Frozen 400-request benchmark manifest (`3a8caf3b...`).
- `data/`: Local storage for checkpoints, receipts, and escalation records.
- `tests/`: Complete automated test suites (43 tests).
