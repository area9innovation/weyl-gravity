#!/usr/bin/env python3
"""Independently verify the BT torus top-band flow certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERTIFICATE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_TOP_BAND_FLOW_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-top-band-flow-v1.schema.json",
)


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_fixture() -> dict[str, Fraction]:
    side = 4
    count = side**4
    q = 8
    diameter = 8
    adjacency = [[] for _ in range(count)]
    edges: list[tuple[int, int]] = []
    for left in range(count):
        digits = [0, 0, 0, 0]
        work = left
        for coordinate in range(3, -1, -1):
            digits[coordinate] = work % side
            work //= side
        for coordinate in range(4):
            other = digits[:]
            other[coordinate] = (other[coordinate] + 1) % side
            right = 0
            for digit in other:
                right = side * right + digit
            edges.append((left, right))
            adjacency[left].append(right)
            adjacency[right].append(left)
    omega = [Fraction(1)] * count
    omega[0] = Fraction(1_000_000)
    residual = [
        sum((omega[y] / omega[x] - 1 for y in adjacency[x]), Fraction())
        for x in range(count)
    ]
    gradient = [
        sum(
            (
                residual[y] * omega[x] / omega[y]
                - residual[x] * omega[y] / omega[x]
                for y in adjacency[x]
            ),
            Fraction(),
        )
        for x in range(count)
    ]
    maximum = max(
        max(omega[x] / omega[y], omega[y] / omega[x]) for x, y in edges
    )
    c = [Fraction() for _ in range(count)]
    oriented: list[tuple[int, int, Fraction]] = []
    equal: list[tuple[int, int]] = []
    for x, y in edges:
        if omega[x] == omega[y]:
            equal.append((x, y))
        else:
            tail, head = (x, y) if omega[x] < omega[y] else (y, x)
            alpha = omega[head] / (omega[tail] * maximum)
            c[tail] += alpha
            oriented.append((tail, head, alpha))
    flow_mass = sum((value**2 for value in c), Fraction())
    h = [residual[x] - maximum * c[x] for x in range(count)]
    main = [Fraction() for _ in range(count)]
    error_div = [Fraction() for _ in range(count)]
    edge_error = Fraction()
    top_mass = Fraction()
    for tail, head, alpha in oriented:
        flow = c[tail] * alpha
        top_mass += flow if alpha >= Fraction(1, 2) else 0
        error = maximum * h[tail] * alpha - c[head] / alpha - h[head] / (maximum * alpha)
        edge_error += error**2
        main[tail] -= flow
        main[head] += flow
        error_div[tail] -= error
        error_div[head] += error
    for x, y in equal:
        error = residual[x] - residual[y]
        edge_error += error**2
        error_div[x] -= error
        error_div[y] += error
    reconstructed = [maximum**2 * main[x] + error_div[x] for x in range(count)]
    if reconstructed != gradient:
        raise AssertionError("current reconstruction failed")
    return {
        "maximum": maximum,
        "F": flow_mass,
        "top_mass": top_mass,
        "main_norm": sum((value**2 for value in main), Fraction()),
        "edge_error": edge_error,
        "error_divergence": sum((value**2 for value in error_div), Fraction()),
        "residual_norm": sum((value**2 for value in residual), Fraction()),
        "gradient_norm": sum((value**2 for value in gradient), Fraction()),
        "edge_ceiling": 7 * q**2 * maximum**2 * flow_mass + 6 * q**3 * count,
        "divergence_ceiling": 14 * q**3 * maximum**2 * flow_mass + 12 * q**4 * count,
        "condition": 256 * q**3 * diameter**2 * count * flow_mass,
    }


def verify(certificate: dict[str, object]) -> list[tuple[str, bool]]:
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)
    try:
        jsonschema.Draft202012Validator(schema).validate(certificate)
        schema_ok = True
    except jsonschema.ValidationError:
        schema_ok = False
    inputs_ok = all(
        os.path.isfile(os.path.join(ROOT, row["path"]))
        and file_hash(os.path.join(ROOT, row["path"])) == row["sha256"]
        for row in certificate["provenance"]["inputs"]
    )
    stored = certificate["exact_fixture"]
    actual = independent_fixture()
    fixture_ok = (
        dec(stored["maximum_edge_ratio"]) == actual["maximum"]
        and dec(stored["density_mass_F"]) == actual["F"]
        and dec(stored["top_half_band_flow_mass"]) == actual["top_mass"]
        and dec(stored["main_divergence_norm_squared"]) == actual["main_norm"]
        and dec(stored["error_edge_norm_squared"]) == actual["edge_error"]
        and dec(stored["error_edge_norm_ceiling"]) == actual["edge_ceiling"]
        and dec(stored["error_divergence_norm_squared"]) == actual["error_divergence"]
        and dec(stored["error_divergence_norm_ceiling"]) == actual["divergence_ceiling"]
        and dec(stored["top_condition_right"]) == actual["condition"]
        and dec(stored["residual_norm_squared"]) == actual["residual_norm"]
        and dec(stored["gradient_norm_squared"]) == actual["gradient_norm"]
        and all(stored["checks"].values())
    )
    error_constants = (
        3 * 8**2 + 7 * 8 <= 7 * 8**2
        and Fraction(11, 2) * 8**3 <= 6 * 8**3
        and 14 <= 4**2
        and 12 <= 4**2
    )
    top_constants = (
        certificate["top_band_theorem"]["hypothesis"] == "W^2>=256*q^3*D^2*N*F"
        and certificate["top_band_theorem"]["divergence_floor"] == "||div(f)||_2>=1/(D*sqrt(N))"
        and certificate["top_band_theorem"]["quotient_floor"] == "Q>=W^2/(4*q^2*D^2*N^2)>=64*q*F/N>=64*q/N"
    )
    dichotomy = certificate["four_torus_dichotomy"]
    dichotomy_constants = (
        24**2 * 8**4 >= 256 * 8**3
        and 48 * 8**2 == 3072
        and dichotomy["common_contrast_hypothesis"] == "W>=24*q^2*D*N^(2/3)"
        and dichotomy["torus_sufficient_condition"] == "W>=3072*L^(11/3)"
        and dichotomy["normalized_conclusion"] == "Q/omega_L^2>=32/pi^4"
    )
    boundary_ok = (
        certificate["research_disposition"]["moderate_sparse_multiband_sector"] == "OPEN"
        and certificate["research_disposition"]["all_field_torus_scaled_PL"] == "OPEN"
        and "a lower bound for all edge contrasts on T_L^4" in certificate["does_not_establish"]
        and "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"]
    )
    self_checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        ("producer_not_imported", "bt_euclidean_torus_top_band_flow" not in sys.modules),
        ("predecessor_hashes", inputs_ok),
        ("fixture_reconstruction", fixture_ok),
        ("refined_error_constants", error_constants),
        ("top_band_constants", top_constants),
        ("dense_sparse_dichotomy", dichotomy_constants),
        ("dependency_tags", certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"]),
        ("claim_boundaries", boundary_ok),
        ("self_checks", self_checks["ok"] is True and self_checks["passed"] == self_checks["total"] == 10 and all(self_checks["details"].values())),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default=DEFAULT_CERTIFICATE)
    args = parser.parse_args(argv)
    try:
        with open(args.certificate, encoding="utf-8") as handle:
            certificate = json.load(handle)
        checks = verify(certificate)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return 1
    for name, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(value for _, value in checks)
    print(f"BT torus top-band verifier: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
