#!/usr/bin/env python3
"""Independent replay of the rational mixed-evolution endpoint obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import fmpq, fmpq_mat
import sympy as sp
from sympy.polys.domains import QQ
from sympy.polys.matrices import DomainMatrix
from sympy.polys.matrices.sdm import SDM


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_MIXED_EVOLUTION_CORRECTION_ENDPOINT_OBSTRUCTION_V1.json"
)
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_mixed_evolution_endpoint_obstruction_v1/"
    "rational_endpoint_witness.json"
)
Q_PATH = (
    ROOT
    / "quantum-weyl/lorentzian/generated/"
    "berger_canonical_graph_q_cauchy_obstruction/rejected_candidate_q_Cauchy_104.json"
)
A_PATH = (
    ROOT
    / "quantum-weyl/lorentzian/generated/"
    "berger_a104_endpoint_completion/global_A104.json"
)
DEGREES = tuple([-1] * 6 + [0] * 20 + [1] * 20 + [2] * 6) * 2


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def constant_matrix(path: Path) -> sp.Matrix:
    record = load(path)
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != digest(body):
        raise AssertionError(f"internal operator hash drifted: {path}")
    alpha_B, u, v = sp.symbols("alpha_B u v")
    substitutions = {alpha_B: 2, u: 1, v: 3}
    matrix = sp.zeros(*record["shape"])
    for row, column, terms in record["entries"]:
        for exponents, coefficient in terms:
            if sum(exponents):
                continue
            matrix[row, column] += sp.sympify(
                coefficient,
                locals={"alpha_B": alpha_B, "u": u, "v": v},
            ).subs(substitutions)
    return matrix


def rational_matrix(record: dict) -> sp.Matrix:
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != digest(body):
        raise AssertionError("serialized witness matrix hash drifted")
    matrix = sp.zeros(*record["shape"])
    for row, column, numerator, denominator in record["entries"]:
        matrix[row, column] = sp.Rational(numerator, denominator)
    return matrix


def flint_matrix(matrix: sp.Matrix) -> fmpq_mat:
    return fmpq_mat(
        [
            [
                fmpq(
                    int(sp.Rational(matrix[row, column]).p),
                    int(sp.Rational(matrix[row, column]).q),
                )
                for column in range(matrix.cols)
            ]
            for row in range(matrix.rows)
        ]
    )


def full_block(old_q: sp.Matrix, correction: sp.Matrix) -> sp.Matrix:
    return sp.Matrix.vstack(
        sp.Matrix.hstack(old_q, -old_q + correction),
        sp.Matrix.hstack(old_q - correction, -old_q + 2 * correction),
    )


def main() -> int:
    certificate = load(CERTIFICATE)
    payload = load(PAYLOAD)
    if payload["sha256"] != digest({key: value for key, value in payload.items() if key != "sha256"}):
        raise SystemExit("payload top-level hash drifted")
    q104 = constant_matrix(Q_PATH)
    a104 = constant_matrix(A_PATH)
    indices = {
        degree: [index for index, value in enumerate(DEGREES) if value == degree]
        for degree in (-1, 0)
    }
    old_q = q104.extract(indices[0], indices[-1])
    source = a104.extract(indices[-1], indices[-1])
    target = a104.extract(indices[0], indices[0])
    system = sp.kronecker_product(sp.eye(12), target) - sp.kronecker_product(
        source.T, sp.eye(40)
    )
    sparse = {}
    for (row, column), value in sp.SparseMatrix(system).todok().items():
        value = sp.Rational(value)
        sparse.setdefault(row, {})[column] = QQ(int(value.p), int(value.q))
    hom = DomainMatrix.from_rep(SDM(sparse, system.shape, QQ)).nullspace()
    if hom.shape[0] != 20:
        raise SystemExit(f"independent Hom_A dimension mismatch: {hom.shape[0]}")
    kernel = source.nullspace()
    if len(kernel) != 1 or old_q * kernel[0] != sp.zeros(40, 1):
        raise SystemExit("independent invariant-line replay failed")
    rank12 = rational_matrix(payload["rank_12_witness"])
    rank11 = rational_matrix(payload["rank_11_witness"])
    checks = {
        "rank12_intertwines": target * rank12 == rank12 * source,
        "rank11_intertwines": target * rank11 == rank11 * source,
        "rank12_is_12": flint_matrix(rank12).rank() == 12,
        "rank11_is_11": flint_matrix(rank11).rank() == 11,
        "rank12_total_is_24": flint_matrix(full_block(old_q, rank12)).rank() == 24,
        "rank11_total_is_22": flint_matrix(full_block(old_q, rank11)).rank() == 22,
        "rank11_kills_unique_line": rank11 * kernel[0] == sp.zeros(40, 1),
        "required_rank_is_23": certificate["exact_obstruction"]["required_left_endpoint_rank"] == 23,
        "general_no_go_not_claimed": not certificate["classification"]["all_rational_104_row_completions_obstructed"],
    }
    if not all(checks.values()):
        raise SystemExit(f"independent replay failed: {checks}")
    if certificate["pinned_inputs"]["q_Cauchy"]["sha256"] != hashlib.sha256(Q_PATH.read_bytes()).hexdigest():
        raise SystemExit("q input hash drifted")
    if certificate["pinned_inputs"]["A104"]["sha256"] != hashlib.sha256(A_PATH.read_bytes()).hexdigest():
        raise SystemExit("A input hash drifted")
    print(
        "BERGER_Q26_104_ROW_MIXED_EVOLUTION_CORRECTION_ENDPOINT_OBSTRUCTION_V1 independent replay: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
