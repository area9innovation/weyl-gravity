#!/usr/bin/env python3
"""Independent frozen-record audit of the unary D-Cartan obstruction."""

from __future__ import annotations

import hashlib
import json

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
    _symbol,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _matrix_record(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]


def main() -> int:
    result = json.loads(
        (ROOT / "d_quotient_classical/certificates/BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION.json").read_text()
    )
    q1 = json.loads(
        (ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json").read_text()
    )
    d_action = json.loads(
        (ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json").read_text()
    )
    blocks = q1["q1_blocks"]
    k = _matrix_from_record(blocks["K_spatial"])
    h = _matrix_from_record(blocks["H_retained"])
    identity = _matrix_from_record(blocks["minus_K_spatial_sharp"])
    d26 = _matrix_from_record(d_action["retained_D_action"]["matrix"])
    p0, p1, p2, p3 = sp.symbols("p0:4")
    fixture = {p0: 1, p1: 1, p2: 0, p3: 0}
    k1 = sp.Matrix(_symbol(k, 1).subs(fixture))
    h4_unspecialized = sp.Matrix(_symbol(h, 4).subs(fixture))
    alpha_B = next(
        symbol for symbol in h4_unspecialized.free_symbols if symbol.name == "alpha_B"
    )
    h4 = h4_unspecialized.subs({alpha_B: 5})
    l1 = sp.Matrix(_symbol(identity, 1).subs(fixture))
    ds = sp.Matrix(_symbol(d26, 1).subs(fixture))
    assert (k1.rank(), h4.rank(), l1.rank()) == (3, 1, 3)
    assert h4 * k1 == sp.zeros(10, 3)
    assert l1 * h4 == sp.zeros(3, 10)
    assert ds == sp.eye(26)
    witness = result["normalized_field_class"]
    x = sp.Matrix([sp.Rational(value) for value in witness["representative"]])
    dual = sp.Matrix([sp.Rational(value) for value in witness["dual_witness"]])
    assert h4 * x == sp.zeros(10, 1)
    assert dual.T * k1 == sp.zeros(1, 3)
    assert (dual.T * x)[0] == 1
    assert result["douglis_symbol_fixture"]["cohomology_dimensions"] == [0, 6, 6, 0]
    assert result["dependency_tags"] == ["LOCAL-ALGEBRAIC"]
    assert result["method_tags"] == ["MICROLOCAL-SYMBOL"]
    hashes = result["douglis_symbol_fixture"]["specialized_symbol_sha256"]
    assert hashes == {
        "K1": _canonical_hash(_matrix_record(k1)),
        "H4": _canonical_hash(_matrix_record(h4)),
        "L1": _canonical_hash(_matrix_record(l1)),
        "D1": _canonical_hash(_matrix_record(ds)),
    }
    for name, matrix in {"K1": k1, "H4": h4, "L1": l1}.items():
        minor = result["douglis_symbol_fixture"]["rank_witness_minors"][name]
        assert str(matrix.extract(minor["rows"], minor["columns"]).det()) == minor["determinant"]
    assert result["flags"]["BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO"] is True
    assert result["flags"]["BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D"] is False
    print("independent null-symbol class and unary D-Cartan obstruction: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
