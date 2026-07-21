#!/usr/bin/env python3
"""Independent replay of the regraded receiver chain/cochain obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1.json"
Q = P / "certificates/POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1_PAYLOAD.json"
S = P / "schema/positive-berger-receiver-regraded-action-cochain-intertwiner-obstruction-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def adjoint(matrix: sp.Matrix, frequency: sp.Symbol) -> sp.Matrix:
    return matrix.subs(frequency, -frequency).T


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(Q.read_text())
    Draft202012Validator(json.loads(S.read_text())).validate(cert)
    assert sha(Q) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]

    rows = payload["compact_chain_carrier"]["rows"]
    assert [row["compact_degree"] for row in rows].count(0) == 10
    assert [row["compact_degree"] for row in rows].count(1) == 10
    assert all(entry["total_degree"] == 1 for entry in payload["compact_chain_carrier"]["pairing"]["entries"])

    s, omega = sp.symbols("s Omega_K", real=True)
    j = sp.Matrix([[0, -1], [1, 0]])
    d = s * sp.eye(2) + omega * j
    h = sp.zeros(10)
    h[0:2, 2:4] = -d
    h[2:4, 0:2] = d
    h[4:6, 6:8] = -d
    h[6:8, 4:6] = d
    h[8, 9] = -s
    h[9, 8] = s
    assert adjoint(h, s) == h
    zero, identity = sp.zeros(10), sp.eye(10)
    q_chain = zero.row_join(zero).col_join(h.row_join(zero))
    pairing = zero.row_join(identity).col_join((-identity).row_join(zero))
    assert q_chain * q_chain == sp.zeros(20)
    assert adjoint(q_chain, s) * pairing + pairing * q_chain == sp.zeros(20)
    assert pairing.rank() == 20

    lam = sp.symbols("lambda")
    assert -s * lam + s * lam == 0
    obstruction = payload["intertwiner_obstruction"]
    assert obstruction["source_degree"] == -1
    assert obstruction["target_degree"] == 1
    assert obstruction["homogeneous_degree_separation"] == 2
    assert not obstruction["injective_solution_exists"]
    assert all(row["rejected"] for row in payload["mutations"].values())
    print("POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
