#!/usr/bin/env python3
"""Generate the fail-closed Phase 1 relational-observable atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "closed_universe_observers"
CERT = P / "certificates/PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1.json"
PAYLOAD = P / "certificates/PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1_PAYLOAD.json"
OUTPUT = ROOT / "residual_atlas/phase1-relational-observable-disposition-synthesis-fragment-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    cert, payload = json.loads(CERT.read_text()), json.loads(PAYLOAD.read_text())
    evidence = {
        "certificate": {"path": str(CERT.relative_to(ROOT)), "sha256": sha(CERT)},
        "payload": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": sha(PAYLOAD)},
    }
    rows = []
    for row in payload["claim_crosswalk"]:
        instances = row.get("carrier_instances")
        if instances:
            rows.extend(
                {
                    "claim": row["layer"] + "::" + instance["id"],
                    "status": instance["status"],
                    "mode_scope": instance["scope"],
                    "evidence": evidence,
                    "claim_boundary": row["does_not_establish"],
                }
                for instance in instances
            )
            continue
        rows.append({
            "claim": row["layer"],
            "status": row["status"],
            "mode_scope": row["scope"],
            "evidence": evidence,
            "claim_boundary": row["does_not_establish"],
        })
    return {
        "schema": "residual-atlas-fragment-v1",
        "result_id": "PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_ATLAS_FRAGMENT_V1",
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
