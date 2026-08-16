#!/usr/bin/env python3
"""Independent verifier for the BT pair-block g4 L6 interval certificate."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
from decimal import Decimal, getcontext
from fractions import Fraction

from jsonschema import Draft202012Validator


getcontext().prec = 100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_INTERVAL_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-g4-l6-interval-v1.schema.json",
)
PREFLIGHT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_PREFLIGHT_V1.json",
)
SOURCE_PATH = os.path.join(
    ROOT, "reverse_physics/bt_euclidean_pair_block_response_g4_l6_interval.c"
)
TERM_ORDER = (
    "F_4_0",
    "F_4_2",
    "F_4_4",
    "minus_F_3_3_Gamma_3",
    "minus_F_2_2_Gamma_4",
    "plus_F_2_2_Gamma_3_squared",
)


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def endpoints(row: dict) -> tuple[Decimal, Decimal]:
    midpoint = Decimal(row["midpoint"])
    radius = Decimal(row["radius"])
    if radius < 0:
        raise ValueError("negative radius")
    return midpoint - radius, midpoint + radius


def fraction_in(row: dict, value: Fraction) -> bool:
    low, high = endpoints(row)
    exact = Decimal(value.numerator) / Decimal(value.denominator)
    return low <= exact <= high


def hex_long_double_fraction(text: str) -> Fraction:
    match = re.fullmatch(r"([+-]?)0x([0-9a-f]+)\.([0-9a-f]+)p([+-]?\d+)", text.lower())
    if not match:
        raise ValueError("bad hexadecimal long double")
    sign, whole, fractional, exponent = match.groups()
    scale = 16 ** len(fractional)
    mantissa = int(whole + fractional, 16)
    value = Fraction(mantissa, scale) * (Fraction(2) ** int(exponent))
    return -value if sign == "-" else value


def platform_probe() -> bool:
    source = "#include <float.h>\nLDBL_MANT_DIG LDBL_MAX_EXP FLT_RADIX FLT_EVAL_METHOD\n"
    run = subprocess.run(
        ["cc", "-E", "-P", "-x", "c", "-"],
        input=source,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    if run.returncode:
        return False
    numbers = [int(value) for value in re.findall(r"-?\d+", run.stdout.splitlines()[-1])]
    libc = ctypes.CDLL(None)
    libc.fegetround.restype = ctypes.c_int
    return (
        numbers == [64, 16384, 2, 0]
        and ctypes.sizeof(ctypes.c_longdouble) == 16
        and libc.fegetround() == 0  # glibc FE_TONEAREST
    )


def verify(path: str = DEFAULT_CERT, check_platform: bool = False) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        with open(PREFLIGHT_PATH, encoding="utf-8") as handle:
            preflight = json.load(handle)
        with open(SOURCE_PATH, encoding="utf-8") as handle:
            source = handle.read()
    except (OSError, json.JSONDecodeError):
        return False
    if list(Draft202012Validator(schema).iter_errors(cert)):
        return False
    try:
        if any(file_hash(row["path"]) != row["sha256"] for row in cert["provenance"]["inputs"]):
            return False
        coefficient = cert["coefficient"]
        if tuple(coefficient["term_order"]) != TERM_ORDER or tuple(coefficient["terms"]) != TERM_ORDER:
            return False
        term_intervals = [endpoints(coefficient["terms"][key]) for key in TERM_ORDER]
        summed_low = sum((row[0] for row in term_intervals), Decimal(0))
        summed_high = sum((row[1] for row in term_intervals), Decimal(0))
        total_low, total_high = endpoints(coefficient["total"])
        if not (total_low <= summed_low <= summed_high <= total_high and total_low > 0):
            return False
        if Decimal(coefficient["real_lower_endpoint"]) != total_low:
            return False
        if Decimal(coefficient["real_upper_endpoint"]) != total_high:
            return False
        for row in [*coefficient["terms"].values(), coefficient["total"]]:
            if abs(Decimal(row["imaginary_midpoint"])) > Decimal(row["radius"]):
                return False
        exact = {
            "F20": Fraction(-15643, 1517824),
            "F40": Fraction(41416831, 82278203392),
            "b2": Fraction(956585197, 10069092633600),
        }
        if any(not fraction_in(cert["calibration"][key]["computed_interval"], value) for key, value in exact.items()):
            return False
        preflight_terms = preflight["six_term_result"]["terms"]
        for key in TERM_ORDER:
            low, high = endpoints(coefficient["terms"][key])
            if not low <= Decimal(str(preflight_terms[key])) <= high:
                return False
        if not total_low <= Decimal(str(preflight["six_term_result"]["sum"])) <= total_high:
            return False
        arithmetic = cert["arithmetic_certificate"]
        mantissa_bits = arithmetic["long_double_mantissa_bits"]
        if Decimal(arithmetic["error_allowance"]) <= Decimal(128) * (Decimal(2) ** -mantissa_bits):
            return False
        phase_mid = hex_long_double_fraction(arithmetic["phase_midpoint_hex"])
        phase_radius = Fraction(19, 10**20)
        if not ((phase_mid - phase_radius) ** 2 < Fraction(3, 4) < (phase_mid + phase_radius) ** 2):
            return False
        required_source = (
            "static const long double ERR = 1.0e-17L;",
            "typedef struct { long double complex mid; long double rad; } Ball;",
            "z.rad=si[dot]?2.0e-19L:0;",
            "(1+4*ERR)",
            "(1+8*ERR)",
        )
        if any(fragment not in source for fragment in required_source):
            return False
        if cert["lifecycle_state"] != "COEFFICIENT_COMPUTED":
            return False
        disposition = cert["method_disposition"]
        if disposition["large_volume_g4_power_or_log"] != "OPEN" or disposition["actual_interacting_h_minus_one"] != "OPEN":
            return False
        if "LORENTZIAN-CAUSAL" in cert["dependency_tags"]:
            return False
    except (KeyError, TypeError, ValueError, ArithmeticError):
        return False
    if check_platform and not platform_probe():
        return False
    print("[PASS] independent BT pair-block g4 L6 interval verifier (20/20)")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate, check_platform=True) else 1


if __name__ == "__main__":
    sys.exit(main())
