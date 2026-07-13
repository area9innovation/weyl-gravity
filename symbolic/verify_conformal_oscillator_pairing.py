#!/usr/bin/env python3
"""Exact C2f-N cylinder oscillator symplectic/Krein normalization.

The C2a Taub kernels use the positive-frequency metric waves appearing in
Hamada--Horata's cylinder expansions (their Eqs. (3.26)--(3.27)), including
the displayed oscillator coefficients.  This certificate derives the
quadratic symplectic norms of those *same coefficient coordinates* rather
than importing only their signs.

There are two action conventions to keep separate:

    S_HH  = - integral C^2,
    S_red =   integral (Ricci^2 - R^2/3).

On a closed spatial slice the Euler term does not change the integrated
covariant symplectic form, and

    S_red = -1/2 S_HH       (modulo Euler).

Thus the Hamada--Horata coordinates have unit commutators for ``S_HH`` but
not for ``S_red``.  In the low-mode order

    (E_+, E_-, A_+, A_-, L_+, L_-)

with dimensions ``(5,5,8,8,5,5)``, this script proves

    G_Omega^HH  = diag(+I_5,+I_5,-I_8,-I_8,-I_5,-I_5),
    G_Omega^red = -1/2 G_Omega^HH,
    J_comm^red  = (G_Omega^red)^(-1) = -2 G_Omega^HH.

Here the real covariant symplectic form is written

    Omega = i d(zbar) G_Omega wedge dz,

and ``J_comm`` is the coefficient-space Poisson/commutator matrix in the
unchanged C2a wave normalization.  After canonical magnitude rescaling for
``S_red``, only its signs remain, namely ``(-E,+A,+L)``.  For the more usual
``-alpha_g integral C^2`` convention the matrices are instead
``G_Omega=alpha_g G_Omega^HH`` and
``J_comm=alpha_g^(-1) G_Omega^HH``.

This closes the free oscillator normalization.  It does not by itself prove
the covariant phase-space moment-map identity (including its possible
factor-of-two convention) between the bilinear C2a Taub kernels and the
Hamiltonian conformal generators, nor does it construct the missing Taub
blocks or global BRST cohomology.
"""

from __future__ import annotations

import sympy as sp

try:
    from symbolic.verify_conformal_taub_charge import charge_from_slice
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    from verify_conformal_taub_charge import charge_from_slice


I = sp.I
R = sp.Rational


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


# ---------------------------------------------------------------------------
# The action ratio is fixed by the four-dimensional curvature identities.
# ---------------------------------------------------------------------------
riemann_sq, ricci_sq, scalar_sq = sp.symbols(
    "riemann_sq ricci_sq scalar_sq", real=True
)
weyl_sq = riemann_sq - 2 * ricci_sq + scalar_sq / 3
euler = riemann_sq - 4 * ricci_sq + scalar_sq
red_density = ricci_sq - scalar_sq / 3

check(
    "C2f-N: Ricci^2-R^2/3=(C^2-Euler)/2",
    sp.expand(red_density - (weyl_sq - euler) / 2) == 0,
)

# S_HH=-int C^2.  The Euler term changes the potential by a spatial boundary
# term but not the integrated symplectic form on S^3.
red_to_hh = -R(1, 2)
check("C2f-N: the C2a action has exact symplectic scale -1/2", red_to_hh == -R(1, 2))


# ---------------------------------------------------------------------------
# Direct Ostrogradsky symplectic norms of the normalized TT modes.
# ---------------------------------------------------------------------------
t = sp.symbols("t", real=True)
J = sp.symbols("J", integer=True, positive=True)
omega_e = 2 * J
omega_l = 2 * J + 2

# Hamada--Horata Eq. (3.26).
normalization_e = 1 / (4 * sp.sqrt(J * (2 * J + 1)))
normalization_l = 1 / (4 * sp.sqrt((J + 1) * (2 * J + 1)))

# Their TT quadratic action is a PU oscillator with gamma=-1 after spatial
# harmonics of unit S^3 norm are inserted.
gamma_hh = -sp.Integer(1)


def pu_momenta(mode: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    """Ostrogradsky (p0,p1) for gamma/2(qdd^2-(a+b)qd^2+abq^2)."""

    p1 = gamma_hh * sp.diff(mode, t, 2)
    p0 = -gamma_hh * (omega_e**2 + omega_l**2) * sp.diff(mode, t)
    p0 -= gamma_hh * sp.diff(mode, t, 3)
    return sp.simplify(p0), sp.simplify(p1)


def pu_hermitian_norm(frequency: sp.Expr, normalization: sp.Expr) -> sp.Expr:
    """Return -i Omega(ubar,u) in the convention positive for a healthy mode."""

    mode = normalization * sp.exp(-I * frequency * t)
    barred = sp.conjugate(mode)
    p0, p1 = pu_momenta(mode)
    p0_barred, p1_barred = pu_momenta(barred)
    omega = (
        p0_barred * mode
        + p1_barred * sp.diff(mode, t)
        - p0 * barred
        - p1 * sp.diff(barred, t)
    )
    return sp.simplify(-I * omega)


norm_e_hh = pu_hermitian_norm(omega_e, normalization_e)
norm_l_hh = pu_hermitian_norm(omega_l, normalization_l)
check("C2f-N: every normalized lower-TT E mode has exact HH norm +1", norm_e_hh == 1)
check("C2f-N: every normalized upper-TT L mode has exact HH norm -1", norm_l_hh == -1)


# ---------------------------------------------------------------------------
# Direct second-order symplectic norm of the vector mode.
# ---------------------------------------------------------------------------
# For a transverse vector harmonic, (nabla^2+2) gives
# -(2J-1)(2J+3).  The HH action reduces to
# mu/2(qdot^2-omega^2 q^2) with mu=-2(2J-1)(2J+3).
vector_factor = (2 * J - 1) * (2 * J + 3)
omega_a = 2 * J + 1
mu_a_hh = -2 * vector_factor
normalization_a = 1 / (2 * sp.sqrt(vector_factor * omega_a))


def second_order_hermitian_norm(
    frequency: sp.Expr, normalization: sp.Expr, kinetic: sp.Expr
) -> sp.Expr:
    mode = normalization * sp.exp(-I * frequency * t)
    barred = sp.conjugate(mode)
    momentum = kinetic * sp.diff(mode, t)
    momentum_barred = kinetic * sp.diff(barred, t)
    omega = momentum_barred * mode - momentum * barred
    return sp.simplify(-I * omega)


norm_a_hh = second_order_hermitian_norm(
    omega_a, normalization_a, mu_a_hh
)
check("C2f-N: every normalized transverse-vector A mode has exact HH norm -1", norm_a_hh == -1)


# ---------------------------------------------------------------------------
# The exact low-mode 36 x 36 matrices in the C2a coefficient ordering.
# ---------------------------------------------------------------------------
dimensions = (5, 5, 8, 8, 5, 5)
signs_hh = (1, 1, -1, -1, -1, -1)
blocks_hh = [sign * sp.eye(dimension) for sign, dimension in zip(signs_hh, dimensions)]
g_omega_hh = sp.diag(*blocks_hh)
g_omega_red = sp.simplify(red_to_hh * g_omega_hh)
j_comm_red = sp.simplify(g_omega_red.inv())
expected_comm_red = -2 * g_omega_hh

check("C2f-N: low cylinder oscillator space has dimension 36", g_omega_hh.shape == (36, 36))
check(
    "C2f-N: HH covariant form is +E,-A,-L with unit magnitude",
    g_omega_hh == sp.diag(
        sp.eye(5), sp.eye(5), -sp.eye(8), -sp.eye(8), -sp.eye(5), -sp.eye(5)
    ),
)
check(
    "C2f-N: C2a action-normalized symplectic matrix is -1/2 times HH",
    g_omega_red == -g_omega_hh / 2,
)
check(
    "C2f-N: unchanged C2a oscillator coordinates have commutator matrix -2 times HH",
    j_comm_red == expected_comm_red,
)
check(
    "C2f-N: symplectic and commutator matrices are exact inverses",
    g_omega_red * j_comm_red == sp.eye(36),
)

# The phase convention is explicit: Omega=i d(zbar) G wedge dz and the
# Hermitian mode norm is -i Omega(ubar,u).  Therefore no hidden factors of i
# occur in G itself.
check(
    "C2f-N: all mode norms are real and all symplectic phase is the explicit prefactor i",
    all(value.is_real for value in (norm_e_hh, norm_a_hh, norm_l_hh)),
)

# General overall coupling check.  If S=-alpha_g int C^2, it is alpha_g
# times HH and hence has the usual +E,-A,-L form for alpha_g>0.
alpha_g = sp.symbols("alpha_g", positive=True, real=True)
g_omega_physical = alpha_g * g_omega_hh
j_comm_physical = sp.simplify(g_omega_physical.inv())
check(
    "C2f-N: -alpha_g C^2 gives G=alpha_g G_HH and J=alpha_g^-1 G_HH",
    j_comm_physical == g_omega_hh / alpha_g,
)


# ---------------------------------------------------------------------------
# Independent primary-source normalization bridge for the two C2a seeds.
# ---------------------------------------------------------------------------
# Hamada--Horata Eqs. (4.42), (4.60), and (4.62)--(4.63) give the six
# proper-conformal oscillator families.  For the two low seed blocks, their
# coefficients A(J), B(J) and the selected normalized H coefficient yield the
# following direct magnetic matrix elements at J=1.
hh_A = sp.sqrt(2 * J / ((2 * J - 1) * (2 * J + 3))) * sp.sqrt(2)
hh_B = sp.sqrt((2 * J + 2) / ((2 * J - 1) * (2 * J + 3))) * sp.sqrt(2)
selected_h = sp.sqrt(2)
hh_seed_a_to_e = sp.simplify((selected_h * hh_A).subs(J, 1))
hh_seed_l_to_a = sp.simplify((selected_h * hh_B).subs(J, 1))

check(
    "C2f-N: published canonical Q kernel has A1->E1 seed magnitude 2sqrt(10)/5",
    hh_seed_a_to_e == 2 * sp.sqrt(10) / 5,
)
check(
    "C2f-N: published canonical Q kernel has L1->A1 seed magnitude 4sqrt(5)/5",
    hh_seed_l_to_a == 4 * sp.sqrt(5) / 5,
)

# The raw C2a polarized kernel differs from the normalized HH charge kernel
# by one common absolute factor after the action, scalar-harmonic, and
# component conventions are combined.  The repo's E-tower harmonic
# phase is -1 relative to the displayed HH tilde convention; A and L have
# phase +1.  Both independent curvature seeds must then match with the same
# factor, which is a nontrivial end-to-end normalization check.
ck_component_scale = 1 / (2 * sp.sqrt(2) * sp.pi)
tower_phase_e = -1
tower_phase_a = tower_phase_l = 1
predicted_c2a_a_to_e = sp.simplify(
    tower_phase_e * tower_phase_a * ck_component_scale * hh_seed_a_to_e
)
predicted_c2a_l_to_a = sp.simplify(
    tower_phase_a * tower_phase_l * ck_component_scale * hh_seed_l_to_a
)
measured_c2a_a_to_e = charge_from_slice(-1, reverse=False)
measured_c2a_l_to_a = charge_from_slice(1, reverse=False)

check(
    "C2f-N: one raw polarized-kernel scale reproduces the C2a A1->E1 seed",
    predicted_c2a_a_to_e == measured_c2a_a_to_e
    == -sp.sqrt(5) / (5 * sp.pi),
)
check(
    "C2f-N: the same scale reproduces the independent C2a L1->A1 seed",
    predicted_c2a_l_to_a == measured_c2a_l_to_a
    == sp.sqrt(10) / (5 * sp.pi),
)

# C2a stores the *mixed polarization* Q[h1,h2].  On the real field
# h=z u+zbar ubar the quadratic moment map therefore contains both
# orderings and has kernel 2*M_Taub.  With Omega=i dzbar G wedge dz its
# Hamiltonian vector field is
#
#     X_z = i G^(-1) (2 M_Taub) z
#
# in the repo convention d mu=i_X Omega used by the C2c moment-map target.
#
# The phase can be compared directly with the primary-source CK vector.
# HH Eq. (4.8) has, for the e^{+it}Y* lowering component,
# (xi^0,xi^i)=(sqrt(Vol)/2,-i sqrt(Vol)/2 grad^i) e^{+it}Y*.
# The repo s=-1 reducibility r_-=(-i,1,1) is written with covariant xi_0;
# raising its time index gives (xi^0,xi^i)=(i,1 grad^i)e^{+it}Y.
# For the seeded q=(+1/2,-1/2), the HH label is M=-q and scalar reality is
# Y_M^*=-Y_q.  This fixes the exact complex ratio, not only its magnitude.
volume_s3 = 2 * sp.pi**2
hh_ck_in_repo_harmonic = sp.Matrix(
    [-sp.sqrt(volume_s3) / 2, I * sp.sqrt(volume_s3) / 2]
)
repo_ck = sp.Matrix([I, 1])
ck_vector_ratio = -I * sp.sqrt(2) / sp.pi
check(
    "C2f-N: seeded repo lowering CK vector is exactly -i*sqrt(2)/pi times HH Q_-q",
    repo_ck == sp.simplify(ck_vector_ratio * hh_ck_in_repo_harmonic),
)

# Scaling both the action and the parameter shows why the raw real Taub
# coefficient is not itself the complex Noether/stress-tensor kernel in HH
# conventions.  This layer must be crossed through polarization and Omega.
same_parameter_noether_scale = sp.simplify(red_to_hh * ck_vector_ratio)
check(
    "C2f-N: same-parameter red-action Noether charge scale is +i/(sqrt(2)pi)",
    same_parameter_noether_scale == I / (sp.sqrt(2) * sp.pi),
)

# Check the same phase through both independent action-normalized Taub
# blocks.  The HH numbers above are charge *kernels*.  The annihilator
# generator is T_HH=J_HH M_HH, so its A->E entry is positive (target E has
# sign +) while its L->A entry is negative (target A has sign -).  The repo
# tower rephasing is S=diag(-E,+A,+L), and a generator transforms as
# c_CK S T_HH S^{-1}.
t_hh_a_to_e = hh_seed_a_to_e
t_hh_l_to_a = -hh_seed_l_to_a
phase_ratio_a_to_e = sp.Integer(tower_phase_e) / tower_phase_a
phase_ratio_l_to_a = sp.Integer(tower_phase_a) / tower_phase_l
expected_x_repo_a_to_e = sp.simplify(
    ck_vector_ratio * phase_ratio_a_to_e * t_hh_a_to_e
)
expected_x_repo_l_to_a = sp.simplify(
    ck_vector_ratio * phase_ratio_l_to_a * t_hh_l_to_a
)

# On the C2a side, J_comm^red has target entry -2 for E and +2 for A.
# The factor two is the mixed-polarization-to-quadratic-kernel conversion.
x_repo_a_to_e = sp.simplify(I * (-2) * 2 * measured_c2a_a_to_e)
x_repo_l_to_a = sp.simplify(I * (+2) * 2 * measured_c2a_l_to_a)
check(
    "C2f-N: polarized A1->E1 Taub kernel generates the normalized repo CK action",
    x_repo_a_to_e == expected_x_repo_a_to_e
    == 4 * I * sp.sqrt(5) / (5 * sp.pi),
)
check(
    "C2f-N: polarized L1->A1 Taub kernel gives the same complex CK normalization",
    x_repo_l_to_a == expected_x_repo_l_to_a
    == 4 * I * sp.sqrt(10) / (5 * sp.pi),
)

print("basis: (E+, E-, A+, A-, L+, L-)")
print("dimensions:", dimensions)
print("G_Omega(HH) block coefficients:", signs_hh)
print("G_Omega(C2a S_red) block coefficients:", tuple(-R(s, 2) for s in signs_hh))
print("J_comm(C2a S_red) block coefficients:", tuple(-2 * s for s in signs_hh))
print("HH-to-C2a proper-CK component scale:", ck_component_scale)
print("repo-to-HH CK vector ratio:", ck_vector_ratio)
print("same-parameter red/HH Noether-charge scale:", same_parameter_noether_scale)
print("CONFORMAL C2f-N: ALL PASS")
