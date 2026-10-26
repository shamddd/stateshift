# StateShift Research Mission 14 — Deliverable 01: Raw Data Recovery Audit

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Investigating Role**: Independent Forensic Recovery Auditor  
**Date of Audit**: October 25, 2026  
**Status**: **PARTIAL RECOVERY / SCIENTIFIC RETRACTION OF UNVERIFIABLE 143-ROLLOUT CLAIMS**  

---

## 1. Executive Forensic Declaration

In strict accordance with the Mission 14 Primary Directive:
> *"If the dataset cannot be recovered, explicitly declare the 7B scientific findings not independently reproducible. Do not reconstruct missing generations from aggregate reports. Do not generate synthetic replacements."*

**OFFICIAL AUDIT FINDING**:  
The primary 7B dataset file `primary_7b_results.jsonl` (intended to contain 400 rollouts, and reported in Mission 13 as having reached 143 rollouts) **was not retrieved to permanent local storage prior to pod destruction**. 

When the local orchestrator encountered a client-side socket read timeout (1,800 seconds) in `runner/orchestrator_mission13.py` at line 344, execution bypassed the SFTP retrieval step (lines 351–354) and jumped directly to the `finally:` cleanup block, which executed `runpod.terminate_pod('xydg2t4rzrx71d')`. Because the RunPod instance was created with ephemeral container storage (`volume_in_gb=0`), the 143 generated records located at `/workspace/stateshift/data/primary_7b_results.jsonl` were permanently erased upon container termination.

Consequently:
1. **The quantitative findings reported in Mission 13 based on the 143 rollouts (e.g., condition accuracies, repair rates, token counts) cannot be independently reproduced from raw local records and are officially declared UNVERIFIABLE.**
2. **We strictly refuse to reconstruct missing generations from aggregate summary tables or generate synthetic replacements.**
3. **Only 6 genuine 7B rollouts physically survive in local logs and verified artifacts.**

---

## 2. Forensic Investigation of Storage Locations

A comprehensive multi-location forensic sweep was conducted across all local research drives, git history, system logs, and process transcripts:

| Location Inspected | Search Scope | Outcome | Recovered Evidence |
| :--- | :--- | :--- | :--- |
| **Mission 13 Data Dir** | `research_mission_13/data/` | Found | `smoke_test_generations.jsonl` (4 complete records, 13,083 bytes) |
| **Git Commit History** | Commit `3e48c05` | Found | `data/smoke_test_generations.jsonl` committed; 0 primary records |
| **Git Working Tree / Stash** | Untracked / Stashed files | None | No uncommitted JSONL files found |
| **Host Temp Dirs** | `/tmp/*`, `/var/tmp/*` | None | Only code bundle tarball (`stateshift_m13_bundle.tar.gz`) found |
| **Process Task Logs** | `.system_generated/tasks/` | Found | `task-2427.log` (captured `primary_100_req_0131`)<br>`task-2436.log` (captured `primary_100_req_0143`) |
| **Orchestrator Log** | `logs/orchestration_live.log` | Found | Contains stdout traces for rollouts 1–4; 0 primary stdout traces |
| **Active Cloud Pod** | RunPod `xydg2t4rzrx71d` | Destroyed | Verified terminated; 0 active pods on account; cannot be reached |

---

## 3. Physical Inventory of Recovered Raw Records

Exactly **6 genuine 7B generation records** physically survive with verified cryptographic integrity:

### 3.1 Smoke Test Cohort (`recovered_smoke_test_generations.jsonl`)
- **File Path**: `research_mission_14/data/recovered_smoke_test_generations.jsonl`
- **File Size**: 13,083 bytes
- **SHA-256 Digest**: `7d3be0fd81afcd8832a05335e201902bfd97c1d0df1dc62f4f59ed70327364be`
- **Record Count**: 4 valid JSONL lines (100% complete four-condition matched block for `math500_001`):
  1. `primary_100_req_0001`: Condition A (Zero-Shot), 728 gen tokens, 39.9 tok/s, Answer: `p - q` (`VERIFIED_TRUE`).
  2. `primary_100_req_0002`: Condition D (Forced Restart), 553 gen tokens, 41.0 tok/s, Answer: `p - q` (`VERIFIED_TRUE`).
  3. `primary_100_req_0003`: Condition E (Explicit Repair), 549 gen tokens, 40.8 tok/s, Answer: `p - q` (`VERIFIED_TRUE`).
  4. `primary_100_req_0004`: Condition F (State Preserving), 558 gen tokens, 40.8 tok/s, Answer: `p - q` (`VERIFIED_TRUE`).

### 3.2 Live Forensic Log Traces (`recovered_live_traces.jsonl`)
- **File Path**: `research_mission_14/data/recovered_live_traces.jsonl`
- **File Size**: 3,745 bytes
- **SHA-256 Digest**: `53cac6a3106cbb17d8e0df5ea39c7daa0dea4a5e10e66613022e99953e63cac1`
- **Record Count**: 2 valid JSONL lines (captured during live SSH inspection tasks):
  1. `primary_100_req_0131`: Problem `math500_026`, Condition E, 465 gen tokens, 41.0 tok/s, Answer: `144` (`VERIFIED_TRUE`), Status: `RESTART_SUCCESS`.
  2. `primary_100_req_0143`: Problem `math500_061`, Condition E, 558 gen tokens, 41.2 tok/s, Answer: `-256` (`VERIFIED_TRUE`), Status: `RESTART_SUCCESS`.

---

## 4. Root Cause of Data Loss

The loss of the intermediate primary records (`primary_100_req_0005` through `primary_100_req_0142`) was caused by a critical software engineering defect in `runner/orchestrator_mission13.py`:

```python
# Flawed Architecture in Mission 13:
cmd = "python3 /workspace/stateshift/runner/cloud_experiment_runner.py ..."
# Blocking call with rigid 1800s timeout:
exit_code, _ = self.execute_remote_cmd(cmd, timeout=1800)  # Line 344

# SFTP retrieval was placed AFTER the blocking execution call:
sftp = self.ssh_client.open_sftp()
local_primary = os.path.join(repo_root, "data", "primary_7b_generations.jsonl")
sftp.get("/workspace/stateshift/data/primary_7b_results.jsonl", local_primary) # Line 351
sftp.close()
```

When Paramiko's socket read timeout occurred at 1,800 seconds, Python raised a `TimeoutError`, skipping lines 345–355 entirely. Control immediately transferred to the outer `finally:` block:
```python
finally:
    print("\nEnsuring cleanup and provider resource termination...")
    orch.terminate_pod_and_verify()  # Line 498
```
This destroyed the ephemeral container before any SFTP transfer could occur.

---

## 5. Corrective Measures & Next Steps

1. In Phase 2 and Phase 3, all statistical evaluations are strictly restricted to the 6 verified recovered records.
2. In Phase 6, `orchestrator_mission13.py` is completely re-engineered into an asynchronous detached execution architecture (`nohup` process, PID tracking, periodic SFTP incremental checkpoint synchronization, independent watchdog).
3. Under no circumstances will synthetic or extrapolated data be presented as genuine empirical observations.
