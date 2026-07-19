#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_wiener_minus_dressing_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_wiener_minus_dressing_no_go.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    lam = sp.symbols("lambda", real=True, positive=True)
    omega = sp.sqrt(lam - sp.sqrt(2 * lam))
    axial = -3 * sp.I * omega * (3 * sp.sqrt(2 * lam) - 1)
    polar = lam**2 * (2 * lam - 1) / 6
    for ell in range(2, 12):
        physical = ell * (ell + 1)
        assert sp.simplify(axial.subs(lam, physical)) != 0
        assert polar.subs(lam, physical) > 0

    topology = value["declared_topology"]
    assert "every r>=0" in topology["seminorms"]
    assert len(topology["consequences"]) == 4
    classes = value["correction_classes"]
    assert classes["BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC"]["status"] == "OBSTRUCTED"
    assert classes["SMOOTH_INFINITE_SECULAR"]["status"] == "OPEN"
    assert classes["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    classification = value["classification"]
    assert classification["smooth_wiener_bohr_minus_completion_classified"]
    assert not classification["maximal_finite_energy_or_sobolev_completion_classified"]
    assert not classification["additional_nonminus_carriers_classified"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_WIENER_MINUS_DRESSING_NO_GO independent verification: PASS")
