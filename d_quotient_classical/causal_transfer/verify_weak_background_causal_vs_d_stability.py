#!/usr/bin/env python3
"""Independent verifier for weak-background causal versus D stability."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/weak-background-causal-vs-d-stability-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero(matrix: sp.Matrix) -> bool:
    return all(sp.factor(value) == 0 for value in matrix)


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for ref in value["dependency_refs"].values():
        path = ROOT / ref["path"]
        if _sha(path) != ref["sha256"]:
            raise AssertionError(f"dependency hash drifted: {path}")
        imported = json.loads(path.read_text())
        if imported["result_id"] != ref["artifact_id"]:
            raise AssertionError(f"dependency id drifted: {path}")

    for rel, digest in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / rel) != digest:
            raise AssertionError(f"source hash drifted: {rel}")

    t, z = sp.symbols("t z", real=True)
    phi_spatial = sp.log(1 + z / 10)
    if sp.diff(phi_spatial, t) != 0:
        raise AssertionError("positive fixture is not D invariant")
    phi_time = sp.log(1 + 1 / (10 * (1 + t**2)))
    sigma = sp.factor(sp.diff(phi_time, t))
    if sp.factor(sigma + 2 * t / ((t**2 + 1) * (10 * t**2 + 11))) != 0:
        raise AssertionError("negative fixture Weyl component drifted")
    if sp.simplify(sigma.subs(t, 1)) != -sp.Rational(1, 21):
        raise AssertionError("negative fixture witness drifted")

    q0 = sp.Matrix([[0, 0], [1, 0]])
    i0 = sp.Matrix([[0, 1], [0, 0]])
    q = sp.diag(sp.Rational(3, 2) * q0, -sp.Rational(1, 2) * q0)
    iota = sp.diag(i0, i0)
    lie = q * iota + iota * q
    expected = sp.diag(
        sp.Rational(3, 2),
        sp.Rational(3, 2),
        -sp.Rational(1, 2),
        -sp.Rational(1, 2),
    )
    if not _zero(lie - expected):
        raise AssertionError("independent Cartan replay failed")
    h = iota * expected.inv()
    if not _zero(q * h + h * q - sp.eye(4)):
        raise AssertionError("independent contraction replay failed")

    flags = value["flags"]
    if not (
        flags["CONFORMAL_CYLINDER_CAUSAL_OPEN_CLASS"]
        and flags["BACH_FLAT_RELATIVE_ADM_CAUSAL_OPEN_CLASS"]
        and flags["KS_COMMON_SLAB_CAUSAL_STABILITY"]
    ):
        raise AssertionError("a positive causal domain disappeared")
    for name in (
        "CAUSAL_STABILITY_IMPLIES_D_CARTAN_STABILITY",
        "D_CARTAN_ON_ALL_BACH_FLAT_BACKGROUNDS",
        "KS_NONZERO_WHOLE_CYLINDER_NEIGHBOURHOOD",
        "HADAMARD_TRANSFER",
        "QUANTUM_CLAIM",
    ):
        if flags[name]:
            raise AssertionError(f"forbidden promotion: {name}")

    ledger = {row["class"]: row for row in value["cross_class_ledger"]}
    positive = ledger["globally conformal cylinder, D(phi)=0"]
    negative = ledger["globally conformal cylinder, D(phi)!=0"]
    if positive["causal_complex"] != "CERTIFIED" or positive["fixed_residual_D"] != "CERTIFIED":
        raise AssertionError("positive same-target row drifted")
    if negative["causal_complex"] != "CERTIFIED" or "OBSTRUCTED" not in negative["fixed_residual_D"]:
        raise AssertionError("causal-versus-D split drifted")


if __name__ == "__main__":
    verify()
    print("independent weak-background causal-versus-D audit: PASS")
