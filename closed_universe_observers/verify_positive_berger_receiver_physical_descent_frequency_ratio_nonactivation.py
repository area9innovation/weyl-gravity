#!/usr/bin/env python3
"""Independent replay of the physical-receiver nonactivation ladder."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1.json"
Q = P / "certificates/POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1_PAYLOAD.json"
S = P / "schema/positive-berger-receiver-physical-descent-frequency-ratio-not-activated-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(Q.read_text())
    Draft202012Validator(json.loads(S.read_text())).validate(cert)
    assert sha(Q) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    integration = json.loads((ROOT / cert["dependency_refs"]["terminal_integration"]["path"]).read_text())
    assert integration["atlas_status"] == "OBSTRUCTED"
    assert integration["downstream_disposition"]["receiver_cocycle_inclusion"] == "NO_CERTIFIED_MAP"
    assert integration["downstream_disposition"]["residual_quotient_input_map"] == "NO_CERTIFIED_MAP"
    ladder = payload["charged_time_gate_ladder"]
    assert ladder[0]["status"] == "CERTIFIED_STANDALONE_ONLY"
    assert ladder[1]["status"] == "OBSTRUCTED" and ladder[1]["first_failure"]
    assert all(row["status"] in {"NOT_REACHED", "NOT_ACTIVATED"} for row in ladder[2:])
    ratio = payload["frequency_ratio_partial_function"]
    assert ratio["domain"] == [] and ratio["domain_cardinality"] == 0
    assert ratio["value"] == "UNDEFINED" and not ratio["coordinate_ratio_promoted"]
    assert all(row["rejected"] for row in payload["mutations"].values())
    print("POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
