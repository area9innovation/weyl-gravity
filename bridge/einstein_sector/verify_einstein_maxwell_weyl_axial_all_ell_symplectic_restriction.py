#!/usr/bin/env python3
"""Independent verifier for the all-ell axial restriction theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.schema.json"


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
    for record in payload["provenance"]["direct_implementation"].values():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]

    eigenvalue, mass = sp.symbols("lambda mu", positive=True)
    local = {"lam": eigenvalue, "mu": mass}
    def parse(value: str) -> sp.Expr:
        return sp.sympify(value.replace("lambda", "lam"), locals=local)

    restriction = payload["restriction"]
    einstein = sp.Matrix(
        [[parse(value) for value in row] for row in restriction["einstein_maxwell_off_shell_coefficient_matrix"]]
    )
    weyl = sp.Matrix(
        [[parse(value) for value in row] for row in restriction["weyl_maxwell_off_shell_coefficient_matrix"]]
    )
    assert einstein == sp.diag(eigenvalue, 2)
    assert weyl == sp.diag(eigenvalue * (3 * mass - 3 * eigenvalue + 1), 2)
    for row, sign in zip(restriction["on_shell_branches"], (1, -1), strict=True):
        branch_mass = eigenvalue + sign * sp.sqrt(2 * eigenvalue)
        vector = sp.Matrix([1, sign * sp.sqrt(eigenvalue / 2)])
        ratio = sp.simplify(
            (vector.T * weyl.subs(mass, branch_mass) * vector)[0]
            / (vector.T * einstein * vector)[0]
        )
        expected = 1 + sign * sp.Rational(3, 2) * sp.sqrt(2 * eigenvalue)
        assert sp.simplify(ratio - expected) == 0
        assert sp.simplify(parse(row["restriction_over_einstein"]) - ratio) == 0
    assert restriction["ell_ge_2_proof"]["rank"] == 2
    assert restriction["ell_ge_2_proof"]["signature_relative_to_positive_einstein_branch_form"] == {"positive": 1, "negative": 1, "zero": 0}
    assert restriction["ell1_consistency_control"]["formal_branch_masses"] == ["4", "0"]
    assert payload["classification"]["all_axial_ell_ge2_restriction_computed"] is True
    assert payload["classification"]["physical_ell1_and_global_twist_restriction_computed"] is False
    assert payload["classification"]["polar_restriction_computed"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_AXIAL_ALL_ELL_SYMPLECTIC_RESTRICTION independent verification: PASS")
