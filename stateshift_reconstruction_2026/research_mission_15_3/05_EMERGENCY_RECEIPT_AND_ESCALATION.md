# StateShift Mission 15.3: Emergency Receipt Ordering & Durable Escalation

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_3/05_EMERGENCY_RECEIPT_AND_ESCALATION.md`  

---

## 1. Strict Emergency Execution Order

In Mission 15.3, emergency shutdown strictly adheres to the following chronological execution order:

1. **Step 1: Emergency Event Persisted**: Controller logs event to `cost_controller_audit.jsonl` with ISO UTC timestamp.
2. **Step 2: Provider Termination Dispatched**: Runner calls `self.transport.terminate_pod(self.pod_id)` immediately via HTTPS GraphQL control plane.
3. **Step 3: Provider Response Persisted**: Controller updates state to `DISPATCHED` with mutation response.
4. **Step 4: Destruction Verification Commences**: Runner queries `verify_pod_terminated(pod_id)`.
5. **Step 5: Verification Results Persisted**:
   - If confirmed destroyed: writes `termination_receipt_<exp_id>.json` with `confirmed_by_provider=True`.
   - If unconfirmed: writes `termination_receipt_<exp_id>.json` with `confirmed_by_provider=False`.
6. **Step 6: Optional Safe Data Retrieval**: SFTP sync is attempted only if socket is alive and within a bounded timeout. Under no circumstances can SFTP block or delay Steps 1–5.
7. **Step 7: Final Status Reported & Escalated**:
   - `TERMINATION_CONFIRMED`: Safe termination complete.
   - `TERMINATION_UNCONFIRMED`: Durable escalation alerts generated.

---

## 2. Durable Escalation Architecture (`DurableEscalationManager`)

When provider destruction cannot be confirmed after all allocated retries ($N=3$), the system refuses to report success. Instead, it activates the `DurableEscalationManager`:

### A. Structured Machine-Readable Alert
File: `data/primary_run/unresolved_pod_<pod_id>.json`
```json
{
  "alert_type": "POD_TERMINATION_UNCONFIRMED",
  "pod_id": "xydg2t4rzrx71d",
  "reason": "Budget limit $1.65 breached | Balance $7.34 <= floor $7.35",
  "attempts": 3,
  "last_known_status": "UNCONFIRMED",
  "error_message": "Provider failed to confirm destruction",
  "timestamp_utc": 1774329600.0,
  "iso_time": "2026-03-24T00:00:00Z",
  "resolved": false
}
```

### B. Prominent Operator Alert & Actionable Guide
File: `data/primary_run/CRITICAL_ALERT_POD_<pod_id>.txt`
Emits human-readable instructions detailing:
1. RunPod Web Console URL: `https://www.runpod.io/console/pods`
2. RunPod CLI Command: `runpodctl remove pod <pod_id>`
3. Direct GraphQL curl command with `$RUNPOD_API_KEY`.

### C. Rehydration on Restart
Upon supervisor restart, `get_unresolved_escalations()` scans for unresolved records and rechecks their status before any new cloud action can be scheduled.
