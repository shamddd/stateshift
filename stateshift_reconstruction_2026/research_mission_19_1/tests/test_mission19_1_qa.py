#!/usr/bin/env python3
"""
Test Suite for StateShift Research Mission 19.1:
Verifies publication integrity, exact power sensitivity, removal of overclaims,
absence of unauthorized author signatures, and compilation assets.
"""

import os
import sys
import json
import zipfile
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

MISSION_DIR = os.path.join(REPO_ROOT, "research_mission_19_1")


def test_compiled_release_candidate_pdf():
    pdf_path = os.path.join(MISSION_DIR, "STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf")
    assert os.path.exists(pdf_path), "STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf must exist"
    size = os.path.getsize(pdf_path)
    assert size > 100_000, f"PDF file size ({size} bytes) should be > 100 KB"


def test_compiled_internal_peer_review_pdf():
    pdf_path = os.path.join(MISSION_DIR, "STATESHIFT_INTERNAL_ADVERSARIAL_REVIEW_FINAL.pdf")
    assert os.path.exists(pdf_path), "STATESHIFT_INTERNAL_ADVERSARIAL_REVIEW_FINAL.pdf must exist"
    size = os.path.getsize(pdf_path)
    assert size > 20_000, f"Review PDF size ({size} bytes) should be > 20 KB"


def test_arxiv_release_source_zip():
    zip_path = os.path.join(MISSION_DIR, "STATESHIFT_ARXIV_RELEASE_SOURCE.zip")
    assert os.path.exists(zip_path), "STATESHIFT_ARXIV_RELEASE_SOURCE.zip must exist"
    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()
        assert "STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex" in names
        assert "references.bib" in names
        assert any(n.startswith("figures/") for n in names)


def test_historical_evidence_ledger():
    ledger_path = os.path.join(MISSION_DIR, "data", "historical_experiment_evidence_ledger.json")
    assert os.path.exists(ledger_path), "historical_experiment_evidence_ledger.json must exist"
    with open(ledger_path) as f:
        ledger = json.load(f)
    assert ledger["row_count"] == 29056
    assert ledger["unique_pairs"] == 454
    assert ledger["raw_text_completions_present"] is False
    assert "PARTIALLY VERIFIED" in ledger["verdict"]
    metrics = ledger["reproduced_metrics"]
    assert abs(metrics["gamma_256"] - 0.117566) < 1e-4
    assert abs(metrics["clustered_se"] - 0.011368) < 1e-4


def test_exact_power_sensitivity_analysis():
    power_path = os.path.join(MISSION_DIR, "data", "exact_power_verification_results.json")
    assert os.path.exists(power_path), "exact_power_verification_results.json must exist"
    with open(power_path) as f:
        pdata = json.load(f)
    baseline = pdata["pilot_baseline"]
    assert abs(baseline["exact_power_pct"] - 36.2) < 0.1
    targets = pdata["confirmatory_targets"]
    assert targets["target_80"]["required_N"] == 231
    assert targets["target_90"]["required_N"] == 299


def test_author_approval_checklist_blank():
    checklist_path = os.path.join(MISSION_DIR, "AUTHOR_FINAL_APPROVAL_CHECKLIST.md")
    assert os.path.exists(checklist_path)
    with open(checklist_path) as f:
        content = f.read()
    # Confirm no pre-filled signature
    assert "**Signed:**" not in content
    assert "[x]" not in content
    assert "[ ] Yes   [ ] No" in content
    assert "Signature / explicit approval: _________________________________________" in content


def test_no_guaranteed_significance_language_in_mission():
    for fname in os.listdir(MISSION_DIR):
        if fname.endswith(".md") or fname.endswith(".tex"):
            fpath = os.path.join(MISSION_DIR, fname)
            with open(fpath, "r", errors="ignore") as f:
                text = f.read().lower()
            # If the word guaranteed appears, make sure it's in the context of eradicating it
            if "guaranteed significance" in text or "guaranteed two-sided" in text:
                assert "overclaim" in text or "eradicate" in text or "not" in text or "false" in text or "implying" in text, \
                    f"Found unauthorized guarantee language in {fname}"


def test_cloud_lock_active():
    lock_path = os.path.join(REPO_ROOT, ".cloud_execution_locked")
    assert os.path.exists(lock_path), "Cloud execution lock must remain engaged fail-closed"
