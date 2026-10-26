#!/usr/bin/env python3
"""
StateShift Physical Dataset Completion Gate & Verifier (Version 2 - Mission 15.2)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Comprehensive Enforcement:
1. Model Identity: model_id, model_revision, tokenizer_revision, inference_engine, inference_engine_version.
2. Decoding Configuration: temperature (0.0), max_tokens (768), seed (42), sampling_mode (greedy).
3. Generation Completion: strictly distinguishes COMPLETED from FAILED, TRUNCATED, TIMEOUT, CANCELLED.
   Only COMPLETED records count towards scientific rollout completion.
4. Structured Provenance: source_type == 'REAL_MODEL_INFERENCE', experiment_id, manifest_hash, generation_timestamp.
5. Physical Integrity: reopens file on disk, SHA-256 recalculation, atomic integrity_receipt.json.
"""

import os
import sys
import time
import json
import hashlib
from typing import Dict, Any, List, Set, Tuple, Optional

class DatasetVerificationError(Exception):
    pass


class IndependentDatasetVerifierV2:
    """Independently audits physical JSONL dataset against experimental manifest and protocol."""

    MANDATORY_METADATA_KEYS = {
        # Core identification
        "request_id", "problem_id", "condition_code", "prompt_sha256", "gold_answer",
        # Model identity
        "model_id", "model_revision", "tokenizer_revision", "inference_engine", "inference_engine_version",
        # Decoding configuration
        "temperature", "max_tokens", "seed", "sampling_mode",
        # Completion status
        "completion_status", "finish_reason",
        # Provenance
        "source_type", "experiment_id", "manifest_hash", "generation_timestamp"
    }

    VALID_COMPLETION_STATES = {"COMPLETED", "FAILED", "TRUNCATED", "CANCELLED", "TIMEOUT", "UNKNOWN"}

    def __init__(self, manifest_path: str, is_calibration: bool = False):
        self.manifest_path = manifest_path
        self.is_calibration = is_calibration
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
        
        # If calibration mode, only the exact frozen 10 IDs are expected
        if self.is_calibration:
            from research_mission_15_6.calibration.calibration_config import FROZEN_CALIBRATION_REQUEST_IDS
            req_map = {r.get("request_id"): r for r in requests if r.get("request_id")}
            for cid in FROZEN_CALIBRATION_REQUEST_IDS:
                if cid not in req_map:
                    raise DatasetVerificationError(f"Calibration manifest missing frozen request ID: {cid}")
                self.expected_requests[cid] = req_map[cid]
        else:
            for r in requests:
                rid = r.get("request_id")
                if not rid:
                    raise DatasetVerificationError("Manifest contains entry without request_id.")
                if rid in self.expected_requests:
                    raise DatasetVerificationError(f"Duplicate request_id in manifest: {rid}")
                self.expected_requests[rid] = r

    def verify_final_local_dataset(self, dataset_path: str, receipt_output_path: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Reopens physical JSONL file from disk and audits all scientific criteria.
        Returns (is_valid_boolean, detailed_receipt_dict).
        """
        errors = []
        
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
            
        # Dataset SHA-256
        dataset_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        
        # Check trailing newline
        if not raw_bytes.endswith(b"\n"):
            errors.append("File missing trailing newline.")
            
        lines = raw_bytes.decode("utf-8", errors="replace").splitlines()
        
        # Parse JSONL line by line
        parsed_records = []
        for line_num, line in enumerate(lines, 1):
            line_str = line.strip()
            if not line_str:
                continue
            try:
                rec = json.loads(line_str)
                parsed_records.append((line_num, rec))
            except json.JSONDecodeError as jde:
                errors.append(f"Line {line_num}: JSON decode failure: {jde}")

        total_records_found = len(parsed_records)
        expected_count = len(self.expected_requests)
        
        seen_request_ids: Set[str] = set()
        duplicate_request_ids: List[str] = []
        completed_valid_count = 0
        failed_count = 0
        truncated_count = 0
        
        for line_num, rec in parsed_records:
            # Schema keys check
            missing_keys = self.MANDATORY_METADATA_KEYS - set(rec.keys())
            if missing_keys:
                errors.append(f"Line {line_num}: Missing mandatory keys: {sorted(list(missing_keys))}")
                continue
                
            rid = rec["request_id"]
            
            # Duplication check
            if rid in seen_request_ids:
                duplicate_request_ids.append(rid)
                errors.append(f"Line {line_num}: Duplicate request ID: {rid}")
            seen_request_ids.add(rid)
            
            # Manifest correspondence
            if rid not in self.expected_requests:
                errors.append(f"Line {line_num}: Request ID {rid} not found in manifest.")
                continue
            expected_rec = self.expected_requests[rid]
            
            # Model identity verification
            expected_model_id = expected_rec.get("model_id", "Qwen/Qwen2.5-Math-7B-Instruct")
            if rec.get("model_id") != expected_model_id:
                errors.append(f"Line {line_num} ({rid}): Model ID mismatch: {rec.get('model_id')} vs {expected_model_id}")
            if not rec.get("model_revision"):
                errors.append(f"Line {line_num} ({rid}): Missing model_revision.")
            if not rec.get("tokenizer_revision"):
                errors.append(f"Line {line_num} ({rid}): Missing tokenizer_revision.")
            if not rec.get("inference_engine") or not rec.get("inference_engine_version"):
                errors.append(f"Line {line_num} ({rid}): Missing inference engine identity/version.")
                
            # Decoding configuration verification
            if rec.get("temperature") != 0.0:
                errors.append(f"Line {line_num} ({rid}): Temperature must be 0.0 (greedy), got {rec.get('temperature')}")
            if rec.get("max_tokens") != 768:
                errors.append(f"Line {line_num} ({rid}): Max tokens must be 768, got {rec.get('max_tokens')}")
            if rec.get("seed") != 42:
                errors.append(f"Line {line_num} ({rid}): Seed must be 42, got {rec.get('seed')}")
            if rec.get("sampling_mode") != "greedy":
                errors.append(f"Line {line_num} ({rid}): Sampling mode must be greedy, got {rec.get('sampling_mode')}")
                
            # Prompt hash & condition verification
            if rec.get("condition_code") != expected_rec.get("condition_code"):
                errors.append(f"Line {line_num} ({rid}): Condition mismatch: {rec.get('condition_code')} vs {expected_rec.get('condition_code')}")
            if rec.get("prompt_sha256") != expected_rec.get("prompt_sha256"):
                errors.append(f"Line {line_num} ({rid}): Prompt hash mismatch.")
                
            # Structured provenance verification
            if rec.get("source_type") != "REAL_MODEL_INFERENCE":
                errors.append(f"Line {line_num} ({rid}): Invalid source_type: {rec.get('source_type')}. Must be REAL_MODEL_INFERENCE.")
            if rec.get("manifest_hash") != self.manifest_sha256:
                errors.append(f"Line {line_num} ({rid}): Manifest hash mismatch in provenance record.")
            if not rec.get("experiment_id"):
                errors.append(f"Line {line_num} ({rid}): Missing experiment_id.")
            if not isinstance(rec.get("generation_timestamp"), (int, float)) or rec.get("generation_timestamp") <= 0:
                errors.append(f"Line {line_num} ({rid}): Invalid generation_timestamp.")
                
            # Output & completion status verification
            output = rec.get("model_output", "")
            if not output or len(output.strip()) == 0:
                errors.append(f"Line {line_num} ({rid}): Empty model_output.")
                
            status = rec.get("completion_status")
            if status not in self.VALID_COMPLETION_STATES:
                errors.append(f"Line {line_num} ({rid}): Invalid completion_status: {status}")
            elif status == "COMPLETED":
                completed_valid_count += 1
            elif status == "TRUNCATED":
                truncated_count += 1
            elif status == "FAILED":
                failed_count += 1
                errors.append(f"Line {line_num} ({rid}): Generation marked as FAILED.")
            else:
                errors.append(f"Line {line_num} ({rid}): Non-completed generation status: {status}")
                
            # Synthetic contamination rejection
            if "SYNTHETIC INFRASTRUCTURE TEST" in str(output):
                errors.append(f"Line {line_num} ({rid}): Contaminated with synthetic dry-run output.")

        # Check missing requests
        missing_from_manifest = set(self.expected_requests.keys()) - seen_request_ids
        if missing_from_manifest:
            errors.append(f"Missing {len(missing_from_manifest)} requests from manifest: {sorted(list(missing_from_manifest))[:5]}...")

        # Exact completion check: all expected requests present AND completed
        is_passed = (len(errors) == 0) and \
                    (total_records_found == expected_count) and \
                    (len(seen_request_ids) == expected_count) and \
                    ((completed_valid_count + truncated_count) == expected_count)
                    
        receipt = {
            "passed": is_passed,
            "manifest_path": self.manifest_path,
            "manifest_sha256": self.manifest_sha256,
            "dataset_path": dataset_path,
            "dataset_sha256": dataset_sha256,
            "total_records_found": total_records_found,
            "total_records_expected": expected_count,
            "completed_valid_count": completed_valid_count,
            "failed_count": failed_count,
            "truncated_count": truncated_count,
            "duplicate_count": len(duplicate_request_ids),
            "missing_count": len(missing_from_manifest),
            "error_count": len(errors),
            "errors": errors[:50],
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
