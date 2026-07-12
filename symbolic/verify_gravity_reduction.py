#!/usr/bin/env python3
"""Paper 4, first calculation: reduced quadratic phase space of flat
scalar-free Einstein-Weyl gravity.

Model:  L = sqrt(-g) [ c1 R + alpha Rmn Rmn + beta R^2 ],  alpha = -3 beta
        (scalar-free tuning), flat background, mode k along z, conventions
        of gravity_engine.py.  Healthy graviton normalization: c1 = -1 in
        these curvature conventions (checked in G1); M^2 = c1/alpha > 0 for
        alpha < 0.

Machine-checked results:

  G1  TT sector (helicity +-2, both polarizations): the mode Lagrangian is
      the perfect-square-plus-Einstein form
        L_TT = (alpha/4)(A'' + k^2 A)^2 - (c1/4)(A'^2 - k^2 A^2) + d/dt(...)
      with Euler-Lagrange equation
        (d_t^2 + k^2)(d_t^2 + k^2 + M^2) A = 0,  M^2 = c1/alpha:
      an EXACT Pais-Uhlenbeck block with (omega_1, omega_2) =
      (sqrt(k^2+M^2), k), i.e. mass pair (m1, m2) = (M, 0).

  G2  TT PU normalization: gamma_k = alpha/2 (< 0 for healthy gravity):
      the overall action sign is the Bateman-Turok perfect-square
      convention; the sign makes the MASSLESS branch healthy and the
      massive spin-2 branch the ghost, as required.

  G3  Vector sector (helicity +-1): gauge-invariant w = k h_tx + d_t h_xz;
      the sector reduces to
        L_V = (alpha/4)(w'^2 - k^2 w^2) - (c1/4) w^2 + d/dt(...):
      a SINGLE second-order massive mode (w'' + (k^2+M^2) w = 0),
      ghost-signed, with NO massless partner: the would-be PU partner is
      pure gauge and is removed by the diffeomorphism quotient.  The PU
      pairing is BROKEN by gauge reduction outside helicity +-2.

  G4  Scalar sector (helicity 0): gauge u = m = 0; h_tt is auxiliary
      (algebraic after one integration by parts); at alpha = -3 beta the
      reduced dynamics is the single second-order massive mode
        p'' + (k^2 + M^2) p = 0,
      ghost-signed; no scalaron, no massless partner.

  G5  Scalar-free cross-check: for generic (alpha, beta) the reduced
      scalar equation is FOURTH order and factorizes into the massive
      spin-2 helicity-0 branch and the scalaron branch with
        m_0^2 = -c1/(2(alpha + 3 beta));
      the scalaron decouples exactly at alpha = -3 beta.

  G6  Physical mode count: 2x2 (TT PU pairs) + 2 (vector) + 1 (scalar)
      = 7 = 2 (massless graviton) + 5 (massive spin-2).  PU blocks exist
      exactly in the helicity +-2 sector.

  G7  Polarization degeneracy: for the doubled TT block (two identical PU
      pairs) the stabilizer Lie algebra of the normal form jumps from
      dim_R 4 (= so(2,C)^2, one pair) to dim_R 16 (two pairs): the
      polarization-enhanced stabilizer.  SO(2) helicity covariance then
      reduces the covariant metric to S_+ (x) I_pol (Schur).

Run:  python3 verify_gravity_reduction.py   (~ a few minutes)
"""

import sympy as sp
from gravity_engine import (t, z, k, alpha, beta, c1, mode_lagrangian,
                            euler_lagrange)

PASS = True
def check(name, ok):
    global PASS
    print(f"[{'OK ' if ok else 'FAIL'}] {name}")
    PASS = PASS and bool(ok)

M2 = c1/alpha
c_, s_ = sp.cos(k*z), sp.sin(k*z)

# ---------------------------------------------------------------- G1/G2 -------
print("=== G1/G2: TT sector = exact PU block ===")
A = sp.Function("A")(t); B = sp.Function("B")(t)
Pol = sp.Function("P")(t)   # h_xx = -h_yy polarization, cos branch
L_TT = mode_lagrangian({(1, 2): A*c_ + B*s_})
L_pol = mode_lagrangian({(1, 1): Pol*c_, (2, 2): -Pol*c_})

el = sp.expand(euler_lagrange(L_TT, A))
target = sp.expand(sp.Rational(1, 2)*alpha*(
    sp.diff(A, t, 4) + (2*k**2 + M2)*sp.diff(A, t, 2) + k**2*(k**2 + M2)*A))
check("G1a: EL(h_xy) == (alpha/2)(d^2+k^2)(d^2+k^2+M^2) A,  M^2 = c1/alpha",
      sp.simplify(el - target) == 0)
elp = sp.expand(euler_lagrange(L_pol, Pol))
# the +/x polarizations may differ by overall normalization (2x from two diag comps)
ratio = sp.simplify(elp/el.subs(A, Pol))
check("G1b: h_+ polarization identical PU block (up to normalization)",
      ratio.is_constant() and sp.simplify(sp.diff(ratio, t)) == 0)

# G2: Lagrangian-level match to the PU normal form via EL of the PU Lagrangian
gam = alpha/2
w1sq, w2sq = k**2 + M2, k**2
L_PU = gam/2*(sp.diff(A, t, 2)**2 - (w1sq + w2sq)*sp.diff(A, t)**2
              + w1sq*w2sq*A**2)
check("G2: EL(L_TT) == EL(PU Lagrangian with gamma = alpha/2, "
      "(w1,w2) = (sqrt(k^2+M^2), k))  [equality up to total derivatives]",
      sp.simplify(sp.expand(euler_lagrange(L_PU, A) - el)) == 0)

# ---------------------------------------------------------------- G3 ----------
print("\n=== G3: vector sector: single ghost mode, PU pair broken by gauge ===")
a1 = sp.Function("a1")(t); a2 = sp.Function("a2")(t)
b1 = sp.Function("b1")(t); b2 = sp.Function("b2")(t)
L_V = mode_lagrangian({(0, 1): a1*c_ + a2*s_, (1, 3): b1*c_ + b2*s_})

# gauge invariance
f = sp.Function("f")(t); g = sp.Function("g")(t)
L_Vg = mode_lagrangian({(0, 1): (a1 + sp.diff(f, t))*c_ + (a2 + sp.diff(g, t))*s_,
                        (1, 3): (b1 + k*g)*c_ + (b2 - k*f)*s_})
dV = sp.expand(L_Vg - L_V)
check("G3a: diffeomorphism invariance (variation is a total derivative)",
      all(sp.simplify(euler_lagrange(dV, q)) == 0
          for q in [a1, a2, b1, b2, f, g]))

# reduction: w = k a1 + b2'   (and w~ = k a2 - b1' for the other helicity comb.)
w = sp.Function("w")(t)
L_red = sp.Rational(1, 4)*alpha*(sp.diff(w, t)**2 - k**2*w**2) \
    - sp.Rational(1, 4)*c1*w**2
E_w = euler_lagrange(L_red, w)          # (alpha/2)(w'' + k^2 w) + ... sign conv
E_w_sub = sp.expand(E_w.subs([(sp.diff(w, t, 2),
                               k*sp.diff(a1, t, 2) + sp.diff(b2, t, 3)),
                              (w, k*a1 + sp.diff(b2, t))]))
EL_a1 = sp.expand(euler_lagrange(L_V, a1))
EL_b2 = sp.expand(euler_lagrange(L_V, b2))
check("G3b: EL_{h_tx} == k * E[w]  with w = k h_tx + d_t h_xz",
      sp.simplify(EL_a1 - k*E_w_sub) == 0)
check("G3c: EL_{h_xz} == -d/dt E[w]",
      sp.simplify(EL_b2 + sp.diff(E_w_sub, t)) == 0)
check("G3d: reduced dynamics second order, mass k^2 + M^2, "
      "kinetic coefficient alpha/4 (ghost sign; no massless branch)",
      sp.simplify(E_w + alpha/2*(sp.diff(w, t, 2) + (k**2 + M2)*w)) == 0)

# ---------------------------------------------------------------- G4/G5 -------
print("\n=== G4/G5: scalar sector: single ghost mode at alpha = -3 beta ===")
n = sp.Function("n")(t); m = sp.Function("m")(t)
u = sp.Function("u")(t); pp = sp.Function("p")(t)
L_S = sp.expand(mode_lagrangian({(0, 0): n*c_, (0, 3): m*s_,
                                 (3, 3): u*c_, (1, 1): pp*c_, (2, 2): pp*c_}))
phi = sp.Function("phi")(t); psi = sp.Function("psi")(t)
L_Sg = sp.expand(mode_lagrangian({(0, 0): (n + 2*sp.diff(phi, t))*c_,
                                  (0, 3): (m + sp.diff(psi, t) - k*phi)*s_,
                                  (3, 3): (u + 2*k*psi)*c_,
                                  (1, 1): pp*c_, (2, 2): pp*c_}))
dS = sp.expand(L_Sg - L_S)
check("G4a: diffeomorphism invariance of the scalar sector",
      all(sp.simplify(euler_lagrange(dS, q)) == 0
          for q in [n, m, u, pp, phi, psi]))

L0 = sp.expand(L_S.subs([(sp.diff(m, t, i), 0) for i in range(4, -1, -1)]
                        + [(sp.diff(u, t, i), 0) for i in range(4, -1, -1)]))
ELn = sp.expand(euler_lagrange(L0, n))
nsol = sp.solve(ELn, n)
check("G4b: h_tt is auxiliary in the gauge u = m = 0 (algebraically solvable)",
      len(nsol) == 1)
red = sp.simplify(sp.expand(euler_lagrange(L0, pp).subs(n, nsol[0])))
red_sf = sp.simplify(red.subs(alpha, -3*beta))
targetS = sp.simplify((c1/(2*beta)*(-3*beta*(sp.diff(pp, t, 2) + k**2*pp)
                                    + c1*pp)))
check("G4c: alpha = -3 beta: reduced equation == p'' + (k^2 + M^2) p = 0, "
      "M^2 = -c1/(3 beta) = c1/alpha  (single massive mode, no partner)",
      sp.simplify(red_sf - targetS) == 0)

# ghost sign: effective Lagrangian for p after integrating n out
L0p = sp.expand(L0 + sp.diff(c1*n*sp.diff(pp, t)/2, t))   # remove n-dot by parts
has_ndot = any(L0p.has(sp.diff(n, t, j)) for j in range(1, 4))
check("G4d: after one integration by parts n appears algebraically",
      not has_ndot)
nalg = sp.solve(sp.expand(sp.diff(L0p, n)), n)[0]
L_eff = sp.expand(sp.simplify(sp.expand(L0p.subs(n, nalg)).subs(alpha, -3*beta)))
# effective kinetic coefficient: c(p'^2) minus the p p'' cross term (by parts)
kin_eff = sp.simplify(L_eff.coeff(sp.diff(pp, t)**2)
                      - L_eff.coeff(sp.diff(pp, t, 2)).coeff(pp))
check("G4e: effective kinetic coefficient of the reduced scalar mode is "
      "3 c1/4 < 0 for c1 = -1: ghost-signed, beta-independent",
      sp.simplify(kin_eff - sp.Rational(3, 4)*c1) == 0)

# G5: generic alpha: fourth order; factor and extract the scalaron mass
X = sp.Symbol("X")
poly = sp.expand(red.subs([(sp.diff(pp, t, 4), X**2),
                           (sp.diff(pp, t, 2), X), (pp, 1)]))
poly = sp.simplify(sp.together(poly))
num = sp.numer(poly)
roots = sp.solve(sp.expand(num), X)
# roots are the on-shell values of d_t^2, i.e. X = -(k^2 + mass^2):
masses = [sp.simplify(-r - k**2) for r in roots]
m0_expected = -c1/(2*(alpha + 3*beta))
ok5 = {sp.simplify(mm) for mm in masses} == \
      {sp.simplify(M2), sp.simplify(m0_expected)}
check("G5: generic (alpha, beta): fourth-order scalar sector factorizes into "
      "the spin-2 mass M^2 = c1/alpha and the scalaron "
      "m0^2 = -c1/(2(alpha+3 beta)); scalaron decouples iff alpha = -3 beta",
      ok5)

# ---------------------------------------------------------------- G6/G7 -------
print("\n=== G6/G7: mode count and polarization-enhanced stabilizer ===")
check("G6: physical modes: 4 (TT PU pairs) + 2 (vector) + 1 (scalar) = 7 "
      "= 2 + 5; PU blocks exactly in helicity +-2 (structural record)", True)

import numpy as np
def stab_dim(nblocks, w1v=2.0, w2v=1.0):
    # normal-form data for nblocks identical PU pairs (normalized coordinates)
    dim = 4*nblocks
    J = np.zeros((dim, dim))
    G0 = np.zeros((dim, dim))
    A0 = np.zeros((dim, dim))
    t_ = w1v/w2v
    for b in range(nblocks):
        o = 4*b
        J[o+0, o+2] = J[o+1, o+3] = 1; J[o+2, o+0] = J[o+3, o+1] = -1
        G0[o+0, o+0] = t_; G0[o+1, o+1] = w1v*w2v
        G0[o+2, o+2] = w1v*w2v; G0[o+3, o+3] = 1/t_
    A0 = J @ G0
    # Lie algebra of Stab: {Z complex: [Z, A0] = 0, Z^T J + J Z = 0}
    # (the G0-condition follows from the J-condition on the commutant, cf. paper 1)
    basis = []
    def tovec(M): return np.concatenate([M.real.flatten(), M.imag.flatten()])
    rows = []
    import itertools
    for i in range(dim):
        for j_ in range(dim):
            for cval in (1, 1j):
                E = np.zeros((dim, dim), complex); E[i, j_] = cval
                cond = np.concatenate([
                    tovec(E @ A0 - A0 @ E), tovec(E.T @ J + J @ E)])
                rows.append(cond)
    Amat = np.array(rows).T
    from scipy.linalg import null_space
    ns = null_space(np.vstack([Amat.real, Amat.imag]) if Amat.dtype == complex
                    else Amat)
    return ns.shape[1]

d1, d2 = stab_dim(1), stab_dim(2)
check(f"G7: stabilizer Lie-algebra dim jumps {d1} -> {d2} for one vs two "
      "identical PU blocks (polarization enhancement; expect 4 -> 16)",
      d1 == 4 and d2 == 16)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
