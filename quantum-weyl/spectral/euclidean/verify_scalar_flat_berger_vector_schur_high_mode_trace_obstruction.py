#!/usr/bin/env python3
"""Independent exact replay of the Berger first-insertion tail obstruction."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator, ValidationError


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_HIGH_MODE_TRACE_MAJORANT_OBSTRUCTION_V1.json"
SCHEMA = HERE / "schema/scalar-flat-berger-vector-schur-high-mode-trace-majorant-obstruction-v1.schema.json"
I = sp.I
T = sp.symbols("t", real=True)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _generators(twice_j: int) -> list[sp.Matrix]:
    dimension = twice_j + 1
    j = sp.Rational(twice_j, 2)
    weights = [sp.Rational(twice_j - 2 * row, 2) for row in range(dimension)]
    plus = sp.zeros(dimension)
    minus = sp.zeros(dimension)
    for col, m in enumerate(weights):
        if col > 0:
            plus[col - 1, col] = sp.sqrt((j - m) * (j + m + 1))
        if col + 1 < dimension:
            minus[col + 1, col] = sp.sqrt((j + m) * (j - m + 1))
    return [(plus + minus) / 2, (plus - minus) / (2 * I), sp.diag(*weights)]


def _connection() -> list[sp.Matrix]:
    rows = [sp.zeros(4) for _ in range(4)]
    rows[1][2, 3], rows[1][3, 2] = -1, 1
    rows[2][1, 3], rows[2][3, 1] = 1, -1
    rows[3][1, 2], rows[3][2, 1] = sp.Rational(1, 2), sp.Rational(-1, 2)
    return rows


@lru_cache(maxsize=None)
def _direct_first_insertion(twice_j: int) -> sp.Matrix:
    angular = _generators(twice_j)
    dim = twice_j + 1
    identity = sp.eye(dim)
    derivatives = [sp.zeros(dim), -I * angular[0], -I * angular[1], -I * angular[2] / 2]
    covariant = [
        sp.kronecker_product(sp.eye(4), derivatives[a])
        + sp.kronecker_product(_connection()[a], identity)
        for a in range(4)
    ]
    ricci = sp.kronecker_product(sp.diag(0, -1, -1, 2), identity)
    f_block = -sum((entry * entry for entry in covariant), sp.zeros(4 * dim)) + ricci
    a_block = f_block - 2 * T * ricci
    gradient = sp.Matrix.vstack(*derivatives)
    delta = gradient.H
    schur = sp.Rational(2, 3) * identity + sp.Rational(1, 3) * delta * a_block.inv() * gradient
    return sp.simplify(schur.diff(T).subs(T, 0))


@lru_cache(maxsize=None)
def _formula_first_insertion(twice_j: int) -> sp.Matrix:
    j = sp.Rational(twice_j, 2)
    values = []
    for row in range(twice_j + 1):
        m = sp.Rational(twice_j - 2 * row, 2)
        q = j * (j + 1) - sp.Rational(3, 4) * m * m
        p = 2 * j * (j + 1) - 3 * m * m
        values.append(sp.factor(-p / (3 * q * q)))
    return sp.diag(*values)


def _shell_witness(twice_j: int) -> tuple[int, sp.Rational]:
    j = sp.Rational(twice_j, 2)
    contribution = sp.Rational(0)
    count = 0
    for row in range(twice_j + 1):
        m = sp.Rational(twice_j - 2 * row, 2)
        if abs(m) <= j / 2:
            count += 1
            contribution += abs(_formula_first_insertion(twice_j)[row, row])
    return count, sp.factor((twice_j + 1) * contribution)


def verify(certificate: dict | None = None) -> None:
    if certificate is None:
        certificate = json.loads(CERTIFICATE.read_text())
    try:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(certificate)
    except ValidationError as exc:
        raise ValueError("high-mode obstruction schema rejected payload") from exc

    for reference in certificate["dependencies"].values():
        path = HERE.parents[2] / reference["path"]
        assert _sha256(path) == reference["sha256"]

    assert certificate["first_insertion"]["first_insertion_eigenvalue"] == "b1_jm=-p_jm/(3*q_jm^2)"
    for twice_j in (1, 2, 3, 4):
        assert sp.simplify(_direct_first_insertion(twice_j) - _formula_first_insertion(twice_j)) == sp.zeros(twice_j + 1)

    # Independent formal inequality decomposition.  For j>=1 and |m|<=j/2,
    # p-5j^2/4 and 2j^2-q are sums of declared nonnegative terms.
    j, m = sp.symbols("j m", real=True)
    q = j * (j + 1) - sp.Rational(3, 4) * m * m
    p = 2 * j * (j + 1) - 3 * m * m
    assert sp.expand(p - sp.Rational(5, 4) * j * j) == sp.expand(2 * j + 3 * (j * j / 4 - m * m))
    assert sp.expand(2 * j * j - q) == sp.expand(j * (j - 1) + sp.Rational(3, 4) * m * m)
    assert sp.expand(q - (j * j / 4 + j)) == sp.expand(sp.Rational(3, 4) * (j * j - m * m))

    # If N=2j, the central weights correspond to integer indices
    # ceil(N/4) <= r <= floor(3N/4).  These four exact residue formulas
    # prove the count is at least N/4 for every integer N>=2.
    k = sp.symbols("k", integer=True, nonnegative=True)
    residue_counts = {
        0: 2 * k + 1,
        1: 2 * k,
        2: 2 * k + 1,
        3: 2 * k + 2,
    }
    residue_thresholds = {
        residue: (4 * k + residue) / sp.Integer(4) for residue in range(4)
    }
    assert sp.expand(residue_counts[0] - residue_thresholds[0]) == k + 1
    # N=4k+1 enters the theorem first at N=5, hence k>=1.
    assert sp.expand(residue_counts[1] - residue_thresholds[1]) == k - sp.Rational(1, 4)
    assert sp.expand(residue_counts[2] - residue_thresholds[2]) == k + sp.Rational(1, 2)
    assert sp.expand(residue_counts[3] - residue_thresholds[3]) == k + sp.Rational(5, 4)
    assert certificate["exact_lower_bound_proof"]["uniform_shell_lower_bound"].endswith(">=5/48")

    witnesses = certificate["exact_shell_witnesses"]
    assert [row["twice_j"] for row in witnesses] == list(range(2, 17))
    for row in witnesses:
        count, contribution = _shell_witness(row["twice_j"])
        assert row["central_weight_count"] == count
        assert sp.sympify(row["absolute_shell_contribution"]) == contribution
        assert sp.sympify(row["minus_uniform_lower_bound"]) == contribution - sp.Rational(5, 48)
        assert contribution >= sp.Rational(5, 48)

    flags = certificate["claim_flags"]
    assert flags["FIRST_INSERTION_SUMMABLE_MAJORANT_OBSTRUCTED"] is True
    assert flags["COMPLETE_HIGH_MODE_COERCIVITY_PREFLIGHT_COMPUTED"] is False
    assert flags["GLOBAL_DETERMINANT_OR_FINITE_TRACE_COMPUTED"] is False
    assert flags["ANOMALY_COEFFICIENT_OR_QME_COMPUTED"] is False
    assert flags["LORENTZIAN_OR_HADAMARD_PROMOTED"] is False
    print("Scalar-flat Berger vector Schur high-mode trace obstruction: PASS")


if __name__ == "__main__":
    verify()
