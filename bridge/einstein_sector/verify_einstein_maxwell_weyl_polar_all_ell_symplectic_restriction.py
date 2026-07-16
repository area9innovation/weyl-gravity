#!/usr/bin/env python3
"""Independent verifier for the all-ell polar restriction theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.schema.json"


def _parse(value: str, eigenvalue: sp.Symbol, mass: sp.Symbol) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals={"lam": eigenvalue, "mu": mass})


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
    restriction = payload["restriction"]
    einstein = sp.Matrix(
        [[_parse(value, eigenvalue, mass) for value in row] for row in restriction["einstein_maxwell_off_shell_matrix"]]
    )
    weyl = sp.Matrix(
        [[_parse(value, eigenvalue, mass) for value in row] for row in restriction["weyl_maxwell_off_shell_matrix"]]
    )
    assert einstein == sp.Matrix([[1, -2], [-2, 2 * eigenvalue]])
    assert weyl == sp.Matrix(
        [[4 * (mass - eigenvalue), 5 * eigenvalue - 4 * mass], [5 * eigenvalue - 4 * mass, 4 * (mass - eigenvalue)]]
    )
    root = sp.sqrt(2 * eigenvalue)
    for row, sign in zip(restriction["on_shell_branches"], (1, -1), strict=True):
        branch_mass = eigenvalue + sign * root
        vector = sp.Matrix([1, -sign / root])
        ratio = sp.simplify(
            (vector.T * weyl.subs(mass, branch_mass) * vector)[0]
            / (vector.T * einstein * vector)[0]
        )
        expected = 1 + sign * sp.Rational(3, 2) * root
        assert sp.simplify(ratio - expected) == 0
        assert sp.simplify(_parse(row["restriction_over_einstein"], eigenvalue, mass) - expected) == 0
    assert restriction["ell_ge_2_proof"]["rank"] == 2
    assert restriction["ell_ge_2_proof"]["signature_relative_to_positive_einstein_branch_form"] == {"positive": 1, "negative": 1, "zero": 0}
    assert restriction["parity_comparison"]["axial_and_polar_on_shell_relative_factors_equal"] is True
    assert payload["classification"]["all_polar_ell_ge2_restriction_computed"] is True
    assert payload["classification"]["physical_ell1_and_global_restriction_computed"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_POLAR_ALL_ELL_SYMPLECTIC_RESTRICTION independent verification: PASS")
