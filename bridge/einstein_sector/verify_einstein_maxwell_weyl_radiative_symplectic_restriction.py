#!/usr/bin/env python3
"""Independent verifier for the combined standard radiative restriction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_radiative_symplectic_restriction.schema.json"


def _parse(value: str, eigenvalue: sp.Symbol) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals={"lam": eigenvalue})


def _matrix(rows: list[list[str]], eigenvalue: sp.Symbol) -> sp.Matrix:
    return sp.Matrix([[_parse(value, eigenvalue) for value in row] for row in rows])


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]

    eigenvalue = sp.symbols("lambda", positive=True)
    root = sp.sqrt(2 * eigenvalue)
    expected = {
        "axial": (
            sp.Matrix([[eigenvalue, 2], [eigenvalue, eigenvalue]]),
            sp.diag(eigenvalue, 2),
            [sp.Matrix([1, sp.sqrt(eigenvalue / 2)]), sp.Matrix([1, -sp.sqrt(eigenvalue / 2)])],
        ),
        "polar": (
            sp.Matrix([[eigenvalue, -2 * eigenvalue], [-1, eigenvalue]]),
            sp.Matrix([[1, -2], [-2, 2 * eigenvalue]]),
            [sp.Matrix([1, -1 / root]), sp.Matrix([1, 1 / root])],
        ),
    }
    theorem = payload["theorem"]
    for parity, (master, form, vectors) in expected.items():
        block = theorem["parity_blocks"][parity]
        assert _matrix(block["master_operator"], eigenvalue) == master
        assert _matrix(block["einstein_coefficient_form"], eigenvalue) == form
        relative = sp.eye(2) + sp.Rational(3, 2) * (master - eigenvalue * sp.eye(2))
        target = form * relative
        assert _matrix(block["relative_operator_p_of_M"], eigenvalue) == relative
        assert _matrix(block["spectral_target_form_E_times_p_of_M"], eigenvalue) == target
        assert form * master == master.T * form
        assert target == target.T
        assert sp.simplify((vectors[0].T * form * vectors[1])[0]) == 0
        assert sp.simplify((vectors[0].T * target * vectors[1])[0]) == 0
        for branch, vector, sign in zip(block["branches"], vectors, (1, -1), strict=True):
            ratio = sp.simplify((vector.T * target * vector)[0] / (vector.T * form * vector)[0])
            wanted = 1 + sign * sp.Rational(3, 2) * root
            assert sp.simplify(ratio - wanted) == 0
            assert sp.simplify(_parse(branch["relative_eigenvalue"], eigenvalue) - wanted) == 0

    signature = theorem["all_ell_ge_2_classification"]["branch_coefficient_relative_signature_per_real_spatial_harmonic"]
    assert signature == {"positive": 2, "negative": 2, "zero": 0}
    assert theorem["mode_counting_convention"]["real_phase_space_dimension_per_q"] == "8*q"
    assert theorem["quantum_norm_boundary"]["ghost_or_unitarity_theorem"] is False
    assert payload["classification"]["complete_standard_axial_polar_ell_ge2_restriction"] is True
    assert payload["classification"]["physical_ell1_restriction_computed"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_RADIATIVE_SYMPLECTIC_RESTRICTION independent verification: PASS")
