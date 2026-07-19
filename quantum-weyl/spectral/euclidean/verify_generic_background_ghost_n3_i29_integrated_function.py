#!/usr/bin/env python3
"""Independent replay of the exact generic I29 integrated function."""

from __future__ import annotations

import hashlib
import json
from itertools import permutations
from pathlib import Path

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
        _domain_matrix,
        _monomials,
        rational_function_from_data,
    )


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_I29_INTEGRATED_FUNCTION.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-i29-integrated-function-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(certificate),
        key=lambda row: list(row.path),
    )
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(row.message for row in errors))

    dependencies = {}
    for reference in certificate["dependencies"].values():
        path = ROOT / reference["path"]
        if _sha256(path) != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {path}")
        value = json.loads(path.read_text())
        if value["result_id"] != reference["result_id"]:
            raise ValueError(f"dependency identity drifted: {path}")
        dependencies[value["result_id"]] = value

    columns = []
    vector_fields = []
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
    masters = (DELTA**3, Q1 * DELTA**2, Q2 * DELTA**2)
    target = -sp.Rational(16, 27) * A**3 * B**3 * C**3
    basis = _monomials(9)
    tangent_columns = tuple(certificate["pivot_columns"])
    tangent_rows = tuple(certificate["tangent_rows"])
    fixture = {X1: sp.Rational(2), X2: sp.Rational(3), X3: sp.Rational(5)}
    tangent_fixture = _domain_matrix(
        [column.subs(fixture) for column in columns], basis
    )
    masters_fixture = _domain_matrix(
        [master.subs(fixture) for master in masters], basis
    )
    target_fixture = _domain_matrix([target], basis)
    if (
        tangent_fixture.rank(),
        tangent_fixture.hstack(masters_fixture).rank(),
        tangent_fixture.hstack(masters_fixture).hstack(target_fixture).rank(),
    ) != (46, 49, 49):
        raise ValueError("independent I29 rank replay failed")

    master_coordinates = {
        master_id: rational_function_from_data(value)
        for master_id, value in certificate["master_coordinates"].items()
    }
    lam = sp.expand(
        X1**2 + X2**2 + X3**2
        - 2 * X1 * X2
        - 2 * X1 * X3
        - 2 * X2 * X3
    )
    master_numerators = [
        sp.cancel(master_coordinates[master_id] * lam**5)
        for master_id in ("J_triangle", "M_x1", "M_x2")
    ]
    if any(sp.fraction(value)[1] != 1 for value in master_numerators):
        raise ValueError("independent I29 lambda-five denominator replay failed")
    residual = sp.expand(
        lam**5 * target
        - sum(master_numerators[index] * masters[index] for index in range(3))
    )
    tangent = _domain_matrix([columns[index] for index in tangent_columns], basis)
    right_hand_side = _domain_matrix([residual], basis, tangent.domain)
    square = tangent.extract(tangent_rows, range(len(tangent_columns)))
    restricted = right_hand_side.extract(tangent_rows, [0])
    numerator, denominator = square.solve_den(restricted)
    primitive_numerator = numerator.to_field() / denominator
    if not (tangent.matmul(primitive_numerator) - right_hand_side).is_zero_matrix:
        raise ValueError("independent full 55-row I29 relative-IBP replay failed")

    epsilon, parameter = sp.symbols("epsilon parameter")

    def epsilon_three(expression: sp.Expr) -> sp.Expr:
        return sp.Poly(sp.expand(expression), epsilon).coeff_monomial(epsilon**3)

    corner_numerators = [sp.S.Zero, sp.S.Zero, sp.S.Zero]
    for coefficient, column_index in zip(
        primitive_numerator.to_Matrix()[:, 0], tangent_columns
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
    if [sp.Poly(value, parameter).degree() for value in corner_numerators] != [1, 1, 1]:
        raise ValueError("independent I29 corner-degree replay failed")

    def integrate_linear(value: sp.Expr, start: sp.Expr, end: sp.Expr) -> sp.Expr:
        polynomial = sp.Poly(value, parameter)
        constant = polynomial.coeff_monomial(1)
        linear = polynomial.coeff_monomial(parameter)
        return sp.cancel(
            constant * (start + end) / (2 * start**2 * end**2)
            + linear / (2 * start * end**2)
        )

    flux = sp.cancel(
        (
            integrate_linear(corner_numerators[0], X1, X3)
            + integrate_linear(corner_numerators[1], X2, X1)
            + integrate_linear(corner_numerators[2], X3, X2)
        )
        / lam**5
    )
    stored_flux = rational_function_from_data(certificate["corner_flux"]["total_flux"])
    if sp.cancel(flux - stored_flux) != 0:
        raise ValueError("independent I29 corner-flux replay failed")

    triangle = dependencies["GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM"]
    triangle_masters = {
        master_id: {
            basis_id: rational_function_from_data(value)
            for basis_id, value in row.items()
        }
        for master_id, row in triangle["master_rows"].items()
    }
    reconstructed = {}
    for basis_id in ("J_triangle", "log_x2_over_x1", "log_x3_over_x1"):
        reconstructed[basis_id] = sp.cancel(
            (master_coordinates["J_triangle"] if basis_id == "J_triangle" else 0)
            + master_coordinates["M_x1"] * triangle_masters["M_x1"][basis_id]
            + master_coordinates["M_x2"] * triangle_masters["M_x2"][basis_id]
        )
    reconstructed["rational_corner"] = flux
    stored_coordinates = {
        basis_id: rational_function_from_data(value)
        for basis_id, value in certificate["function_basis_coordinates"].items()
    }
    if any(sp.cancel(reconstructed[key] - stored_coordinates[key]) for key in reconstructed):
        raise ValueError("independent I29 final master reduction failed")

    log_vectors = ((0, 0), (1, 0), (0, 1))
    for permutation in permutations(range(3)):
        substitution = {XS[index]: XS[permutation[index]] for index in range(3)}
        if sp.cancel(
            reconstructed["J_triangle"].subs(substitution, simultaneous=True)
            - reconstructed["J_triangle"]
        ) != 0:
            raise ValueError("independent I29 J-coordinate covariance failed")
        if sp.cancel(
            flux.subs(substitution, simultaneous=True) - flux
        ) != 0:
            raise ValueError("independent I29 flux covariance failed")
        transformed = [sp.S.Zero, sp.S.Zero]
        for basis_index, basis_id in enumerate(
            ("log_x2_over_x1", "log_x3_over_x1"), start=1
        ):
            coefficient = reconstructed[basis_id].subs(
                substitution, simultaneous=True
            )
            for component in range(2):
                transformed[component] += coefficient * (
                    log_vectors[permutation[basis_index]][component]
                    - log_vectors[permutation[0]][component]
                )
        if any(
            sp.cancel(transformed[index] - reconstructed[basis_id])
            for index, basis_id in enumerate(
                ("log_x2_over_x1", "log_x3_over_x1")
            )
        ):
            raise ValueError("independent I29 logarithmic covariance failed")

    symmetric = dependencies[
        "GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION"
    ]
    symmetric_row = next(
        row for row in symmetric["channel_rows"] if row["channel_id"] == "I29_123"
    )["integrated_value"]
    point = {X1: 1, X2: 1, X3: 1}
    if (
        sp.cancel(reconstructed["J_triangle"].subs(point))
        != sp.Rational(
            symmetric_row["scalar_triangle_master_coefficient"]["numerator"],
            symmetric_row["scalar_triangle_master_coefficient"]["denominator"],
        )
        or sp.cancel(flux.subs(point))
        != sp.Rational(
            symmetric_row["rational"]["numerator"],
            symmetric_row["rational"]["denominator"],
        )
    ):
        raise ValueError("independent I29 symmetric-point replay failed")

    formula_payload = {
        "master_coordinates": certificate["master_coordinates"],
        "function_basis_coordinates": certificate["function_basis_coordinates"],
        "corner_flux": certificate["corner_flux"],
        "pivot_columns": certificate["pivot_columns"],
        "tangent_rows": certificate["tangent_rows"],
        "augmented_rows": certificate["augmented_rows"],
    }
    digest = hashlib.sha256(
        json.dumps(formula_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != certificate["formula_digest"]:
        raise ValueError("I29 formula digest drifted")
    if certificate["claim_flags"] != {
        "ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPUTED": True,
        "COMPLETE_GENERIC_GHOST_DETERMINANT_COMPUTED": False,
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
        "COMPLETE_REPOSITORY_CUBIC_FORM_FACTORS_ASSEMBLED": False,
        "I29_CORNER_FLUX_RATIONAL": True,
        "I29_GENERIC_INTEGRATED_FUNCTION_COMPUTED": True,
        "I29_POLE4_REDUCED": True,
        "I29_REQUIRES_NEW_TRANSCENDENTAL_MASTER": False,
        "LORENTZIAN_CERTIFIED": False,
        "RESIDUAL_TRANSFER_AUTHORIZED": False,
    }:
        raise ValueError("I29 claim boundary drifted")


def main() -> int:
    verify()
    print("independent generic ghost n=3 I29 integrated function: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
