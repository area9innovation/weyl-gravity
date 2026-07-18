#!/usr/bin/env python3
"""Independent replay of the transverse curvature-incidence variation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _adjoint_basis,
    _coordinate_map,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import fixture


CERTIFICATE = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-curvature-incidence-variation-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _deserialize(record: dict) -> sp.Matrix:
    matrix = sp.zeros(*record["shape"])
    for row, column, value in record["entries"]:
        matrix[row, column] = sp.Rational(value)
    return matrix


def _independent_incidence() -> tuple[sp.Matrix, sp.Matrix]:
    metric = sp.diag(-1, 1, 1, 1)
    planes = ((0, 1, 2), (0, 2, -1), (0, 3, -1), (1, 2, 1), (1, 3, 1), (2, 3, -2))

    def curvature(a: int, b: int, c: int, d: int) -> sp.Expr:
        answer = 0
        for left, right, value in planes:
            first = int((a, b) == (left, right)) - int((a, b) == (right, left))
            second = int((c, d) == (left, right)) - int((c, d) == (right, left))
            answer += value * first * second
        return sp.Integer(answer)

    names, basis = _adjoint_basis()
    embedded, left_inverse = _coordinate_map(basis)
    incidence = sp.zeros(60, 4)
    for left, right, _ in planes:
        standard = sp.zeros(6)
        for raised in range(4):
            for lowered in range(4):
                standard[1 + raised, 1 + lowered] = sum(
                    metric[raised, contracted] * curvature(left, right, contracted, lowered)
                    for contracted in range(4)
                )
        coordinates = left_inverse * standard.reshape(36, 1)
        if embedded * coordinates != standard.reshape(36, 1):
            raise AssertionError("independent curvature escaped adjoint tractors")
        incidence[15 * left : 15 * (left + 1), right] = coordinates
        incidence[15 * right : 15 * (right + 1), left] = -coordinates
    if tuple(names[4:10]) != ("M01", "M02", "M03", "M12", "M13", "M23"):
        raise AssertionError("adjoint basis order drifted")
    p0 = fixture()["screen"].harmonic_p0
    return incidence, -incidence * p0


def verify() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    incidence, correction = _independent_incidence()
    if incidence != _deserialize(certificate["exact_data"]["delta_curvature_incidence"]):
        raise AssertionError("independent incidence disagrees")
    if correction != _deserialize(certificate["exact_data"]["delta_daut_incidence_term"]):
        raise AssertionError("independent automorphism correction disagrees")
    if incidence.rank() != 4 or len(incidence.todok()) != 12:
        raise AssertionError("independent incidence rank/support failed")
    if -sp.Rational(1, 2) * incidence[4, 1] != 1:
        raise AssertionError("independent normalization failed")
    if not all(certificate["exact_checks"].values()):
        raise AssertionError("certificate contains a failed exact check")
    for record in certificate["dependency_refs"].values():
        path = ROOT / record["path"]
        payload = json.loads(path.read_text())
        if _sha(path) != record["sha256"] or payload["result_id"] != record["result_id"]:
            raise AssertionError("dependency drifted")
    for name, digest in certificate["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source hash mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1 independent verification: PASS")
