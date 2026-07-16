#!/usr/bin/env python3
"""Independent replay of the frozen raw Berger witness artifacts."""

from __future__ import annotations

import hashlib
import json

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
)
from d_quotient_classical.backreacted_clock.berger_curved_witness_export import (
    _adjoint_matrix,
    _is_zero,
    _matrix_add,
    _sparse_multiply,
)
from d_quotient_classical.backreacted_clock.berger_curved_witness_principal_compatibility import (
    _temporal_order_four,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT
from d_quotient_classical.backreacted_clock.berger_raw_clock_reattached_witness_transport import (
    CERTIFICATE_PATH,
)


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_artifact(reference):
    path = ROOT / reference["path"]
    if _sha256(path) != reference["sha256"]:
        raise AssertionError(f"artifact digest mismatch: {path}")
    return json.loads(path.read_text())


def _subtract(left, right):
    return [[left[row][column] + right[row][column].scale(-1)
             for column in range(len(left[0]))] for row in range(len(left))]


def _slice(matrix, rows, columns):
    return [[matrix[row][column] for column in columns] for row in rows]


def verify() -> None:
    certificate = json.loads(CERTIFICATE_PATH.read_text())
    flags = certificate["flags"]
    if flags != {
        "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        "BERGER_RAW_CLOCK_REATTACHED_GREEN_INVERSION": False,
        "BERGER_RAW_CLOCK_REATTACHED_PRINCIPAL_COMPATIBILITY": True,
        "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT": True,
    }:
        raise AssertionError("raw witness lifecycle flags drifted")

    f = _matrix_from_record(_load_artifact(
        certificate["coordinate_transport"]["artifacts"]["raw_to_dressed_F12"]
    ))
    c = _matrix_from_record(_load_artifact(
        certificate["coordinate_transport"]["artifacts"]["dressed_to_raw_C12"]
    ))
    identity12 = [[f[row][column].from_terms(((0, (), sp.S.One),))
                   if row == column else f[row][column].from_terms(())
                   for column in range(12)] for row in range(12)]
    if not _is_zero(_subtract(_sparse_multiply(f, c), identity12)):
        raise AssertionError("independent F C replay failed")
    if not _is_zero(_subtract(_sparse_multiply(c, f), identity12)):
        raise AssertionError("independent C F replay failed")

    q = _matrix_from_record(_load_artifact(certificate["operators"]["q34_raw"]))
    w = _matrix_from_record(_load_artifact(certificate["operators"]["W34_raw"]))
    p = _matrix_from_record(_load_artifact(certificate["operators"]["P34_raw"]))
    pairing = _matrix_from_record(_load_artifact(certificate["operators"]["pairing34_raw"]))

    # Replay qW+Wq blockwise from frozen artifacts.  The degree layout makes
    # all off-diagonal target blocks identically zero.
    qw = _sparse_multiply(q, w)
    wq = _sparse_multiply(w, q)
    degree_ranges = (range(0, 5), range(5, 17), range(17, 29), range(29, 34))
    for indices in degree_ranges:
        block = _slice(p, indices, indices)
        replay = _matrix_add(
            _slice(qw, indices, indices),
            _slice(wq, indices, indices),
        )
        if not _is_zero(_subtract(replay, block)):
            raise AssertionError("independent qW+Wq replay failed")

    if not _is_zero(_matrix_add(
        _sparse_multiply(_adjoint_matrix(q), pairing),
        _sparse_multiply(pairing, q),
    )):
        raise AssertionError("independent q cyclicity replay failed")
    if not _is_zero(_matrix_add(
        _sparse_multiply(_adjoint_matrix(w), pairing),
        _sparse_multiply(pairing, w),
    )):
        raise AssertionError("independent W cyclicity replay failed")

    p_record = _load_artifact(certificate["operators"]["P34_raw"])
    ghost = _temporal_order_four(p_record, 0, 5)
    field = _temporal_order_four(p_record, 5, 12)
    antifield = _temporal_order_four(p_record, 17, 12)
    identity = _temporal_order_four(p_record, 29, 5)
    if ghost != sp.eye(5) or identity != sp.eye(5):
        raise AssertionError("endpoint principal replay failed")
    if field[:10, :10] != sp.eye(10) or antifield[:10, :10] != sp.eye(10):
        raise AssertionError("metric principal replay failed")
    if field[10:12, 10:12] != sp.zeros(2, 2):
        raise AssertionError("clock principal diagonal replay failed")

    print("independent raw Berger witness transport replay: PASS")
    print("Green inversion remains fail-closed")


if __name__ == "__main__":
    verify()
