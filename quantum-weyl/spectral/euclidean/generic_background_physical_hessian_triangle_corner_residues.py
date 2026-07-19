#!/usr/bin/env python3
"""Compute the generic-box logarithmic corner residues of the H1^3 triangle."""

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
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_CORNER_RESIDUES.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-triangle-corner-residues-v1.schema.json"
PROJECTION = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json"
OBSTRUCTION = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION.json"
VOLTERRA = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER.json"

T = sp.symbols("t")
X1, X2, X3 = sp.symbols("x1 x2 x3")
BOXES = (X1, X2, X3)
# (linear denominator at t=0, linear denominator at t=1)
CORNER_EDGES = ((X2, X1), (X2, X3), (X3, X1))
CORNER_IDS = ("alpha1_dominant", "alpha2_dominant", "alpha0_dominant")


def _q(value: Any) -> dict[str, int]:
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


def _leading_numerator(row: dict[str, Any], corner: int) -> sp.Poly:
    """Coefficient of epsilon^2 in a resolved dominant-alpha corner."""
    expression = 0
    for term in row["terms"]:
        a, b = term["alpha_exponents"]
        coefficient = _from_q(term["coefficient"]) * sp.prod(
            box**power for box, power in zip(BOXES, term["box_exponents"])
        )
        if corner == 0 and b <= 2:
            expression += (
                coefficient
                * sp.binomial(a, 2 - b)
                * (-1) ** (2 - b)
                * (1 - T) ** b
            )
        elif corner == 1 and a <= 2:
            expression += (
                coefficient
                * sp.binomial(b, 2 - a)
                * (-1) ** (2 - a)
                * (1 - T) ** a
            )
        elif corner == 2 and a + b == 2:
            expression += coefficient * T**a * (1 - T) ** b
    polynomial = sp.Poly(sp.expand(expression), T, domain=sp.QQ.frac_field(*BOXES))
    if polynomial.degree() > 2:
        raise ValueError("triangle corner angular degree exceeded two")
    return polynomial


def _angular_moments(left: sp.Symbol, right: sp.Symbol) -> tuple[sp.Expr, ...]:
    """Exact integrals of t^k/[left+(right-left)t]^4, k=0,1,2."""
    return (
        (left**2 + left * right + right**2) / (3 * left**3 * right**3),
        (2 * left + right) / (6 * left**2 * right**3),
        1 / (3 * left * right**3),
    )


def _integrated_corner(row: dict[str, Any], corner: int) -> sp.Expr:
    numerator = _leading_numerator(row, corner)
    moments = _angular_moments(*CORNER_EDGES[corner])
    return sp.cancel(
        sum(numerator.coeff_monomial(T**power) * moments[power] for power in range(3))
        / (X1 * X2 * X3)
    )


def _serialize(expression: sp.Expr) -> dict[str, Any]:
    numerator, denominator = map(sp.expand, sp.fraction(sp.cancel(expression)))
    denominator_poly = sp.Poly(denominator, *BOXES, domain=sp.QQ)
    if len(denominator_poly.terms()) != 1:
        raise ValueError("corner residue denominator is not monomial")
    denominator_exponents, denominator_coefficient = denominator_poly.terms()[0]
    numerator = sp.Poly(numerator / denominator_coefficient, *BOXES, domain=sp.QQ)
    return {
        "box_denominator_exponents": list(denominator_exponents),
        "numerator_terms": [
            {"box_exponents": list(exponents), "coefficient": _q(coefficient)}
            for exponents, coefficient in numerator.terms()
        ],
    }


def _evaluate(serialized: dict[str, Any], boxes: tuple[int, int, int]) -> sp.Rational:
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(value**power for value, power in zip(boxes, term["box_exponents"]))
        for term in serialized["numerator_terms"]
    )
    denominator = sp.prod(
        value**power
        for value, power in zip(boxes, serialized["box_denominator_exponents"])
    )
    return sp.Rational(numerator / denominator)


def build() -> dict[str, Any]:
    projection = json.loads(PROJECTION.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    volterra = json.loads(VOLTERRA.read_text())
    if (
        projection["claim_flags"]["PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"]
        is not True
        or obstruction["claim_flags"]["M14_RAISES_RELATIVE_QUOTIENT_RANK_BY_ONE"]
        is not True
        or volterra["claim_flags"]["COMMON_MELLIN_BOUNDARY_EXTENSION_DEFINED"]
        is not True
    ):
        raise ValueError("triangle corner-residue dependency is not active")

    obstruction_by_channel = {row["channel_id"]: row for row in obstruction["channel_rows"]}
    rows = []
    expressions: list[list[sp.Expr]] = []
    for source in projection["projection_rows"]:
        corners = [_integrated_corner(source, corner) for corner in range(3)]
        expressions.append(corners)
        serialized = [_serialize(value) for value in corners]
        one_order = sp.cancel(sum(corners))
        symmetric = sum(_evaluate(value, (1, 1, 1)) for value in serialized)
        expected = _from_q(
            obstruction_by_channel[source["channel_id"]]["log_corner_coefficient"]
        )
        if symmetric != expected:
            raise ValueError(f"symmetric obstruction regression failed: {source['channel_id']}")
        rows.append(
            {
                "channel_id": source["channel_id"],
                "carrier_id": source["carrier_id"],
                "label_order": source["label_order"],
                "corner_rows": [
                    {"corner_id": CORNER_IDS[index], **value}
                    for index, value in enumerate(serialized)
                ],
                "one_order_total": _serialize(one_order),
                "six_ordering_total": _serialize(6 * one_order),
                "symmetric_one_order_value": _q(symmetric),
            }
        )

    for corner in range(3):
        if sp.cancel(sum(expressions[index][corner] for index in range(7, 10))) != 0:
            raise ValueError("generic corner residues violate the I28 quotient relation")
    if sp.cancel(sum(sum(expressions[index]) for index in range(7, 10))) != 0:
        raise ValueError("generic total residues violate the I28 quotient relation")

    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-triangle-corner-residues-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_CORNER_RESIDUES",
        "result_state": "GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": projection["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "box_domain": "x1*x2*x3 nonzero",
            "carrier": "scalar-flat ten-dimensional five-carrier quotient",
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
        },
        "derivation": {
            "corner_density": "lim_epsilon epsilon^2*N(alpha,x)/(x1*x2*x3*Delta(alpha,x)^4)",
            "angular_degree_bound": 2,
            "angular_moments": [
                "(u^2+u*v+v^2)/(3*u^3*v^3)",
                "(2*u+v)/(6*u^2*v^3)",
                "1/(3*u*v^3)",
            ],
            "corner_edges": [["x2", "x1"], ["x2", "x3"], ["x3", "x1"]],
            "triangle_ordering_multiplicity": 6,
        },
        "channel_rows": rows,
        "regressions": {
            "channel_count": len(rows),
            "symmetric_obstruction_rows_matched": len(rows),
            "generic_I28_corner_relations": "ZERO",
            "generic_I28_total_relation": "ZERO",
        },
        "dependencies": {
            "projection": _reference(PROJECTION),
            "obstruction": _reference(OBSTRUCTION),
            "Volterra_carrier": _reference(VOLTERRA),
        },
        "claim_flags": {
            "GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_COMPUTED": True,
            "ALL_THREE_TRIANGLE_CORNERS_INTEGRATED": True,
            "ALL_ELEVEN_RAW_CHANNELS_COMPUTED": True,
            "SYMMETRIC_OBSTRUCTION_REPLAYED_CHANNELWISE": True,
            "GENERIC_I28_QUOTIENT_RELATION_PRESERVED": True,
            "FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED": False,
            "GENERIC_PHYSICAL_M14_DISPOSED": False,
            "FINITE_LOCAL_MIXED_ROWS_FIXED": False,
            "QME_OR_ANOMALY_STATUS_CHANGED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "ASSEMBLE_GENERIC_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_AND_DISPOSE_M14",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate integrates the three resolved logarithmic triangle corners for all eleven raw physical five-carrier channels as generic rational box functions and replays every symmetric obstruction coefficient. It does not yet combine them with contact residues, dispose M14, fix finite local rows, change the QME or anomaly result, or certify a Lorentzian theory.",
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
            raise SystemExit("stored generic triangle corner residues are stale")
        print("generic physical triangle corner residues: PASS")
        return 0
    OUTPUT.write_text(rendered)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
