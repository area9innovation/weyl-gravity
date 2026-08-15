#!/usr/bin/env python3
"""Independent verifier for the flat-potential BT pushforward."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_"
    "DETERMINANT_PUSHFORWARD_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-flat-potential-"
    "determinant-pushforward-v1.schema.json"
)


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


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
        for entry in range(column, len(work)):
            work[column][entry] /= value
        for row in range(column + 1, len(work)):
            scale = work[row][column]
            for entry in range(column, len(work)):
                work[row][entry] -= scale * work[column][entry]
    return result


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


def generic_fixture(
    neighbors: list[list[int]], omega: list[Fraction]
) -> dict[str, bool]:
    """Reconstruct the theorem on an undeclared exact connected graph."""

    size = len(omega)
    residual = [
        sum((omega[other] for other in neighbors[site]), Fraction(0))
        / omega[site]
        - len(neighbors[site])
        for site in range(size)
    ]
    mean = sum(residual, Fraction(0)) / size
    potential = [value - mean for value in residual]
    kinetic = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    unshifted = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    for site in range(size):
        kinetic[site][site] = len(neighbors[site]) + residual[site]
        unshifted[site][site] = len(neighbors[site]) + potential[site]
        for other in neighbors[site]:
            kinetic[site][other] -= 1
            unshifted[site][other] -= 1
    cofactors = [
        determinant(minor(kinetic, site, site)) for site in range(size)
    ]
    tau_roots = [
        cofactors[site] / (omega[site] * omega[site])
        for site in range(size)
    ]
    pseudodeterminant = sum(cofactors, Fraction(0))
    omega_norm_squared = sum((value * value for value in omega), Fraction(0))

    basis = [
        [
            Fraction(int(row == column)) - Fraction(int(row == size - 1))
            for column in range(size - 1)
        ]
        for row in range(size)
    ]
    probability = [value * value / omega_norm_squared for value in omega]
    image_basis = []
    for column in range(size - 1):
        direction = [basis[row][column] for row in range(size)]
        dc = -sum(
            (probability[row] * direction[row] for row in range(size)),
            Fraction(0),
        )
        image_basis.append([value + dc for value in direction])
    image_basis_matrix = [list(row) for row in zip(*image_basis)]
    domain_gram = multiply(transpose(basis), basis)
    image_gram = multiply(
        transpose(image_basis_matrix), image_basis_matrix
    )
    graph_jacobian_squared = determinant(image_gram) / determinant(domain_gram)
    expected_graph_jacobian_squared = (
        size
        * sum((value**4 for value in omega), Fraction(0))
        / (omega_norm_squared * omega_norm_squared)
    )
    return {
        "kinetic_kills_ground": all(
            sum(
                (kinetic[row][column] * omega[column]
                 for column in range(size)),
                Fraction(0),
            )
            == 0
            for row in range(size)
        ),
        "unshifted_has_declared_ground_eigenpair": all(
            sum(
                (unshifted[row][column] * omega[column]
                 for column in range(size)),
                Fraction(0),
            )
            == -mean * omega[row]
            for row in range(size)
        ),
        "rooted_tree_densities_agree": all(
            value == tau_roots[0] for value in tau_roots
        ),
        "pseudodeterminant_tree_identity": (
            pseudodeterminant == omega_norm_squared * tau_roots[0]
        ),
        "surface_gram_identity": (
            graph_jacobian_squared == expected_graph_jacobian_squared
        ),
    }


def poly_add(
    left: dict[tuple[int, int], Fraction],
    right: dict[tuple[int, int], Fraction],
) -> dict[tuple[int, int], Fraction]:
    result = left.copy()
    for key, value in right.items():
        result[key] = result.get(key, Fraction(0)) + value
        if not result[key]:
            del result[key]
    return result


def poly_multiply(
    left: dict[tuple[int, int], Fraction],
    right: dict[tuple[int, int], Fraction],
) -> dict[tuple[int, int], Fraction]:
    result: dict[tuple[int, int], Fraction] = {}
    for (lt, lz), left_value in left.items():
        for (rt, rz), right_value in right.items():
            key = (lt + rt, lz + rz)
            result[key] = result.get(key, Fraction(0)) + left_value * right_value
    return {key: value for key, value in result.items() if value}


def permutation_sign(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def characteristic_polynomial(
    matrix: list[list[Fraction]], direction: list[Fraction]
) -> dict[tuple[int, int], Fraction]:
    """Return det(matrix+t*diag(direction)-z*I) in (t,z)."""

    size = len(matrix)
    result: dict[tuple[int, int], Fraction] = {}
    for permutation in itertools.permutations(range(size)):
        term = {(0, 0): Fraction(permutation_sign(permutation))}
        for row, column in enumerate(permutation):
            entry = {(0, 0): matrix[row][column]}
            if row == column:
                entry[(1, 0)] = direction[row]
                entry[(0, 1)] = Fraction(-1)
            term = poly_multiply(term, entry)
        result = poly_add(result, term)
    return result


def partial(
    polynomial: dict[tuple[int, int], Fraction],
    dt: int,
    dz: int,
    t: Fraction,
    z: Fraction,
) -> Fraction:
    result = Fraction(0)
    for (power_t, power_z), coefficient in polynomial.items():
        if power_t < dt or power_z < dz:
            continue
        factor = coefficient
        for offset in range(dt):
            factor *= power_t - offset
        for offset in range(dz):
            factor *= power_z - offset
        factor *= t ** (power_t - dt)
        factor *= z ** (power_z - dz)
        result += factor
    return result


def reconstruct_path_curvature() -> dict[str, Fraction | list[Fraction]]:
    """Implicit characteristic-polynomial jet, independent of K-plus."""

    omega = [Fraction(5), Fraction(1), Fraction(100)]
    direction = [Fraction(1), Fraction(0), Fraction(-1)]
    residual = [Fraction(-4, 5), Fraction(103), Fraction(-99, 100)]
    mean = sum(residual, Fraction(0)) / 3
    potential = [value - mean for value in residual]
    ground_eigenvalue = -mean
    graph_laplacian = [
        [Fraction(1), Fraction(-1), Fraction(0)],
        [Fraction(-1), Fraction(2), Fraction(-1)],
        [Fraction(0), Fraction(-1), Fraction(1)],
    ]
    unshifted = [row[:] for row in graph_laplacian]
    for index in range(3):
        unshifted[index][index] += potential[index]
    polynomial = characteristic_polynomial(unshifted, direction)
    zero = Fraction(0)
    p_z = partial(polynomial, 0, 1, zero, ground_eigenvalue)
    p_t = partial(polynomial, 1, 0, zero, ground_eigenvalue)
    p_tt = partial(polynomial, 2, 0, zero, ground_eigenvalue)
    p_tz = partial(polynomial, 1, 1, zero, ground_eigenvalue)
    p_zz = partial(polynomial, 0, 2, zero, ground_eigenvalue)
    eigenvalue_prime = -p_t / p_z
    eigenvalue_second = -(
        p_tt
        + 2 * p_tz * eigenvalue_prime
        + p_zz * eigenvalue_prime**2
    ) / p_z

    determinant_value = -p_z
    determinant_prime = -(
        p_tz + p_zz * eigenvalue_prime
    )
    determinant_second = -(
        partial(polynomial, 2, 1, zero, ground_eigenvalue)
        + 2
        * partial(polynomial, 1, 2, zero, ground_eigenvalue)
        * eigenvalue_prime
        + partial(polynomial, 0, 3, zero, ground_eigenvalue)
        * eigenvalue_prime**2
        + p_zz * eigenvalue_second
    )
    logdet_second = (
        determinant_second / determinant_value
        - (determinant_prime / determinant_value) ** 2
    )
    omega_norm_squared = sum((value * value for value in omega), Fraction(0))
    # Hellmann--Feynman is checked against the implicit derivative.
    hellmann_prime = sum(
        (direction[index] * omega[index] ** 2 for index in range(3)),
        Fraction(0),
    ) / omega_norm_squared
    gaussian_second = (
        sum((value * value for value in direction), Fraction(0))
        + 3
        * (
            eigenvalue_prime**2
            + ground_eigenvalue * eigenvalue_second
        )
    ) / Fraction(4, 25)
    return {
        "omega": omega,
        "direction": direction,
        "potential": potential,
        "ground_eigenvalue": ground_eigenvalue,
        "eigenvalue_prime": eigenvalue_prime,
        "hellmann_prime": hellmann_prime,
        "eigenvalue_second": eigenvalue_second,
        "logdet_second": logdet_second,
        "gaussian_second": gaussian_second,
        "effective_second": gaussian_second + logdet_second,
    }


def reconstruct() -> dict:
    omega = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    residual = [
        (omega[(site - 1) % 4] + omega[(site + 1) % 4]) / omega[site] - 2
        for site in range(4)
    ]
    mean = sum(residual, Fraction(0)) / 4
    potential = [value - mean for value in residual]
    graph_laplacian = [
        [Fraction(2), Fraction(-1), Fraction(0), Fraction(-1)],
        [Fraction(-1), Fraction(2), Fraction(-1), Fraction(0)],
        [Fraction(0), Fraction(-1), Fraction(2), Fraction(-1)],
        [Fraction(-1), Fraction(0), Fraction(-1), Fraction(2)],
    ]
    unshifted = [row[:] for row in graph_laplacian]
    kinetic = [row[:] for row in graph_laplacian]
    for site in range(4):
        unshifted[site][site] += potential[site]
        kinetic[site][site] += residual[site]
    cofactors = [
        determinant(minor(kinetic, site, site)) for site in range(4)
    ]
    pseudodeterminant = sum(cofactors, Fraction(0))
    ground_norm_squared = sum((value * value for value in omega), Fraction(0))
    omega_fourth_norm_squared = sum((value**4 for value in omega), Fraction(0))
    omega_fourth_norm = Fraction(17, 4)
    edge_products = [omega[site] * omega[(site + 1) % 4] for site in range(4)]
    all_edges = __import__("math").prod(edge_products)
    tree_density = sum(
        (all_edges / edge for edge in edge_products), Fraction(0)
    )
    surface_jacobian = 2 * omega_fourth_norm / ground_norm_squared
    coarea_jacobian = 2 * omega_fourth_norm * tree_density
    residual_norm_squared = sum((value * value for value in residual), Fraction(0))
    centered_norm_squared = sum((value * value for value in potential), Fraction(0))
    return {
        "omega": omega,
        "residual": residual,
        "mean": mean,
        "potential": potential,
        "ground_eigenvalue": -mean,
        "unshifted": unshifted,
        "kinetic": kinetic,
        "cofactors": cofactors,
        "pseudodeterminant": pseudodeterminant,
        "ground_norm_squared": ground_norm_squared,
        "omega_fourth_norm_squared": omega_fourth_norm_squared,
        "tree_density": tree_density,
        "surface_jacobian": surface_jacobian,
        "coarea_jacobian": coarea_jacobian,
        "flat_factor": surface_jacobian / coarea_jacobian,
        "residual_norm_squared": residual_norm_squared,
        "centered_norm_squared": centered_norm_squared,
        "exponent": residual_norm_squared / (2 * Fraction(2, 5) ** 2),
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
        failures.append(f"schema: {error.message}")
        return False, failures

    exact = reconstruct()
    fixture = certificate["exact_cycle_fixture"]

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(
        [dec(value) for value in fixture["omega"]] == exact["omega"],
        "ground vector drift",
    )
    require(
        [dec(value) for value in fixture["residual"]] == exact["residual"],
        "residual drift",
    )
    require(dec(fixture["mean_residual"]) == exact["mean"], "mean drift")
    require(
        [dec(value) for value in fixture["centered_potential"]]
        == exact["potential"],
        "centered potential drift",
    )
    require(
        dec(fixture["ground_eigenvalue"]) == exact["ground_eigenvalue"],
        "ground eigenvalue drift",
    )
    require(
        [[dec(value) for value in row] for row in fixture["unshifted_operator"]]
        == exact["unshifted"],
        "unshifted operator drift",
    )
    require(
        [
            [dec(value) for value in row]
            for row in fixture["shifted_kinetic_operator"]
        ]
        == exact["kinetic"],
        "kinetic operator drift",
    )
    require(
        all(
            sum(
                (exact["kinetic"][row][column] * exact["omega"][column]
                 for column in range(4)),
                Fraction(0),
            )
            == 0
            for row in range(4)
        ),
        "kinetic operator does not kill ground vector",
    )
    require(
        [dec(value) for value in fixture["principal_cofactors"]]
        == exact["cofactors"],
        "principal cofactor drift",
    )
    require(
        dec(fixture["pseudodeterminant"]) == exact["pseudodeterminant"],
        "pseudodeterminant drift",
    )
    require(
        exact["pseudodeterminant"]
        == exact["ground_norm_squared"] * exact["tree_density"],
        "symmetric/directed tree identity failed",
    )
    require(
        dec(fixture["graph_surface_jacobian"])
        == exact["surface_jacobian"],
        "surface graph Jacobian drift",
    )
    require(
        dec(fixture["residual_coarea_jacobian"])
        == exact["coarea_jacobian"],
        "residual coarea Jacobian drift",
    )
    require(
        dec(fixture["flat_density_factor"])
        == exact["flat_factor"]
        == 1 / exact["pseudodeterminant"],
        "flat density factor drift",
    )
    require(
        exact["residual_norm_squared"]
        == exact["centered_norm_squared"]
        + 4 * exact["ground_eigenvalue"] ** 2,
        "orthogonal residual norm decomposition failed",
    )
    require(
        dec(fixture["boltzmann_exponent"]) == exact["exponent"],
        "Boltzmann exponent drift",
    )

    theorem = certificate["flat_boundary_graph_theorem"]
    reduction = certificate["surface_and_tree_reduction"]
    pushforward = certificate["flat_normalized_pushforward"]
    disposition = certificate["method_disposition"]
    convexity = certificate["exact_path_three_convexity_obstruction"]
    require("ell_0(u)<=0" in theorem["lowest_eigenvalue"], "Rayleigh sign missing")
    require("det_prime(K)" in reduction["measure_factor"], "determinant factor missing")
    require("det_prime" in pushforward["density"], "flat density formula missing")
    require(
        disposition["global_log_concavity_or_brascamp_lieb_in_flat_potential"]
        == "OBSTRUCTED_BY_EXACT_P3_NEGATIVE_CURVATURE",
        "flat convexity obstruction weakened",
    )
    require(
        disposition["nonconvex_determinant_or_resolvent_estimate"] == "OPEN",
        "nonconvex estimate promoted",
    )
    require(
        disposition["actual_interacting_h_minus_one_second_moment"] == "OPEN",
        "H^-1 claim promoted",
    )
    require(
        disposition["born_rule"] == "NOT_ESTABLISHED"
        and disposition["krein_reconstruction"] == "NOT_ASSESSED"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED",
        "reconstruction boundary weakened",
    )
    path = reconstruct_path_curvature()
    require(
        [dec(value) for value in convexity["omega"]] == path["omega"],
        "P3 ground vector drift",
    )
    require(
        [dec(value) for value in convexity["centered_potential"]]
        == path["potential"],
        "P3 centered potential drift",
    )
    require(
        [dec(value) for value in convexity["direction"]]
        == path["direction"],
        "P3 direction drift",
    )
    require(
        path["eigenvalue_prime"] == path["hellmann_prime"],
        "implicit and Hellmann--Feynman first derivatives disagree",
    )
    require(
        dec(convexity["lowest_eigenvalue_first_derivative"])
        == path["eigenvalue_prime"],
        "P3 first eigenvalue derivative drift",
    )
    require(
        dec(convexity["lowest_eigenvalue_second_derivative"])
        == path["eigenvalue_second"],
        "P3 second eigenvalue derivative drift",
    )
    require(
        dec(convexity["gaussian_effective_potential_second_derivative"])
        == path["gaussian_second"],
        "P3 Gaussian curvature drift",
    )
    require(
        dec(convexity["log_pseudodeterminant_second_derivative"])
        == path["logdet_second"],
        "P3 log-determinant curvature drift",
    )
    require(
        dec(convexity["full_effective_potential_second_derivative"])
        == path["effective_second"]
        == Fraction(-5196641386825675, 498983027333184),
        "P3 full curvature drift",
    )
    require(path["effective_second"] < 0, "P3 curvature is not negative")
    exact_graphs = [
        generic_fixture(
            [[1], [0, 2], [1]],
            [Fraction(1), Fraction(2), Fraction(3)],
        ),
        generic_fixture(
            [[1, 2], [0, 2], [0, 1]],
            [Fraction(1), Fraction(3, 2), Fraction(2, 3)],
        ),
        generic_fixture(
            [[1, 4], [0, 2], [1, 3], [2, 4], [3, 0]],
            [
                Fraction(1),
                Fraction(2),
                Fraction(3, 2),
                Fraction(4, 3),
                Fraction(3, 4),
            ],
        ),
    ]
    require(
        all(all(row.values()) for row in exact_graphs),
        "undeclared exact graph suite failed",
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
    print("BT flat-potential determinant pushforward verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
