"""Structurally independent verifier for BH1B_DYNAMICAL_EXTENSION.

Recomputes the certified dynamical statements on the verifier-side
Schouten/Kulkarni--Nomizu curvature pipeline (`verify_bh0_background`),
with its own compact theta/Q/2-form assembly:

- Noether identity and identity-route diffeo charge annihilation
  (both backgrounds, arbitrary a(t,r), b(t,r));
- conformal charge annihilation on Schwarzschild (symbolic m, arbitrary
  omega(t,r)) through an independent epsilon-geometry variation;
- entropy conformal invariance at the fixture;
- theta audit (conformal density invariance);
- nonzero bare aperture at the fixture.

This is the exhaustive rail; expect a few minutes of exact computation.
"""

from __future__ import annotations

import hashlib
import json
from itertools import combinations, permutations
from pathlib import Path

import jsonschema
import sympy as sp

import verify_bh0_background as vb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH1B_DYNAMICAL_EXTENSION.json"
SCHEMA = HERE / "schema" / "bh1b-dynamical-extension-v1.schema.json"

N = 4


class BH1BVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise BH1BVerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


_SIGN = {}
for p in permutations((0, 1, 2, 3)):
    s = 1
    pl = list(p)
    for i in range(4):
        for j in range(i + 1, 4):
            if pl[i] > pl[j]:
                s = -s
    _SIGN[p] = s


class Pipe:
    """Verifier-side pipeline wrapper around vb.curvature."""

    def __init__(self, coords, g, alpha):
        self.coords, self.g, self.alpha = coords, g, alpha
        self.ginv, self.Gam, self.Ric, self.Rsc, self.C = vb.curvature(coords, g)
        self.sqrtg = sp.sqrt(-g.det())

    def E(self):
        gi, C = self.ginv, self.C
        E = [[[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for d in range(N):
                        s = sp.Integer(0)
                        for pp in range(N):
                            for q in range(N):
                                for u in range(N):
                                    for v in range(N):
                                        w = gi[a, pp] * gi[b, q] * gi[c, u] * gi[d, v]
                                        if w != 0:
                                            s += w * C[pp][q][u][v]
                        E[a][b][c][d] = sp.cancel(2 * self.alpha * s)
        return E

    def covE(self, E, e, a, b, c, d):
        s = sp.diff(E[a][b][c][d], self.coords[e])
        G = self.Gam
        for h in range(N):
            s += (G[a][e][h] * E[h][b][c][d] + G[b][e][h] * E[a][h][c][d]
                  + G[c][e][h] * E[a][b][h][d] + G[d][e][h] * E[a][b][c][h])
        return s

    def theta(self, E, dg):
        out = [sp.Integer(0)] * N

        def covdg(e, b, c):
            s = sp.diff(dg[b, c], self.coords[e])
            for h in range(N):
                s -= self.Gam[h][e][b] * dg[h, c] + self.Gam[h][e][c] * dg[b, h]
            return s

        for a in range(N):
            s = sp.Integer(0)
            for b in range(N):
                for c in range(N):
                    for dd in range(N):
                        if E[a][b][c][dd] != 0:
                            s += 2 * E[a][b][c][dd] * covdg(dd, b, c)
                        if dg[b, c] != 0:
                            s -= 2 * dg[b, c] * self.covE(E, dd, a, b, c, dd)
            out[a] = sp.cancel(sp.together(s))
        return out

    def Qup(self, E, chi):
        chi_low = [sum(self.g[d, e] * chi[e] for e in range(N)) for d in range(N)]

        def nchi(cc, dd):
            s = sp.diff(chi_low[dd], self.coords[cc])
            for h in range(N):
                s -= self.Gam[h][cc][dd] * chi_low[h]
            return s

        Q = [[sp.Integer(0)] * N for _ in range(N)]
        for a in range(N):
            for b in range(a + 1, N):
                s = sp.Integer(0)
                for cc in range(N):
                    for dd in range(N):
                        if E[a][b][cc][dd] != 0:
                            s -= E[a][b][cc][dd] * nchi(cc, dd)
                        if chi_low[dd] != 0:
                            s += 2 * chi_low[dd] * self.covE(E, cc, a, b, cc, dd)
                s = sp.cancel(sp.together(s))
                Q[a][b] = s
                Q[b][a] = -s
        return Q

    def qform(self, Qup):
        out = {}
        for c in range(N):
            for d in range(c + 1, N):
                s = sp.Integer(0)
                for a in range(N):
                    for b in range(N):
                        if len({a, b, c, d}) == 4:
                            s += _SIGN[(a, b, c, d)] * Qup[a][b]
                out[(c, d)] = sp.cancel(sp.together(self.sqrtg * s))
        return out

    def weyl2(self):
        gi, C = self.ginv, self.C
        s = sp.Integer(0)
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for e in range(N):
                        up = sp.Integer(0)
                        for pp in range(N):
                            for q in range(N):
                                for u in range(N):
                                    for v in range(N):
                                        w = gi[a, pp] * gi[b, q] * gi[c, u] * gi[e, v]
                                        if w != 0:
                                            up += w * C[pp][q][u][v]
                        s += up * C[a][b][c][e]
        return sp.simplify(s)


def lie_metric(coords, g, xi):
    h = sp.zeros(N, N)
    for i in range(N):
        for j in range(N):
            h[i, j] = sp.cancel(sum(
                xi[l] * sp.diff(g[i, j], coords[l])
                + g[l, j] * sp.diff(xi[l], coords[i])
                + g[i, l] * sp.diff(xi[l], coords[j]) for l in range(N)))
    return h


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


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    for key in ("machinery", "engine"):
        _check(prov[f"{key}_sha256"] == _sha256(ROOT / prov[f"{key}_path"]), f"{key} hash mismatch")
    _check(
        prov["bh1a_certificate_sha256"] == _sha256(ROOT / prov["bh1a_certificate"]),
        "BH-1A certificate hash mismatch",
    )

    t, ph = sp.symbols("t phi")
    r, th = sp.symbols("r theta", positive=True)
    alpha = sp.Symbol("alpha")
    eps = sp.Symbol("epsilon")
    m = sp.Symbol("m", positive=True)
    coords = [t, r, th, ph]
    om = sp.Function("omega")(t, r)
    a_f = sp.Function("a")(t, r)
    b_f = sp.Function("b")(t, r)

    def diag(B):
        return sp.diag(-B, 1 / B, r**2, r**2 * sp.sin(th) ** 2)

    beta, gam, kk = sp.symbols("beta gamma k")
    B_fix = (1 - 3 * beta * gam - beta * (2 - 3 * beta * gam) / r + gam * r - kk * r**2).subs(
        {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), kk: sp.Rational(1, 19)})

    for label, (B0, u0) in {
        "schwarzschild": (1 - 2 * m / r, 2 * m),
        "fixture": (B_fix, sp.Rational(-24, 19)),
    }.items():
        pipe = Pipe(coords, diag(B0), alpha)
        E = pipe.E()
        L = alpha * pipe.weyl2()
        chi = [u0, 0, 0, 0]
        xi = [a_f, b_f, 0, 0]
        # Noether identity
        h = lie_metric(coords, pipe.g, xi)
        thv = pipe.theta(E, h)
        Qxi = pipe.qform(pipe.Qup(E, xi))

        def qget(F, c, d):
            if c == d:
                return sp.Integer(0)
            return F[(c, d)] if c < d else -F[(d, c)]

        for trip in combinations(range(N), 3):
            bb, cc, dd = trip
            s = sp.Integer(0)
            for a in range(N):
                if len({a, bb, cc, dd}) == 4:
                    s += _SIGN[(a, bb, cc, dd)] * (thv[a] - L * xi[a])
            s = pipe.sqrtg * s
            dq = (sp.diff(qget(Qxi, cc, dd), coords[bb])
                  - sp.diff(qget(Qxi, bb, dd), coords[cc])
                  + sp.diff(qget(Qxi, bb, cc), coords[dd]))
            _check(sp.simplify(sp.cancel(sp.together(s - dq))) == 0,
                   f"Noether identity fails on {label} {trip}")
        # identity-route diffeo charge form
        Qchi = pipe.qform(pipe.Qup(E, chi))
        comm = [sum(chi[e] * sp.diff(xi[a], coords[e]) - xi[e] * sp.diff(chi[a], coords[e])
                    for e in range(N)) for a in range(N)]
        Qcomm = pipe.qform(pipe.Qup(E, comm))
        LxiQchi = lie_2form(coords, xi, Qchi)
        LchiQxi = lie_2form(coords, chi, Qxi)
        one = [sum(qget(Qxi, bb, d) * chi[bb] for bb in range(N) if bb != d) for d in range(N)]
        for c in range(N):
            for d in range(c + 1, N):
                s_eps = sp.Integer(0)
                for a in range(N):
                    for b in range(N):
                        if len({a, b, c, d}) == 4:
                            s_eps += _SIGN[(a, b, c, d)] * xi[a] * chi[b]
                val = (LxiQchi[(c, d)] + Qcomm[(c, d)] - LchiQxi[(c, d)]
                       - pipe.sqrtg * L * s_eps
                       + sp.diff(one[d], coords[c]) - sp.diff(one[c], coords[d]))
                _check(sp.simplify(sp.cancel(sp.together(val))) == 0,
                       f"diffeo charge form nonzero on {label} ({c},{d})")
        print(f"[{label}] Noether + diffeo annihilation verified", flush=True)

    # conformal charge annihilation on Schwarzschild, independent pipeline
    B0 = 1 - 2 * m / r
    g0 = diag(B0)
    pipe0 = Pipe(coords, g0, alpha)
    E0 = pipe0.E()
    chi = [2 * m, 0, 0, 0]
    h_conf = 2 * om * g0
    pipe_e = Pipe(coords, g0 + eps * h_conf, alpha)
    Qf_e = pipe_e.qform(pipe_e.Qup(pipe_e.E(), chi))
    thv = pipe0.theta(E0, h_conf)
    for c in range(N):
        for d in range(c + 1, N):
            it = sp.Integer(0)
            for a in range(N):
                for b in range(N):
                    if len({a, b, c, d}) == 4:
                        it += _SIGN[(a, b, c, d)] * thv[a] * chi[b]
            val = sp.diff(Qf_e[(c, d)], eps).subs(eps, 0) - pipe0.sqrtg * it
            _check(sp.simplify(sp.cancel(sp.together(val))) == 0,
                   f"conformal charge form nonzero ({c},{d})")
    print("[schwarzschild] conformal annihilation verified", flush=True)

    # theta audit: div theta[conformal] = 0
    div = sp.simplify(sum(sp.diff(pipe0.sqrtg * thv[a], coords[a]) for a in range(N)) / pipe0.sqrtg)
    _check(div == 0, "div theta [conformal] != 0")

    # entropy conformal invariance at the fixture (independent pipeline)
    gf = diag(B_fix)
    ge = (1 + 2 * eps * om) * gf
    pipe_s = Pipe(coords, ge, alpha)
    integrand = -2 * sp.pi * 4 * (
        pipe_s.ginv[0, 0] ** 2 * pipe_s.ginv[1, 1] ** 2 * pipe_s.C[0][1][0][1]
    ) * 2 * alpha * (sp.sqrt(-ge[0, 0] * ge[1, 1])) ** 2
    S_e = integrand * sp.sqrt(ge[2, 2] * ge[3, 3]) / sp.sin(th) * 4 * sp.pi
    _check(sp.simplify(sp.diff(S_e, eps).subs(eps, 0)) == 0, "delta_omega S != 0 at fixture")
    print("[fixture] entropy conformal invariance verified", flush=True)

    # bare aperture nonzero
    pipe_f = Pipe(coords, gf, alpha)
    Qb = pipe_f.qform(pipe_f.Qup(pipe_f.E(), [sp.Rational(-24, 19), 0, 0, 0]))
    bare = sp.simplify(sp.integrate(sp.integrate(Qb[(2, 3)], (th, 0, sp.pi)), (ph, 0, 2 * sp.pi)))
    _check(sp.simplify(bare - sp.sympify(payload["generator_extension"]["bare_aperture_fixture"],
                                         locals={"alpha": alpha, "pi": sp.pi, "r": r})) == 0,
           "bare aperture mismatch")
    _check(bare != 0, "bare aperture zero")

    print("BH1B_DYNAMICAL_EXTENSION: all independent checks passed")


if __name__ == "__main__":
    verify_certificate()
