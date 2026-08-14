#!/usr/bin/env python3
"""Independent full-lattice verifier for the BT convexity-route obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import product

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_UNIFORM_CONVEXITY_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-uniform-convexity-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dyadic(exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(2**exponent)
    return Fraction(1, 2 ** (-exponent))


Laurent = dict[int, Fraction]


def laurent_add(left: Laurent, right: Laurent) -> Laurent:
    result = dict(left)
    for exponent, coefficient in right.items():
        result[exponent] = result.get(exponent, Fraction(0)) + coefficient
        if result[exponent] == 0:
            del result[exponent]
    return result


def laurent_scale(value: Laurent, scalar: int) -> Laurent:
    return {
        exponent: coefficient * scalar
        for exponent, coefficient in value.items()
        if coefficient * scalar
    }


def laurent_multiply(left: Laurent, right: Laurent) -> Laurent:
    result: Laurent = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = left_exponent + right_exponent
            result[exponent] = (
                result.get(exponent, Fraction(0))
                + left_coefficient * right_coefficient
            )
    return {
        exponent: coefficient
        for exponent, coefficient in result.items()
        if coefficient
    }


def symbolic_reduced_hessian() -> Laurent:
    """Derive the family for an indeterminate q=2^a as a Laurent polynomial."""
    center_coefficients = (-1, 0, 0, -1, 1, 1)
    direction = (-1, -1, 1, 1, 1, -1)
    total: Laurent = {}
    for time in range(6):
        curvature: Laurent = {0: Fraction(-2)}
        first: Laurent = {}
        second: Laurent = {}
        for neighbor in ((time - 1) % 6, (time + 1) % 6):
            exponent = center_coefficients[neighbor] - center_coefficients[time]
            delta = direction[neighbor] - direction[time]
            monomial = {exponent: Fraction(1)}
            curvature = laurent_add(curvature, monomial)
            first = laurent_add(first, laurent_scale(monomial, delta))
            second = laurent_add(second, laurent_scale(monomial, delta * delta))
        total = laurent_add(total, laurent_multiply(first, first))
        total = laurent_add(total, laurent_multiply(curvature, second))
    return total


def full_lattice_forms(parameter: int) -> tuple[Fraction, Fraction]:
    """Enumerate every site and neighbor; do not use the producer reduction."""
    length = 6
    center_time = (-parameter, 0, 0, -parameter, parameter, parameter)
    direction_time = (-1, -1, 1, 1, 1, -1)
    sites = tuple(product(range(length), repeat=4))
    center = {site: center_time[site[0]] for site in sites}
    direction = {site: direction_time[site[0]] for site in sites}
    hessian = Fraction(0)
    free_form = Fraction(0)
    for site in sites:
        curvature = Fraction(-8)
        first_variation = Fraction(0)
        second_variation = Fraction(0)
        laplacian_direction = Fraction(0)
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(site)
                neighbor[axis] = (neighbor[axis] + step) % length
                neighbor_site = tuple(neighbor)
                weight = dyadic(center[neighbor_site] - center[site])
                delta = direction[neighbor_site] - direction[site]
                curvature += weight
                first_variation += weight * delta
                second_variation += weight * delta * delta
                laplacian_direction += delta
        hessian += first_variation**2 + curvature * second_variation
        free_form += laplacian_direction**2
    return hessian, free_form


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
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )
    recorded_hashes = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["all_provenance_hashes_current"] = len(recorded_hashes) == 3 and all(
        digest == file_hash(relative)
        for relative, digest in recorded_hashes.items()
    )

    section = certificate["exact_degenerating_family"]
    rows = section["fixtures"]
    independent_rows_ok = True
    for expected_parameter, row in enumerate(rows, start=1):
        parameter = row["parameter"]
        hessian, free_form = full_lattice_forms(parameter)
        full_ratio = hessian / free_form
        expected_ratio = Fraction(2**parameter + 1, 2 ** (2 * parameter + 1))
        independent_rows_ok &= (
            parameter == expected_parameter
            and tuple(row["time_center"])
            == (-parameter, 0, 0, -parameter, parameter, parameter)
            and tuple(row["direction"]) == (-1, -1, 1, 1, 1, -1)
            and hessian == 216 * decode(row["hessian_per_spatial_site"])
            and free_form
            == 216 * decode(row["free_bilaplacian_form_per_spatial_site"])
            and free_form == 216 * 16
            and full_ratio == decode(row["ratio"])
            and full_ratio == expected_ratio
        )
    checks["all_twelve_full_6_to_the_4_fixtures_reconstructed"] = (
        independent_rows_ok and len(rows) == 12
    )
    ratios = [decode(row["ratio"]) for row in rows]
    checks["strict_decrease_reconstructed"] = all(
        right < left for left, right in zip(ratios, ratios[1:])
    )
    symbolic_hessian = symbolic_reduced_hessian()
    checks["symbolic_laurent_identity_reconstructed"] = symbolic_hessian == {
        -1: Fraction(8),
        -2: Fraction(8),
    }
    checks["zero_limit_bound_follows_for_all_positive_integers"] = (
        symbolic_hessian == {-1: Fraction(8), -2: Fraction(8)}
        and section["ratio_formula"] == "H_a/B=(2^a+1)/2^(2a+1)"
        and section["limit_bound"]
        == "0 < H_a/B <= 2^(-a), hence H_a/B tends to 0"
    )
    checks["coupling_cancellation_is_recorded"] = (
        decode(section["coupling"]) == Fraction(2, 5)
        and "phi-Hessian equals the psi-Hessian"
        in section["coupling_cancellation"]
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    checks["scoped_method_disposition"] = certificate["method_disposition"] == {
        "global_strong_convexity_in_bilaplacian_metric": "OBSTRUCTED",
        "field_independent_brascamp_lieb_free_covariance_domination": "OBSTRUCTED",
        "ordinary_convexity_of_the_full_action": "NOT_DECIDED",
        "annealed_or_localized_covariance_estimate": "OPEN",
        "interacting_h_minus_one_second_moment_bound": "OPEN",
        "interacting_tightness": "NOT_ESTABLISHED",
        "continuum_limit": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["required_nonclaims_present"] = {
        "nonconvexity of the full finite-volume action",
        "failure of every Brascamp-Lieb or covariance method",
        "failure of an interacting H^-1 moment bound",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} ({passed}/{len(checks)})")
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
