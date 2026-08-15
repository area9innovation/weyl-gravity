#!/usr/bin/env python3
"""Nonimporting verifier for the BT annealed edge-ellipticity theorem."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_EDGE_ELLIPTICITY_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-annealed-edge-ellipticity-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def reconstruct_cycle(omega_data: list[dict[str, int]]) -> dict:
    omega = [decode(item) for item in omega_data]
    residual = [
        omega[(x - 1) % 4] / omega[x]
        + omega[(x + 1) % 4] / omega[x]
        - 2
        for x in range(4)
    ]
    rows = []
    for x in range(4):
        for y in ((x - 1) % 4, (x + 1) % 4):
            ratio = omega[y] / omega[x]
            rows.append(
                {
                    "tail": [x, y],
                    "ratio": ratio,
                    "ratio_square": ratio**2,
                    "row_sum": residual[x] + 2,
                    "pointwise_ratio_square_envelope": 2 * residual[x] ** 2 + 8,
                    "exp_twice_absolute_jump": max(ratio**2, ratio ** (-2)),
                    "two_orientation_envelope": ratio**2 + ratio ** (-2),
                    "current": residual[x] * ratio - residual[y] / ratio,
                }
            )
    return {"omega": omega, "residual": residual, "directed_edges": rows}


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
        file_hash(item["path"]) == item["sha256"] for item in inputs
    )
    fixture = certificate["exact_fixture"]
    rebuilt = reconstruct_cycle(fixture["omega"])
    checks["fixture_residual_reconstructed"] = rebuilt["residual"] == [
        decode(item) for item in fixture["residual"]
    ]
    recorded_rows = fixture["directed_edges"]
    checks["fixture_edge_count"] = len(recorded_rows) == len(rebuilt["directed_edges"]) == 8
    edge_ok = True
    for recorded, actual in zip(recorded_rows, rebuilt["directed_edges"]):
        edge_ok = edge_ok and recorded["tail"] == actual["tail"]
        for key in (
            "ratio", "ratio_square", "row_sum",
            "pointwise_ratio_square_envelope", "exp_twice_absolute_jump",
            "two_orientation_envelope", "current",
        ):
            edge_ok = edge_ok and decode(recorded[key]) == actual[key]
        edge_ok = edge_ok and actual["ratio_square"] <= actual["pointwise_ratio_square_envelope"]
        edge_ok = edge_ok and actual["exp_twice_absolute_jump"] <= actual["two_orientation_envelope"]
    checks["fixture_edges_reconstructed"] = edge_ok
    bounds = certificate["theorem"]["bounds"]
    proof = certificate["proof_chain"]
    checks["rational_constants_reconstructed"] = (
        bounds["expected_residual_square"] == "E[r_x^2]<=2444/25"
        and bounds["directed_ratio_second_moment"] == "E[w_xy^2]<=8088/25"
        and bounds["absolute_jump_exponential_moment"] == "E[exp(2|d_xy|)]<=16176/25"
        and bounds["absolute_current_first_moment"] == "E[|J_xy|]<=8932/25"
        and "four-N" in proof["tails"]
    )
    checks["method_boundary"] = certificate["method_disposition"] == {
        "single_edge_ratio_second_moment": "PROVED_VOLUME_UNIFORM",
        "single_edge_log_jump_exponential_tail": "PROVED_VOLUME_UNIFORM",
        "single_edge_current_first_moment": "PROVED_VOLUME_UNIFORM",
        "coherent_path_or_block_decorrelation": "OPEN",
        "background_marginal_current_hyperuniformity": "OPEN",
        "all_field_gradient_bound": "OPEN",
        "interacting_h_minus_one_bound": "OPEN",
        "continuum_reconstruction": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"
    ]
    checks["required_nonclaims"] = {
        "independence or decay of correlations between edge jumps",
        "current hyperuniformity under the integrated background marginal",
        "a Poincare inequality, Witten coercivity, or interacting H^-1 bound",
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
