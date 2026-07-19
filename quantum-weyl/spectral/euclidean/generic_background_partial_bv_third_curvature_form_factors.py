#!/usr/bin/env python3
"""Assemble every currently integrated generic parity-even BV carrier row."""

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
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PARTIAL_BV_THIRD_CURVATURE_FORM_FACTORS.json"
SCHEMA = HERE / "schema/generic-background-partial-bv-third-curvature-form-factors-v1.schema.json"
PARTIAL_N3 = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_PLUS_GHOST_N3_THIRD_CURVATURE_FORM_FACTORS.json"
PHYSICAL = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_THIRD_CURVATURE_FORM_FACTORS.json"
PHYSICAL_TRIANGLE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX.json"
GHOST_POLE3 = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_INTEGRATED_FUNCTIONS.json"
GHOST_I29 = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_I29_INTEGRATED_FUNCTION.json"
GHOST_VECTOR = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_INTEGRATED_FUNCTIONS.json"

X1, X2, X3 = sp.symbols("x1 x2 x3")
XS = (X1, X2, X3)
HOLDOUTS = ((2, 3, 5), (3, 5, 7))
FUNCTION_BASIS = (
    "J_triangle",
    "log_x2_over_x1",
    "log_x3_over_x1",
    "rational_corner",
    "M14_singlet",
    "M15_standard_u",
    "M16_standard_v",
)


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


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _rational(data: dict[str, Any]) -> sp.Expr:
    def polynomial(terms: list[dict[str, Any]]) -> sp.Expr:
        return sum(
            _from_q(term["coefficient"])
            * sp.prod(variable**power for variable, power in zip(XS, term["exponents"]))
            for term in terms
        )

    return sp.cancel(polynomial(data["numerator_terms"]) / polynomial(data["denominator_terms"]))


def _scale(data: dict[str, Any]) -> sp.Expr:
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(variable**power for variable, power in zip(XS, term["box_exponents"]))
        for term in data["numerator_terms"]
    )
    denominator = sp.prod(
        variable**power
        for variable, power in zip(XS, data["box_denominator_exponents"])
    )
    return sp.cancel(numerator / denominator)


def _evaluate(expression: sp.Expr, point: tuple[int, int, int]) -> dict[str, int]:
    return _q(expression.subs(dict(zip(XS, point))))


def build() -> dict[str, Any]:
    partial_n3, physical, physical_triangle, pole3, i29, vector = (
        json.loads(path.read_text())
        for path in (PARTIAL_N3, PHYSICAL, PHYSICAL_TRIANGLE, GHOST_POLE3, GHOST_I29, GHOST_VECTOR)
    )
    if (
        partial_n3["claim_flags"]["PHYSICAL_PLUS_GHOST_N3_MELLIN_MS_REPRESENTATIVE_COMPUTED"]
        is not True
        or vector["claim_flags"]["GENERIC_GHOST_VECTOR_N1_N2_INTEGRATED_FUNCTIONS_COMPUTED"]
        is not True
    ):
        raise ValueError("partial BV assembly dependency gate is not closed")

    physical_rows = {
        row["channel_id"]: row
        for carrier in physical["carrier_functions"]
        for row in carrier["orientation_channels"]
    }
    triangle_rows = {row["channel_id"]: row for row in physical_triangle["channel_rows"]}
    ghost_n3_rows = {row["channel_id"]: row for row in pole3["channel_rows"]}
    ghost_n3_rows["I29_123"] = {
        "channel_id": "I29_123",
        "function_basis_coordinates": i29["function_basis_coordinates"],
    }
    vector_rows = {row["channel_id"]: row for row in vector["channel_rows"]}
    partial_rows = {row["channel_id"]: row for row in partial_n3["channel_rows"]}
    channel_order = partial_n3["quotient_ledger"]["raw_channel_order"]
    if not all(set(rows) == set(channel_order) for rows in (physical_rows, triangle_rows, ghost_n3_rows, vector_rows, partial_rows)):
        raise ValueError("partial BV channel crosswalk drifted")

    output_rows = []
    expressions: dict[str, dict[str, sp.Expr]] = {}
    scales: dict[str, sp.Expr] = {}
    for channel_id in channel_order:
        physical_row = physical_rows[channel_id]
        triangle_row = triangle_rows[channel_id]
        ghost_n3_row = ghost_n3_rows[channel_id]
        vector_row = vector_rows[channel_id]
        physical_coordinates = {
            basis_id: (
                _rational(physical_row["assembled_rational_coordinate"])
                if basis_id == "rational_corner"
                else _rational(triangle_row["integrated_function_basis"][basis_id])
            )
            for basis_id in FUNCTION_BASIS
        }
        ghost_n3_coordinates = {
            basis_id: _rational(ghost_n3_row["function_basis_coordinates"][basis_id])
            for basis_id in FUNCTION_BASIS[:4]
        }
        vector_coordinates = {
            basis_id: _rational(vector_row["function_basis_coordinates"][basis_id])
            for basis_id in FUNCTION_BASIS[:4]
        }
        combined = {
            basis_id: sp.cancel(
                physical_coordinates[basis_id]
                + ghost_n3_coordinates.get(basis_id, 0)
                + vector_coordinates.get(basis_id, 0)
            )
            for basis_id in FUNCTION_BASIS
        }
        scale = _scale(physical_row["combined_scale_derivative"])
        expressions[channel_id] = combined
        scales[channel_id] = scale
        partial_row = partial_rows[channel_id]
        output_rows.append(
            {
                "channel_id": channel_id,
                "carrier_id": channel_id.split("_", 1)[0],
                "label_order": physical_row["label_order"],
                "included_sector_recipe": {
                    "physical_Hessian": list(FUNCTION_BASIS) + ["scale_derivative"],
                    "ghost_n3": list(FUNCTION_BASIS[:4]),
                    "ghost_vector_n1_n2": list(FUNCTION_BASIS[:4]),
                },
                "source_row_digests": {
                    "prior_partial_n3": _digest(partial_row),
                    "ghost_vector_n1_n2": _digest(vector_row),
                },
                "combined_coordinate_digests": {
                    basis_id: _digest(sp.srepr(combined[basis_id]))
                    for basis_id in FUNCTION_BASIS
                },
                "combined_scale_digest": _digest(sp.srepr(scale)),
                "exact_holdouts": [
                    {
                        "point": list(point),
                        "coordinates": {
                            basis_id: _evaluate(combined[basis_id], point)
                            for basis_id in FUNCTION_BASIS
                        },
                        "scale_derivative": _evaluate(scale, point),
                    }
                    for point in HOLDOUTS
                ],
            }
        )

    i28 = ("I28_123", "I28_132", "I28_231")
    if any(
        sp.cancel(sum(expressions[channel][basis_id] for channel in i28)) != 0
        for basis_id in FUNCTION_BASIS
    ) or sp.cancel(sum(scales[channel] for channel in i28)) != 0:
        raise ValueError("partial BV I28 relation failed")
    payload = {
        "channel_rows": output_rows,
        "I28_relation": {
            "coordinate_status": {basis_id: "ZERO" for basis_id in FUNCTION_BASIS},
            "scale_derivative_status": "ZERO",
        },
    }
    return {
        "schema": "quantum-weyl-generic-background-partial-bv-third-curvature-form-factors-v1",
        "result_id": "GENERIC_BACKGROUND_PARTIAL_BV_THIRD_CURVATURE_FORM_FACTORS",
        "result_state": "COEFFICIENT_COMPUTED",
        "lifecycle_state": "PHYSICAL_GHOST_N3_AND_VECTOR_N1_N2_ASSEMBLED_LONGITUDINAL_AND_REMAINING_BV_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": partial_n3["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic scalar-flat nonexceptional momentum chart",
            "included_sectors": [
                "same-gauge rank-nine physical Hessian",
                "ghost n=3 triangle",
                "ghost N1_VECTOR plus N2_VECTOR_VECTOR",
            ],
            "excluded_sectors": [
                "N1_LONGITUDINAL_SCALAR",
                "N2_VECTOR_LONGITUDINAL",
                "N2_LONGITUDINAL_LONGITUDINAL",
                "generic finite Schur rows and remaining BV sectors",
            ],
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
        },
        "function_basis": list(FUNCTION_BASIS),
        "sector_disposition": {
            "physical_Hessian": "COMPUTED",
            "ghost_n3": "COMPUTED",
            "ghost_vector_n1_n2": "COMPUTED",
            "ghost_longitudinal_and_mixed": "NOT_COMPUTED",
            "remaining_BV": "NOT_COMPUTED",
            "finite_C2_normalization": "NOT_FIXED",
        },
        **payload,
        "quotient_ledger": {
            "raw_channel_count": 11,
            "quotient_dimension": 10,
            "raw_channel_order": channel_order,
            "unique_relation": "I28_123+I28_132+I28_231=0",
            "relation_status": "ZERO_COEFFICIENTWISE",
        },
        "formula_digest": _digest(payload),
        "claim_flags": {
            "PARTIAL_BV_FIVE_CARRIER_REPRESENTATIVE_COMPUTED": True,
            "GHOST_VECTOR_N1_N2_INCLUDED": True,
            "GHOST_N3_INCLUDED": True,
            "GHOST_LONGITUDINAL_CARRIERS_INCLUDED": False,
            "GENERIC_FINITE_SCHUR_ROWS_COMPUTED": False,
            "ABSOLUTE_FINITE_C2_NORMALIZATION_FIXED": False,
            "FULL_GHOST_DETERMINANT_COMPUTED": False,
            "FULL_BV_FORM_FACTORS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {
            "prior_partial_n3": _reference(PARTIAL_N3),
            "physical_form_factors": _reference(PHYSICAL),
            "physical_triangle": _reference(PHYSICAL_TRIANGLE),
            "ghost_pole3_functions": _reference(GHOST_POLE3),
            "ghost_I29_function": _reference(GHOST_I29),
            "ghost_vector_n1_n2_functions": _reference(GHOST_VECTOR),
        },
        "next_gate": "COMPUTE_THREE_LONGITUDINAL_SCHUR_CARRIERS_AND_REMAINING_BV_SECTORS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate assembles every currently integrated generic scalar-flat parity-even row: the physical Hessian, all ghost n=3 channels, and the pure-vector ghost n=1+n=2 slice. It is a partial-BV five-carrier representative, not the complete ghost determinant or full BV effective action. Three longitudinal/mixed D_W carriers, generic finite Schur rows, remaining BV sectors, finite C2 normalization, complete Gamma1/Q1, residual transfer and all Lorentzian claims remain open."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
    payload = {"channel_rows": result["channel_rows"], "I28_relation": result["I28_relation"]}
    if _digest(payload) != result["formula_digest"]:
        raise ValueError("partial BV formula digest drifted")


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
        raise SystemExit(f"stale partial BV form-factor certificate: {OUTPUT}")
    print("GENERIC BACKGROUND PARTIAL BV THIRD-CURVATURE FORM FACTORS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
