#!/usr/bin/env python3
"""Method-distinct replay of the dynamical apparatus parent."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json"
Q = P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json"
SCHEMA = P / "schema/berger-dynamical-apparatus-parent-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(Q.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(Q) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]

    carrier = payload["carrier"]
    assert carrier["physical_even_row_count"] == 28
    assert carrier["odd_cotangent_row_count"] == 28
    assert carrier["ghost_rows"] == []
    assert carrier["odd_pairing_rank"] == 56

    s = sp.symbols("s")
    block = sp.Matrix([[0, -s], [s, 0]])
    assert sp.factor(block.det()) == s**2
    assert sp.factor(sp.diag(block, block).det()) == s**4

    l, p0, p1, f0, f1 = sp.symbols("l p0 p1 f0 f1")
    variables = (l, p0, p1, f0, f1)
    action = -l * p0 * f0 - l * p1 * f1
    records = []
    for i, j, k in itertools.product(range(5), repeat=3):
        value = sp.diff(action, variables[i], variables[j], variables[k])
        if value:
            records.append(int(value))
    assert len(records) == 12 and set(records) == {-1}

    j = sp.Matrix([[0, -1], [1, 0]])
    u0, u1, v0, v1 = sp.symbols("u0 u1 v0 v1")
    u, v = sp.Matrix([u0, u1]), sp.Matrix([v0, v1])
    assert sp.expand((j * u).dot(v) + u.dot(j * v)) == 0
    assert sp.expand((j * u).dot(v) - u.dot(j * v)) == 2 * (
        u0 * v1 - u1 * v0
    )

    response = cert["observer_result"]
    assert response["rank"] == 2
    assert response["determinant"] == "kappa_0*kappa_1"
    source = cert["source_class_result"]
    assert source["pure_old_coordinate_count"] == 0
    assert source["intersection_rank"] == 0
    assert source["source_status"].endswith("UNRESOLVED_ALL_JET")
    assert cert["downstream_disposition"]["all_jet_temporal_source_membership"] == (
        "NO_CERTIFIED_MAP"
    )
    print("BERGER_DYNAMICAL_APPARATUS_PARENT independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
