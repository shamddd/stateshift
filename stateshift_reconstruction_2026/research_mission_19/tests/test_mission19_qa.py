#!/usr/bin/env python3
"""
Test Suite for StateShift Research Mission 19:
Verifies publication artifacts, exact statistics, case studies, and safety invariants.
"""

import os
import sys
import json
import zipfile
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

MISSION_DIR = os.path.join(REPO_ROOT, "research_mission_19")


def test_compiled_manuscript_pdf():
    pdf_path = os.path.join(MISSION_DIR, "STATESHIFT_ARXIV_FINAL.pdf")
    assert os.path.exists(pdf_path), "STATESHIFT_ARXIV_FINAL.pdf must exist"
    size = os.path.getsize(pdf_path)
    assert size > 100_000, f"PDF file size ({size} bytes) should be > 100 KB"


def test_compiled_peer_review_pdf():
    pdf_path = os.path.join(MISSION_DIR, "STATESHIFT_INDEPENDENT_PEER_REVIEW.pdf")
    assert os.path.exists(pdf_path), "STATESHIFT_INDEPENDENT_PEER_REVIEW.pdf must exist"
    size = os.path.getsize(pdf_path)
    assert size > 20_000, f"Peer review PDF size ({size} bytes) should be > 20 KB"


def test_arxiv_source_zip():
    zip_path = os.path.join(MISSION_DIR, "STATESHIFT_ARXIV_SOURCE.zip")
    assert os.path.exists(zip_path), "STATESHIFT_ARXIV_SOURCE.zip must exist"
    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()
        assert "STATESHIFT_ARXIV_FINAL.tex" in names
        assert "references.bib" in names
        assert any(n.startswith("figures/") for n in names)


def test_verified_outcomes_accuracy():
    stats_path = os.path.join(MISSION_DIR, "data", "independent_final_statistics.json")
    assert os.path.exists(stats_path)
    with open(stats_path) as f:
        data = json.load(f)
    
    primary = data["contrasts"]["Primary Estimand (F vs D)"]
    contingency = primary["contingency"]
    assert contingency["a"] == 65
    assert contingency["b"] == 8
    assert contingency["c"] == 2
    assert contingency["d"] == 25
    assert contingency["n"] == 100
    assert primary["point_estimate_pct"] == 6.0
    assert abs(primary["exact_mcnemar_two_sided_p"] - 0.109375) < 1e-5
    assert abs(primary["exact_mcnemar_one_sided_p"] - 0.0546875) < 1e-5


def test_exact_power_analysis():
    power_path = os.path.join(MISSION_DIR, "data", "exact_power_analysis_results.json")
    assert os.path.exists(power_path)
    with open(power_path) as f:
        power_data = json.load(f)
    
    n100 = power_data["power_at_n100"]
    assert abs(n100["exact_discrete_unconditional_power"] - 0.3619) < 0.01
    targets = power_data["sample_size_targets"]
    assert targets["0.8"]["exact_N"] == 231
    assert targets["0.9"]["exact_N"] == 299


def test_math500_012_resolution():
    manifest_path = os.path.join(REPO_ROOT, "research_mission_15_6", "manifests", "primary_100_manifest.json")
    assert os.path.exists(manifest_path), f"Manifest must exist at {manifest_path}"
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    reqs = manifest["requests"]
    m012 = next(r for r in reqs if r["problem_id"] == "math500_012")
    assert m012["gold_answer"] == "284"
    assert "proper divisors" in m012["prompt_text"].lower()
    assert "quadratic" not in m012["prompt_text"].lower()
    assert "(x-14)" not in m012["prompt_text"]


def test_cloud_safety_lock():
    lock_path = os.path.join(REPO_ROOT, ".cloud_execution_locked")
    assert os.path.exists(lock_path), "Cloud execution lock must remain in place"
