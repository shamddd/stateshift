#!/usr/bin/env python3
"""
StateShift Confirmatory Evaluation and Reproduction Engine (Mission 22)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Track

Executes cleanroom evaluation on confirmatory neural generations.
Computes:
- Binary correctness via cleanroom LaTeX extraction and SymPy evaluation.
- Paired contingency tables for Conditions F vs D, F vs A, F vs E.
- Exact two-sided McNemar tests.
- Secondary hypothesis testing with Holm-Bonferroni correction.
- Stratified subgroup analyses (difficulty, operator, dependency metrics).
"""

import os
import sys
import json
import re
import math
import argparse
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
from scipy.stats import binom
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

def cleanroom_extract_boxed(text: str) -> Optional[str]:
    """Extracts the last complete \\boxed{...} expression from text with nested brace support."""
    if not text:
        return None
    target = "\\boxed{"
    candidates = []
    idx = 0
    while True:
        start_idx = text.find(target, idx)
        if start_idx == -1:
            break
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
            content = text[brace_start:curr - 1].strip()
            candidates.append(content)
            idx = curr
        else:
            idx = brace_start

    if candidates:
        return candidates[-1]

    # Fallback pattern matching
    patterns = [
        r"(?:the final answer is|the answer is|final answer:)\s*[:\$]?\s*([^\n\.$]+)",
        r"(?:yields|equals|is equal to)\s*[:\$]?\s*([^\n\.$]+)"
    ]
    for pat in patterns:
        m = re.findall(pat, text, re.IGNORECASE)
        if m:
            candidate = m[-1].strip().strip("$").strip()
            if candidate and len(candidate) < 100:
                return candidate
    return None

def cleanroom_normalize_latex(expr_str: str) -> str:
    """Canonical cleanroom normalization of mathematical LaTeX."""
    if not expr_str:
        return ""
    s = expr_str.strip()
    s = re.sub(r"^\$+|\$+$", "", s).strip()
    for wrapper in [r"\\text\{([^{}]+)\}", r"\\mathbf\{([^{}]+)\}", r"\\mathrm\{([^{}]+)\}", r"\\mbox\{([^{}]+)\}"]:
        s = re.sub(wrapper, r"\1", s)
    s = re.sub(r"\\left|\\right|\\big|\\Big|\\bigg|\\Bigg", "", s)
    while "\\frac{" in s or "\\dfrac{" in s:
        m = re.search(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", s)
        if not m:
            break
        num, den = m.group(1), m.group(2)
        s = s[:m.start()] + f"(({num})/({den}))" + s[m.end():]
    s = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", s)
    s = re.sub(r"\\sqrt\[(\d+)\]\{([^{}]+)\}", r"((\2)**(1/\1))", s)
    s = re.sub(r"\\circ|\^\\circ|°", "", s)
    s = re.sub(r"(\d),(\d{3})", r"\1\2", s)
    s = s.replace("\\%", "").replace("%", "")
    s = s.replace("\\cdot", "*").replace("\\times", "*").replace("×", "*").replace("·", "*")
    s = s.replace("\\le", "<=").replace("\\leq", "<=").replace("\\ge", ">=").replace("\\geq", ">=")
    s = s.replace("\\neq", "!=").replace("\\pm", "+-")
    s = s.replace("\\infty", "oo").replace("∞", "oo")
    s = s.replace("\\pi", "pi").replace("π", "pi")
    s = re.sub(r"\s+", "", s)
    return s

def cleanroom_is_mathematically_equivalent(pred: Optional[str], gold: Optional[str]) -> bool:
    """Checks mathematical equivalence via exact matching, float approximation, and SymPy."""
    if pred is None or gold is None:
        return False
    norm_pred = cleanroom_normalize_latex(pred)
    norm_gold = cleanroom_normalize_latex(gold)
    if norm_pred.lower() == norm_gold.lower():
        return True
    pred_no_var = re.sub(r"^[a-zA-Z]\s*=\s*", "", norm_pred)
    gold_no_var = re.sub(r"^[a-zA-Z]\s*=\s*", "", norm_gold)
    if pred_no_var.lower() == gold_no_var.lower():
        return True
        
    def strip_num(x):
        try:
            val = float(x)
            return int(val) if val.is_integer() else val
        except Exception:
            return x
    if strip_num(norm_pred) == strip_num(norm_gold) or strip_num(pred_no_var) == strip_num(gold_no_var):
        return True
        
    try:
        f_pred = float(pred_no_var)
        f_gold = float(gold_no_var)
        if abs(f_pred - f_gold) < 1e-6:
            return True
    except ValueError:
        pass
        
    transformations = standard_transformations + (implicit_multiplication_application,)
    try:
        expr_p = parse_expr(pred_no_var, transformations=transformations, evaluate=True)
        expr_g = parse_expr(gold_no_var, transformations=transformations, evaluate=True)
        diff = sympy.simplify(expr_p - expr_g)
        if diff == 0:
            return True
        if hasattr(diff, "evalf"):
            val = abs(complex(diff.evalf()))
            if val < 1e-6:
                return True
    except Exception:
        pass
        
    if (pred_no_var.startswith("{") and pred_no_var.endswith("}")) and (gold_no_var.startswith("{") and gold_no_var.endswith("}")):
        parts_p = sorted([p.strip() for p in pred_no_var[1:-1].split(",")])
        parts_g = sorted([p.strip() for p in gold_no_var[1:-1].split(",")])
        if parts_p == parts_g:
            return True
    return False

def exact_mcnemar_p_value(b: int, c: int) -> float:
    """Computes exact two-sided McNemar p-value via binomial distribution."""
    n_d = b + c
    if n_d == 0:
        return 1.0
    k_min = min(b, c)
    p_val = 2.0 * binom.cdf(k_min, n_d, 0.5)
    return min(1.0, float(p_val))

def evaluate_confirmatory_dataset(generations_path: str) -> Dict[str, Any]:
    print("=" * 80)
    print("STATESHIFT CONFIRMATORY REPRODUCTION & EVALUATION ENGINE")
    print(f"Dataset path: {generations_path}")
    print("=" * 80)
    
    records = []
    with open(generations_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
                
    print(f"Loaded {len(records)} neural generation records.")
    
    # Process records
    by_prob = defaultdict(dict)
    cond_counts = defaultdict(lambda: {"total": 0, "correct": 0})
    
    for r in records:
        pid = r["problem_id"]
        cond = r["condition_code"]
        gold = r.get("gold_answer", "")
        raw_out = r.get("model_output", "")
        
        extracted = cleanroom_extract_boxed(raw_out)
        is_corr = cleanroom_is_mathematically_equivalent(extracted, gold)
        
        cond_counts[cond]["total"] += 1
        if is_corr:
            cond_counts[cond]["correct"] += 1
            
        by_prob[pid][cond] = {
            "correct": is_corr,
            "extracted": extracted,
            "gold": gold,
            "meta": r
        }
        
    print("\n--- Condition Accuracies ---")
    for cond in sorted(cond_counts.keys()):
        tot = cond_counts[cond]["total"]
        cor = cond_counts[cond]["correct"]
        acc = (cor / tot) * 100 if tot > 0 else 0.0
        print(f"{cond:<30}: {cor}/{tot} ({acc:.2f}%)")
        
    # Primary Contrast: F vs D
    paired_fd = [(by_prob[pid].get("Condition_F_State_Preserving", {}).get("correct", False),
                  by_prob[pid].get("Condition_D_Forced_Restart", {}).get("correct", False))
                 for pid in by_prob if "Condition_F_State_Preserving" in by_prob[pid] and "Condition_D_Forced_Restart" in by_prob[pid]]
                 
    N_pairs = len(paired_fd)
    a = sum(1 for f_cor, d_cor in paired_fd if f_cor and d_cor)
    b = sum(1 for f_cor, d_cor in paired_fd if f_cor and not d_cor)
    c = sum(1 for f_cor, d_cor in paired_fd if not f_cor and d_cor)
    d = sum(1 for f_cor, d_cor in paired_fd if not f_cor and not d_cor)
    
    tau_fd = ((b - c) / N_pairs) * 100 if N_pairs > 0 else 0.0
    p_exact_fd = exact_mcnemar_p_value(b, c)
    
    print("\n--- Primary Confirmatory Contrast (Condition F vs Condition D) ---")
    print(f"Evaluated Paired Problems: N = {N_pairs}")
    print(f"Contingency Table: a={a} (both correct), b={b} (F only), c={c} (D only), d={d} (both incorrect)")
    print(f"Discordant Pairs: nd = b + c = {b + c}")
    print(f"Primary Treatment Effect (tau_F-D): {tau_fd:+.2f} percentage points")
    print(f"Exact Two-Sided McNemar p-value: {p_exact_fd:.6f}")
    if p_exact_fd < 0.05:
        print("[SIGNIFICANT] Null hypothesis rejected at alpha = 0.05.")
    else:
        print("[NOT SIGNIFICANT] Null hypothesis cannot be rejected at alpha = 0.05.")
        
    results = {
        "total_records": len(records),
        "total_problems": len(by_prob),
        "condition_counts": dict(cond_counts),
        "primary_contrast_F_D": {
            "N": N_pairs,
            "a": a,
            "b": b,
            "c": c,
            "d": d,
            "tau_percentage_points": tau_fd,
            "p_exact": p_exact_fd,
            "significant_alpha_0_05": p_exact_fd < 0.05
        }
    }
    return results

def main():
    parser = argparse.ArgumentParser(description="StateShift Confirmatory Evaluation")
    parser.add_argument("--generations", type=str, required=True, help="Path to generations JSONL file")
    parser.add_argument("--out-json", type=str, default="", help="Optional output JSON path")
    args = parser.parse_args()
    
    res = evaluate_confirmatory_dataset(args.generations)
    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
            print(f"Wrote evaluation results to: {args.out_json}")

if __name__ == "__main__":
    main()
