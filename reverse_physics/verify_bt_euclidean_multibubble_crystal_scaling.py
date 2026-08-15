#!/usr/bin/env python3
"""Independent verifier for the growing BT multibubble crystal."""

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
    "MULTIBUBBLE_CRYSTAL_SCALING_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "multibubble-crystal-scaling-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def reconstruct_k3() -> dict[str, Fraction | int]:
    k = 3
    return {
        "zero_count": (2 * k) ** 4,
        "residual_factor": k**4,
        "euler_factor": k**8,
        "quotient_factor": k**4,
        "concentration": Fraction(512, 3) * k**4,
        "weak": Fraction(512, 17) * k**4,
        "sextic": Fraction(-8, 45) * k**4,
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
    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hash_current"] = (
        len(inputs) == 1 and file_hash(inputs[0]["path"]) == inputs[0]["sha256"]
    )
    rebuilt = reconstruct_k3()
    fixture = certificate["exact_fixture_K3"]
    checks["k3_fixture_reconstructed"] = (
        fixture["K"] == 3
        and fixture["zero_count"] == rebuilt["zero_count"] == 1296
        and fixture["residual_norm_factor"] == rebuilt["residual_factor"] == 81
        and fixture["euler_norm_factor"] == rebuilt["euler_factor"] == 6561
        and fixture["quotient_factor"] == rebuilt["quotient_factor"] == 81
        and decode(fixture["concentration_coefficient"]) == rebuilt["concentration"] == 13824
        and decode(fixture["weak_quotient"]) == rebuilt["weak"] == Fraction(41472, 17)
        and decode(fixture["sextic_jet_coefficient"]) == rebuilt["sextic"] == Fraction(-72, 5)
    )
    scaling = certificate["operator_scaling"]
    checks["operator_chain"] = (
        scaling["residual"] == "R_K,m(x)=K^2*R_16,M(K*x)"
        and scaling["q_scalar"] == "q_K,m(x)=K^-2*q_16,M(K*x)"
        and scaling["euler"] == "E_K,m(x)=K^4*E_16,M(K*x)"
        and scaling["quotient"] == "Q_K(m)=K^4*Q_16(m*K^2)"
    )
    consequences = certificate["consequences"]
    checks["noncollapse_conclusion"] = (
        consequences["uniform_lower_bound"] == "Q_K(m)>=K^4*c_16 for all integer K>=1 and m>0"
        and consequences["normalized_infimum"] == "inf_m Q_K(m)/K^4=c_16>0"
        and consequences["weak_endpoint"] == "Q_K(infinity)=(512/17)*K^4"
    )
    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["synchronized_dense_crystal_gas"] == "RULED_OUT"
        and disposition["irregular_or_correlated_growing_gas"] == "OPEN"
        and disposition["same_point_towers_and_necks"] == "OPEN"
        and disposition["volume_uniform_witten_coercivity"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
    ]
    checks["required_nonclaims"] = {
        "a lower bound for an irregular or correlated growing bubble gas",
        "exclusion of same-point towers, necks, or nonspherical profiles",
        "a Witten/Poincare theorem or interacting Gibbs H^-1 estimate",
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
    print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} ({sum(checks.values())}/{len(checks)})")
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
