#!/usr/bin/env python3
"""Second variation of quadratic gravity around flat space, per helicity sector.

Conventions:
  coordinates (t, x, y, z); signature eta = diag(1, -1, -1, -1);
  g = eta + eps*h, truncation at O(eps^2) throughout;
  R^lam_{mu nu kap} = d_nu Gam^lam_{mu kap} - d_kap Gam^lam_{mu nu} + ...
  R_{mu kap} = R^nu_{mu nu kap};  L = sqrt(-g) (c1*R + alpha*Rmn^2 + beta*R^2).
  Plane waves along z: every component  A(t) cos(kz) + B(t) sin(kz);
  the per-mode Lagrangian is the z-average (coefficient of e^{0 i k z}).

The engine returns the O(eps^2) z-averaged Lagrangian as a function of the
mode amplitudes A_munu(t), B_munu(t).
"""

import sympy as sp

t, x, y, z = sp.symbols("t x y z", real=True)
COORDS = [t, x, y, z]
k = sp.Symbol("k", positive=True)
eps = sp.Symbol("epsilon")
alpha, beta, c1 = sp.symbols("alpha beta c1", real=True)

ETA = sp.diag(1, -1, -1, -1)


def trunc(expr):
    """Drop O(eps^3) and higher."""
    e = sp.expand(expr)
    return e.coeff(eps, 0) + eps*e.coeff(eps, 1) + eps**2*e.coeff(eps, 2)


def build_metric(components):
    """components: dict (mu,nu)->sympy expr in t,z (symmetric keys mu<=nu)."""
    h = sp.zeros(4, 4)
    for (m, n), v in components.items():
        h[m, n] = v
        h[n, m] = v
    g = sp.Matrix(ETA) + eps*h
    # inverse to O(eps^2): eta - eps h^ + eps^2 h^ h^   (indices raised w/ eta)
    hup = sp.Matrix(ETA)*h*sp.Matrix(ETA)          # h^{mu nu}
    ginv = sp.Matrix(ETA) - eps*hup + eps**2*(hup*sp.Matrix(ETA)*hup)
    return g, ginv, h


def christoffel(g, ginv):
    Gam = [[[0]*4 for _ in range(4)] for _ in range(4)]
    dg = [[[sp.diff(g[m, n], COORDS[l]) for l in range(4)] for n in range(4)]
          for m in range(4)]
    for lam in range(4):
        for mu in range(4):
            for nu in range(mu, 4):
                s = 0
                for rho in range(4):
                    if ginv[lam, rho] == 0:
                        continue
                    s += ginv[lam, rho]*(dg[rho][mu][nu] + dg[rho][nu][mu]
                                         - dg[mu][nu][rho])
                val = trunc(sp.Rational(1, 2)*sp.expand(s))
                Gam[lam][mu][nu] = val
                Gam[lam][nu][mu] = val
    return Gam


def ricci(Gam):
    Ric = sp.zeros(4, 4)
    for mu in range(4):
        for kap in range(mu, 4):
            s = 0
            for nu in range(4):
                s += sp.diff(Gam[nu][mu][kap], COORDS[nu])
                s -= sp.diff(Gam[nu][mu][nu], COORDS[kap])
            for nu in range(4):
                for rho in range(4):
                    a = Gam[nu][nu][rho]; b = Gam[rho][mu][kap]
                    if a != 0 and b != 0:
                        s += a*b
                    a = Gam[nu][kap][rho]; b = Gam[rho][mu][nu]
                    if a != 0 and b != 0:
                        s -= a*b
            val = trunc(sp.expand(s))
            Ric[mu, kap] = val
            Ric[kap, mu] = val
    return Ric


def lagrangian_density(components):
    """O(eps^2) coefficient of sqrt(-g)(c1 R + alpha Rmn Rmn + beta R^2)."""
    g, ginv, h = build_metric(components)
    Gam = christoffel(g, ginv)
    Ric = ricci(Gam)
    # R = g^{mu nu} R_{mu nu}
    R = trunc(sp.expand(sum(ginv[m, n]*Ric[m, n]
                            for m in range(4) for n in range(4)
                            if ginv[m, n] != 0 and Ric[m, n] != 0)))
    # Rmn^2 = g^{ma} g^{nb} R_{mn} R_{ab}: at O(eps^2) only eta-raised R1*R1
    R1 = sp.zeros(4, 4)
    for m in range(4):
        for n in range(4):
            R1[m, n] = sp.expand(Ric[m, n]).coeff(eps, 1)
    Rmn2 = sp.expand(sum(ETA[m, a]*ETA[n, b]*R1[m, n]*R1[a, b]
                         for m in range(4) for n in range(4)
                         for a in range(4) for b in range(4)
                         if ETA[m, a] != 0 and ETA[n, b] != 0))
    Rsq1 = sp.expand(R).coeff(eps, 1)
    sqrtg = trunc(sp.sqrt(sp.expand(-g.det()) + sp.S(0)).series(eps, 0, 3).removeO())
    total = trunc(sp.expand(sqrtg*(c1*R))) \
        + eps**2*(alpha*Rmn2 + beta*Rsq1**2)
    return sp.expand(total).coeff(eps, 2)


def z_average(expr):
    """Average over one period in z (coefficient of the constant Fourier mode)."""
    e = sp.expand_trig(sp.expand(expr))
    e = e.rewrite(sp.exp)
    e = sp.expand(e)
    out = 0
    for term in sp.Add.make_args(e):
        # keep terms with no z-dependence after exp-rewrite
        if term.has(z):
            c = sp.simplify(term)
            if not c.has(z):
                out += c
        else:
            out += term
    return sp.simplify(sp.expand(out))


def mode_lagrangian(components):
    """Full pipeline: density -> z-average, integrating by parts is left to
    the caller (Euler-Lagrange handles it automatically)."""
    dens = lagrangian_density(components)
    return z_average(dens)


def euler_lagrange(L, q, order=4):
    """EL expression for variable q(t) up to the given derivative order."""
    expr = -sp.diff(L, q)
    for j in range(1, order + 1):
        expr += (-1)**(j + 1)*sp.diff(sp.diff(L, sp.diff(q, t, j)), t, j)*(-1)**(j+1)*0
    # standard: sum_j (-1)^j d^j/dt^j dL/dq^{(j)}
    expr = 0
    for j in range(0, order + 1):
        expr += (-1)**j * sp.diff(sp.diff(L, sp.diff(q, t, j)), t, j)
    return sp.expand(expr)
