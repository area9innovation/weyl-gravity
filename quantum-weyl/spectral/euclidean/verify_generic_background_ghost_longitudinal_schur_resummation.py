#!/usr/bin/env python3
"""Independent replay of the generic ghost longitudinal Schur resummation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json"
SCHEMA = HERE / "schema/generic-background-ghost-longitudinal-schur-resummation-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rational(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def independent_fixture_residuals(*, mutate_cubic: bool = False) -> dict[str, sp.Expr]:
    """Replay on a fixture not used by the producer.

    The mutation changes the mixed cubic coefficient from 1/9 to 1/8 and
    must leave a nonzero residual.
    """

    delta0 = sp.diag(2, 3, 5)
    d = sp.zeros(5, 3)
    delta = sp.zeros(3, 5)
    for index, eigenvalue in enumerate((2, 3, 5)):
        d[index, index] = 1
        delta[index, index] = eigenvalue
    f = sp.diag(2, 3, 5, 7, 11)
    f[3:5, 3:5] = sp.Matrix([[7, 2], [2, 11]])
    w = sp.Matrix(
        [
            [1, 2, -1, 1, 3],
            [2, -1, 3, -2, 1],
            [-1, 3, 2, 4, -1],
            [1, -2, 4, 1, 2],
            [3, 1, -1, 2, -2],
        ]
    )
    assert delta * d == delta0
    assert f * d == d * delta0
    assert delta * f == delta0 * delta

    h0 = f + sp.Rational(1, 2) * d * delta
    a = f + w
    h = a + sp.Rational(1, 2) * d * delta
    schur = sp.Rational(2, 3) * sp.eye(3) + sp.Rational(1, 3) * delta * a.inv() * d
    determinant = sp.factor(
        h.det() / h0.det() - (a.det() / f.det()) * schur.det()
    )

    g = f.inv()
    b1 = delta0.inv() * delta * w * d * delta0.inv()
    b2 = delta0.inv() * delta * w * g * w * d * delta0.inv()
    b3 = delta0.inv() * delta * w * g * w * g * w * d * delta0.inv()
    direct = h0.inv() * w
    vector = g * w
    direct_rows = (
        sp.trace(direct),
        -sp.Rational(1, 2) * sp.trace(direct**2),
        sp.Rational(1, 3) * sp.trace(direct**3),
    )
    vector_rows = (
        sp.trace(vector),
        -sp.Rational(1, 2) * sp.trace(vector**2),
        sp.Rational(1, 3) * sp.trace(vector**3),
    )
    mixed_cubic = sp.Rational(1, 8) if mutate_cubic else sp.Rational(1, 9)
    scalar_rows = (
        -sp.Rational(1, 3) * sp.trace(b1),
        sp.Rational(1, 3) * sp.trace(b2)
        - sp.Rational(1, 18) * sp.trace(b1**2),
        -sp.Rational(1, 3) * sp.trace(b3)
        + mixed_cubic * sp.trace(b1 * b2)
        - sp.Rational(1, 81) * sp.trace(b1**3),
    )
    return {
        "determinant": determinant,
        "linear": sp.factor(direct_rows[0] - vector_rows[0] - scalar_rows[0]),
        "quadratic": sp.factor(direct_rows[1] - vector_rows[1] - scalar_rows[1]),
        "cubic": sp.factor(direct_rows[2] - vector_rows[2] - scalar_rows[2]),
    }


def verify(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for reference in value["dependencies"].values():
        path = ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        assert _sha256(path) == reference["sha256"]
        assert (dependency.get("result_id") or dependency.get("schema")) == reference["result_id"]

    assert value["regularization_boundary"] == {
        "Fredholm_relative_identity": "EXACT_IF_S_L_MINUS_I_AND_RELATIVE_RESOLVENTS_ARE_DETERMINANT_CLASS_IN_THE_DECLARED_COMMON_PRESCRIPTION",
        "finite_dimensional_identity": "EXACT",
        "generic_4d_trace_class_status": "ORDER_MINUS_TWO_DOES_NOT_PROVE_TRACE_CLASS_IN_DIMENSION_FOUR",
        "nonlocal_consequence": "THE_THREE_DW_TRACE_LOG_TOWERS_ARE_ONE_SCHUR_SERIES; LOCAL_ZETA_ANOMALY_MAY_SHIFT_ONLY_LOCAL_COUNTERTERM_COORDINATES",
        "required_generic_determinant": "REGULARIZED_RELATIVE_DETERMINANT_OR_EQUIVALENT_COMMON_TRACE_REGULATOR",
        "zeta_multiplicative_anomaly": "LOCAL_TERM_NOT_EVALUATED",
    }
    coefficients = value["resolvent_series"]["Hodge_carrier_match"]["completed_n3_longitudinal_coefficients"]
    assert [_rational(row) for row in coefficients] == [
        -sp.Rational(1, 3),
        sp.Rational(1, 9),
        -sp.Rational(1, 81),
    ]

    residuals = independent_fixture_residuals()
    assert all(residual == 0 for residual in residuals.values()), residuals
    mutated = independent_fixture_residuals(mutate_cubic=True)
    assert mutated["determinant"] == 0
    assert mutated["linear"] == 0
    assert mutated["quadratic"] == 0
    assert mutated["cubic"] != 0

    x, curvature = sp.symbols("x R", nonzero=True)
    schur = sp.factor(
        sp.Rational(2, 3)
        + sp.Rational(1, 3) * x / (x - curvature / 2)
    )
    assert sp.factor(schur - (x - curvature / 3) / (x - curvature / 2)) == 0
    assert sp.factor((x - curvature / 2) * schur / x - (x - curvature / 3) / x) == 0

    true_flags = {
        "GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED",
        "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION",
        "EINSTEIN_SCALAR_GHOST_FACTOR_REPRODUCED_FROM_SCHUR_FACTOR",
    }
    for name, flag in value["claim_flags"].items():
        assert flag is (name in true_flags), name


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("GENERIC GHOST LONGITUDINAL SCHUR RESUMMATION: INDEPENDENT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
