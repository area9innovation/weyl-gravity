#!/usr/bin/env python3
"""Produce the exact 36-row auxiliary-q entries from the classical executable."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from covariant_completion.auxiliary_equivalence import GeneralizedAuxiliaryRetract


HERE = ROOT / "quantum-weyl/classical_import"
OUTPUT = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1.json"
SOURCE = ROOT / "covariant_completion/auxiliary_equivalence/generalized_retract.py"
CERTIFICATE = ROOT / "covariant_completion/certificates/generalized_auxiliary_contraction.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode()).hexdigest()


def rational(value: sp.Expr) -> str:
    value = sp.Rational(value)
    return str(value.p) if value.q == 1 else f"{value.p}/{value.q}"


def generated() -> bytes:
    authority = json.loads(CERTIFICATE.read_text())
    retract = GeneralizedAuxiliaryRetract.build()
    matrix = retract.auxiliary_differential
    digest = matrix_digest(matrix)
    if digest != authority["matrix_sha256"]["auxiliary_differential"]:
        raise ValueError("auxiliary-q authority digest drift")
    entries = [
        [row, column, rational(matrix[row, column])]
        for row in range(36)
        for column in range(36)
        if matrix[row, column] != 0
    ]
    value = {
        "schema": "strict-386-auxiliary-q-sign-witness-v1",
        "coefficient_field": "Q",
        "basis": [
            {"block": "AUX_ETA", "start": 0, "dimension": 4, "degree": -1},
            {"block": "AUX_F_HAT", "start": 4, "dimension": 10, "degree": 0},
            {"block": "AUX_V", "start": 14, "dimension": 4, "degree": 0},
            {"block": "AUX_F_HAT_STAR", "start": 18, "dimension": 10, "degree": 1},
            {"block": "AUX_V_STAR", "start": 28, "dimension": 4, "degree": 1},
            {"block": "AUX_ETA_STAR", "start": 32, "dimension": 4, "degree": 2},
        ],
        "shape": [36, 36],
        "orientation": "entry[target_row,source_row]",
        "entries": entries,
        "observed_blocks": {
            "eta_to_v": "-I_4",
            "f_hat_to_f_hat_star": "A_g with 22 nonzero rational entries",
            "v_star_to_eta_star": "+I_4",
        },
        "nonzero_entries": len(entries),
        "matrix_sha256": digest,
        "authority_matrix_sha256": authority["matrix_sha256"]["auxiliary_differential"],
        "source": {
            "path": str(SOURCE.relative_to(ROOT)),
            "sha256": sha(SOURCE),
            "certificate_path": str(CERTIFICATE.relative_to(ROOT)),
            "certificate_sha256": sha(CERTIFICATE),
        },
    }
    return (json.dumps(value, indent=2) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = generated()
    if args.check:
        current = OUTPUT.is_file() and OUTPUT.read_bytes() == content
        print("STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1: " + ("current" if current else "stale"))
        return not current
    OUTPUT.write_bytes(content)
    print("STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1: wrote exact 36-row witness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
