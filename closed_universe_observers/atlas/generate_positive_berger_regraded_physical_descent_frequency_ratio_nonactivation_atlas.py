#!/usr/bin/env python3
"""Generate the final regraded-receiver nonactivation atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "closed_universe_observers"
CERT = P / "certificates/POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1.json"
PAYLOAD = P / "certificates/POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1_PAYLOAD.json"
OUTPUT = ROOT / "residual_atlas/positive-berger-regraded-receiver-physical-descent-frequency-ratio-not-activated-fragment-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    cert, payload = json.loads(CERT.read_text()), json.loads(PAYLOAD.read_text())
    evidence = {"certificate": {"path": str(CERT.relative_to(ROOT)), "sha256": sha(CERT)}, "payload": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": sha(PAYLOAD)}}
    return {
        "schema": "residual-atlas-fragment-v1",
        "result_id": "POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_ATLAS_FRAGMENT_V1",
        "generated_from": cert["result_id"],
        "allowed_statuses": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "rows": [
            {"claim": "regraded_receiver_local_action_and_cochain", "status": "CERTIFIED", "mode_scope": payload["scope"], "evidence": evidence},
            {"claim": "physical_receiver_descent", "status": "NO_CERTIFIED_MAP", "mode_scope": payload["scope"], "evidence": evidence, "first_failed_map": payload["first_failed_map"]},
            {"claim": "operational_frequency_ratio", "status": "NO_CERTIFIED_MAP", "mode_scope": payload["scope"], "evidence": evidence, "domain_cardinality": 0},
            {"claim": "relational_redshift", "status": "NO_CERTIFIED_MAP", "mode_scope": payload["scope"], "evidence": evidence}
        ]
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
