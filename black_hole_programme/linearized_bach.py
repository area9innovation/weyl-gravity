"""First-order linearized Bach operator, exact sympy.

Computes delta B_ab[h] as a LINEAR operator in the perturbation h against
background covariant derivatives — no epsilon-expansion of the nonlinear
pipeline.  All conventions are the frozen ones of `weyl_geometry.py`.

Building blocks (background nabla, indices raised with the background
inverse metric; h^a_b := g^{ac} h_{cb}, trh := g^{ab} h_{ab}):

    delta Gamma^a_bc = (1/2) g^{ad} (nabla_b h_dc + nabla_c h_bd - nabla_d h_bc)
    delta R^a_bcd    = nabla_c delta Gamma^a_db - nabla_d delta Gamma^a_cb
    delta R_bd       = delta R^a_bad
    delta Rlow_abcd  = h_ae R^e_bcd + g_ae delta R^e_bcd
    delta Rsc        = -h^{bd} R_bd + g^{bd} delta R_bd
    delta P_ab       = (1/2) (delta R_ab - (delta Rsc g_ab + Rsc h_ab)/6)
    delta C          = delta Rlow - KN(delta P, g) - KN(P, h)
    delta B_ab       = variation of nabla^c nabla^d C_acbd + (1/2) R^cd C_acbd
                       including all delta Gamma and delta g^{-1} terms.

Validation controls live in the certificate producers that use this
module: the conformal direction gives delta B = 0 exactly, family-tangent
directions give delta B = 0, and a mutation direction reproduces the
epsilon-derivative of the exact nonlinear Bach tensor.
"""

from __future__ import annotations

import sympy as sp

N = 4


class LinearizedBach:
    def __init__(self, geo):
        """geo: a weyl_geometry.Geometry instance (background)."""
        self.geo = geo
        self.g = geo.g
        self.gi = geo.ginv
        self.coords = geo.coords

    # -- background helpers -----------------------------------------------

    def covd1(self, T, e, a):
        s = sp.diff(T[a], self.coords[e])
        G = self.geo.Gamma
        for hh in range(N):
            s -= G[hh][e][a] * T[hh]
        return s

    def covd2(self, T, e, a, b):
        return self.geo.covd2(T, e, a, b)

    def covd3(self, T, e, a, b, c):
        return self.geo.covd3(T, e, a, b, c)

    def covd4(self, T, e, a, b, c, d):
        return self.geo.covd4(T, e, a, b, c, d)

    # -- first-order objects ----------------------------------------------

    def build(self, h):
        geo, g, gi = self.geo, self.g, self.gi
        cancel = lambda e: sp.cancel(sp.together(e))  # noqa: E731

        hup = sp.Matrix(N, N, lambda a, b: cancel(
            sum(gi[a, c] * gi[b, d] * h[c, d] for c in range(N) for d in range(N)
                if gi[a, c] != 0 and gi[b, d] != 0)))
        dginv = -hup  # delta g^{ab} = -h^{ab}

        # delta Gamma^a_bc
        dG = [[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)]
        for a in range(N):
            for b in range(N):
                for c in range(b, N):
                    s = sp.Integer(0)
                    for d in range(N):
                        if gi[a, d] == 0:
                            continue
                        s += gi[a, d] * (
                            self.covd2(h, b, d, c) + self.covd2(h, c, b, d)
                            - self.covd2(h, d, b, c)
                        )
                    val = cancel(s / 2)
                    dG[a][b][c] = val
                    dG[a][c][b] = val
        self.dG = dG

        # nabla_e (delta Gamma)^a_{bc}: treat dG as (1,2) tensor
        def cov_dG(e, a, b, c):
            s = sp.diff(dG[a][b][c], self.coords[e])
            G = geo.Gamma
            for hh in range(N):
                s += G[a][e][hh] * dG[hh][b][c]
                s -= G[hh][e][b] * dG[a][hh][c] + G[hh][e][c] * dG[a][b][hh]
            return s

        # delta R^a_bcd
        dRup = [[[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for d in range(c + 1, N):
                        v = cancel(cov_dG(c, a, d, b) - cov_dG(d, a, c, b))
                        dRup[a][b][c][d] = v
                        dRup[a][b][d][c] = -v

        # delta Ricci and scalar
        dRic = sp.Matrix(N, N, lambda b, d: cancel(
            sum(dRup[a][b][a][d] for a in range(N))))
        Ric, Rsc = geo.Ricci, geo.Rscalar
        dRsc = cancel(
            sum(dginv[b, d] * Ric[b, d] for b in range(N) for d in range(N) if dginv[b, d] != 0)
            + sum(gi[b, d] * dRic[b, d] for b in range(N) for d in range(N) if gi[b, d] != 0))

        # delta Riemann (all covariant)
        dRlow = [[[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for d in range(N):
                        s = sp.Integer(0)
                        for e in range(N):
                            if h[a, e] != 0:
                                s += h[a, e] * geo.Riemann_up[e][b][c][d]
                            if g[a, e] != 0:
                                s += g[a, e] * dRup[e][b][c][d]
                        dRlow[a][b][c][d] = cancel(s)

        # Schouten and its variation
        P = sp.Matrix(N, N, lambda a, b: cancel((Ric[a, b] - Rsc / 6 * g[a, b]) / 2))
        dP = sp.Matrix(N, N, lambda a, b: cancel(
            (dRic[a, b] - (dRsc * g[a, b] + Rsc * h[a, b]) / 6) / 2))

        def KN(Pm, gm, a, b, c, d):
            return (Pm[a, c] * gm[b, d] + Pm[b, d] * gm[a, c]
                    - Pm[a, d] * gm[b, c] - Pm[b, c] * gm[a, d])

        # delta Weyl (all covariant)
        dC = [[[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for d in range(N):
                        dC[a][b][c][d] = cancel(
                            dRlow[a][b][c][d] - KN(dP, g, a, b, c, d) - KN(P, h, a, b, c, d))
        self.dC = dC
        self.dRic = dRic
        self.dRsc = dRsc
        self.dginv = dginv
        C = geo.Weyl

        # variation of the first covariant derivative:
        # delta[(nabla_f C)_{acbd}] = (nabla_f dC)_{acbd}
        #    - dG^h_{fa} C_{hcbd} - dG^h_{fc} C_{ahbd}
        #    - dG^h_{fb} C_{achd} - dG^h_{fd} C_{acbh}
        def d_covC(f, a, c, b, d):
            s = self.covd4(dC, f, a, c, b, d)
            for hh in range(N):
                s -= (dG[hh][f][a] * C[hh][c][b][d] + dG[hh][f][c] * C[a][hh][b][d]
                      + dG[hh][f][b] * C[a][c][hh][d] + dG[hh][f][d] * C[a][c][b][hh])
            return s

        # background A_{acb} = nabla^d C_{acbd} and its variation:
        # delta A_{acb} = dginv^{df} (nabla_f C)_{acbd} + g^{df} delta[(nabla_f C)_{acbd}]
        A = [[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)]
        dA = [[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)]
        for a in range(N):
            for c in range(N):
                for b in range(N):
                    s0 = sp.Integer(0)
                    s1 = sp.Integer(0)
                    for d in range(N):
                        for f in range(N):
                            if gi[d, f] != 0:
                                s0 += gi[d, f] * self.covd4(C, f, a, c, b, d)
                                s1 += gi[d, f] * d_covC(f, a, c, b, d)
                            if dginv[d, f] != 0:
                                s1 += dginv[d, f] * self.covd4(C, f, a, c, b, d)
                    A[a][c][b] = cancel(s0)
                    dA[a][c][b] = cancel(s1)

        # delta[(nabla_e A)_{acb}] = (nabla_e dA)_{acb}
        #    - dG^h_{ea} A_{hcb} - dG^h_{ec} A_{ahb} - dG^h_{eb} A_{ach}
        def d_covA(e, a, c, b):
            s = self.covd3(dA, e, a, c, b)
            for hh in range(N):
                s -= (dG[hh][e][a] * A[hh][c][b] + dG[hh][e][c] * A[a][hh][b]
                      + dG[hh][e][b] * A[a][c][hh])
            return s

        # delta B_ab
        dB = sp.zeros(N, N)
        for a in range(N):
            for b in range(N):
                s = sp.Integer(0)
                for c in range(N):
                    for e in range(N):
                        if gi[c, e] != 0:
                            s += gi[c, e] * d_covA(e, a, c, b)
                        if dginv[c, e] != 0:
                            s += dginv[c, e] * self.covd3(A, e, a, c, b)
                # (1/2) delta[R^{cd} C_acbd]
                for c in range(N):
                    for d in range(N):
                        Rup = sp.Integer(0)
                        dRupcd = sp.Integer(0)
                        for e in range(N):
                            for f in range(N):
                                w = gi[c, e] * gi[d, f]
                                if w != 0:
                                    Rup += w * Ric[e, f]
                                    dRupcd += w * dRic[e, f]
                                dw = dginv[c, e] * gi[d, f] + gi[c, e] * dginv[d, f]
                                if dw != 0:
                                    dRupcd += dw * Ric[e, f]
                        if Rup != 0:
                            s += sp.Rational(1, 2) * Rup * dC[a][c][b][d]
                        if dRupcd != 0:
                            s += sp.Rational(1, 2) * dRupcd * C[a][c][b][d]
                dB[a, b] = cancel(s)
        return dB
