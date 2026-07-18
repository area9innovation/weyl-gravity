#!/usr/bin/env python3
"""Independently verify the coefficient-explicit circumference transport primitive."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows as _axial_rows
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _generic_rows as _polar_rows


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive.json"


def _parse_matrix(values: list[list[str]], symbols: dict[str, sp.Symbol]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals=symbols) for value in row] for row in values])


def _reduce(matrix: sp.MatrixBase, frequency: sp.Symbol) -> sp.Matrix:
    shell = sp.Poly(frequency**2 - sp.Rational(16, 3), frequency)

    def entry(value: sp.Expr) -> sp.Expr:
        numerator, denominator = sp.fraction(sp.cancel(value))
        return sp.factor(
            sp.rem(sp.Poly(numerator, frequency), shell).as_expr()
            / sp.rem(sp.Poly(denominator, frequency), shell).as_expr()
        )

    return matrix.applyfunc(entry)


def verify() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    schema_path = ROOT / value["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if hashlib.sha256(schema_path.read_bytes()).hexdigest() != value["schema_sha256"]:
        raise AssertionError("schema hash changed")
    for relative, expected in value["source_manifest"].items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise AssertionError(f"source manifest changed: {relative}")

    c = sp.symbols("c", real=True)
    axial_rows, axial_symbols = _axial_rows()
    wa = axial_symbols["omega"]
    axial_fields = tuple(axial_symbols[name] for name in ("h_t", "h_x", "q_t", "q_x"))
    axial_operator = sp.Matrix(
        [[sp.diff(axial_rows[name], field) for field in axial_fields]
         for name in ("metric_t", "metric_x", "metric_angular", "maxwell_t", "maxwell_x", "maxwell_angular")]
    ).subs({axial_symbols["lambda"]: 6, axial_symbols["k"]: 0})
    axial = value["transport_primitive"]["axial"]
    axial_correction = _parse_matrix(axial["correction_columns"], {"c": c})
    axial_source = _parse_matrix(axial["source_columns"], {"c": c, "omega": wa, "I": sp.I})
    if axial_correction != sp.Matrix([[0, 0], [0, -c / 3], [0, 0], [0, 3 * c]]):
        raise AssertionError("axial correction columns changed")
    if axial_source != sp.zeros(6, 2) or _reduce(axial_operator * axial_correction + axial_source, wa) != sp.zeros(6, 2):
        raise AssertionError("axial full-row replay failed")

    polar_rows, polar_symbols = _polar_rows()
    eigenvalue, momentum, wp, *polar_fields = polar_symbols
    polar_operator = sp.Matrix(
        [[sp.diff(polar_rows[name], field) for field in polar_fields]
         for name in ("metric_00", "metric_01", "metric_11", "metric_0a", "metric_1a", "sphere_trace", "sphere_tracefree", "maxwell_axial_density")]
    ).subs({eigenvalue: 6, momentum: 0})
    polar = value["transport_primitive"]["polar"]
    polar_correction = _parse_matrix(polar["correction_columns"], {"c": c})
    polar_source = _parse_matrix(polar["source_columns"], {"c": c, "omega": wp, "I": sp.I})
    expected_correction = sp.Matrix([[0, 0], [c / 2, 0], [0, -72 * c], [0, 24 * c]])
    expected_source = sp.Matrix(
        [[0, -36 * c], [0, 0], [0, 164 * c], [0, -6 * sp.I * c * wp], [0, 0], [0, -100 * c], [0, -24 * c], [0, -20 * c]]
    )
    if polar_correction != expected_correction or polar_source != expected_source:
        raise AssertionError("polar correction/source columns changed")
    if _reduce(polar_operator * polar_correction + polar_source, wp) != sp.zeros(8, 2):
        raise AssertionError("polar full-row replay failed")

    negative = value["transport_primitive"]["negative_control"]
    mutated = _parse_matrix(negative["mutated_correction_columns"], {"c": c})
    mutation_remainder = _parse_matrix(negative["remainder_columns"], {"c": c, "omega": wp, "I": sp.I})
    if _reduce(polar_operator * mutated + polar_source, wp) != mutation_remainder:
        raise AssertionError("mutation remainder was not independently reproduced")
    if mutation_remainder == sp.zeros(8, 2):
        raise AssertionError("covariant-index-weight mutation was not detected")
    if value["classification"]["secular_prefactor_required_for_actual_circumference_source"]:
        raise AssertionError("ordinary transport primitive was relabelled secular")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_CIRCUMFERENCE_ELL2_EXTRA_TRANSPORT_PRIMITIVE independent verification: PASS")
