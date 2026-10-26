# Research Mission 15.1: Crash Consistency and Data Preservation Audit

**Principal Investigator**: Sham Satish Thakare  
**Repository**: `github.com/shamddd/stateshift`  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_1/05_CRASH_CONSISTENCY_AUDIT.md`  
**Date**: October 25, 2026  
**Auditor**: Systems Reliability & Filesystem Integrity Specialist  

---

## 1. Executive Summary

A critical weakness of ephemeral cloud GPU inference is that network drops, local controller crashes, or disk-full events can corrupt partially synchronized files. If an in-progress transfer directly overwrites the local output file, a sudden crash destroys the only surviving copy of previously synchronized rollouts.

In `RobustCloudOrchestratorV8` and `IndependentDatasetVerifier`, we audited and enforced strict **crash-consistent, atomic write protocols** across all filesystem operations.

### Non-Negotiable Invariant:
**The last valid local dataset snapshot is NEVER overwritten by an invalid, partial, or corrupted transfer.**

---

## 2. The Atomic Snapshot Pipeline

Every synchronization step adheres to a 5-stage transactional pipeline:

```
[Remote SFTP Host]
         │ (Fetch via Paramiko)
         ▼
1. [destination.tmp] (Written to unique temporary staging path)
         │
         ├─► Step 2: Line-by-line JSON parse verification
         ├─► Step 3: Schema completeness check
         │
  [Failure / Disk Full?] ──► YES ──► Unlink .tmp; Prior destination untouched
         │
         NO
         ▼
4. [os.fsync(fileno())] (Explicit flush of OS dirty pages to non-volatile storage)
         │
         ▼
5. [os.replace(tmp, destination)] (POSIX-guaranteed atomic inode replacement)
```

### Analysis of Failure Modes:
1. **Interrupted Write / Network Drop Mid-Transfer**: Paramiko writes strictly to `.tmp`. If the connection is severed, only `.tmp` contains truncated bytes. The destination file `primary_7b_generations.jsonl` remains 100% intact.
2. **Local Controller Crash (`SIGKILL`)**: If the orchestrator process is killed at any instant during transfer, either:
   - Before `os.replace`: The previous snapshot is intact.
   - After `os.replace`: The new complete snapshot is intact.
   There is zero intermediate window where the file is corrupted.
3. **Disk-Full Error (`ENOSPC`)**: Verified in Scenario 12: when `fetch_file` triggers an `OSError(28, "No space left on device")`, the orchestrator catches the exception, aborts the sync, cleans up `.tmp`, and leaves the existing 100-record snapshot completely undamaged.
4. **Local Host Power Failure**: Calling `os.fsync(fileno())` prior to `os.replace` guarantees that data bytes hit physical storage before the directory metadata pointer is swapped.

---

## 3. Persistent State Rehydration

When `RobustCloudOrchestratorV8` initializes, it writes and updates `orchestrator_state_<exp_id>.json` using the same atomic `.tmp` -> `os.fsync` -> `os.replace` pattern.

If the local machine reboots or the orchestrator process restarts while the remote GPU job is running:
1. The new orchestrator instance re-reads `orchestrator_state_<exp_id>.json`.
2. It re-hydrates `remote_pid`, `manifest_sha256`, and `experiment_id`.
3. It reconnects to the running container and resumes incremental synchronization without re-running or duplicating rollouts (verified in Scenario 6).

---

## 4. Durability Assumptions & Limitations

1. **POSIX Compliance**: Atomicity of `os.replace` relies on a POSIX-compliant filesystem (APFS on macOS, ext4/xfs on Linux). It is supported in our research environment.
2. **Directory Fsync**: On Linux ext4 filesystems in strict writeback caching mode, directory-level sync (`os.fsync(dir_fd)`) is additionally supported where available.
3. **Container Ephemerality**: Container root storage on RunPod is non-durable across pod restarts. Therefore, local snapshotting every 30s is the primary line of defense.
