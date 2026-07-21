#!/usr/bin/env python3
"""Generate the fail-closed atlas fragment for the local receiver preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "closed_universe_observers"
CERT = P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1.json"
PAYLOAD = P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1_PAYLOAD.json"
CONTRACT = P / "generated/POSITIVE_BERGER_LOCAL_RECEIVER_BV_INTEGRATION_CONTRACT_V1.json"
OUTPUT = ROOT / "residual_atlas/positive-berger-local-receiver-action-preflight-fragment-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    cert = json.loads(CERT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    contract = json.loads(CONTRACT.read_text())
    scope = payload["scope"]
    common = {
        "mode_scope": scope,
        "evidence": {
            "certificate": {"path": str(CERT.relative_to(ROOT)), "sha256": sha(CERT)},
            "payload": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": sha(PAYLOAD)},
            "integration_contract": {"path": str(CONTRACT.relative_to(ROOT)), "sha256": sha(CONTRACT)},
        },
    }
    return {
        "schema": "residual-atlas-fragment-v1",
        "result_id": "POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_ATLAS_FRAGMENT_V1",
        "generated_from": cert["result_id"],
        "rows": [
            {
                **common,
                "claim": "standalone_action_derived_local_receiver_BV_cocycle",
                "status": "CERTIFIED",
                "operational_observable": {
                    "detector_response": "external signal port derivative only; no ambient response claimed",
                    "response_rank": "NOT_APPLICABLE",
                    "emitter_preparation": "NOT_APPLICABLE",
                    "clock_and_rod_dependence": "exact D0 W0 profile",
                    "relational_redshift": "NO_CERTIFIED_MAP",
                    "recoil_order": "NO_CERTIFIED_MAP",
                    "survives_gauge_reduction": "NOT_APPLICABLE_NO_GAUGE",
                },
            },
            {
                **common,
                "claim": "ambient_repaired_parent_receiver_inclusion",
                "status": contract["downstream_status"]["ambient_unary_inclusion"],
                "first_missing_gate": "same-background 20-row chain/pairing/support/D-R-K embedding",
            },
            {
                **common,
                "claim": "receiver_quotient_period_denominator_and_redshift",
                "status": "NO_CERTIFIED_MAP",
                "first_missing_gate": "ambient unary inclusion followed by residual quotient and nonradical pairing",
            },
        ],
        "allowed_statuses": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
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
