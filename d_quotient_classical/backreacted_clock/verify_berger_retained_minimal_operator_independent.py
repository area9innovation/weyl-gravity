#!/usr/bin/env python3
"""Independent consumer check of the retained Berger operator preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR_PREFLIGHT.json"


def _matrix(record: dict[str, object], symbols: dict[str, sp.Symbol]) -> sp.SparseMatrix:
    shape = record["shape"]
    entries = record["entries"]
    body = {"shape": shape, "entries": entries}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert record["sha256"] == digest
    parsed = {
        (row, column): sp.sympify(expression, locals=symbols)
        for row, column, expression in entries
    }
    return sp.SparseMatrix(shape[0], shape[1], parsed)


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    names = ("p0", "p1", "p2", "p3", "a", "c", "alpha_B")
    symbols = {name: sp.Symbol(name, nonzero=name in {"a", "c", "alpha_B"}) for name in names}
    matrices = {name: _matrix(record, symbols) for name, record in payload["matrices"].items()}
    gauge = matrices["K_spatial_full_frame_symbol"]
    noether = matrices["minus_K_spatial_sharp_full_frame_symbol"]
    p_flip = {symbols[f"p{i}"]: -symbols[f"p{i}"] for i in range(4)}
    assert gauge.shape == (10, 3)
    assert noether.shape == (3, 10)
    assert sp.simplify(noether + gauge.subs(p_flip, simultaneous=True).T) == sp.zeros(3, 10)

    bach = matrices["Bach_fourth_order_principal"]
    matter = matrices["matter_second_order_covariant_symbol"]
    assert bach.shape == matter.shape == (10, 10)
    assert sp.simplify(bach - bach.T) == sp.zeros(10)
    assert sp.simplify(matter - matter.T) == sp.zeros(10)
    principal_gauge = gauge - gauge.subs({symbols[f"p{i}"]: 0 for i in range(4)})
    assert sp.simplify(bach * principal_gauge) == sp.zeros(10, 3)
    assert sp.simplify(matter * principal_gauge) == sp.zeros(10, 3)

    flags = payload["flags"]
    assert flags["retained_gauge_and_noether_rows_complete"] is True
    assert flags["retained_matter_hessian_complete"] is True
    assert flags["retained_Bach_principal_complete"] is True
    assert flags["retained_Bach_lower_order_PBW_complete"] is False
    assert flags["BERGER_RETAINED_MINIMAL_OPERATOR"] is False
    assert payload["nonconformally_flat_guard"]["round_cylinder_lower_order_hessian_reused"] is False
    assert payload["next_gate"] == "BERGER_LINEARIZED_BACH_PBW_EXPANSION"

    print("BERGER_RETAINED_MINIMAL_OPERATOR_PREFLIGHT_INDEPENDENT: PASS")
    print("K/Ksharp, symmetric principal matrices, and principal gauge kernels: PASS")
    print("lower-order Berger Bach PBW and parent gate: OPEN")


if __name__ == "__main__":
    main()
