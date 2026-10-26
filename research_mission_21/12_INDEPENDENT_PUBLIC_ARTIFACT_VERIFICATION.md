# Phase M: Independent Public Artifact Verification

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training
**Principal Investigator**: Sham Satish Thakare
**Date & Time**: 2026-10-26T17:29:00+05:30
**Repository**: `https://github.com/shamddd/stateshift`

---

## 1. Public HTTPS Raw Retrieval Audit

To guarantee that research files are genuinely accessible to external researchers without requiring GitHub login credentials or API keys, each core artifact was downloaded directly from GitHub's raw CDN endpoint (`https://raw.githubusercontent.com/shamddd/stateshift/main/...`):

| Artifact Path | HTTP Status | Downloaded Size | Computed SHA-256 Checksum | Match Status | Verified Contents |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `data/study1/controlled_endpoint_outcomes.csv` | **200 OK** | 2,366,349 B | `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139` | **EXACT MATCH** | 29,057 lines (header + 29,056 rows) |
| `data/study2/stateshift_primary_400_generations.jsonl` | **200 OK** | 898,204 B | `bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2` | **EXACT MATCH** | 400 valid JSON records |
| `data/study2/final_verified_outcomes.csv` | **200 OK** | 7,998 B | `19a328a95dd25ec326fe824361386cc0ddf731f2bf1c392253be0aa19c2385ba` | **EXACT MATCH** | 101 lines (header + 100 problem pairs) |
| `paper/source/STATESHIFT_ARXIV_RELEASE_SOURCE.zip` | **200 OK** | 797,847 B | `2706cc14ad3f8451eefbd95b68ca316cb32714d9459d676b58414baad65b4470` | **EXACT MATCH** | Valid ZIP archive with 13 files |
| `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf` | **200 OK** | 197,845 B | `11ea41724458f338c23178044ce4a64b58e72b059632eb518df981329a67a216` | **VERIFIED** | Valid PDF binary (Header: `%PDF-1.5`) |
| `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex` | **200 OK** | 25,606 B | `d8c32ec8d80f8373b5da44bb5b67487293e5066a7b3db20c8db832c3f8e43e2e` | **VERIFIED** | Complete compilable LaTeX source |
| `README.md` | **200 OK** | 10,158 B | `58572b8d5a1050ea80c10f3ec1e21b72b810fe813ebec059d08e45873995aa42` | **VERIFIED** | Canonical public documentation |
| `experiments/study1_checkpoint_lineage/reproduce_study1.py` | **200 OK** | 3,375 B | `a796b3ffb916f1997d8df9325ec88a0e98031db5310d57e84a51e604d50e8201` | **VERIFIED** | Python 3 replication script |
| `experiments/study2_reasoning_recovery/reproduce_study2.py` | **200 OK** | 4,615 B | `c8742ca96b5c7776b7e5108b3e839e01fb33c24b9148d88b43f07a419c836934` | **VERIFIED** | Python 3 replication script |
| `experiments/study2_reasoning_recovery/exact_power_analysis.py` | **200 OK** | 4,214 B | `617b076ad85f401f8e8111e0eb7645cf45c71d64380b5fa8ab1a1a681ff5a43b` | **VERIFIED** | Discrete McNemar power engine |

---

## 2. Integrity and Format Assertions

1. **PDF Header**: The downloaded PDF starts with the standard magic byte sequence `%PDF-1.5` and ends with `%%EOF`.
2. **ZIP Archive**: Decompression of the downloaded ZIP archive using Python's `zipfile` module succeeded with 0 CRC errors, unpacking 1 TeX file, 1 Bib file, 1 README file, and 10 figure files.
3. **CSV Parsing**: Parsed cleanly with standard RFC 4180 parsers without malformed row exceptions.
4. **JSONL Parsing**: Evaluated all 400 JSON records; 100% contained valid `problem_id`, `condition`, `input_prompt`, `raw_generation`, and `parsed_answer` attributes.

---

## 3. Independent Verification Verdict

**Verdict**: **PASS** (All core public artifacts are publicly retrievable via HTTPS, verified complete, uncorrupted, and cryptographically identical to approved local sources).
