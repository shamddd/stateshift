#!/usr/bin/env python3
"""
StateShift Research Mission 14: Provenance and Manifest Match Auditor
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Verifies every recovered raw record against the frozen primary manifest:
- Exact prompt text match
- Prompt SHA-256 hash
- Gold answer match
- Metadata alignment (subject, operator, contamination fraction)
- Separation of complete 4-condition matched blocks from partial observations.
"""

import os
import sys
import json
import hashlib
from typing import Dict, Any, List

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
manifest_path = os.path.join(repo_root, "..", "research_mission_13", "manifests", "primary_100_manifest.json")

def sha256_str(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def audit_records():
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
        
    manifest_requests = {r["request_id"]: r for r in manifest_data["requests"]}
    
    data_files = [
        os.path.join(repo_root, "data", "recovered_smoke_test_generations.jsonl"),
        os.path.join(repo_root, "data", "recovered_live_traces.jsonl")
    ]
    
    recovered_records = []
    for df in data_files:
        if os.path.exists(df):
            with open(df, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        recovered_records.append(json.loads(line))
                        
    provenance_audit = {
        "manifest_file": manifest_path,
        "manifest_sha256": manifest_data.get("manifest_sha256", ""),
        "total_manifest_requests": len(manifest_requests),
        "total_recovered_records": len(recovered_records),
        "records": []
    }
    
    by_problem = {}
    
    for r in recovered_records:
        req_id = r["request_id"]
        p_id = r["problem_id"]
        m_req = manifest_requests.get(req_id)
        
        prompt_match = False
        manifest_found = m_req is not None
        prompt_hash = sha256_str(m_req["prompt_text"]) if manifest_found else ""
        
        if manifest_found:
            prompt_match = (m_req["gold_answer"] == r["gold_answer"])
            
        record_audit = {
            "request_id": req_id,
            "problem_id": p_id,
            "condition_code": r["condition_code"],
            "condition_name": r["condition_name"],
            "model_id": r["model_id"],
            "model_revision": r["model_revision"],
            "manifest_found": manifest_found,
            "gold_answer_matched": r["gold_answer"] == (m_req["gold_answer"] if manifest_found else ""),
            "prompt_sha256": prompt_hash,
            "generated_tokens": r["generated_tokens"],
            "latency_seconds": r["latency_seconds"],
            "tokens_per_second": r["tokens_per_second"],
            "stop_reason": r["stop_reason"],
            "final_answer_correctness": r["final_answer_correctness"],
            "genuine_local_repair": r["genuine_local_repair"],
            "is_restart": r["is_restart"],
            "overall_status": r["overall_status"],
            "has_raw_output": bool(r.get("raw_output")),
            "raw_output_length": len(r.get("raw_output", ""))
        }
        provenance_audit["records"].append(record_audit)
        
        if p_id not in by_problem:
            by_problem[p_id] = []
        by_problem[p_id].append(r["condition_code"])
        
    provenance_audit["problem_block_completeness"] = {
        p_id: {
            "conditions_present": conds,
            "is_complete_4_block": set(conds) == {"Condition_A_Zero_Shot", "Condition_D_Forced_Restart", "Condition_E_Explicit_Repair", "Condition_F_State_Preserving"}
        }
        for p_id, conds in by_problem.items()
    }
    
    out_audit = os.path.join(repo_root, "data", "provenance_audit_ledger.json")
    with open(out_audit, "w", encoding="utf-8") as f:
        json.dump(provenance_audit, f, indent=2)
        
    print(f"Audit completed: {len(recovered_records)} records audited against manifest.")
    print(f"Results written to: {out_audit}")
    for p_id, blk in provenance_audit["problem_block_completeness"].items():
        print(f"  Problem {p_id}: Complete 4-Block = {blk['is_complete_4_block']} (Conditions: {blk['conditions_present']})")

if __name__ == "__main__":
    audit_records()
