# 07 Provider Response Classification & State Machine

**Module:** `research_mission_15_5/supervision/independent_financial_watchdog.py`  
**Tests:** `test_blocker_6_provider_response_classification`, `test_scenario_G_provider_api_failure_unconfirmed`, `test_scenario_N_ambiguous_provider_response`.

---

## 1. Provider Response Taxonomy
To prevent catastrophic runaway billing caused by masking unconfirmed terminations, all RunPod API responses are classified strictly into three distinct states:
1. `CONFIRMED_TERMINATED`: The provider explicitly confirms the pod no longer exists.
   - GraphQL `pod(id: $id)` returns `null` or empty data.
   - HTTP response status is 404 (Not Found).
2. `CONFIRMED_ACTIVE`: The provider explicitly confirms the pod is running or allocated.
   - GraphQL returns a pod record with `desiredStatus: "RUNNING"` or valid uptime.
3. `API_ERROR` / `UNCONFIRMED`: Any ambiguous, transient, or failed response.
   - HTTP 500, 502, 503, 504.
   - HTTP 401, 403 (Credential failure).
   - Network timeout, connection reset, SSL handshake failure.
   - Malformed JSON or GraphQL error payloads.
   - `desiredStatus: "STOPPED"` (Storage and GPU reservation charges may still accrue).

## 2. Escalation Invariant
- **Rule:** A pod is NEVER marked terminated upon `API_ERROR` or `UNCONFIRMED`.
- **Action:** The system retries with exponential backoff up to 3 attempts, logs a critical unconfirmed alert to `termination_alerts/`, and keeps the watchdog active.
