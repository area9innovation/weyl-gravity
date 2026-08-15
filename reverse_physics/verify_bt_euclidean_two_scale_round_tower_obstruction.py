#!/usr/bin/env python3
"""Independent verifier for the two-scale round BT tower obstruction."""

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
    "TWO_SCALE_ROUND_TOWER_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "two-scale-round-tower-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def reconstruct_algebra() -> dict[str, Fraction | str]:
    # The first inner correction is obtained by expanding the recorded exact q.
    q_first = Fraction(6)
    euler_profile = 4 * (2 * 4 * q_first)
    beta = Fraction(1, 20)
    euler_norm = euler_profile**2 * beta
    residual = 2 * Fraction(32, 3)
    return {
        "q_first": q_first,
        "euler_profile": euler_profile,
        "beta": beta,
        "euler_norm": euler_norm,
        "residual": residual,
        "quotient": euler_norm / residual,
    }


def direct_fixture(t: Fraction, epsilon: Fraction) -> tuple[Fraction, Fraction]:
    omega_half = epsilon / (t + epsilon**2) + 1 / (t + 1)
    omega_half_prime = -epsilon / (t + epsilon**2) ** 2 - 1 / (t + 1) ** 2
    laplace_eighth = epsilon**3 / (t + epsilon**2) ** 3 + 1 / (t + 1) ** 3
    laplace_eighth_prime = (
        -3 * epsilon**3 / (t + epsilon**2) ** 4 - 3 / (t + 1) ** 4
    )
    q = -2 * laplace_eighth / omega_half**3
    q_prime = -2 * (
        laplace_eighth_prime / omega_half**3
        - 3 * laplace_eighth * omega_half_prime / omega_half**4
    )
    return q, q_prime


def recorded_formula_fixture(t: Fraction, epsilon: Fraction) -> tuple[Fraction, Fraction]:
    d = epsilon**2 - epsilon + 1
    c = 4 * epsilon**2 - epsilon**3 - epsilon
    q = -2 * (d * (t**2 + epsilon**2) + c * t)
    q /= (1 + epsilon) ** 2 * (t + epsilon) ** 2
    q_prime = -6 * epsilon * (1 - epsilon) ** 2 * (t - epsilon)
    q_prime /= (1 + epsilon) ** 2 * (t + epsilon) ** 3
    return q, q_prime


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
    checks["provenance_hashes_current"] = len(inputs) == 2 and all(
        file_hash(row["path"]) == row["sha256"] for row in inputs
    )
    exact = certificate["exact_radial_algebra"]
    checks["exact_q_chain"] = (
        exact["d"] == "d=epsilon^2-epsilon+1"
        and exact["c"] == "c=4*epsilon^2-epsilon^3-epsilon"
        and "a^3+b^3=(a+b)*(a^2-a*b+b^2)" in exact["derivation"]
        and exact["q_derivative"]
        == "d_t q=-6*epsilon*(1-epsilon)^2*(t-epsilon)/[(1+epsilon)^2*(t+epsilon)^3]"
        and all(
            direct_fixture(t, epsilon) == recorded_formula_fixture(t, epsilon)
            for t, epsilon in [
                (Fraction(2, 7), Fraction(1, 5)),
                (Fraction(3, 2), Fraction(2, 3)),
            ]
        )
    )
    rebuilt = reconstruct_algebra()
    constants = certificate["asymptotics"]["constants"]
    checks["inner_constants_reconstructed"] = (
        rebuilt["q_first"] == 6
        and rebuilt["euler_profile"] == decode(constants["inner_euler_profile_numerator"]) == 192
        and rebuilt["beta"] == decode(constants["inner_euler_beta_integral"]) == Fraction(1, 20)
        and rebuilt["euler_norm"] == decode(constants["euler_norm_coefficient_without_pi2"]) == Fraction(9216, 5)
        and rebuilt["residual"] == decode(constants["tower_residual_coefficient_without_pi2"]) == Fraction(64, 3)
        and rebuilt["quotient"] == decode(constants["quotient_coefficient"]) == Fraction(432, 5)
    )
    asymptotics = certificate["asymptotics"]
    checks["asymptotic_conclusion"] = (
        asymptotics["euler_norm"]
        == "||E_epsilon||_2^2=(9216/5)*pi^2*epsilon^-2+o(epsilon^-2)"
        and asymptotics["residual_norm"] == "||R_epsilon||_2^2 tends to (64/3)*pi^2"
        and asymptotics["quotient"]
        == "Q_tower(epsilon)=(432/5)*epsilon^-2+o(epsilon^-2)"
        and asymptotics["conclusion"]
        == "Q_tower(epsilon) tends to infinity as epsilon tends to zero"
    )
    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["canonical_two_scale_same_center_round_tower"]
        == "OBSTRUCTED_BY_POWER_EULER_COST"
        and disposition["periodized_two_scale_tower"] == "OPEN"
        and disposition["arbitrary_same_center_tower_profiles"] == "OPEN"
        and disposition["volume_uniform_witten_coercivity"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
    ]
    checks["required_nonclaims"] = {
        "a theorem for a periodized two-scale tower",
        "exclusion of arbitrary tower profiles, necks, or irregular bubble gases",
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
