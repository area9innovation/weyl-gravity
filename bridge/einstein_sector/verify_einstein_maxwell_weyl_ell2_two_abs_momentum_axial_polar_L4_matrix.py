#!/usr/bin/env python3
"""Independent verifier for the axial-first/polar-second L=4 matrix."""
from __future__ import annotations

import argparse
import subprocess

from bridge.einstein_sector.cross_parity_L4_matrix_verifier_core import ROOT, verify_matrix


def independently_verify(exhaustive: bool = False) -> None:
    verify_matrix("axial_polar")
    if exhaustive:
        subprocess.run(
            [
                "python3",
                "-m",
                "bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_polar_L4_matrix",
                "--recompute-exhaustive",
            ],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exhaustive", action="store_true")
    args = parser.parse_args()
    independently_verify(args.exhaustive)
    print(
        "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_AXIAL_POLAR_L4_MATRIX independent verification: PASS"
    )
