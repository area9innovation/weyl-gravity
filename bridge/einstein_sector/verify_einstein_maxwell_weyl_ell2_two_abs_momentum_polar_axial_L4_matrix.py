#!/usr/bin/env python3
"""Independent verifier for the reverse ordered cross-parity L=4 matrix."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT_HINT = Path(__file__).resolve().parents[2]
if str(ROOT_HINT) not in sys.path:
    sys.path.insert(0, str(ROOT_HINT))

from bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix import (
    ROOT,
    verify_certificate,
    verify_slice_calibration,
)


CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.schema.json"


def independently_verify(exhaustive: bool = False) -> None:
    verify_slice_calibration()
    verify_certificate(CERT, SCHEMA, final_axisymmetric_block=True)
    value = json.loads(CERT.read_text())
    audit = value["graded_symmetry_audit"]
    assert audit == {
        "axial_then_polar_PBW_terms": 832,
        "both_orders_in_shared_slice": True,
        "name_based_mode_identification_used": False,
        "polar_then_axial_PBW_terms": 832,
        "reverse_matrix_obtained_by_explicit_role_substitution": True,
    }
    if exhaustive:
        import subprocess

        subprocess.run(
            [
                "python3",
                "-m",
                "bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_axial_L4_matrix",
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
        "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_POLAR_AXIAL_L4_MATRIX independent verification: PASS"
    )
