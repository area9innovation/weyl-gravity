#!/usr/bin/env python3
"""Exact finite-block certificate for the conformal Born--metric bridge.

The calculation is algebraic.  ``P`` is the complete compact-cylinder
eigenspace of the ordinary-self-adjoint generator ``H0`` and ``Q=1-P`` has
no state at the same energy.  The fixed free Hermitian form ``J`` commutes
with ``H0``.  These hypotheses are stronger than semisimplicity alone and
are what make the reduced resolvent self-adjoint.  For

    H = H0 + g V1 + g**2 V2 + ...,
    G = J  + g G1 + g**2 G2 + ...,

the first two equations in ``H^dagger G = G H`` are used.  The script checks
that the canonical off-shell solution for ``G1`` identifies the complete
second-order shell source with the J-anti-Hermitian part of the stationary
contact-plus-exchange Born operator.

It also checks the important limitation: a homogeneous first-order metric
correction can change the second-order shell source when ``P V1 P`` is
nonzero.  The ambiguity disappears automatically under the stronger cubic
shell statement ``P V1 P=0``.
"""

from __future__ import annotations

import sympy as sp


PASS = True


def check(label: str, condition: object) -> None:
    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


def dagger(matrix: sp.Matrix) -> sp.Matrix:
    return matrix.conjugate().T


def embed_blocks(
    pp: sp.Matrix, pq: sp.Matrix, qp: sp.Matrix, qq: sp.Matrix
) -> sp.Matrix:
    return pp.row_join(pq).col_join(qp.row_join(qq))


def main() -> None:
    # A nontrivial exact fixture: a two-dimensional energy-six shell and a
    # three-dimensional off-shell space with distinct semisimple energies.
    p_dim, q_dim = 2, 3
    energy = sp.Integer(6)
    hq = sp.diag(8, 10, 13)
    h0 = sp.diag(energy, energy, 8, 10, 13)
    jp = sp.diag(1, -1)
    jq = sp.diag(-1, 1, -1)
    j = sp.diag(1, -1, -1, 1, -1)
    zero_pp = sp.zeros(p_dim)
    zero_qq = sp.zeros(q_dim)

    # Use exact complex entries and a vanishing P-P cubic block.  No
    # pseudo-Hermiticity of V1 is assumed; G1 must absorb its off-shell source.
    vpq = sp.Matrix([[1 + sp.I, 2, -sp.I], [3, 1 - 2 * sp.I, 4]])
    vqp = sp.Matrix([[2, 1], [-sp.I, 3], [1 + sp.I, -2]])
    vqq = sp.Matrix(
        [[1, sp.I, 0], [2, -1, 3], [1 - sp.I, 0, 2]]
    )
    v1 = embed_blocks(zero_pp, vpq, vqp, vqq)
    v2 = sp.Matrix(
        [
            [1, 2 + sp.I, 0, 1, -1],
            [3 - sp.I, -2, 1, 0, 2],
            [0, 1, 1, sp.I, 0],
            [2, 0, -1, 3, 1],
            [1, -2, 0, 1 - sp.I, -1],
        ]
    )

    p = sp.diag(1, 1, 0, 0, 0)
    q = sp.eye(p_dim + q_dim) - p
    reduced_q = (energy * sp.eye(q_dim) - hq).inv()
    reduced = embed_blocks(
        zero_pp, sp.zeros(p_dim, q_dim), sp.zeros(q_dim, p_dim), reduced_q
    )
    d1 = j * v1 - dagger(v1) * j

    # Canonical off-shell G1.  Only P-Q and Q-P entries enter the projected
    # second-order identity; the Q-Q solution may be chosen independently.
    g1 = p * d1 * reduced - reduced * d1 * p
    first_residual = h0 * g1 - g1 * h0 - d1
    check(
        "C1-bridge: canonical G1 solves every P-Q first-order component",
        p * first_residual * q == sp.zeros(5)
        and q * first_residual * p == sp.zeros(5),
    )
    check("C1-bridge: canonical off-shell G1 is Hermitian", dagger(g1) == g1)

    source2 = p * (
        j * v2 - dagger(v2) * j + g1 * v1 - dagger(v1) * g1
    ) * p
    born2 = p * (v2 + v1 * reduced * v1) * p
    rhs = p * (j * born2 - dagger(born2) * j) * p
    check(
        "C1-bridge: complete second-order shell source equals J-Born difference",
        sp.simplify(source2 - rhs) == sp.zeros(5),
    )
    alternate_born2 = p * (
        v2
        - v1
        * embed_blocks(
            zero_pp,
            sp.zeros(p_dim, q_dim),
            sp.zeros(q_dim, p_dim),
            (hq - energy * sp.eye(q_dim)).inv(),
        )
        * v1
    ) * p
    check(
        "C1-bridge: reduced convention is contact minus (H0-E)^-1 exchange",
        sp.simplify(born2 - alternate_born2) == sp.zeros(5),
    )

    # The fixed-D shell deformation map vanishes identically on P.
    x2 = sp.Matrix([[1, 2 + sp.I], [2 - sp.I, -1]])
    x2_full = embed_blocks(x2, sp.zeros(2, 3), sp.zeros(3, 2), zero_qq)
    check(
        "C1-bridge: the complete shell source is cokernel for semisimple D",
        p * (h0 * x2_full - x2_full * h0) * p == sp.zeros(5),
    )

    # A homogeneous first-order correction is block diagonal in energy.  Its
    # projected second-order shift vanishes if P V1 P vanishes.
    xp = sp.Matrix([[2, 1 + sp.I], [1 - sp.I, -1]])
    homogeneous = embed_blocks(xp, sp.zeros(2, 3), sp.zeros(3, 2), zero_qq)
    ambiguity = p * (homogeneous * v1 - dagger(v1) * homogeneous) * p
    check(
        "C1-bridge: P V1 P=0 removes first-order metric ambiguity",
        ambiguity == sp.zeros(5),
    )

    # Conversely, first-order source closure alone does not remove the
    # ambiguity.  Choose a nonzero J_P-self-adjoint shell vertex and exhibit a
    # Hermitian homogeneous X_P whose second-order shift is nonzero.
    vpp = sp.Matrix([[1, 1], [-1, 2]])
    check(
        "C1-bridge: example shell vertex is J_P-self-adjoint",
        jp * vpp - dagger(vpp) * jp == sp.zeros(2),
    )
    ambiguity_example = sp.simplify(xp * vpp - dagger(vpp) * xp)
    check(
        "C1-bridge: source closure without P V1 P=0 leaves an ambiguity",
        ambiguity_example != sp.zeros(2),
    )

    print("Reduced resolvent Q(E-H0)^-1Q:", reduced)
    print("Exact shell Born block:", sp.simplify(born2[:2, :2]))
    print("Exact second-order source:", sp.simplify(source2[:2, :2]))
    print("Nonzero ambiguity counterexample:", ambiguity_example)
    if not PASS:
        raise SystemExit("CONFORMAL DEFORMATION BRIDGE: FAIL")
    print("CONFORMAL DEFORMATION BRIDGE: ALL PASS")


if __name__ == "__main__":
    main()
