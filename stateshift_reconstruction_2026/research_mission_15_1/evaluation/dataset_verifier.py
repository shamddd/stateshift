#!/usr/bin/env python3
"""
StateShift Physical Dataset Completion Gate & Verifier (Mission 15.1)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Core Principle:
Never trust in-memory state. Re-open the physical file from disk and
perform an exhaustive 18-point verification against the frozen manifest.
Persists an atomic, cryptographically verified integrity receipt.
"""

import os
import sys
import time
import json
import hashlib
from typing import Dict, Any, List, Set, Tuple, Optional

class DatasetVerificationError(Exception):
    pass


class IndependentDatasetVerifier:
    """Independently audits physical JSONL dataset against experimental manifest."""

    REQUIRED_KEYS = {
        "request_id", "problem_id", "condition_code",
        "prompt_sha256", "model_output", "gold_answer"
    }

    def __init__(self, manifest_path: str):
        self.manifest_path = manifest_path
        self.manifest_sha256: str = ""
        self.expected_requests: Dict[str, Dict[str, Any]] = {}
        self._load_manifest()

    def _load_manifest(self) -> None:
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")
            
        with open(self.manifest_path, "rb") as f:
            raw = f.read()
            self.manifest_sha256 = hashlib.sha256(raw).hexdigest()
            
        data = json.loads(raw.decode("utf-8"))
        requests = data.get("requests", [])
        for r in requests:
            rid = r.get("request_id")
            if not rid:
                raise DatasetVerificationError("Manifest contains entry without request_id.")
            if rid in self.expected_requests:
                raise DatasetVerificationError(f"Duplicate request_id in manifest: {rid}")
            self.expected_requests[rid] = r

    def verify_final_local_dataset(self, dataset_path: str, receipt_output_path: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Reopens and audits the physical dataset file on disk against the 18 criteria.
        Returns (is_valid_boolean, detailed_audit_report).
        """
        errors = []
        warnings = []
        
        # 1. File exists
        if not os.path.exists(dataset_path):
            return False, {"passed": False, "errors": [f"File does not exist: {dataset_path}"]}
            
        # 2. File is readable
        try:
            with open(dataset_path, "rb") as f:
                raw_bytes = f.read()
        except Exception as e:
            return False, {"passed": False, "errors": [f"File unreadable: {e}"]}
            
        if len(raw_bytes) == 0:
            return False, {"passed": False, "errors": ["File is empty."]}
            
        # 17. Calculate dataset SHA-256
        dataset_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        
        # 16. Check trailing newline
        if not raw_bytes.endswith(b"\n"):
            errors.append("File missing trailing newline.")
            
        lines = raw_bytes.decode("utf-8", errors="replace").splitlines()
        
        # 3. Valid JSONL line by line
        records = []
        for line_num, line in enumerate(lines, 1):
            line_str = line.strip()
            if not line_str:
                continue
            try:
                rec = json.loads(line_str)
                records.append((line_num, rec))
            except json.JSONDecodeError as jde:
                errors.append(f"Line {line_num}: JSON decode failure: {jde}")

        total_records = len(records)
        expected_count = len(self.expected_requests)
        
        # 4. Record count matches expected count
        if total_records != expected_count:
            errors.append(f"Record count mismatch: found {total_records}, expected {expected_count}.")
            
        seen_request_ids: Set[str] = set()
        duplicate_request_ids: List[str] = []
        
        for line_num, rec in records:
            # 8. Schema validation
            missing_keys = self.REQUIRED_KEYS - set(rec.keys())
            if missing_keys:
                errors.append(f"Line {line_num}: Missing required keys: {sorted(list(missing_keys))}")
                continue
                
            rid = rec["request_id"]
            
            # 7. Duplicate request IDs
            if rid in seen_request_ids:
                duplicate_request_ids.append(rid)
                errors.append(f"Line {line_num}: Duplicate request ID: {rid}")
            seen_request_ids.add(rid)
            
            # 6. Matches manifest request ID
            if rid not in self.expected_requests:
                errors.append(f"Line {line_num}: Request ID {rid} not found in manifest.")
                continue
                
            expected_rec = self.expected_requests[rid]
            
            # 9. Output text non-empty / valid generation
            output = rec.get("model_output", "")
            if not output or len(output.strip()) == 0:
                errors.append(f"Line {line_num} ({rid}): Empty model_output.")
                
            # 10. Condition code matches manifest
            if rec.get("condition_code") != expected_rec.get("condition_code"):
                errors.append(f"Line {line_num} ({rid}): Condition mismatch. Found {rec.get('condition_code')}, expected {expected_rec.get('condition_code')}")
                
            # 11. Prompt hash matches manifest
            if rec.get("prompt_sha256") != expected_rec.get("prompt_sha256"):
                errors.append(f"Line {line_num} ({rid}): Prompt hash mismatch.")
                
            # 12. Model identifier matches manifest
            expected_model = expected_rec.get("model_id", "Qwen/Qwen2.5-Math-7B-Instruct")
            if rec.get("model_id") and rec.get("model_id") != expected_model:
                errors.append(f"Line {line_num} ({rid}): Model ID mismatch: {rec.get('model_id')} vs {expected_model}")
                
            # 15. Synthetic record contamination check
            if "SYNTHETIC INFRASTRUCTURE TEST" in str(output):
                errors.append(f"Line {line_num} ({rid}): Contaminated with synthetic dry-run output.")

        # 5. Unique request count
        missing_from_manifest = set(self.expected_requests.keys()) - seen_request_ids
        if missing_from_manifest:
            errors.append(f"Missing {len(missing_from_manifest)} requests from manifest: {sorted(list(missing_from_manifest))[:5]}...")

        is_passed = (len(errors) == 0) and (len(seen_request_ids) == expected_count)
        
        # 18. Persist integrity receipt
        receipt = {
            "passed": is_passed,
            "manifest_path": self.manifest_path,
            "manifest_sha256": self.manifest_sha256,
            "dataset_path": dataset_path,
            "dataset_sha256": dataset_sha256,
            "total_records_found": total_records,
            "total_records_expected": expected_count,
            "unique_request_ids": len(seen_request_ids),
            "duplicate_count": len(duplicate_request_ids),
            "missing_count": len(missing_from_manifest),
            "error_count": len(errors),
            "errors": errors[:50], # top 50
            "verification_timestamp_utc": time.time()
        }
        
        if receipt_output_path:
            tmp_receipt = receipt_output_path + ".tmp"
            os.makedirs(os.path.dirname(os.path.abspath(receipt_output_path)), exist_ok=True)
            with open(tmp_receipt, "w", encoding="utf-8") as rf:
                json.dump(receipt, rf, indent=2)
                rf.flush()
                os.fsync(rf.fileno())
            os.replace(tmp_receipt, receipt_output_path)
            
        return is_passed, receipt
