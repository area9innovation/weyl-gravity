#!/usr/bin/env python3
"""Exact C1a reduction of the first conformal-gravity interaction test.

This certificate does not claim to compute a new Weyl-gravity vertex.  It
fixes the arena, enumerates the first complete compact-energy Fock shells,
applies the exact Einstein-subsector selection rule, and identifies the
smallest matrix element which a new cylinder calculation must determine.

There are two distinct free generators in play:

* flat time translation P_0 has a rank-two Jordan block and the C0c metric
  deformation map has a two-real-dimensional cokernel;
* compact cylinder time translation D is diagonal.  On a fixed D-energy
  shell the deformation commutator is identically zero, so the whole
  anti-Hermitian shell source is the cokernel.

The two complexes cannot be mixed.  In particular, a flat growing-mode
"amplitude" contains derivatives of the momentum-conserving delta function
and is not a Hamiltonian-normalized cylinder matrix element.

Checks
------
C1a-1  Reproduce the two flat-Jordan obstruction coordinates
        O_1=2 Im(V_LE), O_2=Im tr(V), and prove that P_0 changes compact
        energy whereas the fixed-D-shell deformation map vanishes.
C1a-2  Enumerate the complete one-particle and bosonic Fock shells at
        compact energies four, five, and six, including their inherited
        Shapovalov signatures.
C1a-3  Apply A(E,E,X)=0.  The E=4 cubic shell vanishes.  At E=5 the only
        possibly nonzero block joins two negative sectors.  At E=6 the
        first possible opposite-sign block is A_3 A_3 -> X_6.
C1a-4  Verify the published finite EAA three-point coefficient on an exact
        complex spinor-helicity point and the SO(4) channels which place it
        at E=5.  At E=6, SO(4) excludes A_3 A_3 -> A_6 but permits
        A_3 A_3 -> L_6.
C1a-5  Show algebraically why a nonzero equal-sign EAA block is compatible
        with fixed-J pseudo-Hermiticity.  A nonzero opposite-sign block can
        also preserve J, but then its reduced off-diagonal matrix is
        ordinary anti-Hermitian and can split a degenerate pair into complex
        conjugates.  The actual AAL coefficient remains to be computed.
C1a-6  An analytic deformation based at the fixed indefinite J cannot
        become positive even when its deformation source vanishes: inertia
        is locally constant.

Sources for the inputs encoded here are arXiv:1406.3542 (cylinder towers),
arXiv:1805.00394, especially Eqs. (2.8) and (4.5) (flat scattering states),
arXiv:0707.4437 (ordinary-derivative conformal fields), and arXiv:2202.08298
(BRST cohomology and indefinite completeness).
"""

from __future__ import annotations

from math import comb

import sympy as sp


PASS = True


def check(label: str, condition: object) -> None:
    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


def dagger(matrix: sp.Matrix) -> sp.Matrix:
    return matrix.conjugate().T


def sym_power_dimension(dimension: int, particle_number: int) -> int:
    return comb(dimension + particle_number - 1, particle_number)


# ---------------------------------------------------------------------------
# C1a-1: flat P_0 Jordan cokernel versus a compact D-energy shell
# ---------------------------------------------------------------------------
I = sp.I
N = sp.Matrix([[0, 1], [0, 0]])
J_flat = sp.Matrix([[0, 1], [1, 0]])

x, u, v, y = sp.symbols("x u v y", real=True)
G1 = sp.Matrix([[x, u + I * v], [u - I * v, y]])
flat_image = sp.simplify(N.T * G1 - G1 * N)
check(
    "C1a-1: flat Jordan metric-deformation image is exact",
    flat_image == sp.Matrix([[0, -x], [x, 2 * I * v]]),
)

a_r, a_i, b_r, b_i = sp.symbols("a_r a_i b_r b_i", real=True)
c_r, c_i, d_r, d_i = sp.symbols("c_r c_i d_r d_i", real=True)
a = a_r + I * a_i
b = b_r + I * b_i
c = c_r + I * c_i
d = d_r + I * d_i
V_flat = sp.Matrix([[a, b], [c, d]])
S_flat = sp.simplify(J_flat * V_flat - dagger(V_flat) * J_flat)
O1 = sp.simplify(-I * S_flat[0, 0])
O2 = sp.simplify(sp.im(S_flat[0, 1]))

check("C1a-1: O1 is twice Im(V_LE)", O1 == 2 * c_i)
check("C1a-1: O2 is Im tr(V)", O2 == a_i + d_i)
flat_solution = sp.solve(
    list(flat_image - S_flat),
    (x, v, c_i, d_i),
    dict=True,
)
check(
    "C1a-1: flat equation is soluble iff O1=O2=0",
    flat_solution
    == [{c_i: 0, d_i: -a_i, v: b_i, x: a_r - d_r}],
)

# In radial quantization [D,P_mu]=P_mu up to the sign convention for which
# matrix acts on columns.  This two-level truncation makes the key point:
# P_0 does not act within one compact-energy eigenspace.
Delta = sp.symbols("Delta", real=True)
D_two_levels = sp.diag(Delta, Delta + 1)
check(
    "C1a-1: the flat nilpotent changes compact energy",
    D_two_levels * N - N * D_two_levels == -N,
)

energy = sp.symbols("energy", real=True)
D_shell = energy * sp.eye(2)
cylinder_image = sp.simplify(dagger(D_shell) * G1 - G1 * D_shell)
check(
    "C1a-1: fixed compact-energy deformation map is zero",
    cylinder_image == sp.zeros(2),
)
check(
    "C1a-1: flat and cylinder cokernels are not the same complex",
    flat_image != cylinder_image,
)


# ---------------------------------------------------------------------------
# C1a-2: exact compact-energy one-particle and Fock-shell content
# ---------------------------------------------------------------------------
def lower_tt(energy_value: int) -> int:
    return 2 * (energy_value - 1) * (energy_value + 3) if energy_value >= 2 else 0


def vector(energy_value: int) -> int:
    return 2 * (energy_value - 1) * (energy_value + 1) if energy_value >= 3 else 0


def upper_tt(energy_value: int) -> int:
    return 2 * (energy_value - 3) * (energy_value + 1) if energy_value >= 4 else 0


def one_particle_signature(energy_value: int) -> tuple[int, int]:
    # Overall convention: the Delta=2 Weyl primary is positive.
    return lower_tt(energy_value), vector(energy_value) + upper_tt(energy_value)


check(
    "C1a-2: one-particle signatures at E=2,...,6 are exact",
    [one_particle_signature(level) for level in range(2, 7)]
    == [(10, 0), (24, 16), (42, 40), (64, 72), (90, 112)],
)

# E=4: H_1(E=4) plus Sym^2 H_1(E=2).
e4_one = sum(one_particle_signature(4))
e4_two = sym_power_dimension(10, 2)
check(
    "C1a-2: complete E=4 Fock shell has 82+55=137 states",
    (e4_one, e4_two, e4_one + e4_two) == (82, 55, 137),
)

# E=5: H_1(E=5) plus H_1(E=2) tensor H_1(E=3).
e5_one_positive, e5_one_negative = one_particle_signature(5)
e5_two_positive = 10 * 24
e5_two_negative = 10 * 16
check(
    "C1a-2: complete E=5 shell signature sectors are exact",
    (
        e5_one_positive,
        e5_one_negative,
        e5_two_positive,
        e5_two_negative,
        e5_one_positive + e5_one_negative
        + e5_two_positive + e5_two_negative,
    )
    == (64, 72, 240, 160, 536),
)

# E=6 partitions: 6; 2+4; 3+3; and 2+2+2.
e6_one_positive, e6_one_negative = one_particle_signature(6)
e6_24_positive = 10 * 42
e6_24_negative = 10 * 40
e6_33_positive = sym_power_dimension(24, 2) + sym_power_dimension(16, 2)
e6_33_negative = 24 * 16
e6_222_positive = sym_power_dimension(10, 3)
e6_total_positive = (
    e6_one_positive + e6_24_positive + e6_33_positive + e6_222_positive
)
e6_total_negative = e6_one_negative + e6_24_negative + e6_33_negative
check(
    "C1a-2: complete E=6 Fock shell partitions are exact",
    (
        e6_one_positive + e6_one_negative,
        e6_24_positive + e6_24_negative,
        e6_33_positive + e6_33_negative,
        e6_222_positive,
    )
    == (202, 820, 820, 220),
)
check(
    "C1a-2: complete E=6 Fock-shell signature is (1166,896)",
    (e6_total_positive, e6_total_negative) == (1166, 896)
    and e6_total_positive + e6_total_negative == 2062,
)


# ---------------------------------------------------------------------------
# C1a-3: exact Einstein-subsector sparsity
# ---------------------------------------------------------------------------
def killed_by_einstein_selection(fields: tuple[str, str, str]) -> bool:
    """A(E,E,X)=0, including X=E, for the exact Einstein subsector."""
    return sum(field != "E" for field in fields) <= 1


# One E=4 state couples at cubic order only to two E=2 Einstein states.
check(
    "C1a-3: every E=4 one-to-two cubic matrix element vanishes",
    killed_by_einstein_selection(("E", "E", "E"))
    and killed_by_einstein_selection(("X", "E", "E")),
)

# At E=5, pairs are EE (positive) or EA (negative), while one-particle
# states are E (positive) or X=(A or L) (negative).
e5_channels = [
    ("E<-EE", ("E", "E", "E"), +1, +1),
    ("X<-EE", ("X", "E", "E"), -1, +1),
    ("E<-EA", ("E", "E", "A"), +1, -1),
    ("X<-EA", ("X", "E", "A"), -1, -1),
]
e5_survivors = [
    (name, one_sign, two_sign)
    for name, fields, one_sign, two_sign in e5_channels
    if not killed_by_einstein_selection(fields)
]
check(
    "C1a-3: only an equal-negative-sign E=5 cubic block survives",
    e5_survivors == [("X<-EA", -1, -1)],
)

# The same reasoning removes every opposite-sign channel in the 2+4
# partition at E=6.  For 3+3, only X<-AA can change the sign.
e6_33_channels = [
    ("E<-EE", ("E", "E", "E"), +1, +1),
    ("X<-EE", ("X", "E", "E"), -1, +1),
    ("E<-EA", ("E", "E", "A"), +1, -1),
    ("X<-EA", ("X", "E", "A"), -1, -1),
    ("E<-AA", ("E", "A", "A"), +1, +1),
    ("X<-AA", ("X", "A", "A"), -1, +1),
]
e6_33_survivors = [
    (name, one_sign, two_sign)
    for name, fields, one_sign, two_sign in e6_33_channels
    if not killed_by_einstein_selection(fields)
]
check(
    "C1a-3: first selection-allowed opposite-sign block is X6<-A3 A3",
    e6_33_survivors
    == [("X<-EA", -1, -1), ("E<-AA", +1, +1), ("X<-AA", -1, +1)],
)

# The only E=6 two-to-three spectator block would contain the already-zero
# E=4 transition E4 <-> E2 E2.
check(
    "C1a-3: the E=6 two-to-three spectator block inherits the E=4 zero",
    killed_by_einstein_selection(("X", "E", "E")),
)


# ---------------------------------------------------------------------------
# C1a-4: finite EAA seed and SO(4) channel selection
# ---------------------------------------------------------------------------
def square(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.expand(left[0] * right[1] - left[1] * right[0])


lam = sp.Matrix([1, 0])
tilde_1 = sp.Matrix([1, 0])
tilde_2 = sp.Matrix([0, 1])
tilde_3 = sp.Matrix([-1, -1])
momenta = [lam * spinor.T for spinor in (tilde_1, tilde_2, tilde_3)]
bracket_12 = square(tilde_1, tilde_2)
bracket_23 = square(tilde_2, tilde_3)
bracket_31 = square(tilde_3, tilde_1)
eaa_coefficient = sp.simplify(bracket_23**4 / bracket_12**2)

check(
    "C1a-4: exact complex three-point momenta sum to zero",
    sum(momenta, sp.zeros(2)) == sp.zeros(2),
)
check(
    "C1a-4: all three nonzero square brackets equal one",
    (bracket_12, bracket_23, bracket_31) == (1, 1, 1),
)
check(
    "C1a-4: published stripped EAA coefficient is nonzero and equals one",
    eaa_coefficient == 1,
)


def irrep_dimension(twice_left_spin: int, twice_right_spin: int) -> int:
    return (twice_left_spin + 1) * (twice_right_spin + 1)


def tensor_product_contains(spin_a: int, spin_b: int, target: int) -> bool:
    """SU(2) tensor-product test using twice-spin nonnegative integers."""
    return (
        abs(spin_a - spin_b) <= target <= spin_a + spin_b
        and (spin_a + spin_b - target) % 2 == 0
    )


def so4_product_contains(
    rep_a: tuple[int, int], rep_b: tuple[int, int], target: tuple[int, int]
) -> bool:
    return tensor_product_contains(rep_a[0], rep_b[0], target[0]) and tensor_product_contains(
        rep_a[1], rep_b[1], target[1]
    )


def symmetric_identical_channel(
    source: tuple[int, int], target: tuple[int, int]
) -> bool:
    if not so4_product_contains(source, source, target):
        return False
    # Exchange parity in j tensor j -> J is (-1)^(2j-J) for each SU(2).
    exponent = source[0] + source[1] - (target[0] + target[1]) // 2
    return exponent % 2 == 0


# Twice-spin labels.  Tensor harmonics have (n+4,n)+(n,n+4), and
# transverse-vector harmonics have (n+2,n)+(n,n+2).
E2_chiral = (0, 4)
A3_chiral = (3, 1)
A5_chiral = (3, 5)
L6_chiral = (6, 2)
A6_chiralities = ((6, 4), (4, 6))
A3_chiralities = ((3, 1), (1, 3))

check(
    "C1a-4: SO(4) dimensions reproduce E2, A3, A5, and L6 towers",
    (
        2 * irrep_dimension(4, 0),
        2 * irrep_dimension(3, 1),
        2 * irrep_dimension(5, 3),
        2 * irrep_dimension(6, 2),
    )
    == (10, 16, 48, 42),
)
check(
    "C1a-4: E2 tensor A3 contains the observed A5 EAA channel",
    so4_product_contains(E2_chiral, A3_chiral, A5_chiral),
)
check(
    "C1a-4: symmetric A3 A3 contains the upper-TT L6 channel",
    symmetric_identical_channel(A3_chiral, L6_chiral),
)
check(
    "C1a-4: A3 A3 cannot produce an A6 vector harmonic",
    not any(
        so4_product_contains(left, right, target)
        for left in A3_chiralities
        for right in A3_chiralities
        for target in A6_chiralities
    ),
)


# ---------------------------------------------------------------------------
# C1a-5: pseudo-Hermiticity versus positivity
# ---------------------------------------------------------------------------
z_r, z_i = sp.symbols("z_r z_i", real=True)
z = z_r + I * z_i

# Representative order: one E+, one X-, two EE+, two EA-.  The only E=5
# block left by the selection theorem joins the two negative entries.
J_e5 = sp.diag(1, -1, 1, -1)
V_e5 = sp.zeros(4)
V_e5[1, 3] = z
V_e5[3, 1] = sp.conjugate(z)
S_e5 = sp.simplify(J_e5 * V_e5 - dagger(V_e5) * J_e5)
check("C1a-5: the nonzero EAA block can be ordinarily Hermitian", dagger(V_e5) == V_e5)
check(
    "C1a-5: the equal-sign EAA block has zero fixed-J source",
    S_e5 == sp.zeros(4),
)
check(
    "C1a-5: zero pseudo-Hermiticity source does not make J positive",
    (sp.Matrix([0, 1, 0, 0]).T * J_e5 * sp.Matrix([0, 1, 0, 0]))[0] == -1,
)

# A reduced opposite-sign block can preserve J only with the compensating
# relative sign.  If the two free levels are exactly degenerate, this simple
# block has a complex-conjugate eigenvalue pair.  The full E=6 matrix may
# contain additional diagonal/multiplicity structure, so this is a target
# diagnostic rather than a claim about Weyl gravity.
J_opposite = sp.diag(1, -1)
V_opposite = sp.Matrix([[0, z], [-sp.conjugate(z), 0]])
spectral_parameter = sp.symbols("lambda")
check(
    "C1a-5: an opposite-sign block can still preserve fixed J",
    J_opposite * V_opposite - dagger(V_opposite) * J_opposite == sp.zeros(2),
)
check(
    "C1a-5: its degenerate reduced characteristic polynomial is lambda^2+|z|^2",
    sp.factor((spectral_parameter * sp.eye(2) - V_opposite).det())
    == spectral_parameter**2 + z_i**2 + z_r**2,
)


# ---------------------------------------------------------------------------
# C1a-6: analytic deformations cannot change the free inertia
# ---------------------------------------------------------------------------
g = sp.symbols("g", real=True)
p, q, r, s = sp.symbols("p q r s", real=True)
G1_arbitrary = sp.Matrix([[p, q + I * r], [q - I * r, s]])
negative_vector = sp.Matrix([1, -1]) / sp.sqrt(2)
deformed_norm = sp.simplify(
    (dagger(negative_vector) * (J_flat + g * G1_arbitrary) * negative_vector)[0]
)
check(
    "C1a-6: a negative free direction stays negative near analytic g=0",
    sp.limit(deformed_norm, g, 0) == -1,
)


if not PASS:
    raise SystemExit("CONFORMAL C1A: FAIL")

print("CONFORMAL C1A: ALL PASS")
print("The flat P0 Jordan cokernel is not a fixed-D cylinder-shell cokernel.")
print("E=4 is cubic-protected; finite EAA first appears at E=5 within one sign.")
print("The first unresolved opposite-sign cylinder coefficient is A3 A3 <-> L6.")
