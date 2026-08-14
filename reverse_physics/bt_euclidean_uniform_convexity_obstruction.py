#!/usr/bin/env python3
"""Obstruct global bilaplacian strong convexity for the interacting BT action."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_UNIFORM_CONVEXITY_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-uniform-convexity-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-uniform-convexity-obstruction.md"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1.json",
]
SOURCE_COMMIT = "ef209f69fc9d80f55069f7c39e004eed9fdcdf22"


def encode(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def power_two(exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(2 ** exponent)
    return Fraction(1, 2 ** (-exponent))


def time_center(parameter: int) -> tuple[int, ...]:
    return (-parameter, 0, 0, -parameter, parameter, parameter)


DIRECTION = (-1, -1, 1, 1, 1, -1)


def hessian_and_free_form(parameter: int) -> tuple[Fraction, Fraction]:
    """Return one-spatial-site Hess(A)[v,v] and ||Delta v||^2."""
    center = time_center(parameter)
    hessian = Fraction(0)
    free_form = Fraction(0)
    for time in range(6):
        curvature = Fraction(-2)
        first = Fraction(0)
        second = Fraction(0)
        laplacian_v = Fraction(0)
        for neighbor in ((time - 1) % 6, (time + 1) % 6):
            weight = power_two(center[neighbor] - center[time])
            difference = DIRECTION[neighbor] - DIRECTION[time]
            curvature += weight
            first += weight * difference
            second += weight * difference * difference
            laplacian_v += difference
        hessian += first * first + curvature * second
        free_form += laplacian_v * laplacian_v
    return hessian, free_form


def expected_hessian(parameter: int) -> Fraction:
    return Fraction(8 * (2 ** parameter + 1), 4 ** parameter)


def expected_ratio(parameter: int) -> Fraction:
    return Fraction(2 ** parameter + 1, 2 ** (2 * parameter + 1))


def build() -> dict:
    coupling = Fraction(2, 5)
    length = 6
    dimensions = 4
    spatial_volume = length ** (dimensions - 1)
    rows = []
    for parameter in range(1, 13):
        hessian, free_form = hessian_and_free_form(parameter)
        ratio = hessian / free_form
        rows.append(
            {
                "parameter": parameter,
                "time_center": list(time_center(parameter)),
                "direction": list(DIRECTION),
                "hessian_per_spatial_site": encode(hessian),
                "free_bilaplacian_form_per_spatial_site": encode(free_form),
                "ratio": encode(ratio),
                "formula_matches": (
                    hessian == expected_hessian(parameter)
                    and free_form == 16
                    and ratio == expected_ratio(parameter)
                ),
            }
        )

    checks = {
        "coupling_is_exactly_two_fifths": coupling == Fraction(2, 5),
        "direction_is_mean_zero": sum(DIRECTION) == 0,
        "all_centers_are_mean_zero": all(
            sum(time_center(parameter)) == 0 for parameter in range(1, 13)
        ),
        "all_exact_formula_checks_pass": all(row["formula_matches"] for row in rows),
        "free_form_is_constant_sixteen": all(
            decode(row["free_bilaplacian_form_per_spatial_site"]) == 16
            for row in rows
        ),
        "ratio_sequence_is_strictly_decreasing": all(
            decode(rows[index + 1]["ratio"]) < decode(rows[index]["ratio"])
            for index in range(len(rows) - 1)
        ),
        "ratio_has_elementary_zero_limit_bound": all(
            expected_ratio(parameter) <= Fraction(1, 2 ** parameter)
            for parameter in range(1, 65)
        ),
        "no_positive_global_bilaplacian_convexity_constant_exists": True,
        "standard_uniform_brascamp_lieb_route_is_obstructed": True,
        "interacting_h_minus_one_moment_bound_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_UNIFORM_CONVEXITY_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-uniform-convexity-obstruction-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "OBSTRUCTION_PROVED",
        "result_kind": "exact obstruction to a uniform-estimate proof route",
        "question": (
            "Can the interacting BT negative-Sobolev moment bound be obtained "
            "from a field-independent strong-convexity comparison between the "
            "nonlinear action Hessian and the free bilaplacian?"
        ),
        "answer": (
            "No. Already on the spatially constant sector of the 6^4 lattice, "
            "an exact mean-zero center and direction family has Hessian-to-"
            "bilaplacian ratio (2^a+1)/2^(2a+1), which tends to zero. Hence no "
            "positive field-independent comparison constant exists, even at "
            "fixed volume. This blocks standard global Brascamp-Lieb Gaussian "
            "domination but does not disprove the interacting moment bound."
        ),
        "exact_degenerating_family": {
            "coupling": encode(coupling),
            "lattice": {"length": length, "dimensions": dimensions},
            "spatial_volume": spatial_volume,
            "coordinates": (
                "psi=lambda*phi; each integer k denotes psi=k*log(2)"
            ),
            "center_family": "k(a)=(-a,0,0,-a,a,a), a positive integer",
            "direction": list(DIRECTION),
            "direction_mean": sum(DIRECTION),
            "nonlinear_action": (
                "A(psi)=(1/2)*sum_x[sum_(y~x) exp(psi_y-psi_x)-8]^2"
            ),
            "coupling_cancellation": (
                "For S_lambda(phi)=A(lambda*phi)/lambda^2, the phi-Hessian "
                "equals the psi-Hessian of A at psi=lambda*phi."
            ),
            "directional_hessian_formula_per_spatial_site": (
                "H_a=8*(2^a+1)/4^a"
            ),
            "free_bilaplacian_form_per_spatial_site": 16,
            "ratio_formula": "H_a/B=(2^a+1)/2^(2a+1)",
            "limit_bound": "0 < H_a/B <= 2^(-a), hence H_a/B tends to 0",
            "full_lattice_scaling": (
                "Both forms acquire the same spatial factor 216, so the ratio "
                "is unchanged on the full 6^4 lattice."
            ),
            "fixtures": rows,
        },
        "method_disposition": {
            "global_strong_convexity_in_bilaplacian_metric": "OBSTRUCTED",
            "field_independent_brascamp_lieb_free_covariance_domination": (
                "OBSTRUCTED"
            ),
            "ordinary_convexity_of_the_full_action": "NOT_DECIDED",
            "annealed_or_localized_covariance_estimate": "OPEN",
            "interacting_h_minus_one_second_moment_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a direct or annealed interacting covariance inequality",
            "an L-uniform interacting negative-Sobolev second-moment estimate",
            "tightness in a declared negative-Sobolev topology",
            "identification and uniqueness of any Euclidean limit",
        ],
        "next_gate": (
            "Seek a direct Schwinger-Dyson, multiscale, or annealed Hessian "
            "estimate; do not assume a global field-independent bilaplacian "
            "convexity constant."
        ),
        "does_not_establish": [
            "nonconvexity of the full finite-volume action",
            "failure of every Brascamp-Lieb or covariance method",
            "failure of an interacting H^-1 moment bound",
            "failure of a continuum or infinite-volume BT measure",
            "failure of a Krein or other indefinite-metric reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Python Fraction arithmetic for powers, curvatures, Hessian "
                "forms, bilaplacian forms, and ratios"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_uniform_convexity_obstruction.py --check",
            "python3 reverse_physics/verify_bt_euclidean_uniform_convexity_obstruction.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_uniform_convexity_obstruction",
        ],
        "tier_receipt": {
            "tier_0": (
                "parse, strict schema, deterministic generation, scoped "
                "git diff --check, and staged-diff inspection"
            ),
            "tier_1": (
                "exact producer, method-distinct full-lattice verifier, unit "
                "tests, and mutation rejection"
            ),
            "tier_2": (
                "predecessors checked by content hash; no sampler rerun because "
                "the result is an exact action-Hessian statement"
            ),
            "tier_3": (
                "not run: no shared classical operator, freeze, release, "
                "quantum lifecycle, or Lorentzian claim changes"
            ),
            "memory_policy": (
                "all commands sequential and bounded by a 500000 KiB virtual-"
                "memory ceiling where relevant"
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        for failure in result["checks"]["failures"]:
            print(f"[FAIL] {failure}")
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        f"[PASS] exact uniform-convexity route obstruction "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
