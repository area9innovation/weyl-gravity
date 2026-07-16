#!/usr/bin/env python3
"""Independent consumer for the Berger 54-to-26 causal reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _identity_matrix,
    _is_zero,
    _matrix_add,
    _sparse_multiply,
    _subtract,
)
from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json"
GAUGE_FIXED = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
RETAINED = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"


def verify() -> None:
    theorem = json.loads(CERTIFICATE.read_text())
    full = json.loads(GAUGE_FIXED.read_text())
    retained = json.loads(RETAINED.read_text())
    dependency = theorem["dependency_refs"]["gauge_fixed_54_row_unary"]
    assert dependency["sha256"] == hashlib.sha256(GAUGE_FIXED.read_bytes()).hexdigest()

    q54 = _matrix_from_record(full["classical_unary_q1"]["matrix"])
    inclusion = _matrix_from_record(full["contraction"]["iota_cl"])
    projection = _matrix_from_record(full["contraction"]["pi_cl"])
    homotopy = _matrix_from_record(full["contraction"]["S_cl"])
    k = _matrix_from_record(retained["q1_blocks"]["K_spatial"])
    h = _matrix_from_record(retained["q1_blocks"]["H_retained"])
    c = _matrix_from_record(retained["q1_blocks"]["minus_K_spatial_sharp"])
    zero = q54[0][0].scale(0)
    q26 = [[zero for _ in range(26)] for _ in range(26)]
    for block, ro, co in ((k, 3, 0), (h, 13, 3), (c, 23, 13)):
        for row in range(len(block)):
            for column in range(len(block[0])):
                q26[ro + row][co + column] = block[row][column]

    assert _is_zero(_subtract(_sparse_multiply(q54, inclusion), _sparse_multiply(inclusion, q26)))
    assert _is_zero(_subtract(_sparse_multiply(projection, q54), _sparse_multiply(q26, projection)))
    assert _is_zero(_subtract(_sparse_multiply(projection, inclusion), _identity_matrix(26)))
    complement = _subtract(_identity_matrix(54), _sparse_multiply(inclusion, projection))
    contracted = _matrix_add(_sparse_multiply(q54, homotopy), _sparse_multiply(homotopy, q54))
    assert _is_zero(_subtract(contracted, complement))
    assert _is_zero(_sparse_multiply(homotopy, homotopy))
    assert theorem["flags"]["BERGER_54_ROW_CAUSAL_REDUCTION"] is True
    assert theorem["flags"]["BERGER_CAUSAL_GREEN_HOMOTOPY"] is False
    assert theorem["next_gate"] == "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    verify()
    print("BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
