#!/usr/bin/env python3
"""Independent verifier for the all-coupling BT OS obstruction."""

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
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_COUPLING_OS_KERNEL_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-all-coupling-os-kernel-obstruction-v1.schema.json",
)


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def pow2(exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(2**exponent)
    return Fraction(1, 2 ** (-exponent))


def half(seed: tuple[int, int, int], n: int) -> tuple[int, ...]:
    return seed + (0,) * (n - 3)


def profile(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return (left[0],) + right + tuple(left[:0:-1])


def direct_time_action(left: tuple[int, ...], right: tuple[int, ...]) -> Fraction:
    values = profile(left, right)
    total = Fraction()
    for site, center in enumerate(values):
        residual = (
            pow2(values[(site - 1) % len(values)] - center)
            + pow2(values[(site + 1) % len(values)] - center)
            - 2
        )
        total += residual * residual
    return total / 2


def full_four_dimensional_action(
    left: tuple[int, ...], right: tuple[int, ...]
) -> Fraction:
    """Enumerate every site and eight neighbors without a spatial reduction."""
    values = profile(left, right)
    length = len(values)
    field = {
        (t, x, y, z): values[t]
        for t in range(length)
        for x in range(length)
        for y in range(length)
        for z in range(length)
    }
    total = Fraction()
    for site, center in field.items():
        residual = Fraction(-8)
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(site)
                neighbor[axis] = (neighbor[axis] + step) % length
                residual += pow2(field[tuple(neighbor)] - center)
        total += residual * residual
    return total / 2


def gap_at_half_length(n: int, full: bool = False) -> Fraction:
    p = half((-7, 0, 7), n)
    q = half((-6, 3, 3), n)
    action = full_four_dimensional_action if full else direct_time_action
    return action(p, p) + action(q, q) - 2 * action(p, q)


def verify(path: str = DEFAULT_CERT) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(cert)
    )
    details = cert.get("checks", {})
    checks["certificate_checks_closed"] = (
        details.get("ok") is True
        and details.get("passed") == details.get("total") == 16
        and details.get("failures") == []
        and all(details.get("details", {}).values())
    )

    hashes = {
        row["path"]: row["sha256"] for row in cert["provenance"]["inputs"]
    }
    checks["predecessor_hashes_current"] = len(hashes) == 2 and all(
        file_hash(relative) == digest for relative, digest in hashes.items()
    )

    l6 = cert["exact_fixtures"]["L6"]
    l8 = cert["exact_fixtures"]["L8_stable_padding"]
    checks["recorded_half_fields_are_reconstructed"] = (
        tuple(l6["p"]) == (-7, 0, 7)
        and tuple(l6["q"]) == (-6, 3, 3)
        and tuple(l8["p"]) == (-7, 0, 7, 0)
        and tuple(l8["q"]) == (-6, 3, 3, 0)
        and sum(l6["p"]) == sum(l6["q"]) == 0
        and sum(l8["p"]) == sum(l8["q"]) == 0
    )

    l6_reduced = gap_at_half_length(3)
    l8_reduced = gap_at_half_length(4)
    checks["reduced_gaps_reconstructed"] = (
        l6_reduced == dec(l6["gap_per_spatial_site"]) == Fraction(28683, 1024)
        and l8_reduced == dec(l8["gap_per_spatial_site"]) == Fraction(1023, 4)
    )
    checks["full_L6_gap_reconstructed"] = (
        gap_at_half_length(3, full=True)
        == 6**3 * l6_reduced
        == Fraction(774441, 128)
    )
    checks["full_L8_gap_reconstructed"] = (
        gap_at_half_length(4, full=True) == 8**3 * Fraction(1023, 4)
    )
    checks["independent_extra_padding_is_stable"] = all(
        gap_at_half_length(n) == Fraction(1023, 4) for n in (5, 7, 11, 16)
    )

    theorem = cert["theorem"]
    checks["coupling_scaling_and_determinant_sign_are_typed"] = (
        theorem["coupling_scope"] == "every finite real lambda!=0"
        and theorem["coupling_scaled_gap"] == "Delta S_lambda=Delta A_L/lambda^2>0"
        and theorem["kernel_determinant"]
        == "det K_lambda=exp(-S_pp-S_qq)*(1-exp(Delta S_lambda))<0"
        and l6_reduced > 0
        and l8_reduced > 0
    )
    disposition = cert["scope_disposition"]
    checks["os_scope_is_promoted_but_continuum_is_not"] = (
        disposition["ordinary_os_at_every_lambda_nonzero_even_L_at_least_6"]
        == "OBSTRUCTED"
        and disposition["ordinary_os_positive_regulator_reconstruction"]
        == "OBSTRUCTED_ON_THE_DECLARED_FAMILY"
        and disposition["continuum_os_for_fixed_cutoff_independent_observables"]
        == "NOT_DECIDED"
        and disposition["interacting_uniform_h_minus_one"] == "OPEN"
    )
    checks["required_nonclaims_present"] = {
        "failure of every possible continuum OS limit for a fixed cutoff-independent observable class",
        "failure or construction of a Krein or other modified reconstruction",
        "boundedness or divergence of the interacting H^-1 moment",
        "a Born rule, scattering probability, or anything LORENTZIAN-CAUSAL",
    }.issubset(set(cert["does_not_establish"]))
    checks["dependency_boundary"] = cert["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} ({passed}/{len(checks)})")
    return all(checks.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args()
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    raise SystemExit(main())
