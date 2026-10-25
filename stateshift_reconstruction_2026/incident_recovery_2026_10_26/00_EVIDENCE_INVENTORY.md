# StateShift Incident Recovery — Evidence Inventory
**Project**: StateShift (NeurIPS 2027 / TMLR)  
**Principal Investigator**: Sham Satish Thakare  
**Incident Date**: October 25–26, 2026  
**Recovery Directory**: `incident_recovery_2026_10_26/`  
**Execution Mode**: STRICTLY LOCAL AND OFFLINE ($0.00 Authorized Spend)  

---

## 1. Executive Summary

This inventory catalogs all authentic forensic artifacts, runtime logs, execution state files, cryptographic receipts, manifests, and codebase components associated with the October 25–26, 2026 financial threshold overrun on RunPod. Every file is documented with its relative repository path, exact byte size, SHA-256 digest, filesystem timestamp (UTC and IST), forensic classification, and sensitivity confirmation.

All files are preserved in place without modification to maintain chain of custody and reproducibility.

---

## 2. Complete Forensic File Catalog

| # | Relative Path | Size (Bytes) | SHA-256 Hash | Timestamp (UTC) | Timestamp (IST) | Evidence Category | Sensitivity Check |
|---|---------------|--------------|--------------|-----------------|-----------------|-------------------|-------------------|
| 1 | `incident_recovery_2026_10_26/evidence/EMERGENCY_SHUTDOWN_INCIDENT_REPORT.md` | 9,588 | `97b0a78b7f3e281c9abe0ac21a65352f3bb163e87f4b493ffe6d14480d9cbe2e` | 2026-10-25 23:37:25 | 2026-10-26 05:07:25 | Incident Report | Sanitized (No Keys) |
| 2 | `incident_recovery_2026_10_26/evidence/execute_physical_calibration.py` | 17,506 | `0ab57935e8d9f4f8b2400e724ce7699f76fdf1f28775e9eb0742862bc9f6f5c9` | 2026-10-25 23:37:25 | 2026-10-26 05:07:25 | Orchestration Script | Reads from `~/.env` (No Hardcoded Secrets) |
| 3 | `incident_recovery_2026_10_26/evidence/task-4934.log` | 1,426 | `8a969b0206693cafccce5d08ef4871e154371c9d474f57d68452cba414a0f2af` | 2026-10-25 23:37:25 | 2026-10-26 05:07:25 | OS Execution Log | Sanitized |
| 4 | `runpod_calibration/calibration_reconciliation_raw.json` | 764 | `16c27fc0de2896f65a888fbaf3eace886cb4d1d61e5b0bd8cab0b47c787c72fd` | 2026-10-25 14:41:18 | 2026-10-25 20:11:18 | Financial Reconciliation | Sanitized |
| 5 | `runpod_calibration/00_PRE_SPEND_READINESS.md` | 7,577 | `47c9954206ee1ebd61cc8b44dd5612452b26c0a375df79926db7044c13e49043` | 2026-10-25 13:04:50 | 2026-10-25 18:34:50 | Pre-Spend Verification | Sanitized |
| 6 | `data/primary_run/cost_controller_audit.jsonl` | 1,818 | `c3a026e7a5e59d17747be66f0f7870526568979eb4838edb33a85c1e88a78964` | 2026-10-25 14:40:35 | 2026-10-25 20:10:35 | Cost Controller Audit | Sanitized |
| 7 | `data/primary_run/operator_pubkey.txt` | 44 | `97582a0357e5dcc28d1d88bf5452bffd2649cef5babd70485614db7f9189cae0` | 2026-10-25 14:40:33 | 2026-10-25 20:10:33 | Cryptographic Public Key | Ed25519 Public Key Only |
| 8 | `data/primary_run/session_auth.json` | 843 | `77d34a92fd81186e163254eec39d53725c9cff4cc68dfa14e65af1b38bfc2b0b` | 2026-10-25 14:40:33 | 2026-10-25 20:10:33 | Signed Authorization | Sanitized (Signature Only) |
| 9 | `data/primary_run/used_nonces.json` | 185 | `4c5301b50d258e0c0045b0de11ac336089cf43e4adc1b314193ba68ecf076607` | 2026-10-25 14:40:33 | 2026-10-25 20:10:33 | Anti-Replay Nonce Store | Sanitized |
| 10 | `data/primary_run/runner_state_stateshift-calibration-10.json` | 478 | `dd592540e4aaca0293a4c7b05ddaffebdeba5bd5b001ede4046cf7f5cc6f720b` | 2026-10-25 14:40:43 | 2026-10-25 20:10:43 | Runner Runtime State | Sanitized |
| 11 | `data/primary_run/shutdown_state_stateshift-calibration-10.json` | 259 | `22fbd4e860c486ba29cecd10d3649cf2f24768aeacb8c6cb2c6be6d21ec4f7f7` | 2026-10-25 13:59:15 | 2026-10-25 19:29:15 | Shutdown Controller State | Sanitized |
| 12 | `data/primary_run/termination_receipt_stateshift-calibration-10.json` | 321 | `0d3abaa801b26a3870014845abc10f1e969dce00bca5a0120bc70cc8dbe67184` | 2026-10-25 13:59:19 | 2026-10-25 19:29:19 | Termination Receipt | Sanitized |
| 13 | `data/primary_run/watchdog/watchdog_state_stateshift-calibration-10.json` | 534 | `108efe43d12211ec7de4e635672398c9c7f086bbbf14d893feed3c197f0222e2` | 2026-10-25 14:41:18 | 2026-10-25 20:11:18 | Watchdog Telemetry | Sanitized |
| 14 | `data/primary_run/watchdog/watchdog_termination_receipt_stateshift-calibration-10.json` | 448 | `9d8e0447cf6b306a7402d47ed402dd0b667be378dc8c2483966369fac5c636e1` | 2026-10-25 14:41:18 | 2026-10-25 20:11:18 | Watchdog Termination Receipt | Sanitized |
| 15 | `data/primary_run/watchdog/watchdog_heartbeat_stateshift-calibration-10.json` | 273 | `075daa833cea3343af37900ab81847c1f2bf2c9c583b40e7d0fea45823a1adec` | 2026-10-25 14:41:16 | 2026-10-25 20:11:16 | Watchdog Heartbeat | Sanitized |
| 16 | `data/primary_run/watchdog/watchdog_readiness_stateshift-calibration-10_exec_1792937837.json` | 517 | `c1323334b95871eb2382eabe42bdc313b3633683246a8ebff726a9a77358acb6` | 2026-10-25 14:17:19 | 2026-10-25 19:47:19 | Watchdog Readiness (Attempt 1) | Sanitized |
| 17 | `data/primary_run/watchdog/watchdog_readiness_stateshift-calibration-10_exec_1792938318.json` | 519 | `a7329eb6389b685120cfb90143486ce167c1dc97020819d0cc340454f6097a7c` | 2026-10-25 14:25:21 | 2026-10-25 19:55:21 | Watchdog Readiness (Attempt 2) | Sanitized |
| 18 | `data/primary_run/watchdog/watchdog_readiness_stateshift-calibration-10_exec_1792939038.json` | 517 | `8dc5d243686e1a1188eec79dbbd9f9cc507ce9e287e2ee2ac01c4dea32826ebd` | 2026-10-25 14:37:20 | 2026-10-25 20:07:20 | Watchdog Readiness (Attempt 3) | Sanitized |
| 19 | `data/primary_run/watchdog/watchdog_readiness_stateshift-calibration-10_exec_1792939233.json` | 517 | `b430e802069778bfacc7198ea6071b2791e374e71e1a01a0314d856e8727f8c5` | 2026-10-25 14:40:35 | 2026-10-25 20:10:35 | Watchdog Readiness (Attempt 4) | Sanitized |
| 20 | `data/primary_run/watchdog/watchdog_readiness_stateshift-calibration-10_test_session.json` | 505 | `3a6c066609a1045fa0093b35426ab354c5bc787b6edf3858a79ecc2ecab9f23f` | 2026-10-25 14:11:34 | 2026-10-25 19:41:34 | Watchdog Readiness (Test) | Sanitized |
| 21 | `research_mission_15_6/manifests/calibration_10_manifest.json` | 13,662 | `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6` | 2026-10-25 11:43:09 | 2026-10-25 17:13:09 | Scientific Calibration Manifest | Sanitized |
| 22 | `research_mission_15_6/manifests/primary_100_manifest.json` | 569,153 | `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` | 2026-10-25 11:43:09 | 2026-10-25 17:13:09 | Scientific Primary Manifest | Sanitized |
| 23 | `research_mission_15_6/runner/remote_experiment_runner.py` | 15,277 | `bf168ee13e87d83c3397eac1f3b3d2743119bfa28cf9d3f626b7e4333e872e57` | 2026-10-25 14:35:03 | 2026-10-25 20:05:03 | Remote Pod Runner | Sanitized |
| 24 | `research_mission_15_6/runner/stateshift_launch.py` | 10,198 | `201138442df489a27af404fdd89096523184193f0575ee80b51d166f3fe61e8f` | 2026-10-25 12:05:41 | 2026-10-25 17:35:41 | Launch Orchestrator | Sanitized |
| 25 | `research_mission_15_6/runner/stateshift_production_runner_v10.py` | 49,711 | `8f1edc9fe5771aac2b4a747b20718ff757a2ed1dc8d872f5342741328ca05339` | 2026-10-25 12:44:50 | 2026-10-25 18:14:50 | Master Production Runner | Sanitized |
| 26 | `research_mission_15_6/supervision/independent_financial_watchdog.py` | 36,053 | `efb9351fe316330a57e0ced6397fc5aede1fa03b4abcb9d91e6d67cf8ee5c17a` | 2026-10-25 14:10:55 | 2026-10-25 19:40:55 | Independent Financial Watchdog | Sanitized |
| 27 | `research_mission_15_6/transport/runpod_transport_v2.py` | 11,526 | `3a6d6fc3a1845aaf8db96f4d609d322870d250139157b619bcffd5173e44b9cc` | 2026-10-25 14:41:48 | 2026-10-25 20:11:48 | RunPod Transport Layer | Sanitized |
| 28 | `research_mission_15_6/deployment/remote_deployment_verifier.py` | 7,105 | `08686b8e204bb0e441879e6491eb79dd53a45c5ed4b8f911d8793ac674b3dd63` | 2026-10-25 14:38:30 | 2026-10-25 20:08:30 | Remote Deployment Verifier | Sanitized |
| 29 | `research_mission_15_6/auth/session_authorizer_v2.py` | 11,988 | `bad83e8d601a3437e3b41e411f23ea5dfa8c04424ee500c9c8e19e53d8be1b70` | 2026-10-25 11:43:22 | 2026-10-25 17:13:22 | Cryptographic Authorizer | Sanitized |
| 30 | `research_mission_15_6/calibration/calibration_config.py` | 5,603 | `23510c1f78d38f91cfc63ae821566126d2a7557d08dd590de3469d9482fc7715` | 2026-10-25 12:00:56 | 2026-10-25 17:30:56 | Calibration Configuration | Sanitized |

---

## 3. Evidence Categories & Roles

1. **Incident Reports & Physical Process Logs** (`#1 - #3`):
   - Contain the real-time execution console stream (`task-4934.log`) showing the exact hanging point at model pre-caching over SSH.
   - Preserves the initial emergency shutdown incident report detailing the financial violation.
2. **Authoritative Financial Reconciliations** (`#4, #6`):
   - Contain the balance snapshot and cost controller event ledger documenting session initialization and thresholds.
3. **Cryptographic Identity & Authorization** (`#7 - #9`):
   - Contain the Ed25519 public key, session authorization certificate, and anti-replay nonce tracking.
4. **Watchdog Telemetry & State Ledgers** (`#10 - #20`):
   - Records the heartbeat signals, readiness certificates for attempts 1 through 4, and the final termination receipts.
5. **Frozen Scientific Manifests** (`#21 - #22`):
   - Invariant source of truth for the 10-request calibration and 400-request primary benchmark. Both SHA-256 hashes are verified identical to the NeurIPS 2027 protocol.
6. **Execution Pipeline Codebase** (`#23 - #30`):
   - Frozen snapshot of the production deployment, runner, transport, and supervision modules at the time of the incident.
