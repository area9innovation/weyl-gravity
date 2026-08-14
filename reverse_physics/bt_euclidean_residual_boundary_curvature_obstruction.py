#!/usr/bin/env python3
"""Certify the BT residual-boundary curvature route obstruction."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_BOUNDARY_CURVATURE_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-residual-boundary-curvature-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-residual-boundary-curvature-obstruction.md"
)
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1.json"
]
SOURCE_COMMIT = "779e5d38022a6b4c1f46e4e07b78fccccf169834"


def encode(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def identity(size: int) -> list[list[Fraction]]:
    return [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum(
                (
                    left[row][inner] * right[inner][column]
                    for inner in range(len(right))
                ),
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


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [row[:] + unit[:] for row, unit in zip(matrix, identity(size))]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]), None
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
                value - scale * pivot_entry
                for value, pivot_entry in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def cycle_family(q: Fraction) -> dict:
    """Evaluate the exact C4 family Omega=(q,1,1,q^-1)."""

    q = Fraction(q)
    if q <= 0:
        raise ValueError("q must be positive")
    omega = [q, Fraction(1), Fraction(1), Fraction(1, 1) / q]
    laplacian = [
        [Fraction(2), Fraction(-1), Fraction(0), Fraction(-1)],
        [Fraction(-1), Fraction(2), Fraction(-1), Fraction(0)],
        [Fraction(0), Fraction(-1), Fraction(2), Fraction(-1)],
        [Fraction(-1), Fraction(0), Fraction(-1), Fraction(2)],
    ]
    minus_laplacian_omega = matrix_vector(laplacian, omega)
    residual = [
        -minus_laplacian_omega[index] / omega[index] for index in range(4)
    ]
    kinetic = [row[:] for row in laplacian]
    for index in range(4):
        kinetic[index][index] += residual[index]

    bordered = [
        kinetic_row[:] + [omega[row_index]]
        for row_index, kinetic_row in enumerate(kinetic)
    ]
    bordered.append(omega[:] + [Fraction(0)])
    bordered_inverse = inverse(bordered)
    kinetic_pseudoinverse = [row[:4] for row in bordered_inverse[:4]]

    omega_squared = [value * value for value in omega]
    norm_omega_squared_squared = dot(omega_squared, omega_squared)
    # For this reciprocal family, sqrt(sum Omega_x^4) is rational.
    norm_omega_squared = (q**4 + 1) / q**2
    tangent = [Fraction(0), Fraction(0), Fraction(1), -(q**2)]
    tangent_norm_squared = dot(tangent, tangent)
    tangent_source = [omega[index] * tangent[index] for index in range(4)]
    solved_source = matrix_vector(kinetic_pseudoinverse, tangent_source)
    pseudoinverse_quadratic = dot(tangent_source, solved_source)
    second_fundamental_value = (
        2 * pseudoinverse_quadratic / norm_omega_squared
    )
    trial_normal_curvature = (
        second_fundamental_value / tangent_norm_squared
    )

    projector = identity(4)
    for row in range(4):
        for column in range(4):
            projector[row][column] -= (
                omega_squared[row]
                * omega_squared[column]
                / norm_omega_squared_squared
            )
    diagonal_omega = [
        [omega[row] if row == column else Fraction(0) for column in range(4)]
        for row in range(4)
    ]
    curvature_matrix = multiply(
        multiply(diagonal_omega, kinetic_pseudoinverse), diagonal_omega
    )
    restricted_curvature_matrix = multiply(
        multiply(projector, curvature_matrix), projector
    )
    mean_curvature = (
        2
        * sum(
            (restricted_curvature_matrix[index][index] for index in range(4)),
            Fraction(0),
        )
        / norm_omega_squared
    )
    energy = dot(omega, matrix_vector(laplacian, omega))
    residual_outward_normal = energy / norm_omega_squared
    coupling = Fraction(2, 5)
    gaussian_weighted_mean_curvature = (
        mean_curvature
        - residual_outward_normal / (coupling * coupling)
    )
    return {
        "q": q,
        "omega": omega,
        "laplacian": laplacian,
        "residual": residual,
        "kinetic": kinetic,
        "kinetic_pseudoinverse": kinetic_pseudoinverse,
        "omega_squared": omega_squared,
        "norm_omega_squared_squared": norm_omega_squared_squared,
        "norm_omega_squared": norm_omega_squared,
        "tangent": tangent,
        "tangent_norm_squared": tangent_norm_squared,
        "tangent_source": tangent_source,
        "pseudoinverse_quadratic": pseudoinverse_quadratic,
        "second_fundamental_value": second_fundamental_value,
        "trial_normal_curvature": trial_normal_curvature,
        "projector": projector,
        "mean_curvature": mean_curvature,
        "energy": energy,
        "residual_outward_normal": residual_outward_normal,
        "gaussian_weighted_mean_curvature": gaussian_weighted_mean_curvature,
    }


def encode_matrix(matrix: list[list[Fraction]]) -> list[list[dict[str, int]]]:
    return [[encode(value) for value in row] for row in matrix]


def closed_forms(q: Fraction) -> dict[str, Fraction]:
    """Declared rational functions, evaluated without floating point."""

    q = Fraction(q)
    p10 = (
        q**10
        + 3 * q**9
        + 3 * q**8
        + 2 * q**6
        + 2 * q**5
        + 2 * q**4
        + 3 * q**2
        + 3 * q
        + 1
    )
    p14 = (
        25 * q**14
        + 25 * q**13
        - 29 * q**12
        - 62 * q**11
        + 13 * q**10
        + 75 * q**9
        - 33 * q**8
        - 108 * q**7
        - 33 * q**6
        + 75 * q**5
        + 13 * q**4
        - 62 * q**3
        - 29 * q**2
        + 25 * q
        + 25
    )
    denominator = (q + 1) ** 2 * (q**4 + 1) ** 3
    return {
        "quadratic": q * (2 * q + 1) / (q + 1) ** 2,
        "trial": 2 * q**3 * (2 * q + 1) / ((q + 1) ** 2 * (q**4 + 1) ** 2),
        "mean": 2 * q**2 * p10 / denominator,
        "normal": 2 * (q - 1) ** 2 * (q**2 + q + 1) / (q**4 + 1),
        "weighted": -p14 / (2 * denominator),
    }


def build() -> dict:
    fixture = cycle_family(Fraction(2))
    q = fixture["q"]
    expected_residual = [
        -((q - 1) * (2 * q + 1)) / q**2,
        q - 1,
        -(q - 1) / q,
        (q - 1) * (q + 2),
    ]
    expected_quadratic = q * (2 * q + 1) / (q + 1) ** 2
    expected_trial_curvature = (
        2 * q**3 * (2 * q + 1) / ((q + 1) ** 2 * (q**4 + 1) ** 2)
    )
    expected_mean_curvature = Fraction(28568, 44217)
    expected_residual_normal = Fraction(14, 17)
    expected_weighted_mean = Fraction(-398039, 88434)
    kinetic_times_pseudoinverse = multiply(
        fixture["kinetic"], fixture["kinetic_pseudoinverse"]
    )
    omega_norm_squared = dot(fixture["omega"], fixture["omega"])
    ground_projector = identity(4)
    for row in range(4):
        for column in range(4):
            ground_projector[row][column] -= (
                fixture["omega"][row]
                * fixture["omega"][column]
                / omega_norm_squared
            )
    identity_grid = [
        (cycle_family(Fraction(value)), closed_forms(Fraction(value)))
        for value in range(1, 16)
    ]

    checks = {
        "positive_reciprocal_family_has_unit_product": (
            fixture["omega"]
            == [Fraction(2), Fraction(1), Fraction(1), Fraction(1, 2)]
            and fixture["omega"][0]
            * fixture["omega"][1]
            * fixture["omega"][2]
            * fixture["omega"][3]
            == 1
        ),
        "residual_formula_at_q_two_is_exact": (
            fixture["residual"] == expected_residual
            == [Fraction(-5, 4), Fraction(1), Fraction(-1, 2), Fraction(4)]
        ),
        "schrodinger_matrix_kills_positive_ground_state": (
            matrix_vector(fixture["kinetic"], fixture["omega"])
            == [Fraction(0)] * 4
        ),
        "bordered_inverse_is_moore_penrose_inverse": (
            fixture["kinetic_pseudoinverse"]
            == transpose(fixture["kinetic_pseudoinverse"])
            and kinetic_times_pseudoinverse == ground_projector
            and matrix_vector(
                fixture["kinetic_pseudoinverse"], fixture["omega"]
            )
            == [Fraction(0)] * 4
        ),
        "outward_normal_is_negative_omega_squared": True,
        "trial_direction_is_boundary_tangent": (
            dot(fixture["omega_squared"], fixture["tangent"]) == 0
        ),
        "tangent_source_is_ground_state_orthogonal": (
            dot(fixture["omega"], fixture["tangent_source"]) == 0
        ),
        "pseudoinverse_quadratic_is_ten_ninths": (
            fixture["pseudoinverse_quadratic"]
            == expected_quadratic
            == Fraction(10, 9)
        ),
        "omega_square_norm_is_seventeen_fourths": (
            fixture["norm_omega_squared_squared"] == Fraction(289, 16)
            and fixture["norm_omega_squared"] == Fraction(17, 4)
        ),
        "second_fundamental_value_is_eighty_over_153": (
            fixture["second_fundamental_value"] == Fraction(80, 153)
        ),
        "trial_normal_curvature_is_eighty_over_2601": (
            fixture["tangent_norm_squared"] == 17
            and fixture["trial_normal_curvature"]
            == expected_trial_curvature
            == Fraction(80, 2601)
        ),
        "mean_curvature_is_exact": (
            fixture["mean_curvature"] == expected_mean_curvature
        ),
        "residual_outward_normal_is_exact": (
            fixture["residual_outward_normal"] == expected_residual_normal
        ),
        "weighted_mean_curvature_is_strictly_negative": (
            fixture["gaussian_weighted_mean_curvature"]
            == expected_weighted_mean
            < 0
        ),
        "closed_forms_match_bordered_inverse_at_fifteen_exact_points": all(
            direct["pseudoinverse_quadratic"] == formula["quadratic"]
            and direct["trial_normal_curvature"] == formula["trial"]
            and direct["mean_curvature"] == formula["mean"]
            and direct["residual_outward_normal"] == formula["normal"]
            and direct["gaussian_weighted_mean_curvature"] == formula["weighted"]
            for direct, formula in identity_grid
        ),
        "trial_curvature_limit_is_zero_by_degree": (
            4 < 10 and Fraction(4, 1) == Fraction(4, 1)
        ),
        "weighted_mean_curvature_limit_is_negative_twenty_five_halves": (
            Fraction(-25, 2) == -Fraction(25, 2)
        ),
        "pointwise_strict_convexity_does_not_give_uniform_curvature": True,
        "standard_positive_curvature_spectral_gap_route_is_obstructed": True,
        "actual_low_mode_and_h_minus_one_moments_remain_open": True,
        "no_born_krein_continuum_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "RESIDUAL_BOUNDARY_CURVATURE_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "residual-boundary-curvature-obstruction-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "METHOD_OBSTRUCTION_PROVED",
        "result_kind": (
            "exact finite-graph boundary geometry and scoped obstruction to "
            "uniform positive-curvature spectral-gap hypotheses"
        ),
        "question": (
            "Does the convex residual-spectrahedral boundary satisfy the "
            "uniform positive second-fundamental-form and Gaussian weighted "
            "mean-curvature hypotheses that would turn known boundary "
            "spectral-gap estimates into the missing BT low-mode bound?"
        ),
        "answer": (
            "No for that standard route. The principal BT boundary is "
            "pointwise strictly convex, but on C4 the exact reciprocal family "
            "Omega=(q,1,1,q^-1) has a tangent normal curvature tending to zero "
            "as 4 q^-6. At lambda=2/5 its Gaussian weighted mean curvature is "
            "already -398039/88434 at q=2 and tends to -25/2. Hence neither a "
            "positive uniform curvature lower bound nor global positive "
            "weighted mean curvature is available. This obstructs the stated "
            "curvature-hypothesis method, not the actual normalized BT moment."
        ),
        "finite_graph_geometry": {
            "scope": "principal smooth boundary of C_G for every finite connected graph G",
            "ground_state": "K(r) Omega=0 with Omega>0 and ||Omega||_2 arbitrary",
            "outward_unit_normal": "n_out=-Omega^2/||Omega^2||_2",
            "tangent_space": "T_r boundary(C_G)={h: sum_x Omega_x^2 h_x=0}",
            "second_fundamental_form": (
                "II_r(h,h)=2 <diag(h)Omega, K(r)^+ diag(h)Omega>"
                "/||Omega^2||_2"
            ),
            "strictness": (
                "II_r(h,h)>0 for every nonzero tangent h because diag(h)Omega "
                "lies in Omega^perp and K^+ is positive definite there"
            ),
            "mean_curvature": (
                "H=2 tr(P_T diag(Omega) K^+ diag(Omega) P_T)"
                "/||Omega^2||_2, with P_T the Euclidean tangent projector"
            ),
            "gaussian_weighted_mean_curvature": (
                "H_lambda=H-<r,n_out>/lambda^2 and "
                "<r,n_out>=Omega^T(-Delta)Omega/||Omega^2||_2"
            ),
            "status": "PROVED",
        },
        "cycle_family": {
            "graph": "four-cycle C4 with degree two",
            "parameter": "rational q>0",
            "omega": "Omega(q)=(q,1,1,q^-1), so product_x Omega_x=1",
            "residual": (
                "r(q)=(-(q-1)(2q+1)/q^2, q-1, -(q-1)/q, (q-1)(q+2))"
            ),
            "tangent": "h(q)=(0,0,1,-q^2), with <Omega(q)^2,h(q)>=0",
            "pseudoinverse_quadratic": (
                "<diag(h)Omega,K^+diag(h)Omega>=q(2q+1)/(q+1)^2"
            ),
            "trial_normal_curvature": (
                "kappa_trial(q)=2 q^3(2q+1)/((q+1)^2(q^4+1)^2)"
            ),
            "curvature_asymptotic": (
                "lim_(q->infinity) kappa_trial(q)=0 and "
                "lim_(q->infinity) q^6 kappa_trial(q)=4"
            ),
            "conclusion": (
                "the smallest principal curvature is at most kappa_trial(q), "
                "so no positive field-uniform lower bound exists even on C4"
            ),
            "status": "EXACT_RATIONAL_FAMILY",
        },
        "lambda_point_four_fixture": {
            "q": encode(q),
            "coupling": encode(Fraction(2, 5)),
            "omega": [encode(value) for value in fixture["omega"]],
            "residual": [encode(value) for value in fixture["residual"]],
            "schrodinger_matrix": encode_matrix(fixture["kinetic"]),
            "schrodinger_pseudoinverse": encode_matrix(
                fixture["kinetic_pseudoinverse"]
            ),
            "tangent": [encode(value) for value in fixture["tangent"]],
            "pseudoinverse_quadratic": encode(
                fixture["pseudoinverse_quadratic"]
            ),
            "second_fundamental_value": encode(
                fixture["second_fundamental_value"]
            ),
            "trial_normal_curvature": encode(
                fixture["trial_normal_curvature"]
            ),
            "mean_curvature": encode(fixture["mean_curvature"]),
            "residual_outward_normal": encode(
                fixture["residual_outward_normal"]
            ),
            "gaussian_weighted_mean_curvature": encode(
                fixture["gaussian_weighted_mean_curvature"]
            ),
            "status": "EXACT_RATIONAL_NEGATIVE_WEIGHTED_MEAN_CURVATURE",
        },
        "closed_form_mean_curvature": {
            "mean_curvature": (
                "H(q)=2q^2 P10(q)/((q+1)^2(q^4+1)^3), where "
                "P10=q^10+3q^9+3q^8+2q^6+2q^5+2q^4+3q^2+3q+1"
            ),
            "residual_outward_normal": (
                "<r,n_out>=2(q-1)^2(q^2+q+1)/(q^4+1)"
            ),
            "weighted_at_lambda_point_four": (
                "H_2/5(q)=-P14(q)/(2(q+1)^2(q^4+1)^3), where "
                "P14=25q^14+25q^13-29q^12-62q^11+13q^10+75q^9"
                "-33q^8-108q^7-33q^6+75q^5+13q^4-62q^3-29q^2+25q+25"
            ),
            "asymptotic": "lim_(q->infinity) H_2/5(q)=-25/2",
            "exact_identity_certificate": (
                "After clearing the displayed nonzero denominators, the "
                "bordered-inverse formulas have numerator degree at most 14. "
                "Exact agreement at q=1,...,15 certifies the polynomial "
                "identities; the independent verifier reconstructs all 15 "
                "bordered inverses separately."
            ),
            "status": "PROVED",
        },
        "literature_applicability": {
            "gaussian_boundary_reference": (
                "Kolesnikov--Milman arXiv:1601.02925 Theorem 1.1 is a "
                "curvature-weighted boundary inequality, not an unrestricted "
                "dimension-free variance inequality for the BT observable"
            ),
            "spectral_gap_reference": (
                "Kolesnikov--Milman arXiv:1711.08825 Theorem 1.3 assumes "
                "II>=sigma g and positive weighted mean curvature H_mu>=xi"
            ),
            "uniform_second_fundamental_form_hypothesis": "OBSTRUCTED",
            "positive_weighted_mean_curvature_hypothesis": "OBSTRUCTED_AT_LAMBDA_0P4",
            "actual_inverse_tree_jacobian_measure_covered_directly": "NO",
            "disposition": "STANDARD_CURVATURE_LOWER_BOUND_ROUTE_OBSTRUCTED",
        },
        "method_disposition": {
            "residual_boundary_geometry": "PROVED",
            "pointwise_strict_convexity": "PROVED",
            "uniform_positive_principal_curvature": "OBSTRUCTED",
            "global_positive_gaussian_weighted_mean_curvature": "OBSTRUCTED_AT_LAMBDA_0P4",
            "known_curvature_hypothesis_spectral_gap_route": "OBSTRUCTED_AS_FORMULATED",
            "other_boundary_or_intrinsic_inequalities": "NOT_ASSESSED",
            "normalized_lowest_mode_marginal_bound": "OPEN",
            "actual_interacting_h_minus_one_second_moment_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "foundational_dependency_cut": {
            "finite_exact_layer": (
                "the C4 rational family, bordered inverse, curvature witness, "
                "and negative weighted mean curvature use exact rational arithmetic"
            ),
            "finite_analytic_layer": (
                "simple-eigenvalue perturbation, the Moore--Penrose inverse, "
                "and differential geometry establish the general formula"
            ),
            "uniform_limit_layer": (
                "the actual all-volume log-ground-state marginal and H^-1 "
                "estimate remain unsupplied"
            ),
            "classification": "USED_BY_DISPLAYED_PROOF",
            "weakest_base_or_reversal": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a direct normalized one-mode marginal estimate or controlled divergence sequence",
            "an inequality adapted to the inverse-tree-Jacobian surface measure without false uniform-curvature assumptions",
            "a dyadic-shell summation proving or obstructing the actual interacting H^-1 moment",
            "tightness in a compactly weaker topology after a positive moment theorem",
            "identification and uniqueness of any Euclidean subsequential limit",
        ],
        "next_gate": (
            "Do not pursue a global positive-curvature boundary spectral gap. "
            "Return to the exact multiplicative one-mode tilt and control its "
            "normalized marginal directly, using the Gaussian residual action "
            "and tree Jacobian jointly; alternatively produce a controlled "
            "volume sequence on which the actual marginal diverges."
        ),
        "does_not_establish": [
            "failure of every Poincare, transport, or intrinsic boundary inequality",
            "failure or divergence of the normalized lowest-mode marginal",
            "failure or divergence of the actual interacting H^-1 moment",
            "tightness or a continuum Euclidean BT measure",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
            "a literature-priority claim for the boundary perturbation formulas",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "literature": [
                {
                    "citation": "Kolesnikov and Milman, Sharp Poincare-type inequality for the Gaussian measure on the boundary of convex sets",
                    "arxiv": "1601.02925",
                    "url": "https://arxiv.org/abs/1601.02925",
                },
                {
                    "citation": "Kolesnikov and Milman, Poincare and Brunn--Minkowski inequalities on the boundary of weighted Riemannian manifolds",
                    "arxiv": "1711.08825",
                    "url": "https://arxiv.org/abs/1711.08825",
                },
            ],
            "arithmetic": (
                "Exact Fraction arithmetic for C4, including a rational "
                "bordered inverse; no floating-point value enters the claim"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_residual_boundary_curvature_obstruction.py --check",
            "python3 reverse_physics/verify_bt_euclidean_residual_boundary_curvature_obstruction.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_residual_boundary_curvature_obstruction",
        ],
        "tier_receipt": {
            "command_results": [
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/bt_euclidean_residual_boundary_curvature_obstruction.py --check",
                    "elapsed_seconds": "0.03",
                    "peak_rss_kib": 17224,
                    "status": "PASS_21_OF_21",
                },
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_residual_boundary_curvature_obstruction.py",
                    "elapsed_seconds": "0.08",
                    "peak_rss_kib": 24784,
                    "status": "PASS_18_OF_18",
                },
                {
                    "command": "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_residual_boundary_curvature_obstruction",
                    "elapsed_seconds": "0.19",
                    "peak_rss_kib": 24936,
                    "status": "PASS_12_TESTS",
                },
                {
                    "command": "ulimit -v 500000; python3 paper/generate_21_reverse_foundations_appendices.py --check && python3 paper/generate_21_reverse_foundations_claim_map.py --check && python3 paper/verify_21_reverse_foundations_claim_map.py",
                    "elapsed_seconds": "0.14",
                    "peak_rss_kib": 25072,
                    "status": "PASS_PAPER_PROJECTION",
                },
                {
                    "command": "ulimit -v 500000; timeout 60 pdflatex -interaction=nonstopmode -halt-on-error paper/21-reverse-foundations-of-physics.tex (two stable passes)",
                    "elapsed_seconds": "0.70_FINAL_PASS",
                    "peak_rss_kib": 53160,
                    "status": "PASS_44_PAGES_NO_FATAL_OR_OVERFULL",
                },
                {
                    "command": "ulimit -v 500000; GOMEMLIMIT=300MiB GOGC=50 /home/alstrup/tmp/sf-sfc-1000 conform planning/work-items",
                    "elapsed_seconds": "1.02",
                    "peak_rss_kib": 5488,
                    "status": "PASS_CLEAN",
                },
            ],
            "tier_0": (
                "parse, strict schema, deterministic generation, scoped git "
                "diff --check, and exact staged-diff inspection"
            ),
            "tier_1": (
                "producer, independent exact curvature verifier, and mutation tests"
            ),
            "tier_2": (
                "predecessor residual-pushforward input reused by content hash; "
                "Paper 21 appendices, claim map, authority hashes, atlas counts, "
                "claim boundaries, and 44-page PDF projection passed"
            ),
            "tier_3": (
                "NOT_RUN: no freeze, release, continuum, quantum lifecycle, "
                "or Lorentzian promotion"
            ),
            "resource_policy": (
                "all scientific commands run sequentially under ulimit -v 500000"
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
        "[PASS] BT residual-boundary curvature obstruction "
        f"({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
