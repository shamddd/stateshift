"""
Mission 20 Automated Release Quality Assurance Test Suite
Verifies all public repository artifacts, datasets, reproducibility scripts, and claim consistency.
"""

import hashlib
import json
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent

def test_public_dataset_hashes():
    """Verify cryptographic SHA-256 hashes for canonical datasets."""
    expected = {
        ROOT / "data" / "study1" / "controlled_endpoint_outcomes.csv":
            "49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139",
        ROOT / "data" / "study2" / "stateshift_primary_400_generations.jsonl":
            "bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2",
        ROOT / "data" / "study2" / "final_verified_outcomes.csv":
            "19a328a95dd25ec326fe824361386cc0ddf731f2bf1c392253be0aa19c2385ba",
    }
    for path, exp_hash in expected.items():
        assert path.exists(), f"File missing: {path}"
        with open(path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        assert actual_hash == exp_hash, f"Hash mismatch for {path.name}: {actual_hash} != {exp_hash}"

def test_paper_artifacts_exist():
    """Verify manuscript PDF, LaTeX source, and arXiv release bundle."""
    pdf_path = ROOT / "paper" / "STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf"
    tex_path = ROOT / "paper" / "STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex"
    zip_path = ROOT / "paper" / "source" / "STATESHIFT_ARXIV_RELEASE_SOURCE.zip"

    assert pdf_path.exists() and pdf_path.stat().st_size > 150_000
    assert tex_path.exists() and tex_path.stat().st_size > 20_000
    assert zip_path.exists() and zip_path.stat().st_size > 500_000

    # Verify figures
    for fig_id in range(1, 6):
        assert (ROOT / "paper" / "figures" / f"figure{fig_id}_framework.pdf" if fig_id==1 else
                ROOT / "paper" / "figures" / f"figure{fig_id}_{['framework','trajectory','cell_means','funnel','results'][fig_id-1]}.pdf").exists()

def test_study1_reproduction_accuracy():
    """Execute Study 1 reproduction and assert exact mathematical estimands."""
    sys_path = ROOT / "experiments" / "study1_checkpoint_lineage" / "reproduce_study1.py"
    assert sys_path.exists()

    from experiments.study1_checkpoint_lineage.reproduce_study1 import run_study1_analysis
    res = run_study1_analysis()
    assert abs(res["gamma_256"] - 0.1176) < 0.001
    assert abs(res["clustered_se"] - 0.0114) < 0.001
    assert res["p_val"] < 1e-15

def test_study2_reproduction_accuracy():
    """Execute Study 2 reproduction and assert exact McNemar contingency and p-values."""
    sys_path = ROOT / "experiments" / "study2_reasoning_recovery" / "reproduce_study2.py"
    assert sys_path.exists()

    from experiments.study2_reasoning_recovery.reproduce_study2 import run_study2_analysis
    res = run_study2_analysis()
    assert abs(res["acc_a"] - 0.64) < 1e-4
    assert abs(res["acc_d"] - 0.67) < 1e-4
    assert abs(res["acc_e"] - 0.71) < 1e-4
    assert abs(res["acc_f"] - 0.73) < 1e-4
    assert abs(res["tau_fd"] - 0.06) < 1e-4

    assert res["contingency"] == {"a": 65, "b": 8, "c": 2, "d": 25}
    assert abs(res["p_two_sided"] - 0.109375) < 1e-6
    assert abs(res["p_one_sided"] - 0.054688) < 1e-6
    assert abs(res["p_fa"] - 0.0117) < 0.001

def test_exact_power_bounds():
    """Assert discrete power at N=100 is 36.20% and N=231 yields >= 80% power."""
    from experiments.study2_reasoning_recovery.exact_power_analysis import (
        compute_exact_mcnemar_power,
        precompute_critical_values
    )
    cache = precompute_critical_values(300, 0.05)
    power_100 = compute_exact_mcnemar_power(100, 0.10, 0.06, crit_cache=cache)
    assert abs(power_100 - 0.3620) < 0.002

    power_231 = compute_exact_mcnemar_power(231, 0.10, 0.06, crit_cache=cache)
    assert power_231 >= 0.8000
    assert abs(power_231 - 0.8007) < 0.002

def test_documentation_and_governance_files():
    """Verify all required documentation and governance files exist."""
    req_docs = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CITATION.cff",
        ROOT / "CITATION.bib",
        ROOT / "CONTRIBUTING.md",
        ROOT / "CODE_OF_CONDUCT.md",
        ROOT / "SECURITY.md",
        ROOT / "CHANGELOG.md",
        ROOT / "docs" / "RESEARCH_HISTORY.md",
        ROOT / "docs" / "SCIENTIFIC_CLAIMS.md",
        ROOT / "docs" / "EXPERIMENTAL_PROTOCOLS.md",
        ROOT / "docs" / "STATISTICAL_METHODS.md",
        ROOT / "docs" / "DATA_PROVENANCE.md",
        ROOT / "docs" / "REPRODUCIBILITY.md",
        ROOT / "docs" / "LIMITATIONS.md",
        ROOT / "docs" / "ETHICS_AND_DISCLOSURES.md",
        ROOT / "docs" / "ARXIV_SUBMISSION_GUIDE.md",
        ROOT / "docs" / "internal_review" / "STATESHIFT_INTERNAL_ADVERSARIAL_REVIEW_FINAL.pdf",
        ROOT / ".github" / "workflows" / "research-ci.yml",
    ]
    for doc in req_docs:
        assert doc.exists(), f"Required document missing: {doc}"
