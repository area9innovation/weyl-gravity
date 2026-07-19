#!/usr/bin/env python3
"""Assemble the physical-Hessian third-curvature form-factor representative."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_physical_hessian_triangle_relative_ibp_boundary_flux import (
    X1,
    X2,
    X3,
    rational_from_data,
)
from .generic_background_physical_hessian_triangle_six_master_coordinates import (
    _rational_function,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_THIRD_CURVATURE_FORM_FACTORS.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-third-curvature-form-factors-v1.schema.json"
TRIANGLE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX.json"
CONTACTS = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_FINITE_ROWS.json"
INCIDENCE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_FULL_BOUNDARY_INCIDENCE.json"
PROJECTION = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json"
MANIFEST = ROOT / "quantum-weyl/transfer/certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json"

XS = (X1, X2, X3)
HOLDOUTS = ((2, 3, 5), (3, 5, 7))
TRIANGLE_BASIS = (
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


def _polynomial_row_expression(
    row: dict[str, Any], term_key: str, denominator_key: str
) -> sp.Expr:
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(variable**power for variable, power in zip(XS, term["box_exponents"]))
        for term in row[term_key]
    )
    denominator = sp.prod(
        variable**power for variable, power in zip(XS, row[denominator_key])
    )
    return sp.cancel(numerator / denominator)


def _contact_expression(row: dict[str, Any]) -> sp.Expr:
    return _polynomial_row_expression(
        row, "minimal_subtraction_finite_terms", "box_denominator_exponents"
    )


def _scale_expression(row: dict[str, Any]) -> sp.Expr:
    return _polynomial_row_expression(
        row, "numerator_terms", "box_denominator_exponents"
    )


def _channel_id(carrier: str, labels: list[int]) -> str:
    return f"{carrier}_{''.join(str(label) for label in labels)}"


def _evaluate(expression: sp.Expr, point: tuple[int, int, int]) -> sp.Rational:
    return sp.Rational(expression.subs(dict(zip(XS, point))))


def _load() -> tuple[dict[str, Any], ...]:
    return tuple(
        json.loads(path.read_text())
        for path in (TRIANGLE, CONTACTS, INCIDENCE, PROJECTION, MANIFEST)
    )


def build() -> dict[str, Any]:
    triangle, contacts, incidence, projection, manifest = _load()
    if not triangle["claim_flags"]["ALL_ELEVEN_CHANNELS_INTEGRATED"]:
        raise ValueError("the physical triangle is not integrated")
    if not contacts["claim_flags"]["ALL_THREE_CONTACT_FINITE_ROWS_PROJECTED"]:
        raise ValueError("the finite contact rows are not complete")
    if not incidence["claim_flags"]["FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED"]:
        raise ValueError("the combined scale row is not complete")

    triangle_rows = {row["channel_id"]: row for row in triangle["channel_rows"]}
    incidence_rows = {row["channel_id"]: row for row in incidence["channel_rows"]}
    contact_rows: dict[str, list[dict[str, Any]]] = {}
    for row in contacts["projection_rows"]:
        channel_id = _channel_id(row["carrier_id"], row["label_order"])
        contact_rows.setdefault(channel_id, []).append(row)

    stabilizers = {
        row["carrier_id"]: row["stabilizer"] for row in manifest["carrier_manifest"]
    }
    projection_rows = projection["projection_rows"]
    if len(projection_rows) != 11:
        raise ValueError("raw channel count drifted")

    carrier_rows: dict[str, list[dict[str, Any]]] = {
        carrier: [] for carrier in ("I10", "I24", "I25", "I28", "I29")
    }
    for metadata in projection_rows:
        channel_id = metadata["channel_id"]
        if len(contact_rows.get(channel_id, [])) != 3:
            raise ValueError(f"contact incidence is incomplete for {channel_id}")
        triangle_row = triangle_rows[channel_id]
        incidence_row = incidence_rows[channel_id]
        triangle_coordinates = {
            basis: rational_from_data(triangle_row["integrated_function_basis"][basis])
            for basis in TRIANGLE_BASIS
        }
        contact_sum = sp.cancel(
            sum((_contact_expression(row) for row in contact_rows[channel_id]), sp.S.Zero)
        )
        assembled_rational = sp.cancel(
            triangle_coordinates["rational_corner"] + contact_sum
        )
        scale_row = _scale_expression(incidence_row["combined_scale_row"])
        source_digests = {
            "triangle_channel": _digest(triangle_row),
            "finite_contact_channels": [_digest(row) for row in contact_rows[channel_id]],
            "combined_scale_channel": _digest(incidence_row),
        }
        holdouts = []
        for point in HOLDOUTS:
            holdouts.append(
                {
                    "box_point": list(point),
                    "triangle_basis_coordinates": {
                        basis: _q(_evaluate(value, point))
                        for basis, value in triangle_coordinates.items()
                    },
                    "finite_contact_sum": _q(_evaluate(contact_sum, point)),
                    "assembled_rational_coordinate": _q(
                        _evaluate(assembled_rational, point)
                    ),
                    "combined_scale_derivative": _q(_evaluate(scale_row, point)),
                }
            )
        carrier_rows[metadata["carrier_id"]].append(
            {
                "channel_id": channel_id,
                "label_order": metadata["label_order"],
                "source_row_digests": source_digests,
                "finite_contact_sum": _rational_function(contact_sum),
                "assembled_rational_coordinate": _rational_function(assembled_rational),
                "combined_scale_derivative": incidence_row["combined_scale_row"],
                "exact_holdouts": holdouts,
                "assembly_recipe": {
                    "at_unit_scale": (
                        "import all seven triangle basis coordinates; replace "
                        "rational_corner by rational_corner+finite_contact_sum"
                    ),
                    "at_general_scale": (
                        "unit_scale_representative+log(mu^2)*combined_scale_derivative"
                    ),
                    "overall_loop_prefactor": "(4*pi)^-2 excluded",
                },
            }
        )

    # The selected four-dimensional quotient removes the symmetric I28 row.
    i28_rows = carrier_rows["I28"]
    if len(i28_rows) != 3:
        raise ValueError("I28 orbit dimension drifted")
    i28_ids = [row["channel_id"] for row in i28_rows]
    for basis in TRIANGLE_BASIS:
        if sp.cancel(
            sum(
                rational_from_data(
                    triangle_rows[channel_id]["integrated_function_basis"][basis]
                )
                for channel_id in i28_ids
            )
        ) != 0:
            raise ValueError(f"triangle I28 relation failed in {basis}")
    for key in ("finite_contact_sum", "assembled_rational_coordinate"):
        if sp.cancel(sum(rational_from_data(row[key]) for row in i28_rows)) != 0:
            raise ValueError(f"assembled I28 relation failed in {key}")
    if sp.cancel(
        sum(
            _scale_expression(incidence_rows[channel_id]["combined_scale_row"])
            for channel_id in i28_ids
        )
    ) != 0:
        raise ValueError("scale I28 relation failed")

    functions = [
        {
            "carrier_id": carrier,
            "stabilizer": stabilizers[carrier],
            "orientation_count": len(carrier_rows[carrier]),
            "orientation_channels": carrier_rows[carrier],
        }
        for carrier in ("I10", "I24", "I25", "I28", "I29")
    ]
    payload = {
        "function_basis": {
            "triangle_basis": list(TRIANGLE_BASIS),
            "finite_contact_basis": "rational function added to rational_corner",
            "scale_basis": "log(mu^2) times combined_scale_derivative",
        },
        "carrier_functions": functions,
        "quotient_ledger": {
            "carrier_function_count": 5,
            "raw_orientation_channel_count": 11,
            "four_dimensional_relation_rank": 1,
            "quotient_dimension": 10,
            "section": "REMOVE_TRIVIAL_S3_COMPONENT_OF_I28",
            "I28_relation": "+".join(i28_ids) + "=0 coefficientwise",
            "status": "EXACT",
        },
    }
    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-third-curvature-form-factors-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_THIRD_CURVATURE_FORM_FACTORS",
        "result_state": "FIVE_CARRIER_LABELLED_PHYSICAL_HESSIAN_MELLIN_MS_FORM_FACTOR_REPRESENTATIVE_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": triangle["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic scalar-flat nonexceptional momentum chart",
            "sector": "same-gauge rank-nine traceless physical Hessian only",
            "subtraction": "common resolved-boundary Mellin minimal subtraction",
            "normalization": "unit dimensionless reference scale with explicit log(mu^2) reconstruction",
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
        },
        "scheme_disposition": {
            "computed_representative": "COMMON_MELLIN_MINIMAL_SUBTRACTION",
            "finite_C2_normalization": "NOT_FIXED",
            "meaning": (
                "the five carrier-labelled nonlocal functions are fixed in the declared "
                "Mellin-MS representative; an independent mu-independent local C2 "
                "counterterm can shift their cubic expansion"
            ),
        },
        **payload,
        "formula_digest": _digest(payload),
        "dependencies": {
            "integrated_physical_triangle": _reference(TRIANGLE),
            "finite_H1_H2_contacts": _reference(CONTACTS),
            "combined_boundary_incidence": _reference(INCIDENCE),
            "five_carrier_projection": _reference(PROJECTION),
            "four_dimensional_carrier_manifest": _reference(MANIFEST),
        },
        "claim_flags": {
            "FIVE_PHYSICAL_CARRIER_FUNCTIONS_ASSEMBLED": True,
            "ALL_ELEVEN_ORIENTATION_CHANNELS_ASSEMBLED": True,
            "COMBINED_SCALE_ROWS_INCLUDED": True,
            "FOUR_DIMENSIONAL_I28_RELATION_VERIFIED": True,
            "PHYSICAL_HESSIAN_MELLIN_MS_FORM_FACTOR_REPRESENTATIVE_COMPUTED": True,
            "ABSOLUTE_FINITE_C2_NORMALIZATION_FIXED": False,
            "FULL_BV_FORM_FACTORS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "QME_OR_ANOMALY_STATUS_CHANGED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "ADD_GHOST_AND_REMAINING_BV_ROWS_AND_FIX_OR_PARAMETERIZE_THE_FINITE_C2_NORMALIZATION",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate assembles "
            "the integrated three-H1 triangle, all three finite H1-H2 contacts and "
            "their combined scale rows into the five carrier-labelled third-curvature "
            "form-factor functions of the same-gauge rank-nine physical Hessian in the "
            "declared Mellin minimal-subtraction representative. It does not fix the "
            "independent finite local C2 normalization, add ghost or remaining BV rows, "
            "supply complete Gamma1 or Q1, change the anomaly/QME disposition, authorize "
            "residual transfer, or establish a Lorentzian or Hadamard theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        key: value[key] for key in ("function_basis", "carrier_functions", "quotient_ledger")
    }
    if _digest(payload) != value["formula_digest"]:
        raise ValueError("physical form-factor digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit(f"stale physical form-factor certificate: {OUTPUT}")
        print("GENERIC PHYSICAL HESSIAN THIRD-CURVATURE FORM FACTORS: PASS")
        return 0
    OUTPUT.write_text(rendered)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
