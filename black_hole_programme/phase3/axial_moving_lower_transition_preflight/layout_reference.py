"""Exact layout and moving-frame oracle for the axial preflight.

This module is intentionally independent of the Forge implementation.  Its
primary purpose is to make the standard-interleaved versus contiguous-block
layout boundary executable and mutation-sensitive.
"""
from __future__ import annotations

from fractions import Fraction as F
from typing import Iterable


Matrix = tuple[tuple[F, ...], ...]


class LayoutError(ValueError):
    pass


def matrix(rows: Iterable[Iterable[int | F]]) -> Matrix:
    out = tuple(tuple(F(x) for x in row) for row in rows)
    if not out or not out[0] or any(len(row) != len(out[0]) for row in out):
        raise LayoutError("ragged or empty matrix")
    return out


def zeros(rows: int, cols: int) -> Matrix:
    return tuple(tuple(F(0) for _ in range(cols)) for _ in range(rows))


def identity(n: int) -> Matrix:
    return tuple(
        tuple(F(i == j) for j in range(n))
        for i in range(n)
    )


def shape(a: Matrix) -> tuple[int, int]:
    return len(a), len(a[0])


def add(a: Matrix, b: Matrix) -> Matrix:
    if shape(a) != shape(b):
        raise LayoutError("add shape mismatch")
    return tuple(
        tuple(x + y for x, y in zip(ar, br, strict=True))
        for ar, br in zip(a, b, strict=True)
    )


def sub(a: Matrix, b: Matrix) -> Matrix:
    if shape(a) != shape(b):
        raise LayoutError("sub shape mismatch")
    return tuple(
        tuple(x - y for x, y in zip(ar, br, strict=True))
        for ar, br in zip(a, b, strict=True)
    )


def mul(a: Matrix, b: Matrix) -> Matrix:
    ar, ac = shape(a)
    br, bc = shape(b)
    if ac != br:
        raise LayoutError("multiply shape mismatch")
    return tuple(
        tuple(sum((a[i][k] * b[k][j] for k in range(ac)), F(0))
              for j in range(bc))
        for i in range(ar)
    )


def inverse(a: Matrix) -> Matrix:
    n, m = shape(a)
    if n != m:
        raise LayoutError("inverse requires square matrix")
    aug = [list(row) + list(identity(n)[i]) for i, row in enumerate(a)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col]), None)
        if pivot is None:
            raise LayoutError("singular matrix")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        p = aug[col][col]
        aug[col] = [x / p for x in aug[col]]
        for r in range(n):
            if r == col:
                continue
            q = aug[r][col]
            aug[r] = [
                x - q * y for x, y in zip(aug[r], aug[col], strict=True)
            ]
    return tuple(tuple(row[n:]) for row in aug)


def block_lower(c: Matrix, d: Matrix, k: Matrix) -> Matrix:
    nc, mc = shape(c)
    nk, mk = shape(k)
    dr, dc = shape(d)
    if nc != mc or nk != mk or (dr, dc) != (nk, nc):
        raise LayoutError("invalid block-lower shapes")
    z = zeros(nc, nk)
    return tuple(
        tuple(c[i]) + tuple(z[i]) for i in range(nc)
    ) + tuple(
        tuple(d[i]) + tuple(k[i]) for i in range(nk)
    )


def contiguous_part(a: Matrix, carrier_dim: int, kind: str) -> Matrix:
    n, m = shape(a)
    if n != m or carrier_dim <= 0 or carrier_dim >= n:
        raise LayoutError("invalid contiguous block layout")
    if kind == "carrier":
        return tuple(tuple(row[:carrier_dim]) for row in a[:carrier_dim])
    if kind == "kernel":
        return tuple(tuple(row[carrier_dim:]) for row in a[carrier_dim:])
    if kind == "lower":
        return tuple(tuple(row[:carrier_dim]) for row in a[carrier_dim:])
    raise LayoutError(f"unknown part {kind}")


def predecessor_interleaved_part(a: Matrix, kind: str) -> Matrix:
    """The rejected 8+4 extractor from the superseded predecessor."""
    if shape(a) != (12, 12):
        raise LayoutError("mutation is specific to the 12-state fixture")
    nr = 8 if kind == "carrier" else 4
    nc = 8 if kind == "lower" else nr
    rows = [
        i if kind == "carrier" and i < 4
        else i + 2 if kind == "carrier"
        else i + 4 if i < 2
        else i + 8
        for i in range(nr)
    ]
    cols = [
        j + 4 if kind == "kernel" and j < 2
        else j + 8 if kind == "kernel"
        else j if j < 4
        else j + 2
        for j in range(nc)
    ]
    return tuple(tuple(a[i][j] for j in cols) for i in rows)


def compose_structured(left: Matrix, right: Matrix, carrier_dim: int) -> Matrix:
    lc = contiguous_part(left, carrier_dim, "carrier")
    lk = contiguous_part(left, carrier_dim, "kernel")
    ld = contiguous_part(left, carrier_dim, "lower")
    rc = contiguous_part(right, carrier_dim, "carrier")
    rk = contiguous_part(right, carrier_dim, "kernel")
    rd = contiguous_part(right, carrier_dim, "lower")
    return block_lower(mul(lc, rc), add(mul(ld, rc), mul(lk, rd)), mul(lk, rk))


def moving_formula(
    u: Matrix,
    b0: Matrix,
    b1: Matrix,
    carrier_dim: int,
) -> Matrix:
    uc = contiguous_part(u, carrier_dim, "carrier")
    uk = contiguous_part(u, carrier_dim, "kernel")
    lower = contiguous_part(u, carrier_dim, "lower")
    cc0 = contiguous_part(b0, carrier_dim, "carrier")
    ck0 = contiguous_part(b0, carrier_dim, "kernel")
    d0 = contiguous_part(b0, carrier_dim, "lower")
    cc1 = contiguous_part(b1, carrier_dim, "carrier")
    ck1 = contiguous_part(b1, carrier_dim, "kernel")
    d1 = contiguous_part(b1, carrier_dim, "lower")
    wc = mul(inverse(cc1), mul(uc, cc0))
    wk = mul(inverse(ck1), mul(uk, ck0))
    wl = mul(
        inverse(ck1),
        sub(add(mul(lower, cc0), mul(uk, d0)), mul(d1, wc)),
    )
    return block_lower(wc, wl, wk)


def verify_layout_fixtures() -> bool:
    c1 = matrix(((2, 1), (0, 3)))
    d1 = matrix(((5, -2),))
    k1 = matrix(((7,),))
    c2 = matrix(((1, 4), (2, 1)))
    d2 = matrix(((-3, 6),))
    k2 = matrix(((11,),))
    left = block_lower(c1, d1, k1)
    right = block_lower(c2, d2, k2)
    if compose_structured(left, right, 2) != mul(left, right):
        return False

    # Exact moving-frame identity, including the lower formula.
    u = block_lower(matrix(((2, 0), (1, 1))), matrix(((3, 2),)), matrix(((5,),)))
    b0 = block_lower(matrix(((1, 1), (0, 2))), matrix(((4, -1),)), matrix(((3,),)))
    b1 = block_lower(matrix(((2, 0), (1, 1))), matrix(((1, 5),)), matrix(((7,),)))
    expected = mul(inverse(b1), mul(u, b0))
    if moving_formula(u, b0, b1, 2) != expected:
        return False

    # A 12-state witness makes the superseded interleaved extractor visibly
    # different from the contiguous carrier block.
    c12 = tuple(
        tuple(F(100 * i + j + 1) for j in range(8))
        for i in range(8)
    )
    d12 = tuple(
        tuple(F(1000 + 100 * i + j) for j in range(8))
        for i in range(4)
    )
    k12 = tuple(
        tuple(F(2000 + 100 * i + j) for j in range(4))
        for i in range(4)
    )
    tagged = block_lower(c12, d12, k12)
    if predecessor_interleaved_part(tagged, "carrier") == c12:
        return False
    if predecessor_interleaved_part(tagged, "kernel") == k12:
        return False
    if predecessor_interleaved_part(tagged, "lower") == d12:
        return False
    return True

