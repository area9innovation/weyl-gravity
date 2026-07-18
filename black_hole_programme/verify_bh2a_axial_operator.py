"""Structurally independent verifier for BH2A_AXIAL_OPERATOR.

The frozen first-order formulas of `linearized_bach.LinearizedBach` are
re-run on the verifier-side Schouten/Kulkarni--Nomizu curvature pipeline
(`verify_bh0_background.curvature`) through an adapter with its own
covariant-derivative code.  The verifier then independently re-checks:

- the l=0 mutation control against the exact nonlinear Bach tensor of the
  verifier-side `bach()` (nonzero, componentwise);
- the axial l=2 nonzero-component set, trace identity, and Bianchi-type
  divergence identity;
- the Regge--Wheeler master-equation reproduction with potential
  V = B (6/r^2 - 6 m/r^3);
- the exact branch-split identity delta B = (1/2) Box delta Ric
  + C . delta Ric with its own Box and Weyl-contraction assembly.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

import verify_bh0_background as vb
from linearized_bach import LinearizedBach

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2A_AXIAL_OPERATOR.json"
SCHEMA = HERE / "schema" / "bh2a-axial-operator-v1.schema.json"

N = 4


class BH2AVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise BH2AVerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class VbGeo:
    """Adapter exposing the Geometry interface on the verifier pipeline."""

    def __init__(self, coords, g):
        self.coords = coords
        self.g = g
        self.ginv, self.Gamma, self.Ricci, self.Rscalar, C = vb.curvature(coords, g)
        self.Weyl = C
        # Riemann up from the verifier pipeline: recompute directly
        d = sp.diff
        G = self.Gamma
        Rup = [[[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for e in range(c + 1, N):
                        s = d(G[a][e][b], coords[c]) - d(G[a][c][b], coords[e])
                        for f in range(N):
                            s += G[a][c][f] * G[f][e][b] - G[a][e][f] * G[f][c][b]
                        s = sp.cancel(sp.together(s))
                        Rup[a][b][c][e] = s
                        Rup[a][b][e][c] = -s
        self.Riemann_up = Rup

    def covd2(self, T, e, a, b):
        s = sp.diff(T[a, b], self.coords[e])
        for h in range(N):
            s -= self.Gamma[h][e][a] * T[h, b] + self.Gamma[h][e][b] * T[a, h]
        return s

    def covd3(self, T, e, a, b, c):
        s = sp.diff(T[a][b][c], self.coords[e])
        for h in range(N):
            s -= (self.Gamma[h][e][a] * T[h][b][c] + self.Gamma[h][e][b] * T[a][h][c]
                  + self.Gamma[h][e][c] * T[a][b][h])
        return s

    def covd4(self, T, e, a, b, c, f):
        s = sp.diff(T[a][b][c][f], self.coords[e])
        for h in range(N):
            s -= (self.Gamma[h][e][a] * T[h][b][c][f] + self.Gamma[h][e][b] * T[a][h][c][f]
                  + self.Gamma[h][e][c] * T[a][b][h][f] + self.Gamma[h][e][f] * T[a][b][c][h])
        return s


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    for key in ("machinery", "engine"):
        _check(prov[f"{key}_sha256"] == _sha256(ROOT / prov[f"{key}_path"]), f"{key} hash mismatch")
    _check(
        prov["bh0_certificate_sha256"] == _sha256(ROOT / prov["bh0_certificate"]),
        "BH-0 certificate hash mismatch",
    )

    t, ph = sp.symbols("t phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    th = sp.Symbol("theta", positive=True)
    m = sp.Symbol("m", positive=True)
    w = sp.Symbol("omega")
    eps = sp.Symbol("epsilon")
    coords = [t, r, x, ph]

    # l=0 mutation control on the verifier pipeline (diagonal chart)
    tc = [t, r, th, ph]
    beta, gam, kk = sp.symbols("beta gamma k")
    Bfx = (1 - 3 * beta * gam - beta * (2 - 3 * beta * gam) / r + gam * r - kk * r**2).subs(
        {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), kk: sp.Rational(1, 19)})
    Beps = Bfx + eps / (7 * r**2)
    g_eps = sp.diag(-Beps, 1 / Beps, r**2, r**2 * sp.sin(th) ** 2)
    Bach_eps = vb.bach(tc, g_eps)
    target = sp.Matrix(4, 4, lambda i, j: sp.diff(Bach_eps[i, j], eps).subs(eps, 0))
    geo_fx = VbGeo(tc, sp.diag(-Bfx, 1 / Bfx, r**2, r**2 * sp.sin(th) ** 2))
    lb_fx = LinearizedBach(geo_fx)
    h_mut = sp.Matrix(4, 4, lambda i, j: sp.diff(g_eps[i, j], eps).subs(eps, 0))
    dB_mut = lb_fx.build(h_mut)
    _check(any(sp.simplify(target[i, j]) != 0 for i in range(4) for j in range(4)),
           "mutation target zero")
    _check(all(sp.simplify(dB_mut[i, j] - target[i, j]) == 0 for i in range(4) for j in range(4)),
           "mutation control fails on verifier pipeline")
    print("[control] l=0 mutation matches verifier-side exact Bach", flush=True)

    # axial rows on the verifier pipeline
    B0 = 1 - 2 * m / r
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = VbGeo(coords, g0)
    lb = LinearizedBach(geo0)
    h0 = sp.Function("h0")(t, r)
    h1 = sp.Function("h1")(t, r)
    S = -3 * x * (1 - x**2)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0 * S
    h[1, 3] = h[3, 1] = h1 * S
    dB = lb.build(h)
    nz = {(i, j) for i in range(4) for j in range(i, 4)
          if sp.cancel(sp.together(dB[i, j])) != 0}
    _check(nz == {(0, 3), (1, 3), (2, 3)}, f"unexpected nonzero rows {nz}")
    gi = geo0.ginv
    _check(sp.simplify(sum(gi[a, b] * dB[a, b] for a in range(4) for b in range(4))) == 0,
           "trace identity fails")
    for b in range(4):
        s = sp.Integer(0)
        for a in range(4):
            for e in range(4):
                if gi[a, e] != 0:
                    s += gi[a, e] * geo0.covd2(dB, e, a, b)
        _check(sp.simplify(sp.cancel(sp.together(s))) == 0, f"divergence identity fails b={b}")
    print("[axial] rows, trace, divergence verified", flush=True)

    # Regge--Wheeler reproduction
    dRic = lb.dRic
    R1 = sp.cancel(sp.cancel(sp.together(dRic[1, 3])) / S)
    R2 = sp.cancel(sp.cancel(sp.together(dRic[2, 3])) / (3 * (x - 1) * (x + 1)))
    _check(not R1.has(x) and not R2.has(x), "angular stripping failed")
    H0 = sp.Function("H0")(r)
    H1 = sp.Function("H1")(r)
    four = {h0: H0 * sp.exp(sp.I * w * t), h1: H1 * sp.exp(sp.I * w * t)}
    E = sp.exp(sp.I * w * t)
    R1f = sp.cancel(sp.together(sp.expand(R1.subs(four).doit() / E)))
    R2f = sp.cancel(sp.together(sp.expand(R2.subs(four).doit() / E)))
    H0sol = sp.solve(sp.Eq(R2f, 0), H0)[0]
    resid = sp.cancel(sp.together(
        R1f.subs({sp.Derivative(H0, r): sp.diff(H0sol, r), H0: H0sol}).doit()))
    num, _den = sp.fraction(resid)
    _check(not sp.expand(num).has(H0), "H0 not eliminated")
    psi = sp.Function("psi")(r)
    n2, _ = sp.fraction(sp.cancel(sp.together(sp.expand(num).subs(H1, r * psi / B0).doit())))
    V = B0 * (6 / r**2 - 6 * m / r**3)
    master = sp.expand(B0 * sp.diff(B0 * sp.diff(psi, r), r) + (w**2 - V) * psi)
    ratio = sp.cancel(sp.together(sp.expand(n2) / master))
    _check(not ratio.has(psi) and sp.simplify(ratio + r**6) == 0, "RW reproduction fails")
    print("[benchmark] Regge-Wheeler master equation reproduced", flush=True)

    # branch-split identity with verifier-side box and Weyl contraction
    X = dRic
    G = geo0.Gamma
    DX = [[[sp.cancel(sp.together(geo0.covd2(X, e, a, b))) for b in range(4)]
           for a in range(4)] for e in range(4)]

    def covd2X2(e, f, a, b):
        s = sp.diff(DX[f][a][b], coords[e])
        for hh in range(4):
            s -= (G[hh][e][f] * DX[hh][a][b] + G[hh][e][a] * DX[f][hh][b]
                  + G[hh][e][b] * DX[f][a][hh])
        return s

    boxX = sp.Matrix(4, 4, lambda a, b: sp.cancel(sp.together(
        sum(gi[e, f] * covd2X2(e, f, a, b) for e in range(4) for f in range(4)
            if gi[e, f] != 0))))
    Xup = sp.Matrix(4, 4, lambda c, d: sp.cancel(
        sum(gi[c, e] * gi[d, f] * X[e, f] for e in range(4) for f in range(4))))
    CX = sp.Matrix(4, 4, lambda a, b: sp.cancel(sp.together(
        sum(geo0.Weyl[a][c][b][d] * Xup[c, d] for c in range(4) for d in range(4)
            if Xup[c, d] != 0))))
    for a in range(4):
        for b in range(a, 4):
            _check(
                sp.simplify(sp.expand(sp.cancel(sp.together(
                    dB[a, b] - boxX[a, b] / 2 - CX[a, b])))) == 0,
                f"branch-split identity fails ({a},{b})",
            )
    print("[split] delta B = (1/2) Box dRic + C.dRic verified", flush=True)

    print("BH2A_AXIAL_OPERATOR: all independent checks passed")


if __name__ == "__main__":
    verify_certificate()
