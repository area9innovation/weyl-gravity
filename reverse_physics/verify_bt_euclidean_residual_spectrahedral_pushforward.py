#!/usr/bin/env python3
"""Independent verifier for the BT residual spectrahedral pushforward."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-residual-spectrahedral-pushforward-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
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


def matrix_product(
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


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def remove_row_column(
    matrix: list[list[Fraction]], deleted: int
) -> list[list[Fraction]]:
    return [
        [value for column, value in enumerate(row) if column != deleted]
        for row_index, row in enumerate(matrix)
        if row_index != deleted
    ]


def independent_cycle() -> dict:
    omega = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    size = 4
    adjacency = [
        [int((row - column) % size in (1, size - 1)) for column in range(size)]
        for row in range(size)
    ]
    delta = [
        sum((adjacency[row][column] * omega[column] for column in range(size)), Fraction(0))
        - 2 * omega[row]
        for row in range(size)
    ]
    residual = [delta[row] / omega[row] for row in range(size)]
    kinetic = [
        [
            Fraction(2 + residual[row]) if row == column else Fraction(-adjacency[row][column])
            for column in range(size)
        ]
        for row in range(size)
    ]
    jacobian = [
        [
            -kinetic[row][column] * omega[column] / omega[row]
            for column in range(size)
        ]
        for row in range(size)
    ]
    basis = [
        [Fraction(int(row == column) - int(row == 3)) for column in range(3)]
        for row in range(4)
    ]
    image = matrix_product(jacobian, basis)
    domain_gram = matrix_product(transpose(basis), basis)
    image_gram = matrix_product(transpose(image), image)
    minus_jacobian = [[-value for value in row] for row in jacobian]
    cofactors = [
        determinant(remove_row_column(minus_jacobian, root))
        for root in range(size)
    ]
    edge_products = [omega[site] * omega[(site + 1) % size] for site in range(size)]
    all_edge_product = (
        edge_products[0] * edge_products[1] * edge_products[2] * edge_products[3]
    )
    tree_terms = [all_edge_product / edge for edge in edge_products]
    normal = [value * value for value in omega]
    return {
        "omega": omega,
        "residual": residual,
        "kinetic": kinetic,
        "jacobian": jacobian,
        "normal": normal,
        "cofactors": cofactors,
        "tree_terms": tree_terms,
        "domain_gram_det": determinant(domain_gram),
        "image_gram_det": determinant(image_gram),
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

        fixture = independent_cycle()
        public = certificate["exact_cycle_fixture"]
        checks["positive_scale_section_rederived"] = (
            fixture["omega"] == [decode(value) for value in public["omega"]]
            and fixture["omega"][0]
            * fixture["omega"][1]
            * fixture["omega"][2]
            * fixture["omega"][3]
            == decode(public["product_omega"])
            == 1
        )
        checks["residual_and_action_rederived"] = (
            fixture["residual"] == [decode(value) for value in public["residual"]]
            == [Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2)]
            and sum((value * value for value in fixture["residual"]), Fraction(0)) / 2
            == decode(public["action"])
            == Fraction(11, 4)
        )
        public_kinetic = [
            [decode(value) for value in row]
            for row in public["schrodinger_matrix"]
        ]
        checks["schrodinger_matrix_and_ground_state_rederived"] = (
            public_kinetic == fixture["kinetic"]
            and all(
                sum(
                    (
                        fixture["kinetic"][row][column] * fixture["omega"][column]
                        for column in range(4)
                    ),
                    Fraction(0),
                )
                == 0
                for row in range(4)
            )
        )
        public_jacobian = [
            [decode(value) for value in row]
            for row in public["residual_jacobian"]
        ]
        checks["residual_derivative_rederived"] = (
            public_jacobian == fixture["jacobian"]
            and all(sum(row, Fraction(0)) == 0 for row in fixture["jacobian"])
        )
        checks["boundary_normal_rederived"] = (
            fixture["normal"] == [decode(value) for value in public["boundary_normal"]]
            and all(
                sum(
                    (
                        fixture["normal"][row] * fixture["jacobian"][row][column]
                        for row in range(4)
                    ),
                    Fraction(0),
                )
                == 0
                for column in range(4)
            )
        )
        checks["matrix_tree_cofactors_rederived"] = (
            fixture["cofactors"] == [decode(value) for value in public["tree_cofactors"]]
            == [Fraction(5), Fraction(20), Fraction(5), Fraction(5, 4)]
            and all(
                fixture["cofactors"][index] / fixture["normal"][index]
                == decode(public["tree_density"])
                == 5
                for index in range(4)
            )
        )
        checks["undirected_tree_formula_rederived"] = (
            fixture["tree_terms"]
            == [decode(value) for value in public["undirected_tree_terms"]]
            == [Fraction(1, 2), Fraction(1, 2), Fraction(2), Fraction(2)]
            and sum(fixture["tree_terms"], Fraction(0))
            == decode(public["tree_density"])
        )
        checks["restricted_coarea_jacobian_rederived"] = (
            fixture["domain_gram_det"]
            == decode(public["domain_gram_determinant"])
            == 4
            and fixture["image_gram_det"]
            == decode(public["image_gram_determinant"])
            == 7225
            and Fraction(7225, 4)
            == decode(public["restricted_jacobian_squared"])
            and Fraction(85, 2) == decode(public["restricted_jacobian"])
        )
        checks["vertex_transitive_minimum_fixture_rederived"] = (
            sum(fixture["tree_terms"], Fraction(0)) > 4
            and decode(public["restricted_jacobian"]) > 4 * 4
        )

        theorem = certificate["finite_graph_theorem"]
        differential = certificate["differential_and_tree_jacobian"]
        pushforward = certificate["normalized_pushforward"]
        checks["general_theorem_objects_are_typed"] = (
            theorem["status"] == "PROVED"
            and "positive semidefinite" in theorem["spectrahedron"]
            and "sum_{edges" in theorem["boundary_identity"]
            and "analytic diffeomorphism" in theorem["geometry"]
            and differential["status"] == "PROVED"
            and "cofactor_i(-J)/Omega_i^2" in differential["tree_density"]
            and "undirected spanning trees" in differential["undirected_tree_formula"]
            and "sqrt(N)" in differential["restricted_jacobian"]
            and "log(Jac_H(t)) is convex" in differential["tilt_log_convexity"]
            and "Jac_H(psi)>=N*kappa(G)" in differential["vertex_transitive_minimum"]
            and pushforward["status"] == "EXACT_NORMALIZED_REFORMULATION_ONLY"
            and "dH^(N-1)" in pushforward["surface_measure"]
        )

        provenance = certificate["provenance"]
        checks["input_hashes_match"] = (
            len(provenance["inputs"]) == 2
            and all(
                item["sha256"] == file_hash(item["path"])
                for item in provenance["inputs"]
            )
        )
        disposition = certificate["method_disposition"]
        checks["claim_boundary_is_fail_closed"] = (
            disposition["vertex_transitive_entropy_jacobian_minimum"] == "PROVED"
            and disposition["normalized_lowest_mode_marginal_bound"] == "OPEN"
            and disposition["actual_interacting_h_minus_one_second_moment_bound"]
            == "OPEN"
            and disposition["interacting_tightness"] == "NOT_ESTABLISHED"
            and disposition["continuum_limit"] == "NOT_ESTABLISHED"
            and disposition["ordinary_os_at_lambda_0p4"]
            == "OBSTRUCTED_BY_PREDECESSOR"
            and disposition["born_rule"] == "NOT_ESTABLISHED"
            and disposition["krein_reconstruction"] == "NOT_ASSESSED"
            and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
            and certificate["dependency_tags"]
            == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"]
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
                "lowest-mode marginal",
                "H^-1",
                "continuum",
                "Born",
                "Krein",
                "LORENTZIAN-CAUSAL",
                "literature-novelty",
            )
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
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
        "[PASS] independent BT residual spectrahedral verifier "
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
