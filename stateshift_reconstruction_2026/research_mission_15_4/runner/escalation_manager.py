#!/usr/bin/env python3
"""
StateShift Durable Escalation Manager (Mission 15.3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Manages durable escalation alerts when cloud provider cannot confirm pod destruction.
Persists structured metadata, emits human-readable instructions, and rechecks
unresolved pods upon controller rehydration.
"""

import os
import sys
import time
import json
from typing import Dict, Any, List, Optional


class DurableEscalationManager:
    """Manages persistent escalation records for unconfirmed cloud terminations."""

    @staticmethod
    def record_unconfirmed_termination(
        pod_id: str,
        reason: str,
        attempts: int,
        last_known_status: str,
        error_message: Optional[str],
        alert_dir: str
    ) -> str:
        """
        Persists structured alert file and writes human-readable manual intervention guide.
        Returns path to the persisted alert file.
        """
        os.makedirs(alert_dir, exist_ok=True)
        now_ts = time.time()
        iso_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts))
        
        payload = {
            "alert_type": "POD_TERMINATION_UNCONFIRMED",
            "pod_id": pod_id,
            "reason": reason,
            "attempts": attempts,
            "last_known_status": last_known_status,
            "error_message": error_message,
            "timestamp_utc": now_ts,
            "iso_time": iso_ts,
            "resolved": False
        }
        
        # 1. Atomic JSON payload
        json_path = os.path.join(alert_dir, f"unresolved_pod_{pod_id}.json")
        tmp_json = json_path + ".tmp"
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_json, json_path)
        
        # 2. Prominent human-readable text alert
        txt_path = os.path.join(alert_dir, f"CRITICAL_ALERT_POD_{pod_id}.txt")
        alert_text = (
            "================================================================================\n"
            "                CRITICAL CLOUD ESCALATION ALERT: MANUAL INTERVENTION REQUIRED    \n"
            "================================================================================\n"
            f"TIMESTAMP: {iso_ts}\n"
            f"AFFECTED POD ID: {pod_id}\n"
            f"LAST KNOWN STATUS: {last_known_status}\n"
            f"SHUTDOWN REASON: {reason}\n"
            f"FAILED ATTEMPTS: {attempts}\n"
            f"LAST ERROR: {error_message or 'No response from provider API'}\n"
            "\n"
            "POD MAY STILL BE BILLABLE — IMMEDIATE MANUAL TERMINATION REQUIRED!\n"
            "\n"
            "ACTIONABLE INSTRUCTIONS TO TERMINATE POD:\n"
            "1. Via RunPod Web Console:\n"
            "   Navigate to: https://www.runpod.io/console/pods\n"
            f"   Locate Pod '{pod_id}' and click Stop/Terminate.\n"
            "\n"
            "2. Via RunPod CLI:\n"
            f"   runpodctl remove pod {pod_id}\n"
            "\n"
            "3. Via GraphQL Direct API Mutation:\n"
            "   curl -X POST https://api.runpod.io/graphql \\\n"
            "     -H 'Content-Type: application/json' \\\n"
            '     -H "Authorization: Bearer $RUNPOD_API_KEY" \\\n'
            f'     -d \'{{"query": "mutation {{ podTerminate(input: {{podId: \\"{pod_id}\\"}}) }}"}}\'\n'
            "================================================================================\n"
        )
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(alert_text)
            f.flush()
            os.fsync(f.fileno())
            
        print(f"\n[CRITICAL ESCALATION] {alert_text}")
        return json_path

    @staticmethod
    def get_unresolved_escalations(alert_dir: str) -> List[Dict[str, Any]]:
        """Scans directory for unresolved pod terminations."""
        if not os.path.exists(alert_dir):
            return []
            
        unresolved = []
        for fname in os.listdir(alert_dir):
            if fname.startswith("unresolved_pod_") and fname.endswith(".json"):
                fpath = os.path.join(alert_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if not data.get("resolved", False):
                            unresolved.append(data)
                except Exception:
                    pass
        return unresolved

    @staticmethod
    def mark_resolved(pod_id: str, alert_dir: str, resolution_notes: str = "Confirmed terminated"):
        """Marks an unresolved escalation as resolved."""
        json_path = os.path.join(alert_dir, f"unresolved_pod_{pod_id}.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["resolved"] = True
                data["resolution_timestamp_utc"] = time.time()
                data["resolution_notes"] = resolution_notes
                tmp = json_path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, json_path)
            except Exception:
                pass
