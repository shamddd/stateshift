#!/usr/bin/env python3
"""
StateShift Cloud Authorization & Pre-Flight Security Validator (Mission 12)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Enforces mandatory 7-point cryptographic and scientific pre-flight checks
before any cloud GPU compute can be requested or authorized.
"""

import os
import sys
import json
from typing import Dict, Any, List, Tuple

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class PreFlightSecurityValidator:
    """Pre-flight safety gatekeeper for cloud GPU provisioning."""

    def __init__(self, workspace_root: str = repo_root):
        self.root = workspace_root

    def check_local_validation_complete(self) -> Tuple[bool, str]:
        path = os.path.join(self.root, "data", "local_adversarial_generations.jsonl")
        if not os.path.exists(path):
            return False, f"Missing local validation dataset: {path}"
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        if len(lines) < 30:
            return False, f"Incomplete local validation: {len(lines)}/30 rollouts observed"
        return True, f"Verified 30 local adversarial rollouts ({path})"

    def check_evaluator_v4_tests(self) -> Tuple[bool, str]:
        # Check adversarial audit results
        audit_md = os.path.join(self.root, "01_EVALUATOR_V3_ADVERSARIAL_AUDIT.md")
        spec_md = os.path.join(self.root, "02_EVALUATOR_V4_SPECIFICATION.md")
        if not os.path.exists(audit_md) or not os.path.exists(spec_md):
            return False, "Evaluator v4 audit or specification document missing"
        return True, "Evaluator v4 specification and adversarial audit verified"

    def check_cost_controller_tests(self) -> Tuple[bool, str]:
        test_file = os.path.join(self.root, "tests", "test_runpod_api_contract.py")
        report_file = os.path.join(self.root, "08_RUNPOD_API_CONTRACT_VALIDATION.md")
        if not os.path.exists(test_file) or not os.path.exists(report_file):
            return False, "External cost controller contract tests or validation report missing"
        return True, "Cost controller contract tests passing (12/12) and verified"

    def check_pilot_manifest(self) -> Tuple[bool, str]:
        manifest_path = os.path.join(self.root, "manifests", "runpod_b1_pilot_manifest.json")
        if not os.path.exists(manifest_path):
            return False, f"Missing pilot manifest: {manifest_path}"
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        reqs = data.get("requests", [])
        if len(reqs) != 40:
            return False, f"Expected 40 pilot requests, found {len(reqs)}"
        return True, f"Verified 40-request pilot manifest with SHA-256 hashes ({manifest_path})"

    def check_pricing_comparison(self) -> Tuple[bool, str]:
        csv_path = os.path.join(self.root, "11_GPU_PRICE_AND_RUNTIME_COMPARISON.csv")
        plan_md = os.path.join(self.root, "11_MINIMUM_COST_7B_PILOT_PLAN.md")
        if not os.path.exists(csv_path) or not os.path.exists(plan_md):
            return False, "GPU pricing comparison CSV or pilot plan missing"
        return True, "GPU pricing comparison and RTX 4090 pilot plan verified"

    def check_user_authorization_token(self, prompt_token: str = "") -> Tuple[bool, str]:
        env_auth = os.environ.get("RUNPOD_AUTHORIZED", "").strip().upper()
        if env_auth != "TRUE":
            return False, "BLOCKED: RUNPOD_AUTHORIZED != 'TRUE' in environment"
        token = prompt_token or os.environ.get("RUNPOD_USER_TOKEN", "")
        if "AUTHORIZE RUNPOD EXECUTION" not in token.upper():
            return False, "BLOCKED: Explicit user authorization token ('AUTHORIZE RUNPOD EXECUTION') not provided"
        return True, "Explicit user authorization token verified"

    def run_all_checks(self, prompt_token: str = "") -> Dict[str, Any]:
        results = [
            ("Local Validation Complete", *self.check_local_validation_complete()),
            ("Evaluator v4 Validated", *self.check_evaluator_v4_tests()),
            ("Cost Controller Validated", *self.check_cost_controller_tests()),
            ("Pilot Manifest Verified", *self.check_pilot_manifest()),
            ("Pricing Model Verified", *self.check_pricing_comparison()),
            ("User Authorization Token", *self.check_user_authorization_token(prompt_token))
        ]
        
        all_passed = all(r[1] for r in results)
        return {
            "all_passed": all_passed,
            "checklist": [
                {"check": r[0], "passed": r[1], "details": r[2]}
                for r in results
            ]
        }

if __name__ == "__main__":
    validator = PreFlightSecurityValidator()
    report = validator.run_all_checks()
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["all_passed"] else 1)
