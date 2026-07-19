#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_ell1_oscillator_minus_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_ell1_oscillator_minus_no_go.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    root3 = sp.sqrt(3)
    root6 = sp.sqrt(6)
    additions = (2 / root3, sp.Integer(2))
    existing = (2 / root3, sp.Integer(2), 4 / root3)
    targets = (6 - 2 * root3, 12 - 2 * root6)
    count = 0
    for left in additions:
        for right in existing:
            for squared in ((left + right) ** 2, (left - right) ** 2):
                for target in targets:
                    assert sp.simplify(squared - target) != 0
                count += 1
        assert sp.simplify(left**2 - targets[0]) != 0
        count += 1
    assert count == len(value["finite_low_ell_audit"]["comparisons"])
    assert value["finite_low_ell_audit"]["all_residuals_nonzero"]
    classes = value["correction_classes"]
    assert classes["BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC"]["status"] == "OBSTRUCTED"
    classification = value["classification"]
    assert classification["all_k0_physical_and_extra_ell1_oscillator_additions_covered"]
    assert not classification["generic_ell_ge_2_nonminus_oscillators_classified"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_ELL1_OSCILLATOR_MINUS_NO_GO independent verification: PASS")
