#!/usr/bin/env python3
"""Independent verifier for the BT logarithmic-bubble virial no-go."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LOG_BUBBLE_VIRIAL_NO_GO_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-log-bubble-virial-no-go-v1.schema.json",
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


def dictionary_product(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    answer: dict[int, Fraction] = {}
    for left_power, left_value in left.items():
        for right_power, right_value in right.items():
            power = left_power + right_power
            answer[power] = answer.get(power, Fraction(0)) + left_value * right_value
    return answer


def dictionary_power(polynomial: dict[int, Fraction], exponent: int) -> dict[int, Fraction]:
    answer = {0: Fraction(1)}
    for _ in range(exponent):
        answer = dictionary_product(answer, polynomial)
    return answer


def integrate(polynomial: dict[int, Fraction]) -> Fraction:
    return sum((value / (power + 1) for power, value in polynomial.items()), Fraction(0))


def reconstruct() -> tuple[dict[str, Fraction], dict[str, Fraction]]:
    """Use sparse exponent dictionaries, distinct from the producer lists."""
    window = {3: Fraction(10), 4: Fraction(-15), 5: Fraction(6)}
    window_prime = {power - 1: power * value for power, value in window.items()}
    moments = {
        "integral_W_squared": integrate(dictionary_power(window, 2)),
        "integral_W_cubed": integrate(dictionary_power(window, 3)),
        "integral_W_fourth": integrate(dictionary_power(window, 4)),
        "integral_W_prime_squared": integrate(dictionary_power(window_prime, 2)),
    }
    a = Fraction(3, 2)
    delta = Fraction(2)
    plateau = Fraction(4)
    q_value = a**2 * (
        4 * plateau
        + 2 * moments["integral_W_prime_squared"] / delta
        + 8 * delta * moments["integral_W_squared"]
    )
    c_value = -2 * a**3 * (
        plateau + 2 * delta * moments["integral_W_cubed"]
    )
    p_value = a**4 * (
        plateau + 2 * delta * moments["integral_W_fourth"]
    )
    totals = {
        "Q": q_value,
        "C": c_value,
        "P": p_value,
        "reduced_action": (q_value + 2 * c_value + p_value) / 2,
        "reduced_radial_virial": q_value + 3 * c_value + 2 * p_value,
    }
    return moments, totals


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        cert = load(path)
        Draft202012Validator(load(SCHEMA)).validate(cert)
        for item in cert["provenance"]["inputs"]:
            require(digest(item["path"]) == item["sha256"], "input hash drift")

        moments, totals = reconstruct()
        recorded = cert["exact_radial_integrals"]
        for name, value in moments.items():
            require(frac(recorded["smoothstep_integrals"][name]) == value, f"{name} mismatch")
        for name, value in totals.items():
            require(frac(recorded[name]) == value, f"{name} mismatch")
        require(totals == {
            "Q": Fraction(1173, 22),
            "C": Fraction(-2781, 77),
            "P": Fraction(886707, 33592),
            "reduced_action": Fraction(19349691, 5173168),
            "reduced_radial_virial": Fraction(-2896611, 1293292),
        }, "closed rational table drift")
        require(totals["reduced_action"] > 0, "action is not positive")
        require(totals["reduced_radial_virial"] < 0, "virial is not negative")

        transfer = cert["finite_lattice_transfer"]
        require(transfer["status"] == "RIGOROUS_EVENTUAL_FINITE_LATTICE_SEQUENCE", "transfer status drift")
        require("h^-2*r_L" in transfer["uniform_expansions"][0], "residual expansion missing")
        require("h^-2*t_L" in transfer["uniform_expansions"][1], "derivative expansion missing")
        require("exists L0" in transfer["finite_volume_consequence"], "finite-volume quantifier missing")
        disposition = cert["method_disposition"]
        require(disposition["pointwise_D_ge_cA_for_any_c_ge_0"] == "OBSTRUCTED", "homogeneous no-go weakened")
        require(disposition["nonpointwise_Gibbs_weighted_block_estimate"] == "OPEN", "Gibbs block estimate promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-1 promoted")
        require("LORENTZIAN-CAUSAL" not in cert["dependency_tags"], "Lorentzian scope promoted")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT logarithmic-bubble virial no-go certificate: PASS" if ok else "BT logarithmic-bubble virial no-go certificate: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
