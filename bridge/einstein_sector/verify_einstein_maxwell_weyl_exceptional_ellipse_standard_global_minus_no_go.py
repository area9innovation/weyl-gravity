#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_standard_global_minus_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_standard_global_minus_no_go.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    reduction = value["standard_global_reduction"]
    assert reduction["universal_bounded_polynomial_ideal"] == "b=0, B=0, Q_e*a=0"
    assert "no positive-degree time-polynomial coefficient" in reduction["completion_extension"]
    assert reduction["remaining_global_mu_H"] == "-a^2-Q_e^2; c,d,W_x,A have zero diagonal Hamiltonian moment map"
    assert set(reduction["spectators"]) == {"W_x", "Q_e", "c", "A"}
    triangular = value["triangular_resonant_reduction"]
    assert "forces a=0" in triangular["first_step"]
    assert "forces every occupied minus coefficient" in triangular["second_step"]
    classes = value["correction_classes"]
    assert classes["BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC"]["status"] == "OBSTRUCTED"
    assert classes["SMOOTH_INFINITE_SECULAR"]["status"] == "OPEN"
    classification = value["classification"]
    assert classification["all_standard_generalized_zero_additions_covered"]
    assert not classification["genuinely_oscillatory_nonminus_carriers_classified"]
    assert not classification["causal_or_quantum_claim"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_STANDARD_GLOBAL_MINUS_NO_GO independent verification: PASS")
