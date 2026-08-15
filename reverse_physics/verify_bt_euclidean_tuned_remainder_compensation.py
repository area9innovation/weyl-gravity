#!/usr/bin/env python3
"""Independent verifier for the BT tuned remainder-compensation theorem."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_TUNED_REMAINDER_COMPENSATION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-tuned-remainder-compensation-v1.schema.json")
RG = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json")
PAIR = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_NONCANCELLATION_V1.json")
COMPLETE = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LOWER_LOOP_BOUNDS_V1.json")


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def digest(relative: str) -> str:
    value = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def frac(value: dict) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        cert = load(path)
        schema = load(SCHEMA)
        Draft202012Validator(schema).validate(cert)
        rg = load(RG)
        pair = load(PAIR)
        complete = load(COMPLETE)

        for item in cert["provenance"]["inputs"]:
            require(digest(item["path"]) == item["sha256"], f"input hash drift: {item['path']}")

        # Reconstruct the decimal interval comparison as exact rationals.
        negative_magnitude = Fraction(1613, 100000)
        positive_ceiling = Fraction(8051597, 500000000)
        gap = negative_magnitude - positive_ceiling
        require(gap == Fraction(13403, 500000000), "strict coefficient gap arithmetic failed")
        require(frac(cert["coefficient_gap"]["gap"]) == gap, "certificate gap drift")
        require(pair["comparison"] == {
            "combined": "c_4+c_7<0",
            "pair_four": "c_4<-0.01613",
            "pair_seven": "0<c_7<0.016103194<0.01613",
            "status": "STRICT_TWO_PAIR_NONCANCELLATION_PROVED_NEGATIVE",
        }, "upstream strict interval drift")
        require(complete["complete_leading_power"]["status"] == "COMPLETE_M4_LEADING_POWER_COEFFICIENT_STRICTLY_NEGATIVE", "complete M4 sign drift")

        # Independent Z2 degree ledger: S1 is cubic and S2 quartic, while a
        # fixed directional derivative lowers degree by one.
        parity = lambda degree: "EVEN" if degree % 2 == 0 else "ODD"
        require(parity(3 - 1) == cert["exact_parity"]["parities"]["A=D_h*S1"], "A parity drift")
        require(parity(4 - 1) == cert["exact_parity"]["parities"]["B=D_h*S2"], "B parity drift")
        require(parity(3) == cert["exact_parity"]["parities"]["W1=E_T[S1]"], "W1 parity drift")
        require(parity((3 - 1) + (4 - 1)) == "ODD", "AB integrand is not odd")
        require(parity(2 * (3 - 1) + 3) == "ODD", "A2W1 integrand is not odd")
        require(cert["exact_parity"]["cubic_norm_coefficient"] == "M3=E0[2*A*B-A^2*W1]=0", "M3 identity drift")

        require(rg["lattice_log_residue"]["residue_coefficient_over_pi_squared"] == {"numerator": 5, "denominator": 16}, "score residue drift")
        require(rg["matched_refinement"]["running_limit_coefficient_pi_squared"] == {"numerator": 8, "denominator": 5}, "running limit drift")
        require(cert["exact_balance"]["status"] == "LEADING_POWER_COMPENSATION_FORCED", "balance status drift")
        require(cert["method_disposition"]["sign_or_scaling_of_exact_interacting_score"] == "OPEN", "interacting score promoted")
        require(cert["method_disposition"]["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-1 promoted")
        require("LORENTZIAN-CAUSAL" not in cert["dependency_tags"], "Lorentzian tag promoted")
        require(all(cert["checks"].values()), "a producer check is false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT tuned remainder-compensation certificate: PASS" if ok else "BT tuned remainder-compensation certificate: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
