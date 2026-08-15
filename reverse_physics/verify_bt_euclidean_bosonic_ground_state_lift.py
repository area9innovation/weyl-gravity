#!/usr/bin/env python3
"""Independent verifier for the BT bosonic ground-state lift."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_BOSONIC_GROUND_STATE_LIFT_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-bosonic-ground-state-lift-v1.schema.json",
)
EXPECTED_INPUT = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_DETERMINANT_PUSHFORWARD_V1.json"
)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def frac_vector(values: list[dict[str, int]]) -> tuple[Fraction, ...]:
    return tuple(frac(value) for value in values)


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def det3(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def delete_root(
    matrix: tuple[tuple[Fraction, ...], ...], root: int
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(value for column, value in enumerate(row) if column != root)
        for index, row in enumerate(matrix)
        if index != root
    )


def independent_fixture() -> dict:
    omega = (Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2))
    edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    residual = tuple(
        (omega[(site - 1) % 4] + omega[(site + 1) % 4] - 2 * omega[site])
        / omega[site]
        for site in range(4)
    )
    kinetic = [[Fraction() for _ in range(4)] for _ in range(4)]
    for site in range(4):
        kinetic[site][site] = 2 + residual[site]
    for left, right in edges:
        kinetic[left][right] = kinetic[right][left] = -1
    matrix = tuple(tuple(row) for row in kinetic)
    norm2 = sum((value * value for value in omega), Fraction())
    q = tuple(value * value / norm2 for value in omega)
    cofactors = tuple(det3(delete_root(matrix, root)) for root in range(4))
    det_prime = sum(cofactors, Fraction())
    conductances = tuple(omega[left] * omega[right] for left, right in edges)
    tree_products = tuple(
        __import__("math").prod(
            conductances[index] for index in range(4) if index != omitted
        )
        for omitted in range(4)
    )
    return {
        "omega": omega,
        "kinetic": matrix,
        "norm2": norm2,
        "q": q,
        "cofactors": cofactors,
        "det_prime": det_prime,
        "integrated": tuple(qi / cofactor for qi, cofactor in zip(q, cofactors)),
        "conductances": conductances,
        "tree_products": tree_products,
        "tree_sum": sum(tree_products, Fraction()),
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(Draft202012Validator(schema).iter_errors(cert))
    inputs = cert.get("provenance", {}).get("inputs", [])
    checks["provenance_hash_current"] = (
        len(inputs) == 1
        and inputs[0].get("path") == EXPECTED_INPUT
        and inputs[0].get("sha256") == file_hash(EXPECTED_INPUT)
    )

    exact = independent_fixture()
    public = cert.get("cycle_four_fixture", {})
    checks["independent_ground_equation"] = all(
        sum(
            (exact["kinetic"][row][column] * exact["omega"][column]
             for column in range(4)),
            Fraction(),
        ) == 0
        for row in range(4)
    )
    checks["independent_root_cofactor_identity"] = (
        frac_vector(public.get("root_probabilities", []))
        == exact["q"]
        == (Fraction(4, 25), Fraction(16, 25), Fraction(4, 25), Fraction(1, 25))
        and frac_vector(public.get("principal_minors", []))
        == exact["cofactors"]
        == (Fraction(5), Fraction(20), Fraction(5), Fraction(5, 4))
        and frac(public.get("pseudodeterminant", {}))
        == exact["det_prime"]
        == Fraction(125, 4)
        and all(
            cofactor == exact["det_prime"] * q
            for cofactor, q in zip(exact["cofactors"], exact["q"])
        )
    )
    checks["independent_gaussian_factor"] = (
        frac_vector(public.get("rootwise_integrated_factors", []))
        == exact["integrated"]
        == (Fraction(4, 125),) * 4
        and cert.get("bosonic_lift_theorem", {}).get("field_count")
        == "two real commuting pinned Gaussian fields"
    )
    checks["independent_ground_state_transform"] = (
        frac_vector(public.get("ground_state_conductances_cyclic_order", []))
        == exact["conductances"]
        == (Fraction(2), Fraction(2), Fraction(1, 2), Fraction(1, 2))
        and frac_vector(public.get("spanning_tree_products", []))
        == exact["tree_products"]
        == (Fraction(1, 2), Fraction(1, 2), Fraction(2), Fraction(2))
        and frac(public.get("spanning_tree_sum", {})) == exact["tree_sum"] == 5
    )

    comparator = cert.get("hyperbolic_comparator", {})
    disposition = cert.get("method_disposition", {})
    checks["determinant_statistics_boundary"] = (
        comparator.get("bt_determinant_power") == "-1 on det'(K)"
        and comparator.get("vrjp_determinant_power")
        == "+1/2 on the spanning-tree determinant"
        and frac(comparator.get("exponent_difference", {})) == Fraction(3, 2)
        and comparator.get("direct_import_disposition")
        == "OBSTRUCTED_AS_MEASURE_IDENTITY"
        and disposition.get("published_vrjp_hyperbolic_localization_direct_import")
        == "OBSTRUCTED"
    )
    checks["claim_boundary"] = (
        disposition.get("positive_auxiliary_probability") == "PROVED_FINITE_GRAPH"
        and disposition.get("pinned_gff_random_conductance_bridge")
        == "PROVED_FINITE_GRAPH"
        and disposition.get("bt_specific_annealed_witten_or_poincare_bound") == "OPEN"
        and disposition.get("actual_interacting_h_minus_one_second_moment") == "OPEN"
        and "a bound or divergence for the actual interacting H^-1 moment"
        in cert.get("does_not_establish", [])
    )
    published = cert.get("checks", {})
    checks["producer_checks_consistent"] = (
        published.get("ok") is True
        and published.get("passed") == published.get("total") == 11
        and published.get("failures") == []
        and all(published.get("details", {}).values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    ok = all(checks.values())
    print(
        "BT bosonic ground-state lift independent verifier: "
        f"{'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})"
    )
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args()
    return 0 if verify(args.path) else 1


if __name__ == "__main__":
    raise SystemExit(main())
