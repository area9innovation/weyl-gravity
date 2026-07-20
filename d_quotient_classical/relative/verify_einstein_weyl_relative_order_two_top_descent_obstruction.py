#!/usr/bin/env python3
"""Independent sparse-algebra replay of the order-two top-descent obstruction."""

from __future__ import annotations

from collections import Counter
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_TWO_TOP_DESCENT_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-two-top-descent-obstruction-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-two-top-descent-system-v1.schema.json"


def _load(path: Path):
    return json.loads(path.read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hom_dimension(
    source: dict[int, int], target: dict[int, int], order: int
) -> int:
    derivative_weights = Counter(
        sum((0, 0, 1, -1)[index] for index in word)
        for word in combinations_with_replacement(range(4), order)
    )
    return sum(
        source_multiplicity
        * derivative_multiplicity
        * target.get(source_weight + derivative_weight, 0)
        for source_weight, source_multiplicity in source.items()
        for derivative_weight, derivative_multiplicity in derivative_weights.items()
    )


def main() -> None:
    certificate = _load(CERT)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    for artifact in certificate["dependencies"].values():
        if _sha(ROOT / artifact["path"]) != artifact["sha256"]:
            raise AssertionError(f"dependency drift: {artifact['path']}")
    payload_path = ROOT / certificate["system_payload"]["path"]
    if _sha(payload_path) != certificate["system_payload"]["sha256"]:
        raise AssertionError("top-descent payload drift")
    payload = _load(payload_path)
    payload_schema = _load(PAYLOAD_SCHEMA)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)

    p3 = {0: 8, 1: 5, -1: 5, 2: 1, -2: 1}
    p4 = {0: 3, 1: 1, -1: 1}
    w1 = {0: 6, 1: 3, -1: 3, 2: 1, -2: 1}
    w2 = {0: 4, 1: 1, -1: 1}
    dimensions = [
        _hom_dimension(p3, w1, 2),
        _hom_dimension(p4, w2, 2),
    ]
    if dimensions != [626, 86]:
        raise AssertionError("independent invariant-character census failed")

    entries = {
        (row, column): sp.Rational(value)
        for row, column, value in payload["matrix_coo"]
    }
    matrix = sp.SparseMatrix(1056, 712, entries)
    functional = sp.zeros(1, 712)
    for column, value in payload["sensitivity_sparse"]:
        functional[column] = sp.Rational(value)
    rowspace = sp.zeros(1, 1056)
    for row, value in payload["rowspace_witness_sparse"]:
        rowspace[row] = sp.Rational(value)

    records = [
        [row, column, str(value)]
        for (row, column), value in sorted(entries.items())
    ]
    digest = hashlib.sha256(
        json.dumps(records, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != certificate["system_payload"]["matrix_coo_sha256"]:
        raise AssertionError("matrix digest mismatch")
    rank = matrix.rank()
    appended_rank = matrix.col_join(functional).rank()
    if (rank, appended_rank) != (516, 516):
        raise AssertionError("exact top-descent rank replay failed")
    if rowspace * matrix != functional:
        raise AssertionError("serialized rowspace witness failed")
    if not any(functional):
        raise AssertionError("unrestricted sensitivity unexpectedly vanished")

    layout = payload["row_layout"]
    for record in certificate["top_descent_system"]["rowspace_witness_rows"]:
        if layout[record["row"]] != {
            "row": record["row"],
            "word": record["word"],
            "output_local": record["output_local"],
            "input_local": record["input_local"],
        }:
            raise AssertionError("rowspace witness semantic layout mismatch")
    print(
        json.dumps(
            {
                "status": "PASS",
                "invariant_dimensions": dimensions,
                "shape": list(matrix.shape),
                "rank": rank,
                "kernel_dimension": matrix.cols - rank,
                "rank_with_sensitivity": appended_rank,
                "rowspace_witness_nonzero_entries": len(rowspace.todok()),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
