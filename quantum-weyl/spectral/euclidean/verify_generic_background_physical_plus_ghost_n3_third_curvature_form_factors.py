#!/usr/bin/env python3
"""Independent consumer for physical plus integrated ghost-n3 carrier functions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_PLUS_GHOST_N3_THIRD_CURVATURE_FORM_FACTORS.json"
SCHEMA = HERE / "schema/generic-background-physical-plus-ghost-n3-third-curvature-form-factors-v1.schema.json"
X1, X2, X3 = sp.symbols("x1 x2 x3")
XS = (X1, X2, X3)
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


def _q(value: sp.Expr) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _rational(data: dict[str, Any]) -> sp.Expr:
    def polynomial(terms: list[dict[str, Any]]) -> sp.Expr:
        return sum(
            _from_q(term["coefficient"])
            * sp.prod(
                variable**power
                for variable, power in zip(XS, term["exponents"])
            )
            for term in terms
        )

    return sp.cancel(polynomial(data["numerator_terms"]) / polynomial(data["denominator_terms"]))


def _scale(data: dict[str, Any]) -> sp.Expr:
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


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    dependencies: dict[str, dict[str, Any]] = {}
    for dependency_id, reference in value["dependencies"].items():
        path = ROOT / reference["path"]
        if _sha256(path) != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {dependency_id}")
        dependency = json.loads(path.read_text())
        if dependency["result_id"] != reference["result_id"]:
            raise ValueError(f"dependency result id drifted: {dependency_id}")
        dependencies[dependency_id] = dependency

    physical = dependencies["physical_form_factors"]
    physical_rows = {
        row["channel_id"]: row
        for carrier in physical["carrier_functions"]
        for row in carrier["orientation_channels"]
    }
    triangle_rows = {
        row["channel_id"]: row
        for row in dependencies["physical_triangle"]["channel_rows"]
    }
    ghost_rows = {
        row["channel_id"]: row
        for row in dependencies["ghost_pole3_functions"]["channel_rows"]
    }
    ghost_rows["I29_123"] = {
        "channel_id": "I29_123",
        "function_basis_coordinates": dependencies["ghost_I29_function"]["function_basis_coordinates"],
    }

    expressions: dict[str, dict[str, sp.Expr]] = {}
    scales: dict[str, sp.Expr] = {}
    for output_row in value["channel_rows"]:
        channel_id = output_row["channel_id"]
        physical_row = physical_rows[channel_id]
        triangle_row = triangle_rows[channel_id]
        ghost_row = ghost_rows[channel_id]
        if output_row["source_row_digests"] != {
            "physical_assembled": _digest(physical_row),
            "physical_triangle": _digest(triangle_row),
            "ghost_n3": _digest(ghost_row),
        }:
            raise ValueError(f"source row digest drifted: {channel_id}")
        physical_coordinates = {
            basis_id: (
                _rational(physical_row["assembled_rational_coordinate"])
                if basis_id == "rational_corner"
                else _rational(triangle_row["integrated_function_basis"][basis_id])
            )
            for basis_id in FUNCTION_BASIS
        }
        combined = {
            basis_id: sp.cancel(
                physical_coordinates[basis_id]
                + (
                    _rational(ghost_row["function_basis_coordinates"][basis_id])
                    if basis_id in FUNCTION_BASIS[:4]
                    else 0
                )
            )
            for basis_id in FUNCTION_BASIS
        }
        scale = _scale(physical_row["combined_scale_derivative"])
        if output_row["combined_coordinate_digests"] != {
            basis_id: _digest(sp.srepr(combined[basis_id]))
            for basis_id in FUNCTION_BASIS
        } or output_row["combined_scale_digest"] != _digest(sp.srepr(scale)):
            raise ValueError(f"combined row digest drifted: {channel_id}")
        for holdout in output_row["exact_holdouts"]:
            substitution = dict(zip(XS, holdout["point"]))
            expected = {
                basis_id: _q(combined[basis_id].subs(substitution))
                for basis_id in FUNCTION_BASIS
            }
            if holdout["coordinates"] != expected or holdout["scale_derivative"] != _q(scale.subs(substitution)):
                raise ValueError(f"combined holdout drifted: {channel_id}")
        expressions[channel_id] = combined
        scales[channel_id] = scale

    i28_ids = ("I28_123", "I28_132", "I28_231")
    if any(
        sp.cancel(sum(expressions[channel_id][basis_id] for channel_id in i28_ids)) != 0
        for basis_id in FUNCTION_BASIS
    ) or sp.cancel(sum(scales[channel_id] for channel_id in i28_ids)) != 0:
        raise ValueError("independent combined I28 relation failed")
    payload = {
        "channel_rows": value["channel_rows"],
        "I28_relation": value["I28_relation"],
    }
    if _digest(payload) != value["formula_digest"]:
        raise ValueError("formula digest drifted")
    print("GENERIC BACKGROUND PHYSICAL PLUS GHOST N3 FORM FACTORS CONSUMER: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
