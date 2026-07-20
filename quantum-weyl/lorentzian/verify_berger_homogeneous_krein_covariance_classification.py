#!/usr/bin/env python3
"""Independent exact replay of the homogeneous Berger covariance theorem.

This verifier intentionally does not import the producer.  It reloads the
committed coefficient artifacts, derives the graph Lagrange form, and builds
the full symmetric Lyapunov matrix independently.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import sympy as sp
from sympy.polys.matrices import DomainMatrix

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = (
    HERE
    / "certificates/BERGER_HOMOGENEOUS_KREIN_COVARIANCE_CLASSIFICATION.json"
)
SCHEMA = (
    HERE
    / "schema/berger-homogeneous-krein-covariance-classification-v1.schema.json"
)
A104 = HERE / "generated/berger_a104_endpoint_completion/global_A104.json"
ACTION_DIR = HERE / "generated/berger_a104_cauchy_operator_preflight"
SOURCES = (
    "berger_homogeneous_krein_covariance_classification.py",
    "berger_homogeneous_krein_covariance_classification_certificate.py",
    "verify_berger_homogeneous_krein_covariance_classification.py",
    "schema/berger-homogeneous-krein-covariance-classification-v1.schema.json",
    "tests/test_berger_homogeneous_krein_covariance_classification.py",
    "../reports/berger-homogeneous-krein-covariance-classification.md",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _specialize(path: Path) -> sp.Matrix:
    record = _load(path)
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _canonical_hash(body):
        raise ValueError(f"action artifact hash failed: {path.name}")
    alpha, u, v = sp.symbols("alpha_B u v")
    matrix = sp.zeros(*record["shape"])
    for row, column, terms in record["entries"]:
        for exponents, coefficient in terms:
            if sum(exponents) == 0:
                matrix[row, column] += sp.sympify(
                    coefficient,
                    locals={"alpha_B": alpha, "u": u, "v": v},
                ).subs({alpha: 1, u: 1, v: 5})
    return matrix


def _a104_blocks() -> tuple[sp.Matrix, sp.Matrix]:
    record = _load(A104)
    body = {key: value for key, value in record.items() if key != "sha256"}
    if record["sha256"] != _canonical_hash(body):
        raise ValueError("A104 payload hash failed")
    alpha, u, v = sp.symbols("alpha_B u v")
    matrix = sp.zeros(104)
    for row, column, terms in record["entries"]:
        for exponents, coefficient in terms:
            if sum(exponents) == 0:
                matrix[row, column] += sp.sympify(
                    coefficient,
                    locals={"alpha_B": alpha, "u": u, "v": v},
                ).subs({alpha: 1, u: 1, v: 5})
    metric = tuple(range(6, 26)) + tuple(range(58, 78))
    antifield = tuple(range(26, 46)) + tuple(range(78, 98))
    return matrix.extract(metric, metric), matrix.extract(antifield, antifield)


def _lyapunov_nullity(A: sp.Matrix) -> tuple[int, int]:
    rank = A.rows
    pairs = [(row, column) for row in range(rank) for column in range(row, rank)]
    variables = {pair: index for index, pair in enumerate(pairs)}
    columns = [
        [(row, A[row, column]) for row in range(rank) if A[row, column]]
        for column in range(rank)
    ]
    entries: dict[tuple[int, int], sp.Expr] = {}
    for equation, (row, column) in enumerate(pairs):
        values: dict[int, sp.Expr] = {}
        for middle, coefficient in columns[row]:
            index = variables[tuple(sorted((middle, column)))]
            values[index] = values.get(index, 0) + coefficient
        for middle, coefficient in columns[column]:
            index = variables[tuple(sorted((row, middle)))]
            values[index] = values.get(index, 0) + coefficient
        for index, coefficient in values.items():
            if coefficient:
                entries[equation, index] = coefficient
    matrix = sp.MutableSparseMatrix(len(pairs), len(pairs), entries)
    exact_rank = DomainMatrix.from_Matrix(matrix, fmt="sparse").rank()
    return exact_rank, len(pairs) - exact_rank


def _poly_nullities(
    A: sp.Matrix, factor: sp.Expr, powers: int, variable: sp.Symbol
) -> list[int]:
    value = sp.zeros(A.rows)
    identity = sp.eye(A.rows)
    for coefficient in sp.Poly(factor, variable).all_coeffs():
        value = value * A + coefficient * identity
    power = sp.eye(A.rows)
    output = []
    for _ in range(powers):
        power = power * value
        output.append(A.rows - int(power.rank()))
    return output


def _verify_source_manifest(value: dict[str, Any]) -> None:
    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("covariance source manifest drifted")


def _verify_pinned_input(value: dict[str, Any]) -> None:
    reference = value["dependency_refs"]["stationary_obstruction"]
    prefix = subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()
    blob = subprocess.check_output(
        [
            "git",
            "show",
            f"{reference['commit']}:{prefix}{reference['path']}",
        ],
        cwd=ROOT,
    )
    source = json.loads(blob)
    if (
        hashlib.sha256(blob).hexdigest() != reference["sha256"]
        or source["result_id"] != reference["result_id"]
    ):
        raise ValueError("pinned stationary obstruction drifted")


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"homogeneous covariance schema failed: {errors}")
    _verify_source_manifest(value)
    _verify_pinned_input(value)

    metric_A, antifield_A = _a104_blocks()
    K0 = _specialize(ACTION_DIR / "metric_K0.json")
    K1 = _specialize(ACTION_DIR / "metric_K1.json")
    K2 = _specialize(ACTION_DIR / "metric_K2.json")
    K0s = _specialize(ACTION_DIR / "metric_antifield_K0.json")
    K1s = _specialize(ACTION_DIR / "metric_antifield_K1.json")
    K2s = _specialize(ACTION_DIR / "metric_antifield_K2.json")
    swap = sp.zeros(20)
    swap[:10, 10:] = sp.eye(10)
    swap[10:, :10] = sp.eye(10)
    if not (
        K2s == swap * K2.T * swap
        and K1s == -swap * K1.T * swap
        and K0s == swap * K0.T * swap
    ):
        raise ValueError("independent graph-adjoint relation failed")

    B = (swap * K1).row_join(swap * K2).col_join(
        (-swap * K2).row_join(sp.zeros(20))
    )
    A = sp.diag(metric_A, antifield_A)
    omega = sp.zeros(80)
    omega[:40, 40:] = -B.T
    omega[40:, :40] = B
    G = sp.zeros(80)
    G[:40, 40:] = B.T
    G[40:, :40] = B
    if (
        int(B.rank()) != 40
        or antifield_A.T * B + B * metric_A != sp.zeros(40)
        or omega.T != -omega
        or int(omega.rank()) != 80
        or G.T != G
        or int(G.rank()) != 80
        or A.T * omega + omega * A != sp.zeros(80)
        or A.T * G + G * A != sp.zeros(80)
    ):
        raise ValueError("independent action-form replay failed")

    hashes = value["action_pairing"]["matrix_hashes"]
    matrices = {"A80": A, "B40": B, "Omega80": omega, "G80": G}
    for name, matrix in matrices.items():
        digest = _canonical_hash(
            [[str(entry) for entry in row] for row in matrix.tolist()]
        )
        if hashes[name] != digest:
            raise ValueError(f"matrix mutation detected: {name}")
    involution = [["1" if row == column else "0" for column in range(80)]
                  for row in range(80)]
    if hashes["real_involution80"] != _canonical_hash(involution):
        raise ValueError("real-involution mutation detected")

    rank, nullity = _lyapunov_nullity(A)
    if (rank, nullity) != (3112, 128):
        raise ValueError("independent symmetric Lyapunov rank failed")
    lam = sp.symbols("lambda")
    instability = (
        9 * lam**12
        + 39 * lam**10
        - 116 * lam**8
        + 900 * lam**6
        - 3160 * lam**4
        - 300 * lam**2
        + 4800
    )
    primary_factors = (
        (lam, 3),
        (2 * lam**2 + 1, 2),
        (lam**2 + 35, 2),
        (2 * lam**2 + 41, 2),
        (lam**2 + 16, 4),
        (lam**4 + 187 * lam**2 + 8720, 2),
        (instability, 2),
    )
    if any(
        _poly_nullities(metric_A, factor, powers, lam)
        != _poly_nullities(antifield_A, factor, powers, lam)
        for factor, powers in primary_factors
    ):
        raise ValueError("metric/antifield primary Jordan mutation detected")
    ledger = value["homogeneous_spectral_classification"]["primary_ledger"]
    totals = value["homogeneous_spectral_classification"]["totals"]
    recomputed = {
        field: sum(row[field] for row in ledger)
        for field in (
            "combined_real_dimension",
            "invariant_symmetric_parameter_dimension",
            "positive_cone_linear_span_dimension",
            "positive_rank_capacity",
            "forced_positive_radical_dimension",
        )
    }
    if recomputed != totals or totals != {
        "combined_real_dimension": 80,
        "invariant_symmetric_parameter_dimension": 128,
        "positive_cone_linear_span_dimension": 95,
        "positive_rank_capacity": 54,
        "forced_positive_radical_dimension": 26,
    }:
        raise ValueError("primary covariance totals failed")

    x = sp.symbols("x")
    coefficients = value["homogeneous_spectral_classification"][
        "instability_root_ledger"
    ]["polynomial_coefficients_descending"]
    p = sp.Poly.from_list(coefficients, gens=x)
    expected = [
        (sp.Rational(-9), sp.Rational(-8)),
        (sp.Rational(-3, 2), sp.Rational(-1)),
        (sp.Rational(3, 2), sp.Rational(2)),
        (sp.Rational(5, 2), sp.Rational(3)),
    ]
    if (
        p.count_roots(-sp.oo, sp.oo) != 4
        or sp.gcd(p, p.diff()).degree() != 0
        or any(p.count_roots(left, right) != 1 for left, right in expected)
    ):
        raise ValueError("exact instability-root mutation detected")

    W = (G + sp.I * omega) / 2
    if (
        W.conjugate().T != W
        or W - W.T != sp.I * omega
        or A.T * W + W * A != sp.zeros(80)
        or int(W.rank()) != 80
    ):
        raise ValueError("canonical Krein covariance replay failed")

    flags = value["claim_flags"]
    if (
        not flags["HOMOGENEOUS_ACTION_COMMUTATOR_AND_KREIN_FORMS_DERIVED"]
        or not flags["HOMOGENEOUS_STATIONARY_COVARIANCE_AFFINE_CLASS_COMPLETE"]
        or flags["HOMOGENEOUS_STATIONARY_POSITIVE_CCR_COVARIANCE_EXISTS"]
        or not flags["HOMOGENEOUS_CANONICAL_KREIN_CCR_COVARIANCE_EXISTS"]
        or not flags["HOMOGENEOUS_NONSTATIONARY_POSITIVE_COVARIANCE_EXISTS"]
        or flags["FULL_104_ROW_CAUCHY_KREIN_FORM_IMPORTED"]
        or flags["CORRECTED_Q_CAUCHY_IMPORTED"]
        or flags["FULL_BV_HADAMARD_STATE"]
        or flags["PHYSICAL_POSITIVITY_CERTIFIED"]
        or flags["LORENTZIAN_QME_CERTIFIED"]
        or flags["QUANTUM_THEORY_CERTIFIED"]
    ):
        raise ValueError("claim boundary mutation detected")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    return value


if __name__ == "__main__":
    verify()
    print("BERGER homogeneous Krein covariance independent replay: PASS")
