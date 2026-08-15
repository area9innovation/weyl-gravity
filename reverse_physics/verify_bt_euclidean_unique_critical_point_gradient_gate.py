#!/usr/bin/env python3
"""Independent exact verifier for the BT critical-point/gradient gate."""

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
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "UNIQUE_CRITICAL_POINT_GRADIENT_GATE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "unique-critical-point-gradient-gate-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independently_reconstruct_fixture(pattern: list[list[int]]) -> dict[str, Fraction]:
    """Use undirected edges, rather than the producer's directed rows."""
    length = len(pattern)
    omega = [Fraction(value, 1000) for row in pattern for value in row]
    edges: list[tuple[int, int]] = []
    for first in range(length):
        for second in range(length):
            site = first * length + second
            edges.append((site, first * length + (second + 1) % length))
            edges.append((site, ((first + 1) % length) * length + second))
    laplacian = [Fraction(0) for _ in omega]
    for left, right in edges:
        difference = omega[right] - omega[left]
        laplacian[left] += difference
        laplacian[right] -= difference
    residual = [laplacian[index] / omega[index] for index in range(len(omega))]
    gradient = [Fraction(0) for _ in omega]
    for left, right in edges:
        left_current = omega[right] * residual[left] / omega[left]
        right_current = omega[left] * residual[right] / omega[right]
        gradient[left] += right_current - left_current
        gradient[right] += left_current - right_current
    residual_norm = sum((value**2 for value in residual), Fraction(0))
    gradient_norm = sum((value**2 for value in gradient), Fraction(0))
    return {
        "residual_norm": residual_norm,
        "gradient_norm": gradient_norm,
        "quotient": gradient_norm / residual_norm,
        "gap": 4 * residual_norm - gradient_norm,
        "gradient_sum": sum(gradient, Fraction(0)),
        "laplacian_sum": sum(laplacian, Fraction(0)),
        "weighted_residual_sum": sum(
            (omega[index] * residual[index] for index in range(len(omega))),
            Fraction(0),
        ),
    }


def independently_reconstruct_four_dimensional_embedding(
    pattern: list[list[int]],
) -> dict[str, Fraction]:
    """Enumerate the 4^4 torus directly, with the field constant on two axes."""
    sites = list(product(range(4), repeat=4))
    index = {site: position for position, site in enumerate(sites)}
    omega = [Fraction(pattern[site[0]][site[1]], 1000) for site in sites]
    laplacian = [Fraction(0) for _ in sites]
    edges: list[tuple[int, int]] = []
    for site in sites:
        left = index[site]
        for axis in range(4):
            neighbor = list(site)
            neighbor[axis] = (neighbor[axis] + 1) % 4
            right = index[tuple(neighbor)]
            edges.append((left, right))
            difference = omega[right] - omega[left]
            laplacian[left] += difference
            laplacian[right] -= difference
    residual = [laplacian[position] / omega[position] for position in range(256)]
    gradient = [Fraction(0) for _ in sites]
    for left, right in edges:
        left_current = omega[right] * residual[left] / omega[left]
        right_current = omega[left] * residual[right] / omega[right]
        gradient[left] += right_current - left_current
        gradient[right] += left_current - right_current
    return {
        "residual_norm": sum((value**2 for value in residual), Fraction(0)),
        "gradient_norm": sum((value**2 for value in gradient), Fraction(0)),
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
    recorded = {
        item["path"]: item["sha256"] for item in certificate["provenance"]["inputs"]
    }
    checks["provenance_hashes_current"] = len(recorded) == 2 and all(
        file_hash(relative) == digest for relative, digest in recorded.items()
    )
    section = certificate["exact_sharp_gradient_obstruction"]
    rebuilt = independently_reconstruct_fixture(section["omega_integer_pattern"])
    checks["residual_norm_reconstructed"] = (
        rebuilt["residual_norm"] == decode(section["residual_norm_squared"])
    )
    checks["gradient_norm_reconstructed"] = (
        rebuilt["gradient_norm"] == decode(section["gradient_norm_squared"])
    )
    checks["quotient_and_gap_reconstructed"] = (
        rebuilt["quotient"] == decode(section["gradient_quotient"])
        and rebuilt["gap"] == decode(section["strict_gap_below_free_sharp_target"])
        and rebuilt["quotient"] < 4
        and rebuilt["gap"] > 0
    )
    checks["graph_sum_identities_reconstructed"] = (
        rebuilt["gradient_sum"] == 0
        and rebuilt["laplacian_sum"] == 0
        and rebuilt["weighted_residual_sum"] == 0
    )
    embedded = independently_reconstruct_four_dimensional_embedding(
        section["omega_integer_pattern"]
    )
    checks["four_dimensional_embedding_enumerated"] = (
        embedded["residual_norm"] == 16 * rebuilt["residual_norm"]
        and embedded["gradient_norm"] == 16 * rebuilt["gradient_norm"]
        and embedded["gradient_norm"] / embedded["residual_norm"]
        == rebuilt["quotient"]
    )
    theorem = certificate["unique_critical_point_theorem"]
    checks["critical_chain_recorded"] = (
        theorem["left_kernel"] == "kernel(Dr^T)=span{Omega^2}"
        and theorem["criticality_reduction"] == "Dr^T*r=0 implies r=c*Omega^2"
        and "c*sum_x Omega_x^3=0" in theorem["closure_identity"]
        and "Omega constant" in theorem["conclusion"]
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    checks["method_boundary"] = certificate["method_disposition"] == {
        "extra_finite_volume_critical_points": "RULED_OUT",
        "finite_volume_multiwell_explanation": "RULED_OUT",
        "global_sharp_free_gradient_domination": "OBSTRUCTED",
        "weaker_global_gradient_domination": "OPEN",
        "volume_uniform_witten_coercivity": "OPEN",
        "interacting_h_minus_one_bound": "OPEN",
        "continuum_reconstruction": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )
    checks["required_nonclaims"] = {
        "a positive volume-uniform gradient-domination constant",
        "a finite-volume or volume-uniform Poincare inequality",
        "Witten one-form coercivity",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} ({sum(checks.values())}/{len(checks)})")
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
