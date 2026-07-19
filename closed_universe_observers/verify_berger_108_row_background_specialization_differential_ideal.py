#!/usr/bin/env python3
"""Independently verify the Berger background differential quotient."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL.json"
SCHEMA = P / "schema/berger-108-row-background-specialization-differential-ideal-v1.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def frame_derivative(value: sp.Expr, axis: int, x: tuple[sp.Symbol, ...]) -> sp.Expr:
    x0, x1, x2, x3 = x
    c = 3 * sp.sqrt(10) / 20
    coefficients = (
        (-x1 / 2, x0 / 2, x3 / 2, -x2 / 2),
        (-x2 / 2, -x3 / 2, x0 / 2, x1 / 2),
        (-x3 / (2 * c), x2 / (2 * c), -x1 / (2 * c), x0 / (2 * c)),
    )[axis]
    return sp.expand(sum(coefficients[index] * sp.diff(value, x[index]) for index in range(4)))


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in value["dependency_refs"].values():
        assert sha256(ROOT / ref["path"]) == ref["sha256"]

    records = value["background_specialization"]["records"]
    assert canonical_sha256(records) == value["background_specialization"]["records_canonical_sha256"]
    assert [record["background_id"] for record in records[:6]] == [
        "R0_1", "R0_2", "R0_3", "R1_1", "R1_2", "R1_3"
    ]
    assert [record["background_id"] for record in records[6:]] == [
        "Phi2_00", "Phi2_01", "Phi2_02", "Phi2_03", "Phi2_11",
        "Phi2_12", "Phi2_13", "Phi2_22", "Phi2_23", "Phi2_33",
    ]

    x = sp.symbols("x0:4", real=True)
    locals_ = {str(symbol): symbol for symbol in x} | {"I": sp.I}
    sphere = sum(item**2 for item in x) - 1
    assert all(frame_derivative(sphere, axis, x) == 0 for axis in range(3))
    brackets = ((0, 1, 2, 3 * sp.sqrt(10) / 20), (1, 2, 0, 2 * sp.sqrt(10) / 3), (2, 0, 1, 2 * sp.sqrt(10) / 3))
    for coordinate in x:
        for left, right, target, coefficient in brackets:
            residual = (
                frame_derivative(frame_derivative(coordinate, right, x), left, x)
                - frame_derivative(frame_derivative(coordinate, left, x), right, x)
                - coefficient * frame_derivative(coordinate, target, x)
            )
            assert sp.simplify(residual) == 0

    # Reconstruct the six displayed Laurent-time rod functions without using
    # the producer and replay Box=-e0^2+sum_i e_i^2 mode by mode.
    omega = sp.sqrt(58) / 6
    for record in records[:6]:
        for term in record["target_terms"]:
            mode = term["time_mode"]
            coefficient = sp.sympify(
                term["coefficient_times_spatial_polynomial"], locals=locals_
            )
            residual = omega**2 * mode**2 * coefficient + sum(
                frame_derivative(frame_derivative(coefficient, axis, x), axis, x)
                for axis in range(3)
            )
            assert sp.trigsimp(sp.expand(residual)) == 0

    assert value["exact_checks"] == {
        "Phi2_reality_defect_count": 0,
        "background_commutator_defect_count": 0,
        "background_count": 16,
        "former_free_residual_quotient_term_count": 0,
        "former_free_residual_term_count": 4,
        "rod_wave_defect_count": 0,
    }
    assert value["differential_ideal"]["Berger_frame_closed"]
    assert value["differential_ideal"]["e1_Box_R0_1_quotient_normal_form"] == []
    assert all(row["detected"] for row in value["mutations"])
    assert not value["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
    print("BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
