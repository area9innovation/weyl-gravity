#!/usr/bin/env python3
"""Reduce and integrate the generic pole-four I29 ghost triangle exactly."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import permutations
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

try:
    from .generic_background_ghost_n3_pole3_relative_ibp import (
        A,
        B,
        C,
        DELTA,
        Q1,
        Q2,
        X1,
        X2,
        X3,
        XS,
        _coefficient_vector,
        _domain_matrix,
        _monomials,
        rational_function_from_data,
    )
except ImportError:
    from generic_background_ghost_n3_pole3_relative_ibp import (
        A,
        B,
        C,
        DELTA,
        Q1,
        Q2,
        X1,
        X2,
        X3,
        XS,
        _coefficient_vector,
        _domain_matrix,
        _monomials,
        rational_function_from_data,
    )


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_I29_INTEGRATED_FUNCTION.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-i29-integrated-function-v1.schema.json"
BARYCENTRIC = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION.json"
TRIANGLE = HERE / "certificates/GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM.json"
SYMMETRIC = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION.json"

LAMBDA = sp.expand(
    X1**2 + X2**2 + X3**2 - 2 * X1 * X2 - 2 * X1 * X3 - 2 * X2 * X3
)
TARGET = -sp.Rational(16, 27) * A**3 * B**3 * C**3
MASTER_POLYNOMIALS = (DELTA**3, Q1 * DELTA**2, Q2 * DELTA**2)
MASTER_IDS = ("J_triangle", "M_x1", "M_x2")
FUNCTION_BASIS = (
    "J_triangle",
    "log_x2_over_x1",
    "log_x3_over_x1",
    "rational_corner",
)
PIVOT_FIXTURE = {X1: sp.Rational(2), X2: sp.Rational(3), X3: sp.Rational(5)}


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


def _poly_terms(expression: sp.Expr) -> list[dict[str, Any]]:
    polynomial = sp.Poly(sp.expand(expression), *XS, domain=sp.QQ)
    return [
        {"exponents": list(exponents), "coefficient": _q(coefficient)}
        for exponents, coefficient in polynomial.terms()
        if coefficient
    ]


def _rational_function(expression: sp.Expr) -> dict[str, Any]:
    numerator, denominator = sp.fraction(sp.cancel(expression))
    numerator = sp.Poly(numerator, *XS, domain=sp.QQ)
    denominator = sp.Poly(denominator, *XS, domain=sp.QQ)
    if denominator.LC() < 0:
        numerator = -numerator
        denominator = -denominator
    return {
        "numerator_terms": _poly_terms(numerator.as_expr()),
        "denominator_terms": _poly_terms(denominator.as_expr()),
    }


def _homogenize(expression: sp.Expr, degree: int) -> sp.Expr:
    polynomial = sp.Poly(sp.expand(expression), X1, X2, domain=sp.QQ)
    return sp.expand(
        sum(
            coefficient * X1**i * X2**j * X3 ** (degree - i - j)
            for (i, j), coefficient in polynomial.terms()
        )
    )


def _pole4_system() -> tuple[
    list[sp.Expr], list[tuple[sp.Expr, sp.Expr]], list[sp.Expr]
]:
    columns: list[sp.Expr] = []
    vector_fields: list[tuple[sp.Expr, sp.Expr]] = []
    for group in ("U", "V", "W"):
        for monomial in _monomials(6):
            U = monomial if group == "U" else 0
            V = monomial if group == "V" else 0
            W = monomial if group == "W" else 0
            P = sp.expand(A * (C * U + B * W))
            Q = sp.expand(B * (C * V - A * W))
            vector_fields.append((P, Q))
            columns.append(
                sp.expand(
                    DELTA * (sp.diff(P, A) + sp.diff(Q, B))
                    - 3 * (P * sp.diff(DELTA, A) + Q * sp.diff(DELTA, B))
                )
            )
    return columns, vector_fields, list(MASTER_POLYNOMIALS)


def _pivots(
    columns: list[sp.Expr], masters: list[sp.Expr], basis: list[sp.Expr]
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...], dict[str, int]]:
    tangent = _domain_matrix([row.subs(PIVOT_FIXTURE) for row in columns], basis)
    _, tangent_columns = tangent.rref()
    tangent_columns = tuple(tangent_columns)
    selected_tangent = tangent.extract(range(len(basis)), tangent_columns)
    _, tangent_rows = selected_tangent.transpose().rref()
    tangent_rows = tuple(tangent_rows)
    augmented = _domain_matrix(
        [
            *(columns[index].subs(PIVOT_FIXTURE) for index in tangent_columns),
            *(master.subs(PIVOT_FIXTURE) for master in masters),
        ],
        basis,
    )
    _, augmented_rows = augmented.transpose().rref()
    augmented_rows = tuple(augmented_rows)
    target = _domain_matrix([TARGET], basis)
    ranks = {
        "tangent_rank": tangent.rank(),
        "tangent_plus_masters_rank": tangent.hstack(
            _domain_matrix([row.subs(PIVOT_FIXTURE) for row in masters], basis)
        ).rank(),
        "tangent_plus_masters_and_target_rank": tangent.hstack(
            _domain_matrix([row.subs(PIVOT_FIXTURE) for row in masters], basis)
        ).hstack(target).rank(),
    }
    return tangent_columns, tangent_rows, augmented_rows, ranks


def _numeric_master_coordinates(
    columns: list[sp.Expr],
    masters: list[sp.Expr],
    basis: list[sp.Expr],
    tangent_columns: tuple[int, ...],
    augmented_rows: tuple[int, ...],
    point: tuple[int, int, int],
) -> list[sp.Expr]:
    substitution = dict(zip(XS, map(sp.Rational, point)))
    selected = [
        *(columns[index].subs(substitution) for index in tangent_columns),
        *(master.subs(substitution) for master in masters),
    ]
    square = _domain_matrix(selected, basis).extract(
        augmented_rows, range(len(selected))
    )
    right_hand_side = _domain_matrix([TARGET], basis).extract(augmented_rows, [0])
    numerator, denominator = square.solve_den(right_hand_side)
    return list((numerator.to_field() / denominator).to_Matrix()[-3:, 0])


def _master_reconstruction(
    columns: list[sp.Expr],
    masters: list[sp.Expr],
    basis: list[sp.Expr],
    tangent_columns: tuple[int, ...],
    augmented_rows: tuple[int, ...],
) -> tuple[list[sp.Expr], list[list[int]], list[list[int]]]:
    monomial_exponents = [
        (i, j) for i in range(9) for j in range(9 - i)
    ]
    points = [
        (i + 1, j + 20, 1) for i in range(9) for j in range(9 - i)
    ]
    interpolation = sp.Matrix(
        [
            [sp.Rational(x1) ** i * sp.Rational(x2) ** j for i, j in monomial_exponents]
            for x1, x2, _ in points
        ]
    )
    if interpolation.det() == 0:
        raise ValueError("I29 interpolation grid is not unisolvent")
    values = []
    for point in points:
        lam = LAMBDA.subs(dict(zip(XS, point)))
        coordinates = _numeric_master_coordinates(
            columns,
            masters,
            basis,
            tangent_columns,
            augmented_rows,
            point,
        )
        values.append([sp.cancel(value * lam**5) for value in coordinates])
    coefficient_matrix = interpolation.inv() * sp.Matrix(values)
    degrees = (7, 8, 8)
    polynomials = []
    for column, degree in enumerate(degrees):
        dehomogenized = sp.expand(
            sum(
                coefficient_matrix[row, column] * X1**i * X2**j
                for row, (i, j) in enumerate(monomial_exponents)
            )
        )
        if sp.Poly(dehomogenized, X1, X2).total_degree() > degree:
            raise ValueError("I29 master numerator degree bound failed")
        polynomials.append(_homogenize(dehomogenized, degree))
    holdouts = [(2, 3, 5), (4, 5, 7), (7, 2, 11), (11, 6, 13), (13, 17, 19)]
    for point in holdouts:
        lam = LAMBDA.subs(dict(zip(XS, point)))
        actual = _numeric_master_coordinates(
            columns,
            masters,
            basis,
            tangent_columns,
            augmented_rows,
            point,
        )
        expected = [
            sp.cancel(polynomial.subs(dict(zip(XS, point))) / lam**5)
            for polynomial in polynomials
        ]
        if actual != expected:
            raise ValueError(f"I29 master holdout failed: {point}")
    return polynomials, [list(point) for point in points], [list(point) for point in holdouts]


def _primitive_and_flux(
    columns: list[sp.Expr],
    vector_fields: list[tuple[sp.Expr, sp.Expr]],
    masters: list[sp.Expr],
    basis: list[sp.Expr],
    tangent_columns: tuple[int, ...],
    tangent_rows: tuple[int, ...],
    master_numerators: list[sp.Expr],
) -> tuple[sp.Expr, dict[str, Any]]:
    residual = sp.expand(
        LAMBDA**5 * TARGET
        - sum(master_numerators[index] * masters[index] for index in range(3))
    )
    tangent = _domain_matrix([columns[index] for index in tangent_columns], basis)
    right_hand_side = _domain_matrix([residual], basis, tangent.domain)
    square = tangent.extract(tangent_rows, range(len(tangent_columns)))
    restricted = right_hand_side.extract(tangent_rows, [0])
    numerator, denominator = square.solve_den(restricted)
    primitive = numerator.to_field() / denominator
    if not (tangent.matmul(primitive) - right_hand_side).is_zero_matrix:
        raise ValueError("I29 full symbolic relative-IBP identity failed")

    epsilon, parameter = sp.symbols("epsilon parameter")

    def epsilon_three(expression: sp.Expr) -> sp.Expr:
        return sp.Poly(sp.expand(expression), epsilon).coeff_monomial(epsilon**3)

    corner_numerators = [sp.S.Zero, sp.S.Zero, sp.S.Zero]
    for coefficient, column_index in zip(
        primitive.to_Matrix()[:, 0], tangent_columns
    ):
        P, Q = vector_fields[column_index]
        candidates = (
            -epsilon
            * (P + Q).subs(
                {A: epsilon * (1 - parameter), B: epsilon * parameter}
            ),
            epsilon * P.subs({A: 1 - epsilon, B: epsilon * (1 - parameter)}),
            epsilon * Q.subs({A: epsilon * parameter, B: 1 - epsilon}),
        )
        for index, candidate in enumerate(candidates):
            coefficient_at_corner = epsilon_three(candidate)
            if coefficient_at_corner:
                corner_numerators[index] += coefficient * coefficient_at_corner
    corner_numerators = [sp.cancel(value) for value in corner_numerators]
    if any(sp.Poly(value, parameter).degree() > 1 for value in corner_numerators):
        raise ValueError("I29 corner numerator exceeds the rational moment basis")

    def integrate_linear(value: sp.Expr, start: sp.Expr, end: sp.Expr) -> sp.Expr:
        polynomial = sp.Poly(value, parameter)
        constant = polynomial.coeff_monomial(1)
        linear = polynomial.coeff_monomial(parameter)
        return sp.cancel(
            constant * (start + end) / (2 * start**2 * end**2)
            + linear / (2 * start * end**2)
        )

    integrated_corners = [
        integrate_linear(corner_numerators[0], X1, X3),
        integrate_linear(corner_numerators[1], X2, X1),
        integrate_linear(corner_numerators[2], X3, X2),
    ]
    flux_numerator = sp.cancel(sum(integrated_corners))
    return sp.cancel(flux_numerator / LAMBDA**5), {
        "corner_ids": ["alpha0_vertex", "alpha1_vertex", "alpha2_vertex"],
        "corner_numerator_degrees": [
            sp.Poly(value, parameter).degree() for value in corner_numerators
        ],
        "angular_moments": {
            "I0": "(a+b)/(2*a^2*b^2)",
            "I1": "1/(2*a*b^2)",
        },
        "integrated_corner_numerators_over_lambda5": [
            _rational_function(sp.cancel(value / LAMBDA**5))
            for value in integrated_corners
        ],
        "total_flux": _rational_function(sp.cancel(flux_numerator / LAMBDA**5)),
    }


def _permutation_checks(coordinates: dict[str, sp.Expr]) -> list[dict[str, Any]]:
    log_vectors = ((0, 0), (1, 0), (0, 1))
    checks = []
    for permutation in permutations(range(3)):
        substitution = {XS[index]: XS[permutation[index]] for index in range(3)}
        j_value = coordinates["J_triangle"].subs(substitution, simultaneous=True)
        rational_value = coordinates["rational_corner"].subs(
            substitution, simultaneous=True
        )
        transformed_logs = [sp.S.Zero, sp.S.Zero]
        for basis_index, basis_id in enumerate(
            ("log_x2_over_x1", "log_x3_over_x1"), start=1
        ):
            coefficient = coordinates[basis_id].subs(substitution, simultaneous=True)
            vector = tuple(
                log_vectors[permutation[basis_index]][component]
                - log_vectors[permutation[0]][component]
                for component in range(2)
            )
            for component in range(2):
                transformed_logs[component] += coefficient * vector[component]
        defects = [
            sp.cancel(j_value - coordinates["J_triangle"]),
            sp.cancel(transformed_logs[0] - coordinates["log_x2_over_x1"]),
            sp.cancel(transformed_logs[1] - coordinates["log_x3_over_x1"]),
            sp.cancel(rational_value - coordinates["rational_corner"]),
        ]
        if any(defects):
            raise ValueError(f"I29 S3 covariance failed: {permutation}")
        checks.append({"permutation": list(permutation), "defects": "ZERO"})
    return checks


def build() -> dict[str, Any]:
    barycentric = json.loads(BARYCENTRIC.read_text())
    triangle = json.loads(TRIANGLE.read_text())
    symmetric = json.loads(SYMMETRIC.read_text())
    i29_row = next(
        row for row in barycentric["channel_rows"] if row["channel_id"] == "I29_123"
    )
    if (
        i29_row["reduced_denominator_power"] != 4
        or i29_row["reduced_numerator_terms"]
        != [
            {
                "alpha_exponents": [3, 3, 3],
                "box_exponents": [0, 0, 0],
                "coefficient": {"numerator": -16, "denominator": 27},
            }
        ]
    ):
        raise ValueError("upstream I29 carrier drifted")
    if not triangle["claim_flags"]["TWO_LOG_MASTER_REDUCTION_COMPUTED"]:
        raise ValueError("scalar-triangle system is not certified")

    columns, vector_fields, masters = _pole4_system()
    basis = _monomials(9)
    tangent_columns, tangent_rows, augmented_rows, ranks = _pivots(
        columns, masters, basis
    )
    if ranks != {
        "tangent_rank": 46,
        "tangent_plus_masters_rank": 49,
        "tangent_plus_masters_and_target_rank": 49,
    }:
        raise ValueError("I29 quotient ranks drifted")
    master_numerators, interpolation_points, holdout_points = _master_reconstruction(
        columns, masters, basis, tangent_columns, augmented_rows
    )
    master_coordinates = {
        master_id: sp.cancel(numerator / LAMBDA**5)
        for master_id, numerator in zip(MASTER_IDS, master_numerators)
    }
    flux, corner_ledger = _primitive_and_flux(
        columns,
        vector_fields,
        masters,
        basis,
        tangent_columns,
        tangent_rows,
        master_numerators,
    )

    triangle_masters = {
        master_id: {
            basis_id: rational_function_from_data(value)
            for basis_id, value in row.items()
        }
        for master_id, row in triangle["master_rows"].items()
    }
    coordinates = {}
    for basis_id in FUNCTION_BASIS[:3]:
        coordinates[basis_id] = sp.cancel(
            (master_coordinates["J_triangle"] if basis_id == "J_triangle" else 0)
            + master_coordinates["M_x1"] * triangle_masters["M_x1"][basis_id]
            + master_coordinates["M_x2"] * triangle_masters["M_x2"][basis_id]
        )
    coordinates["rational_corner"] = flux
    permutation_checks = _permutation_checks(coordinates)

    fixture = {X1: 1, X2: 1, X3: 1}
    symmetric_row = next(
        row for row in symmetric["channel_rows"] if row["channel_id"] == "I29_123"
    )["integrated_value"]
    actual_j = sp.cancel(coordinates["J_triangle"].subs(fixture))
    actual_rational = sp.cancel(flux.subs(fixture))
    if (
        actual_j != _from_q(symmetric_row["scalar_triangle_master_coefficient"])
        or actual_rational != _from_q(symmetric_row["rational"])
        or coordinates["log_x2_over_x1"].subs(fixture) != 0
        or coordinates["log_x3_over_x1"].subs(fixture) != 0
    ):
        raise ValueError("I29 symmetric-point regression failed")

    formula_payload = {
        "master_coordinates": {
            master_id: _rational_function(value)
            for master_id, value in master_coordinates.items()
        },
        "function_basis_coordinates": {
            basis_id: _rational_function(value)
            for basis_id, value in coordinates.items()
        },
        "corner_flux": corner_ledger,
        "pivot_columns": list(tangent_columns),
        "tangent_rows": list(tangent_rows),
        "augmented_rows": list(augmented_rows),
    }
    formula_digest = hashlib.sha256(
        json.dumps(formula_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "schema": "quantum-weyl-generic-background-ghost-n3-i29-integrated-function-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N3_I29_INTEGRATED_FUNCTION",
        "result_state": "COEFFICIENT_COMPUTED",
        "lifecycle_state": "ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPLETE_REPOSITORY_ASSEMBLY_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": barycentric["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "kinematics": "generic nonexceptional x1,x2,x3",
            "channel_id": "I29_123",
            "denominator_power": 4,
            "output": "one exact scalar-flat ghost n=3 form-factor coordinate",
        },
        "convention": {
            "Delta": "alpha1*alpha0*x1+alpha1*alpha2*x2+alpha2*alpha0*x3",
            "lambda": "x1^2+x2^2+x3^2-2*x1*x2-2*x1*x3-2*x2*x3",
            "target": "-(16/27)*(alpha0*alpha1*alpha2)^3/Delta^4",
            "function_basis": list(FUNCTION_BASIS),
            "overall_loop_prefactor": "not included",
        },
        "rank_ledger": {
            **ranks,
            "ambient_numerator_dimension": len(basis),
            "raw_tangent_column_count": len(columns),
            "canonical_tangent_column_count": len(tangent_columns),
            "master_count": 3,
        },
        "exact_reconstruction": {
            "lambda_denominator_power": 5,
            "master_numerator_degrees": [7, 8, 8],
            "interpolation_point_count": len(interpolation_points),
            "interpolation_points": interpolation_points,
            "holdout_points": holdout_points,
            "full_55_row_symbolic_relative_IBP_defect": "ZERO",
        },
        **formula_payload,
        "identity_ledger": {
            "S3_covariance": permutation_checks,
            "symmetric_point": [1, 1, 1],
            "symmetric_point_J_coefficient": _q(actual_j),
            "symmetric_point_rational_term": _q(actual_rational),
            "symmetric_point_status": "EXACT_MATCH",
        },
        "formula_digest": formula_digest,
        "claim_flags": {
            "I29_POLE4_REDUCED": True,
            "I29_GENERIC_INTEGRATED_FUNCTION_COMPUTED": True,
            "ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPUTED": True,
            "I29_REQUIRES_NEW_TRANSCENDENTAL_MASTER": False,
            "I29_CORNER_FLUX_RATIONAL": True,
            "COMPLETE_GENERIC_GHOST_DETERMINANT_COMPUTED": False,
            "COMPLETE_REPOSITORY_CUBIC_FORM_FACTORS_ASSEMBLED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
        },
        "dependencies": {
            "barycentric_factorization": _reference(BARYCENTRIC),
            "scalar_triangle_differential_system": _reference(TRIANGLE),
            "symmetric_point_integration": _reference(SYMMETRIC),
        },
        "next_gate": "ASSEMBLE_THE_ELEVEN_GHOST_FUNCTIONS_WITH_THE_PHYSICAL_FOURTH_ORDER_HESSIAN_INTO_THE_FIVE_REPOSITORY_CARRIERS",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate reduces the sole pole-four I29 ghost n=3 row by an exact full 55-row relative-IBP identity, evaluates its rational corner flux, and expresses the generic function in the same scalar-triangle, two-log and rational basis as the ten pole-three rows. Thus all eleven generic scalar-flat ghost n=3 functions are computed. It does not assemble the complete ghost determinant, supply the generic physical fourth-order Hessian, determine the five repository Weyl-gravity form factors or their coefficients, restore the strict QME, authorize residual transfer, or certify any Lorentzian, Hadamard, particle, positivity, scattering or unitarity claim."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(result), key=lambda row: list(row.path)
    )
    if errors:
        raise ValueError("; ".join(error.message for error in errors))


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
        raise SystemExit(f"stale I29 integrated-function certificate: {OUTPUT}")
    print("GENERIC BACKGROUND GHOST N3 I29 INTEGRATED FUNCTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
