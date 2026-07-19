#!/usr/bin/env python3
"""Assemble the physical-Hessian plus integrated ghost-n3 carrier functions."""

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
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_PLUS_GHOST_N3_THIRD_CURVATURE_FORM_FACTORS.json"
SCHEMA = HERE / "schema/generic-background-physical-plus-ghost-n3-third-curvature-form-factors-v1.schema.json"
PHYSICAL = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_THIRD_CURVATURE_FORM_FACTORS.json"
PHYSICAL_TRIANGLE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX.json"
GHOST_POLE3 = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_INTEGRATED_FUNCTIONS.json"
GHOST_I29 = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_I29_INTEGRATED_FUNCTION.json"

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
GHOST_BASIS = FUNCTION_BASIS[:4]


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
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(variable**power for variable, power in zip(XS, term["exponents"]))
        for term in data["numerator_terms"]
    )
    denominator = sum(
        _from_q(term["coefficient"])
        * sp.prod(variable**power for variable, power in zip(XS, term["exponents"]))
        for term in data["denominator_terms"]
    )
    return sp.cancel(numerator / denominator)


def _scale_rational(data: dict[str, Any]) -> sp.Expr:
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(
            variable**power
            for variable, power in zip(XS, term["box_exponents"])
        )
        for term in data["numerator_terms"]
    )
    denominator = sp.prod(
        variable**power
        for variable, power in zip(XS, data["box_denominator_exponents"])
    )
    return sp.cancel(numerator / denominator)


def _physical_rows(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row["channel_id"]: row
        for carrier in value["carrier_functions"]
        for row in carrier["orientation_channels"]
    }


def _ghost_rows(pole3: dict[str, Any], i29: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {row["channel_id"]: row for row in pole3["channel_rows"]}
    rows["I29_123"] = {
        "channel_id": "I29_123",
        "function_basis_coordinates": i29["function_basis_coordinates"],
    }
    return rows


def _evaluate(expression: sp.Expr, point: tuple[int, int, int]) -> dict[str, int]:
    return _q(expression.subs(dict(zip(XS, point))))


def build() -> dict[str, Any]:
    physical, physical_triangle, pole3, i29 = (
        json.loads(path.read_text())
        for path in (PHYSICAL, PHYSICAL_TRIANGLE, GHOST_POLE3, GHOST_I29)
    )
    if (
        physical["claim_flags"]["PHYSICAL_HESSIAN_MELLIN_MS_FORM_FACTOR_REPRESENTATIVE_COMPUTED"]
        is not True
        or pole3["claim_flags"]["TEN_POLE3_GENERIC_INTEGRATED_FUNCTIONS_COMPUTED"]
        is not True
        or i29["claim_flags"]["ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPUTED"]
        is not True
    ):
        raise ValueError("physical-plus-ghost-n3 dependency gate is not closed")

    physical_rows = _physical_rows(physical)
    triangle_rows = {
        row["channel_id"]: row for row in physical_triangle["channel_rows"]
    }
    ghost_rows = _ghost_rows(pole3, i29)
    channel_order = [
        row["channel_id"]
        for carrier in physical["carrier_functions"]
        for row in carrier["orientation_channels"]
    ]
    if set(channel_order) != set(physical_rows) or set(channel_order) != set(ghost_rows):
        raise ValueError("physical and ghost channel sets do not agree")

    rows: list[dict[str, Any]] = []
    expressions: dict[str, dict[str, sp.Expr]] = {}
    scale_rows: dict[str, sp.Expr] = {}
    for channel_id in channel_order:
        physical_row = physical_rows[channel_id]
        physical_triangle_row = triangle_rows[channel_id]
        ghost_row = ghost_rows[channel_id]
        physical_coordinates = {
            basis_id: (
                _rational(physical_row["assembled_rational_coordinate"])
                if basis_id == "rational_corner"
                else _rational(physical_triangle_row["integrated_function_basis"][basis_id])
            )
            for basis_id in FUNCTION_BASIS
        }
        ghost_coordinates = {
            basis_id: _rational(
                ghost_row["function_basis_coordinates"][basis_id]
            )
            for basis_id in GHOST_BASIS
        }
        combined = {
            basis_id: sp.cancel(
                physical_coordinates[basis_id]
                + ghost_coordinates.get(basis_id, sp.S.Zero)
            )
            for basis_id in FUNCTION_BASIS
        }
        scale = _scale_rational(physical_row["combined_scale_derivative"])
        expressions[channel_id] = combined
        scale_rows[channel_id] = scale
        rows.append(
            {
                "channel_id": channel_id,
                "carrier_id": channel_id.split("_", 1)[0],
                "label_order": physical_row["label_order"],
                "assembly_recipe": {
                    "J_triangle": "physical_Hessian+ghost_n3",
                    "log_x2_over_x1": "physical_Hessian+ghost_n3",
                    "log_x3_over_x1": "physical_Hessian+ghost_n3",
                    "rational_corner": "physical_Hessian+ghost_n3",
                    "M14_singlet": "physical_Hessian",
                    "M15_standard_u": "physical_Hessian",
                    "M16_standard_v": "physical_Hessian",
                    "scale_derivative": "physical_Hessian; ghost_n3_is_scale_free",
                },
                "source_row_digests": {
                    "physical_assembled": _digest(physical_row),
                    "physical_triangle": _digest(physical_triangle_row),
                    "ghost_n3": _digest(ghost_row),
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

    i28_ids = ("I28_123", "I28_132", "I28_231")
    relation = {
        basis_id: sp.cancel(
            sum(expressions[channel_id][basis_id] for channel_id in i28_ids)
        )
        for basis_id in FUNCTION_BASIS
    }
    scale_relation = sp.cancel(sum(scale_rows[channel_id] for channel_id in i28_ids))
    if any(value != 0 for value in relation.values()) or scale_relation != 0:
        raise ValueError("combined physical-plus-ghost I28 relation failed")

    formula_payload = {
        "channel_rows": rows,
        "I28_relation": {
            "coordinate_status": {basis_id: "ZERO" for basis_id in FUNCTION_BASIS},
            "scale_derivative_status": "ZERO",
        },
    }
    return {
        "schema": "quantum-weyl-generic-background-physical-plus-ghost-n3-third-curvature-form-factors-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_PLUS_GHOST_N3_THIRD_CURVATURE_FORM_FACTORS",
        "result_state": "COEFFICIENT_COMPUTED",
        "lifecycle_state": "PHYSICAL_PLUS_GHOST_N3_FIVE_CARRIER_REPRESENTATIVE_COMPUTED_FULL_BV_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": physical["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic scalar-flat nonexceptional momentum chart",
            "included_sectors": [
                "same-gauge rank-nine traceless physical Hessian",
                "integrated scalar-flat generic ghost n=3 triangle",
            ],
            "excluded_sectors": [
                "curved-Endo ghost n=1 and n=2 insertion traces",
                "finite longitudinal Schur rows and multiplicative term",
                "remaining nonminimal and BV rows",
            ],
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
        },
        "function_basis": list(FUNCTION_BASIS),
        "assembly_convention": {
            "physical_multiplier": "bosonic (1/6) Tr[(H0^-1 H1)^3] and finite H1-H2 contacts already included upstream",
            "ghost_multiplier": "W=-2 Ric and fermionic Tr-log multiplier -8/3 already included upstream",
            "subtraction": "physical common resolved-boundary Mellin minimal subtraction; integrated ghost n3 triangle is scale-free",
            "finite_C2_normalization": "NOT_FIXED",
        },
        **formula_payload,
        "quotient_ledger": {
            "raw_channel_count": 11,
            "quotient_dimension": 10,
            "raw_channel_order": channel_order,
            "unique_relation": "I28_123+I28_132+I28_231=0",
            "relation_status": "ZERO_COEFFICIENTWISE",
        },
        "formula_digest": _digest(formula_payload),
        "claim_flags": {
            "PHYSICAL_PLUS_GHOST_N3_FIVE_CARRIER_FUNCTIONS_ASSEMBLED": True,
            "PHYSICAL_PLUS_GHOST_N3_MELLIN_MS_REPRESENTATIVE_COMPUTED": True,
            "GHOST_N1_INSERTION_TRACE_COMPUTED": False,
            "GHOST_N2_INSERTION_TRACE_COMPUTED": False,
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
            "physical_form_factors": _reference(PHYSICAL),
            "physical_triangle": _reference(PHYSICAL_TRIANGLE),
            "ghost_pole3_functions": _reference(GHOST_POLE3),
            "ghost_I29_function": _reference(GHOST_I29),
        },
        "next_gate": "COMPUTE_GHOST_N1_N2_AND_GENERIC_FINITE_SCHUR_ROWS_THEN_ADD_REMAINING_BV_SECTORS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate combines the certified same-gauge physical-Hessian five-carrier representative with all eleven integrated generic scalar-flat ghost n=3 triangle functions, using their upstream determinant signs and multiplicities. It is a coefficient-bearing partial-BV result, not the complete ghost determinant or repository effective action. Ghost n=1/n=2 insertions, generic finite Schur rows, remaining BV sectors, the independent finite C2 normalization, complete Gamma1/Q1, residual transfer and all Lorentzian claims remain open."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
    if _digest(
        {
            "channel_rows": result["channel_rows"],
            "I28_relation": result["I28_relation"],
        }
    ) != result["formula_digest"]:
        raise ValueError("physical-plus-ghost-n3 formula digest drifted")


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
        raise SystemExit(f"stale physical-plus-ghost-n3 certificate: {OUTPUT}")
    print("GENERIC BACKGROUND PHYSICAL PLUS GHOST N3 FORM FACTORS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
