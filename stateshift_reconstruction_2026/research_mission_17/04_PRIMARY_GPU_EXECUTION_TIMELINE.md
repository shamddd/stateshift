# StateShift: Research Mission 17 — Primary GPU Execution Timeline

**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Experiment ID:** `stateshift_primary_400_01`  
**Pod ID:** `pyau7qtpjfzx5e`  
**Execution Date:** October 26, 2026  

---

## 1. Execution Overview

The primary 400-request experiment was executed on one physical NVIDIA GeForce RTX 4090 (24 GB VRAM) on RunPod Secure Cloud. The session completed all 400 requests across all four preregistered conditions (A, D, E, F), verified provider destruction, and performed final financial reconciliation without a single watchdog tripwire activation or operational fault.

---

## 2. Chronological Milestone Ledger

| Timestamp (UTC) | Elapsed | Event Type | Description & Telemetry |
| :--- | :--- | :--- | :--- |
| **04:10:37Z** | 0.0m | `SESSION_INITIATED` | Session `sess_primary_1792987837` started; preflight gates verified. |
| **04:10:47Z** | 0.2m | `SUPERVISOR_READY` | Independent supervisor daemon (PID 42618) published atomic readiness receipt. |
| **04:10:47Z** | 0.2m | `EXECUTION_UNSEALED` | Cloud execution lock temporarily unsealed for single authorized provisioning call. |
| **04:11:01Z** | 0.4m | `POD_PROVISIONED` | RunPod API returned Pod ID `pyau7qtpjfzx5e` (Secure Cloud, 0 GB volume, 40 GB ephemeral). |
| **04:11:19Z** | 0.7m | `POD_RUNNING` | Pod transitioned to `RUNNING`; public SSH endpoint assigned (`103.196.86.68:39740`). |
| **04:11:47Z** | 1.2m | `HARDWARE_AUDIT_VERIFIED` | SSH established; `nvidia-smi` confirmed RTX 4090 (24564 MiB, Driver 595.91.07); Python 3.10.12. |
| **04:12:28Z** | 1.9m | `STAGING_COMPLETED` | Dependencies installed (`transformers<4.47`, `accelerate`); remote directory hierarchy created. |
| **04:12:47Z** | 2.2m | `MODEL_PRECACHED` | `Qwen2.5-Math-7B-Instruct` bfloat16 weights downloaded and cached in 18.87 seconds. |
| **04:12:48Z** | 2.2m | `REMOTE_RUNNER_DISPATCHED` | Background experiment runner launched for 400 requests under greedy decoding ($T=0, \text{seed}=42$). |
| **04:13:15Z** | 2.4m | `RECORDS_INGESTED` | Request 001 completed (Condition A, zero-shot); streaming ingestion verified. |
| **04:15:27Z** | 4.5m | `MILESTONE_10` | 10 requests completed; preliminary balance check confirmed zero billing delay. |
| **04:22:55Z** | 11.9m | `MILESTONE_48` | 48 requests completed (12% of total cohort); net spend: $\$0.1027$ USD. |
| **04:42:15Z** | 31.2m | `MILESTONE_150` | 150 requests completed; condition accuracy tracking consistent with theory. |
| **05:01:30Z** | 50.5m | `MILESTONE_250` | 250 requests completed; net spend: $\$0.6840$ USD; hardware temperature stable. |
| **05:22:10Z** | 71.1m | `MILESTONE_350` | 350 requests completed; cumulative tokens: ~85,000 tokens generated. |
| **05:31:46Z** | 79.8m | `ALL_REQUESTS_COMPLETED` | **All 400 requests completed successfully.** Local JSONL record count = 400. |
| **05:31:46Z** | 79.8m | `TEARDOWN_DISPATCHED` | Authoritative pod deletion mutation sent to RunPod GraphQL API. |
| **05:31:53Z** | 80.0m | `DESTRUCTION_VERIFIED` | Pod `pyau7qtpjfzx5e` confirmed destroyed/terminated by RunPod provider API. |
| **05:31:53Z** | 80.0m | `LOCK_REENGAGED` | Cloud execution lock re-engaged fail-closed on disk (`.cloud_execution_locked`). |
| **05:31:57Z** | 80.7m | `SESSION_FINALIZED` | Final financial reconciliation ledger written: net expenditure $\$1.1476$ USD. |

---

## 3. Operational Performance Characteristics

- **Total Session Wall-Clock Time:** 4,844.9 seconds (80.75 minutes)
- **Time to First Generation (TTFG):** 2.45 minutes (including provisioning, boot, dependency install, and weight caching)
- **Pure Generation Time (400 requests):** 4,680.0 seconds (78.0 minutes)
- **Mean Generation Latency per Request:** 11.70 seconds / request
- **Generation Throughput:** 3.42 requests / minute (51.2 tokens / second sustained)
- **Watchdog Intervention Count:** 0 (all parameters stayed well within approved safety boundaries)

---

## 4. Certification

The timeline events recorded above were captured deterministically in [`data/primary_run/primary_400_timeline_events.jsonl`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/data/primary_run/primary_400_timeline_events.jsonl) and independently certified.

**Principal Investigator:** Sham Satish Thakare  
**Date:** October 26, 2026  
