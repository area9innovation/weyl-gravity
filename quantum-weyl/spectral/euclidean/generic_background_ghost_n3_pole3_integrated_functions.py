#!/usr/bin/env python3
"""Integrate the ten generic pole-three ghost triangle channels exactly."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

try:
    from .generic_background_ghost_n3_pole3_relative_ibp import (
        X1,
        X2,
        X3,
        XS,
        rational_function_from_data,
    )
except ImportError:
    from generic_background_ghost_n3_pole3_relative_ibp import (
        X1,
        X2,
        X3,
        XS,
        rational_function_from_data,
    )


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_INTEGRATED_FUNCTIONS.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-pole3-integrated-functions-v1.schema.json"
RELATIVE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_RELATIVE_IBP.json"
TRIANGLE = HERE / "certificates/GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM.json"
SYMMETRIC = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION.json"

BASIS_IDS = ("J_triangle", "log_x2_over_x1", "log_x3_over_x1", "rational_corner")
REPRESENTATIVES = ("I10_123", "I24_123", "I25_123", "I28_123")


def _q(value: sp.Expr | int) -> dict[str, int]:
    value = sp.Rational(value)
    return {"numerator": int(value.p), "denominator": int(value.q)}


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


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


def _representative_corner_flux(
    representatives: dict[str, Any],
) -> tuple[dict[str, sp.Expr], dict[str, Any]]:
    fluxes = {}
    ledger = {}
    for representative_id in REPRESENTATIVES:
        primitive = representatives[representative_id]
        constant_terms = {"U": sp.S.Zero, "V": sp.S.Zero, "W": sp.S.Zero}
        for row in primitive["coefficients"]:
            if row["monomial_exponents"] == [0, 0]:
                constant_terms[row["group"]] += rational_function_from_data(
                    row["coefficient"]
                )
        U_C = sp.cancel(constant_terms["U"])
        V_C = sp.cancel(constant_terms["V"])
        if sp.cancel(U_C - V_C) != 0:
            raise ValueError(f"unequal alpha0 corner weights: {representative_id}")
        other_corners = [
            row for row in primitive["corner_leading_rows"]
            if row["corner_id"] != "alpha0_vertex"
        ]
        if not all(row["leading_pair_zero"] for row in other_corners):
            raise ValueError(f"unexpected second corner carrier: {representative_id}")
        # The stored oriented alpha0 angular form is
        # -(U_C cos^2+V_C sin^2)/(x1 cos+x3 sin)^2 dtheta.
        # U_C=V_C and I_cos2+I_sin2=1/(x1*x3).
        flux = sp.cancel(-U_C / (X1 * X3))
        fluxes[representative_id] = flux
        ledger[representative_id] = {
            "nonzero_corner": "alpha0_vertex",
            "other_corner_fluxes": "ZERO",
            "U_C": _rational_function(U_C),
            "V_C": _rational_function(V_C),
            "U_C_minus_V_C": "ZERO",
            "oriented_integrated_flux": _rational_function(flux),
        }
    return fluxes, ledger


def build() -> dict[str, Any]:
    relative = json.loads(RELATIVE.read_text())
    triangle = json.loads(TRIANGLE.read_text())
    symmetric = json.loads(SYMMETRIC.read_text())
    if not relative["claim_flags"]["TEN_POLE3_ROWS_REDUCED_TO_J_AND_TWO_DERIVATIVE_MASTERS"]:
        raise ValueError("relative-IBP dependency is not certified")
    if not triangle["claim_flags"]["TWO_LOG_MASTER_REDUCTION_COMPUTED"]:
        raise ValueError("scalar-triangle dependency is not certified")

    triangle_masters = {
        master_id: {
            basis_id: rational_function_from_data(value)
            for basis_id, value in row.items()
        }
        for master_id, row in triangle["master_rows"].items()
    }
    representative_fluxes, representative_ledger = _representative_corner_flux(
        relative["representative_primitives"]
    )
    symmetric_rows = {
        row["channel_id"]: row["integrated_value"] for row in symmetric["channel_rows"]
    }

    channel_rows = []
    expressions: dict[str, dict[str, sp.Expr]] = {}
    fixture = {X1: 1, X2: 1, X3: 1}
    for row in relative["channel_rows"]:
        master_coordinates = {
            master_id: rational_function_from_data(value)
            for master_id, value in row["master_coordinates"].items()
        }
        coordinates = {}
        for basis_id in BASIS_IDS[:3]:
            coordinates[basis_id] = sp.cancel(
                (master_coordinates["J_triangle"] if basis_id == "J_triangle" else 0)
                + master_coordinates["M_x1"] * triangle_masters["M_x1"][basis_id]
                + master_coordinates["M_x2"] * triangle_masters["M_x2"][basis_id]
            )
        permutation = row["x_permutation"]
        substitution = {XS[i]: XS[permutation[i]] for i in range(3)}
        coordinates["rational_corner"] = sp.cancel(
            representative_fluxes[row["representative_id"]].subs(
                substitution, simultaneous=True
            )
        )
        expected = symmetric_rows[row["channel_id"]]
        expected_j = _from_q(expected["scalar_triangle_master_coefficient"])
        expected_rational = _from_q(expected["rational"])
        actual_j = sp.cancel(coordinates["J_triangle"].subs(fixture))
        actual_rational = sp.cancel(coordinates["rational_corner"].subs(fixture))
        if actual_j != expected_j or actual_rational != expected_rational:
            raise ValueError(f"symmetric-point regression failed: {row['channel_id']}")
        expressions[row["channel_id"]] = coordinates
        channel_rows.append(
            {
                "channel_id": row["channel_id"],
                "representative_id": row["representative_id"],
                "x_permutation": row["x_permutation"],
                "function_basis_coordinates": {
                    basis_id: _rational_function(coordinates[basis_id])
                    for basis_id in BASIS_IDS
                },
                "symmetric_point_regression": {
                    "J_triangle_coefficient": _q(actual_j),
                    "rational_term": _q(actual_rational),
                    "log_terms": "ZERO_AT_X1_EQUALS_X2_EQUALS_X3",
                    "status": "EXACT_MATCH",
                },
            }
        )

    i28_ids = ("I28_123", "I28_132", "I28_231")
    i28_defects = {}
    for basis_id in BASIS_IDS:
        defect = sp.cancel(sum(expressions[channel_id][basis_id] for channel_id in i28_ids))
        if defect != 0:
            raise ValueError(f"integrated I28 relation failed: {basis_id}")
        i28_defects[basis_id] = "ZERO"

    payload = {
        "representative_corner_fluxes": representative_ledger,
        "channel_rows": channel_rows,
        "identity_ledger": {
            "I28_integrated_relation": "I28_123+I28_132+I28_231=0",
            "I28_basis_coordinate_defects": i28_defects,
            "symmetric_point_regression_count": len(channel_rows),
            "symmetric_point_regression_status": "ALL_EXACT_MATCH",
        },
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    result = {
        "schema": "quantum-weyl-generic-background-ghost-n3-pole3-integrated-functions-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N3_POLE3_INTEGRATED_FUNCTIONS",
        "result_state": "COEFFICIENT_COMPUTED",
        "lifecycle_state": "TEN_POLE3_GENERIC_FUNCTIONS_COMPLETE_I29_POLE4_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": relative["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "curvature_order": 3,
            "kinematics": "positive nonexceptional x1,x2,x3 with Kallen lambda nonzero",
            "included_channels": [row["channel_id"] for row in channel_rows],
            "excluded_channel": "I29_123 pole-four row",
        },
        "convention": {
            "function_basis": [
                "J_triangle",
                "log(x2/x1)",
                "log(x3/x1)",
                "1",
            ],
            "channel_formula": "A_J*J_triangle+A_21*log(x2/x1)+A_31*log(x3/x1)+R_corner",
            "corner_orientation": "stored oriented punctured-simplex boundary form",
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
            "W_and_Tr_log_multiplier": "-8/3 already included upstream",
        },
        **payload,
        "formula_digest": digest,
        "coefficient_disposition": {
            "ten_pole3_generic_integrated_functions": "COMPUTED",
            "I29_pole4_reduction": "NOT_COMPUTED",
            "all_eleven_generic_integrated_functions": "PARTIAL_10_OF_11_COMPLETE",
            "physical_fourth_order_Hessian_functions": "NOT_COMPUTED",
        },
        "claim_flags": {
            "TEN_POLE3_GENERIC_INTEGRATED_FUNCTIONS_COMPUTED": True,
            "CORNER_ANGULAR_FLUXES_EVALUATED": True,
            "TWO_BUBBLE_LOG_RATIOS_EXPLICIT": True,
            "SYMMETRIC_POINT_REGRESSION_EXACT": True,
            "INTEGRATED_I28_RELATION_VERIFIED": True,
            "I29_POLE4_REDUCED": False,
            "ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPUTED": False,
            "COMPLETE_GENERIC_GHOST_DETERMINANT_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {
            "relative_IBP": _reference(RELATIVE),
            "scalar_triangle_differential_system": _reference(TRIANGLE),
            "symmetric_point_integration": _reference(SYMMETRIC),
        },
        "next_gate": "REDUCE_THE_I29_POLE4_ROW_TO_THE_SAME_TRIANGLE_AND_BUBBLE_MASTER_SYSTEM",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate gives complete exact generic functions for the ten pole-three n=3 ghost channels as rational coefficients multiplying the scalar triangle, two bubble-log ratios, and a rational punctured-corner flux. It independently regresses every row against the exact symmetric-point integration. The pole-four I29 row, the complete eleven-channel ghost block, the generic physical fourth-order Hessian, complete Gamma1/Q1, residual transfer, and every Lorentzian, Hadamard, particle, positivity, scattering, or unitarity claim remain open."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        "representative_corner_fluxes": value["representative_corner_fluxes"],
        "channel_rows": value["channel_rows"],
        "identity_ledger": value["identity_ledger"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != value["formula_digest"]:
        raise ValueError("integrated pole-three formula digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale integrated pole-three certificate: {OUTPUT}")
    if not args.emit and not args.check:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
