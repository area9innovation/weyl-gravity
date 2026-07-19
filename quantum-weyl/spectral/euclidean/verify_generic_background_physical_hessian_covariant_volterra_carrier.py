#!/usr/bin/env python3
"""Independent replay of the physical covariant Volterra carrier."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-covariant-volterra-carrier-v1.schema.json"


def _q(value: sp.Expr) -> dict[str, int]:
    value = sp.Rational(value)
    return {"numerator": int(value.p), "denominator": int(value.q)}


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for reference in value["dependencies"].values():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {path}")
        if json.loads(path.read_text())["result_id"] != reference["result_id"]:
            raise ValueError(f"dependency result id drifted: {path}")

    carrier = value["decorated_carrier"]
    permutations = [list(row) for row in itertools.permutations(range(3))]
    if carrier["ordered_triangle_cells"] != permutations:
        raise ValueError("ordered triangle cell enumeration drifted")
    if carrier["resolved_triangle_boundary_chart_count"] != 3 * len(permutations):
        raise ValueError("triangle boundary chart count drifted")
    if carrier["resolved_contact_endpoint_chart_count"] != 2 * carrier["mixed_contact_cell_count"]:
        raise ValueError("contact endpoint chart count drifted")

    T, r, t, x = sp.symbols("T r t x", positive=True)
    triangle = sp.Matrix([T * (1 - r), T * r * t, T * r * (1 - t)])
    triangle_det = sp.det(triangle.jacobian(sp.Matrix([T, r, t])))
    triangle_weight = sp.factor(-triangle_det * sp.prod(triangle))
    expected_triangle = T**5 * r**3 * (1 - r) * t * (1 - t)
    if sp.simplify(triangle_weight - expected_triangle) != 0:
        raise ValueError("triangle proper-time measure replay failed")
    bubble = sp.Matrix([T * x, T * (1 - x)])
    bubble_det = sp.det(bubble.jacobian(sp.Matrix([T, x])))
    bubble_weight = sp.factor(-bubble_det * sp.prod(bubble))
    if sp.simplify(bubble_weight - T**3 * x * (1 - x)) != 0:
        raise ValueError("bubble proper-time measure replay failed")

    L = sp.diag(1, 2, 3)
    G = L**-2
    h1 = (
        sp.Matrix([[1, 2, 0], [0, -1, 1], [3, 0, 2]]),
        sp.Matrix([[0, 1, 2], [2, 0, -1], [1, 1, 0]]),
        sp.Matrix([[2, 0, 1], [-1, 3, 0], [0, 2, 1]]),
    )
    h2 = (
        sp.Matrix([[1, 0, 2], [2, -1, 0], [0, 1, 1]]),
        sp.Matrix([[0, 2, 1], [1, 1, 0], [3, 0, -1]]),
        sp.Matrix([[2, 1, 0], [0, 1, 2], [1, -1, 1]]),
    )
    triangles = [
        sp.trace(G * h1[i] * G * h1[j] * G * h1[k])
        for i, j, k in itertools.permutations(range(3))
    ]
    contacts = [sp.trace(G * h1[i] * G * h2[i]) for i in range(3)]
    cubic = sp.Rational(1, 6) * sum(triangles) - sp.Rational(1, 2) * sum(contacts)
    stored = value["exact_checks"]["finite_noncommuting_replay"]
    if _q(cubic) != stored["trace_log_cubic_value"]:
        raise ValueError("finite noncommuting Volterra replay failed")

    fixture_reference = value["dependencies"]["fixture_Mellin_subtraction"]
    fixture = json.loads((ROOT / fixture_reference["path"]).read_text())
    pullback = value["exact_checks"]["fixture_pullback"]
    if (
        pullback["triangle_boundary_chart_count"]
        != fixture["resolved_boundary_ledger"][
            "labelled_triangle_boundary_chart_count"
        ]
        or pullback["contact_endpoint_chart_count"]
        != fixture["resolved_boundary_ledger"]["bubble_endpoint_chart_count"]
        or pullback["common_regulator"]
        != fixture["subtraction_definition"]["common_regulator"]
        or pullback["scale_coefficient"]
        != fixture["renormalization_scale_row"]["coefficient"]
    ):
        raise ValueError("fixture-to-Volterra pullback replay failed")

    flags = value["claim_flags"]
    if not flags["GENERIC_COVARIANT_VOLTERRA_CARRIER_COMPUTED"]:
        raise ValueError("Volterra carrier was not promoted")
    for forbidden in (
        "GENERIC_TENSOR_KERNELS_EVALUATED",
        "RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED",
        "PHYSICAL_M14_CORNER_CLASS_DISPOSED",
        "QME_OR_ANOMALY_STATUS_CHANGED",
        "LORENTZIAN_CERTIFIED",
    ):
        if flags[forbidden]:
            raise ValueError(f"claim boundary crossed: {forbidden}")

    print("independent physical covariant Volterra carrier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
