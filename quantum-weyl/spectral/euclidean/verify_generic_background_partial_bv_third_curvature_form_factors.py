#!/usr/bin/env python3
"""Independent consumer for the generic partial-BV carrier representative."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PARTIAL_BV_THIRD_CURVATURE_FORM_FACTORS.json"
SCHEMA = HERE / "schema/generic-background-partial-bv-third-curvature-form-factors-v1.schema.json"
X1, X2, X3 = sp.symbols("x1 x2 x3")
XS = (X1, X2, X3)
BASIS = (
    "J_triangle", "log_x2_over_x1", "log_x3_over_x1", "rational_corner",
    "M14_singlet", "M15_standard_u", "M16_standard_v",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


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
    denominator = sp.prod(variable**power for variable, power in zip(XS, data["box_denominator_exponents"]))
    return sp.cancel(numerator / denominator)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    dependencies = {}
    for name, reference in value["dependencies"].items():
        path = ROOT / reference["path"]
        if _sha256(path) != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {name}")
        dependency = json.loads(path.read_text())
        if dependency["result_id"] != reference["result_id"]:
            raise ValueError(f"dependency result id drifted: {name}")
        dependencies[name] = dependency

    prior = dependencies["prior_partial_n3"]
    prior_rows = {row["channel_id"]: row for row in prior["channel_rows"]}
    physical_rows = {
        row["channel_id"]: row
        for carrier in dependencies["physical_form_factors"]["carrier_functions"]
        for row in carrier["orientation_channels"]
    }
    triangle_rows = {row["channel_id"]: row for row in dependencies["physical_triangle"]["channel_rows"]}
    ghost_rows = {row["channel_id"]: row for row in dependencies["ghost_pole3_functions"]["channel_rows"]}
    ghost_rows["I29_123"] = {
        "channel_id": "I29_123",
        "function_basis_coordinates": dependencies["ghost_I29_function"]["function_basis_coordinates"],
    }
    vector_rows = {row["channel_id"]: row for row in dependencies["ghost_vector_n1_n2_functions"]["channel_rows"]}

    expressions: dict[str, dict[str, sp.Expr]] = {}
    scales: dict[str, sp.Expr] = {}
    for output in value["channel_rows"]:
        channel = output["channel_id"]
        physical = physical_rows[channel]
        triangle = triangle_rows[channel]
        ghost = ghost_rows[channel]
        vector = vector_rows[channel]
        if output["source_row_digests"] != {
            "prior_partial_n3": _digest(prior_rows[channel]),
            "ghost_vector_n1_n2": _digest(vector),
        }:
            raise ValueError(f"source row digest drifted: {channel}")
        combined = {}
        for basis_id in BASIS:
            physical_coordinate = (
                _rational(physical["assembled_rational_coordinate"])
                if basis_id == "rational_corner"
                else _rational(triangle["integrated_function_basis"][basis_id])
            )
            ghost_coordinate = (
                _rational(ghost["function_basis_coordinates"][basis_id])
                if basis_id in BASIS[:4]
                else 0
            )
            vector_coordinate = (
                _rational(vector["function_basis_coordinates"][basis_id])
                if basis_id in BASIS[:4]
                else 0
            )
            combined[basis_id] = sp.cancel(physical_coordinate + ghost_coordinate + vector_coordinate)
        scale = _scale(physical["combined_scale_derivative"])
        if output["combined_coordinate_digests"] != {
            basis_id: _digest(sp.srepr(combined[basis_id])) for basis_id in BASIS
        } or output["combined_scale_digest"] != _digest(sp.srepr(scale)):
            raise ValueError(f"combined coordinate digest drifted: {channel}")
        for holdout in output["exact_holdouts"]:
            substitution = dict(zip(XS, holdout["point"]))
            if holdout["coordinates"] != {
                basis_id: _q(combined[basis_id].subs(substitution)) for basis_id in BASIS
            } or holdout["scale_derivative"] != _q(scale.subs(substitution)):
                raise ValueError(f"exact holdout drifted: {channel}")
        expressions[channel] = combined
        scales[channel] = scale

    i28 = ("I28_123", "I28_132", "I28_231")
    if any(
        sp.cancel(sum(expressions[channel][basis_id] for channel in i28)) != 0
        for basis_id in BASIS
    ) or sp.cancel(sum(scales[channel] for channel in i28)) != 0:
        raise ValueError("independent partial BV I28 relation failed")
    payload = {"channel_rows": value["channel_rows"], "I28_relation": value["I28_relation"]}
    if _digest(payload) != value["formula_digest"]:
        raise ValueError("formula digest drifted")
    print("GENERIC BACKGROUND PARTIAL BV THIRD-CURVATURE FORM FACTORS CONSUMER: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
