"""Exact reference algebra for a block-lower Peano--Baker transition.

This module is deliberately independent of the Forge implementation.  It
provides a small rational rail for the algebraic identity

    A = [[Ac, 0], [G, Ak]]

and for the constant-coefficient recurrence

    Pc[n+1] = Ac Pc[n],
    Pk[n+1] = Ak Pk[n],
    Pl[n+1] = G Pc[n] + Ak Pl[n].

The implementation is a test oracle, not a numerical ODE solver.
"""
from __future__ import annotations

from fractions import Fraction
from math import factorial
from typing import Iterable


Q = Fraction
Matrix = tuple[tuple[Q, ...], ...]


class StructureError(ValueError):
    pass


def matrix(rows: Iterable[Iterable[int | Q]]) -> Matrix:
    out = tuple(tuple(Q(value) for value in row) for row in rows)
    if not out or not out[0] or any(len(row) != len(out[0]) for row in out):
        raise StructureError("matrix must be nonempty and rectangular")
    return out


def zeros(rows: int, cols: int) -> Matrix:
    if rows <= 0 or cols <= 0:
        raise StructureError("matrix dimensions must be positive")
    return tuple(tuple(Q(0) for _ in range(cols)) for _ in range(rows))


def identity(n: int) -> Matrix:
    return tuple(
        tuple(Q(int(i == j)) for j in range(n))
        for i in range(n)
    )


def shape(a: Matrix) -> tuple[int, int]:
    return len(a), len(a[0])


def add(a: Matrix, b: Matrix) -> Matrix:
    if shape(a) != shape(b):
        raise StructureError("addition shape mismatch")
    return tuple(
        tuple(x + y for x, y in zip(ar, br, strict=True))
        for ar, br in zip(a, b, strict=True)
    )


def scale(a: Matrix, q: Q) -> Matrix:
    return tuple(tuple(q * x for x in row) for row in a)


def mul(a: Matrix, b: Matrix) -> Matrix:
    ar, ac = shape(a)
    br, bc = shape(b)
    if ac != br:
        raise StructureError("multiplication shape mismatch")
    return tuple(
        tuple(sum((a[i][k] * b[k][j] for k in range(ac)), Q(0))
              for j in range(bc))
        for i in range(ar)
    )


def block_lower(ac: Matrix, lower: Matrix, ak: Matrix) -> Matrix:
    nc, nc2 = shape(ac)
    nk, nk2 = shape(ak)
    lr, lc = shape(lower)
    if nc != nc2 or nk != nk2 or (lr, lc) != (nk, nc):
        raise StructureError("invalid block-lower shapes")
    z = zeros(nc, nk)
    return tuple(
        tuple(ac[i][j] for j in range(nc)) + z[i]
        for i in range(nc)
    ) + tuple(
        lower[i] + tuple(ak[i][j] for j in range(nk))
        for i in range(nk)
    )


def structured_powers(
    ac: Matrix,
    g: Matrix,
    ak: Matrix,
    order: int,
    *,
    mutation: str | None = None,
) -> tuple[tuple[Matrix, Matrix, Matrix], ...]:
    """Return powers 0..order as (carrier, lower, kernel) blocks.

    Mutation modes exist only for independent negative-control tests.
    """
    nc, nc2 = shape(ac)
    nk, nk2 = shape(ak)
    if nc != nc2 or nk != nk2 or shape(g) != (nk, nc) or order < 0:
        raise StructureError("invalid structured power input")
    pc, pk, pl = identity(nc), identity(nk), zeros(nk, nc)
    out = [(pc, pl, pk)]
    for _ in range(order):
        old_pc, old_pl, old_pk = pc, pl, pk
        pc = mul(ac, old_pc)
        pk = mul(ak, old_pk)
        if mutation == "omit_kernel_lower":
            pl = mul(g, old_pc)
        elif mutation == "swap_order":
            # Shape-compatible only for the square fixture; intentionally
            # reverses both products.
            pl = add(mul(old_pc, g), mul(old_pl, ak))
        else:
            pl = add(mul(g, old_pc), mul(ak, old_pl))
        out.append((pc, pl, pk))
    return tuple(out)


def structured_truncated_exponential(
    ac: Matrix,
    g: Matrix,
    ak: Matrix,
    h: Q,
    order: int,
    *,
    mutation: str | None = None,
) -> Matrix:
    powers = structured_powers(ac, g, ak, order, mutation=mutation)
    nc, _ = shape(ac)
    nk, _ = shape(ak)
    sc, sk, sl = zeros(nc, nc), zeros(nk, nk), zeros(nk, nc)
    for n, (pc, pl, pk) in enumerate(powers):
        q = h**n / factorial(n)
        sc = add(sc, scale(pc, q))
        sl = add(sl, scale(pl, q))
        sk = add(sk, scale(pk, q))
    return block_lower(sc, sl, sk)


def full_truncated_exponential(a: Matrix, h: Q, order: int) -> Matrix:
    n, m = shape(a)
    if n != m:
        raise StructureError("full exponential requires a square matrix")
    power = identity(n)
    out = zeros(n, n)
    for j in range(order + 1):
        out = add(out, scale(power, h**j / factorial(j)))
        power = mul(a, power)
    return out


def exact_nilpotent_exponential(a: Matrix, h: Q) -> Matrix:
    """Sum until a power vanishes, refusing a non-nilpotent fixture."""
    n, m = shape(a)
    if n != m:
        raise StructureError("nilpotent exponential requires a square matrix")
    power = identity(n)
    out = zeros(n, n)
    for j in range(n + 1):
        out = add(out, scale(power, h**j / factorial(j)))
        power = mul(a, power)
        if power == zeros(n, n):
            return out
    raise StructureError("fixture is not nilpotent within its dimension")


def exact_fixture() -> tuple[Matrix, Matrix, Matrix, Q]:
    # Both diagonal blocks and the complete block matrix are nilpotent, while
    # the lower recurrence uses both G Pc and Ak Pl nontrivially.
    ac = matrix(((0, 1), (0, 0)))
    ak = matrix(((0, 2), (0, 0)))
    g = matrix(((1, 3), (2, 5)))
    return ac, g, ak, Q(3, 8)


def verify_exact_fixture(mutation: str | None = None) -> bool:
    ac, g, ak, h = exact_fixture()
    a = block_lower(ac, g, ak)
    expected = exact_nilpotent_exponential(a, h)
    got = structured_truncated_exponential(
        ac, g, ak, h, len(a), mutation=mutation
    )
    return got == expected
