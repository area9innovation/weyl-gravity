#!/usr/bin/env python3
"""Independent replay of the finite KS four-block incidence obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-ks-four-block-incidence-obstruction-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, ref in value["dependency_refs"].items():
        path = ROOT / ref["path"]
        payload = json.loads(path.read_text())
        if _sha(path) != ref["sha256"] or payload["result_id"] != ref["artifact_id"]:
            raise ValueError(f"dependency drifted: {name}")
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise ValueError(f"source drifted: {relative}")

    e = sp.symbols("e", real=True)
    b = 1 - e**2 / 6
    metric = sp.diag(-1, 1, b**2, b**2)
    # Directly evaluate the trace-free symmetrized-gradient symbol channel.
    zeta = sp.Matrix([0, 0, 1, 0])
    vector = sp.Matrix([0, 0, 1, 0])
    covector = metric * vector
    contraction = (zeta.T * vector)[0]
    tensor = sp.zeros(4)
    for mu in range(4):
        for nu in range(4):
            tensor[mu, nu] = (
                zeta[mu] * covector[nu]
                + zeta[nu] * covector[mu]
                - sp.Rational(1, 2) * metric[mu, nu] * contraction
            )
    metric0 = sp.diag(-1, 1, 1, 1)
    trace0 = sp.trace(metric0 * tensor)
    transported = tensor - sp.Rational(1, 4) * metric0 * trace0
    channel = sp.expand(transported[2, 2])
    defect = sp.factor(channel - sp.Rational(3, 2))
    expected = sp.factor(5 * e**2 * (e**2 - 12) / 144)
    if sp.factor(defect - expected) != 0:
        raise ValueError("independent conformal-Killing symbol replay failed")
    if sp.diff(defect, e).subs(e, 0) != 0 or sp.diff(defect, e, 2).subs(e, 0) != -sp.Rational(5, 6):
        raise ValueError("order-of-first-failure replay failed")
    diagonal_transport = sp.Matrix(
        [
            [1, -sp.Rational(1, 4) + 1 / (4 * b**2), -sp.Rational(1, 4) + 1 / (4 * b**2)],
            [0, sp.Rational(3, 4) + 1 / (4 * b**2), -sp.Rational(1, 4) + 1 / (4 * b**2)],
            [0, -sp.Rational(1, 4) + 1 / (4 * b**2), sp.Rational(3, 4) + 1 / (4 * b**2)],
        ]
    )
    determinant = sp.factor(diagonal_transport.det())
    if determinant != sp.factor((b**2 + 1) / (2 * b**2)):
        raise ValueError("output transport determinant replay failed")
    if value["flags"]["TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER"]:
        raise ValueError("common-slab theorem was promoted before six-block HPL")
    print("NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
