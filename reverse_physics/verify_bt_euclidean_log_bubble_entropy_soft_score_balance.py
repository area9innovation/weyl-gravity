#!/usr/bin/env python3
"""Independent verifier for the BT bubble entropy/soft-score balance."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LOG_BUBBLE_ENTROPY_SOFT_SCORE_BALANCE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-log-bubble-entropy-soft-score-balance-v1.schema.json",
)


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def digest(relative: str) -> str:
    value = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def product(
    left: dict[int, Fraction], right: dict[int, Fraction]
) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for i, a in left.items():
        for j, b in right.items():
            result[i + j] = result.get(i + j, Fraction(0)) + a * b
    return result


def polynomial_power(
    polynomial: dict[int, Fraction], exponent: int
) -> dict[int, Fraction]:
    result = {0: Fraction(1)}
    for _ in range(exponent):
        result = product(result, polynomial)
    return result


def integrate(polynomial: dict[int, Fraction]) -> Fraction:
    return sum(
        (coefficient / (power + 1) for power, coefficient in polynomial.items()),
        Fraction(0),
    )


def reconstruct() -> tuple[dict[str, Fraction], dict[str, Fraction]]:
    """Reconstruct with sparse exponent maps, independent of producer lists."""
    window = {3: Fraction(10), 4: Fraction(-15), 5: Fraction(6)}
    window_prime = {power - 1: power * value for power, value in window.items()}
    moments = {
        "integral_W_squared": integrate(polynomial_power(window, 2)),
        "integral_W_cubed": integrate(polynomial_power(window, 3)),
        "integral_W_fourth": integrate(polynomial_power(window, 4)),
        "integral_W_prime_squared": integrate(polynomial_power(window_prime, 2)),
    }
    a = Fraction(5, 3)
    delta = Fraction(7, 2)
    q_value = a**2 * (
        2 * moments["integral_W_prime_squared"] / delta
        + 8 * delta * moments["integral_W_squared"]
    )
    c_value = -4 * a**3 * delta * moments["integral_W_cubed"]
    p_value = 2 * a**4 * delta * moments["integral_W_fourth"]
    action = (q_value + 2 * c_value + p_value) / 2
    virial = q_value + 3 * c_value + 2 * p_value
    exponent = Fraction(5, 4) * action
    totals = {
        "Q": q_value,
        "C": c_value,
        "P": p_value,
        "reduced_action": action,
        "reduced_radial_virial": virial,
        "reduced_action_threshold": Fraction(16, 5),
        "single_bubble_activity_exponent": exponent,
        "positional_entropy_exponent": Fraction(4),
        "positive_entropy_gap": Fraction(4) - exponent,
    }
    return moments, totals


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        cert = load(path)
        Draft202012Validator(load(SCHEMA)).validate(cert)
        for item in cert["provenance"]["inputs"]:
            require(digest(item["path"]) == item["sha256"], "input hash drift")

        moments, totals = reconstruct()
        wall = cert["optimized_wall"]
        for name, value in moments.items():
            require(frac(wall["smoothstep_integrals"][name]) == value, f"{name} mismatch")
        for name in ("Q", "C", "P", "reduced_action", "reduced_radial_virial"):
            require(frac(wall[name]) == totals[name], f"{name} mismatch")
        entropy = cert["tuned_entropy_balance"]
        for name in (
            "reduced_action_threshold",
            "single_bubble_activity_exponent",
            "positional_entropy_exponent",
            "positive_entropy_gap",
        ):
            require(frac(entropy[name]) == totals[name], f"{name} mismatch")

        require(totals["reduced_action"] == Fraction(1965963925, 733296564), "closed action drift")
        require(totals["reduced_radial_virial"] == Fraction(-2157475, 16665831), "closed virial drift")
        require(totals["single_bubble_activity_exponent"] == Fraction(9829819625, 2933186256), "activity exponent drift")
        require(totals["positive_entropy_gap"] == Fraction(1902925399, 2933186256), "entropy gap drift")
        require(totals["reduced_radial_virial"] < 0, "virial is not negative")
        require(totals["reduced_action"] < totals["reduced_action_threshold"], "wall is not subcritical")
        require(totals["positive_entropy_gap"] > 0, "positional entropy does not win")

        soft = cert["soft_score_balance"]
        require(soft["status"] == "DILUTE_ONE_BUBBLE_SCORE_ACTIVITY_VANISHES", "soft-score status drift")
        require("O((K/L)^2)" in soft["discrete_transfer"], "quadratic discrete soft factor missing")
        require("O(g_L^-2*L^(-beta+o(1)))" in soft["score_weighted_scale_balance"], "weighted activity scaling missing")
        disposition = cert["method_disposition"]
        require(disposition["energy_only_bubble_rarity_bound"] == "OBSTRUCTED", "energy-only obstruction weakened")
        require(disposition["dilute_single_bubble_score_weighted_activity"] == "VANISHES", "soft balance weakened")
        require(disposition["interacting_multibubble_cluster_bound"] == "OPEN", "cluster theorem promoted")
        require(disposition["actual_annealed_zero_fiber_score_bound"] == "OPEN", "score theorem promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one theorem promoted")
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print(
        "BT logarithmic-bubble entropy/soft-score certificate: PASS"
        if ok
        else "BT logarithmic-bubble entropy/soft-score certificate: FAIL"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
