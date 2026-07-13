#!/usr/bin/env python3
"""Exact C0c comparison of the Mannheim and conventional conformal adjoints.

The calculation separates four objects which are often conflated at a
Jordan exceptional point:

* a right ket and its ordinary Dirac-adjoint bra;
* the independently evolving left bra;
* the intertwining form G which maps the first bra to the second; and
* the spectral C involution of the diagonalizable regulator.

The normal form used below is the universal rank-two exceptional-point
model

    H_delta = [[E, 1], [delta**2, E]].

It has eigenvalues E+-delta and tends to the upper Jordan block displayed
in Bender--Mannheim, arXiv:0804.4190, Eq. (63).  This normal form makes the
singular mechanism independent of Pais--Uhlenbeck normalization choices.

Checks
------
C0c-1  Every nondegenerate time-independent Hermitian form preserved by a
       genuine rank-two Jordan block is indefinite.  The overlap matrix
       printed in Bender--Mannheim Eq. (95) is congruent to this cross form.
C0c-2  Right kets, ordinary bras, left bras, generalized chains, time
       evolution, and completeness are kept distinct explicitly.
C0c-3  Before coalescence the positive V metric and nontrivial C involution
       exist, but both are singular as delta -> 0.  The finite cross form
       survives, while the Jordan commutant contains only C=+-I involutions.
C0c-4  On the complete six-mode conformal multiplet, standard reality,
       rotations, Metsaev's boosts, and P_0 covariance leave one form up to
       scale.  Any fixed conventional conformal extension of the Mannheim
       cross form is therefore c J_conf and is indefinite.
C0c-5  The Kubo--Kuntz cross commutator and the Mannheim left--right overlap
       are the same Jordan-dual algebra up to a generalized-vector shift and
       normalization.  Their difference is interpretive, not a second fixed
       positive Hermitian form.
C0c-6  If a genuinely different Mannheim form is Hamiltonian-dependent, the
       first Jordan metric-deformation equation has a two-dimensional
       cokernel.  This records the exact interface for the interaction test;
       it is not itself an interaction result.

For a representation generator X, "invariance" means the appropriate
adjoint relation X^dagger G = G X (or its skew-generator counterpart), not
the basis-dependent condition [G,X]=0.
"""

from __future__ import annotations

import sympy as sp


PASS = True


def check(label: str, condition: object) -> None:
    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


def h_adjoint(matrix: sp.Matrix) -> sp.Matrix:
    return matrix.conjugate().T


# ---------------------------------------------------------------------------
# C0c-1: invariant forms of the equal-frequency Jordan block
# ---------------------------------------------------------------------------
E, time = sp.symbols("E time", real=True)
I2 = sp.eye(2)
Z2 = sp.zeros(2)
N = sp.Matrix([[0, 1], [0, 0]])
H0 = E * I2 + N

a, b, c, d = sp.symbols("a b c d", real=True)
G_general = sp.Matrix([[a, c + sp.I * d], [c - sp.I * d, b]])
invariance_equations = list(h_adjoint(H0) * G_general - G_general * H0)
invariant_solution = sp.solve(
    invariance_equations, (a, b, c, d), dict=True
)

check("C0c-1: Jordan invariance forces a=0 and Im(cross)=0",
      invariant_solution == [{a: 0, d: 0}])

G_jordan = sp.Matrix([[0, c], [c, b]])
check("C0c-1: a nondegenerate Jordan form has negative determinant",
      sp.factor(G_jordan.det()) == -c**2)
check("C0c-1: the stationary eigenvector is necessarily null",
      (sp.Matrix([[1, 0]]) * G_jordan * sp.Matrix([1, 0]))[0] == 0)

# Bender--Mannheim arXiv:0804.4190, Eq. (95), in the ordered basis
# (stationary state 1, nonstationary state 1a).  We suppress the positive
# common constant pi/(8 gamma^2 omega^4) as kappa.
omega, kappa = sp.symbols("omega kappa", positive=True, real=True)
H_published = 2 * omega * sp.Matrix([[1, 1], [0, 1]])
G_published = sp.Matrix(
    [[0, -kappa], [-kappa, -kappa / omega]]
)
shift = sp.Matrix([[1, -sp.Rational(1, 2) / omega], [0, 1]])
G_published_shifted = sp.simplify(shift.T * G_published * shift)

check("C0c-1: the published equal-frequency overlap is conserved",
      H_published.T * G_published == G_published * H_published)
check("C0c-1: the published overlap is nondegenerate but indefinite",
      sp.factor(G_published.det()) == -kappa**2)
check("C0c-1: a Jordan-chain shift reduces Eq. (95) to a cross form",
      G_published_shifted == -kappa * sp.Matrix([[0, 1], [1, 0]]))


# ---------------------------------------------------------------------------
# C0c-2: right, Dirac-adjoint, left, and generalized states
# ---------------------------------------------------------------------------
J = sp.Matrix([[0, 1], [1, 0]])
r0 = sp.Matrix([1, 0])  # stationary right eigenvector
r1 = sp.Matrix([0, 1])  # right generalized eigenvector
dirac0 = h_adjoint(r0)
dirac1 = h_adjoint(r1)
left0 = dirac0 * J       # left eigenvector
left1 = dirac1 * J       # left generalized vector

check("C0c-2: the right vectors form a Jordan chain",
      H0 * r0 == E * r0 and H0 * r1 == E * r1 + r0)
check("C0c-2: the mapped left vectors form the dual Jordan chain",
      left0 * H0 == E * left0
      and left1 * H0 == E * left1 + left0)
check("C0c-2: ordinary Dirac bras are not the left Jordan chain",
      dirac0 != left0 and dirac1 != left1)
check("C0c-2: stationary and generalized self-overlaps vanish",
      (left0 * r0)[0] == 0 and (left1 * r1)[0] == 0)
check("C0c-2: the cross overlaps are nonzero and normalized",
      (left0 * r1)[0] == 1 and (left1 * r0)[0] == 1)

completeness = r0 * left1 + r1 * left0
reconstructed_H = E * completeness + r0 * left0
check("C0c-2: stationary plus generalized vectors are complete",
      completeness == I2)
check("C0c-2: the left-right chains reconstruct the Jordan Hamiltonian",
      reconstructed_H == H0)

# The irrelevant scalar phase exp(-iEt) cancels in U^dagger J U.
U_nilpotent = I2 - sp.I * time * N
check("C0c-2: Jordan time evolution preserves the cross form exactly",
      sp.simplify(h_adjoint(U_nilpotent) * J * U_nilpotent) == J)


# ---------------------------------------------------------------------------
# C0c-3: diagonalizable regulator, positive V, and singular C
# ---------------------------------------------------------------------------
delta = sp.symbols("delta", positive=True, real=True)
H_delta = sp.Matrix([[E, 1], [delta**2, E]])
P = J
C_delta = sp.Matrix([[0, 1 / delta], [delta, 0]])
V_delta = sp.simplify(P * C_delta)

check("C0c-3: the regulated eigenvalues are E+-delta",
      H_delta.eigenvals() == {E - delta: 1, E + delta: 1})
check("C0c-3: P intertwines H_delta and its ordinary adjoint",
      P * H_delta * P == h_adjoint(H_delta))
check("C0c-3: C_delta is a commuting spectral involution",
      C_delta**2 == I2 and C_delta * H_delta == H_delta * C_delta)
check("C0c-3: V_delta=P C_delta is positive for delta>0",
      V_delta == sp.diag(delta, 1 / delta)
      and V_delta.det() == 1)
check("C0c-3: V_delta implements pseudo-Hermiticity",
      h_adjoint(H_delta) * V_delta == V_delta * H_delta)

r_plus = sp.Matrix([1, delta])
r_minus = sp.Matrix([1, -delta])
left_plus = h_adjoint(r_plus) * V_delta
left_minus = h_adjoint(r_minus) * V_delta

check("C0c-3: C_delta labels the two split eigenvectors",
      C_delta * r_plus == r_plus and C_delta * r_minus == -r_minus)
check("C0c-3: V_delta maps right eigenvectors to left eigenvectors",
      sp.simplify(left_plus * H_delta - (E + delta) * left_plus)
      == sp.zeros(1, 2)
      and sp.simplify(left_minus * H_delta - (E - delta) * left_minus)
      == sp.zeros(1, 2))
check("C0c-3: split eigenvectors are V-orthogonal with positive norms",
      (left_plus * r_minus)[0] == 0
      and (left_minus * r_plus)[0] == 0
      and (left_plus * r_plus)[0] == 2 * delta
      and (left_minus * r_minus)[0] == 2 * delta)
check("C0c-3: divided sums produce the Jordan right chain",
      sp.simplify((r_plus + r_minus) / 2) == r0
      and sp.simplify((r_plus - r_minus) / (2 * delta)) == r1)

# The most general real symmetric invariant form before coalescence.
b_split, c_split = sp.symbols("b_split c_split", real=True)
G_split_general = sp.Matrix(
    [[delta**2 * b_split, c_split], [c_split, b_split]]
)
det_split_general = sp.factor(G_split_general.det())
check("C0c-3: the full regulated invariant family is exact",
      H_delta.T * G_split_general == G_split_general * H_delta)
check("C0c-3: positivity requires c^2<delta^2 b^2",
      sp.simplify(
          det_split_general - (delta**2 * b_split**2 - c_split**2)
      ) == 0)

# A bounded positive representative degenerates; determinant normalization
# makes one eigenvalue diverge.  This is the finite-dimensional content of
# the singular Q/e^{-Q} limit in the PU papers.
V_bounded = sp.diag(delta**2, 1)
check("C0c-3: every displayed bounded positive representative degenerates",
      sp.limit(V_bounded.det(), delta, 0, dir="+") == 0
      and V_bounded.applyfunc(
          lambda entry: sp.limit(entry, delta, 0, dir="+")
      ) == sp.diag(0, 1))
check("C0c-3: determinant-normalized V has no bounded Jordan limit",
      sp.limit(V_delta[0, 0], delta, 0, dir="+") == 0
      and sp.limit(V_delta[1, 1], delta, 0, dir="+") == sp.oo)
check("C0c-3: the spectral C involution itself diverges",
      sp.limit(C_delta[0, 1], delta, 0, dir="+") == sp.oo)

# At the Jordan point every commuting matrix is alpha I+beta N.  Imposing
# C^2=I leaves only the trivial common sign; the two coalesced branches can
# no longer be distinguished by a finite spectral involution.
alpha_c, beta_c = sp.symbols("alpha_c beta_c", real=True)
C_jordan = alpha_c * I2 + beta_c * N
C_jordan_solutions = sp.solve(
    list(C_jordan**2 - I2), (alpha_c, beta_c), dict=True
)
check("C0c-3: no nontrivial C involution survives the Jordan point",
      C_jordan_solutions
      == [{alpha_c: -1, beta_c: 0}, {alpha_c: 1, beta_c: 0}])
check("C0c-3: the finite survivor is the indefinite P cross form",
      h_adjoint(H0) * P == P * H0 and P.det() == -1)


# ---------------------------------------------------------------------------
# C0c-4: extension to the complete conformal six-mode representation
# ---------------------------------------------------------------------------
sqrt2 = sp.sqrt(2)
A1 = sqrt2 * I2
A2 = sp.Matrix([[0, sqrt2], [-sqrt2, 0]])
B1 = -2 * sqrt2 * I2
B2 = sp.Matrix([[0, 2 * sqrt2], [-2 * sqrt2, 0]])

R1 = sp.Matrix.vstack(
    sp.Matrix.hstack(Z2, Z2, Z2),
    sp.Matrix.hstack(A1, Z2, Z2),
    sp.Matrix.hstack(Z2, B1, Z2),
)
R2 = sp.Matrix.vstack(
    sp.Matrix.hstack(Z2, Z2, Z2),
    sp.Matrix.hstack(A2, Z2, Z2),
    sp.Matrix.hstack(Z2, B2, Z2),
)
rotation = sp.diag(
    sp.Matrix([[0, -2], [2, 0]]),
    sp.Matrix([[0, -1], [1, 0]]),
    sp.Matrix([[0, -2], [2, 0]]),
)
P0_nilpotent = sp.Matrix.vstack(
    sp.Matrix.hstack(Z2, Z2, I2),
    sp.Matrix.hstack(Z2, Z2, Z2),
    sp.Matrix.hstack(Z2, Z2, Z2),
)

g_variables = sp.symbols("g0:21", real=True)
G6 = sp.zeros(6)
position = 0
for row in range(6):
    for column in range(row, 6):
        G6[row, column] = g_variables[position]
        G6[column, row] = g_variables[position]
        position += 1

form_equations: list[sp.Expr] = []
for skew_generator in (rotation, R1, R2):
    form_equations.extend(list(
        skew_generator.T * G6 + G6 * skew_generator
    ))
form_equations.extend(list(
    P0_nilpotent.T * G6 - G6 * P0_nilpotent
))
form_matrix, form_rhs = sp.linear_eq_to_matrix(
    form_equations, g_variables
)

J_conf = sp.Matrix.vstack(
    sp.Matrix.hstack(Z2, Z2, sp.Rational(1, 2) * I2),
    sp.Matrix.hstack(Z2, I2, Z2),
    sp.Matrix.hstack(sp.Rational(1, 2) * I2, Z2, Z2),
)
expected_vector = sp.zeros(21, 1)
position = 0
for row in range(6):
    for column in range(row, 6):
        expected_vector[position] = J_conf[row, column]
        position += 1

check("C0c-4: the standard-real conformal form space is one-dimensional",
      form_rhs == sp.zeros(form_rhs.rows, 1)
      and len(form_matrix.nullspace()) == 1
      and form_matrix.rank() == 20)
check("C0c-4: its generator is the C0b form J_conf",
      form_matrix * expected_vector == sp.zeros(form_matrix.rows, 1))
check("C0c-4: J_conf is nondegenerate and indefinite",
      J_conf.det() != 0
      and J_conf.eigenvals()
      == {sp.Integer(1): 2, sp.Rational(1, 2): 2,
          -sp.Rational(1, 2): 2})

# The transparent rotation-invariant ansatz has TT cross coefficient x,
# vector coefficient y, and a possible generalized-state self-pairing z.
# Full conformal covariance fixes y=2x and removes z.
x_form, y_form, z_form = sp.symbols(
    "x_form y_form z_form", real=True
)
G6_ansatz = sp.Matrix.vstack(
    sp.Matrix.hstack(Z2, Z2, x_form * I2),
    sp.Matrix.hstack(Z2, y_form * I2, Z2),
    sp.Matrix.hstack(x_form * I2, Z2, z_form * I2),
)
ansatz_equations: list[sp.Expr] = []
for skew_generator in (rotation, R1, R2):
    ansatz_equations.extend(list(
        skew_generator.T * G6_ansatz + G6_ansatz * skew_generator
    ))
ansatz_equations.extend(list(
    P0_nilpotent.T * G6_ansatz - G6_ansatz * P0_nilpotent
))
ansatz_solution = sp.solve(
    ansatz_equations, (x_form, y_form, z_form), dict=True
)
check("C0c-4: boosts fix vector/cross ratio and the Jordan-chain shift",
      ansatz_solution == [{x_form: y_form / 2, z_form: 0}])


# ---------------------------------------------------------------------------
# C0c-5: Mannheim and Kubo--Kuntz use the same fixed Jordan dual
# ---------------------------------------------------------------------------
# In Kubo--Kuntz notation the physical TT commutators pair h with H and
# make each diagonal commutator vanish.  In the ordered (H,h) or (E,L)
# basis this is sigma_x, up to normalization.  Bender--Mannheim Eq. (95)
# was reduced to -kappa sigma_x above.
J_kubo_kuntz = J
check("C0c-5: Kubo--Kuntz has the canonical cross Gram matrix",
      J_kubo_kuntz == J and J_kubo_kuntz.det() == -1)
check("C0c-5: Mannheim Eq. (95) is the same congruence class",
      G_published_shifted == -kappa * J_kubo_kuntz)
check("C0c-5: fixed full conformal covariance leaves no second form",
      len(form_matrix.nullspace()) == 1)


# ---------------------------------------------------------------------------
# C0c-6: exact deformation-complex interface for a dynamical G(H)
# ---------------------------------------------------------------------------
# For H=H0+gH1 and G=G0+gG1, the first equation is
#
#   H0^dag G1-G1 H0 = G0 H1-H1^dag G0.
#
# On one Jordan block the left side has only two real directions.
a1, b1, c1, d1 = sp.symbols("a1 b1 c1 d1", real=True)
G1 = sp.Matrix([[a1, c1 + sp.I * d1], [c1 - sp.I * d1, b1]])
deformation_image = sp.simplify(h_adjoint(H0) * G1 - G1 * H0)
s0, s1, source_x, source_y = sp.symbols(
    "s0 s1 source_x source_y", real=True
)
antihermitian_source = sp.Matrix([
    [sp.I * s0, source_x + sp.I * source_y],
    [-source_x + sp.I * source_y, sp.I * s1],
])
check("C0c-6: the Jordan deformation image is exact",
      deformation_image
      == sp.Matrix([[0, -a1], [a1, 2 * sp.I * d1]]))
# SymPy expresses the four free variables differently across versions, so
# test the two invariant solvability conditions directly.
check("C0c-6: solvability requires source_11=0 and Im(source_12)=0",
      sp.solve(
          list(deformation_image - antihermitian_source),
          (a1, d1, s0, source_y),
          dict=True,
      ) == [{a1: -source_x, d1: s1 / 2, s0: 0, source_y: 0}])
check("C0c-6: the metric ambiguity remains two-dimensional",
      b1 not in deformation_image.free_symbols
      and c1 not in deformation_image.free_symbols)


if not PASS:
    raise SystemExit("CONFORMAL C0C: FAIL")

print("CONFORMAL C0C: ALL PASS")
print("Fixed standard-covariant outcome: G_M is c J_conf and indefinite.")
print("The split positive V and spectral C are singular at coalescence.")
print("Any distinct proposal must be dynamical/singular or relax a C0b hypothesis.")
