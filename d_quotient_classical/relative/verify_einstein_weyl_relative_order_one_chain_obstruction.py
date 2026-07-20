#!/usr/bin/env python3
"""Independent sparse-algebra replay of the order-one chain obstruction."""

from __future__ import annotations

from collections import Counter
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_CHAIN_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-one-chain-obstruction-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-one-chain-system-v1.schema.json"


def _load(path: Path):
    return json.loads(path.read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hom_dimension(source: dict[int, int], target: dict[int, int], order: int) -> int:
    derivative_weights = Counter(
        sum((0, 0, 1, -1)[index] for index in word)
        for word in combinations_with_replacement(range(4), order)
    )
    return sum(
        source_weight_multiplicity
        * derivative_weights[derivative_weight]
        * target.get(source_weight + derivative_weight, 0)
        for source_weight, source_weight_multiplicity in source.items()
        for derivative_weight in derivative_weights
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
        raise AssertionError("system payload drift")
    payload = _load(payload_path)
    payload_schema = _load(PAYLOAD_SCHEMA)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)

    p3 = {0: 8, 1: 5, -1: 5, 2: 1, -2: 1}
    p4 = {0: 3, 1: 1, -1: 1}
    w1 = {0: 6, 1: 3, -1: 3, 2: 1, -2: 1}
    w2 = {0: 4, 1: 1, -1: 1}
    dimensions = [
        _hom_dimension(p3, w1, 0),
        _hom_dimension(p3, w1, 1),
        _hom_dimension(p4, w2, 1),
    ]
    if dimensions != [80, 284, 42]:
        raise AssertionError("independent invariant-character census failed")

    entries = {
        (row, column): sp.Rational(value)
        for row, column, value in payload["matrix_coo"]
    }
    matrix = sp.SparseMatrix(822, 406, entries)
    rhs = sp.zeros(822, 1)
    for row, value in payload["rhs_sparse"]:
        rhs[row] = sp.Rational(value)
    system = certificate["exact_linear_system"]
    records = [
        [row, column, str(int(value.p)) if value.q == 1 else f"{int(value.p)}/{int(value.q)}"]
        for (row, column), value in sorted(entries.items())
    ]
    digest = hashlib.sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest()
    if digest != system["matrix_coo_sha256"]:
        raise AssertionError("matrix digest mismatch")
    rank = matrix.rank()
    augmented_rank = matrix.row_join(rhs).rank()
    if (rank, augmented_rank) != (398, 399):
        raise AssertionError("independent exact rank replay failed")

    witness = sp.zeros(822, 1)
    for row, value in system["left_null_witness"]["terms"]:
        witness[row] = sp.Rational(value)
    if any(witness.T * matrix):
        raise AssertionError("serialized witness is not left-null")
    evaluation = (witness.T * rhs)[0]
    if str(evaluation) != system["left_null_witness"]["evaluation"]:
        raise AssertionError("left-null witness evaluation mismatch")
    print(json.dumps({
        "status": "PASS",
        "invariant_dimensions": dimensions,
        "rank": rank,
        "augmented_rank": augmented_rank,
        "left_null_evaluation": str(evaluation),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
