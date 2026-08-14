#!/usr/bin/env python3
"""Independent verifier for the exact BT lambda=0.4 OS obstruction."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-lambda04-os-kernel-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def power_two(exponent: int) -> Fraction:
    return Fraction(2 ** exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def full_lattice_action(
    negative: tuple[int, int, int], positive: tuple[int, int, int]
) -> Fraction:
    """Reconstruct all 6^4 sites and eight neighbors, not the 1D reduction."""
    length = 6
    time_values = (
        negative[0],
        positive[0],
        positive[1],
        positive[2],
        negative[2],
        negative[1],
    )
    field = {
        (time, x, y, z): time_values[time]
        for time in range(length)
        for x in range(length)
        for y in range(length)
        for z in range(length)
    }
    squared_curvature = Fraction(0)
    for site, value in field.items():
        neighbors = []
        for axis in range(4):
            for step in (-1, 1):
                shifted = list(site)
                shifted[axis] = (shifted[axis] + step) % length
                neighbors.append(tuple(shifted))
        curvature = sum(
            (power_two(field[neighbor] - value) for neighbor in neighbors),
            Fraction(0),
        ) - 8
        squared_curvature += curvature * curvature
    return Fraction(25, 8) * squared_curvature


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
    checks["all_provenance_hashes_current"] = bool(recorded_hashes) and all(
        digest == file_hash(relative)
        for relative, digest in recorded_hashes.items()
    )

    section = certificate["finite_volume_kernel_obstruction"]
    p = tuple(section["half_centers"]["p"])
    q = tuple(section["half_centers"]["q"])
    spp = full_lattice_action(p, p)
    sqq = full_lattice_action(q, q)
    spq = full_lattice_action(p, q)
    sqp = full_lattice_action(q, p)
    recorded = section["full_actions"]
    gap = spp + sqq - 2 * spq
    checks["half_centers_reconstructed"] = (
        p == (-7, 0, 7)
        and q == (-6, 3, 3)
        and sum(p) == sum(q) == 0
    )
    checks["full_6_to_the_4_actions_reconstructed"] = (
        spp == decode(recorded["S_pp"])
        and sqq == decode(recorded["S_qq"])
        and spq == decode(recorded["S_pq"])
    )
    checks["reflection_symmetry_reconstructed"] = spq == sqp
    checks["strict_gap_reconstructed"] = (
        gap == Fraction(19361025, 512)
        and gap == decode(section["log_kernel_convexity_gap_full_lattice"])
        and gap > 0
    )
    checks["negative_determinant_identity"] = (
        section["determinant_identity"]
        == "det(K)=exp(-S_pp-S_qq)*(1-exp(S_pp+S_qq-2*S_pq))<0"
        and gap > 0
    )

    bump = section["bump_cylinder_lemma"]
    half_dimension = 3 * 6 ** 3
    checks["zero_mode_slice_and_bump_scaling_are_typed"] = (
        bump["ambient_half_space"] == f"R^{half_dimension}"
        and bump["center_condition"] == "p,q lie in ker(ell)"
        and "2*n-1" in bump["scaling_limit"]
        and "strictly negative" in bump["consequence"]
    )

    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    checks["scoped_disposition"] = certificate["disposition"] == {
        "ordinary_os_reflection_positivity_at_lambda_zero": "OBSTRUCTED",
        "ordinary_os_reflection_positivity_near_lambda_zero": (
            "OBSTRUCTED_ON_SOME_OPEN_INTERVAL"
        ),
        "ordinary_os_reflection_positivity_at_lambda_0p4": "OBSTRUCTED",
        "lambda_0p4_numerical_preflight_role": "SUPPORTING_ONLY",
        "ordinary_os_reflection_positivity_at_every_nonzero_coupling": (
            "NOT_ESTABLISHED"
        ),
        "krein_compatible_reconstruction": "NOT_ASSESSED",
        "interacting_uniform_estimate": "OPEN",
        "continuum_limit": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["required_nonclaims_present"] = {
        "reflection-positivity failure at every nonzero coupling",
        "failure of a Krein or other indefinite-metric reconstruction",
        "an interacting volume-uniform estimate",
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
