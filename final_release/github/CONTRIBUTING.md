# Contributing to StateShift

Thank you for your interest in contributing to StateShift! This project adheres to the highest standards of scientific reproducibility, preregistration integrity, and open-source software hygiene.

## 1. Principles of Scientific Integrity
- **Immutable Empirical Records**: Raw model outputs and frozen manifests from past experiments cannot be retroactively modified or deleted.
- **Hypothesis Testing**: Any new confirmatory evaluation must prespecify sample sizes, pinned model checkpoints, decoding parameters, and primary contrast functions before data collection.
- **Reporting Negative Results**: We value negative, confirmatory, and replication findings equally with positive discoveries.

## 2. Development Workflow
1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Set up the Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the full test suite before committing:
   ```bash
   pytest tests/
   python final_release/reproducibility/reproduce_all_statistics.py
   ```
4. Submit a Pull Request targeting the `main` branch with a clear description of changes.
