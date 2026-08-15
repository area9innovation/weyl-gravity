#!/usr/bin/env python3
"""Independent verifier for the flat-potential Piola/Ward cancellation."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_"
    "PIOLA_WARD_CANCELLATION_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-flat-potential-"
    "piola-ward-cancellation-v1.schema.json"
)


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [
        row[:] + [Fraction(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * entry
                for value, entry in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        value = work[column][column]
        result *= value
        work[column] = [entry / value for entry in work[column]]
        for row in range(column + 1, len(work)):
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return result


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum(
                (left[row][inner] * right[inner][column]
                 for inner in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_vector(
    matrix: list[list[Fraction]], vector: list[Fraction]
) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def minor(
    matrix: list[list[Fraction]], deleted_row: int, deleted_column: int
) -> list[list[Fraction]]:
    return [
        [
            value
            for column, value in enumerate(row)
            if column != deleted_column
        ]
        for row_index, row in enumerate(matrix)
        if row_index != deleted_row
    ]


def reconstruct() -> dict:
    omega = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    direction = [Fraction(1), Fraction(-1), Fraction(0), Fraction(0)]
    size = 4
    neighbors = [
        [(site - 1) % size, (site + 1) % size] for site in range(size)
    ]
    residual = [
        sum((omega[other] for other in neighbors[site]), Fraction(0))
        / omega[site]
        - 2
        for site in range(size)
    ]
    jacobian = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    jacobian_directional = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    for site in range(size):
        for other in neighbors[site]:
            weight = omega[other] / omega[site]
            delta = direction[other] - direction[site]
            jacobian[site][other] = weight
            jacobian[site][site] -= weight
            jacobian_directional[site][other] = weight * delta
            jacobian_directional[site][site] -= weight * delta
    projection = [
        [Fraction(int(row == column)) - Fraction(1, size)
         for column in range(size)]
        for row in range(size)
    ]
    flat = multiply(projection, jacobian)
    flat_directional = multiply(projection, jacobian_directional)
    basis = [
        [
            Fraction(int(row == column)) - Fraction(int(row == size - 1))
            for column in range(size - 1)
        ]
        for row in range(size)
    ]
    left = multiply(
        inverse(multiply(transpose(basis), basis)), transpose(basis)
    )
    coordinate = multiply(multiply(left, flat), basis)
    coordinate_directional = multiply(
        multiply(left, flat_directional), basis
    )
    induced = matrix_vector(flat, direction)

    # Independent logarithmic determinant jet from ||Omega||^2*tau.
    ground_norm_squared = dot(omega, omega)
    norm_log_derivative = (
        2
        * sum(
            (omega[index] ** 2 * direction[index] for index in range(size)),
            Fraction(0),
        )
        / ground_norm_squared
    )
    edge_products = [
        omega[index] * omega[(index + 1) % size] for index in range(size)
    ]
    all_edges = __import__("math").prod(edge_products)
    tree_terms = [all_edges / edge for edge in edge_products]
    tree_log_derivatives = [
        -(direction[index] + direction[(index + 1) % size])
        for index in range(size)
    ]
    tree_log_derivative = sum(
        (term * derivative
         for term, derivative in zip(tree_terms, tree_log_derivatives)),
        Fraction(0),
    ) / sum(tree_terms, Fraction(0))
    logdet_directional = norm_log_derivative + tree_log_derivative

    kinetic = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    for site in range(size):
        kinetic[site][site] = 2 + residual[site]
        for other in neighbors[site]:
            kinetic[site][other] -= 1
    cofactors = [
        determinant(minor(kinetic, index, index)) for index in range(size)
    ]
    pseudodeterminant = sum(cofactors, Fraction(0))

    # Ground-state resolvent gradient checked against inverse transpose.
    bordered = [
        row[:] + [omega[index]] for index, row in enumerate(kinetic)
    ]
    bordered.append(omega[:] + [Fraction(0)])
    pseudoinverse = [row[:size] for row in inverse(bordered)[:size]]
    source = [direction[index] / omega[index] for index in range(size)]
    solved = matrix_vector(pseudoinverse, source)
    resolvent_gradient = [
        -omega[index] * solved[index] for index in range(size)
    ]
    coordinate_resolvent_covector = matrix_vector(
        transpose(basis), resolvent_gradient
    )
    inverse_transpose_covector = matrix_vector(
        transpose(inverse(coordinate)),
        matrix_vector(transpose(basis), direction),
    )

    action_score = dot(
        residual, matrix_vector(jacobian, direction)
    ) / Fraction(4, 25)
    return {
        "omega": omega,
        "direction": direction,
        "residual": residual,
        "coordinate": coordinate,
        "coordinate_directional": coordinate_directional,
        "oriented_determinant": determinant(coordinate),
        "pseudodeterminant": pseudodeterminant,
        "induced": induced,
        "norm_log_derivative": norm_log_derivative,
        "tree_log_derivative": tree_log_derivative,
        "logdet_directional": logdet_directional,
        "action_score": action_score,
        "effective_score": action_score + logdet_directional,
        "resolvent_gradient": resolvent_gradient,
        "coordinate_resolvent_covector": coordinate_resolvent_covector,
        "inverse_transpose_covector": inverse_transpose_covector,
    }


def verify(certificate: dict | None = None) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if certificate is None:
        with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
            certificate = json.load(handle)
    with open(os.path.join(ROOT, SCHEMA_REL), encoding="utf-8") as handle:
        schema = json.load(handle)
    try:
        jsonschema.Draft202012Validator(schema).validate(certificate)
    except jsonschema.ValidationError as error:
        return False, [f"schema: {error.message}"]

    exact = reconstruct()
    fixture = certificate["exact_cycle_fixture"]

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(
        [dec(value) for value in fixture["omega"]] == exact["omega"],
        "omega drift",
    )
    require(
        [dec(value) for value in fixture["direction"]] == exact["direction"],
        "direction drift",
    )
    require(
        [dec(value) for value in fixture["residual"]] == exact["residual"],
        "residual drift",
    )
    require(
        [[dec(value) for value in row]
         for row in fixture["flat_coordinate_jacobian"]]
        == exact["coordinate"],
        "coordinate Jacobian drift",
    )
    require(
        [[dec(value) for value in row]
         for row in fixture["flat_coordinate_jacobian_directional_derivative"]]
        == exact["coordinate_directional"],
        "directional Jacobian drift",
    )
    require(
        dec(fixture["oriented_jacobian_determinant"])
        == exact["oriented_determinant"]
        == Fraction(-125, 4),
        "oriented determinant drift",
    )
    require(
        dec(fixture["pseudodeterminant"])
        == exact["pseudodeterminant"]
        == abs(exact["oriented_determinant"]),
        "pseudodeterminant drift",
    )
    require(
        [dec(value) for value in fixture["induced_vector"]]
        == exact["induced"],
        "induced vector drift",
    )
    require(
        exact["norm_log_derivative"] == Fraction(-24, 25)
        and exact["tree_log_derivative"] == Fraction(-3, 10),
        "independent norm/tree derivative split failed",
    )
    require(
        dec(fixture["piola_divergence"])
        == dec(fixture["log_pseudodeterminant_directional_derivative"])
        == exact["logdet_directional"]
        == Fraction(-63, 50),
        "Piola/log-determinant derivative drift",
    )
    require(
        dec(fixture["action_score"])
        == exact["action_score"]
        == Fraction(-75, 16),
        "action score drift",
    )
    require(
        dec(fixture["effective_potential_directional_derivative"])
        == exact["effective_score"],
        "effective score drift",
    )
    require(
        dec(fixture["effective_minus_divergence"])
        == exact["effective_score"] - exact["logdet_directional"]
        == exact["action_score"],
        "pointwise cancellation drift",
    )
    require(
        exact["coordinate_resolvent_covector"]
        == exact["inverse_transpose_covector"],
        "resolvent/inverse-transpose interface failed",
    )
    require(
        exact["resolvent_gradient"]
        == [Fraction(-9, 25), Fraction(9, 25), Fraction(1, 25), Fraction(-1, 25)]
        and sum(exact["resolvent_gradient"], Fraction(0)) == 0,
        "ground-state resolvent gradient drift",
    )

    piola = certificate["piola_ward_theorem"]
    resolvent = certificate["ground_state_resolvent_interface"]
    disposition = certificate["method_disposition"]
    require("E[X_h dot grad_u f]" in piola["integrated_identity"], "Ward identity missing")
    require("K^+" in resolvent["potential_gradient"], "resolvent formula missing")
    require(
        disposition["induced_determinant_ward_as_new_estimate"]
        == "OBSTRUCTED_BY_EXACT_CANCELLATION",
        "method obstruction weakened",
    )
    require(
        disposition["noninduced_determinant_resolvent_stein_estimate"] == "OPEN"
        and disposition["actual_interacting_h_minus_one_second_moment"] == "OPEN",
        "open estimate promoted",
    )
    require(
        disposition["born_rule"] == "NOT_ESTABLISHED"
        and disposition["krein_reconstruction"] == "NOT_ASSESSED"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED",
        "reconstruction boundary weakened",
    )
    for item in certificate["provenance"]["inputs"]:
        require(item["sha256"] == sha256(item["path"]), f"hash drift: {item['path']}")
    return not failures, failures


def main() -> int:
    ok, failures = verify()
    if not ok:
        for failure in failures:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1
    print("BT flat-potential Piola/Ward independent verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
