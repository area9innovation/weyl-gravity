#!/usr/bin/env python3
"""Independent verifier for the physical ell=1 quotient restriction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.schema.json"


def _parse(value: str, frequency: sp.Symbol) -> sp.Expr:
    return sp.sympify(value, locals={"omega": frequency})


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

    frequency = sp.symbols("omega", real=True)
    theorem = payload["theorem"]
    axial = theorem["direct_gauge_descent"]["axial_on_shell_target_matrix_raw"]
    polar = theorem["direct_gauge_descent"]["polar_on_shell_target_matrix_raw"]
    axial_matrix = sp.Matrix([[_parse(value, frequency) for value in row] for row in axial])
    polar_matrix = sp.Matrix([[_parse(value, frequency) for value in row] for row in polar])
    assert axial_matrix == sp.Matrix([[-sp.Rational(256, 3) * sp.I * sp.pi * frequency, 0], [0, 0]])
    assert polar_matrix == sp.Matrix([[-sp.Rational(64, 3) * sp.I * sp.pi * frequency, 0], [0, 0]])
    assert theorem["direct_gauge_descent"]["both_gauge_rows_and_columns_zero"] is True
    for row in theorem["parity_rows"].values():
        assert row["restriction_over_einstein"] == "4"
    normalized = theorem["normalized_direct_sum_theorem"]
    assert normalized["relative_operator"] == [["4", "0"], ["0", "4"]]
    assert normalized["relative_coefficient_signature_per_real_spatial_harmonic"] == {"positive": 2, "negative": 0, "zero": 0}
    failure = theorem["generic_polar_lambda_to_2_failure"]
    assert failure["einstein_gauge_norm"] == "0"
    assert failure["target_gauge_norm"] == "16"
    assert failure["target_gauge_physical_cross"] == "-24"
    assert failure["quotient_representative_naive_ratio"] == "2"
    assert payload["classification"]["target_current_descends_to_exceptional_quotient"] is True
    assert payload["classification"]["generic_polar_lambda_to_2_continuation_valid"] is False
    assert payload["classification"]["axial_twist_restriction_computed"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_ELL1_PHYSICAL_SYMPLECTIC_RESTRICTION independent verification: PASS")
