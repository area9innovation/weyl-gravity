"""Iyer--Wald surface machinery for Lagrangians L(g, Riemann), exact sympy.

Frozen conventions (BH-1 preflight; shared with the certificate schema):

- E^{abcd} = dL/dR_{abcd} with Riemann index symmetries;
- theta^a  = 2 (E^{abcd} nabla_d dg_{bc} - dg_{bc} nabla_d E^{abcd});
- Q^{ab}   = -E^{abcd} nabla_c chi_d + 2 chi_d nabla_c E^{abcd};
- 2-forms on the sphere S_r in a static diagonal chart (t, r, th, ph) with
  eps_{t r th ph} = +sqrt(-g):
      (Q-form)_{th ph}        = eps_{ab th ph} Q^{ab} = 2 sqrt(-g) Q^{tr},
      (i_chi theta)_{th ph}   = chi^b eps_{a b th ph} theta^a
                              = -sqrt(-g) chi^t theta^r  (chi = chi^t d_t).

Normalization control (certified): for Einstein gravity E^{abcd} =
(g^{ac} g^{bd} - g^{ad} g^{bc})/2 (i.e. L = R, units 16 pi G = 1) these
conventions give F = Int_{S_r}(delta Q - i_chi theta) = 16 pi delta m on
Schwarzschild and Schwarzschild--de Sitter (fixed k), the Wald/ADM value.

For pure-Weyl gravity L = alpha C_abcd C^abcd the tensor is
E^{abcd} = 2 alpha C^{abcd}.
"""

from __future__ import annotations

import sympy as sp

N = 4


def up4(geo, Tlow):
    """Raise all four indices of a covariant 4-tensor."""
    gi = geo.ginv
    out = [[[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]
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
                                        s += w * Tlow[p][q][u][v]
                    out[a][b][c][d] = sp.cancel(sp.together(s))
    return out


def covd_up4(geo, T, e, a, b, c, d):
    """(nabla_e T)^{abcd} for a contravariant 4-tensor."""
    s = sp.diff(T[a][b][c][d], geo.coords[e])
    G = geo.Gamma
    for h in range(N):
        s += (
            G[a][e][h] * T[h][b][c][d]
            + G[b][e][h] * T[a][h][c][d]
            + G[c][e][h] * T[a][b][h][d]
            + G[d][e][h] * T[a][b][c][h]
        )
    return s


def E_einstein(geo):
    """E^{abcd} for L = R (units 16 pi G = 1)."""
    gi = geo.ginv
    return [
        [
            [
                [
                    sp.cancel((gi[a, c] * gi[b, d] - gi[a, d] * gi[b, c]) / 2)
                    for d in range(N)
                ]
                for c in range(N)
            ]
            for b in range(N)
        ]
        for a in range(N)
    ]


def E_weyl(geo, alpha):
    """E^{abcd} = 2 alpha C^{abcd} for L = alpha C_abcd C^abcd."""
    Cup = up4(geo, geo.Weyl)
    return [
        [
            [[sp.cancel(2 * alpha * Cup[a][b][c][d]) for d in range(N)] for c in range(N)]
            for b in range(N)
        ]
        for a in range(N)
    ]


def surface_forms(geo, E_up, chi_up, dg):
    """((Q-form)_{th ph}, (i_chi theta)_{th ph}) on S_r, exact.

    Valid in a static diagonal chart with coordinates (t, r, th, ph) and
    chi = chi^t d_t.
    """
    g = geo.g
    sqrtg = sp.sqrt(-g.det())
    theta_up = [sp.Integer(0)] * N
    for a in range(N):
        s = sp.Integer(0)
        for b in range(N):
            for c in range(N):
                for dd in range(N):
                    Ed = E_up[a][b][c][dd]
                    if Ed != 0:
                        s += 2 * Ed * geo.covd2(dg, dd, b, c)
                    if dg[b, c] != 0:
                        s -= 2 * dg[b, c] * covd_up4(geo, E_up, dd, a, b, c, dd)
        theta_up[a] = sp.cancel(sp.together(s))
    chi_low = [sp.cancel(sum(g[d, e] * chi_up[e] for e in range(N))) for d in range(N)]

    def nabla_chi(cc, dd):
        s = sp.diff(chi_low[dd], geo.coords[cc])
        for h in range(N):
            s -= geo.Gamma[h][cc][dd] * chi_low[h]
        return s

    Q_tr = sp.Integer(0)
    for cc in range(N):
        for dd in range(N):
            if E_up[0][1][cc][dd] != 0:
                Q_tr -= E_up[0][1][cc][dd] * nabla_chi(cc, dd)
            if chi_low[dd] != 0:
                Q_tr += 2 * chi_low[dd] * covd_up4(geo, E_up, cc, 0, 1, cc, dd)
    q_form = sp.cancel(sp.together(2 * sqrtg * Q_tr))
    itheta = sp.cancel(sp.together(-sqrtg * chi_up[0] * theta_up[1]))
    return q_form, itheta


def sphere_integral(expr, th, ph):
    """Exact integral of a 2-form component over th in (0, pi), ph in (0, 2 pi)."""
    return sp.integrate(sp.integrate(expr, (th, 0, sp.pi)), (ph, 0, 2 * sp.pi))
