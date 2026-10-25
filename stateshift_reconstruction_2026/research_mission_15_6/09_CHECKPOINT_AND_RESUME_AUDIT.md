# StateShift Mission 15.6: Checkpoint Transactionality & Safe Resume Audit

**Project:** StateShift Research Mission 15.6  
**Document:** `09_CHECKPOINT_AND_RESUME_AUDIT.md`  
**Subsystem:** `research_mission_15_6.checkpoint.transactional_checkpoint_manager`  
**Status:** Certified Monotonic & Atomically Protected  

---

## 1. Zero-Loss Transactional Checkpointing Design

StateShift employs a three-tier atomic staging architecture for checkpoint promotion:

```
[Remote Pod: output.jsonl]
           │
           │ (SFTP fetch with bounded 15s timeout)
           ▼
[Local Candidate: dataset.jsonl.candidate.tmp]
           │
           │ (Strict Record-by-Record Integrity Audit)
           ├─ All mandatory metadata keys present
           ├─ Valid greedy decoding parameters (temp=0.0, seed=42)
           ├─ Real model inference provenance & manifest hash
           ├─ Strictly monotonic record count (count >= current_count)
           ├─ Zero synthetic dry-run contamination
           ▼
[Local Staging: dataset.jsonl.staged.tmp]
           │
           │ (Atomic Kernel Rename: os.replace)
           ▼
[Local Authoritative Dataset: dataset.jsonl]
```

### Invariant Guarantees
1. **Monotonicity:** An update is rejected if the candidate file has fewer valid records than the already-promoted authoritative dataset.
2. **Atomicity:** File promotions are executed exclusively via `os.replace()`, guaranteeing POSIX atomicity. At no point is the dataset file partially written or corrupt.
3. **Rollback Resilience:** If remote sync fails, network drops, or candidate is corrupt, promotion is deferred and the existing authoritative dataset remains 100% intact.

---

## 2. Safe Resume Mechanics

When an interrupted run is resumed via `--resume`:
1. **Checkpoint Recovery:** `TransactionalCheckpointManager` inspects the local authoritative dataset.
2. **Reconciliation:**
   - Reads all existing valid records into memory.
   - Computes set of already-completed `request_id`s.
   - Calculates remaining requests required to reach the target.
3. **No Duplicate Execution:**
   - Pre-populates scheduler and inference runner with completed IDs.
   - Remote inference runner skips completed request IDs, preventing duplicate GPU computation.
4. **No Double Counting:**
   - Sync logic reconciles remote rollouts against local records via unique `request_id` deduplication.

---

## 3. Test Verification Traceability

- **`test_scenario_N_valid_checkpoint_promoted`**: Verifies that 10 generated records are promoted to disk atomically and match expectations.
- **`test_scenario_O_corrupted_checkpoint_rejected`**: Injects corrupt JSONL candidate; verifies that promotion is safely deferred and existing records are preserved.
- **`test_scenario_P_safe_resume_reattach`**: Exercises resume workflow; verifies clean reattachment without duplicate generation or error.
