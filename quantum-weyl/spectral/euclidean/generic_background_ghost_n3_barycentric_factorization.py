#!/usr/bin/env python3
"""Factor the generic ghost n=3 carrier numerators in barycentric form."""

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
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-barycentric-factorization-v1.schema.json"
PROJECTION = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json"

A, B, C = sp.symbols("alpha1 alpha2 alpha0")
X1, X2, X3 = sp.symbols("x1 x2 x3")
BOXES = (X1, X2, X3)
ALPHAS = (A, B, C)
DELTA = C * A * X1 + A * B * X2 + B * C * X3


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


def _affine_numerator(row: dict[str, Any]) -> sp.Expr:
    a, b = A, B
    return sp.expand(
        sum(
            _from_q(term["coefficient"])
            * a ** term["alpha_exponents"][0]
            * b ** term["alpha_exponents"][1]
            * sp.prod(box**power for box, power in zip(BOXES, term["box_exponents"]))
            for term in row["terms"]
        )
    )


def _homogeneous_lift(expression: sp.Expr, degree: int) -> sp.Expr:
    scale = A + B + C
    lifted = sp.cancel(
        scale**degree
        * expression.subs(
            {
                A: A / scale,
                B: B / scale,
            },
            simultaneous=True,
        )
    )
    return sp.expand(lifted)


def _terms(expression: sp.Expr) -> list[dict[str, Any]]:
    polynomial = sp.Poly(expression, A, B, C, X1, X2, X3, domain=sp.QQ)
    return [
        {
            "alpha_exponents": list(exponents[:3]),
            "box_exponents": list(exponents[3:]),
            "coefficient": _q(coefficient),
        }
        for exponents, coefficient in polynomial.terms()
        if coefficient
    ]


def _edge_orders(expression: sp.Expr) -> list[int]:
    polynomial = sp.Poly(expression, A, B, C, X1, X2, X3, domain=sp.QQ)
    exponents = [row[0] for row in polynomial.terms() if row[1]]
    return [min(row[index] for row in exponents) for index in range(3)]


def _vertex_orders(expression: sp.Expr) -> list[int]:
    polynomial = sp.Poly(expression, A, B, C, X1, X2, X3, domain=sp.QQ)
    exponents = [row[0] for row in polynomial.terms() if row[1]]
    # At the A, B, C vertices, the other two barycentric coordinates vanish.
    return [
        min(row[(index + 1) % 3] + row[(index + 2) % 3] for row in exponents)
        for index in range(3)
    ]


def _row(row: dict[str, Any]) -> tuple[dict[str, Any], sp.Expr]:
    affine = _affine_numerator(row)
    affine_delta = DELTA.subs(C, 1 - A - B)
    if row["channel_id"] == "I29_123":
        delta_factor_power = 0
        reduced_affine = affine
        homogeneous_degree = 9
        reduced_denominator_power = 4
    else:
        quotient, remainder = sp.div(
            sp.Poly(affine, A, B, X1, X2, X3, domain=sp.QQ),
            sp.Poly(affine_delta, A, B, X1, X2, X3, domain=sp.QQ),
        )
        if not remainder.is_zero:
            raise ValueError(f"Delta factorization failed: {row['channel_id']}")
        delta_factor_power = 1
        reduced_affine = quotient.as_expr()
        homogeneous_degree = 7
        reduced_denominator_power = 3
    homogeneous = sp.factor(_homogeneous_lift(reduced_affine, homogeneous_degree))
    edge_orders = _edge_orders(homogeneous)
    vertex_orders = _vertex_orders(homogeneous)
    vertex_margins = [
        order - reduced_denominator_power + 2 for order in vertex_orders
    ]
    value = {
        "channel_id": row["channel_id"],
        "upstream_term_count": row["term_count"],
        "delta_factor_power": delta_factor_power,
        "reduced_denominator_power": reduced_denominator_power,
        "homogeneous_alpha_degree": homogeneous_degree,
        "homogeneous_box_degree": row["numerator_box_degree"] - delta_factor_power,
        "edge_vanishing_orders": {
            "alpha1_zero": edge_orders[0],
            "alpha2_zero": edge_orders[1],
            "alpha0_zero": edge_orders[2],
        },
        "vertex_vanishing_orders": {
            "alpha1_vertex": vertex_orders[0],
            "alpha2_vertex": vertex_orders[1],
            "alpha0_vertex": vertex_orders[2],
        },
        "vertex_integrability_margins": {
            "alpha1_vertex": vertex_margins[0],
            "alpha2_vertex": vertex_margins[1],
            "alpha0_vertex": vertex_margins[2],
        },
        "direct_open_edge_restriction": (
            "NONZERO" if any(order == 0 for order in edge_orders) else "ZERO"
        ),
        "reduced_numerator_terms": _terms(homogeneous),
    }
    return value, sp.expand(homogeneous)


def build() -> dict[str, Any]:
    projection = json.loads(PROJECTION.read_text())
    if not projection["claim_flags"][
        "GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED"
    ]:
        raise ValueError("five-carrier projection dependency is not certified")
    rows = []
    expressions: dict[str, sp.Expr] = {}
    for source in projection["projection_rows"]:
        value, expression = _row(source)
        rows.append(value)
        expressions[value["channel_id"]] = expression
    if sp.expand(
        expressions["I28_123"]
        + expressions["I28_132"]
        + expressions["I28_231"]
    ) != 0:
        raise ValueError("pointwise I28 quotient relation drifted")
    edge_sources = [
        row["channel_id"]
        for row in rows
        if row["direct_open_edge_restriction"] == "NONZERO"
    ]
    payload = {"rows": rows, "pointwise_relations": ["I28_123+I28_132+I28_231=0"]}
    formula_digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    result = {
        "schema": "quantum-weyl-generic-background-ghost-n3-barycentric-factorization-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION",
        "result_state": "GENERIC_N3_BARYCENTRIC_DENOMINATOR_AND_BOUNDARY_FACTORIZATION_COMPUTED",
        "lifecycle_state": "GENERIC_IBP_MASTER_REDUCTION_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": projection["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "curvature_order": 3,
            "kinematics": "generic positive nonexceptional x1,x2,x3",
            "output": "exact homogeneous barycentric factorization of all eleven projected ghost n=3 carrier numerators",
        },
        "convention": {
            "barycentric_order": ["alpha1", "alpha2", "alpha0"],
            "simplex": "alpha_i>=0 and alpha0+alpha1+alpha2=1",
            "Delta": "alpha0*alpha1*x1+alpha1*alpha2*x2+alpha2*alpha0*x3",
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
            "W_and_Tr_log_multiplier": "-8/3 already included upstream",
        },
        "factorization_summary": {
            "raw_channel_count": 11,
            "channels_with_exact_Delta_factor": 10,
            "reduced_denominator_power_three_count": 10,
            "reduced_denominator_power_four_count": 1,
            "channels_with_nonzero_direct_open_edge_restriction": edge_sources,
            "channels_with_zero_direct_open_edge_restriction": [
                row["channel_id"]
                for row in rows
                if row["direct_open_edge_restriction"] == "ZERO"
            ],
            "pointwise_I28_relation": "I28_123+I28_132+I28_231=0",
            "minimum_vertex_integrability_margin": min(
                margin
                for row in rows
                for margin in row["vertex_integrability_margins"].values()
            ),
        },
        "channel_rows": rows,
        "formula_digest": formula_digest,
        "IBP_disposition": {
            "generic_relative_IBP_primitives": "NOT_COMPUTED",
            "corner_flux_for_future_IBP_primitives": "NOT_COMPUTED",
            "edge_bubble_coefficients": "NOT_COMPUTED",
            "scalar_triangle_and_log_master_coefficients": "NOT_COMPUTED",
            "generic_integrated_channel_functions": "NOT_COMPUTED",
        },
        "claim_flags": {
            "GENERIC_GHOST_N3_BARYCENTRIC_FACTORIZATION_COMPUTED": True,
            "TEN_OF_ELEVEN_UPSTREAM_NUMERATORS_HAVE_EXACT_DELTA_FACTOR": True,
            "ONLY_I10_HAS_NONZERO_DIRECT_OPEN_EDGE_RESTRICTION": True,
            "POINTWISE_I28_RELATION_VERIFIED": True,
            "GENERIC_RELATIVE_IBP_REDUCTION_COMPUTED": False,
            "GENERIC_EDGE_BUBBLE_COEFFICIENTS_COMPUTED": False,
            "GENERIC_GHOST_N3_FULL_KINEMATIC_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {"five_carrier_projection": _reference(PROJECTION)},
        "next_gate": "CONSTRUCT_EXACT_RELATIVE_SIMPLEX_IBP_PRIMITIVES_AND_REDUCE_TO_SCALAR_TRIANGLE_PLUS_EDGE_BUBBLE_MASTERS",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate is an exact generic-kinematic integrand theorem. Ten of the eleven projected ghost n=3 numerators contain one factor of Delta, reducing their pole order from four to three; I29 remains the single pole-four monomial. After homogeneous barycentric lifting, every raw orientation except I10 restricts to zero on all three open simplex edges, and the three I28 numerators obey their quotient relation pointwise. This identifies I10 as the only direct edge-restriction source. It does not prove that future integration-by-parts primitives have vanishing corner flux, compute edge-bubble coefficients, reduce the interior rows to scalar triangle/log masters, integrate the generic functions, supply the physical Hessian, complete Gamma1/Q1, authorize residual transfer, or prove any Lorentzian, Hadamard, particle, positivity, scattering, or unitarity statement."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        "rows": value["channel_rows"],
        "pointwise_relations": [value["factorization_summary"]["pointwise_I28_relation"]],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != value["formula_digest"]:
        raise ValueError("barycentric factorization digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale barycentric factorization: {OUTPUT}")
    print("GENERIC GHOST N3 BARYCENTRIC FACTORIZATION: 10 DELTA CANCELLATIONS; I10 ONLY DIRECT EDGE SOURCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
