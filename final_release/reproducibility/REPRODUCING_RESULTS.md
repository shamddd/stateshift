# Reproducing StateShift Results

This guide provides end-to-end instructions for reproducing all empirical and statistical results reported in the StateShift publication package.

---

## 1. Fast CPU-Only Reproduction (< 10 seconds)
You do NOT need a GPU, cloud account, or API keys to verify all statistical calculations from the raw generation data.

### Step 1.1: Clone and Setup
```bash
git clone https://github.com/shamddd/stateshift.git
cd stateshift

python3 -m venv .venv
source .venv/bin/activate
pip install numpy pandas scipy statsmodels sympy pytest
```

### Step 1.2: Verify Dataset Checksums
Ensure all raw records match their frozen cryptographic signatures:
```bash
shasum -a 256 -c final_release/reproducibility/artifact_hashes.sha256
```
Expected output:
```text
research_mission_22/data/confirmatory_231_manifest.jsonl: OK
research_mission_23/data/confirmatory_924_generations.jsonl: OK
research_mission_23/data/confirmatory_statistical_summary.json: OK
data/study2/final_verified_outcomes.csv: OK
data/study2/stateshift_primary_400_generations.jsonl: OK
data/study1/controlled_endpoint_outcomes.csv: OK
.cloud_execution_locked: OK
```

### Step 1.3: Run the Master Reproduction Script
Execute the independent statistical re-computation:
```bash
python final_release/reproducibility/reproduce_all_statistics.py
```
Expected output highlights:
- Confirmatory Accuracies: A = 66.67%, D = 68.40%, E = 66.67%, F = 67.97%
- Primary Contingency Matrix (F vs D): $a=146, b=11, c=12, d=62$, total $N=231$
- Treatment Effect $\hat{\tau}_{F-D}$: $-0.43\text{ percentage points}$
- Exact Two-Sided McNemar p-value: $p = 1.000000$
- Paired 95% Wald Confidence Interval: $[-4.50\%, +3.64\%]$
- Pilot Effect: $+6.00\text{ pp}, p = 0.109375$
- Study 1 Difference Score Correlation: $r = 0.0794, p = 0.0910 \implies$ Disattenuated $r^* \approx 0.60$

### Step 1.4: Run the Regression Test Suite
```bash
pytest final_release/tests/ -v
```
All tests should pass with exit code 0.

---

## 2. Compiling the LaTeX Manuscript
To compile the release candidate paper and supplement locally:
```bash
# Install Tectonic (if not installed)
# macOS: brew install tectonic
# Linux: curl -sL https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-gnu.tar.gz | tar -xz

# Compile the paper
tectonic paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex --outdir paper/

# Compile the supplement
tectonic stateshift-manuscript-source/supplement.tex --outdir stateshift-manuscript-source/
```

---

## 3. Optional: Full GPU Regeneration from Scratch
To regenerate all 924 neural completions on authentic GPU hardware:
1. Provision a host with 1x NVIDIA RTX 4090 (24GB VRAM).
2. Clone `Qwen/Qwen2.5-Math-7B-Instruct` pinned to commit `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`.
3. Ingest the frozen manifest `research_mission_22/data/confirmatory_231_manifest.jsonl`.
4. Run inference using greedy decoding ($\tau = 0.0$, seed = 42, max tokens = 768).
5. Pass outputs through the cleanroom evaluator to re-score boxed answers.
