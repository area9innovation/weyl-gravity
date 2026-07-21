#!/usr/bin/env python3
"""Independent grading audit for the receiver/q70 integration obstruction."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1.json"
Q = P / "certificates/POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1_PAYLOAD.json"
S = P / "schema/positive-berger-receiver-bv-cocycle-integration-grading-obstruction-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, result = json.loads(C.read_text()), json.loads(Q.read_text())
    Draft202012Validator(json.loads(S.read_text())).validate(cert)
    assert sha(Q) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]

    app = json.loads((ROOT / cert["dependency_refs"]["receiver_payload"]["path"]).read_text())
    parent = json.loads((ROOT / cert["dependency_refs"]["q70_payload"]["path"]).read_text())
    app_rows = app["carrier"]["physical_fields"] + app["carrier"]["antifields_and_bv_duals"]
    app_degree = {row["name"]: row["bv_degree"] for row in app_rows}
    parent_rows = parent["row_layout"]["component_rows"]
    parent_degree = {row["index"]: row["degree"] for row in parent_rows}

    assert Counter(app_degree.values()) == Counter({-1: 10, 0: 10})
    assert Counter(parent_degree.values()) == Counter({-1: 6, 0: 29, 1: 29, 2: 6})
    app_sums = {
        app_degree[entry["left"]] + app_degree[entry["right"]]
        for entry in app["odd_pairing"]["entries"]
    }
    parent_sums = {
        parent_degree[entry[0]] + parent_degree[entry[1]]
        for entry in parent["operators"]["pairing70"]["entries"]
    }
    assert app_sums == {-1}
    assert parent_sums == {1}
    assert len([d for d in app_degree.values() if d == -1]) > len(
        [d for d in parent_degree.values() if d == -1]
    )

    audit = result["grading_audit"]
    assert audit["degree_minus_one_injection_deficiency"] == 4
    assert audit["pairing_degree_difference"] == 2
    assert result["canonical_witness"]["receiver_pair_total_degree"] == -1
    assert result["canonical_witness"]["q70_pair_total_degree"] == 1
    assert all(row["rejected"] for row in result["mutations"].values())
    assert result["pushout_disposition"]["homogeneous_graded_odd_symplectic_pushout"] == "OBSTRUCTED"
    assert result["pushout_disposition"]["mixed_gravity_clock_apparatus_unary_rows"] == "NOT_REACHED"
    print("POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
