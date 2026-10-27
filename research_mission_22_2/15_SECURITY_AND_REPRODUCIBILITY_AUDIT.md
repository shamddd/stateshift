# Research Mission 22.2 — Security and Reproducibility Audit

## 1. Security & Credential Protection Audit

A complete forensic scan of the StateShift repository was conducted to ensure zero leakage of confidential credentials, API keys, or private tokens:
- **RunPod Credentials**: `runpod_credentials.json` and `RUNPOD_API_KEY` are strictly excluded from Git tracking via `.gitignore`.
- **Pre-Commit Verification**: No hardcoded secrets, private SSH keys, or bearer tokens were detected in any tracked file, script, or documentation artifact.
- **Environment Isolation**: All cloud authentication is injected at runtime via environment variables or interactive user prompts.

---

## 2. `.gitignore` Policy Governance

The repository's `.gitignore` file enforces strict exclusion patterns:
- Secrets & Credentials: `.env`, `.env.*`, `secrets.yaml`, `*.pem`, `*.key`, `credentials/`, `runpod_credentials*`, `*secret*`, `*token*`.
- Heavy Checkpoints & Model Caches: `*.safetensors`, `*.bin`, `*.pt`, `huggingface_cache/`, `models/cache/`.
- Temporary Logs & Virtual Envs: `*.log`, `.venv/`, `__pycache__/`, `.pytest_cache/`.

*(Note: Essential documentation files that touch upon token budgets, such as `10_CAUSAL_VALIDITY_AND_TOKEN_BUDGET_AUDIT.md`, are force-tracked using `git add -f` to prevent unintended omission).*

---

## 3. Computational Reproducibility Checklist

Every result reported in StateShift can be independently reproduced on a standard workstation:
1. **Pilot Outcome Reconstruction**:
   ```bash
   python3 research_mission_22_2/scripts/reconstruct_pilot_outcomes.py
   ```
   Reproduces the 400-generation evaluation, generates the dual-path contingency tables, and produces `verified_pilot_contingency.json`.
2. **Exact McNemar Power Calculations**:
   ```bash
   python3 research_mission_22/scripts/confirmatory_exact_power.py
   ```
   Reproduces $80.07\%$ power at $N=231$ and generates `confirmatory_power_sensitivity.pdf`.
3. **Automated Regression Suite**:
   ```bash
   python3 -m pytest research_mission_22/tests/ research_mission_22_1/tests/ research_mission_22_2/tests/ -v
   ```
   Executes 24 automated test cases covering statistics, manifests, execution schema, and contingency reconciliation.
