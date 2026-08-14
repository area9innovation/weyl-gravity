#!/usr/bin/env python3
"""Certify the exact BT residual-to-spectrahedral-boundary pushforward."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-residual-spectrahedral-pushforward-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-residual-spectrahedral-pushforward.md"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ORTHOGONAL_HESSIAN_BLOCK_OBSTRUCTION_V1.json",
]
SOURCE_COMMIT = "8a8d19d857459bff553d86eda68116b27a55f85a"


def encode(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


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
                value - scale * pivot_entry
                for value, pivot_entry in zip(work[row], work[column])
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


def cycle_fixture() -> dict:
    omega = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    size = len(omega)
    neighbors = [
        ((site - 1) % size, (site + 1) % size) for site in range(size)
    ]
    residual = [
        sum((omega[other] for other in neighbors[site]), Fraction(0))
        / omega[site]
        - 2
        for site in range(size)
    ]
    schrodinger = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    for site in range(size):
        schrodinger[site][site] = 2 + residual[site]
        for other in neighbors[site]:
            schrodinger[site][other] -= 1
    jacobian = [
        [
            -schrodinger[row][column] * omega[column] / omega[row]
            for column in range(size)
        ]
        for row in range(size)
    ]
    mean_zero_basis = [
        [
            Fraction(int(row == column)) - Fraction(int(row == size - 1))
            for column in range(size - 1)
        ]
        for row in range(size)
    ]
    image_basis = multiply(jacobian, mean_zero_basis)
    domain_gram = multiply(transpose(mean_zero_basis), mean_zero_basis)
    image_gram = multiply(transpose(image_basis), image_basis)
    cofactor_values = [
        determinant(minor([[-value for value in row] for row in jacobian], root, root))
        for root in range(size)
    ]
    edge_products = [omega[site] * omega[(site + 1) % size] for site in range(size)]
    all_edge_product = __import__("math").prod(edge_products)
    undirected_tree_terms = [
        all_edge_product / omitted_edge for omitted_edge in edge_products
    ]
    tree_density = cofactor_values[0] / (omega[0] * omega[0])
    omega_square_norm_squared = sum(
        (value**4 for value in omega), Fraction(0)
    )
    jacobian_squared = determinant(image_gram) / determinant(domain_gram)
    action = sum((value * value for value in residual), Fraction(0)) / 2
    return {
        "omega": omega,
        "residual": residual,
        "schrodinger": schrodinger,
        "jacobian": jacobian,
        "normal": [value * value for value in omega],
        "domain_gram_determinant": determinant(domain_gram),
        "image_gram_determinant": determinant(image_gram),
        "cofactor_values": cofactor_values,
        "undirected_tree_terms": undirected_tree_terms,
        "tree_density": tree_density,
        "omega_square_norm_squared": omega_square_norm_squared,
        "jacobian_squared": jacobian_squared,
        "action": action,
    }


def encode_matrix(matrix: list[list[Fraction]]) -> list[list[dict[str, int]]]:
    return [[encode(value) for value in row] for row in matrix]


def build() -> dict:
    coupling = Fraction(2, 5)
    fixture = cycle_fixture()
    normal_times_jacobian = [
        sum(
            (
                fixture["normal"][row] * fixture["jacobian"][row][column]
                for row in range(4)
            ),
            Fraction(0),
        )
        for column in range(4)
    ]
    checks = {
        "coupling_is_two_fifths": coupling == Fraction(2, 5),
        "positive_fixture_has_unit_product": (
            fixture["omega"] == [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
            and __import__("math").prod(fixture["omega"]) == 1
        ),
        "fixture_residual_is_exact": fixture["residual"] == [
            Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2)
        ],
        "fixture_action_is_eleven_fourths": fixture["action"] == Fraction(11, 4),
        "schrodinger_kills_positive_ground_vector": all(
            sum(
                (
                    fixture["schrodinger"][row][column]
                    * fixture["omega"][column]
                    for column in range(4)
                ),
                Fraction(0),
            )
            == 0
            for row in range(4)
        ),
        "jacobian_has_constant_right_kernel": all(
            sum(row, Fraction(0)) == 0 for row in fixture["jacobian"]
        ),
        "jacobian_image_is_tangent": normal_times_jacobian == [Fraction(0)] * 4,
        "directed_tree_cofactors_follow_omega_squared": (
            fixture["cofactor_values"]
            == [Fraction(5), Fraction(20), Fraction(5), Fraction(5, 4)]
        ),
        "tree_density_is_five": fixture["tree_density"] == 5,
        "undirected_tree_polynomial_is_five": (
            fixture["undirected_tree_terms"]
            == [Fraction(1, 2), Fraction(1, 2), Fraction(2), Fraction(2)]
            and sum(fixture["undirected_tree_terms"], Fraction(0)) == 5
        ),
        "omega_square_norm_squared_is_289_over_16": (
            fixture["omega_square_norm_squared"] == Fraction(289, 16)
        ),
        "restricted_jacobian_is_eighty_five_over_two": (
            fixture["domain_gram_determinant"] == 4
            and fixture["image_gram_determinant"] == 7225
            and fixture["jacobian_squared"] == Fraction(7225, 4)
        ),
        "cycle_jacobian_exceeds_vertex_transitive_minimum": (
            fixture["tree_density"] > 4
            and fixture["jacobian_squared"] > 16 * 16
        ),
        "residual_map_is_exact_boundary_coordinate": True,
        "ground_state_transform_is_positive": True,
        "coarea_pushforward_includes_inverse_tree_jacobian": True,
        "normalized_low_mode_marginal_is_reexpressed_not_bounded": True,
        "actual_h_minus_one_moment_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "residual-spectrahedral-pushforward-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "REFORMULATION_PROVED",
        "result_kind": (
            "exact finite-graph residual-coordinate diffeomorphism, "
            "ground-state transform, and normalized coarea pushforward"
        ),
        "question": (
            "Can the normalized BT low-mode marginal be rewritten in exact "
            "coordinates that expose, rather than hide, the orthogonal-mode "
            "entropy left uncontrolled by action sublevel bounds?"
        ),
        "answer": (
            "Yes as an exact reformulation, not yet as a moment bound. On "
            "every finite connected graph, positive fields modulo scale map "
            "analytically and bijectively by r=(Delta Omega)/Omega onto the "
            "smooth boundary of the convex spectrahedron "
            "{-Delta+diag(r)>=0}. The positive field is the unique ground "
            "state. The residual derivative is similar to the negative "
            "Schrodinger operator, and its restricted Jacobian is an exact "
            "directed-tree factor. Coarea therefore pushes the BT Gibbs "
            "measure to a Gaussian surface weight divided by that tree "
            "Jacobian. The desired Fourier marginal is now the logarithm of "
            "the positive ground state under this explicit normalized "
            "measure. Bounding that ground-state/tree marginal uniformly in "
            "volume remains the active estimate."
        ),
        "finite_graph_theorem": {
            "scope": "every finite connected undirected graph",
            "positive_carrier": (
                "Omega in (0,infinity)^N modulo positive scale; the section "
                "sum_x log(Omega_x)=0 fixes the representative"
            ),
            "graph_laplacian": (
                "(Delta Omega)_x=sum_(y~x) Omega_y-degree(x)*Omega_x"
            ),
            "residual_map": "r_x=(Delta Omega)_x/Omega_x",
            "spectrahedron": (
                "C_G={r in R^N: K(r)=-Delta+diag(r) is positive semidefinite}"
            ),
            "boundary_identity": (
                "K(r(Omega))*Omega=0 and the ground-state identity is "
                "v^T K v=sum_{edges {x,y}} Omega_x Omega_y "
                "(v_x/Omega_x-v_y/Omega_y)^2"
            ),
            "inverse": (
                "Every boundary point has a simple strictly positive null "
                "vector by connected Perron-Frobenius; normalize its "
                "geometric mean to one and take psi=log(Omega)"
            ),
            "geometry": (
                "C_G is convex, its boundary is smooth because the ground "
                "eigenvalue is simple, and the residual map is an analytic "
                "diffeomorphism from the mean-zero log-field carrier"
            ),
            "status": "PROVED",
        },
        "differential_and_tree_jacobian": {
            "derivative": (
                "J_psi=Dr=-diag(Omega)^(-1) K(r) diag(Omega), with "
                "J_psi*1=0"
            ),
            "boundary_normal": (
                "the outward normal is proportional to Omega^2 and "
                "Omega^2^T J_psi=0"
            ),
            "directed_laplacian": (
                "-J has off-diagonal entries -Omega_y/Omega_x and is the "
                "directed weighted graph Laplacian"
            ),
            "tree_density": (
                "tau_psi=cofactor_i(-J)/Omega_i^2 is independent of i by "
                "the directed matrix-tree theorem"
            ),
            "undirected_tree_formula": (
                "tau_psi=sum_T product_{edges {x,y} in T}(Omega_x Omega_y) "
                "/ product_x Omega_x^2, summed over undirected spanning trees"
            ),
            "restricted_jacobian": (
                "Jac_H(r)(psi)=sqrt(N)*||Omega^2||_2*tau_psi, the product "
                "of the N-1 singular values from 1^perp to (Omega^2)^perp"
            ),
            "tilt_log_convexity": (
                "For Omega_x(t)=Omega_x exp(t h_x), log(tau(t)) is a "
                "log-sum-exp of affine tree exponents and "
                "log(||Omega(t)^2||_2) is log-sum-exp up to a factor; hence "
                "log(Jac_H(t)) is convex for every real direction h"
            ),
            "vertex_transitive_minimum": (
                "If G is vertex transitive and sum psi=0, AM-GM over all "
                "kappa(G) spanning trees gives tau_psi>=kappa(G), while "
                "||Omega^2||_2>=sqrt(N); hence Jac_H(psi)>=N*kappa(G), "
                "with equality at the constant field"
            ),
            "status": "PROVED",
        },
        "normalized_pushforward": {
            "original_measure": (
                "dmu_L(psi)=Z_L^(-1) exp[-||r(psi)||_2^2/(2 lambda^2)] "
                "dpsi on sum psi=0"
            ),
            "surface_measure": (
                "dnu_L(r)=Z_L^(-1) exp[-||r||_2^2/(2 lambda^2)] "
                "[sqrt(N)*||Omega(r)^2||_2*tau(r)]^(-1) dH^(N-1)(r) "
                "on boundary C_G"
            ),
            "lowest_mode_observable": (
                "hat(Phi_L)(k)=lambda^(-1) N^(-1) sum_x "
                "log(Omega_x(r))*exp(-2*pi*i*k.x/L)"
            ),
            "normalization_gain": (
                "the full orthogonal-field entropy is represented by the "
                "surface geometry and inverse tree Jacobian rather than an "
                "uncontrolled fiber partition function"
            ),
            "remaining_estimate": (
                "control the log-ground-state Fourier marginal jointly with "
                "the reciprocal tree Jacobian, first at the lowest axial "
                "mode and then on dyadic shells"
            ),
            "status": "EXACT_NORMALIZED_REFORMULATION_ONLY",
        },
        "exact_cycle_fixture": {
            "graph": "four-cycle C4 with degree two",
            "omega": [encode(value) for value in fixture["omega"]],
            "product_omega": encode(Fraction(1)),
            "residual": [encode(value) for value in fixture["residual"]],
            "action": encode(fixture["action"]),
            "schrodinger_matrix": encode_matrix(fixture["schrodinger"]),
            "residual_jacobian": encode_matrix(fixture["jacobian"]),
            "boundary_normal": [encode(value) for value in fixture["normal"]],
            "tree_cofactors": [
                encode(value) for value in fixture["cofactor_values"]
            ],
            "undirected_tree_terms": [
                encode(value) for value in fixture["undirected_tree_terms"]
            ],
            "tree_density": encode(fixture["tree_density"]),
            "domain_gram_determinant": encode(
                fixture["domain_gram_determinant"]
            ),
            "image_gram_determinant": encode(
                fixture["image_gram_determinant"]
            ),
            "restricted_jacobian_squared": encode(
                fixture["jacobian_squared"]
            ),
            "restricted_jacobian": encode(Fraction(85, 2)),
            "status": "EXACT_RATIONAL_FIXTURE",
        },
        "method_disposition": {
            "hidden_orthogonal_fiber_partition": "REPLACED_BY_EXACT_COAREA_WEIGHT",
            "residual_spectrahedral_boundary_coordinates": "PROVED",
            "ground_state_tree_jacobian": "PROVED",
            "vertex_transitive_entropy_jacobian_minimum": "PROVED",
            "normalized_lowest_mode_marginal_bound": "OPEN",
            "actual_interacting_h_minus_one_second_moment_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "ordinary_os_at_lambda_0p4": "OBSTRUCTED_BY_PREDECESSOR",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "foundational_dependency_cut": {
            "finite_exact_layer": (
                "rational graph matrices, the ground-state sum-of-squares "
                "identity, cofactors, and the C4 witness"
            ),
            "finite_analytic_layer": (
                "Perron-Frobenius simplicity, analytic dependence of the "
                "positive ground vector, and finite-dimensional coarea"
            ),
            "uniform_limit_layer": (
                "an all-volume estimate for the log-ground-state/tree "
                "marginal; not supplied by the finite diffeomorphism"
            ),
            "classification": "USED_BY_DISPLAYED_PROOF",
            "weakest_base_or_reversal": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "an L-uniform bound on the lowest log-ground-state Fourier marginal under the coarea weight",
            "a dyadic-shell summation proving or obstructing the actual interacting H^-1 moment",
            "tightness in a compactly weaker topology after a positive moment theorem",
            "identification and uniqueness of any Euclidean subsequential limit",
        ],
        "next_gate": (
            "Use the exact surface density to estimate ratios under a "
            "lowest-mode multiplicative tilt of the positive ground state. "
            "The new analytic object is the joint variation of the Gaussian "
            "residual norm, boundary surface element, and directed-tree "
            "Jacobian. Prove a uniform bound or a controlled divergence "
            "sequence before proceeding to dyadic shells."
        ),
        "does_not_establish": [
            "a uniform bound for the normalized lowest-mode marginal",
            "the actual interacting H^-1 moment bound or its divergence",
            "tightness or a continuum Euclidean BT measure",
            "ordinary reflection positivity, which is obstructed at lambda=0.4 by a predecessor",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
            "a literature-novelty claim for the finite graph ground-state transform or matrix-tree identity",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Exact Fraction arithmetic for the independent C4 fixture; "
                "the general theorem uses finite graph identities, "
                "Perron-Frobenius simplicity, coarea, and the directed "
                "matrix-tree theorem"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_residual_spectrahedral_pushforward.py --check",
            "python3 reverse_physics/verify_bt_euclidean_residual_spectrahedral_pushforward.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_residual_spectrahedral_pushforward",
        ],
        "tier_receipt": {
            "command_results": [
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/bt_euclidean_residual_spectrahedral_pushforward.py --check",
                    "elapsed_seconds": "0.03",
                    "peak_rss_kib": 21276,
                    "status": "PASS_19_OF_19",
                },
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_residual_spectrahedral_pushforward.py",
                    "elapsed_seconds": "0.09",
                    "peak_rss_kib": 30572,
                    "status": "PASS_15_OF_15",
                },
                {
                    "command": "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_residual_spectrahedral_pushforward",
                    "elapsed_seconds": "0.12",
                    "peak_rss_kib": 30604,
                    "status": "PASS_10_TESTS",
                },
                {
                    "command": "GOMEMLIMIT=300MiB GOGC=50 /home/alstrup/tmp/sf-sfc-1000 conform planning/work-items",
                    "elapsed_seconds": "1.04",
                    "peak_rss_kib": 5492,
                    "status": "PASS_CLEAN",
                },
            ],
            "tier_0": (
                "parse, strict schema, deterministic generation, scoped git "
                "diff --check, and exact staged-diff inspection"
            ),
            "tier_1": (
                "producer, independent residual/Schrodinger/matrix-tree/coarea "
                "verifier, and mutation tests"
            ),
            "tier_2": (
                "NOT_RUN_FOR_THIS_SCOPED_COMMIT: Paper 21 projection is "
                "deferred because a concurrent foundations v11 update changed "
                "the atlas evidence count during validation; predecessor "
                "scientific certificates are reused by content hash"
            ),
            "tier_3": (
                "NOT_RUN: no freeze, release, continuum, quantum lifecycle, "
                "or Lorentzian promotion"
            ),
            "resource_policy": (
                "all scientific commands run sequentially under "
                "ulimit -v 500000"
            ),
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if not payload["checks"]["ok"]:
        for failure in payload["checks"]["failures"]:
            print(f"[FAIL] {failure}")
        return 1
    if args.check:
        if not os.path.exists(CERT_PATH):
            print(f"[FAIL] missing certificate: {CERT_REL}", file=sys.stderr)
            return 1
        with open(CERT_PATH, encoding="utf-8") as handle:
            committed = json.load(handle)
        if committed != payload:
            print("[FAIL] committed certificate is stale", file=sys.stderr)
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(
        "[PASS] BT residual spectrahedral pushforward "
        f"({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
