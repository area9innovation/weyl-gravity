#!/usr/bin/env python3
"""Nonimporting verifier for bounded-oscillation BT gradient coercivity."""

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
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "BOUNDED_OSCILLATION_GRADIENT_COERCIVITY_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "bounded-oscillation-gradient-coercivity-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independently_reconstruct_cycle(omega_data: list[dict[str, int]]) -> dict:
    """Reconstruct using directed neighbor rows, unlike the edge producer."""
    omega = [decode(value) for value in omega_data]
    laplacian = []
    for site in range(4):
        laplacian.append(
            omega[(site - 1) % 4] + omega[(site + 1) % 4] - 2 * omega[site]
        )
    residual = [laplacian[i] / omega[i] for i in range(4)]
    gradient = [Fraction(0) for _ in omega]
    for site in range(4):
        for other in ((site - 1) % 4, (site + 1) % 4):
            current = omega[other] * residual[site] / omega[site]
            gradient[other] += current
            gradient[site] -= current
    residual_norm = sum((value**2 for value in residual), Fraction(0))
    gradient_norm = sum((value**2 for value in gradient), Fraction(0))
    lower = Fraction(4) * (min(omega) / max(omega)) ** 12 * residual_norm
    return {
        "omega": omega,
        "residual": residual,
        "gradient": gradient,
        "weighted_sum": sum(
            (omega[i] * residual[i] for i in range(4)), Fraction(0)
        ),
        "residual_norm": residual_norm,
        "gradient_norm": gradient_norm,
        "lower": lower,
        "slack": gradient_norm - lower,
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
    checks["provenance_hash_current"] = len(inputs) == 1 and all(
        file_hash(item["path"]) == item["sha256"] for item in inputs
    )
    fixture = certificate["exact_fixture"]
    rebuilt = independently_reconstruct_cycle(fixture["omega"])
    checks["residual_reconstructed"] = rebuilt["residual"] == [
        decode(value) for value in fixture["residual"]
    ]
    checks["gradient_reconstructed"] = rebuilt["gradient"] == [
        decode(value) for value in fixture["gradient"]
    ]
    checks["constraint_reconstructed"] = (
        rebuilt["weighted_sum"] == decode(fixture["weighted_residual_sum"]) == 0
    )
    checks["norms_reconstructed"] = (
        rebuilt["residual_norm"] == decode(fixture["residual_norm_squared"])
        and rebuilt["gradient_norm"] == decode(fixture["gradient_norm_squared"])
    )
    checks["bound_reconstructed"] = (
        rebuilt["lower"] == decode(fixture["certified_lower_bound"])
        and rebuilt["slack"] == decode(fixture["strict_slack"])
        and rebuilt["slack"] > 0
    )
    theorem = certificate["theorem"]
    proof = certificate["proof_chain"]
    checks["theorem_chain_recorded"] = (
        theorem["conclusion"]
        == "||grad A||_2^2 >= omega_G^2 (m/M)^12 ||r||_2^2"
        and ">=(min Omega/max Omega)^12" in theorem["normalized_conclusion"]
        and ">=(m/M)^3" in proof["kernel_angle"]
        and "(m/M)^6" in proof["norm_conversion"]
        and "exponent twelve" in proof["squaring"]
    )
    checks["method_boundary"] = certificate["method_disposition"] == {
        "bounded_oscillation_gradient_collapse": "RULED_OUT",
        "unbounded_oscillation_gradient_collapse": "OPEN",
        "all_field_volume_uniform_gradient_bound": "OPEN",
        "witten_poincare_transfer": "OPEN",
        "interacting_h_minus_one_bound": "OPEN",
        "continuum_reconstruction": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    checks["required_nonclaims"] = {
        "an all-field positive volume-uniform gradient constant",
        "a Poincare inequality or Witten one-form coercivity",
        "anything LORENTZIAN-CAUSAL",
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
