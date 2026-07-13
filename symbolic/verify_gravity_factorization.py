#!/usr/bin/env python3
"""Exact symbolic seed for the Einstein-Weyl MM -> Mh obstruction.

Conventions follow Magnano-Sokolowski's Einstein-frame action and signature
(-,+,+,+), with massive spin-2 mass m=1 and irrelevant overall gravitational
couplings suppressed.

Checks:
  G14a  exact three-point kinematics and TT polarizations
  G14b  no cubic potential term for linearly traceless massive fields
  G14c  nonzero MMM three-point amplitude
  G14d  nonzero MMh three-point amplitude
  G14e  exact graviton Ward identity
  G14f  Bose symmetry of MMh
  G14g  five-polarization factorization sum
  G14h  exact nonzero reduced residue numerator sqrt(3)/32
  G14i  massive inverse-propagator slope and pole-normalized residue

The script is a compact independent derivation from
  L_M = 1/2 K(Q) + m^2/(8 A) [-tau^2 + psi_{mu nu} psi^{mu nu}
                               + 6 A tau - 12 A^2],
with psi = g + Phi.
"""

from __future__ import annotations

import sympy as s

I = s.I
eta = s.diag(-1, 1, 1, 1)
a, b, c = s.symbols("a b c")
_poly_vars = (a, b, c)


def trunc(expr: s.Expr, degree: int = 3) -> s.Expr:
    """Truncate a polynomial in a,b,c by total degree."""
    out = s.Integer(0)
    for term in s.expand(expr).as_ordered_terms():
        powers = term.as_powers_dict()
        total = sum(powers.get(v, 0) for v in _poly_vars)
        if total <= degree:
            out += term
    return s.expand(out)


def mat_trunc(matrix: s.Matrix, degree: int = 3) -> s.Matrix:
    return matrix.applyfunc(lambda x: trunc(x, degree))


def lower(vector: s.Matrix) -> s.Matrix:
    return eta * vector


def outer_lower(v: s.Matrix, w: s.Matrix) -> s.Matrix:
    return lower(v) * lower(w).T


def dot(p: s.Matrix, q: s.Matrix) -> s.Expr:
    return s.simplify((p.T * eta * q)[0])


def tensor_trace(E: s.Matrix) -> s.Expr:
    return s.simplify(sum(eta[mu, nu] * E[mu, nu]
                          for mu in range(4) for nu in range(4)))


def transverse(p: s.Matrix, E: s.Matrix) -> bool:
    return all(s.simplify(sum(p[mu] * E[mu, nu] for mu in range(4))) == 0
               for nu in range(4))


def tensor_inner(E: s.Matrix, F: s.Matrix) -> s.Expr:
    return s.simplify(sum(
        eta[mu, rho] * eta[nu, sig] * E[mu, nu] * F[rho, sig]
        for mu in range(4) for nu in range(4)
        for rho in range(4) for sig in range(4)
    ))


# ---------------------------------------------------------------------------
# Einstein-frame cubic action evaluator: two Phi legs and one graviton.
# ---------------------------------------------------------------------------

def mmh_amplitude(
    p1: s.Matrix,
    p2: s.Matrix,
    k: s.Matrix,
    E1: s.Matrix,
    E2: s.Matrix,
    H: s.Matrix,
) -> s.Expr:
    """Coefficient of a*b*c in sqrt(-g) L_M for Phi1 Phi2 h."""
    h = a * H
    Phi = b * E1 + c * E2
    X = h + Phi

    # g^{-1} and psi^{-1}, sufficient through cubic order.
    g_inv = mat_trunc(eta - eta * h * eta, 1)
    psi_inv = mat_trunc(
        eta - eta * X * eta + eta * X * eta * X * eta,
        2,
    )

    p1_l, p2_l, k_l = lower(p1), lower(p2), lower(k)
    dh = [I * k_l[mu] * a * H for mu in range(4)]
    dphi = [I * p1_l[mu] * b * E1 + I * p2_l[mu] * c * E2
            for mu in range(4)]

    # Gamma(g), linear in h.
    Gamma = [[[s.Integer(0) for _ in range(4)] for _ in range(4)]
             for _ in range(4)]
    for al in range(4):
        for mu in range(4):
            for nu in range(4):
                value = sum(
                    eta[al, be]
                    * (dh[mu][be, nu] + dh[nu][be, mu] - dh[be][mu, nu])
                    for be in range(4)
                ) / 2
                Gamma[al][mu][nu] = trunc(value, 1)

    # nabla_mu Phi_{be nu}.
    nabla = [[[s.Integer(0) for _ in range(4)] for _ in range(4)]
             for _ in range(4)]
    for mu in range(4):
        for be in range(4):
            for nu in range(4):
                value = dphi[mu][be, nu] - sum(
                    Gamma[rho][mu][be] * Phi[rho, nu]
                    + Gamma[rho][mu][nu] * Phi[be, rho]
                    for rho in range(4)
                )
                nabla[mu][be][nu] = trunc(value, 2)

    # Q^al_{mu nu} = 1/2 psi^{-1 al be}
    #                  (nabla_mu Phi_{be nu}+nabla_nu Phi_{be mu}
    #                   -nabla_be Phi_{mu nu}).
    Q = [[[s.Integer(0) for _ in range(4)] for _ in range(4)]
         for _ in range(4)]
    for al in range(4):
        for mu in range(4):
            for nu in range(4):
                value = sum(
                    psi_inv[al, be]
                    * (nabla[mu][be][nu] + nabla[nu][be][mu]
                       - nabla[be][mu][nu])
                    for be in range(4)
                ) / 2
                Q[al][mu][nu] = trunc(value, 2)

    K = s.Integer(0)
    for mu in range(4):
        for nu in range(4):
            if g_inv[mu, nu] == 0:
                continue
            first = s.Integer(0)
            second = s.Integer(0)
            for al in range(4):
                for be in range(4):
                    first += Q[al][mu][nu] * Q[be][al][be]
                    second += Q[al][mu][be] * Q[be][nu][al]
            K += g_inv[mu, nu] * (first - second)
    K = trunc(K, 3)

    # Exact potential expanded through degree three.
    X_mix = mat_trunc(g_inv * Phi, 2)
    t1 = trunc(s.trace(X_mix), 2)
    t2 = trunc(s.trace(X_mix * X_mix), 3)
    t3 = trunc(s.trace(X_mix * X_mix * X_mix), 3)
    A = trunc(
        1 + s.Rational(1, 2) * t1
        + s.Rational(1, 8) * t1**2 - s.Rational(1, 4) * t2
        + s.Rational(1, 48) * t1**3
        - s.Rational(1, 8) * t1 * t2
        + s.Rational(1, 6) * t3,
        3,
    )
    inv_A = trunc(1 - (A - 1) + (A - 1)**2 - (A - 1)**3, 3)
    tau = 4 + t1
    psi_squared = 4 + 2 * t1 + t2
    potential = trunc(
        s.Rational(1, 8) * inv_A
        * (-tau**2 + psi_squared + 6 * A * tau - 12 * A**2),
        3,
    )

    sqrt_minus_g = trunc(1 + s.Rational(1, 2) * s.trace(eta * h), 1)
    lagrangian = trunc(
        sqrt_minus_g * (s.Rational(1, 2) * K + potential),
        3,
    )
    return s.simplify(
        s.expand(lagrangian).coeff(a, 1).coeff(b, 1).coeff(c, 1)
    )


# ---------------------------------------------------------------------------
# Pure Phi cubic kinetic vertex.
# ---------------------------------------------------------------------------

def q1(E: s.Matrix, p: s.Matrix):
    p_l = lower(p)
    Q = [[[s.Integer(0) for _ in range(4)] for _ in range(4)]
         for _ in range(4)]
    for al in range(4):
        for mu in range(4):
            for nu in range(4):
                value = sum(
                    eta[al, be]
                    * (p_l[mu] * E[be, nu] + p_l[nu] * E[be, mu]
                       - p_l[be] * E[mu, nu])
                    for be in range(4)
                )
                Q[al][mu][nu] = s.simplify(I * value / 2)
    return Q


def q2(Ea: s.Matrix, Eb: s.Matrix, pb: s.Matrix):
    """Inverse-metric correction Ea times derivative field Eb."""
    Ea_up = eta * Ea * eta
    pb_l = lower(pb)
    Q = [[[s.Integer(0) for _ in range(4)] for _ in range(4)]
         for _ in range(4)]
    for al in range(4):
        for mu in range(4):
            for nu in range(4):
                value = sum(
                    Ea_up[al, be]
                    * (pb_l[mu] * Eb[be, nu] + pb_l[nu] * Eb[be, mu]
                       - pb_l[be] * Eb[mu, nu])
                    for be in range(4)
                )
                Q[al][mu][nu] = s.simplify(-I * value / 2)
    return Q


def k_bilinear(QA, QB) -> s.Expr:
    value = s.Integer(0)
    for mu in range(4):
        for nu in range(4):
            if eta[mu, nu] == 0:
                continue
            first = s.Integer(0)
            second = s.Integer(0)
            for al in range(4):
                for be in range(4):
                    first += QA[al][mu][nu] * QB[be][al][be]
                    second += QA[al][mu][be] * QB[be][nu][al]
            value += eta[mu, nu] * (first - second)
    return s.simplify(value)


def mmm_amplitude(momenta, polarizations) -> s.Expr:
    q_linear = [q1(polarizations[i], momenta[i]) for i in range(3)]
    value = s.Integer(0)
    for i in range(3):
        remaining = [j for j in range(3) if j != i]
        j, k = remaining
        for x, y in ((j, k), (k, j)):
            q_quad = q2(polarizations[x], polarizations[y], momenta[y])
            value += k_bilinear(q_linear[i], q_quad)
            value += k_bilinear(q_quad, q_linear[i])
    # L_M contains 1/2 K.
    return s.simplify(value / 2)


def massive_tt_two_point(p: s.Matrix, E: s.Matrix) -> s.Expr:
    """Quadratic L_M coefficient for TT waves (p,E) and (-p,E).

    This fixes the internal-line normalization that is not contained in a
    bare product of two cubic vertices.  With m=1 and E.E=1, the coefficient
    is (p^2+1)/4 in the conventions of this script.
    """
    qp = q1(E, p)
    qm = q1(E, -p)
    kinetic = s.Rational(1, 2) * (
        k_bilinear(qp, qm) + k_bilinear(qm, qp)
    )
    # For two distinct linearly traceless waves, the coefficient of the
    # quadratic potential (m^2/8) Tr(Phi^2) is (m^2/4) E.E.
    potential = s.Rational(1, 4) * tensor_inner(E, E)
    return s.simplify(kinetic + potential)


def massive_polarizations_along_z(p: s.Matrix):
    E, z = p[0], p[3]
    ex = s.Matrix([0, 1, 0, 0])
    ey = s.Matrix([0, 0, 1, 0])
    ell = s.Matrix([z, 0, 0, E])
    plus = (outer_lower(ex, ex) - outer_lower(ey, ey)) / s.sqrt(2)
    cross = (outer_lower(ex, ey) + outer_lower(ey, ex)) / s.sqrt(2)
    zero = (outer_lower(ex, ex) + outer_lower(ey, ey)
            - 2 * outer_lower(ell, ell)) / s.sqrt(6)
    return {"plus": plus, "cross": cross, "zero": zero}


# ---------------------------------------------------------------------------
# Exact checks.
# ---------------------------------------------------------------------------

# Left three-point MMM kinematics: P + p + q = 0.
P = s.Matrix([1, 0, 0, 0])
p = s.Matrix([-s.Rational(1, 2), 0, 0, I * s.sqrt(3) / 2])
q = s.Matrix([-s.Rational(1, 2), 0, 0, -I * s.sqrt(3) / 2])
assert P + p + q == s.zeros(4, 1)
assert [dot(x, x) for x in (P, p, q)] == [-1, -1, -1]

pol_P = massive_polarizations_along_z(P)
pol_p = massive_polarizations_along_z(p)
pol_q = massive_polarizations_along_z(q)
for momentum, collection in ((P, pol_P), (p, pol_p), (q, pol_q)):
    for polarization in collection.values():
        assert tensor_trace(polarization) == 0
        assert transverse(momentum, polarization)
print("G14a PASS: exact massive three-point shell and TT polarizations")

# Potential expansion: for t1=Tr Phi=0, the cubic potential vanishes.
t1, t2, t3 = s.symbols("t1 t2 t3")

def weighted_trunc(expr):
    out = 0
    for term in s.expand(expr).as_ordered_terms():
        powers = term.as_powers_dict()
        weight = powers.get(t1, 0) + 2 * powers.get(t2, 0) + 3 * powers.get(t3, 0)
        if weight <= 3:
            out += term
    return s.expand(out)

log_A = s.Rational(1, 2) * (t1 - t2 / 2 + t3 / 3)
A_series = weighted_trunc(1 + log_A + log_A**2 / 2 + log_A**3 / 6)
A2_series = weighted_trunc(A_series**2)
inv_A_series = weighted_trunc(1 - (A_series - 1) + (A_series - 1)**2 - (A_series - 1)**3)
tau_series = 4 + t1
psi_squared_series = 4 + 2 * t1 + t2
V_series = weighted_trunc(inv_A_series * (-tau_series**2 + psi_squared_series + 6 * A_series * tau_series - 12 * A2_series))
assert s.simplify(V_series.subs(t1, 0) - t2) == 0
assert s.expand(V_series.subs(t1, 0)).coeff(t3) == 0
print("G14b PASS: the traceless massive potential has no cubic term")

A_MMM = mmm_amplitude(
    (P, p, q),
    (pol_P["plus"], pol_p["plus"], pol_q["zero"]),
)
assert s.simplify(A_MMM + s.sqrt(6) / 8) == 0
print(f"G14c PASS: A3(M_plus,M_plus,M_0) = {A_MMM}")

# Right MMh kinematics: -P + r + k = 0.
r = s.Matrix([1, -1, -I, 0])
k = s.Matrix([0, 1, I, 0])
assert -P + r + k == s.zeros(4, 1)
assert dot(r, r) == -1 and dot(k, k) == 0

v_r = s.Matrix([1, -1, 0, 0])
e_h = s.Matrix([1, 0, 0, 1])
E_r = outer_lower(v_r, v_r)
H = outer_lower(e_h, e_h)
assert tensor_trace(E_r) == 0 and transverse(r, E_r)
assert tensor_trace(H) == 0 and transverse(k, H)

A_MMh = mmh_amplitude(-P, r, k, pol_P["plus"], E_r, H)
assert s.simplify(A_MMh + s.sqrt(2) / 8) == 0
print(f"G14d PASS: A3(M_plus,M,h) = {A_MMh}")

# Exact Ward identity for arbitrary xi.
xi0, xi1, xi2, xi3 = s.symbols("xi0 xi1 xi2 xi3")
xi = s.Matrix([xi0, xi1, xi2, xi3])
k_l = lower(k)
xi_l = lower(xi)
H_gauge = k_l * xi_l.T + xi_l * k_l.T
ward = mmh_amplitude(-P, r, k, pol_P["plus"], E_r, H_gauge)
assert s.simplify(ward) == 0
print("G14e PASS: exact MMh graviton Ward identity")

# Bose exchange of the two massive legs.
A_MMh_swap = mmh_amplitude(r, -P, k, E_r, pol_P["plus"], H)
assert s.simplify(A_MMh_swap - A_MMh) == 0
print("G14f PASS: MMh is symmetric under exchange of massive legs")

# Complete orthonormal massive spin-2 basis at rest.
ex = s.Matrix([0, 1, 0, 0])
ey = s.Matrix([0, 0, 1, 0])
ez = s.Matrix([0, 0, 0, 1])
rest_basis = {
    "plus": (outer_lower(ex, ex) - outer_lower(ey, ey)) / s.sqrt(2),
    "cross": (outer_lower(ex, ey) + outer_lower(ey, ex)) / s.sqrt(2),
    "zero": (outer_lower(ex, ex) + outer_lower(ey, ey)
             - 2 * outer_lower(ez, ez)) / s.sqrt(6),
    "xz": (outer_lower(ex, ez) + outer_lower(ez, ex)) / s.sqrt(2),
    "yz": (outer_lower(ey, ez) + outer_lower(ez, ey)) / s.sqrt(2),
}
for name, Ei in rest_basis.items():
    assert tensor_inner(Ei, Ei) == 1, name
    assert transverse(P, Ei), name
    assert tensor_trace(Ei) == 0, name
print("G14g PASS: complete orthonormal five-polarization internal basis")

# Choose left external polarizations p_plus and q_zero. Sum the complete
# five-polarization numerator of the internal massive-pole residue.
residue_numerator = s.Integer(0)
contributions = {}
for name, E_internal in rest_basis.items():
    left = mmm_amplitude(
        (P, p, q),
        (E_internal, pol_p["plus"], pol_q["zero"]),
    )
    right = mmh_amplitude(-P, r, k, E_internal, E_r, H)
    product = s.simplify(left * right)
    contributions[name] = (left, right, product)
    residue_numerator += product
residue_numerator = s.simplify(residue_numerator)
assert s.simplify(residue_numerator - s.sqrt(3) / 32) == 0
print("G14h PASS: complete five-polarization residue numerator")
for name, values in contributions.items():
    print(f"  {name:>5s}: left={values[0]}, right={values[1]}, product={values[2]}")
print(f"  SUM = {residue_numerator}")

# The cubic-vertex product must be multiplied by the inverse quadratic
# kernel on the internal line.  Determine that factor rather than silently
# treating the polarization completeness relation as a unit-residue
# propagator.  For p=(w,0,0,0), p^2=-w^2 and L_M^(2)=(p^2+1)/4.
w = s.symbols("w", real=True)
p_off = s.Matrix([w, 0, 0, 0])
inverse_kernel = massive_tt_two_point(p_off, rest_basis["plus"])
assert s.simplify(inverse_kernel - (1 - w**2) / 4) == 0
z_massive = s.Rational(1, 4)
pole_residue_lm = s.simplify(residue_numerator / z_massive)
assert s.simplify(pole_residue_lm - s.sqrt(3) / 8) == 0
print("G14i PASS: L_M massive inverse kernel = (p^2+1)/4; "
      f"pole-normalized residue = {pole_residue_lm}")
print("  (An overall rescaling of the full action rescales the displayed "
      "residue but cannot change its nonvanishing.)")

print("ALL PASS")
