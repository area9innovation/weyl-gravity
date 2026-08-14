#!/usr/bin/env python3
"""Independent verifier for the BT residual-boundary curvature obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_BOUNDARY_CURVATURE_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-residual-boundary-curvature-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def unit(size: int) -> list[list[Fraction]]:
    return [
        [Fraction(row == column) for column in range(size)]
        for row in range(size)
    ]


def matmul(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(0),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matvec(
    matrix: list[list[Fraction]], vector: list[Fraction]
) -> list[Fraction]:
    return [
        sum((row[index] * vector[index] for index in range(len(vector))), Fraction(0))
        for row in matrix
    ]


def scalar(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def gauss_jordan(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    augmented = [row[:] + unit_row[:] for row, unit_row in zip(matrix, unit(size))]
    for pivot_column in range(size):
        pivot_row = next(
            row
            for row in range(pivot_column, size)
            if augmented[row][pivot_column] != 0
        )
        augmented[pivot_column], augmented[pivot_row] = (
            augmented[pivot_row],
            augmented[pivot_column],
        )
        pivot = augmented[pivot_column][pivot_column]
        augmented[pivot_column] = [entry / pivot for entry in augmented[pivot_column]]
        for row in range(size):
            if row == pivot_column:
                continue
            coefficient = augmented[row][pivot_column]
            augmented[row] = [
                entry - coefficient * pivot_entry
                for entry, pivot_entry in zip(
                    augmented[row], augmented[pivot_column]
                )
            ]
    return [row[size:] for row in augmented]


def independent_family(q: Fraction) -> dict:
    q = Fraction(q)
    omega = [q, Fraction(1), Fraction(1), 1 / q]
    graph_laplacian = [
        [Fraction(2), Fraction(-1), Fraction(0), Fraction(-1)],
        [Fraction(-1), Fraction(2), Fraction(-1), Fraction(0)],
        [Fraction(0), Fraction(-1), Fraction(2), Fraction(-1)],
        [Fraction(-1), Fraction(0), Fraction(-1), Fraction(2)],
    ]
    residual = [
        -value / omega[index]
        for index, value in enumerate(matvec(graph_laplacian, omega))
    ]
    kinetic = [row[:] for row in graph_laplacian]
    for index, value in enumerate(residual):
        kinetic[index][index] += value
    bordered = [
        kinetic[index][:] + [omega[index]] for index in range(4)
    ] + [omega[:] + [Fraction(0)]]
    inverse_bordered = gauss_jordan(bordered)
    pseudoinverse = [row[:4] for row in inverse_bordered[:4]]

    omega2 = [value * value for value in omega]
    sum_omega4 = scalar(omega2, omega2)
    sqrt_sum_omega4 = (q**4 + 1) / q**2
    tangent = [Fraction(0), Fraction(0), Fraction(1), -(q**2)]
    source = [tangent[index] * omega[index] for index in range(4)]
    quadratic = scalar(source, matvec(pseudoinverse, source))
    second_fundamental = 2 * quadratic / sqrt_sum_omega4
    trial_curvature = second_fundamental / scalar(tangent, tangent)

    tangent_projector = unit(4)
    for row in range(4):
        for column in range(4):
            tangent_projector[row][column] -= (
                omega2[row] * omega2[column] / sum_omega4
            )
    weighted_inverse = [
        [omega[row] * pseudoinverse[row][column] * omega[column] for column in range(4)]
        for row in range(4)
    ]
    restricted = matmul(matmul(tangent_projector, weighted_inverse), tangent_projector)
    mean_curvature = (
        2
        * sum((restricted[index][index] for index in range(4)), Fraction(0))
        / sqrt_sum_omega4
    )
    energy = scalar(omega, matvec(graph_laplacian, omega))
    residual_normal = energy / sqrt_sum_omega4
    weighted_mean = mean_curvature - Fraction(25, 4) * residual_normal
    return {
        "omega": omega,
        "residual": residual,
        "kinetic": kinetic,
        "pseudoinverse": pseudoinverse,
        "tangent": tangent,
        "quadratic": quadratic,
        "second_fundamental": second_fundamental,
        "trial_curvature": trial_curvature,
        "mean_curvature": mean_curvature,
        "residual_normal": residual_normal,
        "weighted_mean": weighted_mean,
    }


def closed_forms(q: Fraction) -> dict:
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
    mean = 2 * q**2 * p10 / ((q + 1) ** 2 * (q**4 + 1) ** 3)
    normal = 2 * (q - 1) ** 2 * (q**2 + q + 1) / (q**4 + 1)
    trial = 2 * q**3 * (2 * q + 1) / ((q + 1) ** 2 * (q**4 + 1) ** 2)
    return {
        "quadratic": q * (2 * q + 1) / (q + 1) ** 2,
        "trial": trial,
        "mean": mean,
        "normal": normal,
        "weighted": -p14 / (2 * (q + 1) ** 2 * (q**4 + 1) ** 3),
    }


def verify(path: str = DEFAULT_CERT) -> bool:
    checks: dict[str, bool] = {}
    errors = []
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(certificate),
            key=lambda error: list(error.path),
        )
        checks["strict_schema"] = not errors

        fixture = independent_family(Fraction(2))
        public = certificate["lambda_point_four_fixture"]
        checks["positive_family_and_residual_rederived"] = (
            fixture["omega"] == [decode(value) for value in public["omega"]]
            == [Fraction(2), Fraction(1), Fraction(1), Fraction(1, 2)]
            and fixture["residual"] == [decode(value) for value in public["residual"]]
            == [Fraction(-5, 4), Fraction(1), Fraction(-1, 2), Fraction(4)]
        )
        checks["schrodinger_and_ground_state_rederived"] = (
            fixture["kinetic"]
            == [[decode(value) for value in row] for row in public["schrodinger_matrix"]]
            and matvec(fixture["kinetic"], fixture["omega"])
            == [Fraction(0)] * 4
        )
        checks["pseudoinverse_rederived"] = (
            fixture["pseudoinverse"]
            == [
                [decode(value) for value in row]
                for row in public["schrodinger_pseudoinverse"]
            ]
            and fixture["pseudoinverse"][0][0] == Fraction(1372, 5625)
            and matvec(fixture["pseudoinverse"], fixture["omega"])
            == [Fraction(0)] * 4
        )
        checks["tangent_and_quadratic_rederived"] = (
            fixture["tangent"] == [decode(value) for value in public["tangent"]]
            and scalar(
                [value * value for value in fixture["omega"]], fixture["tangent"]
            )
            == 0
            and fixture["quadratic"]
            == decode(public["pseudoinverse_quadratic"])
            == Fraction(10, 9)
        )
        checks["second_fundamental_form_rederived"] = (
            fixture["second_fundamental"]
            == decode(public["second_fundamental_value"])
            == Fraction(80, 153)
            and fixture["trial_curvature"]
            == decode(public["trial_normal_curvature"])
            == Fraction(80, 2601)
        )
        checks["mean_curvature_rederived"] = (
            fixture["mean_curvature"]
            == decode(public["mean_curvature"])
            == Fraction(28568, 44217)
        )
        checks["weighted_mean_curvature_rederived"] = (
            fixture["residual_normal"]
            == decode(public["residual_outward_normal"])
            == Fraction(14, 17)
            and fixture["weighted_mean"]
            == decode(public["gaussian_weighted_mean_curvature"])
            == Fraction(-398039, 88434)
            < 0
        )

        independent_points = [
            independent_family(Fraction(q)) for q in range(1, 16)
        ]
        formula_points = [closed_forms(Fraction(q)) for q in range(1, 16)]
        checks["cleared_denominator_identities_rederived_at_fifteen_points"] = all(
            direct["quadratic"] == formula["quadratic"]
            and direct["trial_curvature"] == formula["trial"]
            and direct["mean_curvature"] == formula["mean"]
            and direct["residual_normal"] == formula["normal"]
            and direct["weighted_mean"] == formula["weighted"]
            for direct, formula in zip(independent_points, formula_points)
        ) and "degree at most 14" in certificate["closed_form_mean_curvature"][
            "exact_identity_certificate"
        ]
        checks["curvature_asymptotic_is_degree_certified"] = (
            "q^6 kappa_trial(q)=4" in certificate["cycle_family"]["curvature_asymptotic"]
            and closed_forms(Fraction(8))["trial"]
            < closed_forms(Fraction(4))["trial"]
            < closed_forms(Fraction(2))["trial"]
        )
        checks["weighted_asymptotic_and_sign_are_typed"] = (
            certificate["closed_form_mean_curvature"]["asymptotic"]
            == "lim_(q->infinity) H_2/5(q)=-25/2"
            and closed_forms(Fraction(3))["weighted"] < 0
        )
        geometry = certificate["finite_graph_geometry"]
        checks["general_geometry_formula_is_typed"] = (
            geometry["status"] == "PROVED"
            and "K(r)^+" in geometry["second_fundamental_form"]
            and "P_T" in geometry["mean_curvature"]
            and "Omega^T(-Delta)Omega" in geometry["gaussian_weighted_mean_curvature"]
        )
        applicability = certificate["literature_applicability"]
        checks["literature_applicability_is_scoped"] = (
            "1601.02925" in applicability["gaussian_boundary_reference"]
            and "1711.08825" in applicability["spectral_gap_reference"]
            and applicability["uniform_second_fundamental_form_hypothesis"]
            == "OBSTRUCTED"
            and applicability["positive_weighted_mean_curvature_hypothesis"]
            == "OBSTRUCTED_AT_LAMBDA_0P4"
            and applicability["actual_inverse_tree_jacobian_measure_covered_directly"]
            == "NO"
        )
        disposition = certificate["method_disposition"]
        checks["method_boundary_is_fail_closed"] = (
            disposition["known_curvature_hypothesis_spectral_gap_route"]
            == "OBSTRUCTED_AS_FORMULATED"
            and disposition["other_boundary_or_intrinsic_inequalities"]
            == "NOT_ASSESSED"
            and disposition["normalized_lowest_mode_marginal_bound"] == "OPEN"
            and disposition["actual_interacting_h_minus_one_second_moment_bound"]
            == "OPEN"
            and disposition["interacting_tightness"] == "NOT_ESTABLISHED"
            and disposition["continuum_limit"] == "NOT_ESTABLISHED"
            and disposition["born_rule"] == "NOT_ESTABLISHED"
            and disposition["krein_reconstruction"] == "NOT_ASSESSED"
            and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
        )
        foundation = certificate["foundational_dependency_cut"]
        checks["foundational_boundary_is_fail_closed"] = (
            foundation["classification"] == "USED_BY_DISPLAYED_PROOF"
            and foundation["weakest_base_or_reversal"] == "NOT_ESTABLISHED"
        )
        nonclaims = certificate["does_not_establish"]
        checks["required_nonclaims_are_explicit"] = all(
            any(token in statement for statement in nonclaims)
            for token in (
                "Poincare",
                "lowest-mode",
                "H^-1",
                "continuum",
                "Born",
                "Krein",
                "LORENTZIAN-CAUSAL",
                "literature-priority",
            )
        )
        provenance = certificate["provenance"]
        checks["input_hash_and_primary_references_match"] = (
            len(provenance["inputs"]) == 1
            and all(
                item["sha256"] == file_hash(item["path"])
                for item in provenance["inputs"]
            )
            and [item["arxiv"] for item in provenance["literature"]]
            == ["1601.02925", "1711.08825"]
        )
        checks["dependency_tags_are_exact"] = certificate["dependency_tags"] == [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
        ]
    except (OSError, ValueError, KeyError, TypeError, StopIteration, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return False

    passed = sum(checks.values())
    if not all(checks.values()):
        for error in errors[:3]:
            print(f"[FAIL] schema: {error.message}")
        for name, ok in checks.items():
            if not ok:
                print(f"[FAIL] {name}")
        return False
    print(
        "[PASS] independent BT residual-boundary curvature verifier "
        f"({passed}/{len(checks)})"
    )
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
