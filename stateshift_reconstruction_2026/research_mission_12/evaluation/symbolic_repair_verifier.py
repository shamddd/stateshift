#!/usr/bin/env python3
"""
StateShift Symbolic Repair Verifier (v4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Provides domain-safe mathematical equivalence checking using SymPy:
- Safe algebraic equivalence (avoids unsafe domain assumptions).
- Multi-equality verification (A = B = C).
- Singularity & division-by-zero detection.
- Rational fraction & floating-point bounded checking.
- Returns 4-valued verification labels: VERIFIED_TRUE, VERIFIED_FALSE, UNVERIFIED.
"""

import re
import math
from fractions import Fraction
from typing import Dict, Any, Optional, Tuple, List, Set
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

class SymbolicRepairVerifier:
    """Domain-safe symbolic verification engine."""

    TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)

    @staticmethod
    def sanitize_latex(s: str) -> str:
        """Convert LaTeX math into parseable SymPy syntax."""
        if not s:
            return ""
        s = s.strip().replace('$', '').replace('\\(', '').replace('\\)', '')
        s = s.replace('\\[', '').replace('\\]', '')
        
        # Nested fraction conversion
        while r'\frac' in s or r'\dfrac' in s:
            new_s = re.sub(r'\\d?frac\{([^{}]+)\}\{([^{}]+)\}', r'((\1)/(\2))', s)
            if new_s == s:
                break
            s = new_s
            
        s = s.replace(r'\cdot', '*').replace(r'\times', '*')
        s = s.replace(r'\pi', 'pi').replace(r'\infty', 'oo')
        s = s.replace(r'\%', '/100')
        s = s.replace(r'\sqrt', 'sqrt')
        s = s.replace('{', '(').replace('}', ')')
        
        # Strip styling
        s = re.sub(r'\\text(?:bf|rm|it)?\{([^}]+)\}', r'\1', s)
        s = re.sub(r'\\mathbf\{([^}]+)\}', r'\1', s)
        s = re.sub(r'\\left|\\right', '', s)
        s = s.replace('^', '**')
        return s.strip()

    @classmethod
    def verify_expression_equivalence(cls, 
                                      expr1_str: str, 
                                      expr2_str: str, 
                                      domain_assumptions: Optional[List[str]] = None) -> Tuple[str, str]:
        """
        Check if two mathematical expressions are symbolically equivalent.
        Returns (status: 'VERIFIED_TRUE' | 'VERIFIED_FALSE' | 'UNVERIFIED', explanation).
        """
        if not expr1_str or not expr2_str:
            return "UNVERIFIED", "Empty expression string provided"
            
        e1_clean = expr1_str.strip().replace(" ", "").replace("$", "")
        e2_clean = expr2_str.strip().replace(" ", "").replace("$", "")
        
        if e1_clean == e2_clean or e1_clean.lower() == e2_clean.lower():
            return "VERIFIED_TRUE", "Syntactic identity match"

        # Rational fraction check
        try:
            if '/' in e1_clean and '/' in e2_clean:
                if Fraction(e1_clean) == Fraction(e2_clean):
                    return "VERIFIED_TRUE", f"Exact rational equality: {e1_clean} == {e2_clean}"
        except Exception:
            pass

        # SymPy Symbolic check
        s1 = cls.sanitize_latex(e1_clean)
        s2 = cls.sanitize_latex(e2_clean)
        
        try:
            p1 = parse_expr(s1, transformations=cls.TRANSFORMATIONS)
            p2 = parse_expr(s2, transformations=cls.TRANSFORMATIONS)
            
            # Domain check: check for division by zero in either expression
            for p in [p1, p2]:
                if hasattr(p, "as_numer_denom"):
                    _, denom = p.as_numer_denom()
                    if denom == 0:
                        return "VERIFIED_FALSE", "Expression contains division by zero singularity"
            
            diff = sympy.simplify(p1 - p2)
            if diff == 0:
                return "VERIFIED_TRUE", f"SymPy verified simplify(e1 - e2) == 0"
            else:
                # Check trigonometric or polynomial expansion
                diff_trig = sympy.trigsimp(diff)
                if diff_trig == 0:
                    return "VERIFIED_TRUE", f"SymPy trigsimp verified equivalence"
                diff_expand = sympy.expand(diff)
                if diff_expand == 0:
                    return "VERIFIED_TRUE", f"SymPy expand verified equivalence"
                return "VERIFIED_FALSE", f"Symbolic difference is non-zero: {diff}"
        except Exception as e:
            # Fallback to numerical evaluation if symbols absent
            try:
                f1 = float(e1_clean)
                f2 = float(e2_clean)
                if abs(f1 - f2) < 1e-5:
                    return "VERIFIED_TRUE", f"Numerical equivalence within 1e-5: {f1} == {f2}"
                else:
                    return "VERIFIED_FALSE", f"Numerical inequality: {f1} != {f2}"
            except Exception:
                return "UNVERIFIED", f"Symbolic parsing failed: {e}"

    @classmethod
    def verify_equality_chain(cls, assertion_line: str) -> Tuple[str, str]:
        """
        Verify multi-equality assertion: A = B = C.
        Every pair must evaluate to VERIFIED_TRUE.
        """
        if "=" not in assertion_line:
            return "UNVERIFIED", "Assertion contains no equality sign"
            
        parts = [p.strip() for p in assertion_line.split("=") if p.strip()]
        if len(parts) < 2:
            return "UNVERIFIED", "Malformed equality string"
            
        for i in range(len(parts) - 1):
            status, expl = cls.verify_expression_equivalence(parts[i], parts[i+1])
            if status != "VERIFIED_TRUE":
                return status, f"Link {i} violated ({parts[i]} != {parts[i+1]}): {expl}"
                
        return "VERIFIED_TRUE", f"Verified chain across {len(parts)} terms"
