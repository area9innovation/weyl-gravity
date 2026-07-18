"""Structurally independent verifier for BH2A_HORIZON_REACH.

Recomputes the entire horizon-reach analysis on the verifier-side
Schouten/Kulkarni--Nomizu curvature pipeline (via the VbGeo adapter of
`verify_bh2a_axial_operator`): carrier constraint regularity, operator
rows, regular-singular structure, residue spectrum, kernel dimension and
(P, Q)-profile independence, and the Regge--Wheeler benchmark.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2A_HORIZON_REACH.json"
SCHEMA = HERE / "schema" / "bh2a-horizon-reach-v1.schema.json"


class ReachVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ReachVerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    _check(prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]), "engine hash mismatch")
    _check(
        prov["bh2a_certificate_sha256"] == _sha256(ROOT / prov["bh2a_certificate"]),
        "BH-2A stage-1 certificate hash mismatch",
    )

    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    m = sp.Symbol("m", positive=True)
    w = sp.Symbol("omega")
    rho = sp.Symbol("rho", positive=True)
    coords = [v, r, x, ph]
    B0 = 1 - 2 * m / r
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = VbGeo(coords, g0)
    gi = geo0.ginv
    S = -3 * x * (1 - x**2)
    p = sp.Function("p")(v, r)
    q = sp.Function("q")(v, r)
    c = sp.Function("c")(v, r)
    psi = sp.zeros(4, 4)
    psi[0, 3] = psi[3, 0] = p * S
    psi[1, 3] = psi[3, 1] = q * S
    psi[2, 3] = psi[3, 2] = c * 3 * (x**2 - 1)
    sdiv = sum(gi[a, e] * geo0.covd2(psi, e, a, 3)
               for a in range(4) for e in range(4) if gi[a, e] != 0)
    csol = sp.solve(sp.Eq(sp.cancel(sp.together(sdiv)), 0), c)
    _check(len(csol) == 1, "constraint not uniquely solvable")
    _num, cden = sp.fraction(sp.cancel(sp.together(csol[0])))
    _check(not cden.has(r), "constraint solution not polynomial")
    psi2 = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(psi.subs(c, csol[0]).doit()[i, j])))
    G = geo0.Gamma
    DX = [[[sp.cancel(sp.together(geo0.covd2(psi2, e, a, b))) for b in range(4)]
           for a in range(4)] for e in range(4)]

    def covd2X2(e, f, a, b):
        s = sp.diff(DX[f][a][b], coords[e])
        for hh in range(4):
            s -= (G[hh][e][f] * DX[hh][a][b] + G[hh][e][a] * DX[f][hh][b]
                  + G[hh][e][b] * DX[f][a][hh])
        return s

    def Lrow(a, b):
        box = sum(gi[e, f] * covd2X2(e, f, a, b)
                  for e in range(4) for f in range(4) if gi[e, f] != 0)
        cx = sum(geo0.Weyl[a][cc][b][d]
                 * sum(gi[cc, e] * gi[d, f] * psi2[e, f] for e in range(4) for f in range(4))
                 for cc in range(4) for d in range(4))
        return sp.cancel(sp.together(box / 2 + cx))

    Lt = sp.cancel(Lrow(0, 3) / S)
    Lr = sp.cancel(Lrow(1, 3) / S)
    _check(not Lt.has(x) and not Lr.has(x), "angular stripping failed")
    P = sp.Function("P")(r)
    Q = sp.Function("Q")(r)
    four = {p: P * sp.exp(sp.I * w * v), q: Q * sp.exp(sp.I * w * v)}
    E = sp.exp(sp.I * w * v)
    Ltf = sp.expand(sp.cancel(sp.together(Lt.subs(four).doit() / E)))
    Lrf = sp.expand(sp.cancel(sp.together(Lr.subs(four).doit() / E)))
    D2P, D2Q = sp.Derivative(P, (r, 2)), sp.Derivative(Q, (r, 2))
    sol = sp.solve([sp.Eq(Ltf, 0), sp.Eq(Lrf, 0)], [D2P, D2Q], dict=True)
    _check(bool(sol), "second-derivative solve failed")
    s0 = sol[0]
    DP, DQ = sp.Derivative(P, r), sp.Derivative(Q, r)
    A = sp.zeros(4, 4)
    A[0, 1] = sp.Integer(1)
    A[2, 3] = sp.Integer(1)
    eP = sp.expand(s0[D2P])
    eQ = sp.expand(s0[D2Q])
    A[1, 0] = eP.coeff(P); A[1, 1] = eP.coeff(DP); A[1, 2] = eP.coeff(Q); A[1, 3] = eP.coeff(DQ)
    A[3, 0] = eQ.coeff(P); A[3, 1] = eQ.coeff(DP); A[3, 2] = eQ.coeff(Q); A[3, 3] = eQ.coeff(DQ)
    Ar = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(A[i, j].subs(r, 2 * m + rho))))
    for i in range(4):
        for j in range(4):
            _check(sp.simplify(sp.limit(rho**2 * Ar[i, j], rho, 0)) == 0, "irregular point")
    Res = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.limit(rho * Ar[i, j], rho, 0)))
    ev = {sp.nsimplify(sp.simplify(kk)): mult for kk, mult in Res.eigenvals().items()}
    expected = {sp.Integer(0): 2,
                sp.nsimplify(-4 * sp.I * m * w): 1,
                sp.nsimplify(-2 - 4 * sp.I * m * w): 1}
    _check(
        len(ev) == len(expected) and all(
            any(sp.simplify(kk - ee) == 0 and mult == emult for ee, emult in expected.items())
            for kk, mult in ev.items()),
        f"exponent mismatch {ev}",
    )
    null = Res.nullspace()
    _check(len(null) == 2, "kernel dimension != 2")
    comp = sp.Matrix([[null[0][0], null[0][2]], [null[1][0], null[1][2]]])
    _check(comp.rank() == 2, "(P,Q) profiles not independent")

    # RW benchmark
    F = sp.Function("F")(r)
    V = B0 * (6 / r**2 - 6 * m / r**3)
    op = B0 * sp.diff(B0 * sp.diff(F, r), r) + 2 * sp.I * w * B0 * sp.diff(F, r) - V * F
    solF = sp.solve(sp.Eq(sp.expand(op), 0), sp.Derivative(F, (r, 2)), dict=True)
    e2 = sp.expand(solF[0][sp.Derivative(F, (r, 2))])
    A2 = sp.zeros(2, 2)
    A2[0, 1] = sp.Integer(1)
    A2[1, 0] = e2.coeff(F)
    A2[1, 1] = e2.coeff(sp.Derivative(F, r))
    A2r = sp.Matrix(2, 2, lambda i, j: sp.cancel(sp.together(A2[i, j].subs(r, 2 * m + rho))))
    Res2 = sp.Matrix(2, 2, lambda i, j: sp.cancel(sp.limit(rho * A2r[i, j], rho, 0)))
    ev2 = {sp.nsimplify(sp.simplify(kk)) for kk in Res2.eigenvals()}
    _check(
        len(ev2) == 2 and any(sp.simplify(kk) == 0 for kk in ev2)
        and any(sp.simplify(kk + 1 + 4 * sp.I * m * w) == 0 for kk in ev2),
        f"RW benchmark mismatch {ev2}",
    )

    print("BH2A_HORIZON_REACH: all independent checks passed")


if __name__ == "__main__":
    verify_certificate()
