#!/usr/bin/env python3
"""Build/check the supporting seven-kernel binary64 preflight.

The analytic certificate does not depend on these floating-point values.  A
short L=5 smoke check is intended for scoped commits; ``--check`` reruns the
complete L=5,6,7,8 table.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_REL = (
    "reverse_physics/bt_euclidean_complete_g4_seven_kernel_preflight.c"
)
SOURCE_PATH = os.path.join(ROOT, SOURCE_REL)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_seven_kernel_preflight_v1.json"
)
DATA_PATH = os.path.join(ROOT, DATA_REL)
LENGTHS = (5, 6, 7, 8)


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def compile_evaluator(binary: str) -> None:
    subprocess.run(
        [
            "cc",
            "-std=c11",
            "-O3",
            "-Wall",
            "-Wextra",
            "-Werror",
            SOURCE_PATH,
            "-lm",
            "-o",
            binary,
        ],
        check=True,
    )


def evaluate(binary: str, length: int) -> dict:
    output = subprocess.run(
        [binary, str(length)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return json.loads(output)


def build(lengths: tuple[int, ...] = LENGTHS) -> dict:
    with tempfile.TemporaryDirectory(prefix="bt-g4-seven-") as directory:
        binary = os.path.join(directory, "evaluate")
        compile_evaluator(binary)
        rows = [evaluate(binary, length) for length in lengths]
    return {
        "result_id": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_PREFLIGHT_V1",
        "evidence_type": "SUPPORTING_ONLY_BINARY64_STREAMING_SEVEN_KERNEL_SUM",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "source": SOURCE_REL,
        "source_sha256": sha256(SOURCE_PATH),
        "compile_command": (
            "cc -std=c11 -O3 -Wall -Wextra -Werror "
            f"{SOURCE_REL} -lm -o /tmp/bt-g4-seven-kernel"
        ),
        "formula_scope": (
            "the fourteen unfactorized s=0 atlas entries after exact pairing "
            "under global momentum inversion; the factorized conditioning "
            "bubble square and lower-loop sectors are excluded"
        ),
        "rows": rows,
        "observed_pattern": (
            "At L=5,6,7,8 the seven-kernel sum is negative and its ratio to "
            "N*omega(p) is -0.01913, -0.01784, -0.01686, -0.01609. This "
            "locates a plausible nonzero power carrier but is not an "
            "asymptotic sign or scaling proof."
        ),
        "does_not_establish": [
            "the sign at any uncomputed volume",
            "an asymptotic coefficient or bound",
            "the sign or scaling of the complete M4 coefficient after the factorized and lower-loop sectors are restored",
            "boundedness or divergence of the nonperturbative Gibbs score or interacting H^-1 moment",
            "continuum, Born, Krein, or Lorentzian physics",
        ],
        "status": "SUPPORTING_ONLY_ANALYTIC_POWER_CARRIER_TARGET",
    }


def close(left: float, right: float) -> bool:
    return abs(left - right) <= 2e-11 * max(1.0, abs(left), abs(right))


def same_row(left: dict, right: dict) -> bool:
    exact = ("length", "volume")
    numeric = ("omega_p", "sum", "sum_over_N_omega_p")
    return (
        all(left[key] == right[key] for key in exact)
        and all(close(left[key], right[key]) for key in numeric)
        and len(left["kernels"]) == len(right["kernels"]) == 7
        and all(close(a, b) for a, b in zip(left["kernels"], right["kernels"]))
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.write:
        payload = build()
        with open(DATA_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
    if args.check or args.smoke:
        try:
            with open(DATA_PATH, encoding="utf-8") as handle:
                stored = json.load(handle)
        except OSError:
            return 1
        lengths = (5,) if args.smoke else LENGTHS
        observed = build(lengths)["rows"]
        expected = [
            row for row in stored["rows"] if row["length"] in lengths
        ]
        if len(observed) != len(expected):
            return 1
        if not all(same_row(left, right) for left, right in zip(observed, expected)):
            return 1
        if stored["source_sha256"] != sha256(SOURCE_PATH):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
