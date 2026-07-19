"""Independent verifier for the fixed-ell constant-twist zero-map theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_zero_map.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / value["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert hashlib.sha256(schema_path.read_bytes()).hexdigest() == value["schema_sha256"]
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    lam, k, omega, alpha, j = sp.symbols("lambda k omega alpha j", real=True)
    K = k + alpha * j
    p = omega**2 - K**2 - lam + sp.Rational(2, 3)
    q = (omega**2 - K**2 - lam) ** 2 - 2 * lam
    assert sp.diff(p, alpha).subs({alpha: 0, k: 0}) == 0
    assert sp.diff(q, alpha).subs({alpha: 0, k: 0}) == 0
    matrix_checks = value["flat_connection_reduction"]["primary_derivative"]["matrix_gram_checks"]
    assert matrix_checks["q"]["dimension"] == 2 and matrix_checks["q"]["shell_remainder_rank"] == 0
    assert matrix_checks["p"]["dimension"] == 4 and matrix_checks["p"]["shell_remainder_rank"] == 0
    matrices = value["multiplicity_matrices"]
    assert sp.Matrix(matrices["Q_(ell,-)"]["matrix"]) == sp.zeros(2)
    assert sp.Matrix(matrices["Q_(ell,+)"]["matrix"]) == sp.zeros(2)
    assert sp.Matrix(matrices["P_ell"]["matrix"]) == sp.zeros(4)
    assert value["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "OPEN"
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_FIXED_ELL_CONSTANT_TWIST_ZERO_MAP independent verification: PASS")


if __name__ == "__main__":
    main()
