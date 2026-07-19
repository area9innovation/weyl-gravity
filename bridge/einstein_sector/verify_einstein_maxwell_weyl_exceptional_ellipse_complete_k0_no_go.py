#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_complete_k0_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_complete_k0_no_go.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
    inventory = value["complete_carrier_inventory"]
    assert set(inventory) == {"generalized_zero", "dipoles", "generic_nonminus", "generic_minus", "excluded"}
    assert "at least one" in value["taub_reduction"]["necessity"]
    assert "only d*C_parity" in value["complete_minus_shell_isolation"]["remaining_source"]
    assert value["contradiction"]["verdict"].startswith("the bounded second-order tangent cone has empty intersection")
    classes = value["correction_classes"]
    assert classes["BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC"]["status"] == "OBSTRUCTED"
    assert classes["SMOOTH_INFINITE_SECULAR"]["status"] == "OPEN"
    assert classes["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    classification = value["classification"]
    assert classification["complete_declared_k0_carrier_covered"]
    assert classification["bounded_tangent_cone_intersection_empty_over_nonzero_ellipse"]
    assert not classification["nonzero_momentum_classified"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_COMPLETE_K0_NO_GO independent verification: PASS")
