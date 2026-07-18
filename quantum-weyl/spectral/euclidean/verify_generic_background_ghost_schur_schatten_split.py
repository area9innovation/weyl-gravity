#!/usr/bin/env python3
"""Independent replay of the longitudinal Schur Schatten/det3 split."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT.json"
SCHEMA = HERE / "schema/generic-background-ghost-schur-schatten-split-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _sphere_expectation_degree_four(polynomial: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    expanded = sp.Poly(sp.expand(polynomial), *variables)
    total = sp.Integer(0)
    for exponents, coefficient in expanded.terms():
        if any(exponent % 2 for exponent in exponents):
            continue
        pattern = sorted((exponent for exponent in exponents if exponent), reverse=True)
        if pattern == [4]:
            moment = sp.Rational(1, 8)
        elif pattern == [2, 2]:
            moment = sp.Rational(1, 24)
        elif not pattern:
            moment = sp.Integer(1)
        else:
            raise AssertionError(f"unexpected sphere monomial pattern {pattern}")
        total += coefficient * moment
    return sp.expand(total)


def independent_residue_residual(*, mutate: bool = False) -> sp.Expr:
    n = sp.symbols("n0:4")
    w = sp.Matrix(
        [
            [2, 1, -1, 0],
            [1, -3, 2, 1],
            [-1, 2, 5, -2],
            [0, 1, -2, 4],
        ]
    )
    vector = sp.Matrix(n)
    direct_average = _sphere_expectation_degree_four((vector.dot(w * vector)) ** 2, n)
    direct_wres_in_4pi_units = sp.Rational(2, 9) * direct_average
    denominator = 109 if mutate else 108
    claimed = ((sp.trace(w)) ** 2 + 2 * sp.trace(w * w)) / denominator
    return sp.factor(direct_wres_in_4pi_units - claimed)


def independent_det3_series_residuals() -> dict[int, sp.Expr]:
    t = sp.Symbol("t")
    k = sp.Matrix(
        [
            [sp.Rational(1, 2), sp.Rational(1, 3), 0, sp.Rational(1, 7)],
            [0, -sp.Rational(1, 5), sp.Rational(1, 4), 0],
            [sp.Rational(1, 6), 0, sp.Rational(1, 8), sp.Rational(1, 9)],
            [0, sp.Rational(1, 10), 0, -sp.Rational(1, 11)],
        ]
    )
    determinant = sp.expand((sp.eye(4) + t * k).det())
    direct = sp.series(
        sp.log(determinant)
        - t * sp.trace(k)
        + t**2 * sp.trace(k**2) / 2,
        t,
        0,
        7,
    ).removeO()
    expected = sum(
        sp.Rational((-1) ** (power + 1), power) * sp.trace(k**power) * t**power
        for power in range(3, 7)
    )
    difference = sp.Poly(sp.expand(direct - expected), t)
    return {power: sp.factor(difference.coeff_monomial(t**power)) for power in range(7)}


def verify(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for reference in value["dependencies"].values():
        path = ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        assert _sha256(path) == reference["sha256"]
        assert (dependency.get("result_id") or dependency.get("schema")) == reference["result_id"]

    ideal = value["sharp_ideal_classification"]
    assert ideal["minimal_modified_determinant_order"] == 3
    assert ideal["ordinary_trace_class"] == "NOT_PROVED_AND_NOT_GENERIC_FROM_ORDER_MINUS_TWO"
    dimension = value["scope"]["dimension"]
    correction_order = 2
    assert dimension / correction_order == 2
    assert 3 > dimension / correction_order
    assert -3 * correction_order < -dimension
    assert -2 * correction_order == -dimension

    assert independent_residue_residual() == 0
    assert independent_residue_residual(mutate=True) != 0
    assert all(value == 0 for value in independent_det3_series_residuals().values())

    residue = value["critical_local_residue"]
    assert residue["W_basis"].endswith("[(tr W)^2+2 tr(W^2)]/108")
    assert residue["Ricci_basis"].endswith("[R^2+2 Ric_mn Ric^mn]/27")
    assert residue["scalar_flat_basis"].endswith("[2 Ric_mn Ric^mn]/27 when R=0")
    assert _q(residue["sphere_moment_replay"]["symbolic_residual"]) == 0

    true_flags = {
        "SCHUR_CORRECTION_S3_CLASS_PROVED",
        "CANONICAL_DET3_TAIL_DEFINED",
        "CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED",
    }
    for name, flag in value["claim_flags"].items():
        assert flag is (name in true_flags), name


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("GENERIC GHOST SCHUR SCHATTEN SPLIT: INDEPENDENT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
