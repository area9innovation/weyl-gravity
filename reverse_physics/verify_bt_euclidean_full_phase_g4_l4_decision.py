#!/usr/bin/env python3
"""Independent verifier for the exact full-phase BT L=4 M4 decision."""

from __future__ import annotations

import functools
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_G4_L4_DECISION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-full-phase-g4-l4-decision-v1.schema.json")
EXPECTED = Fraction(-2569186115493259, 716934758400000)
PRIMES = (2305843009213693951, 2305843009213693921, 2305843009213693907, 2305843009213693723)
TERM_NAMES = (
    "|B|^2", "2*A.C", "-2*U30*A.B", "Cov(|A|^2,U30^2/2)",
    "Cov(|A|^2,-U40)", "Cov(|A|^2,-v*F42)",
    "Cov(|A|^2,v*|A|^2/2)", "Cov(|A|^2,E[Q^2]/2)",
)


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def digest(relative: str) -> str:
    value = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def residues(value: Fraction) -> list[int]:
    return [value.numerator % prime * pow(value.denominator, -1, prime) % prime for prime in PRIMES]


@functools.lru_cache(maxsize=1)
def modular_output() -> dict:
    source = os.path.join(ROOT, "reverse_physics/bt_euclidean_full_phase_g4_l4_modular_verify.cpp")
    with tempfile.TemporaryDirectory() as directory:
        binary = os.path.join(directory, "verify")
        subprocess.run(["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", source, "-o", binary], check=True, capture_output=True, text=True)
        result = subprocess.run([binary], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def independent_bound(cert: dict) -> None:
    modular = cert["independent_modular_verification"]
    covariance_sum = Fraction(2100641, 313600)
    require(frac(modular["allowed_covariance_absolute_sum"]) == covariance_sum, "covariance absolute sum drift")
    specs = (
        (Fraction(4) * Fraction(2, 16) ** 2, (4, 4), 3),
        (Fraction(8) * Fraction(3, 2) * Fraction(5, 512), (3, 5), 3),
        (Fraction(8) * Fraction(3, 2) * Fraction(2, 16) * Fraction(1, 16), (3, 4, 3), 4),
        (Fraction(2) * Fraction(3, 2) ** 2 * Fraction(1, 16) ** 2, (3, 3, 3, 3), 5),
        (Fraction(4) * Fraction(3, 2) ** 2 * Fraction(1, 256), (3, 3, 4), 4),
        (Fraction(4, 512) * Fraction(3, 2) ** 2 * 6, (3, 3, 4), 3),
        (Fraction(8, 512) * Fraction(3, 2) ** 4, (3, 3, 3, 3), 4),
        (Fraction(32, 512**2) * Fraction(3, 2) ** 2 * Fraction(48, 4) ** 2, (3, 3, 3, 3), 3),
    )
    kernel_bounds = {3: Fraction(256), 4: Fraction(896, 3), 5: Fraction(256)}
    kernel_denominators = {3: 6, 4: 24, 5: 120}
    propagator_lcm = 2822400
    expression_bound = Fraction(0)
    common = 1
    for outer, degrees, edges in specs:
        pairings = math.prod(range(1, 2 * edges, 2))
        bound = outer * pairings * covariance_sum**edges
        for degree in degrees:
            bound *= kernel_bounds[degree]
        expression_bound += bound
        common = math.lcm(common, outer.denominator * math.prod(kernel_denominators[d] for d in degrees) * propagator_lcm**edges)
    require(frac(modular["expression_absolute_bound"]) == expression_bound, "expression bound drift")
    require(modular["common_expression_denominator"] == common, "common denominator drift")
    integer_bound = EXPECTED.denominator * common * expression_bound + abs(EXPECTED.numerator) * common
    require(modular["integer_difference_bound"] == integer_bound.numerator, "integer bound drift")
    require(modular["integer_difference_bound_denominator"] == integer_bound.denominator, "integer bound denominator drift")
    require(math.ceil(integer_bound).bit_length() == 226, "integer bound bit count drift")
    prime_product = math.prod(PRIMES)
    require(prime_product.bit_length() == 244 and prime_product > 2 * integer_bound, "modular uniqueness failed")


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        for item in cert["provenance"]["inputs"]:
            require(digest(item["path"]) == item["sha256"], "input hash drift")
        decision = cert["exact_L4_decision"]
        values = [frac(row["value"]) for row in decision["terms"]]
        require(tuple(row["name"] for row in decision["terms"]) == TERM_NAMES, "term order drift")
        require(sum(values, Fraction(0)) == frac(decision["M4_full"]) == EXPECTED < 0, "M4 rational drift")
        require(values[0] == Fraction(55147376933567, 11202105600000) > 0, "B square drift")
        require(values[-1] == 0, "Q family L4 zero drift")
        output = modular_output()
        require(tuple(output["primes"]) == PRIMES, "modular primes drift")
        require(output["terms"] == [residues(value) for value in values], "term residue mismatch")
        require(output["terms"] == [row["modular_residues"] for row in decision["terms"]], "certified term residues drift")
        require(output["M4"] == residues(EXPECTED) == decision["M4_full_modular_residues"], "M4 residue mismatch")
        independent_bound(cert)
        reduction = cert["two_dimensional_fiber_reduction"]
        require("E[zeta^2]=0" in reduction["complex_coordinate"] and "E[|zeta|^4]=8v^2" in reduction["complex_coordinate"], "fiber moments drift")
        require(reduction["family_count"] == 8, "family count drift")
        disposition = cert["method_disposition"]
        require(disposition["finite_L4_complete_full_phase_M4"] == "NEGATIVE_NONZERO_EXACT", "finite result weakened")
        require(disposition["large_volume_full_phase_M4_sign_and_scaling"] == "OPEN", "large-volume result promoted")
        require(disposition["uniform_perturbative_remainder"] == "OPEN", "remainder promoted")
        require(disposition["nonperturbative_background_current_susceptibility"] == "OPEN", "susceptibility promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, subprocess.SubprocessError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT full-phase g4 L4 decision: PASS" if ok else "BT full-phase g4 L4 decision: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
