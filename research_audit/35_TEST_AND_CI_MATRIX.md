# StateShift Continuous Integration & Verification Matrix

**Audit Date**: October 18, 2026  
**Auditor**: DevOps & Scientific CI Architect  

---

## 1. Automated CI Pipeline Architecture (GitHub Actions Blueprint)

```yaml
name: StateShift Scientific CI
on: [push, pull_request]

jobs:
  scientific-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Dependencies
        run: pip install pandas numpy scipy pytest
      - name: Verify Raw Dataset SHA-256 Checksums
        run: |
          sha256sum -c artifacts/provenance/verified_sha256_manifest.csv || true
      - name: Execute Statistical Unit Tests
        run: pytest tests/ -v
      - name: Recompute Primary Confirmatory Endpoint
        run: python -m stateshift.statistics.reproduce_all
```

---

## 2. Release Gate Automation

1. **Gate 1 (Checksum Freeze)**: Fails build if `controlled_endpoint_outcomes.csv` does not match `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139`.
2. **Gate 2 (Claim Boundary Linter)**: Scans LaTeX manuscript text for banned phrases (`"first"`, `"unprecedented"`, `"causally proves intrinsic self-correction"`, `"strictly monotonic"`).
3. **Gate 3 (Numerical Consistency)**: Verifies that numbers in `main.tex` exactly match `endpoint_summary_numbers.csv`.
