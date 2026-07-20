#!/usr/bin/env python3
"""Independent replay of the canonical 104-row cone-lift obstruction.

This verifier does not import the producer.  It parses the two sparse PBW
records directly, applies the one-dimensional rational Berger
representation, and checks the two explicit non-membership witnesses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1.json"
)
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_canonical_cone_lift_obstruction_v1/"
    "rational_trivial_representation_witness.json"
)
Q_PATH = (
    ROOT
    / "quantum-weyl/lorentzian/generated/"
    "berger_canonical_graph_q_cauchy_obstruction/"
    "rejected_candidate_q_Cauchy_104.json"
)
A_PATH = (
    ROOT
    / "quantum-weyl/lorentzian/generated/"
    "berger_a104_endpoint_completion/global_A104.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _constant_matrix(path: Path) -> sp.Matrix:
    record = _load(path)
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _digest(body) or record["shape"] != [104, 104]:
        raise AssertionError(f"operator record drifted: {path}")
    alpha_B, u, v = sp.symbols("alpha_B u v")
    result = sp.zeros(104)
    for row, column, terms in record["entries"]:
        for exponents, coefficient in terms:
            if sum(exponents) == 0:
                result[row, column] += sp.sympify(
                    coefficient,
                    locals={"alpha_B": alpha_B, "u": u, "v": v},
                ).subs({alpha_B: 2, u: 1, v: 3})
    return result


def _column(entries: list[list[int | str]]) -> sp.Matrix:
    result = sp.zeros(104, 1)
    for row, coefficient in entries:
        result[int(row), 0] = sp.Rational(str(coefficient))
    return result


def verify() -> dict[str, int]:
    certificate = _load(CERT)
    payload = _load(PAYLOAD)
    if (
        certificate["result_id"]
        != "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1"
        or certificate["rational_obstruction"]["payload"]["sha256"]
        != _sha(PAYLOAD)
    ):
        raise AssertionError("certificate/payload identity drifted")
    for key, path in (("q_Cauchy", Q_PATH), ("A104", A_PATH)):
        if certificate["pinned_inputs"][key]["sha256"] != _sha(path):
            raise AssertionError(f"{key} dependency hash drifted")
    q = _constant_matrix(Q_PATH)
    evolution = _constant_matrix(A_PATH)
    ranks = {
        "rank_q": int(q.rank()),
        "rank_row_stack_q_qA": int(q.col_join(q * evolution).rank()),
        "rank_column_stack_q_Aq": int(
            q.row_join(evolution * q).rank()
        ),
    }
    if ranks != {
        "rank_q": 34,
        "rank_row_stack_q_qA": 35,
        "rank_column_stack_q_Aq": 35,
    } or ranks != payload["ranks"]:
        raise AssertionError(f"rank replay drifted: {ranks}")
    right = payload["right_lift_Dq_equals_qA"]
    z = _column(right["witness_z"])
    if q * z != sp.zeros(104, 1):
        raise AssertionError("right witness left ker(q)")
    if q * evolution * z != _column(right["q_A_z"]):
        raise AssertionError("right cokernel witness drifted")
    left = payload["left_adjoint_lift_Aq_equals_qD"]
    ell = _column(left["witness_ell"])
    if ell.T * q != sp.zeros(1, 104):
        raise AssertionError("left witness left left-kernel(q)")
    expected_left = _column(left["ell_transpose_A_q"]).T
    if ell.T * evolution * q != expected_left:
        raise AssertionError("left cokernel witness drifted")
    flags = certificate["classification"]
    if (
        flags["canonical_doubled_cone_evolution_lift_exists"]
        or flags["free_adjoint_cone_orientation_exists"]
        or flags["all_104_row_completions_obstructed"]
        or flags["Hadamard_or_quantum_claim"]
    ):
        raise AssertionError("claim boundary was promoted")
    return ranks


if __name__ == "__main__":
    result = verify()
    print(
        "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1: "
        f"VERIFIED ({result})"
    )
