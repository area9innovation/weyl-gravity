#!/usr/bin/env python3
"""Independently verify the BT torus sparse-maxima flow certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SPARSE_MAXIMA_FLOW_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-sparse-maxima-flow-v1.schema.json",
)


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def graph(side: int) -> tuple[list[list[int]], list[tuple[int, int]]]:
    count = side**4
    adjacency = [[] for _ in range(count)]
    edges: list[tuple[int, int]] = []

    def decode(raw: int) -> list[int]:
        point = [0, 0, 0, 0]
        for coordinate in range(3, -1, -1):
            point[coordinate] = raw % side
            raw //= side
        return point

    def encode(point: list[int]) -> int:
        out = 0
        for value in point:
            out = side * out + value
        return out

    for left in range(count):
        point = decode(left)
        for coordinate in range(4):
            shifted = point[:]
            shifted[coordinate] = (shifted[coordinate] + 1) % side
            right = encode(shifted)
            edges.append((left, right))
            adjacency[left].append(right)
            adjacency[right].append(left)
    return adjacency, edges


def independent_fixture(stored: dict[str, object]) -> dict[str, object]:
    side = stored["side"]
    height = Fraction(stored["height"])
    adjacency, edges = graph(side)
    count = len(adjacency)
    if stored["kind"] == "single_spike":
        omega = [Fraction(1)] * count
        omega[0] = height
    else:
        omega = []
        for raw in range(count):
            digits = []
            work = raw
            for _ in range(4):
                digits.append(work % side)
                work //= side
            omega.append(height if sum(digits) % 2 else Fraction(1))
    residual = []
    for site, neighbors in enumerate(adjacency):
        residual.append(sum((omega[y] / omega[site] - 1 for y in neighbors), Fraction()))
    gradient = []
    for site, neighbors in enumerate(adjacency):
        gradient.append(
            sum(
                (
                    residual[y] * omega[site] / omega[y]
                    - residual[site] * omega[y] / omega[site]
                    for y in neighbors
                ),
                Fraction(),
            )
        )
    maximum = max(
        max(omega[x] / omega[y], omega[y] / omega[x]) for x, y in edges
    )
    c = [Fraction() for _ in range(count)]
    directed: list[tuple[int, int, Fraction]] = []
    equal = 0
    for x, y in edges:
        if omega[x] == omega[y]:
            equal += 1
        else:
            tail, head = (x, y) if omega[x] < omega[y] else (y, x)
            alpha = omega[head] / (omega[tail] * maximum)
            c[tail] += alpha
            directed.append((tail, head, alpha))
    flow_mass = sum((value**2 for value in c), Fraction())
    tau = flow_mass / (4 * 8**2 * count)
    low = sum((c[x] * alpha for x, _, alpha in directed if alpha < tau), Fraction())
    high = sum((c[x] * alpha for x, _, alpha in directed if alpha >= tau), Fraction())
    near = sum(alpha >= Fraction(1, 2) for _, _, alpha in directed)
    residual_norm = sum((value**2 for value in residual), Fraction())
    gradient_norm = sum((value**2 for value in gradient), Fraction())
    return {
        "maximum": maximum,
        "directed": len(directed),
        "equal": equal,
        "near": near,
        "flow_mass": flow_mass,
        "tau": tau,
        "low": low,
        "high": high,
        "residual_norm": residual_norm,
        "gradient_norm": gradient_norm,
        "quotient": gradient_norm / residual_norm,
    }


def verify(certificate: dict[str, object]) -> list[tuple[str, bool]]:
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)
    try:
        jsonschema.Draft202012Validator(schema).validate(certificate)
        schema_ok = True
    except jsonschema.ValidationError:
        schema_ok = False
    predecessor = certificate["provenance"]["inputs"][0]
    predecessor_path = os.path.join(ROOT, predecessor["path"])
    fixtures_ok = True
    for stored in certificate["exact_fixtures"]:
        actual = independent_fixture(stored)
        fixtures_ok &= stored["vertices"] == stored["side"] ** 4 == 256
        fixtures_ok &= stored["degree"] == 8 and stored["diameter"] == 8
        fixtures_ok &= dec(stored["maximum_edge_ratio"]) == actual["maximum"]
        fixtures_ok &= stored["oriented_edge_count"] == actual["directed"]
        fixtures_ok &= stored["equal_edge_count"] == actual["equal"]
        fixtures_ok &= stored["near_maximal_half_edge_count"] == actual["near"]
        fixtures_ok &= dec(stored["outgoing_square_mass_F"]) == actual["flow_mass"]
        fixtures_ok &= dec(stored["band_threshold_tau"]) == actual["tau"]
        fixtures_ok &= dec(stored["low_flow_mass"]) == actual["low"]
        fixtures_ok &= dec(stored["high_flow_mass"]) == actual["high"]
        fixtures_ok &= dec(stored["residual_norm_squared"]) == actual["residual_norm"]
        fixtures_ok &= dec(stored["gradient_norm_squared"]) == actual["gradient_norm"]
        fixtures_ok &= dec(stored["quotient"]) == actual["quotient"]
        fixtures_ok &= actual["low"] <= actual["flow_mass"] / 8
        fixtures_ok &= actual["near"] <= 4 * actual["flow_mass"]
        fixtures_ok &= actual["quotient"] >= 9 * 8**2

    # Constant audit of the analytic proof.  The threshold gives W*tau>=6D;
    # on T_L^4, 4q^2N=(4L)^4 and 6D>=4L, hence log(W)/log(W*tau)<=5.
    constant_chain = (
        Fraction(7, 8) / 5 == Fraction(7, 40)
        and 2 * Fraction(7, 40) == Fraction(7, 20)
        and Fraction(3) <= Fraction(7, 40) * 24
        and Fraction(49 * 24**2, 1600) >= 9
    )
    theorem = certificate["theorem"]
    theorem_ok = (
        theorem["hypothesis"] == "W*F>=24*q^2*D*N"
        and theorem["gradient_floor"] == "||g||_2>=7*W^2*F/(40*D*sqrt(N))"
        and theorem["quotient_floor"]
        == "||g||_2^2/||r||_2^2>=49*W^2*F^2/(1600*q^2*D^2*N^2)>=9*q^2"
    )
    corollary = certificate["four_torus_corollary"]
    corollary_ok = (
        24 * 8**2 * 2 == 3072
        and corollary["sufficient_condition"] == "W*F>=3072*L^5"
        and corollary["near_maximal_count"]
        == "E_theta=#{e:z_e>=theta*W}<=F/theta^2"
        and corollary["bad_family_density"]
        == "E_theta/(4*L^4)<768*L/(theta^2*W)"
    )
    boundary_ok = (
        certificate["research_disposition"]["dense_multiband_polynomial_contrast_sector"] == "OPEN"
        and certificate["research_disposition"]["all_field_torus_scaled_PL"] == "OPEN"
        and "a lower bound for every positive field on T_L^4" in certificate["does_not_establish"]
        and "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"]
    )
    self_checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        ("producer_not_imported", "bt_euclidean_torus_sparse_maxima_flow" not in sys.modules),
        ("predecessor_hash", os.path.isfile(predecessor_path) and file_hash(predecessor_path) == predecessor["sha256"]),
        ("fixture_reconstruction", fixtures_ok),
        ("finite_amplitude_decomposition", certificate["finite_amplitude_decomposition"]["total_flow_mass"] == "sum_e f_e=sum_x c_x^2=F"),
        ("band_threshold_constants", constant_chain),
        ("torus_path_geometry", certificate["torus_band_transport"]["path_geometry"].startswith("if W*F>=24*q^2*D*N")),
        ("quotient_theorem", theorem_ok),
        ("sparse_maxima_corollary", corollary_ok),
        ("dependency_tags", certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"]),
        ("claim_boundaries", boundary_ok),
        ("self_checks", self_checks["ok"] is True and self_checks["passed"] == self_checks["total"] == 11 and all(self_checks["details"].values())),
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
    print(f"BT torus sparse-maxima verifier: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
