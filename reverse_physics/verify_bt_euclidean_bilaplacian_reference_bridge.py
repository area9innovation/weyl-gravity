#!/usr/bin/env python3
"""Independent verifier for the BT bilaplacian reference bridge."""

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
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_BILAPLACIAN_REFERENCE_BRIDGE_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-euclidean-bilaplacian-reference-bridge-v1.schema.json",
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
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def alternating_log_two_lower(terms: int = 20) -> Fraction:
    return sum(
        (Fraction(1 if index % 2 else -1, index) for index in range(1, terms + 1)),
        Fraction(0),
    )


def full_lattice_hessian_forms(
    center_time: tuple[int, ...], direction_time: tuple[int, ...]
) -> dict[str, Fraction]:
    """Enumerate the 6^4 graph, independently of the producer reduction."""
    length = 6
    sites = tuple(product(range(length), repeat=4))
    actual_hessian = Fraction(0)
    center_bilaplacian = 0
    direction_bilaplacian = 0
    bilaplacian_cross = 0
    for site in sites:
        residual = Fraction(-8)
        first_variation = Fraction(0)
        second_variation = Fraction(0)
        laplacian_center = 0
        laplacian_direction = 0
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(site)
                neighbor[axis] = (neighbor[axis] + step) % length
                neighbor = tuple(neighbor)
                center_difference = center_time[neighbor[0]] - center_time[site[0]]
                direction_difference = direction_time[neighbor[0]] - direction_time[site[0]]
                weight = dyadic(center_difference)
                residual += weight
                first_variation += weight * direction_difference
                second_variation += weight * direction_difference**2
                laplacian_center += center_difference
                laplacian_direction += direction_difference
        actual_hessian += first_variation**2 + residual * second_variation
        center_bilaplacian += laplacian_center**2
        direction_bilaplacian += laplacian_direction**2
        bilaplacian_cross += laplacian_center * laplacian_direction
    return {
        "actual_hessian": actual_hessian,
        "center_bilaplacian_integer": Fraction(center_bilaplacian),
        "direction_bilaplacian": Fraction(direction_bilaplacian),
        "bilaplacian_cross": Fraction(bilaplacian_cross),
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

    checks["strict_schema"] = not list(Draft202012Validator(schema).iter_errors(certificate))
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"] == 13
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )
    recorded_hashes = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["all_three_provenance_hashes_current"] = len(recorded_hashes) == 3 and all(
        digest == file_hash(relative) for relative, digest in recorded_hashes.items()
    )

    envelope = certificate["all_volume_bilaplacian_envelope"]
    fixtures_ok = True
    for row in envelope["positive_part_fixtures"]:
        values = tuple(row["mean_zero_vector"])
        positive = sum(value * value for value in values if value >= 0)
        total = sum(value * value for value in values)
        fixtures_ok &= (
            sum(values) == 0
            and decode(row["positive_square_fraction"]) == Fraction(positive, total)
            and decode(row["one_over_dimension"]) == Fraction(1, len(values))
            and positive * len(values) >= total
        )
    checks["mean_zero_positive_part_fixtures_reconstructed"] = fixtures_ok
    checks["envelope_proof_chain_typed"] = (
        envelope["first_bound"] == "A>=B/(2N)"
        and envelope["second_bound"] == "A>=B^2/(8q^2N)"
        and envelope["combined_theorem"] == "A>=B/(4N)+B^2/(16q^2N)"
        and "B<=2q" in envelope["spectral_step"]
    )

    obstruction = certificate["convex_transfer_obstruction"]
    center = tuple(obstruction["center_time"])
    direction = tuple(obstruction["direction"])
    forms = full_lattice_hessian_forms(center, direction)
    checks["full_6_to_the_4_hessian_reconstructed"] = (
        center == (-3, 0, 0, -3, 3, 3)
        and direction == (-1, -1, 1, 1, 1, -1)
        and sum(center) == sum(direction) == 0
        and forms["actual_hessian"] == decode(obstruction["actual_directional_hessian_full"]) == 243
        and forms["center_bilaplacian_integer"] == 216 * 252
        and forms["direction_bilaplacian"] == 216 * 16
        and forms["bilaplacian_cross"] == 0
    )
    log_lower = alternating_log_two_lower()
    checks["log_two_lower_bound_reconstructed"] = (
        log_lower == Fraction(155685007, 232792560)
        and log_lower > Fraction(2, 3)
        and decode(obstruction["log_two_lower_bound"]["value"]) == log_lower
    )
    volume = 6**4
    spatial = 6**3
    degree = 8
    quadratic_hessian = Fraction(2 * spatial * 16, 4 * volume)
    quartic_hessian_lower = Fraction(
        (spatial * 252) * (2 * spatial * 16), 8 * degree**2 * volume
    ) * Fraction(4, 9)
    reference_lower = quadratic_hessian + quartic_hessian_lower
    difference_upper = forms["actual_hessian"] - reference_lower
    checks["strict_nonconvexity_bound_reconstructed"] = (
        quadratic_hessian == Fraction(4, 3)
        and quartic_hessian_lower == 252
        and reference_lower == decode(obstruction["reference_directional_hessian_strict_lower_bound"]) == Fraction(760, 3)
        and difference_upper == decode(obstruction["difference_directional_hessian_strict_upper_bound"]) == Fraction(-31, 3)
    )

    radial = certificate["normalized_radial_reference"]
    free_trace = decode(radial["imported_free_h_minus_one_trace_bound"])
    bound = radial["lambda_0p4_q8_bound"]
    checks["radial_reference_bound_reconstructed"] = (
        free_trace == Fraction(15, 32)
        and decode(bound["rational_prefactor"]) == Fraction(8, 4 * Fraction(2, 5)) == 5
        and bound["squarefree_radicand"] == 15
        and radial["lambda_0p4_q8_reading"] == "5*sqrt(15)"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"
    ]
    checks["scoped_disposition"] = certificate["disposition"] == {
        "actual_all_volume_bilaplacian_envelope": "PROVED",
        "radial_reference_uniform_h_minus_one_bound": "PROVED",
        "pointwise_actual_over_reference_action_domination": "PROVED",
        "convex_perturbation_moment_transfer": "OBSTRUCTED",
        "general_nonconvex_or_annealed_moment_transfer": "OPEN",
        "actual_interacting_h_minus_one_second_moment_bound": "OPEN",
        "interacting_tightness": "NOT_ESTABLISHED",
        "continuum_limit": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["required_nonclaims_present"] = {
        "an H^-1 moment bound for the actual interacting BT Gibbs measure",
        "a valid moment comparison from pointwise action domination alone",
        "a Born rule or Krein reconstruction",
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
