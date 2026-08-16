#!/usr/bin/env python3
"""Independent verifier for the BT pair-block g4 L6 numerical preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_PREFLIGHT_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-g4-l6-preflight-v1.schema.json",
)
SOURCE_REL = "reverse_physics/bt_euclidean_pair_block_response_g4_l6_preflight.c"


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fast_compiled_calibration() -> bool:
    with tempfile.TemporaryDirectory() as directory:
        executable = os.path.join(directory, "preflight")
        compile_result = subprocess.run(
            [
                "cc", "-std=c11", "-O3", "-fopenmp", "-D_DEFAULT_SOURCE",
                "-Wall", "-Wextra", "-Werror", os.path.join(ROOT, SOURCE_REL),
                "-lm", "-o", executable,
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if compile_result.returncode:
            return False
        environment = dict(os.environ)
        environment["OMP_NUM_THREADS"] = "8"
        run = subprocess.run(
            [executable, "1"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
            env=environment,
        )
        if run.returncode:
            return False
        match = re.search(r"b2 ([^ ]+) expected ([^ ]+) error ([^\n]+)", run.stdout)
        fixture = re.search(r"F20 ([^ ]+) F40 ([^\n]+)", run.stdout)
        if not match or not fixture:
            return False
        computed, expected, error = map(float, match.groups())
        f20, f40 = map(float, fixture.groups())
        return (
            abs(computed - expected) < 2e-16
            and abs(error) < 2e-16
            and math.isclose(f20, -15643 / 1517824, rel_tol=0, abs_tol=2e-16)
            and math.isclose(f40, 41416831 / 82278203392, rel_tol=0, abs_tol=2e-16)
        )


def verify(path=DEFAULT_CERT, run_calibration=False):
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return False
    if list(Draft202012Validator(schema).iter_errors(cert)):
        return False
    if any(file_hash(row["path"]) != row["sha256"] for row in cert["provenance"]["inputs"]):
        return False
    result = cert["six_term_result"]
    terms = result["terms"]
    order = ("F_4_0", "F_4_2", "F_4_4", "minus_F_3_3_Gamma_3", "minus_F_2_2_Gamma_4", "plus_F_2_2_Gamma_3_squared")
    if set(terms) != set(order):
        return False
    total = math.fsum(terms[key] for key in order)
    absolute = math.fsum(abs(terms[key]) for key in order)
    if not math.isclose(total, result["sum"], rel_tol=0, abs_tol=5e-18):
        return False
    if not math.isclose(absolute, result["sum_of_absolute_terms"], rel_tol=0, abs_tol=5e-18):
        return False
    if result["sum"] <= 0 or result["sum"] / absolute <= 0.1:
        return False
    calibration = cert["calibration"]
    exact = calibration["exact_one_loop"]["numerator"] / calibration["exact_one_loop"]["denominator"]
    if abs(calibration["computed_binary64"] - exact) >= 2e-16:
        return False
    disposition = cert["method_disposition"]
    if disposition["exact_or_rigorous_L6_g4_sign"] != "OPEN" or disposition["coefficient_computed_lifecycle"] != "NOT_PROMOTED":
        return False
    if "LORENTZIAN-CAUSAL" in cert["dependency_tags"]:
        return False
    if run_calibration and not fast_compiled_calibration():
        return False
    print("[PASS] independent BT pair-block g4 L6 preflight verifier (14/14)")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate, run_calibration=True) else 1


if __name__ == "__main__":
    sys.exit(main())
