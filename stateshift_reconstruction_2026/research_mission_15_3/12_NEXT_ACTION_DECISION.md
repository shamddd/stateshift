# StateShift Mission 15.3: Next Action Decision & Authorization Request Protocol

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_3/12_NEXT_ACTION_DECISION.md`  

---

## 1. Recommendation to Principal Investigator

The research and systems engineering team formally recommends requesting **PI Authorization for Stage B Cloud Execution** on RunPod.

All software, transport, watchdog, scheduling, verification, and escalation components are certified, tested, and frozen.

---

## 2. Mandatory Protocol for Next Steps

1. **Do NOT Create Pod Automatically**:
   - The agent must not provision or start any cloud instance autonomously.
2. **Obtain Explicit PI Approval**:
   - The Principal Investigator must review the financial baseline and issue a signed session authorization document binding the execution to a specific pod ID and budget limit (\$2.00).
3. **Execute Preflight First**:
   - Once the pod is provisioned by the PI, execute `--mode PREFLIGHT` to verify credentials, SSH connectivity, and GraphQL API permissions without starting GPU compute.
4. **Execute 10-Request Calibration**:
   - Verify empirical throughput (tokens/second) on the live RTX 4090 before committing to the full 400 rollouts.
5. **Execute Full Replication Run**:
   - Launch `stateshift_production_runner.py` with continuous financial watchdog supervision.
