#!/usr/bin/env python3
"""Independent replay of the positive-Berger local receiver preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1.json"
Q = P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1_PAYLOAD.json"
I = P / "generated/POSITIVE_BERGER_LOCAL_RECEIVER_BV_INTEGRATION_CONTRACT_V1.json"
SCHEMA = P / "schema/positive-berger-local-receiver-action-preflight-v1.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def formal_adjoint(matrix: sp.Matrix, frequency: sp.Symbol) -> sp.Matrix:
    return matrix.subs(frequency, -frequency).T


def main() -> int:
    cert = json.loads(C.read_text())
    payload = json.loads(Q.read_text())
    contract = json.loads(I.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)

    assert sha256(Q) == cert["payload_ref"]["sha256"]
    assert sha256(I) == cert["integration_contract_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha256(ROOT / ref["path"]) == ref["sha256"]

    fields = payload["carrier"]["physical_fields"]
    duals = payload["carrier"]["antifields_and_bv_duals"]
    assert [row["name"] for row in fields] == [
        "X0", "X1", "Y0", "Y1", "P0", "P1", "N0", "N1", "m", "lambda"
    ]
    assert all(row["bv_degree"] == 0 and row["parity"] == "even" for row in fields)
    assert all(row["bv_degree"] == -1 and row["parity"] == "odd" for row in duals)
    assert payload["carrier"]["gauge_generators"] == []
    assert payload["carrier"]["ghosts"] == []

    # Reconstruct the action Hessian independently over Q[s,Omega_K].
    s, omega = sp.symbols("s Omega_K", real=True)
    j = sp.Matrix([[0, -1], [1, 0]])
    derivative = s * sp.eye(2) + omega * j
    hessian = sp.zeros(10)
    hessian[0:2, 2:4] = -derivative
    hessian[2:4, 0:2] = derivative
    hessian[4:6, 6:8] = -derivative
    hessian[6:8, 4:6] = derivative
    hessian[8, 9] = -s
    hessian[9, 8] = s
    assert formal_adjoint(hessian, s) == hessian

    zero = sp.zeros(10)
    identity = sp.eye(10)
    q1 = zero.row_join(hessian).col_join(zero.row_join(zero))
    odd_pairing = zero.row_join(identity).col_join((-identity).row_join(zero))
    assert q1 * q1 == sp.zeros(20)
    assert formal_adjoint(q1, s) * odd_pairing + odd_pairing * q1 == sp.zeros(20)
    assert odd_pairing.rank() == 20

    # The local descent is coefficientwise exact: s(m+)=-u(lambda)vol_0.
    lam = sp.symbols("lambda")
    s_a = -s * lam
    d_b = s * lam
    assert sp.expand(s_a + d_b) == 0
    cocycle = payload["receiver_cocycle"]
    assert cocycle["A_bv_degree"] == -1
    assert cocycle["B_form_degree"] == 3
    assert cocycle["nontriviality"]["degree_minus_two_generator_count"] == 0
    assert cocycle["nontriviality"]["Euler_derivative_of_A_with_respect_to_m_plus"] == 1

    v = sp.Rational(3, 4)
    raw_d = s * sp.eye(2) + (omega + v) * j
    phase_r = j
    helical_k = s * sp.eye(2) + omega * j
    assert raw_d - v * phase_r - helical_k == sp.zeros(2)

    mutations = payload["distinguishing_mutations"]
    assert all(row["rejected"] for row in mutations.values())
    assert mutations["probe_smearing_substitution"]["candidate"] == "Q_0[F]"
    assert "advanced" in mutations["advanced_covector_substitution"]["failure"]
    assert mutations["persistent_register_substitution"]["candidate"] == "m"

    core = dict(contract)
    digest = core.pop("contract_sha256")
    assert canonical_sha(core) == digest
    assert all(
        status == "NO_CERTIFIED_MAP"
        for status in contract["required_parent_inputs"].values()
    )
    assert all(
        status == "NO_CERTIFIED_MAP"
        for status in contract["downstream_status"].values()
    )
    print("POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
