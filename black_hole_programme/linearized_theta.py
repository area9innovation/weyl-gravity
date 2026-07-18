"""First-order variation of the Iyer--Wald theta and the symplectic current.

For L = alpha C^2 with E^{abcd} = 2 alpha C^{abcd} and
theta^a(g; k) = 2 E^{abcd} (nabla_d k)_{bc} - 2 k_{bc} (nabla_d E)^{abcd},
this module computes the exact first-order variation delta_h theta^a(k)
(k held fixed) using the linearized-curvature objects of
`linearized_bach.LinearizedBach`, and assembles the corrected symplectic
current (density variation, including the (1/2) tr(h) theta terms):

    omega^a(h1, h2) = d_1 theta^a(h2) - d_2 theta^a(h1)
                      + (1/2) tr(h1) theta^a(h2) - (1/2) tr(h2) theta^a(h1).

This is the fast replacement for `dynamical_charges.omega_symplectic`
(which epsilon-differentiates the nonlinear pipeline and is intractable
for angular perturbations); it must agree with the certified BH-1B values
on the l=0 sector, which is enforced by the producers that use it.
"""

from __future__ import annotations

import sympy as sp

from linearized_bach import LinearizedBach

N = 4


class LinearizedTheta:
    def __init__(self, geo, alpha):
        self.geo = geo
        self.alpha = alpha
        self.g = geo.g
        self.gi = geo.ginv
        self.coords = geo.coords
        # background E^{abcd} = 2 alpha C^{abcd}
        gi, C = self.gi, geo.Weyl
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
                        E[a][b][c][d] = sp.cancel(2 * alpha * s)
        self.E = E

    def _covd_up4(self, T, e, a, b, c, d):
        s = sp.diff(T[a][b][c][d], self.coords[e])
        G = self.geo.Gamma
        for h in range(N):
            s += (G[a][e][h] * T[h][b][c][d] + G[b][e][h] * T[a][h][c][d]
                  + G[c][e][h] * T[a][b][h][d] + G[d][e][h] * T[a][b][c][h])
        return s

    def theta(self, k):
        """background theta^a(g; k)."""
        out = [sp.Integer(0)] * N
        E = self.E
        for a in range(N):
            s = sp.Integer(0)
            for b in range(N):
                for c in range(N):
                    for dd in range(N):
                        if E[a][b][c][dd] != 0:
                            s += 2 * E[a][b][c][dd] * self.geo.covd2(k, dd, b, c)
                        if k[b, c] != 0:
                            s -= 2 * k[b, c] * self._covd_up4(E, dd, a, b, c, dd)
            out[a] = sp.cancel(sp.together(s))
        return out

    def delta_theta(self, h, k, lb_h=None):
        """delta_h theta^a(g; k), k held fixed."""
        geo, g, gi, alpha = self.geo, self.g, self.gi, self.alpha
        cancel = lambda e: sp.cancel(sp.together(e))  # noqa: E731
        lb = lb_h if lb_h is not None else LinearizedBach(geo)
        if not hasattr(lb, "dC") or lb_h is None:
            lb.build(h)
        dG = lb.dG
        dC_low = lb.dC
        hup = sp.Matrix(N, N, lambda a, b: cancel(
            sum(gi[a, c] * gi[b, d] * h[c, d] for c in range(N) for d in range(N))))
        E = self.E
        # delta E^{abcd} = -h^a_p E^{pbcd} - ... + 2 alpha (raised dC)
        hmix = sp.Matrix(N, N, lambda a, b: cancel(
            sum(gi[a, c] * h[c, b] for c in range(N))))  # h^a_b
        dE = [[[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]
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
                                            s += 2 * alpha * w * dC_low[p][q][u][v]
                        for p in range(N):
                            s -= (hmix[a, p] * E[p][b][c][d] + hmix[b, p] * E[a][p][c][d]
                                  + hmix[c, p] * E[a][b][p][d] + hmix[d, p] * E[a][b][c][p])
                        dE[a][b][c][d] = cancel(s)

        def d_cov_k(dd, b, c):
            # delta[(nabla_d k)_{bc}] = -dG^e_{db} k_{ec} - dG^e_{dc} k_{be}
            s = sp.Integer(0)
            for e in range(N):
                s -= dG[e][dd][b] * k[e, c] + dG[e][dd][c] * k[b, e]
            return s

        def d_covd_up4E(a, b, c):
            # delta[(nabla_d E)^{abcd}] (d contracted with derivative index)
            s = sp.Integer(0)
            for dd in range(N):
                s += self._covd_up4(dE, dd, a, b, c, dd)
                for p in range(N):
                    s += (dG[a][dd][p] * E[p][b][c][dd] + dG[b][dd][p] * E[a][p][c][dd]
                          + dG[c][dd][p] * E[a][b][p][dd] + dG[dd][dd][p] * E[a][b][c][p])
            return s

        out = [sp.Integer(0)] * N
        for a in range(N):
            s = sp.Integer(0)
            for b in range(N):
                for c in range(N):
                    for dd in range(N):
                        if dE[a][b][c][dd] != 0:
                            s += 2 * dE[a][b][c][dd] * geo.covd2(k, dd, b, c)
                        if E[a][b][c][dd] != 0:
                            s += 2 * E[a][b][c][dd] * d_cov_k(dd, b, c)
                    if k[b, c] != 0:
                        s -= 2 * k[b, c] * d_covd_up4E(a, b, c)
            out[a] = cancel(s)
        return out

    def omega(self, h1, h2):
        """corrected symplectic current vector omega^a(h1, h2)."""
        gi = self.gi
        th1 = self.theta(h1)
        th2 = self.theta(h2)
        d1th2 = self.delta_theta(h1, h2)
        d2th1 = self.delta_theta(h2, h1)
        tr1 = sum(gi[a, b] * h1[a, b] for a in range(N) for b in range(N))
        tr2 = sum(gi[a, b] * h2[a, b] for a in range(N) for b in range(N))
        return [
            sp.simplify(sp.cancel(sp.together(
                d1th2[a] - d2th1[a]
                + sp.Rational(1, 2) * tr1 * th2[a] - sp.Rational(1, 2) * tr2 * th1[a])))
            for a in range(N)
        ]
