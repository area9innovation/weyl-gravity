#!/usr/bin/env python3
"""Independent replay of the generic pole-three relative-simplex IBP theorem."""

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
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_RELATIVE_IBP.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-pole3-relative-ibp-v1.schema.json"
BARYCENTRIC = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION.json"

A, B = sp.symbols("alpha1 alpha2")
C = 1 - A - B
H1, H2, H0 = sp.symbols("alpha1_h alpha2_h alpha0_h")
X1, X2, X3 = sp.symbols("x1 x2 x3")
XS = (X1, X2, X3)
HS = (H1, H2, H0)
DELTA = A * C * X1 + A * B * X2 + B * C * X3
DELTA_H = H1 * H0 * X1 + H1 * H2 * X2 + H2 * H0 * X3
MASTERS = (DELTA**2, A * C * DELTA, A * B * DELTA)
MASTERS_H = (DELTA_H**2, H1 * H0 * DELTA_H, H1 * H2 * DELTA_H)
MASTER_IDS = ("J_triangle", "M_x1", "M_x2")
PIVOT_FIXTURE = {X1: sp.Rational(2), X2: sp.Rational(3), X3: sp.Rational(5)}
EXACT_FIXTURES = (
    PIVOT_FIXTURE,
    {X1: sp.Rational(3), X2: sp.Rational(5), X3: sp.Rational(7)},
)
REPRESENTATIVES = ("I10_123", "I24_123", "I25_123", "I28_123")


def _q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _poly_from_terms(
    terms: list[dict[str, Any]], variables: tuple[sp.Symbol, ...]
) -> sp.Expr:
    return sp.expand(
        sum(
            _q(term["coefficient"])
            * sp.prod(
                variable**power
                for variable, power in zip(variables, term["exponents"])
            )
            for term in terms
        )
    )


def _rf(value: dict[str, Any]) -> sp.Expr:
    numerator = _poly_from_terms(value["numerator_terms"], XS)
    denominator = _poly_from_terms(value["denominator_terms"], XS)
    return sp.cancel(numerator / denominator)


def _monomials(degree: int) -> list[sp.Expr]:
    return [
        A**i * B**j
        for i in range(degree + 1)
        for j in range(degree + 1 - i)
    ]


def _target_affine(row: dict[str, Any]) -> sp.Expr:
    return sp.expand(
        sum(
            _q(term["coefficient"])
            * A ** term["alpha_exponents"][0]
            * B ** term["alpha_exponents"][1]
            * C ** term["alpha_exponents"][2]
            * X1 ** term["box_exponents"][0]
            * X2 ** term["box_exponents"][1]
            * X3 ** term["box_exponents"][2]
            for term in row["reduced_numerator_terms"]
        )
    )


def _target_homogeneous(row: dict[str, Any]) -> sp.Expr:
    return sp.expand(
        sum(
            _q(term["coefficient"])
            * H1 ** term["alpha_exponents"][0]
            * H2 ** term["alpha_exponents"][1]
            * H0 ** term["alpha_exponents"][2]
            * X1 ** term["box_exponents"][0]
            * X2 ** term["box_exponents"][1]
            * X3 ** term["box_exponents"][2]
            for term in row["reduced_numerator_terms"]
        )
    )


def _coefficient_vector(expression: sp.Expr, basis: list[sp.Expr]) -> list[sp.Expr]:
    polynomial = sp.Poly(sp.expand(expression), A, B)
    return [polynomial.coeff_monomial(monomial) for monomial in basis]


def _domain_matrix(expressions: list[sp.Expr], basis: list[sp.Expr]) -> Any:
    rows = list(
        map(
            list,
            zip(*[_coefficient_vector(expression, basis) for expression in expressions]),
        )
    )
    return sp.polys.matrices.DomainMatrix.from_list_sympy(
        len(basis), len(expressions), rows
    ).to_field()


def _tangent_columns() -> list[sp.Expr]:
    columns = []
    for group in ("U", "V", "W"):
        for monomial in _monomials(4):
            U = monomial if group == "U" else 0
            V = monomial if group == "V" else 0
            W = monomial if group == "W" else 0
            P = sp.expand(A * (C * U + B * W))
            Q = sp.expand(B * (C * V - A * W))
            columns.append(
                sp.expand(
                    DELTA * (sp.diff(P, A) + sp.diff(Q, B))
                    - 2 * (P * sp.diff(DELTA, A) + Q * sp.diff(DELTA, B))
                )
            )
    return columns


def _corner_zero_columns(fixture: dict[sp.Symbol, sp.Rational] | None = None) -> list[sp.Expr]:
    monomials = _monomials(4)
    delta = DELTA if fixture is None else DELTA.subs(fixture)

    def kernel(points: tuple[tuple[int, int], tuple[int, int]]) -> list[sp.Expr]:
        evaluation = sp.Matrix(
            [
                [monomial.subs({A: a, B: b}) for monomial in monomials]
                for a, b in points
            ]
        )
        return [
            sp.expand(
                sum(vector[index] * monomials[index] for index in range(len(monomials)))
            )
            for vector in evaluation.nullspace()
        ]

    columns = []
    for group, basis in (
        ("U", kernel(((1, 0), (0, 0)))),
        ("V", kernel(((0, 1), (0, 0)))),
        ("W", kernel(((1, 0), (0, 1)))),
    ):
        for polynomial in basis:
            U = polynomial if group == "U" else 0
            V = polynomial if group == "V" else 0
            W = polynomial if group == "W" else 0
            P = sp.expand(A * (C * U + B * W))
            Q = sp.expand(B * (C * V - A * W))
            columns.append(
                sp.expand(
                    delta * (sp.diff(P, A) + sp.diff(Q, B))
                    - 2 * (P * sp.diff(delta, A) + Q * sp.diff(delta, B))
                )
            )
    return columns


def _primitive_polynomials(
    primitive: dict[str, Any],
    fixture: dict[sp.Symbol, sp.Rational] | None = None,
) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    values = {"U": sp.S.Zero, "V": sp.S.Zero, "W": sp.S.Zero}
    for row in primitive["coefficients"]:
        i, j = row["monomial_exponents"]
        coefficient = _rf(row["coefficient"])
        if fixture is not None:
            coefficient = coefficient.subs(fixture)
        values[row["group"]] += coefficient * A**i * B**j
    if primitive["coefficient_count"] != len(primitive["coefficients"]):
        raise ValueError("primitive coefficient count drifted")
    return tuple(sp.cancel(values[name]) for name in ("U", "V", "W"))


def _homogeneous_master(
    row: dict[str, Any],
    fixture: dict[sp.Symbol, sp.Rational] | None = None,
) -> sp.Expr:
    return sp.expand(
        sum(
            (
                _rf(row["master_coordinates"][master_id])
                if fixture is None
                else _rf(row["master_coordinates"][master_id]).subs(fixture)
            )
            * (master if fixture is None else master.subs(fixture))
            for master_id, master in zip(MASTER_IDS, MASTERS_H)
        )
    )


def _permuted(
    expression: sp.Expr,
    alpha_permutation: list[int],
    x_permutation: list[int],
) -> sp.Expr:
    substitutions = {
        HS[index]: HS[alpha_permutation[index]] for index in range(3)
    }
    substitutions.update(
        {XS[index]: XS[x_permutation[index]] for index in range(3)}
    )
    return sp.expand(expression.xreplace(substitutions))


def _verify_representative(
    channel_id: str,
    row: dict[str, Any],
    target: sp.Expr,
    primitive: dict[str, Any],
    fixture: dict[sp.Symbol, sp.Rational] | None = None,
) -> None:
    U, V, W = _primitive_polynomials(primitive, fixture)
    delta = DELTA if fixture is None else DELTA.subs(fixture)
    target = target if fixture is None else target.subs(fixture)
    P = sp.expand(A * (C * U + B * W))
    Q = sp.expand(B * (C * V - A * W))
    if P.subs(A, 0) != 0 or Q.subs(B, 0) != 0:
        raise ValueError(f"coordinate-edge flux drifted: {channel_id}")
    if sp.expand((P + Q).subs(B, 1 - A)) != 0:
        raise ValueError(f"diagonal-edge flux drifted: {channel_id}")
    master = sum(
        (
            _rf(row["master_coordinates"][master_id])
            if fixture is None
            else _rf(row["master_coordinates"][master_id]).subs(fixture)
        )
        * (polynomial if fixture is None else polynomial.subs(fixture))
        for master_id, polynomial in zip(MASTER_IDS, MASTERS)
    )
    right = (
        delta * (sp.diff(P, A) + sp.diff(Q, B))
        - 2 * (P * sp.diff(delta, A) + Q * sp.diff(delta, B))
        + master
    )
    if sp.cancel(target - right) != 0:
        raise ValueError(f"explicit primitive identity failed: {channel_id}")
    expected_pairs = {
        "alpha1_vertex": (U.subs({A: 1, B: 0}), W.subs({A: 1, B: 0})),
        "alpha2_vertex": (V.subs({A: 0, B: 1}), W.subs({A: 0, B: 1})),
        "alpha0_vertex": (U.subs({A: 0, B: 0}), V.subs({A: 0, B: 0})),
    }
    for corner in primitive["corner_leading_rows"]:
        pair = tuple(
            _rf(value) if fixture is None else _rf(value).subs(fixture)
            for value in corner["leading_pair"]
        )
        expected = tuple(sp.cancel(value) for value in expected_pairs[corner["corner_id"]])
        if any(sp.cancel(left - right) != 0 for left, right in zip(pair, expected)):
            raise ValueError(f"corner-leading pair drifted: {channel_id}")
        if corner["leading_pair_zero"] != all(value == 0 for value in expected):
            raise ValueError(f"corner-zero flag drifted: {channel_id}")


def _verify_dual_witnesses(
    stored: dict[str, Any],
    source_rows: dict[str, dict[str, Any]],
) -> None:
    basis = _monomials(7)
    corner_expressions = _corner_zero_columns(PIVOT_FIXTURE) + [
        master.subs(PIVOT_FIXTURE) for master in MASTERS
    ]
    corner = sp.Matrix(
        list(
            map(
                list,
                zip(
                    *[
                        [sp.Poly(expression, A, B).coeff_monomial(m) for m in basis]
                        for expression in corner_expressions
                    ]
                ),
            )
        )
    )
    if corner.rank() != 26:
        raise ValueError("corner-zero fixture rank drifted")
    for channel_id, witness in stored["corner_zero_dual_witnesses"].items():
        vector = sp.zeros(1, len(basis))
        for coefficient in witness["coefficients"]:
            vector[0, coefficient["monomial_index"]] = _q(coefficient["coefficient"])
        if witness["coefficient_count"] != len(witness["coefficients"]):
            raise ValueError(f"dual coefficient count drifted: {channel_id}")
        if vector * corner != sp.zeros(1, corner.cols):
            raise ValueError(f"dual does not annihilate corner span: {channel_id}")
        target = sp.Matrix(
            _coefficient_vector(_target_affine(source_rows[channel_id]), basis)
        ).subs(PIVOT_FIXTURE)
        if (vector * target)[0] != 1:
            raise ValueError(f"dual target normalization drifted: {channel_id}")


def verify(*, exhaustive: bool = False) -> None:
    stored = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(stored)
    dependency = stored["dependencies"]["barycentric_factorization"]
    source = json.loads(BARYCENTRIC.read_text())
    if dependency["sha256"] != _sha256(BARYCENTRIC):
        raise ValueError("barycentric dependency hash drifted")
    if dependency["result_id"] != source["result_id"]:
        raise ValueError("barycentric dependency identity drifted")
    source_rows = {
        row["channel_id"]: row
        for row in source["channel_rows"]
        if row["reduced_denominator_power"] == 3
    }
    rows = {row["channel_id"]: row for row in stored["channel_rows"]}
    if set(rows) != set(source_rows):
        raise ValueError("pole-three inventory drifted")

    for representative_id in REPRESENTATIVES:
        fixtures = (None,) if exhaustive else EXACT_FIXTURES
        for fixture in fixtures:
            _verify_representative(
                representative_id,
                rows[representative_id],
                _target_affine(source_rows[representative_id]),
                stored["representative_primitives"][representative_id],
                fixture,
            )

    for channel_id, row in rows.items():
        representative_id = row["representative_id"]
        alpha_permutation = row["alpha_permutation"]
        x_permutation = row["x_permutation"]
        if exhaustive:
            transformed_target = _permuted(
                _target_homogeneous(source_rows[representative_id]),
                alpha_permutation,
                x_permutation,
            )
            if sp.expand(transformed_target - _target_homogeneous(source_rows[channel_id])) != 0:
                raise ValueError(f"target orbit map failed: {channel_id}")
            transformed_master = _permuted(
                _homogeneous_master(rows[representative_id]),
                alpha_permutation,
                x_permutation,
            )
            if sp.cancel(transformed_master - _homogeneous_master(row)) != 0:
                raise ValueError(f"master orbit map failed: {channel_id}")
        else:
            for fixture in EXACT_FIXTURES:
                permuted_fixture = {
                    XS[index]: fixture[XS[x_permutation[index]]]
                    for index in range(3)
                }
                alpha_map = {
                    HS[index]: HS[alpha_permutation[index]] for index in range(3)
                }
                transformed_target = _target_homogeneous(
                    source_rows[representative_id]
                ).subs(permuted_fixture).xreplace(alpha_map)
                expected_target = _target_homogeneous(source_rows[channel_id]).subs(fixture)
                if sp.expand(transformed_target - expected_target) != 0:
                    raise ValueError(f"target orbit fixture failed: {channel_id}")
                transformed_master = _homogeneous_master(
                    rows[representative_id], permuted_fixture
                ).xreplace(alpha_map)
                expected_master = _homogeneous_master(row, fixture)
                if sp.expand(transformed_master - expected_master) != 0:
                    raise ValueError(f"master orbit fixture failed: {channel_id}")

    basis = _monomials(7)
    tangent = _domain_matrix(_tangent_columns(), basis)
    if exhaustive and tangent.rank() != 27:
        raise ValueError("open-edge tangent rank drifted")
    tangent_numeric = tangent.to_Matrix().subs(PIVOT_FIXTURE)
    if tangent_numeric.rank() != 27:
        raise ValueError("open-edge pivot rank drifted")
    masters_numeric = sp.Matrix(
        list(map(list, zip(*[_coefficient_vector(m, basis) for m in MASTERS])))
    ).subs(PIVOT_FIXTURE)
    if tangent_numeric.row_join(masters_numeric).rank() != 30:
        raise ValueError("master quotient rank drifted")
    _verify_dual_witnesses(stored, source_rows)

    rank_ledger = stored["rank_ledger"]
    if any(
        row["augmented_rank"] != rank_ledger["corner_zero_tangent_plus_master_rank"] + 1
        for row in rank_ledger["corner_zero_augmented_ranks"]
    ):
        raise ValueError("corner-zero augmented rank ledger drifted")
    payload = {
        "channel_rows": stored["channel_rows"],
        "representative_primitives": stored["representative_primitives"],
        "corner_zero_dual_witnesses": stored["corner_zero_dual_witnesses"],
        "rank_ledger": stored["rank_ledger"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != stored["formula_digest"]:
        raise ValueError("relative-IBP formula digest drifted")
    flags = stored["claim_flags"]
    required = [
        "TEN_POLE3_ROWS_REDUCED_TO_J_AND_TWO_DERIVATIVE_MASTERS",
        "FOUR_EXPLICIT_OPEN_EDGE_TANGENT_PRIMITIVE_REPRESENTATIVES",
        "ALL_TEN_ORIENTATIONS_COVERED_BY_EXACT_PERMUTATION",
        "OPEN_EDGE_NORMAL_FLUX_ZERO",
    ]
    forbidden = [
        "ZERO_CORNER_FLUX_REDUCTION_EXISTS_IN_DECLARED_ANSATZ",
        "CORNER_LOG_BUBBLE_SYSTEM_EVALUATED",
        "I29_POLE4_REDUCED",
        "GENERIC_GHOST_N3_FULL_KINEMATIC_FUNCTIONS_COMPUTED",
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
        "LORENTZIAN_CERTIFIED",
    ]
    if not all(flags[name] for name in required) or any(flags[name] for name in forbidden):
        raise ValueError("relative-IBP claim boundary drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exhaustive", action="store_true")
    args = parser.parse_args()
    verify(exhaustive=args.exhaustive)
    mode = "EXHAUSTIVE" if args.exhaustive else "FAST EXACT-FIXTURE"
    print(f"independent generic ghost n=3 pole-three relative IBP ({mode}): PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
