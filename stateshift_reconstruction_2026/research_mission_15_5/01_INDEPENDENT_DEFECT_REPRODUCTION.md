# 01 Independent Defect Reproduction Audit

**Target:** Forensic verification of the 7 launch blockers inherited from Mission 15.4.  
**Suite:** `research_mission_15_5/tests/test_blocker_reproductions.py` (7/7 Passed).

---

## 1. Blocker 1: In-Process Synchronous Watchdog
- **Vulnerability:** Mission 15.4 instantiated `IndependentFinancialWatchdog` as a standard Python object within the controller process. If the controller blocked on network I/O, hung in a GIL lock, or received `SIGKILL`, the watchdog ceased execution simultaneously.
- **Reproduction:** Instantiating `IndependentFinancialWatchdog` in Mission 15.4 confirmed `os.getpid() == controller_pid`. No independent OS thread or process existed.

## 2. Blocker 2: Embedded Test Signing Key Default Trust
- **Vulnerability:** `CryptographicAuthorizer` in Mission 15.4 contained a hardcoded fallback test key seed (`b"stateshift_test_signing_key_32b!"`). If no external key was provided, it defaulted to this test key, allowing test authorizations to validate in paid execution modes.
- **Reproduction:** Creating a signed authorization with the embedded test key in Mission 15.4 successfully authorized a simulated production run without error.

## 3. Blocker 3: Calibration Unbound to Pod ID
- **Vulnerability:** In Mission 15.4, `CryptographicAuthorizer.create_signed_authorization` accepted `pod_id=None` when `mode="CALIBRATION"`. A signed calibration authorization could be reused across multiple pods or arbitrary machines.
- **Reproduction:** Creating a calibration authorization with `pod_id=None` passed schema and cryptographic validation in Mission 15.4.

## 4. Blocker 4: Simulation Flags Accepted in Paid Modes
- **Vulnerability:** Mission 15.4 parsed `--simulate-*` flags without validating mutually exclusive execution modes. An operator could pass `--mode PRODUCTION --simulate-records 10`, causing simulated records to be treated as real production outputs.
- **Reproduction:** Invoking the runner with `--mode CALIBRATION --simulate-records 10` proceeded past CLI parsing and initialized cloud transport.

## 5. Blocker 5: Calibration Budget Threshold Disconnect
- **Vulnerability:** The controller and watchdog permitted overriding budget limits independently from the signed authorization. A calibration run could be launched with a $2.00 ceiling instead of the mandatory $0.35 calibration cap and $0.25 emergency trigger.
- **Reproduction:** Passing `--max-cost-usd 2.00` in calibration mode was accepted by the controller without authorization rejection.

## 6. Blocker 6: Provider API Errors Treated as Confirmation
- **Vulnerability:** In `RunPodTransportV2`, HTTP timeouts, GraphQL 500 errors, or connection resets during pod status checks returned `is_terminated = True` if the pod was unreachable, falsely declaring confirmed destruction.
- **Reproduction:** Simulating an HTTP 500 internal server error during `verify_pod_terminated()` returned `True`, masking an active running pod.

## 7. Blocker 7: Calibration Slicing Fallback
- **Vulnerability:** When calibration mode was requested, Mission 15.4 performed a naive slice `manifest["requests"][:10]`. If requests were reordered, missing, or corrupted, the system silently proceeded with whatever 10 requests were present.
- **Reproduction:** Supplying a manifest with missing request IDs caused the runner to select arbitrary requests without cryptographic validation of the calibration subset hash.
