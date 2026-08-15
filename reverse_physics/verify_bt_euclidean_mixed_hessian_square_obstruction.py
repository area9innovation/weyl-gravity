#!/usr/bin/env python3
"""Independent verifier for the BT mixed-Hessian-square obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import product

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_MIXED_HESSIAN_SQUARE_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-mixed-hessian-square-obstruction-v1.schema.json",
)
Site = tuple[int, int, int, int]


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def torus_neighbors(site: Site, length: int) -> list[Site]:
    result: list[Site] = []
    for axis in range(4):
        for step in (-1, 1):
            changed = list(site)
            changed[axis] = (changed[axis] + step) % length
            result.append(tuple(changed))
    return result


def signed_offset(coordinate: int, length: int) -> int:
    return coordinate if coordinate <= length // 2 else coordinate - length


def independent_hessian_row(length: int = 8) -> dict[Site, Fraction]:
    """Differentiate every residual term, without using the producer stencil."""

    origin = (0, 0, 0, 0)
    profile = tuple(Fraction(value) for value in (1, 2, 3, 4))

    def transfer(left: Site, right: Site) -> Fraction:
        return profile[right[0] % 4] / profile[left[0] % 4]

    def first_derivative(site: Site, variable: Site) -> Fraction:
        result = Fraction()
        for neighbor in torus_neighbors(site, length):
            coefficient = int(neighbor == variable) - int(site == variable)
            result += transfer(site, neighbor) * coefficient
        return result

    def second_derivative(site: Site, left: Site, right: Site) -> Fraction:
        result = Fraction()
        for neighbor in torus_neighbors(site, length):
            left_coefficient = int(neighbor == left) - int(site == left)
            right_coefficient = int(neighbor == right) - int(site == right)
            result += transfer(site, neighbor) * left_coefficient * right_coefficient
        return result

    # A derivative with respect to the origin can occur only in the origin
    # residual or one of its eight neighboring residuals.  Restricting to
    # those nine rows is an exact support reduction, not a copied Hessian
    # stencil.
    active_sites = [origin, *torus_neighbors(origin, length)]
    residuals = {
        site: sum(
            (transfer(site, neighbor) for neighbor in torus_neighbors(site, length)),
            Fraction(),
        )
        - 8
        for site in active_sites
    }
    candidates: list[Site] = []
    for site in product(range(length), repeat=4):
        offsets = [abs(signed_offset(value, length)) for value in site]
        if sum(offsets) <= 2:
            candidates.append(site)
    row: dict[Site, Fraction] = {}
    for variable in candidates:
        value = Fraction()
        for site in active_sites:
            value += (
                first_derivative(site, origin) * first_derivative(site, variable)
                + residuals[site] * second_derivative(site, origin, variable)
            )
        offset = tuple(signed_offset(value, length) for value in variable)
        row[offset] = value
    return row


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

    checks["strict_schema"] = not list(Draft202012Validator(schema).iter_errors(certificate))
    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hashes_current"] = len(inputs) == 2 and all(
        file_hash(row["path"]) == row["sha256"] for row in inputs
    )
    row = independent_hessian_row()
    shells = {
        offset: sum(
            (value for site, value in row.items() if site[0] == offset),
            Fraction(),
        )
        for offset in (-2, -1, 1, 2)
    }
    fixture = certificate["periodic_fixture"]
    certified_shells = {
        int(key): decode(value) for key, value in fixture["axial_shell_sums"].items()
    }
    first = shells[1] - shells[-1]
    second = shells[2] - shells[-2]
    moment = first + 2 * second
    checks["independent_residual_derivative_hessian"] = (
        len(row) == fixture["origin_row_support"] == 41
        and sum(row.values(), Fraction()) == 0
        and shells == certified_shells
        and shells == {
            -2: Fraction(3, 16),
            -1: Fraction(-40),
            1: Fraction(-21),
            2: Fraction(3, 4),
        }
    )
    checks["independent_sine_symbol"] = (
        first == decode(fixture["signed_unit_sine_coefficient"]) == 19
        and second
        == decode(fixture["signed_double_sine_coefficient"])
        == Fraction(9, 16)
        and moment == decode(fixture["first_axial_moment"]) == Fraction(161, 8)
        and moment * moment
        == decode(fixture["first_axial_moment_square"])
        == Fraction(25921, 64)
    )
    obstruction = certificate["long_wave_obstruction"]
    checks["long_wave_boundary"] = (
        obstruction["obstructed_estimate"]
        == "E_q[(Hess S[h_o,k_L])^2]<=C*omega(p_L)^2 uniformly in L and conditional backgrounds"
        and "E_q[M(s)^2]>0" in obstruction["positive_limit"]
        and "p_L^-2" in obstruction["divergence"]
    )
    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["background_uniform_pointwise_bilaplacian_square_bound"]
        == "OBSTRUCTED"
        and disposition["signed_conditional_covariance_response"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE",
    ]
    checks["required_nonclaims"] = {
        "failure of the signed conditional covariance or every heat-bath method",
        "failure of a global finite-volume or volume-uniform Poincare/Witten theorem",
        "the normalized lowest-mode or interacting Gibbs H^-1 bound",
        "a new physical dimension, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
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
