#!/usr/bin/env python3
"""Independent payload replay for the rational non-cone feasibility witness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_FEASIBILITY_V1.json"
)
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_noncone_rational_nilpotence_feasibility_v1/"
    "rational_noncone_differential.json"
)
Q104 = (
    ROOT
    / "quantum-weyl/lorentzian/generated/"
    "berger_canonical_graph_q_cauchy_obstruction/"
    "rejected_candidate_q_Cauchy_104.json"
)
DEGREES = tuple(
    [-1] * 6 + [0] * 20 + [1] * 20 + [2] * 6
) * 2
PRIME = 1013


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _matrix(record: dict) -> sp.Matrix:
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _digest(body):
        raise AssertionError("matrix internal hash drifted")
    result = sp.zeros(*record["shape"])
    for row, column, numerator, denominator in record["entries"]:
        result[row, column] = sp.Rational(numerator, denominator)
    return result


def _rank_mod(matrix: sp.Matrix) -> int:
    value = np.asarray(
        [
            [
                int(sp.Rational(entry).p)
                * pow(int(sp.Rational(entry).q), -1, PRIME)
                % PRIME
                for entry in row
            ]
            for row in matrix.tolist()
        ],
        dtype=np.int64,
    )
    rank = 0
    for column in range(value.shape[1]):
        candidates = np.flatnonzero(value[rank:, column])
        if not len(candidates):
            continue
        selected = rank + int(candidates[0])
        value[[rank, selected]] = value[[selected, rank]]
        value[rank] = (
            value[rank] * pow(int(value[rank, column]), -1, PRIME)
        ) % PRIME
        for row in range(rank + 1, value.shape[0]):
            if value[row, column]:
                value[row] = (
                    value[row] - value[row, column] * value[rank]
                ) % PRIME
        rank += 1
        if rank == value.shape[0]:
            break
    return rank


def _constant_q() -> sp.Matrix:
    record = json.loads(Q104.read_text())
    result = sp.zeros(104)
    alpha_B, u, v = sp.symbols("alpha_B u v")
    substitutions = {alpha_B: 2, u: 1, v: 3}
    for row, column, terms in record["entries"]:
        for exponents, coefficient in terms:
            if not any(exponents):
                result[row, column] += sp.sympify(
                    coefficient,
                    locals={"alpha_B": alpha_B, "u": u, "v": v},
                ).subs(substitutions)
    return result


def verify() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    body = {key: value for key, value in payload.items() if key != "sha256"}
    if payload["sha256"] != _digest(body):
        raise AssertionError("payload internal hash drifted")
    if (
        certificate["result_id"]
        != "BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_FEASIBILITY_V1"
    ):
        raise AssertionError("certificate identity drifted")
    exact = certificate["exact_witness"]
    if _sha(ROOT / exact["path"]) != exact["sha256"]:
        raise AssertionError("payload content hash drifted")
    q = _constant_q()
    indices = {
        degree: [
            index
            for index, value in enumerate(DEGREES)
            if value == degree
        ]
        for degree in (-1, 0, 1, 2)
    }
    old = [
        q.extract(indices[0], indices[-1]),
        q.extract(indices[1], indices[0]),
        q.extract(indices[2], indices[1]),
    ]
    records = payload["matrices"]
    matrices = [
        _matrix(records["degree_minus1_to_0"]),
        _matrix(records["degree_0_to_plus1"]),
        _matrix(records["degree_plus1_to_plus2"]),
    ]
    if (
        matrices[0][:40, :12] != old[0]
        or matrices[1][:40, :40] != old[1]
        or matrices[2][:12, :40] != old[2]
    ):
        raise AssertionError("old-old block incidence drifted")
    if (
        matrices[1] * matrices[0] != sp.zeros(80, 24)
        or matrices[2] * matrices[1] != sp.zeros(24, 80)
    ):
        raise AssertionError("nilpotence drifted")
    ranks = [_rank_mod(matrix) for matrix in matrices]
    if ranks != [23, 56, 23]:
        raise AssertionError(f"independent rank replay drifted: {ranks}")
    homology = [
        24 - ranks[0],
        80 - ranks[0] - ranks[1],
        80 - ranks[1] - ranks[2],
        24 - ranks[2],
    ]
    if homology != [1, 1, 1, 1]:
        raise AssertionError("independent cohomology replay drifted")
    flags = certificate["classification"]
    if (
        flags["nilpotence_rank_only_global_104_row_obstruction"]
        or flags["rational_PBW_operator_completion_constructed"]
        or flags["A104_evolution_lift_constructed"]
    ):
        raise AssertionError("claim boundary drifted")
    print(
        "BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_"
        "FEASIBILITY_V1: PASS prime=1013 ranks=[23,56,23]"
    )


if __name__ == "__main__":
    verify()
