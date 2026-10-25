# Phase 3: Transactional Checkpoint Preservation Specification

**Module**: `research_mission_15_4/checkpoint/transactional_checkpoint_manager.py`  
**Test Suite**: `research_mission_15_4/tests/test_transactional_checkpoint.py` (8 Tests Passing)  

### Architecture & Guarantees
1. **Isolated Ingestion**: Downloads and writes remote snapshots to `.candidate.tmp` with explicit `flush()` and `os.fsync()`.
2. **Schema & Provenance Validation**: Validates all 20 required metadata fields per record. Rejects simulated, mock, or synthetic tags.
3. **Monotonicity Enforcement**: Computes the valid record count in the candidate. If `candidate_count < promoted_count`, rejects immediately with `Regression rejection`, preventing network truncation from wiping valid data.
4. **Contradiction Detection**: Cross-references existing promoted records against candidate records. If a previously promoted request has conflicting prompt hashes, condition codes, or model outputs, candidate is rejected.
5. **Atomic Promotion & Rollback**: Promotes valid candidates via atomic POSIX rename (`os.replace`), backing up the previous valid version to `.bak`.
