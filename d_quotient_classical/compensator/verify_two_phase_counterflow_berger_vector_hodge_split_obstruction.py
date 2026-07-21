#!/usr/bin/env python3
"""Independent finite-matrix verifier for the Berger vector Hodge obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import (
    d_matrix,
    generators,
)

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_V1.json"
)
PAYLOAD = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_PAYLOAD_V1.json"
)
SCHEMA = Path(__file__).with_name("schema") / (
    "two-phase-counterflow-berger-vector-hodge-split-obstruction-v1.schema.json"
)
PAYLOAD_SCHEMA = Path(__file__).with_name("schema") / (
    "two-phase-counterflow-berger-vector-hodge-split-obstruction-payload-v1.schema.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _endpoint(q54: dict, two_j: int) -> sp.Matrix:
    n = two_j + 1
    spatial = generators(two_j)
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    matrix = sp.zeros(3 * n)
    for row, column, terms in q54["classical_unary_q1"]["matrix"]["entries"]:
        if not (22 <= row < 25 and 0 <= column < 3):
            continue
        block = sp.zeros(n)
        for exponents, coefficient in terms:
            if exponents[0] != 2:
                continue
            word = sp.eye(n)
            for axis in range(1, 4):
                word *= spatial[axis - 1] ** exponents[axis]
            block += sp.sympify(coefficient, locals={"u": u, "v": v, "alpha_B": 5}) * word
        matrix[(row - 22) * n : (row - 21) * n, column * n : (column + 1) * n] = sp.simplify(block)
    return matrix


def _round_generators(two_j: int) -> list[sp.Matrix]:
    n = two_j + 1
    j = sp.Rational(two_j, 2)
    weights = [-j + index for index in range(n)]
    raising = sp.zeros(n)
    for index, weight in enumerate(weights[:-1]):
        raising[index + 1, index] = sp.sqrt((j - weight) * (j + weight + 1))
    lowering = raising.T
    return [-sp.I * (raising + lowering) / 2, (lowering - raising) / 2, -sp.I * sp.diag(*weights)]


def _round_endpoint(q54: dict, two_j: int) -> sp.Matrix:
    n = two_j + 1
    spatial = _round_generators(two_j)
    matrix = sp.zeros(3 * n)
    for row, column, terms in q54["classical_unary_q1"]["matrix"]["entries"]:
        if not (22 <= row < 25 and 0 <= column < 3):
            continue
        block = sp.zeros(n)
        for exponents, coefficient in terms:
            if exponents[0] != 2:
                continue
            word = sp.eye(n)
            for axis in range(1, 4):
                word *= spatial[axis - 1] ** exponents[axis]
            block += sp.sympify(coefficient, locals={"u": 1, "v": 1, "alpha_B": 5}) * word
        matrix[(row - 22) * n : (row - 21) * n, column * n : (column + 1) * n] = sp.simplify(block)
    return matrix


def _replay(q54: dict) -> None:
    for two_j in range(1, 9):
        n = two_j + 1
        d0 = d_matrix(two_j, 0)
        exact = sp.simplify(d0 * (d0.conjugate().T * d0).inv() * d0.conjugate().T)
        coexact = sp.eye(3 * n) - exact
        endpoint = _endpoint(q54, two_j)
        forward = sp.simplify(coexact * endpoint * exact)
        backward = sp.simplify(exact * endpoint * coexact)
        expected = n if two_j % 2 else n - 1
        if endpoint != endpoint.conjugate().T:
            raise AssertionError(f"endpoint lost Hermiticity at two_j={two_j}")
        if forward != backward.conjugate().T:
            raise AssertionError(f"cross blocks lost adjointness at two_j={two_j}")
        if forward.rank() != expected or backward.rank() != expected:
            raise AssertionError(f"cross rank mismatch at two_j={two_j}")
    for two_j in range(1, 5):
        n = two_j + 1
        d0 = sp.Matrix.vstack(*_round_generators(two_j))
        exact = sp.simplify(d0 * (d0.conjugate().T * d0).inv() * d0.conjugate().T)
        coexact = sp.eye(3 * n) - exact
        endpoint = _round_endpoint(q54, two_j)
        if (coexact * endpoint * exact).rank() or (exact * endpoint * coexact).rank():
            raise AssertionError(f"round negative control failed at two_j={two_j}")


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for path in (SCHEMA, PAYLOAD_SCHEMA):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if certificate["payload_ref"]["sha256"] != _sha(PAYLOAD):
        raise AssertionError("payload hash mismatch")
    for item in certificate["imports"].values():
        path = ROOT / item["path"]
        if _sha(path) != item["sha256"]:
            raise AssertionError(f"dependency drifted: {path}")
    q54 = json.loads((ROOT / certificate["imports"]["gauge_fixed_q54"]["path"]).read_text())
    _replay(q54)
    terminal = certificate["terminal_verdict"]
    if terminal["complete_vector_tensor_quotient_status"] != "NOT_DEFINED_BEFORE_FULL_ISOTYPICAL_ENLARGEMENT":
        raise AssertionError("nonclosed split was promoted")
    if not terminal["q70_parent_preserved"]:
        raise AssertionError("full parent was incorrectly revoked")
    print("INDEPENDENT BERGER VECTOR-HODGE SPLIT OBSTRUCTION: PASS")


if __name__ == "__main__":
    main()
