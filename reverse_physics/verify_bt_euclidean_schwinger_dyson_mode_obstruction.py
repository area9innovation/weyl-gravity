#!/usr/bin/env python3
"""Independent verifier for the BT Schwinger--Dyson mode obstruction."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SCHWINGER_DYSON_MODE_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-schwinger-dyson-mode-obstruction-v1.schema.json",
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


def full_lattice_forms(
    center_time: tuple[int, ...], direction_time: tuple[int, ...]
) -> dict[str, Fraction]:
    """Enumerate all sites and eight neighbors without the 1D reduction."""
    length = 6
    sites = tuple(product(range(length), repeat=4))
    center = {site: center_time[site[0]] for site in sites}
    direction = {site: direction_time[site[0]] for site in sites}
    action = Fraction(0)
    directional_action = Fraction(0)
    free_directional_action = Fraction(0)
    negative_laplacian_direction: dict[tuple[int, ...], int] = {}
    for site in sites:
        residual = Fraction(-8)
        residual_variation = Fraction(0)
        laplacian_center = 0
        laplacian_direction = 0
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(site)
                neighbor[axis] = (neighbor[axis] + step) % length
                neighbor_site = tuple(neighbor)
                center_difference = center[neighbor_site] - center[site]
                direction_difference = direction[neighbor_site] - direction[site]
                weight = dyadic(center_difference)
                residual += weight
                residual_variation += weight * direction_difference
                laplacian_center += center_difference
                laplacian_direction += direction_difference
        action += residual * residual / 2
        directional_action += residual * residual_variation
        free_directional_action += laplacian_center * laplacian_direction
        negative_laplacian_direction[site] = -laplacian_direction
    return {
        "action": action,
        "directional_action": directional_action,
        "free_directional_action": free_directional_action,
        "center_direction_dot": Fraction(
            sum(center[site] * direction[site] for site in sites)
        ),
        "direction_norm_squared": Fraction(
            sum(direction[site] ** 2 for site in sites)
        ),
        "lowest_mode_residual": Fraction(
            max(
                abs(negative_laplacian_direction[site] - direction[site])
                for site in sites
            )
        ),
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
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )
    recorded_hashes = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["all_four_provenance_hashes_current"] = len(recorded_hashes) == 4 and all(
        digest == file_hash(relative)
        for relative, digest in recorded_hashes.items()
    )

    section = certificate["exact_lowest_mode_counterexample"]
    center = tuple(section["spatially_constant_time_center"])
    direction = tuple(section["spatially_constant_lowest_mode_direction"])
    forms = full_lattice_forms(center, direction)
    full = section["full_lattice"]
    per_site = section["per_spatial_site"]
    checks["full_6_to_the_4_counterexample_reconstructed"] = (
        center == (-8, 8, -2, -8, 2, 8)
        and direction == (2, 1, -1, -2, -1, 1)
        and sum(center) == sum(direction) == 0
        and forms["action"] == 216 * decode(per_site["nonlinear_action"])
        and forms["directional_action"]
        == decode(full["nonlinear_directional_action"])
        and forms["free_directional_action"]
        == decode(full["free_directional_action"])
        and forms["center_direction_dot"] == decode(full["center_direction_dot"])
        and forms["direction_norm_squared"]
        == decode(full["direction_norm_squared"])
    )
    checks["lowest_mode_eigenvector_reconstructed"] = (
        forms["lowest_mode_residual"] == 0
        and section["negative_laplacian_eigenvalue"] == 1
    )
    checks["strict_negative_remainder_factors_reconstructed"] = (
        forms["center_direction_dot"] > 0
        and forms["directional_action"] < 0
        and forms["free_directional_action"] > 0
        and decode(section["coupling"]) == Fraction(2, 5)
    )

    coercivity = certificate["all_volume_quartic_coercivity"]
    fourier = coercivity["lowest_axial_fourier_consequence"]
    checks["all_volume_coercivity_proof_chain_is_typed"] = (
        "cosh" in coercivity["residual_sum_identity"]
        and "sum_(m>=2)" in coercivity["scalar_inequality"]
        and coercivity["cauchy_schwarz"]
        == "sum_x r_x^2 >= (sum_x r_x)^2/N"
        and coercivity["theorem"]
        == "S_lambda(phi)>=(lambda^2/(2N))*E_grad(phi)^2"
    )
    checks["four_dimensional_lowest_mode_constant_reconstructed"] = (
        "N*omega_L^2>=256" in fourier["elementary_bound"]
        and fourier["all_volume_bound"]
        == "S_lambda(phi)>=128*lambda^2*|hat(Phi_L)(e_mu)|^4"
        and decode(fourier["lambda_0p4_coefficient"]) == Fraction(512, 25)
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    checks["scoped_method_disposition"] = certificate["method_disposition"] == {
        "finite_volume_schwinger_dyson_identity": "PROVED",
        "all_volume_quartic_gradient_action_bound": "PROVED",
        "uniform_lowest_mode_action_sublevel_bound": "PROVED",
        "pointwise_nonnegative_mode_remainder": "OBSTRUCTED",
        "annealed_nonnegative_mode_remainder": "OPEN",
        "interacting_h_minus_one_second_moment_bound": "OPEN",
        "interacting_tightness": "NOT_ESTABLISHED",
        "continuum_limit": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["probabilistic_shortfall_is_explicit"] = (
        "partition function" in coercivity["probabilistic_shortfall"]
        and "still required" in coercivity["probabilistic_shortfall"]
    )
    checks["required_nonclaims_present"] = {
        "a negative Gibbs expectation of the mode remainder",
        "failure of the interacting H^-1 moment bound",
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
