#!/usr/bin/env python3
"""Independent replay of the generic ghost n=3 barycentric factorization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-barycentric-factorization-v1.schema.json"
PROJECTION = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json"

A, B, C = sp.symbols("alpha1 alpha2 alpha0")
X1, X2, X3 = sp.symbols("x1 x2 x3")
VARIABLES = (A, B, C, X1, X2, X3)
DELTA = C * A * X1 + A * B * X2 + B * C * X3


def _q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stored_polynomial(terms: list[dict[str, Any]]) -> sp.Expr:
    return sp.expand(
        sum(
            _q(term["coefficient"])
            * sp.prod(
                variable**power
                for variable, power in zip(
                    VARIABLES,
                    term["alpha_exponents"] + term["box_exponents"],
                )
            )
            for term in terms
        )
    )


def _upstream_affine(row: dict[str, Any]) -> sp.Expr:
    return sp.expand(
        sum(
            _q(term["coefficient"])
            * A ** term["alpha_exponents"][0]
            * B ** term["alpha_exponents"][1]
            * X1 ** term["box_exponents"][0]
            * X2 ** term["box_exponents"][1]
            * X3 ** term["box_exponents"][2]
            for term in row["terms"]
        )
    )


def _orders(polynomial: sp.Expr) -> tuple[list[int], list[int]]:
    rows = [
        exponents
        for exponents, coefficient in sp.Poly(polynomial, *VARIABLES, domain=sp.QQ).terms()
        if coefficient
    ]
    edges = [min(row[index] for row in rows) for index in range(3)]
    vertices = [
        min(row[(index + 1) % 3] + row[(index + 2) % 3] for row in rows)
        for index in range(3)
    ]
    return edges, vertices


def verify() -> None:
    stored = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(stored)
    dependency = stored["dependencies"]["five_carrier_projection"]
    if dependency["sha256"] != _sha256(PROJECTION):
        raise ValueError("five-carrier projection dependency hash drifted")
    projection = json.loads(PROJECTION.read_text())
    if dependency["result_id"] != projection["result_id"]:
        raise ValueError("five-carrier projection dependency identity drifted")
    source_rows = {row["channel_id"]: row for row in projection["projection_rows"]}
    reduced: dict[str, sp.Expr] = {}
    for row in stored["channel_rows"]:
        channel = row["channel_id"]
        source = source_rows[channel]
        polynomial = _stored_polynomial(row["reduced_numerator_terms"])
        reduced[channel] = polynomial
        if sp.Poly(polynomial, A, B, C).total_degree() != row["homogeneous_alpha_degree"]:
            raise ValueError(f"homogeneous alpha degree drifted: {channel}")
        if sp.Poly(polynomial, X1, X2, X3).total_degree() != row["homogeneous_box_degree"]:
            raise ValueError(f"homogeneous box degree drifted: {channel}")
        affine_reduced = sp.expand(polynomial.subs(C, 1 - A - B))
        reconstructed = sp.expand(
            DELTA.subs(C, 1 - A - B) ** row["delta_factor_power"]
            * affine_reduced
        )
        if sp.expand(reconstructed - _upstream_affine(source)) != 0:
            raise ValueError(f"upstream numerator reconstruction failed: {channel}")
        edges, vertices = _orders(polynomial)
        stored_edges = row["edge_vanishing_orders"]
        stored_vertices = row["vertex_vanishing_orders"]
        if edges != [
            stored_edges["alpha1_zero"],
            stored_edges["alpha2_zero"],
            stored_edges["alpha0_zero"],
        ]:
            raise ValueError(f"edge order drifted: {channel}")
        if vertices != [
            stored_vertices["alpha1_vertex"],
            stored_vertices["alpha2_vertex"],
            stored_vertices["alpha0_vertex"],
        ]:
            raise ValueError(f"vertex order drifted: {channel}")
        margins = [order - row["reduced_denominator_power"] + 2 for order in vertices]
        stored_margins = row["vertex_integrability_margins"]
        if margins != [
            stored_margins["alpha1_vertex"],
            stored_margins["alpha2_vertex"],
            stored_margins["alpha0_vertex"],
        ] or min(margins) <= 0:
            raise ValueError(f"vertex integrability margin drifted: {channel}")
        expected_edge_status = "NONZERO" if any(order == 0 for order in edges) else "ZERO"
        if row["direct_open_edge_restriction"] != expected_edge_status:
            raise ValueError(f"direct edge disposition drifted: {channel}")

    if sp.expand(reduced["I28_123"] + reduced["I28_132"] + reduced["I28_231"]) != 0:
        raise ValueError("pointwise I28 relation failed")
    summary = stored["factorization_summary"]
    if [
        row["channel_id"]
        for row in stored["channel_rows"]
        if row["direct_open_edge_restriction"] == "NONZERO"
    ] != ["I10_123"]:
        raise ValueError("unique direct edge source drifted")
    if sum(row["delta_factor_power"] for row in stored["channel_rows"]) != 10:
        raise ValueError("Delta cancellation count drifted")
    if summary["minimum_vertex_integrability_margin"] != min(
        value
        for row in stored["channel_rows"]
        for value in row["vertex_integrability_margins"].values()
    ):
        raise ValueError("minimum integrability margin drifted")
    payload = {
        "rows": stored["channel_rows"],
        "pointwise_relations": [summary["pointwise_I28_relation"]],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != stored["formula_digest"]:
        raise ValueError("formula digest drifted")
    flags = stored["claim_flags"]
    if not flags["GENERIC_GHOST_N3_BARYCENTRIC_FACTORIZATION_COMPUTED"]:
        raise ValueError("positive factorization flag missing")
    forbidden = [
        "GENERIC_RELATIVE_IBP_REDUCTION_COMPUTED",
        "GENERIC_EDGE_BUBBLE_COEFFICIENTS_COMPUTED",
        "GENERIC_GHOST_N3_FULL_KINEMATIC_FUNCTIONS_COMPUTED",
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
        "LORENTZIAN_CERTIFIED",
    ]
    if any(flags[name] for name in forbidden):
        raise ValueError("factorization certificate crossed its claim boundary")


def main() -> int:
    verify()
    print("independent generic ghost n=3 barycentric factorization: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
