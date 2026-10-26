#!/usr/bin/env python3
"""
StateShift Mathematical Oracles (v3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Provides rigorous symbolic and numerical mathematical verification using SymPy,
exact rational arithmetic, and domain-specific algebraic equivalence checkers.
Replaces naive string matching and regex-based equality checks.
"""

import re
import math
from fractions import Fraction
from typing import Optional, Any, Union, Tuple, List
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

class MathematicalOracle:
    """Rigorous mathematical oracle for symbolic, algebraic, and numerical verification."""
    
    TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)

    @staticmethod
    def extract_boxed_answer(text: str) -> Optional[str]:
        """Extract content from LaTeX \\boxed{...} or fallback patterns."""
        if not text:
            return None
        
        # 1. Recursive / nested brace matching for \boxed{...}
        matches = []
        pattern = r'\\boxed\{'
        for m in re.finditer(pattern, text):
            start = m.end()
            depth = 1
            idx = start
            while idx < len(text) and depth > 0:
                if text[idx] == '{':
                    depth += 1
                elif text[idx] == '}':
                    depth -= 1
                idx += 1
            if depth == 0:
                matches.append(text[start:idx-1].strip())
        
        if matches:
            return matches[-1]
            
        # 2. Loose boxed{...} without backslash
        pattern_loose = r'(?<!\\)boxed\{'
        for m in re.finditer(pattern_loose, text):
            start = m.end()
            depth = 1
            idx = start
            while idx < len(text) and depth > 0:
                if text[idx] == '{':
                    depth += 1
                elif text[idx] == '}':
                    depth -= 1
                idx += 1
            if depth == 0:
                matches.append(text[start:idx-1].strip())
                
        if matches:
            return matches[-1]

        # 3. Fallback to explicit concluding sentences
        fallback_patterns = [
            r'(?:final answer is|answer is|the answer is|equal to|value is)[:\s]*\$?([^\n\$\.]+)\$?',
            r'(?:therefore|thus|hence|so)[,\s]*\$?([^\n\$\.]+)\$?'
        ]
        for pat in fallback_patterns:
            founds = re.findall(pat, text, flags=re.IGNORECASE)
            if founds:
                ans = founds[-1].strip().rstrip('.')
                if len(ans) > 0 and len(ans) < 100:
                    return ans
                    
        return None

    @staticmethod
    def sanitize_latex(s: str) -> str:
        """Convert LaTeX math notation into parseable SymPy expression syntax."""
        if not s:
            return ""
        s = s.strip().replace('$', '').replace('\\(', '').replace('\\)', '')
        s = s.replace('\\[', '').replace('\\]', '')
        
        # Handle \frac{a}{b} and \dfrac{a}{b}
        # Nested fraction support
        while r'\frac' in s or r'\dfrac' in s:
            new_s = re.sub(r'\\d?frac\{([^{}]+)\}\{([^{}]+)\}', r'((\1)/(\2))', s)
            if new_s == s:
                break
            s = new_s
            
        # Basic LaTeX symbols
        s = s.replace(r'\cdot', '*').replace(r'\times', '*')
        s = s.replace(r'\pi', 'pi').replace(r'\infty', 'oo')
        s = s.replace(r'\%', '/100')
        s = s.replace(r'\sqrt', 'sqrt')
        s = s.replace('{', '(').replace('}', ')')
        
        # Remove LaTeX styling commands
        s = re.sub(r'\\text(?:bf|rm|it)?\{([^}]+)\}', r'\1', s)
        s = re.sub(r'\\mathbf\{([^}]+)\}', r'\1', s)
        s = re.sub(r'\\left|\\right', '', s)
        s = s.replace('^', '**')
        s = s.strip()
        return s

    @classmethod
    def verify_symbolic_equivalence(cls, pred: Optional[str], gold: Optional[str]) -> bool:
        """Check whether predicted answer is mathematically equivalent to gold standard."""
        if pred is None or gold is None:
            return False
            
        p_str = pred.strip()
        g_str = gold.strip()
        
        # Direct string equality (fast path)
        if p_str == g_str or p_str.lower() == g_str.lower():
            return True
            
        # Strip spaces and dollar signs
        p_clean = p_str.replace(" ", "").replace("$", "")
        g_clean = g_str.replace(" ", "").replace("$", "")
        if p_clean == g_clean or p_clean.lower() == g_clean.lower():
            return True

        # Coordinate tuple / Interval check: e.g. (2, 3) or [0, 4)
        if (p_clean.startswith('(') and p_clean.endswith(')')) or (p_clean.startswith('[') and p_clean.endswith(']')):
            if p_clean[0] == g_clean[0] and p_clean[-1] == g_clean[-1]:
                p_parts = p_clean[1:-1].split(',')
                g_parts = g_clean[1:-1].split(',')
                if len(p_parts) == len(g_parts):
                    if all(cls.verify_symbolic_equivalence(p_sub, g_sub) for p_sub, g_sub in zip(p_parts, g_parts)):
                        return True

        # Rational fraction check
        try:
            if '/' in p_clean and '/' in g_clean:
                if Fraction(p_clean) == Fraction(g_clean):
                    return True
        except Exception:
            pass

        # SymPy Symbolic check
        p_san = cls.sanitize_latex(p_clean)
        g_san = cls.sanitize_latex(g_clean)
        
        try:
            p_sym = parse_expr(p_san, transformations=cls.TRANSFORMATIONS)
            g_sym = parse_expr(g_san, transformations=cls.TRANSFORMATIONS)
            diff = sympy.simplify(p_sym - g_sym)
            if diff == 0:
                return True
        except Exception:
            pass

        # Numerical evaluation fallback
        try:
            p_float = float(p_clean)
            g_float = float(g_clean)
            if abs(p_float - g_float) < 1e-5:
                return True
        except Exception:
            pass
            
        return False

    @classmethod
    def verify_assertion_validity(cls, assertion: str) -> Tuple[bool, str]:
        """
        Verify whether an algebraic assertion (e.g., '99 * 100 = 9900') is mathematically true.
        Returns (is_valid, explanation).
        """
        if not assertion:
            return False, "Empty assertion"
            
        # Check equality assertions: A = B
        if '=' in assertion:
            sides = assertion.split('=')
            if len(sides) == 2:
                lhs_str, rhs_str = sides[0].strip(), sides[1].strip()
                if cls.verify_symbolic_equivalence(lhs_str, rhs_str):
                    return True, f"SymPy verified {lhs_str} == {rhs_str}"
                else:
                    return False, f"Equality violated: {lhs_str} != {rhs_str}"
                    
        return False, "Non-equality assertion requires trace analysis"
