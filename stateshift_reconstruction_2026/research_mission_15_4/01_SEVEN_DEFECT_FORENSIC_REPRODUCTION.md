# Forensic Reproduction & Verification of Seven Pre-Hardening Defects

This document details the exact reproduction methodology, failure characteristics, and hardened architectural solutions for the seven vulnerabilities identified at the conclusion of Mission 15.3.

---

### Defect 1: Plain JSON Authorization Lacked Cryptographic Tamper Resistance
- **Pre-Hardening Flaw**: In Mission 15.3, `SessionAuthorizer` verified approval by inspecting simple string values inside a dictionary (e.g. `approval_status == 'APPROVED'`). A corrupted file or an attacker could modify the maximum spend ceiling from `$2.00` to `$20.00` or change the target pod ID without invalidating the document.
- **Reproduction**: In `test_defect_1_unauthenticated_json_vs_ed25519_signature`, a session authorization payload was modified in memory (spending cap raised to `$20.00`). The unhardened check accepted the modified dictionary.
- **Hardened Solution**: `CryptographicAuthorizer` signs canonical sorted JSON bytes using standard Ed25519 asymmetric cryptography. When the modified document is verified against the public key, signature verification fails definitively (`Ed25519 cryptographic signature verification FAILED`). Single-use nonces prevent replay attacks.

---

### Defect 2: Intermediate Checkpoint Sync Risked Overwrite and Data Truncation
- **Pre-Hardening Flaw**: The intermediate checkpoint downloader directly wrote to the local dataset file path. If a remote sync occurred during a partial runner write or suffered network interruption, the local file was truncated, destroying valid historical records.
- **Reproduction**: In `test_defect_2_checkpoint_overwrite_vs_monotonic_transaction`, an existing checkpoint of 2 records was subjected to an incoming candidate with only 1 record (simulating network truncation).
- **Hardened Solution**: `TransactionalCheckpointManager` stages incoming data into a `.candidate.tmp` file, executes full JSON syntax and schema validation across all 20 required metadata fields, checks for duplicate request IDs, and enforces strict monotonicity. Candidates containing fewer records than the existing promoted checkpoint are rejected with `Regression rejection`, leaving the active checkpoint and `.bak` file completely intact.

---

### Defect 3: Remote Deployment Verification Assumed Script Existence
- **Pre-Hardening Flaw**: The orchestrator assumed remote `git clone` or SFTP deployment succeeded and immediately invoked `nohup python3 remote_experiment_runner.py`. If a script was missing, had an invalid SHA-256 hash, or disk space was exhausted, the pod ran blindly.
- **Reproduction**: In `test_defect_3_missing_deployment_verification`, remote `sha256sum` checks returned a mismatched hash for `remote_experiment_runner.py`.
- **Hardened Solution**: `RemoteDeploymentVerifier` executes preflight inspection verifying the remote Python interpreter, ensuring at least 20 GB free disk space on `/workspace`, and validating that both `primary_100_manifest.json` and `remote_experiment_runner.py` match approved cryptographic hashes prior to launch.

---

### Defect 4: Controller Resume Risked Duplicate Remote Processes
- **Pre-Hardening Flaw**: Invoking `--resume` simply re-ran the detached launch script if local state indicated an unfinished run, risking multiple competing instances running on the same GPU.
- **Reproduction**: In `test_defect_4_duplicate_remote_inference_vs_reconciler`, the system reconciled against an existing remote record with active PID 54321.
- **Hardened Solution**: `SafeResumeReconciler` parses the remote execution record, checks `ps -p <pid>` on the pod, verifies the running command line, and inspects heartbeat freshness. If the process is active, it returns `REATTACH` without launching a new process; if confirmed dead, it permits `SAFE_RESTART`; if an unknown process exists, it executes `HALT_FOR_OPERATOR`.

---

### Defect 5: Termination Receipts Delayed by Blocking Network Calls
- **Pre-Hardening Flaw**: During emergency or normal termination, the orchestrator attempted to retrieve final dataset files via SFTP before persisting the termination receipt. An SFTP socket hang delayed or prevented writing the termination receipt.
- **Reproduction**: In `test_defect_5_termination_receipt_ordering`, an exception was injected into the SFTP sync call during shutdown.
- **Hardened Solution**: The shutdown sequence was reordered to write and fsync `termination_receipt_{experiment_id}.json` to local disk immediately upon dispatching provider termination, ensuring durable proof of termination even if downstream retrieval fails.

---

### Defect 6: Synchronous Network Operations Blocked Financial Supervision
- **Pre-Hardening Flaw**: Cost checks ran inside the same orchestrator thread performing blocking SSH/SFTP calls. A network timeout would stall cost calculation and shutdown triggers.
- **Reproduction**: In `test_defect_6_watchdog_independent_process_supervision`, a network stall was simulated while elapsed time continued.
- **Hardened Solution**: `IndependentFinancialWatchdog` runs in a separate process with its own monotonic clock, queries RunPod GraphQL control plane directly, detects stale controller heartbeats ($> 120$s), and dispatches pod destruction directly when spend breaches `$1.65` USD.

---

### Defect 7: Uncalibrated Launch Risked Rapid Budget Overrun
- **Pre-Hardening Flaw**: The system permitted launching the full 400-request experiment immediately without empirically establishing GPU throughput or token latency on the actual hardware.
- **Reproduction**: In `test_defect_7_physical_calibration_limits`, the configuration bounds were verified.
- **Hardened Solution**: Implemented a standalone 10-request physical calibration configuration covering GSM8K Problem 0 across all 4 conditions and 6 diverse problems, strictly isolating calibration from full production runs.
