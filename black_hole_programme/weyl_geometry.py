"""Exact curvature and Bach-tensor engine for the black-hole programme.

Frozen conventions (BH-0, do not change without a new schema version):

- coordinates and metric are supplied explicitly; signature is (-,+,+,+);
- Christoffel:  Gamma^a_{bc} = (1/2) g^{ae} (d_b g_{ec} + d_c g_{eb} - d_e g_{bc});
- Riemann:      R^a_{bcd} = d_c Gamma^a_{db} - d_d Gamma^a_{cb}
                            + Gamma^a_{ce} Gamma^e_{db} - Gamma^a_{de} Gamma^e_{cb};
- Ricci:        R_{bd} = R^a_{bad};   scalar R = g^{bd} R_{bd};
- Weyl (4D):    C_{abcd} = R_{abcd}
                  - (g_{ac} R_{bd} - g_{ad} R_{bc} + g_{bd} R_{ac} - g_{bc} R_{ad})/2
                  + R (g_{ac} g_{bd} - g_{ad} g_{bc})/6;
- Bach:         B_{ab} = nabla^c nabla^d C_{acbd} + (1/2) R^{cd} C_{acbd};
- action:       S_W = alpha * Integral( sqrt(-g) C_{abcd} C^{abcd} ).

Linearized on Minkowski with transverse-traceless h these conventions reduce
to B_mn = d^r d^s C_mrns, matching the frozen flat certificate
`bridge/certificates/flat_tt_bach_operator.json` (the R^{cd} C term is second
order around a flat background).

All arithmetic is exact sympy; no floating point enters any canonical form.
"""

from __future__ import annotations

import sympy as sp

N = 4


def _zeros4():
    return [[[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]


class Geometry:
    """Exact curvature data for one metric in one chart."""

    def __init__(self, coords, metric: sp.Matrix):
        if metric.shape != (N, N):
            raise ValueError("metric must be 4x4")
        self.coords = list(coords)
        self.g = metric
        self.ginv = metric.inv()
        self._d = lambda expr, i: sp.diff(expr, self.coords[i])
        self._christoffel()
        self._riemann()
        self._ricci()
        self._weyl()

    # -- curvature ---------------------------------------------------------

    def _christoffel(self):
        d, g, ginv = self._d, self.g, self.ginv
        G = [[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)]
        for a in range(N):
            for b in range(N):
                for c in range(b, N):
                    s = sp.Integer(0)
                    for e in range(N):
                        if ginv[a, e] == 0:
                            continue
                        s += ginv[a, e] * (d(g[e, b], c) + d(g[e, c], b) - d(g[b, c], e))
                    s = sp.cancel(sp.together(s / 2))
                    G[a][b][c] = s
                    G[a][c][b] = s
        self.Gamma = G

    def _riemann(self):
        d, G = self._d, self.Gamma
        Rup = _zeros4()
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for e in range(c + 1, N):
                        s = d(G[a][e][b], c) - d(G[a][c][b], e)
                        for f in range(N):
                            s += G[a][c][f] * G[f][e][b] - G[a][e][f] * G[f][c][b]
                        s = sp.cancel(sp.together(s))
                        Rup[a][b][c][e] = s
                        Rup[a][b][e][c] = -s
        self.Riemann_up = Rup
        Rlow = _zeros4()
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for e in range(N):
                        s = sp.Integer(0)
                        for f in range(N):
                            if self.g[a, f] != 0:
                                s += self.g[a, f] * Rup[f][b][c][e]
                        Rlow[a][b][c][e] = sp.cancel(sp.together(s))
        self.Riemann = Rlow

    def _ricci(self):
        Ric = sp.zeros(N, N)
        for b in range(N):
            for e in range(N):
                s = sp.Integer(0)
                for a in range(N):
                    s += self.Riemann_up[a][b][a][e]
                Ric[b, e] = sp.cancel(sp.together(s))
        self.Ricci = Ric
        self.Rscalar = sp.cancel(
            sp.together(
                sum(self.ginv[a, b] * Ric[a, b] for a in range(N) for b in range(N))
            )
        )

    def _weyl(self):
        g, Ric, R = self.g, self.Ricci, self.Rscalar
        C = _zeros4()
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for e in range(N):
                        s = (
                            self.Riemann[a][b][c][e]
                            - sp.Rational(1, 2)
                            * (
                                g[a, c] * Ric[b, e]
                                - g[a, e] * Ric[b, c]
                                + g[b, e] * Ric[a, c]
                                - g[b, c] * Ric[a, e]
                            )
                            + R / 6 * (g[a, c] * g[b, e] - g[a, e] * g[b, c])
                        )
                        C[a][b][c][e] = sp.cancel(sp.together(s))
        self.Weyl = C

    # -- derived operators -------------------------------------------------

    def covd4(self, T, e, a, b, c, f):
        """(nabla_e T)_{abcf} for a covariant 4-tensor T."""
        s = self._d(T[a][b][c][f], e)
        G = self.Gamma
        for h in range(N):
            s -= (
                G[h][e][a] * T[h][b][c][f]
                + G[h][e][b] * T[a][h][c][f]
                + G[h][e][c] * T[a][b][h][f]
                + G[h][e][f] * T[a][b][c][h]
            )
        return s

    def covd3(self, T, e, a, b, c):
        """(nabla_e T)_{abc} for a covariant 3-tensor T."""
        s = self._d(T[a][b][c], e)
        G = self.Gamma
        for h in range(N):
            s -= G[h][e][a] * T[h][b][c] + G[h][e][b] * T[a][h][c] + G[h][e][c] * T[a][b][h]
        return s

    def covd2(self, T, e, a, b):
        """(nabla_e T)_{ab} for a covariant 2-tensor T (sympy Matrix)."""
        s = self._d(T[a, b], e)
        G = self.Gamma
        for h in range(N):
            s -= G[h][e][a] * T[h, b] + G[h][e][b] * T[a, h]
        return s

    def bach(self) -> sp.Matrix:
        """B_{ab} = nabla^c nabla^d C_{acbd} + (1/2) R^{cd} C_{acbd}, exact."""
        ginv, C, Ric = self.ginv, self.Weyl, self.Ricci
        # A_{acb} = nabla^d C_{acbd}
        A = [[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)]
        for a in range(N):
            for c in range(N):
                for b in range(N):
                    s = sp.Integer(0)
                    for dd in range(N):
                        for f in range(N):
                            if ginv[dd, f] != 0:
                                s += ginv[dd, f] * self.covd4(C, f, a, c, b, dd)
                    A[a][c][b] = sp.cancel(sp.together(s))
        B = sp.zeros(N, N)
        for a in range(N):
            for b in range(N):
                s = sp.Integer(0)
                for c in range(N):
                    for e in range(N):
                        if ginv[c, e] != 0:
                            s += ginv[c, e] * self.covd3(A, e, a, c, b)
                for c in range(N):
                    for dd in range(N):
                        Rcd = sp.Integer(0)
                        for e in range(N):
                            for f in range(N):
                                if ginv[c, e] != 0 and ginv[dd, f] != 0:
                                    Rcd += ginv[c, e] * ginv[dd, f] * Ric[e, f]
                        if Rcd != 0:
                            s += sp.Rational(1, 2) * Rcd * C[a][c][b][dd]
                B[a, b] = sp.simplify(sp.cancel(sp.together(s)))
        return B

    def einstein_defect(self) -> sp.Matrix:
        """Trace-free Ricci E_{ab} = R_{ab} - (R/4) g_{ab}; zero iff Einstein."""
        E = sp.zeros(N, N)
        for a in range(N):
            for b in range(N):
                E[a, b] = sp.simplify(self.Ricci[a, b] - self.Rscalar / 4 * self.g[a, b])
        return E

    def invariants(self) -> dict:
        """Exact scalar invariants: R, Ricci^2, Weyl^2, Kretschmann."""
        ginv = self.ginv
        ric2 = sp.Integer(0)
        for a in range(N):
            for b in range(N):
                up = sp.Integer(0)
                for c in range(N):
                    for e in range(N):
                        if ginv[a, c] != 0 and ginv[b, e] != 0:
                            up += ginv[a, c] * ginv[b, e] * self.Ricci[c, e]
                ric2 += up * self.Ricci[a, b]
        weyl2 = sp.Integer(0)
        riem2 = sp.Integer(0)
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for e in range(N):
                        Cup = sp.Integer(0)
                        Rup = sp.Integer(0)
                        for p in range(N):
                            for q in range(N):
                                for u in range(N):
                                    for v in range(N):
                                        w = ginv[a, p] * ginv[b, q] * ginv[c, u] * ginv[e, v]
                                        if w != 0:
                                            Cup += w * self.Weyl[p][q][u][v]
                                            Rup += w * self.Riemann[p][q][u][v]
                        weyl2 += Cup * self.Weyl[a][b][c][e]
                        riem2 += Rup * self.Riemann[a][b][c][e]
        return {
            "R": sp.simplify(self.Rscalar),
            "RicciSq": sp.simplify(ric2),
            "WeylSq": sp.simplify(weyl2),
            "Kretschmann": sp.simplify(riem2),
        }


def static_spherical_metric(a_fun, b_fun, r, theta) -> sp.Matrix:
    """diag(-a(r), b(r), r^2, r^2 sin^2 theta): areal chart, pre-conformal-gauge."""
    return sp.diag(-a_fun, b_fun, r**2, r**2 * sp.sin(theta) ** 2)


def eddington_finkelstein_metric(B_fun, r, theta) -> sp.Matrix:
    """Ingoing EF chart (v, r, theta, phi): ds^2 = -B dv^2 + 2 dv dr + r^2 dOmega^2."""
    g = sp.zeros(4, 4)
    g[0, 0] = -B_fun
    g[0, 1] = g[1, 0] = sp.Integer(1)
    g[2, 2] = r**2
    g[3, 3] = r**2 * sp.sin(theta) ** 2
    return g


def mk_metric_function(beta, gamma, k, r):
    """Mannheim--Kazanas vacuum family, our frozen parametrization.

    B(r) = 1 - 3 beta gamma - beta (2 - 3 beta gamma)/r + gamma r - k r^2.

    Dictionary: identical to Mannheim--Kazanas (1989) (beta, gamma, k);
    Schwarzschild control: beta = m, gamma = k = 0; Schwarzschild--(A)dS:
    gamma = 0, k = Lambda/3.
    """
    return 1 - 3 * beta * gamma - beta * (2 - 3 * beta * gamma) / r + gamma * r - k * r**2
