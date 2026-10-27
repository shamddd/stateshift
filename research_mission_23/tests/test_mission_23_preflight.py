"""
test_mission_23_preflight.py

Comprehensive preflight unit test suite for StateShift Research Mission 23.
Verifies baseline recomputations, manifest cryptographic integrity, Major Issue M1-M5 remediations,
and fail-closed execution safeguards.
"""

import os
import csv
import json
import hashlib
import subprocess
from pathlib import Path
import pytest
from scipy.stats import binom

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PILOT_CSV = REPO_ROOT / "data" / "study2" / "final_verified_outcomes.csv"
PILOT_JSONL = REPO_ROOT / "data" / "study2" / "stateshift_primary_400_generations.jsonl"
CONFIRMATORY_MANIFEST = REPO_ROOT / "research_mission_22" / "data" / "confirmatory_231_manifest.jsonl"
LOCK_FILE = REPO_ROOT / ".cloud_execution_locked"
M2_DOC = REPO_ROOT / "research_mission_23" / "02_MAJOR_SCIENTIFIC_REMEDIATION.md"
RUNNER_SCRIPT = REPO_ROOT / "research_mission_22" / "scripts" / "run_confirmatory_trial.py"

def test_pilot_baseline_recomputation():
    """Verify pilot data directly yields a=65, b=8, c=2, d=25 and p=0.109375."""
    assert PILOT_CSV.exists()
    with open(PILOT_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 100

    a = sum(1 for r in rows if r["condition_D_correct"] == "True" and r["condition_F_correct"] == "True")
    b = sum(1 for r in rows if r["condition_D_correct"] == "False" and r["condition_F_correct"] == "True")
    c = sum(1 for r in rows if r["condition_D_correct"] == "True" and r["condition_F_correct"] == "False")
    d = sum(1 for r in rows if r["condition_D_correct"] == "False" and r["condition_F_correct"] == "False")

    assert (a, b, c, d) == (65, 8, 2, 25)
    p_exact = 2.0 * float(binom.sf(max(b, c) - 1, b + c, 0.5))
    assert pytest.approx(p_exact, 1e-6) == 0.109375

def test_confirmatory_manifest_crypto_hash():
    """Verify confirmatory manifest hash and 924 request count."""
    assert CONFIRMATORY_MANIFEST.exists()
    with open(CONFIRMATORY_MANIFEST, "rb") as f:
        manifest_hash = hashlib.sha256(f.read()).hexdigest()
    assert manifest_hash == "2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5"

    with open(CONFIRMATORY_MANIFEST, "r", encoding="utf-8") as f:
        recs = [json.loads(line) for line in f]
    assert len(recs) == 924
    assert len(set(r["problem_id"] for r in recs)) == 231
    assert len(set(r["request_id"] for r in recs)) == 924

def test_major_issue_m1_standardized_formulation():
    """Verify that Major Issue M1 standardized text is present in the remediation doc."""
    assert M2_DOC.exists()
    text = M2_DOC.read_text(encoding="utf-8")
    expected_phrase = (
        "The primary experiment estimates the effect of a bundled prompt-level continuation intervention "
        "relative to forced restart. The intervention combines retained reasoning context, continuation instructions, "
        "and potentially different effective reasoning budgets. Existing controls are consistent with a contribution "
        "from semantically valid context but do not uniquely isolate the causal mechanism."
    )
    assert expected_phrase in text

def test_cloud_lock_is_active_and_enforced():
    """Verify .cloud_execution_locked exists and runner fails closed with code 101."""
    assert LOCK_FILE.exists()
    cmd = [subprocess.sys.executable, str(RUNNER_SCRIPT)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 101
    assert "Cloud execution lock active" in res.stdout

def test_runner_dry_run_local_cpu_success():
    """Verify that runner dry run completes successfully on local CPU with zero cloud calls."""
    cmd = ["python3", str(RUNNER_SCRIPT), "--dry-run"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "DRY-RUN STATUS: FULL PREFLIGHT SUCCESS. READY FOR EXECUTION." in res.stdout
