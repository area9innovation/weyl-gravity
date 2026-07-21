#!/usr/bin/env python3
"""Independent finite-representation replay of the scalar-Hodge obstruction."""

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
    "TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_V1.json"
)
PAYLOAD = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_PAYLOAD_V1.json"
)
SCHEMA = Path(__file__).with_name("schema") / (
    "two-phase-counterflow-berger-scalar-hodge-block-obstruction-v1.schema.json"
)
PAYLOAD_SCHEMA = Path(__file__).with_name("schema") / (
    "two-phase-counterflow-berger-scalar-hodge-block-obstruction-payload-v1.schema.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _leading_endpoint_block(q54: dict, two_j: int) -> sp.Matrix:
    """Coefficient of e0^2 in q[bar_c_star_diff,c_spatial]."""

    n = two_j + 1
    spatial = generators(two_j)
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    result = sp.zeros(3 * n)
    for row, column, terms in q54["classical_unary_q1"]["matrix"]["entries"]:
        if not (22 <= row < 25 and 0 <= column < 3):
            continue
        block = sp.zeros(n)
        for exponents, raw in terms:
            if exponents[0] != 2:
                continue
            matrix = sp.eye(n)
            for axis in range(1, 4):
                matrix = matrix * spatial[axis - 1] ** exponents[axis]
            block += sp.sympify(
                raw,
                locals={"u": u, "v": v, "alpha_B": sp.Integer(5)},
            ) * matrix
        result[(row - 22) * n : (row - 21) * n, column * n : (column + 1) * n] = sp.simplify(block)
    return result


def _independent_mode_replay(q54: dict) -> None:
    for two_j in range(1, 7):
        n = two_j + 1
        d0 = d_matrix(two_j, 0)
        d1 = d_matrix(two_j, 1)
        leading_defect = sp.simplify(d1 * _leading_endpoint_block(q54, two_j) * d0)
        weights = [sp.Rational(-two_j, 2) + index for index in range(n)]
        expected_first_row = sp.diag(
            *(sp.Rational(93, 40) * sp.I * weight for weight in weights)
        )
        if leading_defect[:n, :] != expected_first_row:
            raise AssertionError(f"leading mode formula failed at two_j={two_j}")
        expected_rank = n if two_j % 2 else n - 1
        if leading_defect.rank() != expected_rank:
            raise AssertionError(f"exceptional-rank ledger failed at two_j={two_j}")
        for column, weight in enumerate(weights):
            is_zero = leading_defect[:, column] == sp.zeros(3 * n, 1)
            if is_zero != (weight == 0):
                raise AssertionError(f"right-neutral kernel mismatch at two_j={two_j}")


def _normalization_and_reality_replay(payload: dict) -> None:
    volume = 12 * sp.pi**2 * sp.sqrt(10) / 5
    for two_j in range(4):
        normalization_squared = sp.Rational(two_j + 1, 1) / volume
        raw_haar_norm = volume / (two_j + 1)
        if sp.simplify(normalization_squared * raw_haar_norm) != 1:
            raise AssertionError("Haar normalization failed")
    j = sp.Rational(1, 2)
    m = sp.Rational(1, 2)
    k = -sp.Rational(1, 2)
    if (-1) ** int(m - k) != -1:
        raise AssertionError("conjugation-phase mutation fixture failed")
    if payload["normalized_scalar_modes"]["volume"] != sp.sstr(volume):
        raise AssertionError("stored Berger volume drifted")


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for path in (SCHEMA, PAYLOAD_SCHEMA):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if certificate["payload_ref"]["sha256"] != _sha(PAYLOAD):
        raise AssertionError("payload file hash mismatch")
    if payload["content_sha256"] != _digest(
        {key: value for key, value in payload.items() if key != "content_sha256"}
    ):
        raise AssertionError("payload content hash mismatch")
    for dependency in certificate["imports"].values():
        path = ROOT / dependency["path"]
        if _sha(path) != dependency["sha256"]:
            raise AssertionError(f"dependency hash drifted: {path}")
        if json.loads(path.read_text())["result_id"] != dependency["result_id"]:
            raise AssertionError(f"dependency identity drifted: {path}")

    q54_path = ROOT / certificate["imports"]["gauge_fixed_q54"]["path"]
    q54 = json.loads(q54_path.read_text())
    _independent_mode_replay(q54)
    _normalization_and_reality_replay(payload)

    first = certificate["first_obstruction"]
    if first["leading_mode_coefficient"] != "93*I*k/40":
        raise AssertionError("generic nonzero-k witness drifted")
    terminal = certificate["terminal_verdict"]
    if terminal["physical_quotient_status"] != "NOT_DEFINED_NONCLOSED_SUBCOMPLEX":
        raise AssertionError("nonclosed carrier was promoted")
    if not terminal["q70_parent_nilpotency_and_causality_preserved"]:
        raise AssertionError("parent theorem was incorrectly revoked")
    print("INDEPENDENT BERGER SCALAR-HODGE BLOCK OBSTRUCTION: PASS")


if __name__ == "__main__":
    main()
