#!/usr/bin/env python3
"""Independent verifier for the typed 160-row unary pushout."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112.json"
X = P / "certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112_PAYLOAD.json"
SCHEMA = P / "schema/berger-apparatus-combined-q1-after-replacement-112-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    pushout = payload["typed_pushout"]
    assert pushout["direct_sum_row_count"] - pushout["relation_rank"] == 160
    relation = sp.zeros(8, 168)
    for row, item in enumerate(pushout["quotient_relations"]):
        relation[row, item["direct_sum_base_index"]] = 1
        relation[row, item["direct_sum_parent_index"]] = -1
    assert relation.rank() == 8
    assert len(set(pushout["base_embedding"])) == 112
    assert len(set(pushout["parent_embedding"].values())) == 56
    pairing = sp.zeros(160)
    for left, right, value in payload["carrier"]["pairing_entries"]:
        scalar = value[0][1] if isinstance(value, list) else value
        pairing[left, right] = sp.sympify(scalar)
    assert pairing.rank() == 160
    unary = payload["complete_q1"]
    for key in (
        "q1_squared_defect_count",
        "odd_cyclicity_defect_count",
        "K_commutator_defect_count",
        "base_embedding_chain_defect_count",
        "parent_embedding_chain_defect_count",
        "quotient_well_defined_defect_count",
    ):
        assert unary[key] == 0
    assert payload["support_and_detector"]["detector_chain_defect_count"] == 0
    assert payload["support_and_detector"]["leading_response_rank"] == 2
    assert payload["support_and_detector"]["full_physical_reduction"] == "NO_CERTIFIED_MAP"
    print("BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
