#!/usr/bin/env python3
"""Independent verification of global conformal causal BV transport."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
CERT = ROOT / "d_quotient_classical/certificates/CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/conformally-related-cyclic-causal-transfer-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"source digest drifted: {relative}")
    dependencies = {}
    for name, record in value["dependency_refs"].items():
        path = ROOT / record["path"]
        if _sha256(path) != record["sha256"]:
            raise ValueError(f"dependency digest drifted: {name}")
        dependencies[name] = json.loads(path.read_text())
    if dependencies["abstract_causal_transfer"]["flags"]["ABSTRACT_CAUSAL_TRANSFER_CERTIFIED"] is not True:
        raise ValueError("abstract theorem import failed")
    if dependencies["cylinder_full_green_homotopy"]["causal_green_homotopy"] is not True:
        raise ValueError("cylinder Green import failed")

    r, a = sp.symbols("r a", nonzero=True, real=True)
    tangent = sp.Matrix([[r, 0, 0], [0, 1, 0], [0, -a, 1]])
    cotangent = tangent.inv().T
    full = sp.diag(tangent, cotangent)
    odd = sp.zeros(6)
    odd[:3, 3:] = sp.eye(3)
    odd[3:, :3] = -sp.eye(3)
    if sp.simplify(full.T * odd * full - odd) != sp.zeros(6):
        raise ValueError("independent BV-canonical check failed")
    if [[str(x) for x in row] for row in tangent.tolist()] != value["finite_BV_canonical_map"]["finite_fixture_tangent_matrix"]:
        raise ValueError("tangent map record drifted")
    if [[str(x) for x in row] for row in cotangent.tolist()] != value["finite_BV_canonical_map"]["finite_fixture_cotangent_matrix"]:
        raise ValueError("cotangent map record drifted")

    t = sp.symbols("t", real=True)
    omega = 1 + 1 / (10 * (1 + t**2))
    if sp.simplify(sp.factor(omega - 1) - 1 / (10 * (t**2 + 1))) != 0:
        raise ValueError("consumer lower bound failed")
    if sp.simplify(sp.factor(sp.Rational(11, 10) - omega) - t**2 / (10 * (t**2 + 1))) != 0:
        raise ValueError("consumer upper bound failed")
    if sp.simplify(sp.factor(sp.diff(sp.log(omega), t)) + 2 * t / ((t**2 + 1) * (10 * t**2 + 11))) != 0:
        raise ValueError("consumer affine coefficient failed")

    flags = value["flags"]
    if (
        flags["G3_OPEN_BACKGROUND_CLASS"] is not True
        or flags["ALL_LOCALLY_CONFORMALLY_FLAT_TOPOLOGIES"] is not False
        or flags["FIXED_UNTRANSFORMED_GAUGE_FERMION"] is not False
        or flags["QUANTUM_CLAIM"] is not False
    ):
        raise ValueError("claim boundary drifted")
    print("CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
