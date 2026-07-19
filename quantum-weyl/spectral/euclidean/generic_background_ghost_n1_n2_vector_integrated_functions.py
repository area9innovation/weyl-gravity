#!/usr/bin/env python3
"""Integrate the exact generic ghost vector n=1+n=2 CPT carrier slice."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_INTEGRATED_FUNCTIONS.json"
SCHEMA = HERE / "schema/generic-background-ghost-n1-n2-vector-integrated-functions-v1.schema.json"
PROJECTION = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_CPT_PROJECTION.json"
TRIANGLE = HERE / "certificates/GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM.json"

A1, A2 = sp.symbols("alpha1 alpha2")
X1, X2, X3 = sp.symbols("x1 x2 x3")
XS = (X1, X2, X3)
J, L21, L31 = sp.symbols("J_triangle log_x2_over_x1 log_x3_over_x1")
L32 = L31 - L21
LAMBDA = sp.expand(
    X1**2 + X2**2 + X3**2 - 2 * X1 * X2 - 2 * X1 * X3 - 2 * X2 * X3
)
DELTA = sp.expand(
    (1 - A1 - A2) * A1 * X2
    + (1 - A1 - A2) * A2 * X1
    + A1 * A2 * X3
)
FUNCTION_BASIS = (
    "J_triangle",
    "log_x2_over_x1",
    "log_x3_over_x1",
    "rational_corner",
)
HOLDOUTS = ((2, 3, 5), (3, 5, 7))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _q(value: sp.Expr) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def _poly_terms(expression: sp.Expr) -> list[dict[str, Any]]:
    polynomial = sp.Poly(sp.expand(expression), *XS, domain=sp.QQ)
    return [
        {"exponents": list(exponents), "coefficient": _q(coefficient)}
        for exponents, coefficient in polynomial.terms()
        if coefficient
    ]


def _rational_function(expression: sp.Expr) -> dict[str, Any]:
    numerator, denominator = sp.fraction(sp.cancel(expression))
    numerator = sp.Poly(numerator, *XS, domain=sp.QQ)
    denominator = sp.Poly(denominator, *XS, domain=sp.QQ)
    if denominator.LC() < 0:
        numerator = -numerator
        denominator = -denominator
    return {
        "numerator_terms": _poly_terms(numerator.as_expr()),
        "denominator_terms": _poly_terms(denominator.as_expr()),
    }


def moment_rows() -> dict[tuple[int, int], sp.Expr]:
    i10, i01 = sp.symbols("I10 I01")
    c = X3 - X1 - X2
    first = sp.solve(
        (
            X2 * J - 2 * X2 * i10 + c * i01 - L31,
            X1 * J + c * i10 - 2 * X1 * i01 - L32,
        ),
        (i10, i01),
        dict=True,
    )[0]
    i20, i11, i02 = sp.symbols("I20 I11 I02")
    second = sp.solve(
        (
            X2 * first[i01] - 2 * X2 * i11 + c * i02 - L31 / 2,
            X1 * first[i10] + c * i20 - 2 * X1 * i11 - L32 / 2,
            X2 * first[i10]
            + X1 * first[i01]
            - X2 * i20
            - X1 * i02
            + c * i11
            - sp.Rational(1, 2),
        ),
        (i20, i11, i02),
        dict=True,
    )[0]
    return {
        (0, 0): J,
        (1, 0): sp.cancel(first[i10]),
        (0, 1): sp.cancel(first[i01]),
        (2, 0): sp.cancel(second[i20]),
        (1, 1): sp.cancel(second[i11]),
        (0, 2): sp.cancel(second[i02]),
    }


def _moment_identity_defects(moments: dict[tuple[int, int], sp.Expr]) -> dict[str, sp.Expr]:
    c = X3 - X1 - X2
    i00 = moments[(0, 0)]
    i10 = moments[(1, 0)]
    i01 = moments[(0, 1)]
    i20 = moments[(2, 0)]
    i11 = moments[(1, 1)]
    i02 = moments[(0, 2)]
    return {
        "d_alpha1_log_Delta_boundary": sp.cancel(
            X2 * i00 - 2 * X2 * i10 + c * i01 - L31
        ),
        "d_alpha2_log_Delta_boundary": sp.cancel(
            X1 * i00 + c * i10 - 2 * X1 * i01 - L32
        ),
        "d_alpha1_alpha2_log_Delta_boundary": sp.cancel(
            X2 * i01 - 2 * X2 * i11 + c * i02 - L31 / 2
        ),
        "d_alpha2_alpha1_log_Delta_boundary": sp.cancel(
            X1 * i10 + c * i20 - 2 * X1 * i11 - L32 / 2
        ),
        "Delta_over_Delta_area": sp.cancel(
            X2 * i10
            + X1 * i01
            - X2 * i20
            - X1 * i02
            + c * i11
            - sp.Rational(1, 2)
        ),
    }


def _parse_integrand(value: str) -> sp.Expr:
    return sp.sympify(
        value,
        locals={
            "alpha1": A1,
            "alpha2": A2,
            "x1": X1,
            "x2": X2,
            "x3": X3,
        },
    )


def _integrate_row(integrand: sp.Expr, moments: dict[tuple[int, int], sp.Expr]) -> tuple[sp.Expr, dict[str, sp.Expr]]:
    numerator = sp.cancel(integrand * DELTA)
    polynomial = sp.Poly(numerator, A1, A2, domain="EX")
    if polynomial.total_degree() > 2:
        raise ValueError("vector n1+n2 numerator exceeded quadratic moment span")
    integrated = sp.cancel(
        sum(coefficient * moments[exponents] for exponents, coefficient in polynomial.terms())
    )
    expanded = sp.expand(integrated)
    coordinates = {
        "J_triangle": sp.cancel(expanded.coeff(J)),
        "log_x2_over_x1": sp.cancel(expanded.coeff(L21)),
        "log_x3_over_x1": sp.cancel(expanded.coeff(L31)),
    }
    coordinates["rational_corner"] = sp.cancel(
        expanded
        - coordinates["J_triangle"] * J
        - coordinates["log_x2_over_x1"] * L21
        - coordinates["log_x3_over_x1"] * L31
    )
    reconstruction = sp.cancel(
        integrated
        - coordinates["J_triangle"] * J
        - coordinates["log_x2_over_x1"] * L21
        - coordinates["log_x3_over_x1"] * L31
        - coordinates["rational_corner"]
    )
    if reconstruction != 0:
        raise ValueError("vector n1+n2 function-basis reconstruction failed")
    return numerator, coordinates


def build() -> dict[str, Any]:
    projection = json.loads(PROJECTION.read_text())
    triangle = json.loads(TRIANGLE.read_text())
    if (
        projection["claim_flags"]["GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED"]
        is not True
        or triangle["claim_flags"]["SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED"]
        is not True
    ):
        raise ValueError("vector integration dependency gate is not closed")
    moments = moment_rows()
    defects = _moment_identity_defects(moments)
    if any(value != 0 for value in defects.values()):
        raise ValueError("simplex moment identity failed")

    rows = []
    expressions: dict[str, dict[str, sp.Expr]] = {}
    nonzero_count = 0
    for source_row in projection["vector_n1_plus_n2_channel_integrands"]:
        channel_id = f"{source_row['carrier_id']}_{''.join(str(value) for value in source_row['labels'])}"
        integrand = _parse_integrand(source_row["alpha_integrand"])
        numerator, coordinates = _integrate_row(integrand, moments)
        is_zero = all(value == 0 for value in coordinates.values())
        if is_zero != source_row["identically_zero"]:
            raise ValueError(f"source zero status drifted: {channel_id}")
        nonzero_count += int(not is_zero)
        expressions[channel_id] = coordinates
        rows.append(
            {
                "channel_id": channel_id,
                "carrier_id": source_row["carrier_id"],
                "label_order": source_row["labels"],
                "source_integrand_digest": _digest(source_row),
                "Delta_times_integrand": sp.sstr(sp.factor(numerator)),
                "numerator_total_degree": sp.Poly(numerator, A1, A2, domain="EX").total_degree(),
                "function_basis_coordinates": {
                    basis_id: _rational_function(coordinates[basis_id])
                    for basis_id in FUNCTION_BASIS
                },
                "identically_zero": is_zero,
                "exact_holdouts": [
                    {
                        "point": list(point),
                        "coordinates": {
                            basis_id: _q(coordinates[basis_id].subs(dict(zip(XS, point))))
                            for basis_id in FUNCTION_BASIS
                        },
                    }
                    for point in HOLDOUTS
                ],
            }
        )

    i28_ids = ("I28_123", "I28_132", "I28_231")
    if any(
        sp.cancel(sum(expressions[channel_id][basis_id] for channel_id in i28_ids))
        != 0
        for basis_id in FUNCTION_BASIS
    ):
        raise ValueError("integrated vector I28 relation failed")
    payload = {
        "moment_rows": {
            f"I_{powers[0]}{powers[1]}": sp.sstr(value)
            for powers, value in moments.items()
        },
        "channel_rows": rows,
        "identity_ledger": {
            "moment_boundary_identity_status": {
                key: "ZERO" for key in defects
            },
            "channel_count": len(rows),
            "nonzero_channel_count": nonzero_count,
            "zero_channel_count": len(rows) - nonzero_count,
            "maximum_numerator_degree": max(row["numerator_total_degree"] for row in rows),
            "I28_relation_status": "ZERO_COEFFICIENTWISE",
        },
    }
    return {
        "schema": "quantum-weyl-generic-background-ghost-n1-n2-vector-integrated-functions-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_INTEGRATED_FUNCTIONS",
        "result_state": "COEFFICIENT_COMPUTED",
        "lifecycle_state": "GHOST_VECTOR_N1_N2_GENERIC_FUNCTIONS_INTEGRATED_LONGITUDINAL_CARRIERS_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": projection["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic scalar-flat nonexceptional momentum chart",
            "included_carriers": ["N1_VECTOR", "N2_VECTOR_VECTOR"],
            "excluded_carriers": projection["minimal_missing_carrier_theorem"]["missing_carriers"],
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
        },
        "convention": {
            "simplex": "alpha1>=0, alpha2>=0, alpha1+alpha2<=1",
            "Delta": sp.sstr(DELTA),
            "J_triangle": "integral_simplex 1/Delta",
            "log_basis": ["log(x2/x1)", "log(x3/x1)"],
            "function_basis": list(FUNCTION_BASIS),
            "source_determinant_multiplier": "the vector n1+n2 coefficients and positive-determinant sign are already included upstream",
        },
        **payload,
        "formula_digest": _digest(payload),
        "claim_flags": {
            "GENERIC_GHOST_VECTOR_N1_N2_INTEGRATED_FUNCTIONS_COMPUTED": True,
            "NO_NEW_TRANSCENDENTAL_MASTER_REQUIRED": True,
            "ALL_FIVE_HODGE_RESOLVENT_CARRIERS_EVALUATED": False,
            "GENERIC_GHOST_LONGITUDINAL_CARRIERS_EVALUATED": False,
            "GENERIC_FINITE_SCHUR_ROWS_COMPUTED": False,
            "COMPLETE_GENERIC_GHOST_THIRD_CURVATURE_FUNCTIONS_COMPUTED": False,
            "FULL_BV_FORM_FACTORS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {
            "vector_CPT_projection": _reference(PROJECTION),
            "scalar_triangle_system": _reference(TRIANGLE),
        },
        "next_gate": "ADD_VECTOR_N1_N2_FUNCTIONS_TO_PARTIAL_BV_REPRESENTATIVE_AND_COMPUTE_THREE_LONGITUDINAL_SCHUR_CARRIERS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate integrates the already projected pure minimal-vector N1_VECTOR plus N2_VECTOR_VECTOR ghost slice on the generic scalar-flat carrier. Five simplex moment identities reduce all eleven channels to the scalar triangle, two bubble-log ratios and a rational term; six channels are nonzero and five vanish. It does not evaluate the three D_W longitudinal/mixed carriers, generic finite Schur rows, the complete ghost determinant or full BV form factors, fix finite normalization, supply complete Gamma1/Q1, authorize residual transfer, or establish a Lorentzian theorem."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
    payload = {
        "moment_rows": result["moment_rows"],
        "channel_rows": result["channel_rows"],
        "identity_ledger": result["identity_ledger"],
    }
    if _digest(payload) != result["formula_digest"]:
        raise ValueError("vector integrated-function digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    validate(result)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale ghost vector n1+n2 integrated certificate: {OUTPUT}")
    print("GENERIC GHOST VECTOR N1+N2 INTEGRATED FUNCTIONS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
