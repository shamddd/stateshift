# Phase 6: Termination Receipt Ordering Specification

**Implementation**: Embedded in `research_mission_15_4/runner/stateshift_production_runner_v10.py`  
**Test Suite**: `research_mission_15_4/tests/test_defect_reproductions.py` (Defect 5 Test Passing)  

### Inverted Shutdown Ordering
In previous missions, the shutdown handler attempted best-effort final dataset retrieval via SFTP before writing the termination receipt. Network socket drops or hangs resulted in missing or delayed receipts.

In Mission 15.4:
1. **Priority 1**: Immediately upon dispatching pod termination to the RunPod API, write `termination_receipt_{experiment_id}.json` to local disk with `fsync`.
2. **Priority 2**: Update local persistent state to `TERMINATION_REQUESTED` / `PROVIDER_TERMINATION_CONFIRMED`.
3. **Priority 3 (Optional & Non-Blocking)**: Attempt bounded final sync. If network stalls or errors occur, the termination receipt is already durable and immutable.
