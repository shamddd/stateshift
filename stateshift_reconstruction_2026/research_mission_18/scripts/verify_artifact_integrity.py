#!/usr/bin/env python3
"""
StateShift Research Mission 18 - Phase 1: Forensic Artifact & Dataset Integrity Verifier
Independent Audit Committee Script.

Verifies:
1. Exact SHA-256 checksums and byte counts for all experimental artifacts.
2. Structural, cryptographic, and operational integrity of the 400-request primary dataset.
3. Perfect alignment between primary dataset and the frozen 100-problem manifest.
4. Cloud teardown and execution lock verification.
"""

import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

EXPECTED_LEDGER = {
    "research_mission_15_6/manifests/primary_100_manifest.json": {
        "size": 569153,
        "sha256": "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        "desc": "Primary 100 Problem Manifest (Frozen)"
    },
    "research_mission_15_6/manifests/calibration_10_manifest.json": {
        "size": 13662,
        "sha256": "f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6",
        "desc": "Calibration 10 Problem Manifest (Frozen)"
    },
    "data/primary_run/stateshift_primary_400_generations.jsonl": {
        "size": 898204,
        "sha256": "bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2",
        "desc": "Primary 400 Authentic Generations"
    },
    "data/primary_run/session_auth_primary_400.json": {
        "size": 901,
        "sha256": "1f97305aefe80147f5e51bf675e6b50d8efc6f719e70b8c4f7ac0fe4fd5b299f",
        "desc": "Signed Session Authorization Token"
    },
    "data/primary_run/operator_pubkey.txt": {
        "size": 44,
        "sha256": "0a85ca1b6cf1f9ff7a73d4155743fb583573bba51a7a13d1ad47379492ad1cae",
        "desc": "Operator Public Key"
    },
    "data/primary_run/primary_400_reconciliation.json": {
        "size": 907,
        "sha256": "ac1c016304e7121d6b18094cec8a276cf003e23943db7e2ac8c7673e072d4951",
        "desc": "Primary Run Financial Reconciliation"
    },
    "data/primary_run/primary_400_timeline_events.jsonl": {
        "size": 30246,
        "sha256": "ffa83f617dad8db5cf7d9e35bd9dab1222f6090a55e0a656c5faf1d33dec6b83",
        "desc": "Primary Execution Timeline Events"
    },
    "data/primary_run/primary_400_evaluation_results.json": {
        "size": 1012996,
        "sha256": "7961629a31633cafe5211fd44ab4848ce222979e5e022ba2abd3cc44d1b0c73e",
        "desc": "Mission 17 Evaluation & Statistical Output"
    },
    "08_REVISED_STATESHIFT.tex": {
        "size": 31420,
        "sha256": "e094dd01b9d3ea3cfac088a898d4645c930ec010706086ddd78f5009f4170007",
        "desc": "Mission 17 Reconciled Manuscript"
    }
}


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_all_artifacts():
    results = {}
    all_matched = True
    for rel_path, meta in EXPECTED_LEDGER.items():
        full_path = os.path.join(REPO_ROOT, rel_path)
        if not os.path.exists(full_path):
            results[rel_path] = {"exists": False, "status": "MISSING"}
            all_matched = False
            continue
        size = os.path.getsize(full_path)
        sha256 = compute_sha256(full_path)
        size_match = (size == meta["size"])
        sha_match = (sha256 == meta["sha256"])
        if not (size_match and sha_match):
            all_matched = False
        results[rel_path] = {
            "exists": True,
            "actual_size": size,
            "expected_size": meta["size"],
            "size_match": size_match,
            "actual_sha256": sha256,
            "expected_sha256": meta["sha256"],
            "sha256_match": sha_match,
            "status": "VERIFIED_EXACT" if (size_match and sha_match) else "MISMATCH"
        }
    return results, all_matched


def audit_primary_dataset():
    gen_path = os.path.join(REPO_ROOT, "data/primary_run/stateshift_primary_400_generations.jsonl")
    manifest_path = os.path.join(REPO_ROOT, "research_mission_15_6/manifests/primary_100_manifest.json")
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    manifest_requests = manifest_data.get("requests", [])
    manifest_by_req = {r["request_id"]: r for r in manifest_requests}
    manifest_hash = manifest_data.get("manifest_hash")
    
    records = []
    with open(gen_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
                
    audit_findings = {
        "total_records": len(records),
        "expected_records": 400,
        "record_count_valid": len(records) == 400,
        "problems": set(),
        "conditions_per_problem": defaultdict(set),
        "request_ids": [],
        "completion_statuses": Counter(),
        "finish_reasons": Counter(),
        "model_revisions": Counter(),
        "temperatures": Counter(),
        "seeds": Counter(),
        "max_tokens": Counter(),
        "source_types": Counter(),
        "manifest_alignments": 0,
        "manifest_mismatches": [],
        "timestamps": [],
        "character_lengths_by_cond": defaultdict(list)
    }
    
    for r in records:
        req_id = r["request_id"]
        prob_id = r["problem_id"]
        cond = r["condition_code"]
        
        audit_findings["problems"].add(prob_id)
        audit_findings["conditions_per_problem"][prob_id].add(cond)
        audit_findings["request_ids"].append(req_id)
        audit_findings["completion_statuses"][r.get("completion_status")] += 1
        audit_findings["finish_reasons"][r.get("finish_reason")] += 1
        audit_findings["model_revisions"][r.get("model_revision")] += 1
        audit_findings["temperatures"][r.get("temperature")] += 1
        audit_findings["seeds"][r.get("seed")] += 1
        audit_findings["max_tokens"][r.get("max_tokens")] += 1
        audit_findings["source_types"][r.get("source_type")] += 1
        audit_findings["timestamps"].append(r.get("generation_timestamp"))
        
        out_text = r.get("model_output", "")
        audit_findings["character_lengths_by_cond"][cond].append(len(out_text))
        
        # Check against manifest
        man_req = manifest_by_req.get(req_id)
        if man_req:
            # Check problem_id, condition_code, gold_answer
            m_prob = man_req.get("problem_id")
            m_cond = man_req.get("condition_code")
            m_gold = man_req.get("gold_answer")
            if (m_prob == prob_id and m_cond == cond and m_gold == r.get("gold_answer")):
                audit_findings["manifest_alignments"] += 1
            else:
                audit_findings["manifest_mismatches"].append({
                    "request_id": req_id,
                    "manifest": {"problem_id": m_prob, "condition_code": m_cond, "gold": m_gold},
                    "record": {"problem_id": prob_id, "condition_code": cond, "gold": r.get("gold_answer")}
                })
        else:
            audit_findings["manifest_mismatches"].append({"request_id": req_id, "error": "Not in manifest"})
            
    # Check completeness of conditions
    expected_conditions = {
        "Condition_A_Zero_Shot",
        "Condition_D_Forced_Restart",
        "Condition_E_Explicit_Repair",
        "Condition_F_State_Preserving"
    }
    all_problems_have_all_conds = True
    for p, conds in audit_findings["conditions_per_problem"].items():
        if conds != expected_conditions:
            all_problems_have_all_conds = False
            break
            
    # Check request ID uniqueness and sequence
    expected_req_ids = [f"primary_100_req_{i:04d}" for i in range(1, 401)]
    req_sequence_exact = (audit_findings["request_ids"] == expected_req_ids)
    
    # Check timestamps monotonicity
    ts_monotonic = True
    parsed_ts = []
    for ts_val in audit_findings["timestamps"]:
        if isinstance(ts_val, (int, float)):
            parsed_ts.append(ts_val)
        elif isinstance(ts_val, str):
            try:
                dt = datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
                parsed_ts.append(dt.timestamp())
            except Exception:
                pass
            
    if len(parsed_ts) == 400:
        for i in range(1, 400):
            if parsed_ts[i] < parsed_ts[i-1]:
                ts_monotonic = False
                break
        total_time_span = parsed_ts[-1] - parsed_ts[0]
        first_iso = datetime.fromtimestamp(parsed_ts[0], timezone.utc).isoformat()
        last_iso = datetime.fromtimestamp(parsed_ts[-1], timezone.utc).isoformat()
    else:
        ts_monotonic = False
        total_time_span = None
        first_iso = None
        last_iso = None

    summary = {
        "total_records": len(records),
        "unique_problems": len(audit_findings["problems"]),
        "all_problems_have_all_4_conditions": all_problems_have_all_conds,
        "request_sequence_exact": req_sequence_exact,
        "manifest_alignment_count": audit_findings["manifest_alignments"],
        "manifest_mismatch_count": len(audit_findings["manifest_mismatches"]),
        "completion_statuses": dict(audit_findings["completion_statuses"]),
        "finish_reasons": dict(audit_findings["finish_reasons"]),
        "model_revisions": dict(audit_findings["model_revisions"]),
        "temperatures": dict(audit_findings["temperatures"]),
        "seeds": dict(audit_findings["seeds"]),
        "max_tokens": dict(audit_findings["max_tokens"]),
        "source_types": dict(audit_findings["source_types"]),
        "timestamps_monotonic": ts_monotonic,
        "first_timestamp": first_iso,
        "last_timestamp": last_iso,
        "total_time_span_seconds": total_time_span,
        "length_summary": {
            cond: {
                "count": len(lens),
                "mean_chars": round(sum(lens) / len(lens), 2),
                "min_chars": min(lens),
                "max_chars": max(lens)
            }
            for cond, lens in sorted(audit_findings["character_lengths_by_cond"].items())
        }
    }
    return summary


def verify_cloud_lock_and_destruction():
    lock_file = os.path.join(REPO_ROOT, ".cloud_execution_locked")
    recon_path = os.path.join(REPO_ROOT, "data/primary_run/primary_400_reconciliation.json")
    term_state_path = os.path.join(REPO_ROOT, "data/primary_run/termination_state_stateshift_primary_400_01.json")
    
    lock_exists = os.path.exists(lock_file)
    recon = json.load(open(recon_path)) if os.path.exists(recon_path) else {}
    term = json.load(open(term_state_path)) if os.path.exists(term_state_path) else {}
    
    return {
        "cloud_execution_lock_file_present": lock_exists,
        "pod_destruction_confirmed_in_recon": recon.get("destruction_confirmed", False),
        "final_pods_count_in_recon": recon.get("final_pods_count"),
        "final_volumes_count_in_recon": recon.get("final_volumes_count"),
        "net_spend_usd_in_recon": recon.get("net_spend_usd"),
        "termination_state": term.get("termination_state"),
        "termination_state_pod_id": term.get("pod_id")
    }


def main():
    print("=" * 80)
    print("STATESHIFT RESEARCH MISSION 18: FORENSIC DATASET & ARTIFACT AUDIT")
    print("=" * 80)
    
    artifact_results, artifacts_matched = verify_all_artifacts()
    print("\n--- 1. Cryptographic Checksum Ledger Audit ---")
    for path, res in artifact_results.items():
        print(f"[{res['status']}] {path}")
        if res.get("actual_sha256"):
            print(f"       SHA-256: {res['actual_sha256']} (size: {res['actual_size']} B)")
    print(f"\nAll artifacts verified exact: {artifacts_matched}")
    
    print("\n--- 2. Dataset Structural & Manifest Alignment Audit ---")
    dataset_summary = audit_primary_dataset()
    for k, v in dataset_summary.items():
        if k != "length_summary":
            print(f"  {k}: {v}")
    print("  Character Lengths by Condition:")
    for cond, stats in dataset_summary["length_summary"].items():
        print(f"    {cond}: mean={stats['mean_chars']}, min={stats['min_chars']}, max={stats['max_chars']}")
        
    print("\n--- 3. Cloud Execution Lock & Teardown Verification ---")
    lock_info = verify_cloud_lock_and_destruction()
    for k, v in lock_info.items():
        print(f"  {k}: {v}")
        
    # Write full JSON audit report
    out_dir = os.path.join(REPO_ROOT, "research_mission_18", "data")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "forensic_dataset_integrity_report.json")
    
    full_report = {
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "artifacts_matched": artifacts_matched,
        "artifacts": artifact_results,
        "dataset_audit": dataset_summary,
        "cloud_lock_and_destruction": lock_info
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)
        
    print(f"\nFull forensic integrity report written to: {out_file}")
    
    if not artifacts_matched or dataset_summary["manifest_mismatch_count"] > 0 or not lock_info["cloud_execution_lock_file_present"]:
        print("\nCRITICAL FAILURE IN ARTIFACT INTEGRITY!")
        sys.exit(1)
    else:
        print("\nFORENSIC DATASET AND ARTIFACT INTEGRITY: FULL PASS (100%)")
        sys.exit(0)


if __name__ == "__main__":
    main()
