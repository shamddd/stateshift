#!/usr/bin/env python3
"""
Unit Test Suite for StateShift Math Answer Evaluator & Statistical Inference
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)
"""

import os
import json
import pytest

from research_mission_15_6.evaluation.math_answer_evaluator import (
    extract_boxed_answer,
    normalize_latex_string,
    parse_numeric_value,
    is_symbolically_equal,
    is_answer_correct,
    evaluate_cohort,
    paired_bootstrap_ci,
    mcnemar_test,
    permutation_test
)


# =========================================================================
# 1. Answer Extraction & Nested Brace Parsing
# =========================================================================
def test_extract_boxed_simple():
    text = "The answer is \\boxed{42}."
    assert extract_boxed_answer(text) == "42"


def test_extract_boxed_nested_braces():
    text = "Therefore, we have \\boxed{\\frac{3\\sqrt{2}}{5}}."
    assert extract_boxed_answer(text) == "\\frac{3\\sqrt{2}}{5}"


def test_extract_boxed_deeply_nested():
    text = "Result is \\boxed{\\sum_{k=1}^\\infty \\frac{1}{k^2} - \\frac{1}{k^3}}."
    assert extract_boxed_answer(text) == "\\sum_{k=1}^\\infty \\frac{1}{k^2} - \\frac{1}{k^3}"


def test_extract_boxed_multiple_returns_last():
    text = "First we tried \\boxed{10}, but after re-evaluating we find \\boxed{20}."
    assert extract_boxed_answer(text) == "20"


def test_extract_fallback_pattern():
    text = "Solving the quadratic gives x = 5. Therefore, the final answer is 5."
    assert extract_boxed_answer(text) == "5"


def test_extract_fallback_none_when_empty():
    assert extract_boxed_answer("") is None
    assert extract_boxed_answer(None) is None


# =========================================================================
# 2. LaTeX Normalization & Numeric Parsing
# =========================================================================
def test_normalize_latex_string():
    raw = "$ \\displaystyle \\left( \\frac{1}{2} \\right) \\times 4 $"
    norm = normalize_latex_string(raw)
    assert norm == "(1)/(2) * 4"


def test_parse_numeric_fraction():
    assert parse_numeric_value("3/4") == 0.75
    assert parse_numeric_value("(3)/(4)") == 0.75
    assert parse_numeric_value("-12.5") == -12.5
    assert parse_numeric_value("invalid") is None


# =========================================================================
# 3. Correctness & Equivalence Engine
# =========================================================================
def test_correctness_exact():
    assert is_answer_correct("p - q", "p - q") is True
    assert is_answer_correct("42", "42") is True


def test_correctness_numeric_tolerance():
    assert is_answer_correct("0.5", "\\frac{1}{2}") is True
    assert is_answer_correct("0.3333333", "1/3") is True
    assert is_answer_correct("10", "11") is False


def test_correctness_symbolic():
    assert is_answer_correct("x + y", "y + x") is True
    assert is_answer_correct("x^2 - 1", "(x - 1)*(x + 1)") is True
    assert is_answer_correct("p - q", "p - q") is True
    assert is_answer_correct("p - q", "q - p") is False


# =========================================================================
# 4. Cohort Evaluation on Historical Smoke Test Records
# =========================================================================
def test_evaluate_cohort_on_historical_smoke_data():
    smoke_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "data", "recovered_smoke_test_generations.jsonl"
    ))
    if os.path.exists(smoke_file):
        records = [json.loads(line) for line in open(smoke_file) if line.strip()]
        res = evaluate_cohort(records)
        assert res["total_records"] == 4
        assert res["total_problems"] == 1
        assert res["accuracies"]["A"] == 1.0
        assert res["accuracies"]["D"] == 1.0
        assert res["accuracies"]["E"] == 1.0
        assert res["accuracies"]["F"] == 1.0


# =========================================================================
# 5. Statistical Inference (Bootstrap, McNemar, Permutation)
# =========================================================================
def test_paired_bootstrap_ci():
    # 100 problems where Condition F is 80% correct and Condition D is 60% correct
    y_f = [1] * 80 + [0] * 20
    y_d = [1] * 60 + [0] * 40
    res = paired_bootstrap_ci(y_f, y_d, n_bootstraps=1000, seed=42)
    assert res["mean_diff"] == 0.20
    assert res["ci_lower"] > 0.05
    assert res["ci_upper"] < 0.35


def test_mcnemar_test():
    # Discordant pairs: b=25 (F correct, D wrong), c=5 (F wrong, D correct)
    y_f = [1] * 25 + [0] * 5 + [1] * 50 + [0] * 20
    y_d = [0] * 25 + [1] * 5 + [1] * 50 + [0] * 20

    res = mcnemar_test(y_f, y_d)
    assert res["discordant_b"] == 25
    assert res["discordant_c"] == 5
    assert res["p_value"] < 0.001  # Highly significant difference


def test_mcnemar_identical_outcomes():
    y1 = [1, 1, 0, 0]
    y2 = [1, 1, 0, 0]
    res = mcnemar_test(y1, y2)
    assert res["p_value"] == 1.0
    assert res["discordant_b"] == 0
    assert res["discordant_c"] == 0


def test_permutation_test():
    y_f = [1] * 75 + [0] * 25
    y_d = [1] * 50 + [0] * 50
    res = permutation_test(y_f, y_d, n_permutations=2000, seed=42)
    assert res["observed_diff"] == 0.25
    assert res["p_value"] < 0.01
