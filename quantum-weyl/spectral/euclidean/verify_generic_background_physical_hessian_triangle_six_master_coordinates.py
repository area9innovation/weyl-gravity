#!/usr/bin/env python3
"""Independently verify the physical triangle six-master coordinates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_ghost_n3_pole3_relative_ibp import (
    X1,
    X2,
    X3,
    _domain_matrix,
)
from .generic_background_physical_hessian_triangle_master_completeness import (
    PIVOT_FIXTURE,
    PROJECTION,
    _system,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_SIX_MASTER_COORDINATES.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-triangle-six-master-coordinates-v1.schema.json"
XS = (X1, X2, X3)
MASTER_IDS = ("J_triangle", "M_x1", "M_x2", "M14_singlet", "M15_standard_u", "M16_standard_v")
MASTER_DEGREES = (3, 2, 2, 0, 0, 0)
LAMBDA = sp.expand(
    X1**2 + X2**2 + X3**2 - 2 * X1 * X2 - 2 * X1 * X3 - 2 * X2 * X3
)
CHART_FACTOR = sp.expand(2 * X1 * X2 + X2**2 - 2 * X2 * X3 + X3**2)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _from_terms(terms: list[dict]) -> sp.Expr:
    return sp.expand(
        sum(
            sp.Rational(term["coefficient"]["numerator"], term["coefficient"]["denominator"])
            * X1 ** term["exponents"][0]
            * X2 ** term["exponents"][1]
            * X3 ** term["exponents"][2]
            for term in terms
        )
    )


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        key: value[key]
        for key in ("selected_minor", "pivot_rows", "channel_rows", "solve_ledger")
    }
    if _digest(payload) != value["formula_digest"]:
        raise ValueError("six-master coordinate formula digest mismatch")
    for reference in value["dependencies"].values():
        path = ROOT / reference["path"]
        source = json.loads(path.read_text())
        if _sha256(path) != reference["sha256"] or source["result_id"] != reference["result_id"]:
            raise ValueError(f"dependency mismatch: {path}")

    projection = json.loads(PROJECTION.read_text())
    system = _system(projection)
    selected = system["selected_matrix"]
    targets = _domain_matrix(system["targets"], system["basis"], selected.domain)
    pivot_rows = tuple(selected.to_Matrix().subs(PIVOT_FIXTURE).transpose().rref()[1])
    if list(pivot_rows) != value["pivot_rows"]:
        raise ValueError("pivot-row reconstruction mismatch")

    ring = sp.ZZ.poly_ring(*XS)
    determinant = selected.extract(pivot_rows, range(52)).convert_to(ring).det()
    expected_determinant = ring.from_sympy(
        132239526912
        * X1**14
        * X2**13
        * X3**10
        * CHART_FACTOR**3
        * LAMBDA**5
    )
    if determinant != expected_determinant:
        raise ValueError("selected-minor factorization mismatch")

    expected_channels = [row["channel_id"] for row in projection["projection_rows"]]
    rows = value["channel_rows"]
    if [row["channel_id"] for row in rows] != expected_channels:
        raise ValueError("physical channel order drifted")
    expressions: list[list[sp.Expr]] = []
    determinant_poly = sp.Poly(expected_determinant.as_expr(), *XS, domain=sp.QQ)
    for channel_row, projection_row in zip(rows, projection["projection_rows"]):
        master_rows = channel_row["master_coordinates"]
        if [row["master_id"] for row in master_rows] != list(MASTER_IDS):
            raise ValueError(f"master order drifted: {channel_row['channel_id']}")
        channel_expressions = []
        for master_row, master_degree in zip(master_rows, MASTER_DEGREES):
            numerator = _from_terms(master_row["coordinate"]["numerator_terms"])
            denominator = _from_terms(master_row["coordinate"]["denominator_terms"])
            numerator_poly = sp.Poly(numerator, *XS, domain=sp.QQ)
            denominator_poly = sp.Poly(denominator, *XS, domain=sp.QQ)
            weight = numerator_poly.total_degree() - denominator_poly.total_degree()
            expected_weight = projection_row["numerator_box_degree"] - master_degree
            if weight != expected_weight or master_row["homogeneity_weight"] != expected_weight:
                raise ValueError(
                    f"coordinate homogeneity mismatch: {channel_row['channel_id']} {master_row['master_id']}"
                )
            if sp.rem(determinant_poly, denominator_poly) != 0:
                raise ValueError(
                    f"coordinate denominator escapes selected minor: {channel_row['channel_id']} {master_row['master_id']}"
                )
            channel_expressions.append(sp.cancel(numerator / denominator))
        expressions.append(channel_expressions)

    square = selected.extract(pivot_rows, range(52)).to_Matrix()
    right_hand_sides = targets.extract(pivot_rows, range(11)).to_Matrix()
    for point in value["solve_ledger"]["holdout_points"]:
        substitution = dict(zip(XS, map(sp.Rational, point)))
        actual = square.subs(substitution).inv() * right_hand_sides.subs(substitution)
        for channel_index in range(11):
            for master_index in range(6):
                expected = expressions[channel_index][master_index].subs(substitution)
                if actual[46 + master_index, channel_index] != expected:
                    raise ValueError(
                        f"exact holdout mismatch: {point} {expected_channels[channel_index]} {MASTER_IDS[master_index]}"
                    )

    flags = value["claim_flags"]
    if not (
        flags["PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED"]
        and flags["ALL_ELEVEN_CHANNELS_COORDINATED"]
        and flags["SELECTED_MINOR_LAMBDA5_FACTOR_CERTIFIED"]
    ):
        raise ValueError("coordinate claim flags are not closed")
    if (
        flags["PHYSICAL_N3_TRIANGLE_BOUNDARY_FLUX_COMPUTED"]
        or flags["PHYSICAL_N3_TRIANGLE_INTEGRATED"]
        or flags["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"]
        or flags["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"]
        or flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"]
        or flags["QME_RESTORED"]
        or flags["RESIDUAL_TRANSFER_AUTHORIZED"]
        or flags["LORENTZIAN_CERTIFIED"]
    ):
        raise ValueError("a downstream claim was promoted")


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("generic physical triangle six-master coordinates: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
