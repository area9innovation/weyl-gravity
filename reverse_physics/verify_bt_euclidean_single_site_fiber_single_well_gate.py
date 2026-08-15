#!/usr/bin/env python3
"""Independent verifier for the BT one-site fiber single-well gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SINGLE_SITE_FIBER_SINGLE_WELL_GATE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-single-site-fiber-single-well-gate-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def power_two(exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(2**exponent)
    return Fraction(1, 2 ** (-exponent))


def torus_neighbors(site: tuple[int, ...], length: int = 4) -> list[tuple[int, ...]]:
    result = []
    for axis in range(4):
        for step in (-1, 1):
            changed = list(site)
            changed[axis] = (changed[axis] + step) % length
            result.append(tuple(changed))
    return result


def reconstruct_fixture() -> dict[str, Fraction]:
    origin = (0, 0, 0, 0)
    neighbors = set(torus_neighbors(origin))

    def exponent(site: tuple[int, ...]) -> int:
        if site == origin:
            return 0
        if site in neighbors:
            return -1
        return -5

    residuals: dict[tuple[int, ...], Fraction] = {}
    first: dict[tuple[int, ...], Fraction] = {}
    second: dict[tuple[int, ...], Fraction] = {}
    relevant = {origin, *neighbors}
    for site in relevant:
        residual = Fraction(-8)
        derivative = Fraction()
        twice = Fraction()
        h_site = int(site == origin)
        for other in torus_neighbors(site):
            weight = power_two(exponent(other) - exponent(site))
            delta = int(other == origin) - h_site
            residual += weight
            derivative += weight * delta
            twice += weight * delta * delta
        residuals[site] = residual
        first[site] = derivative
        second[site] = twice
    curvature = sum(
        first[site] ** 2 + residuals[site] * second[site]
        for site in relevant
    )
    deleted = residuals[next(iter(neighbors))] - Fraction(2)
    a_value = sum(
        power_two(exponent(site) - exponent(origin)) for site in neighbors
    )
    c2 = sum(
        power_two(2 * (exponent(origin) - exponent(site)))
        for site in neighbors
    )
    c1 = sum(
        power_two(exponent(origin) - exponent(site))
        * (residuals[site] - power_two(exponent(origin) - exponent(site)))
        for site in neighbors
    )
    return {
        "A": a_value,
        "C2": c2,
        "C1": c1,
        "deleted": deleted,
        "curvature": curvature,
        "P3": c2 * 3**4 + c1 * 3**3 + 8 * a_value * 3 - a_value**2,
        "P4": c2 * 4**4 + c1 * 4**3 + 8 * a_value * 4 - a_value**2,
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hashes_current"] = len(inputs) == 2 and all(
        file_hash(row["path"]) == row["sha256"] for row in inputs
    )
    theorem = certificate["single_well_theorem"]
    q_value = theorem["bt_degree"]
    checks["product_and_degree_margin"] = (
        q_value == 8
        and decode(theorem["exact_product_lower_bound"]) == q_value**3
        and decode(theorem["exact_q_less_than_16_margin"])
        == 16 * q_value**3 - q_value**4
        > 0
    )
    # At P'=0, eliminating C1 from P is direct polynomial arithmetic.
    samples = [
        (Fraction(2), Fraction(3), Fraction(5)),
        (Fraction(7, 3), Fraction(11, 2), Fraction(4, 5)),
    ]
    stationary_identity = True
    for x, a_value, c2 in samples:
        c1 = -(4 * c2 * x**3 + q_value * a_value) / (3 * x**2)
        p_value = c2 * x**4 + c1 * x**3 + q_value * a_value * x - a_value**2
        reduced = -Fraction(1, 3) * (
            c2 * x**4 - 2 * q_value * a_value * x + 3 * a_value**2
        )
        stationary_identity = stationary_identity and p_value == reduced
    checks["stationary_value_identity"] = stationary_identity
    checks["minimum_curvature_rational_bound"] = (
        2 * 32**2 > 45**2
        and certificate["minimum_curvature"]["bt_action_bound"] == "F''(z_star)>13"
        and certificate["minimum_curvature"]["scope"]
        == "curvature at the minimum only, not global strong convexity"
    )
    rebuilt = reconstruct_fixture()
    fixture = certificate["nonconvex_fixture"]
    checks["direct_lattice_fixture"] = (
        rebuilt["A"] == decode(fixture["A"]) == 4
        and rebuilt["C2"] == decode(fixture["C2"]) == 32
        and rebuilt["C1"] == decode(fixture["C1"]) == -121
        and rebuilt["deleted"]
        == decode(fixture["deleted_neighbor_residuals"][0])
        == Fraction(-121, 16)
        and rebuilt["curvature"]
        == decode(fixture["fiber_curvature_at_z_0"])
        == -57
        and rebuilt["P3"] == decode(fixture["P_at_3"]) < 0
        and rebuilt["P4"] == decode(fixture["P_at_4"]) > 0
    )
    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["all_one_site_fibers_single_well"]
        == "PROVED_FOR_Q_LESS_THAN_16"
        and disposition["global_one_site_strong_convexity"]
        == "OBSTRUCTED_BY_EXACT_L4_FIXTURE"
        and disposition["uniform_one_site_poincare"] == "OPEN"
        and disposition["uniform_inter_site_influence"] == "OPEN"
        and disposition["volume_uniform_witten_coercivity"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
    )
    checks["literature_boundary"] = (
        certificate["literature_hypothesis_audit"]["import_status"]
        == "METHODS_IDENTIFIED_THEOREMS_NOT_IMPORTED"
        and certificate["provenance"]["literature_sources"]
        == [
            "https://arxiv.org/abs/2112.07584",
            "https://arxiv.org/abs/1307.2338",
            "https://arxiv.org/abs/2007.10869",
        ]
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    checks["required_nonclaims"] = {
        "a uniform one-site Poincare or logarithmic-Sobolev inequality",
        "a volume-uniform global Poincare or Witten one-form estimate",
        "the normalized lowest-mode or interacting Gibbs H^-1 bound",
        "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
