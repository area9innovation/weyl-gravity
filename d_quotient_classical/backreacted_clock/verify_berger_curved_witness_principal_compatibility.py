#!/usr/bin/env python3
"""Independent audit of the submitted Berger W34 principal mismatch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY.json"
SOURCE = ROOT / "d_quotient_classical/certificates/BERGER_CURVED_CLOCK_REATTACHED_WITNESS.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _temporal_block(record: dict[str, object], start: int, rank: int) -> sp.Matrix:
    matrix = sp.zeros(rank)
    symbols = {"u": sp.Symbol("u"), "v": sp.Symbol("v"), "alpha_B": sp.Symbol("alpha_B", nonzero=True)}
    for row, column, terms in record["entries"]:
        if start <= row < start + rank and start <= column < start + rank:
            for exponents, coefficient in terms:
                if exponents == [4, 0, 0, 0]:
                    matrix[row - start, column - start] += sp.sympify(coefficient, locals=symbols)
    return matrix


def main() -> int:
    result = json.loads(CERTIFICATE.read_text())
    source = json.loads(SOURCE.read_text())
    artifact = source["operators"]["P34"]
    p34_path = ROOT / artifact["path"]
    assert _sha256(p34_path) == artifact["sha256"]
    p34 = json.loads(p34_path.read_text())

    ghost = _temporal_block(p34, 0, 5)
    field = _temporal_block(p34, 5, 12)
    antifield = _temporal_block(p34, 17, 12)
    identity = _temporal_block(p34, 29, 5)
    assert ghost == sp.eye(5)
    assert identity == sp.eye(5)
    assert field[:10, :10].rank() == 8
    assert antifield[:10, :10].rank() == 8
    assert field.rank() == 10
    assert antifield.rank() == 10
    assert field[0, 0] == 0

    audit = result["degree_block_audit"]
    assert audit["dressed_metric_rank"] == 8
    assert audit["required_metric_rank"] == 10
    assert audit["full_field_rank_with_two_clock_rows"] == 10
    assert result["normalized_obstruction"]["defect"] == "-1"
    assert result["normalization_test"]["J_only_corrected_metric_rank"] == 8
    flags = result["flags"]
    assert flags["BERGER_CURVED_WITNESS_ALGEBRAIC_IDENTITY"] is True
    assert flags["BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY"] is False
    assert flags["BERGER_CURVED_WITNESS_GREEN_EXECUTION"] is False
    assert flags["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"] is False
    print("independent Berger curved-witness principal compatibility audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
