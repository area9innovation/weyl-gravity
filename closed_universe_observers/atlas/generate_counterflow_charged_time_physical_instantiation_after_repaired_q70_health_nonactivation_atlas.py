#!/usr/bin/env python3
"""Generate the repaired-q70-health receiver nonactivation atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "closed_universe_observers"
CERT = P / "certificates/COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1.json"
PAYLOAD = P / "certificates/COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1_PAYLOAD.json"
OUTPUT = ROOT / "residual_atlas/counterflow-charged-time-physical-instantiation-after-repaired-q70-health-not-activated-fragment-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    cert, payload = json.loads(CERT.read_text()), json.loads(PAYLOAD.read_text())
    evidence = {
        "certificate": {"path": str(CERT.relative_to(ROOT)), "sha256": sha(CERT)},
        "payload": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": sha(PAYLOAD)},
    }
    rows = [
        {
            "claim": f"healthy_physical_receiver_candidate_j_{row['j']}",
            "status": "OBSTRUCTED",
            "mode_scope": row["scope"],
            "evidence": evidence,
            "instability_class": row["instability_class"],
        }
        for row in payload["certified_block_dispositions"]
    ]
    rows.extend([
        {"claim": "higher_j_physical_receiver_candidate", "status": "NO_CERTIFIED_MAP", "mode_scope": payload["remaining_carrier"]["scope"], "evidence": evidence},
        {"claim": "thirteen_field_physical_receiver_interface", "status": "NO_CERTIFIED_MAP", "mode_scope": payload["remaining_carrier"]["scope"], "evidence": evidence},
        {"claim": "operational_frequency_ratio_and_redshift", "status": "NO_CERTIFIED_MAP", "mode_scope": payload["remaining_carrier"]["scope"], "evidence": evidence, "domain_cardinality": 0},
    ])
    return {
        "schema": "residual-atlas-fragment-v1",
        "result_id": "COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_ATLAS_FRAGMENT_V1",
        "generated_from": cert["result_id"],
        "allowed_statuses": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
