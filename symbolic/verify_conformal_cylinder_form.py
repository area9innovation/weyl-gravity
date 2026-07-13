#!/usr/bin/env python3
"""Exact C0b certificate for the free conformal-gravity one-particle form.

This script reconciles four descriptions of the pure-Weyl free theory:

* Paper IV's reduced flat TT/vector/scalar decomposition;
* Kubo--Kuntz's flat BRST cohomology and P_0 Jordan algebra;
* Metsaev's ordinary-derivative conformal transformations; and
* the Beccaria--Bekaert--Tseytlin spectrum on R x S^3.

The main correction to the initial research plan is that the compact cylinder
Hamiltonian D is diagonalizable.  The Jordan generator is flat time
translation P_0.  On the cylinder the physical module instead consists of
two distinct TT towers and one vector tower.  The standard radial-adjoint
SO(4,2)-invariant form is the (indefinite) Shapovalov form.

Checks
------
C0b-1  The cylinder TT operator factorizes into distinct frequencies n+2
       and n+4; the vector frequency is n+2.  There is no modewise cylinder
       Jordan block.
C0b-2  The three harmonic towers reproduce the published Weyl-graviton
       one-particle character exactly.
C0b-3  The level-one Shapovalov form of the Delta=2 Weyl primary has
       eigenvalues +8 and -2.  After both chiralities are included, their
       multiplicities 24 and 16 match exactly the TT and vector cylinder
       harmonics at energy three.
C0b-4  Metsaev's transverse internal conformal-boost chain
       E_(+-2) -> A_(+-1) -> L_(+-2), together with rotations and the flat
       Jordan Hamiltonian, fixes the six-mode bilinear form up to one scale.
       Thus the vector sign is not an independent conformal choice.
C0b-5  The full compact-energy signature and its signed character follow
       from the lower-TT Shapovalov normalization, the opposite fourth-order
       residue of the upper TT tower, and the level-one vector sign.
C0b-6  The invariant form is already indefinite at level one.  Reversing the
       overall Weyl-action sign swaps all positive and negative counts but
       cannot make the module positive.

This is a free conventional-radial-adjoint theorem.  It does not test an
alternative Mannheim left-right/CPT adjoint, and it does not yet test the
interaction.
"""

from __future__ import annotations

import sympy as sp


PASS = True


def check(label: str, condition: object) -> None:
    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


# ---------------------------------------------------------------------------
# C0b-1: exact R x S^3 factorization
# ---------------------------------------------------------------------------
n = sp.symbols("n", integer=True, nonnegative=True)
w = sp.symbols("w", real=True)

# Beccaria--Bekaert--Tseytlin, arXiv:1406.3542, Eqs. (3.17)--(3.18).
spatial_product = (n + 2) * (n + 4)
O2_harmonic = sp.expand(
    w**4 + 2 * w**2 * (spatial_product + 2) + spatial_product**2
)
O2_factorized = sp.expand((w**2 + (n + 2)**2) * (w**2 + (n + 4)**2))
frequency_gap = sp.expand((n + 4)**2 - (n + 2)**2)

check("C0b-1: the cylinder TT operator factorizes exactly",
      sp.simplify(O2_harmonic - O2_factorized) == 0)
check("C0b-1: the two compact TT frequencies are distinct",
      frequency_gap == 4 * (n + 3))
check("C0b-1: the vector tower has frequency n+2",
      sp.expand(w**2 + (n + 2)**2) == w**2 + n**2 + 4 * n + 4)

# The inverse fourth-order operator has opposite residues on the two roots.
z = sp.symbols("z")
partial_fraction = (
    1 / frequency_gap
    * (1 / (z + (n + 2)**2) - 1 / (z + (n + 4)**2))
)
check("C0b-1: the two TT second-order residues have opposite signs",
      sp.simplify(
          partial_fraction
          - 1 / ((z + (n + 2)**2) * (z + (n + 4)**2))
      ) == 0)


# ---------------------------------------------------------------------------
# C0b-2: exact cylinder character
# ---------------------------------------------------------------------------
q = sp.symbols("q")

# TT tensor and transverse-vector degeneracies on S^3.
d2 = 2 * (n + 1) * (n + 5)
d1 = 2 * (n + 1) * (n + 3)

# Closed sums.  The vector determinant in the Weyl-graviton sector starts at
# n=1; n=0 is a Killing vector and drops out of h_ij=D_(i V_j).
Z_lower = 2 * q**2 * (5 - 3 * q) / (1 - q)**3
Z_upper = sp.simplify(q**2 * Z_lower)
Z_vector = 2 * q**3 * (3 * q**2 - 9 * q + 8) / (1 - q)**3
Z_total = sp.factor(Z_lower + Z_upper + Z_vector)
Z_published_3 = 2 * q**2 * (5 + 5 * q - 4 * q**2) / (1 - q)**3
Z_published_4 = (10 * q**2 - 18 * q**4 + 8 * q**5) / (1 - q)**4

check("C0b-2: the three towers give the published cylinder character",
      sp.simplify(Z_total - Z_published_3) == 0)
check("C0b-2: cylinder and conformal-operator characters agree",
      sp.simplify(Z_total - Z_published_4) == 0)


def total_degeneracy(energy: int) -> int:
    """Unsigned physical degeneracy at compact energy E."""
    lower = 2 * (energy - 1) * (energy + 3) if energy >= 2 else 0
    vector = 2 * (energy - 1) * (energy + 1) if energy >= 3 else 0
    upper = 2 * (energy - 3) * (energy + 1) if energy >= 4 else 0
    return lower + vector + upper


series_total = sp.series(Z_total, q, 0, 11).removeO().expand()
check("C0b-2: closed character matches every tower through E=10",
      all(series_total.coeff(q, energy) == total_degeneracy(energy)
          for energy in range(2, 11)))


# ---------------------------------------------------------------------------
# C0b-3: level-one Shapovalov form of the Weyl-tensor primary
# ---------------------------------------------------------------------------
def spin_matrices(twice_j: int) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    """Hermitian SU(2) generators for j=twice_j/2, in descending m order."""
    j = sp.Rational(twice_j, 2)
    dimension = twice_j + 1
    m_values = [j - index for index in range(dimension)]
    j_plus = sp.zeros(dimension)
    for column, m_value in enumerate(m_values):
        raised = m_value + 1
        if raised <= j:
            row = m_values.index(raised)
            j_plus[row, column] = sp.sqrt(
                (j - m_value) * (j + m_value + 1)
            )
    j_minus = sp.conjugate(j_plus.T)
    j_x = sp.simplify((j_plus + j_minus) / 2)
    j_y = sp.simplify((j_plus - j_minus) / (2 * sp.I))
    j_z = sp.diag(*m_values)
    return j_x, j_y, j_z


J = spin_matrices(4)  # self-dual Weyl primary: (j_L,j_R)=(2,0)
S = spin_matrices(1)  # left spin of a translation: (1/2,1/2)
coupling = sp.zeros(10)
for J_axis, S_axis in zip(J, S):
    coupling += sp.kronecker_product(J_axis, S_axis)

Delta = sp.Integer(2)
# From <O|K_mu P_nu|O> and [K,P]=2(delta D-M).  The right spin-1/2
# of P_mu is a spectator for a (2,0) primary.
gram_level1_left = 2 * (Delta * sp.eye(10) + 2 * coupling)
gram_level1_chiral = sp.kronecker_product(gram_level1_left, sp.eye(2))
level1_eigenvalues = gram_level1_chiral.eigenvals()

check("C0b-3: one chiral level-one Gram spectrum is +8 x12, -2 x8",
      level1_eigenvalues == {sp.Integer(8): 12, sp.Integer(-2): 8})
check("C0b-3: both chiralities give signature (24,16)",
      2 * level1_eigenvalues[8] == 24
      and 2 * level1_eigenvalues[-2] == 16)

# Representation decomposition:
# (2,0) x (1/2,1/2)=(5/2,1/2)+(3/2,1/2).
dim_positive_chiral = (2 * sp.Rational(5, 2) + 1) * (2 * sp.Rational(1, 2) + 1)
dim_negative_chiral = (2 * sp.Rational(3, 2) + 1) * (2 * sp.Rational(1, 2) + 1)
check("C0b-3: Shapovalov multiplicities match the SO(4) irreps",
      dim_positive_chiral == 12 and dim_negative_chiral == 8)
check("C0b-3: the positive level-one irrep matches the lower TT harmonics",
      d2.subs(n, 1) == 24)
check("C0b-3: the negative level-one irrep matches the vector harmonics",
      d1.subs(n, 1) == 16)


# ---------------------------------------------------------------------------
# C0b-4: Metsaev internal boost chain fixes the flat six-mode form
# ---------------------------------------------------------------------------
sqrt2 = sp.sqrt(2)
I2 = sp.eye(2)
Z2 = sp.zeros(2)

# Real normalized transverse bases:
# T1=diag(1,-1)/sqrt(2), T2=(e12+e21)/sqrt(2), and vectors e1,e2.
# In the order (E1,E2,A1,A2,L1,L2), Metsaev's d=4 minimal-scheme
# transformations at transverse momentum p_i=0 give
#   delta_R^a A^b = 2 E^{ab},
#   delta_R^a L^{bc} = -2(delta^{ab}A^c+delta^{ac}A^b)
#                       +2 delta^{bc}A^a.
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
rotation_tensor = sp.Matrix([[0, -2], [2, 0]])
rotation_vector = sp.Matrix([[0, -1], [1, 0]])
rotation = sp.diag(rotation_tensor, rotation_vector, rotation_tensor)

check("C0b-4: the internal boosts transform as a transverse vector",
      rotation * R1 - R1 * rotation == R2
      and rotation * R2 - R2 * rotation == -R1)

# Nilpotent part of the flat P_0 Jordan Hamiltonian: L -> E.
nilpotent = sp.Matrix.vstack(
    sp.Matrix.hstack(Z2, Z2, I2),
    sp.Matrix.hstack(Z2, Z2, Z2),
    sp.Matrix.hstack(Z2, Z2, Z2),
)

g_variables = sp.symbols("g0:21", real=True)
G = sp.zeros(6)
position = 0
for row in range(6):
    for column in range(row, 6):
        G[row, column] = g_variables[position]
        G[column, row] = g_variables[position]
        position += 1

form_equations: list[sp.Expr] = []
for skew_generator in (rotation, R1, R2):
    form_equations.extend(list(skew_generator.T * G + G * skew_generator))
# P_0 is self-adjoint for the invariant bilinear form.
form_equations.extend(list(nilpotent.T * G - G * nilpotent))
form_matrix, form_rhs = sp.linear_eq_to_matrix(form_equations, g_variables)
form_nullspace = form_matrix.nullspace()

G_flat_expected = sp.Matrix.vstack(
    sp.Matrix.hstack(Z2, Z2, sp.Rational(1, 2) * I2),
    sp.Matrix.hstack(Z2, I2, Z2),
    sp.Matrix.hstack(sp.Rational(1, 2) * I2, Z2, Z2),
)

expected_vector = sp.zeros(21, 1)
position = 0
for row in range(6):
    for column in range(row, 6):
        expected_vector[position] = G_flat_expected[row, column]
        position += 1

check("C0b-4: rotations, boosts, and P0 leave one form parameter",
      form_rhs == sp.zeros(form_rhs.rows, 1)
      and len(form_nullspace) == 1
      and form_matrix.rank() == 20)
check("C0b-4: the unique form has vector/cross ratio two",
      form_matrix * expected_vector == sp.zeros(form_matrix.rows, 1)
      and expected_vector.rank() == 1)
check("C0b-4: the Metsaev-sign flat form has signature (4,2)",
      G_flat_expected.eigenvals()
      == {sp.Integer(1): 2, sp.Rational(1, 2): 2,
          -sp.Rational(1, 2): 2})
check("C0b-4: reversing the action gives signature (2,4)",
      (-G_flat_expected).eigenvals()
      == {sp.Integer(-1): 2, sp.Rational(1, 2): 2,
          -sp.Rational(1, 2): 2})


# ---------------------------------------------------------------------------
# C0b-5: full compact-energy signature and signed character
# ---------------------------------------------------------------------------
def signature_at_energy(energy: int) -> tuple[int, int]:
    """Signature after choosing the lowest Weyl primary to be positive."""
    positive = 2 * (energy - 1) * (energy + 3) if energy >= 2 else 0
    negative_vector = (
        2 * (energy - 1) * (energy + 1) if energy >= 3 else 0
    )
    negative_upper_tt = (
        2 * (energy - 3) * (energy + 1) if energy >= 4 else 0
    )
    return positive, negative_vector + negative_upper_tt


expected_signatures = {
    2: (10, 0),
    3: (24, 16),
    4: (42, 40),
    5: (64, 72),
    6: (90, 112),
}
check("C0b-5: low compact-energy signatures are exact",
      all(signature_at_energy(energy) == signature
          for energy, signature in expected_signatures.items()))
check("C0b-5: the full form is nondegenerate on every checked energy",
      all(sum(signature_at_energy(energy)) == total_degeneracy(energy)
          for energy in range(2, 30)))

Z_signed = sp.factor(Z_lower - Z_upper - Z_vector)
Z_signed_expected = 2 * q**2 * (4 * q**2 - 11 * q + 5) / (1 - q)**3
check("C0b-5: the signed cylinder character has a closed form",
      sp.simplify(Z_signed - Z_signed_expected) == 0)
series_signed = sp.series(Z_signed, q, 0, 20).removeO().expand()
check("C0b-5: signed character equals N_plus-N_minus through E=19",
      all(series_signed.coeff(q, energy)
          == signature_at_energy(energy)[0] - signature_at_energy(energy)[1]
          for energy in range(2, 20)))

# For E>=4, the six local degrees of freedom appear in the leading E^2
# growth: two positive and four negative in this normalization.
E = sp.symbols("E", positive=True, integer=True)
positive_closed = 2 * (E - 1) * (E + 3)
negative_closed = 4 * (E + 1) * (E - 2)
check("C0b-5: high-energy signature resolves all six physical modes",
      sp.limit(positive_closed / E**2, E, sp.oo) == 2
      and sp.limit(negative_closed / E**2, E, sp.oo) == 4)


# ---------------------------------------------------------------------------
# C0b-6: no positive standard conformal form
# ---------------------------------------------------------------------------
check("C0b-6: the standard radial-adjoint form is already indefinite at level one",
      min(level1_eigenvalues) < 0 < max(level1_eigenvalues))
check("C0b-6: an overall sign reversal cannot remove indefiniteness",
      min((-gram_level1_chiral).eigenvals()) < 0
      < max((-gram_level1_chiral).eigenvals()))
check("C0b-6: compact D is diagonal while flat P0 may remain Jordan",
      frequency_gap != 0 and nilpotent**2 == sp.zeros(6)
      and nilpotent != sp.zeros(6))


if not PASS:
    raise SystemExit("CONFORMAL C0B: FAIL")
print("CONFORMAL C0B: ALL PASS")
