"""The G0 reverse-physics carrier: linear vector fields on a 2n-dimensional
state space, with the degree-of-freedom split declared explicitly.

Coordinates are ordered ``(q_1, p_1, ..., q_n, p_n)`` so that "degree of
freedom k" is literally the 2x2 diagonal block k.  That ordering is the whole
point of the carrier: the assumption under test ("each degree of freedom
independently conserves information") is only *statable* once the split is
part of the structure, and the marginal condition below is exactly the block
statement.

This module holds only declarations -- the symplectic form, the block split,
and the witness matrices.  It deliberately computes no dimension, no rank and
no verdict, so that the generator (rail A) and the verifier (rail B) share
definitions without sharing inference.
"""

from __future__ import annotations

from fractions import Fraction

from reverse_physics.exact_linalg import Matrix

# --- assumption vocabulary -------------------------------------------------
#
# A separate namespace from the programme's four computational-regime tags
# (LOCAL-ALGEBRAIC / EUCLIDEAN-SPECTRAL / REDUCED-MODE / LORENTZIAN-CAUSAL).
# These name *physical postulates*, not computational regimes, and the two
# namespaces must never be mixed in one field.

RP_DETERMINISTIC = "RP-DETERMINISTIC"
RP_REVERSIBLE = "RP-REVERSIBLE"
RP_INFORMATION_CONSERVING = "RP-INFORMATION-CONSERVING"
RP_MARGINAL_INFORMATION_CONSERVING = "RP-MARGINAL-INFORMATION-CONSERVING"
RP_LINEAR_CARRIER = "RP-LINEAR-CARRIER"

# NOTE (REVERSE_PHYSICS_STOCHASTIC_ROCQ_V1): RP-REVERSIBLE is NOT independent of
# {RP-DETERMINISTIC, RP-INFORMATION-CONSERVING} on the finite-state stochastic
# carrier -- there it is exactly their conjunction.  Certificates on the
# Hamiltonian carriers list determinism and reversibility as two separate
# consumed assumptions, which on that evidence overstates how many are in play.
# The equivalence is NOT proved for the continuous carriers, so the listings are
# left as they are rather than silently merged.

ASSUMPTION_GLOSS = {
    RP_DETERMINISTIC: "the state at one time fixes the state at every other time",
    RP_REVERSIBLE: "the evolution map is invertible; distinct states stay distinct",
    RP_INFORMATION_CONSERVING: "the flow preserves the total phase-space volume (global Liouville)",
    RP_MARGINAL_INFORMATION_CONSERVING: "each degree of freedom independently preserves its own 2-dimensional phase-space area",
    RP_LINEAR_CARRIER: "SCOPE RESTRICTION, not a physical postulate: the vector field is linear, so the flow is exp(tA)",
}


def symplectic_form(dof: int) -> Matrix:
    """Block-diagonal Omega = diag(J, ..., J) with J = [[0, 1], [-1, 0]]."""
    size = 2 * dof
    omega = [[Fraction(0)] * size for _ in range(size)]
    for k in range(dof):
        omega[2 * k][2 * k + 1] = Fraction(1)
        omega[2 * k + 1][2 * k] = Fraction(-1)
    return omega


def block(matrix: Matrix, i: int, j: int) -> Matrix:
    """The 2x2 block coupling degree of freedom ``i`` to degree of freedom ``j``."""
    return [[matrix[2 * i + a][2 * j + b] for b in range(2)] for a in range(2)]


def from_blocks(blocks: dict[tuple[int, int], list[list[int]]], dof: int) -> Matrix:
    """Assemble a 2n x 2n matrix from a sparse dict of 2x2 blocks."""
    size = 2 * dof
    matrix = [[Fraction(0)] * size for _ in range(size)]
    for (i, j), entries in blocks.items():
        for a in range(2):
            for b in range(2):
                matrix[2 * i + a][2 * j + b] = Fraction(entries[a][b])
    return matrix


I2 = [[1, 0], [0, 1]]
J2 = [[0, 1], [-1, 0]]


# --- witnesses -------------------------------------------------------------
#
# Each witness is a named separating example.  A witness is what makes a
# necessity claim falsifiable: it is a concrete system satisfying every
# assumption except the one under test.

def witness_marginal_not_hamiltonian() -> Matrix:
    """2 DOF: pure inter-DOF shear.

    dq1/dt = q2, dp1/dt = p2, dq2/dt = dp2/dt = 0.

    Every degree of freedom independently preserves its own area (both diagonal
    blocks vanish, so both marginal traces are zero), yet the flow is not
    symplectic.  This is the witness that kills sufficiency of marginal
    information conservation.
    """
    return from_blocks({(0, 1): I2}, dof=2)


def witness_global_not_marginal() -> Matrix:
    """2 DOF: DOF 1 expands, DOF 2 contracts at the matching rate.

    Total phase-space volume is preserved but neither degree of freedom
    preserves its own area.  This is the witness that separates global from
    marginal information conservation.
    """
    return from_blocks({(0, 0): I2, (1, 1): [[-1, 0], [0, -1]]}, dof=2)


def witness_hamiltonian_control() -> Matrix:
    """2 DOF positive control: the Hamiltonian flow of H = (1/2)|x|^2.

    A genuine element of sp(4, Q).  Present so that the membership predicates
    are demonstrably non-vacuous -- a test suite in which every witness fails
    every predicate proves nothing.
    """
    return symplectic_form(2)


WITNESSES = {
    "marginal_not_hamiltonian": witness_marginal_not_hamiltonian,
    "global_not_marginal": witness_global_not_marginal,
    "hamiltonian_control": witness_hamiltonian_control,
}
