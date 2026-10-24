# Mandatory Adversarial Fixtures for Evaluator Regression Testing
ADVERSARIAL_FIXTURES = [
  {
    "id": "ADV_01_FALSE_ERROR_CLAIM",
    "name": "False error claim without true detection",
    "description": "Model says 'I found the error in step 1', but fabricates a non-existent flaw on a valid line.",
    "problem": {
      "problem_id": "fixture_adv_01",
      "gold_answer": "42",
      "recovery_state": {
        "step_index": 2,
        "target_assertion": "2x + 10 = 20"
      }
    },
    "raw_output": "I found an error in step 1! The number 2 is not prime. Therefore, the answer is \\boxed{42}.",
    "expected_scientific_classification": {
      "error_detected": false,
      "error_localized": false,
      "genuine_local_repair": false
    }
  },
  {
    "id": "ADV_02_CORRECT_ANSWER_UNREPAIRED_STEP",
    "name": "Correct answer without repairing corrupted step",
    "description": "Model circumvents the corrupted step entirely by switching to an unrelated formula, never repairing the error.",
    "problem": {
      "problem_id": "fixture_adv_02",
      "gold_answer": "10",
      "recovery_state": {
        "step_index": 1,
        "target_assertion": "x + 5 = 20 => x = 12"
      }
    },
    "raw_output": "Using an alternative identity: 2x = 20, so x = \\boxed{10}.",
    "expected_scientific_classification": {
      "error_detected": false,
      "error_localized": false,
      "genuine_local_repair": false,
      "final_answer_correctness": true
    }
  },
  {
    "id": "ADV_03_VALID_PREFIX_INVALID_DEPENDENCY",
    "name": "Preserving valid prefix while propagating invalid dependency",
    "description": "Model retains valid Step 1, but uncritically consumes the corrupted Step 2 in Step 3.",
    "problem": {
      "problem_id": "fixture_adv_03",
      "gold_answer": "15",
      "recovery_state": {
        "step_index": 2,
        "target_assertion": "y = 8"
      }
    },
    "raw_output": "Keeping step 1 where x = 5. Now from step 2 where y = 8, we get x + y = 5 + 8 = \\boxed{13}.",
    "expected_scientific_classification": {
      "error_detected": false,
      "valid_prefix_preservation": true,
      "restart_class": "BLIND_COPYING",
      "genuine_local_repair": false,
      "final_answer_correctness": false
    }
  },
  {
    "id": "ADV_04_SILENT_IMPLICIT_RESTART",
    "name": "Silent implicit restart without keywords or openers",
    "description": "Model restarts from scratch without saying 'start over' or standard openers like 'To solve'.",
    "problem": {
      "problem_id": "fixture_adv_04",
      "gold_answer": "25",
      "recovery_state": {
        "step_index": 2,
        "target_assertion": "5^2 = 30"
      }
    },
    "raw_output": "\\[ f(x) = x^2 \\]\n\\[ f(5) = 5^2 = 25 \\]\nThus \\boxed{25}.",
    "expected_scientific_classification": {
      "is_restart": true,
      "restart_class": "IMPLICIT_RESTART",
      "valid_prefix_preservation": false,
      "genuine_local_repair": false
    }
  },
  {
    "id": "ADV_05_LOCAL_REPAIR_NO_KEYWORDS",
    "name": "Surgical local repair without repair keywords",
    "description": "Model performs exact mathematical correction without words like 'error', 'mistake', 'wrong'.",
    "problem": {
      "problem_id": "fixture_adv_05",
      "gold_answer": "9901",
      "recovery_state": {
        "step_index": 1,
        "target_assertion": "99*99 + 1"
      }
    },
    "raw_output": "99(99 + 1) + 1 = 99 \\cdot 100 + 1 = 9900 + 1 = 9901. Therefore \\boxed{9901}.",
    "expected_scientific_classification": {
      "error_detected": true,
      "error_localized": true,
      "valid_prefix_preservation": true,
      "genuine_local_repair": true
    }
  },
  {
    "id": "ADV_06_PARTIAL_PRESERVE_PARTIAL_RECOMPUTE",
    "name": "Hybrid: partial preservation and partial recomputation",
    "description": "Model retains Step 1, recalculates Step 2 from scratch, and continues.",
    "problem": {
      "problem_id": "fixture_adv_06",
      "gold_answer": "30",
      "recovery_state": {
        "step_index": 2,
        "target_assertion": "2 * 10 = 25"
      }
    },
    "raw_output": "From step 1, a = 10. Recalculating the product: 2 * 10 = 20. Adding 10 yields \\boxed{30}.",
    "expected_scientific_classification": {
      "is_restart": false,
      "restart_class": "PARTIAL_RECOMPUTATION",
      "valid_prefix_preservation": true,
      "genuine_local_repair": true
    }
  },
  {
    "id": "ADV_07_EQUIVALENT_DIFFERENT_SYNTAX",
    "name": "Mathematically equivalent expression with different syntax",
    "description": "1 / (sqrt(2) - 1) is equivalent to sqrt(2) + 1, written with non-trivial algebraic syntax.",
    "problem": {
      "problem_id": "fixture_adv_07",
      "gold_answer": "\\sqrt{2} + 1",
      "recovery_state": {
        "step_index": 1,
        "target_assertion": "rationalize"
      }
    },
    "raw_output": "Rationalizing the denominator gives \\boxed{\\frac{1}{\\sqrt{2}-1}}.",
    "expected_scientific_classification": {
      "final_answer_correctness": true
    }
  },
  {
    "id": "ADV_08_CORRECT_ANSWER_INVALID_REASONING",
    "name": "Lucky correct answer via invalid reasoning (anomalous cancellation)",
    "description": "16/64 = 1/4 achieved by 'canceling the 6s' (mathematically fallacious).",
    "problem": {
      "problem_id": "fixture_adv_08",
      "gold_answer": "1/4",
      "recovery_state": {
        "step_index": 1,
        "target_assertion": "simplify 16/64"
      }
    },
    "raw_output": "In 16/64, we cancel the 6 on the top with the 6 on the bottom, leaving 1/4. Thus \\boxed{1/4}.",
    "expected_scientific_classification": {
      "final_answer_correctness": true,
      "continuation_validity": false,
      "genuine_local_repair": false
    }
  },
  {
    "id": "ADV_09_VALID_UNVERIFIABLE",
    "name": "Mathematically valid but non-elementary step requiring manual adjudication",
    "description": "Invokes a high-level theorem or lemma that cannot be simplified to 0 by SymPy alone.",
    "problem": {
      "problem_id": "fixture_adv_09",
      "gold_answer": "0",
      "recovery_state": {
        "step_index": 1,
        "target_assertion": "integral"
      }
    },
    "raw_output": "By Cauchy's Integral Theorem for a holomorphic function on a simply connected domain, the closed contour integral vanishes: \\boxed{0}.",
    "expected_scientific_classification": {
      "final_answer_correctness": true,
      "status_label": "UNVERIFIED"
    }
  }
]
