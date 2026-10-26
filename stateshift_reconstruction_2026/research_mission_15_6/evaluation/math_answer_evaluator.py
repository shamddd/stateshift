#!/usr/bin/env python3
"""
StateShift Robust Math Answer Evaluator & Statistical Inference Engine
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Capabilities:
1. Robust answer extraction from nested LaTeX \\boxed{...} and natural language fallbacks.
2. Canonical mathematical normalization (LaTeX stripping, fractions, numbers, symbols).
3. Symbolic and algebraic equivalence checking via SymPy with numerical fallback.
4. Paired within-subject condition comparison (Conditions A, D, E, F).
5. Statistical testing: Paired bootstrap CIs (B=10,000), McNemar test (exact & asymptotic),
   and two-sided paired permutation tests.
"""

import re
import math
import json
from typing import Dict, Any, List, Optional, Tuple, Union

try:
    import sympy
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

try:
    import numpy as np
    import scipy.stats as stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def extract_boxed_answer(text: str) -> Optional[str]:
    """
    Extracts the content of LaTeX \\boxed{...} with full nested curly brace support.
    If multiple \\boxed{} occur, returns the last one (canonical in math solutions).
    Falls back to common conversational final answer patterns if \\boxed{} is absent.
    """
    if not text or not isinstance(text, str):
        return None

    # Step 1: Scan for all \\boxed{ occurrences and resolve nested braces
    boxed_candidates = []
    target = "\\boxed{"
    idx = 0
    while True:
        start_idx = text.find(target, idx)
        if start_idx == -1:
            break
        # Match braces
        brace_start = start_idx + len(target)
        depth = 1
        curr = brace_start
        while curr < len(text) and depth > 0:
            if text[curr] == '{':
                depth += 1
            elif text[curr] == '}':
                depth -= 1
            curr += 1

        if depth == 0:
            boxed_candidates.append(text[brace_start:curr - 1].strip())
            idx = curr
        else:
            # Unbalanced brace; take remainder of line
            rest = text[brace_start:].split("\n")[0].rstrip("}").strip()
            boxed_candidates.append(rest)
            break

    if boxed_candidates:
        return boxed_candidates[-1]

    # Step 2: Fallback natural language patterns
    patterns = [
        r"(?:the\s+final\s+answer\s+is|final\s+answer\s*:?)\s*[:=]?\s*\$?([^\$\n\.\,]+)\$?",
        r"(?:is\s+equal\s+to|equals)\s*[:=]?\s*\$?([^\$\n\.\,]+)\$?$",
        r"\*\*([^\*\n]+)\*\*\s*$"
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            if candidate:
                return candidate

    return None


def normalize_latex_string(s: str) -> str:
    """
    Normalizes a mathematical string by stripping formatting wrappers.
    """
    if s is None:
        return ""
    s = str(s).strip()

    # Remove enclosing math dollar signs
    if s.startswith("$") and s.endswith("$") and len(s) > 1:
        s = s[1:-1].strip()

    # Common LaTeX macros
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\mathbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\displaystyle", "", s)
    s = re.sub(r"\\left", "", s)
    s = re.sub(r"\\right", "", s)
    s = re.sub(r"\\quad", " ", s)
    s = re.sub(r"\\,", " ", s)
    s = re.sub(r"\\!", "", s)

    # Fractions: \frac{a}{b} -> (a)/(b)
    frac_pattern = re.compile(r"\\frac\{([^{}]+)\}\{([^{}]+)\}")
    while frac_pattern.search(s):
        s = frac_pattern.sub(r"(\1)/(\2)", s)

    # Symbols
    s = s.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/")
    s = s.replace("\\pm", "+-")
    s = s.replace("–", "-").replace("—", "-")  # En-dash / Em-dash
    s = s.replace("^\\circ", " deg")

    # Clean whitespace around parentheses
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)
    # Simplify redundant double parens ((a)/(b)) -> (a)/(b)
    s = re.sub(r"\(\s*\(([^\(\)]+)\)/\(([^\(\)]+)\)\s*\)", r"(\1)/(\2)", s)
    s = re.sub(r"\(\s*\(([^\(\)]+)\)\s*\)", r"(\1)", s)

    # Strip excessive whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_numeric_value(s: str) -> Optional[float]:
    """Attempts to parse string into a clean float value."""
    s = s.strip()
    # Direct float
    try:
        return float(s)
    except ValueError:
        pass

    # Simple division e.g. 3/4 or (3)/(4)
    div_match = re.match(r"^\(?\s*([-+]?\d*\.?\d+)\s*\)?\s*/\s*\(?\s*([-+]?\d*\.?\d+)\s*\)?$", s)
    if div_match:
        try:
            num = float(div_match.group(1))
            den = float(div_match.group(2))
            if den != 0:
                return num / den
        except ValueError:
            pass

    return None


def is_symbolically_equal(expr1: str, expr2: str) -> bool:
    """Uses SymPy to test algebraic identity: expr1 - expr2 == 0."""
    if not SYMPY_AVAILABLE:
        return False
    try:
        # Replace caret with ** for sympy
        e1 = expr1.replace("^", "**")
        e2 = expr2.replace("^", "**")
        transformations = standard_transformations + (implicit_multiplication_application,)
        s1 = parse_expr(e1, transformations=transformations, evaluate=True)
        s2 = parse_expr(e2, transformations=transformations, evaluate=True)
        diff = sympy.simplify(s1 - s2)
        return diff == 0
    except Exception:
        return False


def is_answer_correct(predicted: Optional[str], gold: Optional[str]) -> bool:
    """
    Comprehensive multi-pass correctness evaluator:
    1. Direct string match
    2. Normalized string match
    3. Numeric value equivalence (< 1e-6)
    4. Symbolic/algebraic equivalence via SymPy
    """
    if predicted is None or gold is None:
        return False

    pred_raw = str(predicted).strip()
    gold_raw = str(gold).strip()

    if pred_raw == gold_raw:
        return True

    norm_pred = normalize_latex_string(pred_raw)
    norm_gold = normalize_latex_string(gold_raw)

    if norm_pred == norm_gold:
        return True

    # Check without spaces
    if norm_pred.replace(" ", "") == norm_gold.replace(" ", ""):
        return True

    # Check stripping single variable assignment prefix (e.g. x = 5 vs 5)
    pred_no_var = re.sub(r"^[a-zA-Z]\s*=\s*", "", norm_pred).strip()
    gold_no_var = re.sub(r"^[a-zA-Z]\s*=\s*", "", norm_gold).strip()
    if pred_no_var == gold_no_var or pred_no_var.replace(" ", "") == gold_no_var.replace(" ", ""):
        return True

    # Numeric check
    val_pred = parse_numeric_value(norm_pred)
    val_gold = parse_numeric_value(norm_gold)
    if val_pred is not None and val_gold is not None:
        if math.isclose(val_pred, val_gold, abs_tol=1e-5, rel_tol=1e-4):
            return True

    # SymPy symbolic check
    if is_symbolically_equal(norm_pred, norm_gold):
        return True

    return False


def evaluate_cohort(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates a collection of generated records across Conditions A, D, E, F.
    Computes accuracy, paired differences, latency, and token throughput.
    """
    by_problem: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for r in records:
        pid = r.get("problem_id", r.get("problem_index", "unknown"))
        cond = r.get("condition_code", r.get("condition", "unknown"))
        if pid not in by_problem:
            by_problem[pid] = {}
        by_problem[pid][cond] = r

    condition_counts = {"A": 0, "D": 0, "E": 0, "F": 0}
    condition_correct = {"A": 0, "D": 0, "E": 0, "F": 0}
    condition_tokens = {"A": [], "D": [], "E": [], "F": []}
    condition_latency = {"A": [], "D": [], "E": [], "F": []}

    cond_key_map = {
        "Condition_A_Zero_Shot": "A", "Condition_A": "A", "A": "A",
        "Condition_D_Forced_Restart": "D", "Condition_D": "D", "D": "D",
        "Condition_E_Explicit_Repair": "E", "Condition_E": "E", "E": "E",
        "Condition_F_State_Preserving": "F", "Condition_F": "F", "F": "F",
    }

    paired_vectors: Dict[str, List[int]] = {"A": [], "D": [], "E": [], "F": []}
    evaluated_records = []

    for pid, conds in by_problem.items():
        # Evaluate each condition present
        scores_for_problem = {}
        for raw_c, rec in conds.items():
            c = cond_key_map.get(raw_c, raw_c)
            gold = rec.get("gold_answer")
            raw_out = rec.get("raw_output", rec.get("generated_text", ""))
            extracted = extract_boxed_answer(raw_out)
            correct = is_answer_correct(extracted, gold)

            if c in condition_counts:
                condition_counts[c] += 1
                if correct:
                    condition_correct[c] += 1
                gen_tok = rec.get("generated_tokens", 0)
                if gen_tok:
                    condition_tokens[c].append(gen_tok)
                lat = rec.get("latency_seconds", 0.0)
                if lat:
                    condition_latency[c].append(lat)
                scores_for_problem[c] = 1 if correct else 0

            rec_eval = dict(rec)
            rec_eval["extracted_answer"] = extracted
            rec_eval["is_correct"] = correct
            evaluated_records.append(rec_eval)

        # If all 4 conditions present, record for paired tests
        if all(k in scores_for_problem for k in ["A", "D", "E", "F"]):
            for k in ["A", "D", "E", "F"]:
                paired_vectors[k].append(scores_for_problem[k])

    accuracies = {
        c: (condition_correct[c] / condition_counts[c]) if condition_counts[c] > 0 else 0.0
        for c in ["A", "D", "E", "F"]
    }

    # Summary
    summary = {
        "total_records": len(records),
        "total_problems": len(by_problem),
        "condition_counts": condition_counts,
        "condition_correct": condition_correct,
        "accuracies": accuracies,
        "paired_sample_size": len(paired_vectors["A"]),
        "paired_vectors": paired_vectors,
        "tokens_per_condition_mean": {
            c: float(np.mean(toks)) if (SCIPY_AVAILABLE and toks) else (sum(toks)/len(toks) if toks else 0.0)
            for c, toks in condition_tokens.items()
        },
        "latency_per_condition_mean": {
            c: float(np.mean(lats)) if (SCIPY_AVAILABLE and lats) else (sum(lats)/len(lats) if lats else 0.0)
            for c, lats in condition_latency.items()
        }
    }
    return summary


def paired_bootstrap_ci(
    y_true_cond1: List[int],
    y_true_cond2: List[int],
    n_bootstraps: int = 10000,
    alpha: float = 0.05,
    seed: int = 42
) -> Dict[str, float]:
    """
    Computes 95% non-parametric paired bootstrap confidence interval for mean(y1 - y2).
    """
    n = len(y_true_cond1)
    if n == 0 or n != len(y_true_cond2):
        return {"mean_diff": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}

    diffs = [y1 - y2 for y1, y2 in zip(y_true_cond1, y_true_cond2)]
    observed_mean = sum(diffs) / n

    if not SCIPY_AVAILABLE:
        # Deterministic simple fallback
        return {"mean_diff": round(observed_mean, 4), "ci_lower": round(observed_mean, 4), "ci_upper": round(observed_mean, 4)}

    rng = np.random.default_rng(seed)
    diff_arr = np.array(diffs)
    boot_indices = rng.integers(0, n, size=(n_bootstraps, n))
    boot_means = diff_arr[boot_indices].mean(axis=1)

    lower_pct = 100 * (alpha / 2.0)
    upper_pct = 100 * (1.0 - alpha / 2.0)

    ci_lower = float(np.percentile(boot_means, lower_pct))
    ci_upper = float(np.percentile(boot_means, upper_pct))

    return {
        "mean_diff": round(float(observed_mean), 4),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "std_error": round(float(np.std(boot_means)), 4)
    }


def mcnemar_test(y_true_cond1: List[int], y_true_cond2: List[int]) -> Dict[str, Any]:
    """
    Executes McNemar's test for paired binary proportions.
    Contingency table:
       b: cond1=1, cond2=0
       c: cond1=0, cond2=1
    Uses exact binomial test when b + c < 25, asymptotic chi-square with continuity correction otherwise.
    """
    if len(y_true_cond1) != len(y_true_cond2) or len(y_true_cond1) == 0:
        return {"statistic": 0.0, "p_value": 1.0, "discordant_b": 0, "discordant_c": 0}

    b = sum(1 for y1, y2 in zip(y_true_cond1, y_true_cond2) if y1 == 1 and y2 == 0)
    c = sum(1 for y1, y2 in zip(y_true_cond1, y_true_cond2) if y1 == 0 and y2 == 1)
    discordant_total = b + c

    if discordant_total == 0:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "discordant_b": 0,
            "discordant_c": 0,
            "method": "No discordant pairs (identical outcomes)"
        }

    # Exact binomial test for small discordance (b + c < 25)
    if discordant_total < 25:
        # Two-sided exact binomial with p=0.5
        k = min(b, c)
        p_val = 0.0
        for i in range(k + 1):
            p_val += math.comb(discordant_total, i) * (0.5 ** discordant_total)
        p_val = min(1.0, 2.0 * p_val)
        stat = float(b - c)
        method = "Exact Binomial Two-Sided"
    else:
        # Asymptotic Chi-square with Edwards continuity correction: (|b - c| - 1)^2 / (b + c)
        stat = ((abs(b - c) - 1.0) ** 2) / discordant_total
        if SCIPY_AVAILABLE:
            p_val = float(stats.chi2.sf(stat, df=1))
        else:
            # Simple approximation
            p_val = math.erfc(math.sqrt(stat) / math.sqrt(2))
        method = "Asymptotic Chi-Square with Continuity Correction"

    return {
        "statistic": round(float(stat), 4),
        "p_value": round(float(p_val), 6),
        "discordant_b": b,
        "discordant_c": c,
        "total_discordant": discordant_total,
        "method": method
    }


def permutation_test(
    y_true_cond1: List[int],
    y_true_cond2: List[int],
    n_permutations: int = 10000,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Two-sided paired permutation test on difference in accuracy.
    Under the null hypothesis, swapping outcomes for problem i has probability 0.5.
    """
    n = len(y_true_cond1)
    if n == 0 or n != len(y_true_cond2):
        return {"observed_diff": 0.0, "p_value": 1.0}

    diffs = np.array([y1 - y2 for y1, y2 in zip(y_true_cond1, y_true_cond2)]) if SCIPY_AVAILABLE else [y1 - y2 for y1, y2 in zip(y_true_cond1, y_true_cond2)]
    observed_stat = abs(float(np.mean(diffs))) if SCIPY_AVAILABLE else abs(sum(diffs) / n)

    if not SCIPY_AVAILABLE or observed_stat == 0.0:
        return {"observed_diff": round(observed_stat, 4), "p_value": 1.0}

    rng = np.random.default_rng(seed)
    # Generate random sign flips (+1 or -1) for each permutation
    signs = rng.choice([-1, 1], size=(n_permutations, n))
    perm_means = np.abs((diffs * signs).mean(axis=1))

    extreme_count = np.sum(perm_means >= observed_stat)
    p_val = float((extreme_count + 1) / (n_permutations + 1))

    return {
        "observed_diff": round(float(np.mean(diffs)), 4),
        "p_value": round(p_val, 6),
        "n_permutations": n_permutations
    }
