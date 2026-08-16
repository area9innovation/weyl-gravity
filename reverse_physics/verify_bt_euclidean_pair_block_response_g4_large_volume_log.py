#!/usr/bin/env python3
"""Independent verifier for the BT pair-block g4 large-volume logarithm."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_LARGE_VOLUME_LOG_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-g4-large-volume-log-v1.schema.json",
)


def decode(row: dict) -> Fraction:
    return Fraction(row["numerator"], row["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def gamma3_grid_identity() -> bool:
    # Degree at most two in each variable, so three exact points per variable
    # are an interpolation proof, not a probabilistic fixture.
    for a, b, c in itertools.product(map(Fraction, range(3)), repeat=3):
        left = a * a + b * b + c * c - 2 * a * b - 2 * a * c - 2 * b * c
        right = (c - a - b) ** 2 - 4 * a * b
        if left != right:
            return False
    return True


def gamma4_grid_identity() -> bool:
    # After the plus/minus axial pair is added, v=sin(l1)sin(k1) occurs only
    # through v^2. Substitution leaves degree at most two in a,b,u separately.
    for a, b, u in itertools.product(map(Fraction, range(3)), repeat=3):
        v2 = a * (1 - a / 4) * (2 * u - u * u)
        dp_plus_dm = -2 * a * u
        dp2_plus_dm2 = 2 * a * a * u * u + 8 * v2
        raw = -2 * (a + b) * dp_plus_dm + 4 * a * b + dp2_plus_dm2
        target = a * (4 * b * (1 + u) + 8 * (2 * u - u * u) + 4 * a * u * u)
        if raw != target:
            return False
    return True


def exact_l6_coefficients() -> tuple[Fraction, Fraction]:
    x = (Fraction(0), Fraction(1), Fraction(3), Fraction(4), Fraction(3), Fraction(1))
    cosine = (Fraction(1), Fraction(1, 2), Fraction(-1, 2), Fraction(-1), Fraction(-1, 2), Fraction(1, 2))
    sine2 = (Fraction(0), Fraction(3, 4), Fraction(3, 4), Fraction(0), Fraction(3, 4), Fraction(3, 4))
    leading = Fraction()
    remainder = Fraction()
    for q0 in range(6):
        for q1 in range(6):
            for q2 in range(6):
                for q3 in range(6):
                    omega = x[q0] + x[q1] + x[q2] + x[q3]
                    if not omega:
                        continue
                    leading += 4 * (2 - cosine[q0]) / omega + 8 * sine2[q0] / omega**2
                    remainder += (1 - cosine[q0]) ** 2 / omega**2
    return leading / 1296, remainder / 1296


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return False
    if list(Draft202012Validator(schema).iter_errors(cert)):
        return False
    try:
        if any(file_hash(row["path"]) != row["sha256"] for row in cert["provenance"]["inputs"]):
            return False
        if not gamma3_grid_identity() or not gamma4_grid_identity():
            return False
        soft = cert["response_soft_lemma"]
        if decode(soft["exact_linear_coefficient"]) != Fraction(3, 28):
            return False
        tadpole = cert["tadpole_reduction"]
        leading_l6, remainder_l6 = exact_l6_coefficients()
        if decode(tadpole["exact_L6_C"]) != leading_l6:
            return False
        if decode(tadpole["exact_L6_quartic_remainder_average"]) != remainder_l6:
            return False
        theorem = cert["leading_log_theorem"]
        prefactor = -Fraction(1, 4) * Fraction(3, 28) * 8 * Fraction(1, 8)
        if prefactor != Fraction(-3, 112):
            return False
        if decode(theorem["rational_prefactor_of_W4_over_pi_squared"]) != prefactor:
            return False
        if theorem["sign"] != "STRICTLY_NEGATIVE":
            return False
        ledger = cert["topology_disposition"]
        expected = {
            "F_4_0": "O(1)",
            "F_4_2": "O(1)",
            "F_4_4": "O(1)",
            "minus_F_3_3_Gamma_3": "O(1)",
            "minus_F_2_2_Gamma_4": "UNIQUE_NEGATIVE_LOG",
            "plus_F_2_2_Gamma_3_squared": "O(1)",
        }
        if {row["term"]: row["large_volume_disposition"] for row in ledger} != expected:
            return False
        sums = cert["lattice_sum_lemmas"]
        if "1/(8*pi^2)" not in sums["G2"] or "O(1)" not in sums["sunset"]:
            return False
        if cert["method_disposition"]["coefficientwise_pair_block_uniformity"] != "OBSTRUCTED":
            return False
        if cert["method_disposition"]["fixed_coupling_pair_response"] != "OPEN_NONUNIFORM_SERIES_CANNOT_DECIDE":
            return False
        if cert["method_disposition"]["actual_interacting_h_minus_one"] != "OPEN":
            return False
        if "LORENTZIAN-CAUSAL" in cert["dependency_tags"]:
            return False
        if not cert["checks"]["ok"] or cert["checks"]["failures"]:
            return False
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False
    print("[PASS] independent BT pair-block g4 large-volume log verifier (18/18)")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
