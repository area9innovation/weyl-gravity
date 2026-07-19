#!/usr/bin/env python3
"""Reduce the ten generic pole-three ghost triangle rows by relative IBP."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_RELATIVE_IBP.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-pole3-relative-ibp-v1.schema.json"
BARYCENTRIC = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION.json"

A, B = sp.symbols("alpha1 alpha2")
C = 1 - A - B
X1, X2, X3 = sp.symbols("x1 x2 x3")
XS = (X1, X2, X3)
Q1, Q2, Q3 = A * C, A * B, B * C
DELTA = sp.expand(Q1 * X1 + Q2 * X2 + Q3 * X3)
MASTER_POLYNOMIALS = (DELTA**2, Q1 * DELTA, Q2 * DELTA)
MASTER_IDS = ("J_triangle", "M_x1", "M_x2")
PIVOT_FIXTURE = {X1: sp.Rational(2), X2: sp.Rational(3), X3: sp.Rational(5)}

ORBIT_MAP = {
    "I10_123": ("I10_123", (0, 1, 2), (0, 1, 2)),
    "I24_123": ("I24_123", (0, 1, 2), (0, 1, 2)),
    "I24_213": ("I24_123", (0, 2, 1), (1, 0, 2)),
    "I24_312": ("I24_123", (1, 0, 2), (2, 1, 0)),
    "I25_123": ("I25_123", (0, 1, 2), (0, 1, 2)),
    "I25_213": ("I25_123", (0, 2, 1), (1, 0, 2)),
    "I25_312": ("I25_123", (1, 0, 2), (2, 1, 0)),
    "I28_123": ("I28_123", (0, 1, 2), (0, 1, 2)),
    "I28_132": ("I28_123", (2, 0, 1), (2, 0, 1)),
    "I28_231": ("I28_123", (1, 0, 2), (2, 1, 0)),
}
REPRESENTATIVES = ("I10_123", "I24_123", "I25_123", "I28_123")


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


def _monomials(degree: int) -> list[sp.Expr]:
    return [
        A**i * B**j
        for i in range(degree + 1)
        for j in range(degree + 1 - i)
    ]


def _monomial_exponents(degree: int) -> list[list[int]]:
    return [
        [i, j]
        for i in range(degree + 1)
        for j in range(degree + 1 - i)
    ]


def _poly_terms(expression: sp.Expr, variables: tuple[sp.Symbol, ...]) -> list[dict[str, Any]]:
    polynomial = sp.Poly(sp.expand(expression), *variables, domain=sp.QQ)
    return [
        {"exponents": list(exponents), "coefficient": _q(coefficient)}
        for exponents, coefficient in polynomial.terms()
        if coefficient
    ]


def _poly_from_terms(terms: list[dict[str, Any]], variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    return sp.expand(
        sum(
            _from_q(term["coefficient"])
            * sp.prod(variable**power for variable, power in zip(variables, term["exponents"]))
            for term in terms
        )
    )


def _rational_function(expression: sp.Expr) -> dict[str, Any]:
    numerator, denominator = sp.fraction(sp.cancel(expression))
    numerator = sp.Poly(numerator, *XS, domain=sp.QQ)
    denominator = sp.Poly(denominator, *XS, domain=sp.QQ)
    if denominator.LC() < 0:
        numerator = -numerator
        denominator = -denominator
    return {
        "numerator_terms": _poly_terms(numerator.as_expr(), XS),
        "denominator_terms": _poly_terms(denominator.as_expr(), XS),
    }


def rational_function_from_data(value: dict[str, Any]) -> sp.Expr:
    return sp.cancel(
        _poly_from_terms(value["numerator_terms"], XS)
        / _poly_from_terms(value["denominator_terms"], XS)
    )


def _target(row: dict[str, Any]) -> sp.Expr:
    return sp.expand(
        sum(
            _from_q(term["coefficient"])
            * A ** term["alpha_exponents"][0]
            * B ** term["alpha_exponents"][1]
            * C ** term["alpha_exponents"][2]
            * X1 ** term["box_exponents"][0]
            * X2 ** term["box_exponents"][1]
            * X3 ** term["box_exponents"][2]
            for term in row["reduced_numerator_terms"]
        )
    )


def _coefficient_vector(expression: sp.Expr, basis: list[sp.Expr]) -> list[sp.Expr]:
    polynomial = sp.Poly(sp.expand(expression), A, B)
    return [polynomial.coeff_monomial(monomial) for monomial in basis]


def _domain_matrix(
    expressions: list[sp.Expr],
    basis: list[sp.Expr],
    domain: Any | None = None,
) -> Any:
    rows = list(
        map(list, zip(*[_coefficient_vector(expression, basis) for expression in expressions]))
    )
    matrix = sp.polys.matrices.DomainMatrix.from_list_sympy(
        len(basis), len(expressions), rows
    )
    return matrix.to_field() if domain is None else matrix.convert_to(domain)


def _tangent_basis() -> tuple[list[sp.Expr], list[tuple[sp.Expr, sp.Expr]], list[dict[str, Any]]]:
    monomials = _monomials(4)
    columns: list[sp.Expr] = []
    vector_fields: list[tuple[sp.Expr, sp.Expr]] = []
    labels: list[dict[str, Any]] = []
    for group_index, group in enumerate(("U", "V", "W")):
        for monomial_index, monomial in enumerate(monomials):
            U = monomial if group == "U" else 0
            V = monomial if group == "V" else 0
            W = monomial if group == "W" else 0
            P = sp.expand(A * (C * U + B * W))
            Q = sp.expand(B * (C * V - A * W))
            column = sp.expand(
                DELTA * (sp.diff(P, A) + sp.diff(Q, B))
                - 2 * (P * sp.diff(DELTA, A) + Q * sp.diff(DELTA, B))
            )
            columns.append(column)
            vector_fields.append((P, Q))
            labels.append(
                {
                    "group": group,
                    "group_index": group_index,
                    "monomial_index": monomial_index,
                    "monomial_exponents": _monomial_exponents(4)[monomial_index],
                }
            )
    return columns, vector_fields, labels


def _corner_zero_subspace() -> list[sp.Expr]:
    monomials = _monomials(4)

    def kernel(points: tuple[tuple[int, int], tuple[int, int]]) -> list[sp.Expr]:
        evaluation = sp.Matrix(
            [
                [monomial.subs({A: a, B: b}) for monomial in monomials]
                for a, b in points
            ]
        )
        return [
            sp.expand(sum(vector[i] * monomials[i] for i in range(len(monomials))))
            for vector in evaluation.nullspace()
        ]

    U_basis = kernel(((1, 0), (0, 0)))
    V_basis = kernel(((0, 1), (0, 0)))
    W_basis = kernel(((1, 0), (0, 1)))
    columns = []
    for group, basis in (("U", U_basis), ("V", V_basis), ("W", W_basis)):
        for monomial in basis:
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


def _master_solution(tangent: Any, masters: Any, targets: Any) -> Any:
    annihilator = tangent.transpose().nullspace()
    quotient = annihilator.matmul(masters)
    _, pivot_rows = quotient.transpose().rref()
    square = quotient.extract(pivot_rows, range(3))
    right_hand_side = annihilator.matmul(targets).extract(
        pivot_rows, range(targets.shape[1])
    )
    numerator, denominator = square.solve_den(right_hand_side)
    solution = numerator.to_field() / denominator
    if not annihilator.matmul(masters.matmul(solution) - targets).is_zero_matrix:
        raise ValueError("master quotient solve failed")
    return solution


def _primitive_pivots(tangent: Any) -> tuple[tuple[int, ...], tuple[int, ...], Any]:
    numeric = tangent.to_Matrix().subs(PIVOT_FIXTURE)
    _, pivot_columns = numeric.rref()
    _, pivot_rows = numeric[:, list(pivot_columns)].transpose().rref()
    square = tangent.extract(pivot_rows, pivot_columns)
    if len(pivot_columns) != 27 or len(pivot_rows) != 27:
        raise ValueError("canonical primitive pivot fixture drifted")
    return tuple(pivot_columns), tuple(pivot_rows), square


def _primitive_data(
    channel_index: int,
    residuals: Any,
    tangent: Any,
    pivot_columns: tuple[int, ...],
    pivot_rows: tuple[int, ...],
    square: Any,
    labels: list[dict[str, Any]],
) -> dict[str, Any]:
    right_hand_side = residuals.extract(pivot_rows, [channel_index])
    numerator, denominator = square.solve_den(right_hand_side)
    solution = numerator.to_field() / denominator
    domain = tangent.domain
    full_rows: list[list[Any]] = []
    pivot_cursor = 0
    for column_index in range(tangent.shape[1]):
        if column_index in pivot_columns:
            full_rows.append([solution[pivot_cursor, 0].element])
            pivot_cursor += 1
        else:
            full_rows.append([domain.zero])
    full = sp.polys.matrices.DomainMatrix(
        full_rows, (tangent.shape[1], 1), domain
    )
    if tangent.matmul(full) != residuals.extract(range(tangent.shape[0]), [channel_index]):
        raise ValueError("canonical primitive identity failed")
    expressions = [sp.S.Zero, sp.S.Zero, sp.S.Zero]
    coefficients = []
    for column_index, row in enumerate(full_rows):
        coefficient = row[0].as_expr()
        if coefficient == 0:
            continue
        label = labels[column_index]
        monomial = A ** label["monomial_exponents"][0] * B ** label["monomial_exponents"][1]
        expressions[label["group_index"]] += coefficient * monomial
        coefficients.append(
            {
                "basis_column": column_index,
                **label,
                "coefficient": _rational_function(coefficient),
            }
        )
    U, V, W = map(sp.cancel, expressions)
    P = sp.expand(A * (C * U + B * W))
    Q = sp.expand(B * (C * V - A * W))
    if (
        sp.expand(P.subs(A, 0)) != 0
        or sp.expand(Q.subs(B, 0)) != 0
        or sp.expand((P + Q).subs(B, 1 - A)) != 0
    ):
        raise ValueError("open-edge tangency failed")
    corner_pairs = {
        "alpha1_vertex": (U.subs({A: 1, B: 0}), W.subs({A: 1, B: 0})),
        "alpha2_vertex": (V.subs({A: 0, B: 1}), W.subs({A: 0, B: 1})),
        "alpha0_vertex": (U.subs({A: 0, B: 0}), V.subs({A: 0, B: 0})),
    }
    corner_rows = []
    for corner_id, pair in corner_pairs.items():
        corner_rows.append(
            {
                "corner_id": corner_id,
                "leading_pair": [_rational_function(pair[0]), _rational_function(pair[1])],
                "leading_pair_zero": bool(pair[0] == 0 and pair[1] == 0),
            }
        )
    return {
        "coefficient_count": len(coefficients),
        "coefficients": coefficients,
        "open_edge_normal_flux": "ZERO",
        "corner_leading_rows": corner_rows,
        "all_punctured_corner_fluxes_zero": all(
            row["leading_pair_zero"] for row in corner_rows
        ),
    }


def build() -> dict[str, Any]:
    source = json.loads(BARYCENTRIC.read_text())
    if not source["claim_flags"]["GENERIC_GHOST_N3_BARYCENTRIC_FACTORIZATION_COMPUTED"]:
        raise ValueError("barycentric dependency is not certified")
    rows = [
        row for row in source["channel_rows"]
        if row["reduced_denominator_power"] == 3
    ]
    if len(rows) != 10 or {row["channel_id"] for row in rows} != set(ORBIT_MAP):
        raise ValueError("pole-three channel inventory drifted")

    polynomial_basis = _monomials(7)
    tangent_columns, _, labels = _tangent_basis()
    tangent = _domain_matrix(tangent_columns, polynomial_basis)
    masters = _domain_matrix(list(MASTER_POLYNOMIALS), polynomial_basis, tangent.domain)
    targets = _domain_matrix([_target(row) for row in rows], polynomial_basis, tangent.domain)
    master_solution = _master_solution(tangent, masters, targets)
    residuals = targets - masters.matmul(master_solution)
    pivot_columns, pivot_rows, primitive_square = _primitive_pivots(tangent)

    representatives = {}
    for representative_id in REPRESENTATIVES:
        channel_index = next(
            index for index, row in enumerate(rows)
            if row["channel_id"] == representative_id
        )
        primitive = _primitive_data(
            channel_index,
            residuals,
            tangent,
            pivot_columns,
            pivot_rows,
            primitive_square,
            labels,
        )
        representatives[representative_id] = primitive
        gc.collect()

    channel_rows = []
    for channel_index, row in enumerate(rows):
        representative_id, alpha_permutation, x_permutation = ORBIT_MAP[row["channel_id"]]
        master_coordinates = [
            master_solution[index, channel_index].element.as_expr()
            for index in range(3)
        ]
        channel_rows.append(
            {
                "channel_id": row["channel_id"],
                "representative_id": representative_id,
                "alpha_permutation": list(alpha_permutation),
                "x_permutation": list(x_permutation),
                "master_coordinates": {
                    master_id: _rational_function(coordinate)
                    for master_id, coordinate in zip(MASTER_IDS, master_coordinates)
                },
                "integrated_form": (
                    "c_J*J_triangle-c_x1*dJ_triangle/dx1-c_x2*dJ_triangle/dx2"
                ),
            }
        )

    corner_zero_columns = _corner_zero_subspace()
    corner_zero = _domain_matrix(
        corner_zero_columns + list(MASTER_POLYNOMIALS),
        polynomial_basis,
        tangent.domain,
    )
    corner_zero_rank = corner_zero.rank()
    if corner_zero_rank != 26:
        raise ValueError("corner-zero tangent-plus-master rank drifted")
    corner_numeric = corner_zero.to_Matrix().subs(PIVOT_FIXTURE)
    corner_numeric_rank = corner_numeric.rank()
    if corner_numeric_rank != corner_zero_rank:
        raise ValueError("corner-zero pivot fixture is rank-singular")
    corner_annihilator = corner_numeric.transpose().nullspace()
    representative_indices = {
        row["channel_id"]: channel_index
        for channel_index, row in enumerate(rows)
        if row["channel_id"] in REPRESENTATIVES
    }
    representative_corner_ranks = {}
    corner_zero_dual_witnesses = {}
    polynomial_exponents = _monomial_exponents(7)
    for representative_id in REPRESENTATIVES:
        target = targets.extract(
            range(len(polynomial_basis)),
            [representative_indices[representative_id]],
        )
        target_numeric = target.to_Matrix().subs(PIVOT_FIXTURE)
        witness_row = next(
            (
                row_index
                for row_index, vector in enumerate(corner_annihilator)
                if (vector.dot(target_numeric)) != 0
            ),
            None,
        )
        if witness_row is None:
            raise ValueError(f"corner-zero non-membership failed: {representative_id}")
        witness_vector = corner_annihilator[witness_row]
        normalization = witness_vector.dot(target_numeric)
        coefficients = []
        for monomial_index in range(len(polynomial_basis)):
            coefficient = sp.cancel(witness_vector[monomial_index] / normalization)
            if coefficient == 0:
                continue
            coefficients.append(
                {
                    "monomial_index": monomial_index,
                    "monomial_exponents": polynomial_exponents[monomial_index],
                    "coefficient": _q(coefficient),
                }
            )
        representative_corner_ranks[representative_id] = corner_zero_rank + 1
        corner_zero_dual_witnesses[representative_id] = {
            "annihilator_row_index": witness_row,
            "coefficient_count": len(coefficients),
            "coefficients": coefficients,
            "annihilates_corner_zero_span": True,
            "generic_base_rank": corner_zero_rank,
            "fixture_base_rank": corner_numeric_rank,
            "fixture": {"x1": 2, "x2": 3, "x3": 5},
            "generic_nonmembership_reason": "rank-stable rational fixture has a normalized nonzero augmented minor",
            "target_normalization": "ONE",
        }
    corner_augmented_ranks = []
    for row in rows:
        representative_id = ORBIT_MAP[row["channel_id"]][0]
        corner_augmented_ranks.append(
            {
                "channel_id": row["channel_id"],
                "rank_source_channel": representative_id,
                "augmented_rank": representative_corner_ranks[representative_id],
            }
        )

    # The pivot minor proves rank(tangent)=27.  The exact quotient solve proves
    # that the three master columns are independent modulo the tangent span and
    # that every target lies in the resulting 30-dimensional span, so replaying
    # three additional generic-rational rank eliminations would add cost but no
    # independent evidence.
    tangent_rank = len(pivot_columns)
    formula_payload = {
        "channel_rows": channel_rows,
        "representative_primitives": representatives,
        "corner_zero_dual_witnesses": corner_zero_dual_witnesses,
        "rank_ledger": {
            "polynomial_space_dimension": len(polynomial_basis),
            "open_edge_tangent_rank": tangent_rank,
            "open_edge_tangent_plus_master_rank": tangent_rank + 3,
            "open_edge_tangent_plus_master_and_targets_rank": tangent_rank + 3,
            "corner_zero_tangent_plus_master_rank": corner_zero_rank,
            "corner_zero_augmented_ranks": corner_augmented_ranks,
        },
    }
    formula_digest = hashlib.sha256(
        json.dumps(formula_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    result = {
        "schema": "quantum-weyl-generic-background-ghost-n3-pole3-relative-ibp-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N3_POLE3_RELATIVE_IBP",
        "result_state": "GENERIC_N3_TEN_POLE3_ROWS_REDUCED_TO_TRIANGLE_DERIVATIVE_MASTERS",
        "lifecycle_state": "CORNER_LOG_SYSTEM_AND_I29_POLE4_REDUCTION_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": source["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "curvature_order": 3,
            "kinematics": "generic positive nonexceptional x1,x2,x3 with Kallen lambda nonzero",
            "included_channels": [row["channel_id"] for row in rows],
            "excluded_channel": "I29_123 pole-four row",
        },
        "convention": {
            "affine_coordinates": ["alpha1", "alpha2"],
            "alpha0": "1-alpha1-alpha2",
            "Delta": "alpha0*alpha1*x1+alpha1*alpha2*x2+alpha2*alpha0*x3",
            "Kallen_lambda": "x1^2+x2^2+x3^2-2*x1*x2-2*x1*x3-2*x2*x3",
            "master_basis": [
                "J_triangle=integral_simplex 1/Delta",
                "M_x1=integral_simplex alpha0*alpha1/Delta^2=-dJ_triangle/dx1",
                "M_x2=integral_simplex alpha1*alpha2/Delta^2=-dJ_triangle/dx2",
            ],
            "master_relation": "x1*M_x1+x2*M_x2+x3*M_x3=J_triangle",
            "primitive_parameterization": "P=alpha1*(alpha0*U+alpha2*W), Q=alpha2*(alpha0*V-alpha1*W)",
            "primitive_identity": "N=Delta*(dP/dalpha1+dQ/dalpha2)-2*(P*dDelta/dalpha1+Q*dDelta/dalpha2)+cJ*Delta^2+cx1*alpha0*alpha1*Delta+cx2*alpha1*alpha2*Delta",
            "primitive_gauge": {
                "UV_W_affine_degree_bound": 4,
                "monomial_order": _monomial_exponents(4),
                "pivot_fixture": {"x1": 2, "x2": 3, "x3": 5},
                "pivot_columns": list(pivot_columns),
                "pivot_rows": list(pivot_rows),
                "nonpivot_coefficients": "ZERO",
            },
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
            "W_and_Tr_log_multiplier": "-8/3 already included upstream",
        },
        "rank_ledger": formula_payload["rank_ledger"],
        "channel_rows": channel_rows,
        "representative_primitives": representatives,
        "corner_zero_dual_witnesses": corner_zero_dual_witnesses,
        "corner_flux_carrier": {
            "status": "ISOLATED_NOT_INTEGRATED",
            "alpha1_vertex_angular_form": "(W_A*cos(theta)^2+U_A*sin(theta)^2)/(x2*cos(theta)+x1*sin(theta))^2 dtheta",
            "alpha2_vertex_angular_form": "(V_B*sin(theta)^2-W_B*cos(theta)^2)/(x2*cos(theta)+x3*sin(theta))^2 dtheta",
            "alpha0_vertex_angular_form": "-(U_C*cos(theta)^2+V_C*sin(theta)^2)/(x1*cos(theta)+x3*sin(theta))^2 dtheta",
            "theta_interval": "[0,pi/2]",
            "interpretation": "two independent corner-log directions equivalent to descendant edge-bubble logarithm ratios",
        },
        "formula_digest": formula_digest,
        "coefficient_disposition": {
            "ten_pole3_relative_IBP_reductions": "COMPUTED",
            "corner_log_bubble_conversion": "NOT_COMPUTED",
            "I29_pole4_reduction": "NOT_COMPUTED",
            "generic_integrated_channel_functions": "PARTIAL_10_OF_11_DERIVATIVE_MASTER_FORM",
        },
        "claim_flags": {
            "TEN_POLE3_ROWS_REDUCED_TO_J_AND_TWO_DERIVATIVE_MASTERS": True,
            "FOUR_EXPLICIT_OPEN_EDGE_TANGENT_PRIMITIVE_REPRESENTATIVES": True,
            "ALL_TEN_ORIENTATIONS_COVERED_BY_EXACT_PERMUTATION": True,
            "OPEN_EDGE_NORMAL_FLUX_ZERO": True,
            "ZERO_CORNER_FLUX_REDUCTION_EXISTS_IN_DECLARED_ANSATZ": False,
            "CORNER_LOG_BUBBLE_SYSTEM_EVALUATED": False,
            "I29_POLE4_REDUCED": False,
            "GENERIC_GHOST_N3_FULL_KINEMATIC_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {"barycentric_factorization": _reference(BARYCENTRIC)},
        "next_gate": "EVALUATE_SCALAR_TRIANGLE_DERIVATIVE_SYSTEM_AS_TWO_CORNER_LOG_RATIOS_AND_REDUCE_I29_POLE4",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate gives exact generic relative-IBP reductions for the ten pole-three ghost n=3 rows. Four explicit canonical primitives cover all ten orientations by exact simplex permutations. Their normal flux vanishes on every open edge. The quotient is three-dimensional and is represented by the scalar triangle and two independent first kinematic derivatives. Imposing the stronger quadratic corner-vanishing conditions makes every target leave the generated span, so punctured-corner logarithm carriers are unavoidable. Their exact angular forms are isolated but not yet evaluated as bubble-log ratios. The pole-four I29 row, all eleven fully integrated generic functions, the physical Hessian, complete Gamma1/Q1, residual transfer, and every Lorentzian, Hadamard, particle, positivity, scattering, or unitarity claim remain open."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        "channel_rows": value["channel_rows"],
        "representative_primitives": value["representative_primitives"],
        "corner_zero_dual_witnesses": value["corner_zero_dual_witnesses"],
        "rank_ledger": value["rank_ledger"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != value["formula_digest"]:
        raise ValueError("pole-three relative-IBP digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale pole-three relative-IBP certificate: {OUTPUT}")
    print("GENERIC GHOST N3 POLE3 IBP: TEN ROWS -> J TRIANGLE + TWO DERIVATIVE MASTERS; CORNER LOGS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
