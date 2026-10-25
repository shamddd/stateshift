#!/usr/bin/env python3
"""
StateShift Transactional Checkpoint Manager (Mission 15.4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Guarantees atomic promotion and monotonic dataset preservation:
- Pulls to temporary file with fsync
- Validates JSONL syntax, required metadata, condition, prompt hash, and manifest membership
- Enforces strict monotonic progression (prevents regression in completed request count)
- Prevents conflicting/contradictory records for existing requests
- Promotes atomically via os.replace
- Preserves previous valid snapshot on any validation or transfer failure
"""

import os
import sys
import json
import hashlib
import time
from typing import Dict, Any, List, Set, Tuple, Optional


class TransactionalCheckpointError(Exception):
    pass


class TransactionalCheckpointManager:
    MANDATORY_FIELDS = {
        "request_id", "problem_id", "condition_code", "prompt_sha256", "gold_answer",
        "model_id", "model_revision", "tokenizer_revision", "inference_engine",
        "temperature", "max_tokens", "seed", "sampling_mode", "completion_status",
        "finish_reason", "source_type", "experiment_id", "manifest_hash",
        "generation_timestamp", "model_output"
    }

    def __init__(self, target_checkpoint_path: str, manifest_path: str):
        self.target_checkpoint_path = target_checkpoint_path
        self.manifest_path = manifest_path
        self.backup_checkpoint_path = target_checkpoint_path + ".bak"
        self.receipt_path = target_checkpoint_path + ".receipt.json"

        self.expected_requests: Dict[str, Dict[str, Any]] = {}
        self.manifest_sha256: str = ""
        self._load_manifest()

        # In-memory index of currently promoted valid checkpoint
        self.promoted_records: Dict[str, Dict[str, Any]] = {}
        self._load_existing_target()

    def _load_manifest(self):
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")
        with open(self.manifest_path, "rb") as f:
            raw = f.read()
            self.manifest_sha256 = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw.decode("utf-8"))
        for req in data.get("requests", []):
            self.expected_requests[req["request_id"]] = req

    def _load_existing_target(self):
        if os.path.exists(self.target_checkpoint_path):
            try:
                valid_records = {}
                with open(self.target_checkpoint_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line_str = line.strip()
                        if line_str:
                            rec = json.loads(line_str)
                            valid_records[rec["request_id"]] = rec
                self.promoted_records = valid_records
            except Exception:
                self.promoted_records = {}

    def validate_candidate_file(self, temp_candidate_path: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Thoroughly validates a candidate snapshot file on physical disk before promotion.
        Returns: (is_valid: bool, parsed_records: List[Dict], rejection_reason: str)
        """
        if not os.path.exists(temp_candidate_path):
            return False, [], "Candidate snapshot file does not exist on disk."

        try:
            with open(temp_candidate_path, "rb") as f:
                raw_bytes = f.read()
        except Exception as e:
            return False, [], f"Candidate file unreadable: {e}"

        if len(raw_bytes) == 0:
            return False, [], "Candidate file is completely empty."

        lines = raw_bytes.decode("utf-8", errors="replace").splitlines()
        candidate_records: List[Dict[str, Any]] = []
        seen_ids: Set[str] = set()

        for line_no, line in enumerate(lines, 1):
            line_str = line.strip()
            if not line_str:
                continue

            try:
                rec = json.loads(line_str)
            except json.JSONDecodeError as jde:
                return False, [], f"Line {line_no}: JSON decode failure (truncated/corrupted line): {jde}"

            if not isinstance(rec, dict):
                return False, [], f"Line {line_no}: Record is not a valid JSON object."

            missing = self.MANDATORY_FIELDS - set(rec.keys())
            if missing:
                return False, [], f"Line {line_no}: Missing required metadata keys: {sorted(list(missing))}."

            rid = rec["request_id"]
            if rid in seen_ids:
                return False, [], f"Line {line_no}: Duplicate request_id '{rid}' in snapshot."
            seen_ids.add(rid)

            if rid not in self.expected_requests:
                return False, [], f"Line {line_no}: request_id '{rid}' not in frozen manifest."

            exp_req = self.expected_requests[rid]
            if rec["condition_code"] != exp_req["condition_code"]:
                return False, [], f"Line {line_no} ({rid}): Condition mismatch: {rec['condition_code']} vs {exp_req['condition_code']}."

            if rec["prompt_sha256"] != exp_req["prompt_sha256"]:
                return False, [], f"Line {line_no} ({rid}): Prompt hash mismatch with manifest request."

            if rec["source_type"] != "REAL_MODEL_INFERENCE":
                return False, [], f"Line {line_no} ({rid}): Invalid source_type '{rec['source_type']}'. Must be REAL_MODEL_INFERENCE."

            if rec["completion_status"] not in ["COMPLETED", "TRUNCATED", "FAILED"]:
                return False, [], f"Line {line_no} ({rid}): Invalid completion_status '{rec['completion_status']}'."

            out = rec.get("model_output", "")
            if not out or len(out.strip()) == 0:
                return False, [], f"Line {line_no} ({rid}): Model output is empty."

            candidate_records.append(rec)

        # Monotonicity checks against currently promoted checkpoint
        current_valid_count = len(self.promoted_records)
        new_valid_count = len(candidate_records)

        # Rule 1: A candidate snapshot cannot regress in count
        if new_valid_count < current_valid_count:
            return False, [], (
                f"Regression rejection: candidate snapshot contains {new_valid_count} valid records, "
                f"which is fewer than the existing promoted checkpoint ({current_valid_count} records)."
            )

        # Rule 2: Existing records cannot be silently contradicted or altered
        new_records_map = {r["request_id"]: r for r in candidate_records}
        for rid, existing_rec in self.promoted_records.items():
            if rid not in new_records_map:
                return False, [], f"Data loss rejection: existing completed request_id '{rid}' is missing from candidate snapshot."
            new_rec = new_records_map[rid]
            if new_rec["model_output"] != existing_rec["model_output"]:
                return False, [], f"Contradiction rejection: model_output for request_id '{rid}' differs from previously promoted checkpoint."

        return True, candidate_records, "Candidate validated successfully."

    def promote_candidate_checkpoint(self, temp_candidate_path: str) -> Tuple[bool, int, str]:
        """
        Validates, backs up, and atomically promotes the candidate file.
        Returns: (success: bool, total_promoted_records: int, message: str)
        """
        is_valid, records, reason = self.validate_candidate_file(temp_candidate_path)
        if not is_valid:
            # Clean up temp file safely and preserve existing checkpoint
            try:
                if os.path.exists(temp_candidate_path):
                    os.remove(temp_candidate_path)
            except Exception:
                pass
            return False, len(self.promoted_records), f"Promotion rejected: {reason}"

        # 1. Back up existing target if present
        if os.path.exists(self.target_checkpoint_path):
            try:
                import shutil
                shutil.copy2(self.target_checkpoint_path, self.backup_checkpoint_path)
            except Exception as e:
                return False, len(self.promoted_records), f"Failed to create backup checkpoint: {e}"

        # 2. Flush and fsync temp candidate file
        try:
            with open(temp_candidate_path, "a", encoding="utf-8") as f:
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            return False, len(self.promoted_records), f"Failed to fsync candidate file: {e}"

        # 3. Atomic replacement
        try:
            os.replace(temp_candidate_path, self.target_checkpoint_path)
        except Exception as e:
            return False, len(self.promoted_records), f"Atomic os.replace failed: {e}"

        # 4. Update in-memory index
        self.promoted_records = {r["request_id"]: r for r in records}

        # 5. Commit cryptographic promotion receipt
        with open(self.target_checkpoint_path, "rb") as f:
            chk_sha256 = hashlib.sha256(f.read()).hexdigest()

        receipt = {
            "checkpoint_sha256": chk_sha256,
            "manifest_sha256": self.manifest_sha256,
            "total_promoted_records": len(self.promoted_records),
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "PROMOTED_VALID"
        }
        tmp_receipt = self.receipt_path + ".tmp"
        with open(tmp_receipt, "w", encoding="utf-8") as rf:
            json.dump(receipt, rf, indent=2)
            rf.flush()
            os.fsync(rf.fileno())
        os.replace(tmp_receipt, self.receipt_path)

        return True, len(self.promoted_records), f"Successfully promoted checkpoint ({len(self.promoted_records)} records)."
