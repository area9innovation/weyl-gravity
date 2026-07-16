#!/usr/bin/env python3
"""Independent PBW consumer for the complete Berger local D action."""

from __future__ import annotations

import hashlib
import json

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record
from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _is_zero,
    _sparse_multiply,
    _subtract,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
GAUGE_FIXED = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    unary = json.loads(GAUGE_FIXED.read_text())
    assert payload["dependency_refs"]["gauge_fixed_54_row_unary"]["sha256"] == hashlib.sha256(GAUGE_FIXED.read_bytes()).hexdigest()
    q = _matrix_from_record(unary["classical_unary_q1"]["matrix"])
    d = _matrix_from_record(payload["D_action"]["matrix"])
    inclusion = _matrix_from_record(unary["contraction"]["iota_cl"])
    projection = _matrix_from_record(unary["contraction"]["pi_cl"])
    homotopy = _matrix_from_record(unary["contraction"]["S_cl"])
    d_retained = _matrix_from_record(payload["retained_D_action"]["matrix"])
    assert _is_zero(_subtract(_sparse_multiply(q, d), _sparse_multiply(d, q)))
    assert _is_zero(_subtract(_sparse_multiply(d, inclusion), _sparse_multiply(inclusion, d_retained)))
    assert _is_zero(_subtract(_sparse_multiply(projection, d), _sparse_multiply(d_retained, projection)))
    assert _is_zero(_subtract(_sparse_multiply(d, homotopy), _sparse_multiply(homotopy, d)))
    assert payload["flags"]["BERGER_LOCAL_D_ACTION_EQUIVARIANT"] is True
    assert payload["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is False


def main() -> int:
    verify()
    print("BERGER_54_ROW_LOCAL_D_ACTION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
