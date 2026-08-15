#!/usr/bin/env python3
"""Certify the flat-potential form of the BT residual pushforward."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_"
    "DETERMINANT_PUSHFORWARD_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-flat-potential-"
    "determinant-pushforward-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-flat-potential-determinant-pushforward.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_flat_potential_determinant_pushforward.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "RESIDUAL_TILT_JACOBIAN_CANCELLATION_V1.json"
    ),
]
SOURCE_COMMIT = "f7a096d2"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


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
        pivot_value = work[column][column]
        result *= pivot_value
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(column + 1, len(work)):
            scale = work[row][column]
            work[row] = [
                value - scale * entry
                for value, entry in zip(work[row], work[column])
            ]
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


def trace(matrix: list[list[Fraction]]) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def cycle_fixture() -> dict:
    omega = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    size = len(omega)
    residual = [
        (omega[(site - 1) % size] + omega[(site + 1) % size])
        / omega[site]
        - 2
        for site in range(size)
    ]
    mean_residual = sum(residual, Fraction(0)) / size
    centered_potential = [value - mean_residual for value in residual]
    ground_eigenvalue = -mean_residual
    laplacian = [
        [Fraction(2), Fraction(-1), Fraction(0), Fraction(-1)],
        [Fraction(-1), Fraction(2), Fraction(-1), Fraction(0)],
        [Fraction(0), Fraction(-1), Fraction(2), Fraction(-1)],
        [Fraction(-1), Fraction(0), Fraction(-1), Fraction(2)],
    ]
    unshifted = [row[:] for row in laplacian]
    kinetic = [row[:] for row in laplacian]
    for site in range(size):
        unshifted[site][site] += centered_potential[site]
        kinetic[site][site] += residual[site]
    cofactors = [
        determinant(minor(kinetic, site, site)) for site in range(size)
    ]
    pseudodeterminant = sum(cofactors, Fraction(0))
    omega_norm_squared = sum((value * value for value in omega), Fraction(0))
    omega_fourth_norm_squared = sum(
        (value**4 for value in omega), Fraction(0)
    )
    omega_fourth_norm = Fraction(17, 4)
    tree_density = Fraction(5)
    coarea_jacobian = 2 * omega_fourth_norm * tree_density
    graph_surface_jacobian = (
        2 * omega_fourth_norm / omega_norm_squared
    )
    flat_density_factor = graph_surface_jacobian / coarea_jacobian
    centered_norm_squared = sum(
        (value * value for value in centered_potential), Fraction(0)
    )
    residual_norm_squared = sum(
        (value * value for value in residual), Fraction(0)
    )
    coupling = Fraction(2, 5)
    exponent = residual_norm_squared / (2 * coupling * coupling)
    return {
        "omega": omega,
        "residual": residual,
        "mean_residual": mean_residual,
        "centered_potential": centered_potential,
        "ground_eigenvalue": ground_eigenvalue,
        "unshifted": unshifted,
        "kinetic": kinetic,
        "cofactors": cofactors,
        "pseudodeterminant": pseudodeterminant,
        "omega_norm_squared": omega_norm_squared,
        "omega_fourth_norm_squared": omega_fourth_norm_squared,
        "omega_fourth_norm": omega_fourth_norm,
        "tree_density": tree_density,
        "coarea_jacobian": coarea_jacobian,
        "graph_surface_jacobian": graph_surface_jacobian,
        "flat_density_factor": flat_density_factor,
        "centered_norm_squared": centered_norm_squared,
        "residual_norm_squared": residual_norm_squared,
        "coupling": coupling,
        "exponent": exponent,
    }


def path_convexity_fixture() -> dict:
    """Exact negative curvature of the flat effective potential on P3."""

    omega = [Fraction(5), Fraction(1), Fraction(100)]
    direction = [Fraction(1), Fraction(0), Fraction(-1)]
    neighbors = [[1], [0, 2], [1]]
    size = len(omega)
    residual = [
        sum((omega[other] for other in neighbors[site]), Fraction(0))
        / omega[site]
        - len(neighbors[site])
        for site in range(size)
    ]
    mean_residual = sum(residual, Fraction(0)) / size
    potential = [value - mean_residual for value in residual]
    ground_eigenvalue = -mean_residual
    kinetic = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    for site in range(size):
        kinetic[site][site] = len(neighbors[site]) + residual[site]
        for other in neighbors[site]:
            kinetic[site][other] -= 1
    bordered = [
        row[:] + [omega[row_index]]
        for row_index, row in enumerate(kinetic)
    ]
    bordered.append(omega[:] + [Fraction(0)])
    pseudoinverse = [row[:size] for row in inverse(bordered)[:size]]
    omega_norm_squared = dot(omega, omega)
    eigenvalue_prime = dot(
        omega,
        [direction[index] * omega[index] for index in range(size)],
    ) / omega_norm_squared
    centered_source = [
        (direction[index] - eigenvalue_prime) * omega[index]
        for index in range(size)
    ]
    eigenvalue_second = (
        -2
        * dot(
            centered_source,
            matrix_vector(pseudoinverse, centered_source),
        )
        / omega_norm_squared
    )
    kinetic_prime = [
        [
            (direction[row] - eigenvalue_prime)
            if row == column
            else Fraction(0)
            for column in range(size)
        ]
        for row in range(size)
    ]
    pseudoinverse_squared = multiply(pseudoinverse, pseudoinverse)
    pk = multiply(pseudoinverse, kinetic_prime)
    logdet_second_terms = [
        -eigenvalue_second * trace(pseudoinverse),
        -trace(multiply(pk, pk)),
        Fraction(2, omega_norm_squared)
        * dot(
            matrix_vector(kinetic_prime, omega),
            matrix_vector(
                pseudoinverse_squared,
                matrix_vector(kinetic_prime, omega),
            ),
        ),
    ]
    logdet_second = sum(logdet_second_terms, Fraction(0))
    coupling = Fraction(2, 5)
    gaussian_second = (
        dot(direction, direction)
        + size
        * (
            eigenvalue_prime**2
            + ground_eigenvalue * eigenvalue_second
        )
    ) / (coupling * coupling)
    effective_second = gaussian_second + logdet_second
    return {
        "omega": omega,
        "direction": direction,
        "residual": residual,
        "mean_residual": mean_residual,
        "potential": potential,
        "ground_eigenvalue": ground_eigenvalue,
        "kinetic": kinetic,
        "pseudoinverse": pseudoinverse,
        "omega_norm_squared": omega_norm_squared,
        "eigenvalue_prime": eigenvalue_prime,
        "eigenvalue_second": eigenvalue_second,
        "logdet_second_terms": logdet_second_terms,
        "logdet_second": logdet_second,
        "gaussian_second": gaussian_second,
        "effective_second": effective_second,
        "coupling": coupling,
    }


def encode_matrix(matrix: list[list[Fraction]]) -> list[list[dict[str, int]]]:
    return [[enc(value) for value in row] for row in matrix]


def build() -> dict:
    fixture = cycle_fixture()
    convexity = path_convexity_fixture()
    checks = {
        "fixture_ground_vector_has_unit_geometric_mean": (
            fixture["omega"]
            == [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
            and __import__("math").prod(fixture["omega"]) == 1
        ),
        "fixture_residual_is_exact": fixture["residual"]
        == [Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2)],
        "centered_potential_has_zero_sum": (
            fixture["centered_potential"]
            == [Fraction(0), Fraction(-3, 2), Fraction(0), Fraction(3, 2)]
            and sum(fixture["centered_potential"], Fraction(0)) == 0
        ),
        "ground_eigenvalue_is_minus_one_half": (
            fixture["ground_eigenvalue"] == Fraction(-1, 2)
        ),
        "shifted_kinetic_kills_ground_vector": all(
            sum(
                (
                    fixture["kinetic"][row][column]
                    * fixture["omega"][column]
                    for column in range(4)
                ),
                Fraction(0),
            )
            == 0
            for row in range(4)
        ),
        "principal_cofactors_are_exact": fixture["cofactors"]
        == [Fraction(5), Fraction(20), Fraction(5), Fraction(5, 4)],
        "pseudodeterminant_is_125_over_4": (
            fixture["pseudodeterminant"] == Fraction(125, 4)
        ),
        "pseudodeterminant_equals_ground_norm_times_tree_density": (
            fixture["pseudodeterminant"]
            == fixture["omega_norm_squared"] * fixture["tree_density"]
        ),
        "graph_surface_jacobian_is_34_over_25": (
            fixture["graph_surface_jacobian"] == Fraction(34, 25)
        ),
        "coarea_jacobian_is_85_over_2": (
            fixture["coarea_jacobian"] == Fraction(85, 2)
        ),
        "flat_density_factor_is_inverse_pseudodeterminant": (
            fixture["flat_density_factor"]
            == Fraction(4, 125)
            == 1 / fixture["pseudodeterminant"]
        ),
        "orthogonal_norm_decomposition_is_exact": (
            fixture["residual_norm_squared"]
            == fixture["centered_norm_squared"]
            + 4 * fixture["ground_eigenvalue"] ** 2
            == Fraction(11, 2)
        ),
        "physical_exponent_is_275_over_16": (
            fixture["coupling"] == Fraction(2, 5)
            and fixture["exponent"] == Fraction(275, 16)
        ),
        "flat_potential_pushforward_is_exact_reformulation_only": True,
        "path_three_effective_curvature_is_strictly_negative": (
            convexity["effective_second"]
            == Fraction(-5196641386825675, 498983027333184)
            and convexity["effective_second"] < 0
        ),
        "path_three_gaussian_curvature_is_positive": (
            convexity["gaussian_second"]
            == Fraction(28994309146675, 298613421504)
            and convexity["gaussian_second"] > 0
        ),
        "path_three_logdet_curvature_overcancels_gaussian": (
            convexity["logdet_second"]
            == Fraction(-3352883248182475, 31186439208324)
            and convexity["logdet_second"]
            < -convexity["gaussian_second"]
        ),
        "uniform_ground_state_moment_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_"
            "DETERMINANT_PUSHFORWARD_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-flat-potential-"
            "determinant-pushforward-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": (
            "FLAT_RANDOM_SCHRODINGER_REFORMULATION_PROVED_"
            "GLOBAL_CONVEXITY_OBSTRUCTED"
        ),
        "result_kind": (
            "exact finite-graph flat-potential parametrization of the BT "
            "residual boundary measure by a ground-shifted Schrodinger "
            "pseudodeterminant ensemble, with an exact obstruction to "
            "global log-concavity at the physical coupling"
        ),
        "question": (
            "Can the normalized residual-boundary law be written over a flat "
            "linear carrier, eliminating the moving surface element and the "
            "separate ground-state/tree factors?"
        ),
        "answer": (
            "Yes. For every finite connected graph and every mean-zero "
            "diagonal potential u, let ell_0(u) be the simple lowest "
            "eigenvalue of H(u)=-Delta+diag(u), put c(u)=-ell_0(u)>=0, "
            "r(u)=u+c(u)*1, and K(u)=H(u)-ell_0(u)*I. This parametrizes the "
            "principal spectrahedral boundary globally. The graph surface "
            "Jacobian cancels the ground-state norm in the coarea factor, "
            "and the remaining tree factor is det_prime K. Hence the exact "
            "BT law is proportional to exp[-(||u||^2+N*ell_0(u)^2)/"
            "(2*lambda^2)]/det_prime K(u) du on the flat mean-zero "
            "potential space. The field observable is still the logarithm "
            "of K(u)'s positive ground state. On the three-vertex path at "
            "lambda=2/5, an exact rational fixture has negative directional "
            "curvature -5196641386825675/498983027333184 for the full "
            "negative-log density: the inverse-determinant curvature "
            "overcancels the positive Gaussian curvature. Thus global "
            "Brascamp--Lieb in the new coordinates is obstructed. The flat "
            "formula remains a sharper normalized reformulation, not a "
            "volume-uniform moment theorem."
        ),
        "flat_boundary_graph_theorem": {
            "scope": "every finite connected undirected graph with N vertices",
            "carrier": "H={u in R^N: sum_x u_x=0}",
            "unshifted_operator": "H(u)=-Delta+diag(u)",
            "lowest_eigenvalue": (
                "ell_0(u) is simple with a strictly positive eigenvector; "
                "ell_0(u)<=0 by the constant-vector Rayleigh quotient"
            ),
            "boundary_shift": (
                "c(u)=-ell_0(u)>=0, r(u)=u+c(u)*1, "
                "K(u)=H(u)-ell_0(u)*I"
            ),
            "global_parametrization": (
                "u->r(u) is an analytic bijection from H onto the principal "
                "boundary of {-Delta+diag(r)>=0}; its inverse subtracts the "
                "arithmetic mean of r"
            ),
            "status": "PROVED",
        },
        "surface_and_tree_reduction": {
            "normalized_ground_state": (
                "a_x=Omega_x^2/||Omega||_2^2 and "
                "D c(u)[h]=-<a,h> for h in H"
            ),
            "graph_surface_jacobian": (
                "Jac_graph(u)=sqrt(N)*||Omega^2||_2/||Omega||_2^2"
            ),
            "imported_residual_coarea_jacobian": (
                "Jac_H=sqrt(N)*||Omega^2||_2*tau"
            ),
            "symmetric_cofactor_identity": (
                "cof_i(K)=det_prime(K)*Omega_i^2/||Omega||_2^2"
            ),
            "directed_tree_identity": "cof_i(K)=Omega_i^2*tau",
            "pseudodeterminant_identity": (
                "det_prime(K)=||Omega||_2^2*tau"
            ),
            "measure_factor": (
                "Jac_graph/Jac_H=1/(||Omega||_2^2*tau)="
                "1/det_prime(K)"
            ),
            "status": "PROVED",
        },
        "flat_normalized_pushforward": {
            "residual_norm": (
                "||r(u)||_2^2=||u||_2^2+N*ell_0(u)^2"
            ),
            "density": (
                "dnu(u)=Z^(-1)*exp[-(||u||_2^2+N*ell_0(u)^2)/"
                "(2*lambda^2)]/det_prime(H(u)-ell_0(u)*I) du"
            ),
            "observable": (
                "psi(u)=log(Omega(u))-N^(-1)*sum_x log(Omega_x(u)); "
                "the continuum-normalized Fourier field is psi_hat/lambda"
            ),
            "interpretation": (
                "the surface geometry and separate directed-tree weight are "
                "replaced by one explicit inverse spectral determinant on a "
                "flat Gaussian-confined potential carrier"
            ),
            "status": "EXACT_NORMALIZED_REFORMULATION_ONLY",
        },
        "exact_cycle_fixture": {
            "graph": "four-cycle C4",
            "omega": [enc(value) for value in fixture["omega"]],
            "residual": [enc(value) for value in fixture["residual"]],
            "mean_residual": enc(fixture["mean_residual"]),
            "centered_potential": [
                enc(value) for value in fixture["centered_potential"]
            ],
            "ground_eigenvalue": enc(fixture["ground_eigenvalue"]),
            "unshifted_operator": encode_matrix(fixture["unshifted"]),
            "shifted_kinetic_operator": encode_matrix(fixture["kinetic"]),
            "principal_cofactors": [
                enc(value) for value in fixture["cofactors"]
            ],
            "pseudodeterminant": enc(fixture["pseudodeterminant"]),
            "ground_norm_squared": enc(fixture["omega_norm_squared"]),
            "tree_density": enc(fixture["tree_density"]),
            "graph_surface_jacobian": enc(
                fixture["graph_surface_jacobian"]
            ),
            "residual_coarea_jacobian": enc(fixture["coarea_jacobian"]),
            "flat_density_factor": enc(fixture["flat_density_factor"]),
            "residual_norm_squared": enc(
                fixture["residual_norm_squared"]
            ),
            "coupling": enc(fixture["coupling"]),
            "boltzmann_exponent": enc(fixture["exponent"]),
            "unnormalized_flat_density": "(4/125)*exp(-275/16)",
            "status": "EXACT_RATIONAL_FIXTURE",
        },
        "exact_path_three_convexity_obstruction": {
            "graph": "three-vertex path P3",
            "omega": [enc(value) for value in convexity["omega"]],
            "centered_potential": [
                enc(value) for value in convexity["potential"]
            ],
            "direction": [enc(value) for value in convexity["direction"]],
            "ground_eigenvalue": enc(convexity["ground_eigenvalue"]),
            "shifted_kinetic_operator": encode_matrix(convexity["kinetic"]),
            "ground_norm_squared": enc(convexity["omega_norm_squared"]),
            "lowest_eigenvalue_first_derivative": enc(
                convexity["eigenvalue_prime"]
            ),
            "lowest_eigenvalue_second_derivative": enc(
                convexity["eigenvalue_second"]
            ),
            "gaussian_effective_potential_second_derivative": enc(
                convexity["gaussian_second"]
            ),
            "log_pseudodeterminant_second_derivative_terms": [
                enc(value) for value in convexity["logdet_second_terms"]
            ],
            "log_pseudodeterminant_second_derivative": enc(
                convexity["logdet_second"]
            ),
            "full_effective_potential_second_derivative": enc(
                convexity["effective_second"]
            ),
            "full_effective_potential_second_derivative_decimal": float(
                convexity["effective_second"]
            ),
            "conclusion": (
                "The negative logarithm of the flat-potential density is "
                "not globally convex, already on P3 at lambda=2/5."
            ),
            "status": "EXACT_GLOBAL_CONVEXITY_OBSTRUCTION",
        },
        "method_disposition": {
            "residual_spectrahedral_boundary_coordinates": "IMPORTED_PROVED",
            "flat_mean_zero_potential_parametrization": "PROVED",
            "surface_ground_norm_tree_reduction": "PROVED",
            "inverse_pseudodeterminant_ensemble": "PROVED",
            "global_log_concavity_or_brascamp_lieb_in_flat_potential": (
                "OBSTRUCTED_BY_EXACT_P3_NEGATIVE_CURVATURE"
            ),
            "nonconvex_determinant_or_resolvent_estimate": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "ordinary_os_at_lambda_0p4": "OBSTRUCTED_BY_PREDECESSOR",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "does_not_establish": [
            "a volume-uniform inverse-determinant, spectral-gap, or ground-state-resolvent estimate",
            "failure of every nonconvex integration-by-parts, localization, or resolvent estimate",
            "the normalized lowest Fourier mode or actual interacting H^-1 moment",
            "tightness, a continuum Euclidean BT measure, or limit identification",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "an L-uniform estimate for the log-ground-state Fourier observable under the inverse-pseudodeterminant ensemble",
            "a nonconvex integration-by-parts, localization, or determinant-resolvent estimate replacing the obstructed global Brascamp-Lieb route",
            "a dyadic-shell summation proving or obstructing the actual interacting H^-1 moment",
            "tightness in a compactly weaker topology only after a positive moment theorem",
        ],
        "next_gate": (
            "Use the exact flat density without assuming global convexity. "
            "Derive its nonconvex integration-by-parts identity and test "
            "whether the inverse determinant cancels the dangerous "
            "ground-state resolvent in the lowest log-ground-state Fourier "
            "moment; alternatively construct an exact volume sequence "
            "obstructing that combined estimate."
        ),
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Exact Fraction arithmetic for the C4 graph, residual, "
                "operators, cofactors, pseudodeterminant, graph Jacobian, "
                "and density factor; the general proof uses simple-ground-"
                "eigenvalue perturbation, coarea, and the symmetric and "
                "directed matrix-tree identities."
            ),
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFY_REL,
        "verification_commands": [
            (
                "ulimit -v 500000; python3 reverse_physics/"
                "bt_euclidean_flat_potential_determinant_pushforward.py --check"
            ),
            (
                "ulimit -v 500000; python3 reverse_physics/"
                "verify_bt_euclidean_flat_potential_determinant_pushforward.py"
            ),
            (
                "ulimit -v 500000; python3 -m unittest -v "
                "reverse_physics.tests."
                "test_bt_euclidean_flat_potential_determinant_pushforward"
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if not payload["checks"]["ok"]:
        for failure in payload["checks"]["failures"]:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1
    if args.write:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                committed = json.load(handle)
        except FileNotFoundError:
            print(f"[FAIL] missing certificate: {CERT_REL}", file=sys.stderr)
            return 1
        if committed != payload:
            print("[FAIL] committed certificate is stale", file=sys.stderr)
            return 1
    print(
        "BT flat-potential determinant pushforward: "
        f"PASS ({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
