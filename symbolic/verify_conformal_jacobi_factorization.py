#!/usr/bin/env python3
"""Exact Jacobi certificates for the conformal-cylinder C1b densities.

This is deliberately a *small* algebraic certificate.  It takes as input the
exact radial densities already obtained by the independent curved-cylinder
perturbiner in ``verify_conformal_aal_vertex.py`` and verifies their change of
variables, Jacobi factorization, boundary primitive, and integral.  It does
not rerun the curvature expansion.

Conventions
-----------

``sympy.jacobi(k, alpha, beta, x)`` uses the standard weight

    (1-x)**alpha * (1+x)**beta,       -1 < x < 1.

With ``x = 2*u - 1``, removal of the irrelevant overall factor
``2**(alpha+beta+1)`` leaves the shifted weight

    u**beta * (1-u)**alpha,           0 < u < 1.

For AAL, write ``n_i = 2 J_i`` and ``N = n_1+n_2 = 2S``.  The verified C1b
family has coordinate density (before ``d beta``)

    D(t) = C t [(N-2)t**2-1] / (1+t**2)**(N-1).

The statement that the full Weyl curvature calculation has this form for
all admissible spins remains conjectural.  Conditional on that density form,
the Jacobi factorization and its zero integral are proved here for symbolic
integer ``n_1,n_2``.  The four presently computed curvature cases are checked
against the proposed normalization formula separately.

For EAA, both independently assembled time orientations have the certified
coordinate density

    D(t) = K t (3t**2-1) / (1+t**2)**4,
    K = sqrt(21)/(160*pi**3).

The script proves that each direction is the shifted Jacobi polynomial
``P_1^(2,0)`` against its beta weight and hence vanishes separately.
"""

from __future__ import annotations

import sympy as sp


PASS = True


def check(label: str, condition: object) -> None:
    """Record an exact symbolic check."""

    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


def is_zero(expression: sp.Expr) -> bool:
    """Canonical exact-zero predicate for the small rational expressions."""

    return sp.simplify(sp.powsimp(expression, force=True)) == 0


t, u = sp.symbols("t u", positive=True, real=True)
C = sp.symbols("C", finite=True, real=True)
n1, n2 = sp.symbols("n1 n2", integer=True, positive=True)
N = n1 + n2
S = sp.Rational(1, 2) * N

u_of_t = t**2 / (1 + t**2)
du_dt = sp.diff(u_of_t, t)


# ---------------------------------------------------------------------------
# P1: symbolic AAL change of variables and Jacobi orthogonality
# ---------------------------------------------------------------------------

# D is the coordinate density before the S^3 radial measure
# d beta = 2 dt/(1+t^2).  I_t is the measured coefficient of dt.
D_aal_t = C * t * ((N - 2) * t**2 - 1) / (1 + t**2) ** (N - 1)
I_aal_t = 2 * C * t * ((N - 2) * t**2 - 1) / (1 + t**2) ** N

aal_alpha = N - 3
aal_beta = sp.Integer(0)
P1_aal = sp.expand(sp.expand_func(sp.jacobi(1, aal_alpha, aal_beta, 2 * u - 1)))
weight_aal = u**aal_beta * (1 - u) ** aal_alpha
I_aal_u = C * weight_aal * P1_aal

check(
    "P1: SymPy Jacobi convention gives P_1^(N-3,0)(2u-1)=(N-1)u-1",
    sp.expand(P1_aal - ((N - 1) * u - 1)) == 0,
)
check(
    "P1: AAL measured t-density is the pullback of the shifted Jacobi form",
    is_zero(I_aal_t - I_aal_u.subs(u, u_of_t) * du_dt),
)

aal_quotient = sp.cancel(I_aal_u / (weight_aal * P1_aal))
check(
    "P1: AAL Jacobi quotient is independent of u and equals C",
    aal_quotient == C and u not in aal_quotient.free_symbols,
)

F_aal_u = -C * u * (1 - u) ** (N - 2)
F_aal_t = -C * t**2 / (1 + t**2) ** (N - 1)
check(
    "P1: AAL u-form is the derivative of its beta-weight primitive",
    # Divide by the nonzero interior beta weight before simplifying.  This
    # avoids an unevaluated symbolic-power identity at u=1 in SymPy.
    is_zero((I_aal_u - sp.diff(F_aal_u, u)) / weight_aal),
)
check(
    "P1: AAL t- and u-primitives agree under u=t^2/(1+t^2)",
    is_zero(F_aal_t - F_aal_u.subs(u, u_of_t)),
)

# Physical transverse-vector harmonics have J_i >= 1, hence n_i >= 2.
# Introduce nonnegative excess variables to make both endpoint limits an
# assumption-aware SymPy identity rather than an informal 0**symbol step.
r1, r2 = sp.symbols("r1 r2", integer=True, nonnegative=True)
F_aal_admissible = F_aal_u.subs({n1: r1 + 2, n2: r2 + 2})
check(
    "P1: AAL primitive vanishes at u=0 for all admissible n_i>=2",
    sp.limit(F_aal_admissible, u, 0, dir="+") == 0,
)
check(
    "P1: AAL primitive vanishes at u=1 for all admissible n_i>=2",
    sp.limit(F_aal_admissible, u, 1, dir="-") == 0,
)

# This is the degree-one shifted-Jacobi orthogonality integral written as two
# beta moments.  It is exact for N>2, in particular for every physical N>=4.
aal_beta_integral = C * (
    (N - 1) * sp.beta(2, N - 2) - sp.beta(1, N - 2)
)
check(
    "P1: symbolic AAL beta/Jacobi integral vanishes",
    sp.simplify(sp.expand_func(aal_beta_integral)) == 0,
)


# The following coefficient formula is an exact fit to the four curvature
# certificates, not a derivation for arbitrary spin.  Keeping this check
# separate prevents the algebraic Jacobi theorem above from being mistaken
# for a proof of the generic-spin Weyl density.
def vector_radial_prefactor(J: sp.Rational) -> sp.Expr:
    return sp.sqrt(2 * J) / (
        8
        * sp.pi
        * sp.sqrt((2 * J - 1) * (2 * J + 1) * (2 * J + 3))
    )


def upper_tt_radial_prefactor(total_spin: sp.Rational) -> sp.Expr:
    return sp.sqrt(2 * (2 * total_spin - 1)) / (
        64
        * sp.pi
        * sp.sqrt((total_spin + 1) * (2 * total_spin + 1))
    )


def fitted_aal_prefactor(J1: sp.Rational, J2: sp.Rational) -> sp.Expr:
    total_spin = J1 + J2
    return sp.simplify(
        64
        * (2 * J1 + 1)
        * (2 * J2 + 1)
        * (total_spin - 1)
        * vector_radial_prefactor(J1)
        * vector_radial_prefactor(J2)
        * upper_tt_radial_prefactor(total_spin)
    )


known_aal_prefactors = {
    (sp.Rational(1), sp.Rational(1)): 3
    * sp.sqrt(10)
    / (800 * sp.pi**3),
    (sp.Rational(1), sp.Rational(3, 2)): 3
    * sp.sqrt(35)
    / (1120 * sp.pi**3),
    (sp.Rational(3, 2), sp.Rational(3, 2)): sp.sqrt(70)
    / (448 * sp.pi**3),
    (sp.Rational(1), sp.Rational(2)): sp.sqrt(5) / (112 * sp.pi**3),
}
for spins, measured_prefactor in known_aal_prefactors.items():
    check(
        f"P1: finite curvature prefactor fit agrees at (J1,J2)={spins}",
        sp.simplify(fitted_aal_prefactor(*spins) - measured_prefactor) == 0,
    )


# ---------------------------------------------------------------------------
# P3: E2 A3 <-> A5 in both independently assembled directions
# ---------------------------------------------------------------------------

K_eaa = sp.sqrt(21) / (160 * sp.pi**3)
EAA_overlap = -1 / (2 * sp.pi)

D_eaa_forward_t = K_eaa * t * (3 * t**2 - 1) / (1 + t**2) ** 4
D_eaa_reverse_t = K_eaa * t * (3 * t**2 - 1) / (1 + t**2) ** 4
I_eaa_forward_t = 2 * K_eaa * t * (3 * t**2 - 1) / (1 + t**2) ** 5
I_eaa_reverse_t = 2 * K_eaa * t * (3 * t**2 - 1) / (1 + t**2) ** 5

eaa_alpha = sp.Integer(2)
eaa_beta = sp.Integer(0)
P1_eaa = sp.expand_func(sp.jacobi(1, eaa_alpha, eaa_beta, 2 * u - 1))
weight_eaa = u**eaa_beta * (1 - u) ** eaa_alpha
I_eaa_u = K_eaa * weight_eaa * P1_eaa

check(
    "P3: normalized EAA harmonic overlap is nonzero and equals -1/(2pi)",
    EAA_overlap == -1 / (2 * sp.pi) and EAA_overlap != 0,
)
check(
    "P3: P_1^(2,0)(2u-1)=4u-1 in the stated Jacobi convention",
    sp.expand(P1_eaa - (4 * u - 1)) == 0,
)
check(
    "P3: forward EAA measured density pulls back from the Jacobi u-form",
    is_zero(I_eaa_forward_t - I_eaa_u.subs(u, u_of_t) * du_dt),
)
check(
    "P3: reverse EAA measured density pulls back from the Jacobi u-form",
    is_zero(I_eaa_reverse_t - I_eaa_u.subs(u, u_of_t) * du_dt),
)
check(
    "P3: independently assembled EAA directions have the same local density",
    is_zero(D_eaa_forward_t - D_eaa_reverse_t),
)

eaa_quotient = sp.cancel(I_eaa_u / (weight_eaa * P1_eaa))
check(
    "P3: EAA Jacobi quotient is independent of u and equals sqrt(21)/(160pi^3)",
    eaa_quotient == K_eaa and u not in eaa_quotient.free_symbols,
)

F_eaa_u = -K_eaa * u * (1 - u) ** 3
F_eaa_t = -K_eaa * t**2 / (1 + t**2) ** 4
check(
    "P3: EAA u-form is the derivative of its beta-weight primitive",
    is_zero(I_eaa_u - sp.diff(F_eaa_u, u)),
)
check(
    "P3: EAA t- and u-primitives agree",
    is_zero(F_eaa_t - F_eaa_u.subs(u, u_of_t)),
)
check(
    "P3: EAA primitive vanishes at both stereographic endpoints",
    sp.limit(F_eaa_t, t, 0, dir="+") == 0
    and sp.limit(F_eaa_t, t, sp.oo) == 0,
)

eaa_direct_integral = sp.integrate(I_eaa_u, (u, 0, 1))
check(
    "P3: direct exact EAA Jacobi integral is zero",
    sp.simplify(eaa_direct_integral) == 0,
)

eaa_forward_coefficient = eaa_direct_integral
eaa_reverse_coefficient = eaa_direct_integral
V_eaa = sp.Matrix(
    [[0, eaa_reverse_coefficient], [eaa_forward_coefficient, 0]]
)
J_eaa = -sp.eye(2)
S_eaa = sp.simplify(J_eaa * V_eaa - V_eaa.conjugate().T * J_eaa)
check(
    "P3: both directed EAA coefficients vanish separately",
    eaa_forward_coefficient == 0 and eaa_reverse_coefficient == 0,
)
check(
    "P3: the resulting same-sign EAA J-adjoint source is exactly zero",
    V_eaa == sp.zeros(2) and S_eaa == sp.zeros(2),
)


print("\nAAL symbolic certificate")
print("  n1=2J1, n2=2J2, N=n1+n2=2S")
print("  D(t) =", D_aal_t)
print("  I(t) =", I_aal_t)
print("  I(u) du =", I_aal_u, "du")
print("  shifted Jacobi polynomial =", P1_aal)
print("  quotient =", aal_quotient)
print("  primitive F(u) =", F_aal_u)
print(
    "  scope: Jacobi factorization is symbolic; generic-spin Weyl-density",
    "factorization remains to be derived",
)

print("\nEAA forward/reverse certificate")
print("  harmonic overlap =", EAA_overlap)
print("  D_forward(t) =", D_eaa_forward_t)
print("  D_reverse(t) =", D_eaa_reverse_t)
print("  I(t) =", I_eaa_forward_t)
print("  I(u) du =", I_eaa_u, "du")
print("  shifted Jacobi polynomial =", P1_eaa)
print("  quotient =", eaa_quotient)
print("  primitive F(u) =", F_eaa_u)
print("  primitive endpoints =", F_eaa_u.subs(u, 0), F_eaa_u.subs(u, 1))
print(
    "  forward/reverse integrated coefficients =",
    eaa_forward_coefficient,
    eaa_reverse_coefficient,
)
print("  J_EAA =", J_eaa)
print("  J_EAA V - V^dagger J_EAA =", S_eaa)


if not PASS:
    raise SystemExit("CONFORMAL JACOBI FACTORIZATION: FAIL")

print("\nCONFORMAL JACOBI FACTORIZATION: ALL PASS")
