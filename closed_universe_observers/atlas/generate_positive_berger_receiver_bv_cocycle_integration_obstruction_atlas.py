#!/usr/bin/env python3
"""Generate the fail-closed atlas fragment for the integration obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "closed_universe_observers"
CERT = P / "certificates/POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1.json"
PAYLOAD = P / "certificates/POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1_PAYLOAD.json"
OUTPUT = ROOT / "residual_atlas/positive-berger-receiver-bv-cocycle-integration-grading-obstruction-fragment-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    cert, payload = json.loads(CERT.read_text()), json.loads(PAYLOAD.read_text())
    evidence = {
        "certificate": {"path": str(CERT.relative_to(ROOT)), "sha256": sha(CERT)},
        "payload": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": sha(PAYLOAD)},
    }
    return {
        "schema": "residual-atlas-fragment-v1",
        "result_id": "POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_ATLAS_FRAGMENT_V1",
        "generated_from": cert["result_id"],
        "allowed_statuses": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "rows": [
            {"claim": "individual_receiver20_and_q70_input_readiness", "status": "CERTIFIED", "mode_scope": payload["scope"], "evidence": evidence},
            {"claim": "homogeneous_graded_receiver20_q70_action_pushout", "status": "OBSTRUCTED", "mode_scope": payload["scope"], "evidence": evidence, "first_obstruction": "pairing degree -1 versus +1; degree-minus-one injection deficiency 4"},
            {"claim": "receiver_cocycle_inclusion_and_residual_quotient_input", "status": "NO_CERTIFIED_MAP", "mode_scope": payload["scope"], "evidence": evidence, "first_missing_gate": "regraded action-derived receiver20 contract"},
            {"claim": "nonradical_period_denominator_and_operational_redshift", "status": "NO_CERTIFIED_MAP", "mode_scope": payload["scope"], "evidence": evidence, "first_missing_gate": "successful homogeneous action pushout and residual quotient"}
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
