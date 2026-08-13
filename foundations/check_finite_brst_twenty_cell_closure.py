#!/usr/bin/env python3
"""Independently rederive the finite rational BRST twenty-cell witness."""
from __future__ import annotations

from fractions import Fraction as Qn
import hashlib
import json
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "foundations/results/FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1.json"
Matrix = list[list[Qn]]
Vector = list[Qn]


def zeros(rows: int, cols: int) -> Matrix:
    return [[Qn(0) for _ in range(cols)] for _ in range(rows)]


def eye(n: int) -> Matrix:
    return [[Qn(i == j) for j in range(n)] for i in range(n)]


def mmul(a: Matrix, b: Matrix) -> Matrix:
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Qn(0)) for j in range(len(b[0]))] for i in range(len(a))]


def madd(a: Matrix, b: Matrix) -> Matrix:
    return [[x + y for x, y in zip(rx, ry)] for rx, ry in zip(a, b)]


def msub(a: Matrix, b: Matrix) -> Matrix:
    return [[x - y for x, y in zip(rx, ry)] for rx, ry in zip(a, b)]


def transpose(a: Matrix) -> Matrix:
    return [list(row) for row in zip(*a)]


def matvec(a: Matrix, v: Vector) -> Vector:
    return [sum((x * y for x, y in zip(row, v)), Qn(0)) for row in a]


def rank(a: Matrix) -> int:
    work = [row[:] for row in a]
    rows, cols, pivot_row = len(work), len(work[0]) if work else 0, 0
    for col in range(cols):
        pivot = next((r for r in range(pivot_row, rows) if work[r][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][col]
        work[pivot_row] = [x / scale for x in work[pivot_row]]
        for row in range(rows):
            if row != pivot_row and work[row][col]:
                factor = work[row][col]
                work[row] = [x - factor * y for x, y in zip(work[row], work[pivot_row])]
        pivot_row += 1
    return pivot_row


def vector(**entries: int) -> Vector:
    names = ["u", "b", "h", "k", "a", "r"]
    return [Qn(entries.get(name, 0)) for name in names]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_payload(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def expected_coordinates() -> list[tuple[str, str, str]]:
    out = []
    for foundation in ("CLASSICAL_STANDARD", "CONSTRUCTIVE_COMPUTABLE", "WEAK_CHOICE_ZF"):
        for obligation in ("ANOMALY_CLASSIFICATION", "COUNTERTERM_CLASSIFICATION", "QME_RESTORATION", "RENORMALIZED_PRODUCTS", "RESIDUAL_QUANTUM_TRANSFER"):
            out.append((foundation, "HILBERT_OPERATOR", obligation))
    for obligation in ("ANOMALY_CLASSIFICATION", "QME_RESTORATION", "RESIDUAL_QUANTUM_TRANSFER"):
        out.append(("FINITE_DISCRETE", "HILBERT_OPERATOR", obligation))
    for foundation in ("CLASSICAL_STANDARD", "WEAK_CHOICE_ZF"):
        out.append((foundation, "KREIN_INDEFINITE", "QME_RESTORATION"))
    return out


def check() -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    n = 6
    q = zeros(n, n)
    q[1][0] = 1  # Q(u)=b
    q[4][2] = 1  # Q(h)=a
    if mmul(q, q) != zeros(n, n):
        errors.append("nilpotency")

    # Degree-restricted ranks and explicit representatives.
    q_minus1 = [[q[row][0]] for row in (1, 2, 3)]
    q_zero = [[q[row][col] for col in (1, 2, 3)] for row in (4, 5)]
    h_minus1 = 1 - rank(q_minus1)
    h_zero = (3 - rank(q_zero)) - rank(q_minus1)
    h_one = 2 - rank(q_zero)
    if (h_minus1, h_zero, h_one) != (0, 1, 1):
        errors.append("cohomology dimensions")
    if matvec(q, vector(k=1)) != vector() or matvec(q, vector(r=1)) != vector():
        errors.append("cohomology representatives")
    if matvec(q, vector(u=1)) != vector(b=1) or matvec(q, vector(h=1)) != vector(a=1):
        errors.append("exact directions")

    projection = zeros(n, n)
    projection[3][3] = projection[5][5] = 1
    homotopy = zeros(n, n)
    homotopy[0][1] = 1  # H(b)=u
    homotopy[2][4] = 1  # H(a)=h
    if mmul(projection, projection) != projection:
        errors.append("pi_cl iota_cl")
    if msub(eye(n), projection) != madd(mmul(q, homotopy), mmul(homotopy, q)):
        errors.append("contraction identity")
    if mmul(homotopy, homotopy) != zeros(n, n) or mmul(homotopy, projection) != zeros(n, n) or mmul(projection, homotopy) != zeros(n, n):
        errors.append("contraction side conditions")

    bare = vector(b=1, h=1, k=1)
    counterterm = vector(h=-1)
    renormalized = [x + y for x, y in zip(bare, counterterm)]
    if matvec(q, bare) != vector(a=1) or matvec(q, counterterm) != vector(a=-1) or matvec(q, renormalized) != vector():
        errors.append("one-loop restoration")
    transferred = matvec(projection, renormalized)
    if transferred != vector(k=1) or [x - y for x, y in zip(renormalized, transferred)] != matvec(q, vector(u=1)):
        errors.append("post-restoration transfer")

    j = zeros(n, n)
    j[0][1] = j[1][0] = 1
    j[2][4] = j[4][2] = 1
    j[3][3] = 1
    j[5][5] = -1
    q_sharp = mmul(mmul(j, transpose(q)), j)
    if mmul(j, j) != eye(n) or transpose(j) != j or q_sharp != q:
        errors.append("Krein adjoint")

    units: list[tuple[tuple[int, int], Matrix]] = []
    for i in range(n):
        for jcol in range(n):
            unit = zeros(n, n)
            unit[i][jcol] = 1
            units.append(((i, jcol), unit))
    product_count = 0
    for (i, jcol), left in units:
        for (k, ell), right in units:
            expected = zeros(n, n)
            if jcol == k:
                expected[i][ell] = 1
            if mmul(left, right) != expected:
                errors.append("matrix-unit products")
                break
            product_count += 1

    coordinates = expected_coordinates()
    if len(coordinates) != 20 or len(set(coordinates)) != 20:
        errors.append("twenty coordinates")
    payload = {
        "source_hash": sha(SOURCE),
        "coordinates": [list(item) for item in coordinates],
        "complex_dimension": n,
        "q_rank": rank(q),
        "q_squared_zero": True,
        "cohomology_dimensions": {"H^-1": h_minus1, "H^0": h_zero, "H^1": h_one},
        "counterterm_basis": ["[k]"],
        "anomaly_basis": ["[r]"],
        "removable_breaking": "a=Q(h)",
        "qme_restored": True,
        "transferred_class": "[k]",
        "contraction_identities": 5,
        "krein_q_sharp_equals_q": True,
        "matrix_units": len(units),
        "products_checked": product_count,
        "status_split": {"LOCAL_RESULT": 17, "PIECES_ONLY": 3},
    }
    return errors, {**payload, "digest": digest_payload(payload)}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
