#!/usr/bin/env python3
"""Method-distinct replay of the material-parent56 unary and readout map."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE.json"
X = P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE_PAYLOAD.json"
SCHEMA = P / "schema/berger-material-parent56-executable-unary-after-readout-interface-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    certificate = json.loads(C.read_text())
    payload = json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    assert sha(X) == certificate["payload_ref"]["sha256"]
    for reference in certificate["dependency_refs"].values():
        assert sha(ROOT / reference["path"]) == reference["sha256"]

    rows = payload["carrier"]["rows"]
    physical = [row["row_id"] for row in rows[:28]]
    s, omega = sp.symbols("s Omega_K")
    j2 = sp.Matrix([[0, -1], [1, 0]])
    d = s * sp.eye(2) + omega * j2
    hessian = sp.zeros(28)
    for block in payload["complete_internal_q1"]["blocks"]:
        x = [physical.index(name) for name in block["coordinate_rows"]]
        y = [physical.index(name) for name in block["momentum_rows"]]
        if len(x) == 2:
            for a in range(2):
                for b in range(2):
                    hessian[y[a], x[b]] = d[a, b]
                    hessian[x[a], y[b]] = -d[a, b]
        else:
            hessian[y[0], x[0]] = s
            hessian[x[0], y[0]] = -s
    reconstructed = [
        {"output": 28 + row, "input": column, "coefficient": sp.sstr(sp.factor(hessian[row, column]))}
        for row in range(28) for column in range(28) if hessian[row, column] != 0
    ]
    assert reconstructed == payload["complete_internal_q1"]["sparse_entries"]
    assert len(reconstructed) == 52
    q1 = sp.zeros(56)
    q1[28:56, 0:28] = hessian
    assert q1 * q1 == sp.zeros(56)
    assert hessian.T.applyfunc(lambda value: sp.expand(value.subs(s, -s))) == hessian
    assert payload["complete_internal_q1"]["pairing_rank"] == 56
    assert payload["detector_chain_map"]["rank"] == 2
    assert payload["detector_chain_map"]["internal_chain_defect_count"] == 0

    blocks = payload["external_mixed_readout_interface"]["blocks"]
    observed = [(block["detector"], tuple(block["action_variables"]), block["operator"], block["action_hessian_coefficient"]) for block in blocks]
    expected = [
        ("D0", ("memory_multiplier_0", "F_0_0"), "-delta_gHat(Btilde_0)", "-1"),
        ("D0", ("F_0_0", "memory_multiplier_0"), "+(delta_gHat(Btilde_0))^sharp", "-1"),
        ("D1", ("memory_multiplier_1", "F_1_1"), "-delta_gHat(Btilde_1)", "-1"),
        ("D1", ("F_1_1", "memory_multiplier_1"), "+(delta_gHat(Btilde_1))^sharp", "-1"),
    ]
    assert observed == expected
    assert all(block["internal_56_entry"] is False for block in blocks)
    assert payload["external_mixed_readout_interface"]["chain_and_support_audit"]["mixed_nilpotency_defect_count"] == 0
    assert payload["gate_disposition"]["combined_160_pushout"] == "NO_CERTIFIED_MAP"
    print("BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
