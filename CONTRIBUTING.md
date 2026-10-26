# Contributing to StateShift

Thank you for your interest in contributing to Project StateShift.

StateShift is a rigorous scientific research project targeting conference publication and open-source scientific reproducibility. We welcome contributions that improve reproducibility, fix bugs, or expand independent benchmark evaluations.

---

## Code of Conduct

All contributors and participants are expected to adhere to the [Code of Conduct](CODE_OF_CONDUCT.md), fostering an open, respectful, and scientifically rigorous community.

---

## Contribution Guidelines

1. **Scientific Integrity**: Any proposed empirical changes must include exact data provenance, cryptographic checksums, and reproduction scripts. Synthetic or fabricated model outputs are strictly prohibited.
2. **Deterministic & CPU-Friendly**: Code contributions should avoid hard requirements on paid cloud GPUs for regression testing. Automated tests must execute on CPU.
3. **Branching & Pull Requests**:
   * Create a feature branch: `git checkout -b feature/your-improvement`.
   * Ensure all unit tests pass: `pytest -q`.
   * Submit a clear pull request with a detailed summary of methodological or software enhancements.

---

## Security & Bug Reports

For potential security vulnerabilities, private credential leaks, or sensitive disclosures, please refer to our [Security Policy](SECURITY.md) and report directly to the Principal Investigator via email.
