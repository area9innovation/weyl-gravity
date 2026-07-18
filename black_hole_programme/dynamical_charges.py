"""Dynamical covariant-phase-space machinery for the black-hole programme.

Exact sympy objects on a static spherical background, frozen conventions
continued from `lee_wald.py` (Q-form and i_chi Theta normalizations fixed by
the certified GR controls):

- full component set of the charge 2-form
      k(delta) = delta Q_chi - i_chi Theta(delta)
  for an arbitrary (possibly time-dependent) metric perturbation, with the
  delta Q computed as an exact epsilon-derivative of Q on g + eps*h;
- the corrected presymplectic current (variation of the DENSITY sqrt(-g)
  theta^a, i.e. including the (1/2) tr(h) theta^a terms):
      omega^a(d1,d2) = d1 theta^a(d2) - d2 theta^a(d1)
                       + (1/2) tr(d1) theta^a(d2) - (1/2) tr(d2) theta^a(d1);
- the on-shell Noether identity  Theta(L_xi g) - i_xi(L eps) = d Q_xi  and
  the resulting background-only identity route for diffeo directions:
      k(delta_xi) = L_xi Q_chi + Q_{[chi,xi]} - L_chi Q_xi
                    - i_chi i_xi (L eps) + d(i_chi Q_xi).
"""

from __future__ import annotations

from itertools import combinations

import sympy as sp

N = 4


def E_weyl(geo, alpha):
    """E^{abcd} = 2 alpha C^{abcd}."""
    gi = geo.ginv
    C = geo.Weyl
    E = [[[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]
    for a in range(N):
        for b in range(N):
            for c in range(N):
                for d in range(N):
                    s = sp.Integer(0)
                    for p in range(N):
                        for q in range(N):
                            for u in range(N):
                                for v in range(N):
                                    w = gi[a, p] * gi[b, q] * gi[c, u] * gi[d, v]
                                    if w != 0:
                                        s += w * C[p][q][u][v]
                    E[a][b][c][d] = sp.cancel(sp.together(2 * alpha * s))
    return E


def covd_up4(geo, T, e, a, b, c, d):
    s = sp.diff(T[a][b][c][d], geo.coords[e])
    G = geo.Gamma
    for h in range(N):
        s += (G[a][e][h] * T[h][b][c][d] + G[b][e][h] * T[a][h][c][d]
              + G[c][e][h] * T[a][b][h][d] + G[d][e][h] * T[a][b][c][h])
    return s


def theta_up(geo, E, dg):
    """theta^a = 2 E^{abcd} nabla_d dg_{bc} - 2 dg_{bc} nabla_d E^{abcd}."""
    out = [sp.Integer(0)] * N
    for a in range(N):
        s = sp.Integer(0)
        for b in range(N):
            for c in range(N):
                for dd in range(N):
                    if E[a][b][c][dd] != 0:
                        s += 2 * E[a][b][c][dd] * geo.covd2(dg, dd, b, c)
                    if dg[b, c] != 0:
                        s -= 2 * dg[b, c] * covd_up4(geo, E, dd, a, b, c, dd)
        out[a] = sp.cancel(sp.together(s))
    return out


def Q_up(geo, E, chi_up):
    """antisymmetric Q^{ab} = -E^{abcd} nabla_c chi_d + 2 chi_d nabla_c E^{abcd}."""
    g = geo.g
    chi_low = [sum(g[d, e] * chi_up[e] for e in range(N)) for d in range(N)]

    def nabla_chi(cc, dd):
        s = sp.diff(chi_low[dd], geo.coords[cc])
        for h in range(N):
            s -= geo.Gamma[h][cc][dd] * chi_low[h]
        return s

    Q = [[sp.Integer(0)] * N for _ in range(N)]
    for a in range(N):
        for b in range(a + 1, N):
            s = sp.Integer(0)
            for cc in range(N):
                for dd in range(N):
                    if E[a][b][cc][dd] != 0:
                        s -= E[a][b][cc][dd] * nabla_chi(cc, dd)
                    if chi_low[dd] != 0:
                        s += 2 * chi_low[dd] * covd_up4(geo, E, cc, a, b, cc, dd)
            s = sp.cancel(sp.together(s))
            Q[a][b] = s
            Q[b][a] = -s
    return Q


def perm_sign():
    sign = {}
    from itertools import permutations
    for p in permutations((0, 1, 2, 3)):
        s = 1
        pl = list(p)
        for i in range(4):
            for j in range(i + 1, 4):
                if pl[i] > pl[j]:
                    s = -s
        sign[p] = s
    return sign


_SIGN = perm_sign()


def q_two_form(geo, Qup):
    """(Q-form)_{cd} = eps_{abcd} Q^{ab} (full double sum), keys c<d."""
    sqrtg = sp.sqrt(-geo.g.det())
    out = {}
    for c in range(N):
        for d in range(c + 1, N):
            s = sp.Integer(0)
            for a in range(N):
                for b in range(N):
                    if len({a, b, c, d}) == 4:
                        s += _SIGN[(a, b, c, d)] * Qup[a][b]
            out[(c, d)] = sp.cancel(sp.together(sqrtg * s))
    return out


def i_chi_theta_form(geo, theta, chi_up):
    """(i_chi Theta)_{cd} = eps_{abcd} theta^a chi^b, keys c<d."""
    sqrtg = sp.sqrt(-geo.g.det())
    out = {}
    for c in range(N):
        for d in range(c + 1, N):
            s = sp.Integer(0)
            for a in range(N):
                for b in range(N):
                    if len({a, b, c, d}) == 4:
                        s += _SIGN[(a, b, c, d)] * theta[a] * chi_up[b]
            out[(c, d)] = sp.cancel(sp.together(sqrtg * s))
    return out


def charge_form(GeoCls, coords, g0, geo0, E0, chi_up, h, alpha, eps):
    """k_{cd} = (d/deps Q-form[g0+eps h])|_0 - (i_chi Theta(h))_{cd}, chi fixed."""
    geo_e = GeoCls(coords, g0 + eps * h)
    Qf_e = q_two_form(geo_e, Q_up(geo_e, E_weyl(geo_e, alpha), chi_up))
    IT = i_chi_theta_form(geo0, theta_up(geo0, E0, h), chi_up)
    return {
        key: sp.simplify(sp.cancel(sp.together(sp.diff(Qf_e[key], eps).subs(eps, 0) - IT[key])))
        for key in Qf_e
    }


def omega_symplectic(GeoCls, coords, g0, geo0, E0, h1, h2, alpha, eps, eps2):
    """Corrected symplectic current vector omega^a(d1, d2), exact."""
    th12 = theta_up(GeoCls(coords, g0 + eps * h1), E_weyl(GeoCls(coords, g0 + eps * h1), alpha), h2)
    th21 = theta_up(GeoCls(coords, g0 + eps2 * h2), E_weyl(GeoCls(coords, g0 + eps2 * h2), alpha), h1)
    th_1 = theta_up(geo0, E0, h1)
    th_2 = theta_up(geo0, E0, h2)
    gi = geo0.ginv
    tr1 = sum(gi[a, b] * h1[a, b] for a in range(N) for b in range(N))
    tr2 = sum(gi[a, b] * h2[a, b] for a in range(N) for b in range(N))
    out = []
    for a in range(N):
        v = (sp.diff(th12[a], eps).subs(eps, 0) - sp.diff(th21[a], eps2).subs(eps2, 0)
             + sp.Rational(1, 2) * tr1 * th_2[a] - sp.Rational(1, 2) * tr2 * th_1[a])
        out.append(sp.simplify(sp.cancel(sp.together(v))))
    return out


def lie_2form(coords, V, F):
    def get(c, d):
        if c == d:
            return sp.Integer(0)
        return F[(c, d)] if c < d else -F[(d, c)]

    out = {}
    for c in range(N):
        for d in range(c + 1, N):
            s = sum(V[e] * sp.diff(get(c, d), coords[e]) for e in range(N))
            s += sum(get(e, d) * sp.diff(V[e], coords[c]) for e in range(N))
            s += sum(get(c, e) * sp.diff(V[e], coords[d]) for e in range(N))
            out[(c, d)] = sp.cancel(sp.together(s))
    return out


def lie_metric(coords, g, xi):
    h = sp.zeros(N, N)
    for i in range(N):
        for j in range(N):
            s = sum(xi[l] * sp.diff(g[i, j], coords[l])
                    + g[l, j] * sp.diff(xi[l], coords[i])
                    + g[i, l] * sp.diff(xi[l], coords[j]) for l in range(N))
            h[i, j] = sp.cancel(sp.together(s))
    return h


def noether_identity_defect(coords, geo0, E0, xi, L_scalar, alpha):
    """components of Theta(L_xi g) - i_xi(L eps) - d Q_xi (must vanish on shell)."""
    sqrtg = sp.sqrt(-geo0.g.det())
    h = lie_metric(coords, geo0.g, xi)
    thv = theta_up(geo0, E0, h)
    Qxi = q_two_form(geo0, Q_up(geo0, E0, xi))

    def qget(c, d):
        if c == d:
            return sp.Integer(0)
        return Qxi[(c, d)] if c < d else -Qxi[(d, c)]

    defects = {}
    for trip in combinations(range(N), 3):
        bb, cc, dd = trip
        s = sp.Integer(0)
        for a in range(N):
            if len({a, bb, cc, dd}) == 4:
                s += _SIGN[(a, bb, cc, dd)] * (thv[a] - L_scalar * xi[a])
        s = sqrtg * s
        dq = (sp.diff(qget(cc, dd), coords[bb])
              - sp.diff(qget(bb, dd), coords[cc])
              + sp.diff(qget(bb, cc), coords[dd]))
        defects[trip] = sp.simplify(sp.cancel(sp.together(s - dq)))
    return defects


def diffeo_charge_form_identity_route(coords, geo0, E0, chi_up, xi, L_scalar):
    """k(delta_xi) via the on-shell identity route; background objects only."""
    sqrtg = sp.sqrt(-geo0.g.det())
    Qchi = q_two_form(geo0, Q_up(geo0, E0, chi_up))
    Qxi = q_two_form(geo0, Q_up(geo0, E0, xi))
    comm = [sum(chi_up[e] * sp.diff(xi[a], coords[e]) - xi[e] * sp.diff(chi_up[a], coords[e])
                for e in range(N)) for a in range(N)]
    Qcomm = q_two_form(geo0, Q_up(geo0, E0, comm))
    LxiQchi = lie_2form(coords, xi, Qchi)
    LchiQxi = lie_2form(coords, chi_up, Qxi)
    one = [sum((Qxi[(bb, d)] if bb < d else -Qxi[(d, bb)]) * chi_up[bb]
               for bb in range(N) if bb != d) for d in range(N)]
    out = {}
    for c in range(N):
        for d in range(c + 1, N):
            s_eps = sp.Integer(0)
            for a in range(N):
                for b in range(N):
                    if len({a, b, c, d}) == 4:
                        s_eps += _SIGN[(a, b, c, d)] * xi[a] * chi_up[b]
            val = (LxiQchi[(c, d)] + Qcomm[(c, d)] - LchiQxi[(c, d)]
                   - sqrtg * L_scalar * s_eps
                   + sp.diff(one[d], coords[c]) - sp.diff(one[c], coords[d]))
            out[(c, d)] = sp.simplify(sp.cancel(sp.together(val)))
    return out
