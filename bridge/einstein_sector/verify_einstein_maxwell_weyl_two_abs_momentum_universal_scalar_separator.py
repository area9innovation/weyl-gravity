"""Independent verifier for the universal signed 1:-2 scalar separator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_two_abs_momentum_universal_scalar_separator.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if payload["schema_sha256"] != sha(schema_path):
        raise AssertionError("universal separator schema hash changed")
    for name, item in payload["provenance"]["inputs"].items():
        if item["sha256"] != sha(ROOT / item["path"]):
            raise AssertionError(f"stale universal-separator input: {name}")
    omega, t1, t2 = sp.symbols("omega t1 t2", positive=True)
    B, C = t2 / 2 - t1, -t1 * t2 / 2
    if sp.expand(omega**2 + B * omega + C - (omega - t1) * (2 * omega + t2) / 2) != 0:
        raise AssertionError("n=1 factorization failed")
    if sp.expand(omega**2 - 2 * B * omega + 4 * C - (omega - t2) * (omega + 2 * t1)) != 0:
        raise AssertionError("n=-2 factorization failed")
    rows = payload["candidate_coverage"]
    if len(rows) != 15 or [row["candidate_index"] for row in rows] != list(range(1, 16)):
        raise AssertionError("candidate coverage changed")
    for row in rows:
        rho = sp.sympify(row["rho"], locals={"sqrt": sp.sqrt})
        if rho.is_positive is not True or row["bounded_generic_cone"] != "{0}":
            raise AssertionError(f"candidate {row['candidate_index']} failed")
    flags = payload["classification"]
    if not flags["universal_positive_rho_separator_certified"] or not flags["all_15_opposite_signed_real_generic_bounded_cones_are_origin"]:
        raise AssertionError("universal lifecycle changed")
    if flags["smooth_cones_classified_here"] or flags["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("universal theorem exceeded scope")
    print("EINSTEIN_MAXWELL_WEYL_TWO_ABS_MOMENTUM_UNIVERSAL_SCALAR_SEPARATOR verifier: PASS")


if __name__ == "__main__":
    verify()
