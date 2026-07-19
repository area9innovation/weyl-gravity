#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_identity_audit.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_identity_audit.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    input_offsets = [6 - 2 * sp.sqrt(3), sp.Rational(16, 3), 6 + 2 * sp.sqrt(3)]
    target_offsets: list[sp.Expr] = [sp.Integer(4), sp.Rational(4, 3)]
    for output_ell in range(2, 5):
        eigenvalue = output_ell * (output_ell + 1)
        target_offsets.extend([eigenvalue - sp.sqrt(2 * eigenvalue), eigenvalue - sp.Rational(2, 3), eigenvalue + sp.sqrt(2 * eigenvalue)])
    count = 0
    for relative_sign in (-1, 1):
        n1, n2 = 1, 2 * relative_sign
        for first in input_offsets:
            for second in input_offsets:
                for target in target_offsets:
                    difference = target - first - second
                    coefficient = sp.radsimp(n1**2 * second + n2**2 * first - n1 * n2 * difference)
                    constant = sp.radsimp(4 * first * second - difference**2)
                    assert not (sp.simplify(coefficient) == 0 and sp.simplify(constant) == 0)
                    count += 1
    assert count == 198
    audit = value["identity_audit"]
    assert len(audit["rows"]) == 198
    assert audit["identity_resonant_row_count"] == 0
    assert all(not row["identity_resonant"] for row in audit["rows"])
    classification = value["classification"]
    assert classification["no_identity_resonant_channel"]
    assert classification["generic_circumference_cross_fibre_nonresonance_certified"]
    assert not classification["isolated_circumference_source_coefficients_computed"]
    assert not classification["complete_two_fibre_tangent_cone_classified"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_IDENTITY_AUDIT independent verification: PASS")
