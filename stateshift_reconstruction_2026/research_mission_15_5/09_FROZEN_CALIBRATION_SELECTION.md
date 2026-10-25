# 09 Frozen Calibration Selection Specification

**Module:** `research_mission_15_5/calibration/calibration_config.py`  
**Parent Manifest:** `research_mission_15_5/manifests/primary_100_manifest.json`  
**Parent Manifest SHA-256:** `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`

---

## 1. Frozen 10-Request Calibration Subset
The calibration subset represents exactly 10 requests selected deterministically across 3 distinct problems and 4 experimental conditions.

| Request ID | Problem ID | Condition Code | Description | Gold Answer |
| :--- | :--- | :---: | :--- | :--- |
| `primary_100_req_0001` | `math500_001` | A | Base Baseline | `4` |
| `primary_100_req_0002` | `math500_001` | B | Forced Error Injection | `4` |
| `primary_100_req_0003` | `math500_001` | C | State-Only Conditioning | `4` |
| `primary_100_req_0004` | `math500_001` | D | State + Reflection Intervention | `4` |
| `primary_100_req_0005` | `math500_012` | A | Base Baseline | `12` |
| `primary_100_req_0006` | `math500_012` | B | Forced Error Injection | `12` |
| `primary_100_req_0007` | `math500_012` | C | State-Only Conditioning | `12` |
| `primary_100_req_0008` | `math500_012` | D | State + Reflection Intervention | `12` |
| `primary_100_req_0009` | `math500_023` | A | Base Baseline | `\frac{1}{2}` |
| `primary_100_req_0010` | `math500_023` | B | Forced Error Injection | `\frac{1}{2}` |

## 2. Cryptographic Hashes
- **Calibration Subset Canonical JSON SHA-256:**  
  `91c57ea9f3e26045abb34a721c43bad38af49f9bb647037941f2c261b61adfec`
- **Integrity Rule:** The calibration loader verifies all 10 request IDs. If any ID is missing, modified, or out of order, execution aborts immediately without silent slicing.
