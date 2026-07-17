"""Structurally independent verifier for BH0_STATIC_SPHERICAL_BACKGROUND.

Independence from the producer `bh0_background.py` / `weyl_geometry.py`:

- curvature is recomputed here with separately written code;
- the Weyl tensor is assembled through the Schouten tensor and the
  Kulkarni--Nomizu product, not the direct trace-subtraction formula;
- the verifier carries its own mutation controls, so a common-mode "always
  zero" failure of the tensor pipeline is detected here independently.

The Bach tensor definition itself, B_ab = nabla^c nabla^d C_acbd
+ (1/2) R^cd C_acbd, is the frozen convention shared with the producer.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH0_STATIC_SPHERICAL_BACKGROUND.json"
SCHEMA = HERE / "schema" / "bh0-static-spherical-background-v1.schema.json"

N = 4


class BH0VerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise BH0VerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---- independent curvature pipeline (Schouten / Kulkarni--Nomizu) --------


def curvature(coords, g):
    ginv = g.inv()
    d = sp.diff
    Gam = [[[sp.cancel(
        sum(ginv[a, e] * (d(g[e, b], coords[c]) + d(g[e, c], coords[b]) - d(g[b, c], coords[e]))
            for e in range(N)) / 2)
        for c in range(N)] for b in range(N)] for a in range(N)]
    Rup = [[[[sp.cancel(sp.together(
        d(Gam[a][b][e], coords[c]) - d(Gam[a][b][c], coords[e])
        + sum(Gam[a][f][c] * Gam[f][b][e] - Gam[a][f][e] * Gam[f][b][c] for f in range(N))))
        for e in range(N)] for c in range(N)] for b in range(N)] for a in range(N)]
    Rlow = [[[[sp.cancel(sum(g[a, f] * Rup[f][b][c][e] for f in range(N)))
               for e in range(N)] for c in range(N)] for b in range(N)] for a in range(N)]
    Ric = sp.Matrix(N, N, lambda b, e: sp.cancel(sum(Rup[a][b][a][e] for a in range(N))))
    Rsc = sp.cancel(sum(ginv[a, b] * Ric[a, b] for a in range(N) for b in range(N)))
    # Schouten in 4D and Weyl via Kulkarni--Nomizu:  C = Riem - P (x) g
    P = sp.Matrix(N, N, lambda a_, b_: sp.cancel((Ric[a_, b_] - Rsc / 6 * g[a_, b_]) / 2))
    C = [[[[sp.cancel(sp.together(
        Rlow[a][b][c][e]
        - (P[a, c] * g[b, e] + P[b, e] * g[a, c] - P[a, e] * g[b, c] - P[b, c] * g[a, e])))
        for e in range(N)] for c in range(N)] for b in range(N)] for a in range(N)]
    return ginv, Gam, Ric, Rsc, C


def bach(coords, g):
    ginv, Gam, Ric, Rsc, C = curvature(coords, g)
    d = sp.diff

    def covC(e, a, b, c, f):
        s = d(C[a][b][c][f], coords[e])
        for h in range(N):
            s -= (Gam[h][e][a] * C[h][b][c][f] + Gam[h][e][b] * C[a][h][c][f]
                  + Gam[h][e][c] * C[a][b][h][f] + Gam[h][e][f] * C[a][b][c][h])
        return s

    A = [[[sp.cancel(sp.together(
        sum(ginv[dd, f] * covC(f, a, c, b, dd) for dd in range(N) for f in range(N)
            if ginv[dd, f] != 0)))
        for b in range(N)] for c in range(N)] for a in range(N)]

    def covA(e, a, b, c):
        s = d(A[a][b][c], coords[e])
        for h in range(N):
            s -= Gam[h][e][a] * A[h][b][c] + Gam[h][e][b] * A[a][h][c] + Gam[h][e][c] * A[a][b][h]
        return s

    B = sp.zeros(N, N)
    Rup2 = sp.Matrix(N, N, lambda c, dd: sp.cancel(
        sum(ginv[c, e] * ginv[dd, f] * Ric[e, f] for e in range(N) for f in range(N))))
    for a in range(N):
        for b in range(N):
            s = sum(ginv[c, e] * covA(e, a, c, b) for c in range(N) for e in range(N)
                    if ginv[c, e] != 0)
            s += sum(sp.Rational(1, 2) * Rup2[c, dd] * C[a][c][b][dd]
                     for c in range(N) for dd in range(N) if Rup2[c, dd] != 0)
            B[a, b] = sp.simplify(sp.cancel(sp.together(s)))
    return B


def _zero(M) -> bool:
    return all(sp.simplify(M[i, j]) == 0 for i in range(N) for j in range(N))


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    _check(prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]), "engine hash mismatch")
    lind = payload["conventions"]["linearized_dictionary"]
    _check(
        lind["flat_certificate_sha256"] == _sha256(ROOT / lind["flat_certificate"]),
        "flat TT certificate hash mismatch",
    )

    t, ph, v = sp.symbols("t phi v")
    r, th = sp.symbols("r theta", positive=True)
    beta, gam, k = sp.symbols("beta gamma k")
    coords = [t, r, th, ph]

    SYMTAB = {"beta": beta, "gamma": gam, "k": k, "r": r, "theta": th,
              "u": sp.Symbol("u"), "w": sp.Symbol("w"),
              "c2": sp.Symbol("c2"), "c3": sp.Symbol("c3"),
              "m": sp.Symbol("m", positive=True)}

    def _sym(s):
        return sp.sympify(s, locals=dict(SYMTAB))

    def diag_metric(B):
        return sp.diag(-B, 1 / B, r**2, r**2 * sp.sin(th) ** 2)

    # -- own controls (also guard against a trivially-zero pipeline) -------
    m = sp.Symbol("m", positive=True)
    _, _, RicS, _, _ = curvature(coords, diag_metric(1 - 2 * m / r))
    _check(_zero(RicS), "verifier control: Schwarzschild not Ricci-flat")
    _check(_zero(bach(coords, diag_metric(1 - 2 * m / r))), "verifier control: Schwarzschild not Bach-flat")
    gSdS = diag_metric(1 - 2 * m / r - k * r**2)
    _, _, RicD, _, _ = curvature(coords, gSdS)
    _check(_zero(RicD - 3 * k * gSdS), "verifier control: S-dS not Einstein")
    _check(_zero(bach(coords, gSdS)), "verifier control: S-dS not Bach-flat")

    # -- family, defect, EF chart ------------------------------------------
    MK = _sym(payload["vacuum_family"]["B"])
    _check(
        sp.simplify(
            MK - (1 - 3 * beta * gam - beta * (2 - 3 * beta * gam) / r + gam * r - k * r**2)
        ) == 0,
        "stored family B differs from the declared MK form",
    )
    _check(_zero(bach(coords, diag_metric(MK))), "MK family not Bach-flat (independent pipeline)")
    _, _, RicMK, RscMK, _ = curvature(coords, diag_metric(MK))
    gMK = diag_metric(MK)
    E_thth = sp.simplify(RicMK[2, 2] - RscMK / 4 * gMK[2, 2])
    _check(
        sp.simplify(E_thth - _sym(payload["einstein_split"]["defect_thth"])) == 0,
        "Einstein defect mismatch",
    )
    _check(sp.simplify(E_thth.subs(gam, 0)) == 0, "gamma=0 defect does not vanish")
    gEF = sp.zeros(4, 4)
    gEF[0, 0] = -MK
    gEF[0, 1] = gEF[1, 0] = 1
    gEF[2, 2] = r**2
    gEF[3, 3] = r**2 * sp.sin(th) ** 2
    _check(_zero(bach([v, r, th, ph], gEF)), "MK not Bach-flat in EF chart (independent)")

    # -- Laurent completeness ----------------------------------------------
    u, w, c2, c3 = sp.symbols("u w c2 c3")
    Bgen = w - u / r + gam * r - k * r**2 + c2 / r**2 + c3 * r**3
    BL = bach(coords, diag_metric(Bgen))
    conds = set()
    for i in range(N):
        for j in range(N):
            e = sp.simplify(BL[i, j])
            if e != 0:
                num, _den = sp.fraction(sp.cancel(sp.together(e)))
                for cf in sp.Poly(sp.expand(num), r).coeffs():
                    conds.add(sp.factor(cf))
    gb = sp.groebner(sorted(conds, key=sp.default_sort_key), c2, c3, u, w, gam, k, order="lex")
    got = {sp.factor(e) for e in gb.exprs}
    want = {_sym(s) for s in payload["laurent_completeness"]["groebner_basis"]}
    _check(
        {sp.factor(e) for e in want} == got,
        f"Laurent Groebner basis mismatch: {got}",
    )

    # -- residual gauge algebra --------------------------------------------
    c, lam, x = sp.symbols("c lambda x")
    rho = sp.Symbol("rho", positive=True)
    rg = payload["residual_gauge"]
    Btilde = sp.expand(sp.cancel((1 - c * rho) ** 2 * MK.subs(r, rho / (1 - c * rho))))
    p = sp.Poly(sp.cancel(sp.together(Btilde * rho)), rho)
    bt = sp.simplify(-p.coeff_monomial(rho**0) / (1 + p.coeff_monomial(rho**1)))
    gt = sp.simplify(p.coeff_monomial(rho**2))
    kt = sp.simplify(-p.coeff_monomial(rho**3))
    for key, expr in [("beta", bt), ("gamma", gt), ("k", kt)]:
        _check(
            sp.simplify(expr - _sym(rg["c_map"][key])) == 0,
            f"c-map image for {key} mismatch",
        )
    uu = beta * (2 - 3 * beta * gam)
    ww = 1 - 3 * beta * gam
    ut = sp.expand(bt * (2 - 3 * bt * gt))
    wt = sp.expand(1 - 3 * bt * gt)
    Q = -uu * x**3 + ww * x**2 + gam * x - k
    Qt = -ut * x**3 + wt * x**2 + gt * x - kt
    _check(sp.simplify(sp.expand(Qt - Q.subs(x, x - c))) == 0, "translation property fails")
    J = sp.expand(uu**2 * sp.discriminant(Q, x))
    _check(sp.simplify(J - sp.expand(_sym(rg["continuous_invariant"]["J"]))) == 0, "stored J mismatch")
    _check(sp.simplify(sp.expand(ut**2 * sp.discriminant(Qt, x)) - J) == 0, "J not c-invariant")
    bs, gs, ks = beta / lam, lam * gam, lam**2 * k
    us = sp.expand(bs * (2 - 3 * bs * gs))
    Qs = -us * x**3 + (1 - 3 * bs * gs) * x**2 + gs * x - ks
    _check(sp.simplify(sp.expand(us**2 * sp.discriminant(Qs, x)) - J) == 0, "J not dilation-invariant")
    gen = sp.Matrix([
        [sp.diff(e, c).subs(c, 0) for e in (bt, gt, kt)],
        [sp.diff(e, lam).subs(lam, 1) for e in (bs, gs, ks)],
    ])
    _check(gen.rank() == 2, "residual orbit rank != 2")

    # -- fixture ------------------------------------------------------------
    hf = payload["horizon_fixture"]
    fx = {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), k: sp.Rational(1, 19)}
    Bfx = sp.cancel(MK.subs(fx))
    _check(sp.simplify(Bfx - _sym(hf["B"])) == 0, "fixture B mismatch")
    _check(
        sp.expand(Bfx * r - sp.Rational(-1, 19) * (r - 1) * (r - 3) * (r - 8)) == 0,
        "fixture cubic factorization fails",
    )
    dB = sp.diff(Bfx, r)
    for root in hf["roots"]:
        rh = sp.Integer(int(root["r"]))
        _check(sp.simplify(Bfx.subs(r, rh)) == 0, f"B({rh}) != 0")
        slope = sp.simplify(dB.subs(r, rh))
        _check(sp.simplify(slope - _sym(root["B_prime"])) == 0, f"B'({rh}) mismatch")
        _check(
            sp.simplify(slope / 2 - _sym(root["chart_surface_gravity"])) == 0,
            f"surface gravity mismatch at {rh}",
        )
    _check(_sym(hf["non_einstein_witness"]) != 0, "fixture defect witness is zero")
    _check(
        sp.simplify(E_thth.subs(fx) - _sym(hf["non_einstein_witness"])) == 0,
        "fixture defect witness mismatch",
    )
    _check(
        sp.simplify(J.subs(fx) - _sym(hf["invariant_J_value"])) == 0,
        "fixture J value mismatch",
    )

    # -- singularity data ----------------------------------------------------
    weyl2 = _sym(payload["singularities"]["WeylSq"])
    _check(
        sp.simplify(weyl2 - 12 * beta**2 * (2 - 3 * beta * gam + gam * r) ** 2 / r**6) == 0,
        "stored WeylSq mismatch with closed form",
    )
    for name in ("R", "RicciSq", "WeylSq", "Kretschmann"):
        expr = _sym(payload["singularities"][name])
        _num, den = sp.fraction(sp.cancel(sp.together(expr)))
        _check(den.free_symbols <= {r}, f"{name} has parameter-dependent poles")
        for rh in (1, 3, 8):
            _check(expr.subs(fx).subs(r, rh).is_finite is True, f"{name} infinite at horizon {rh}")

    # -- mutations must fail in the independent pipeline too -----------------
    for mut in payload["mutation_tests"]:
        Bmut = _sym(mut["B"])
        BM = bach(coords, diag_metric(Bmut))
        _check(not _zero(BM), f"mutation {mut['label']} is Bach-flat in independent pipeline")

    # -- stored reduced rows match an independent recomputation --------------
    a = sp.Function("a")(r)
    b = sp.Function("b")(r)
    B2 = bach(coords, sp.diag(-a, b, r**2, r**2 * sp.sin(th) ** 2))
    stored = payload["reduced_equations"]["rows"]
    loc = {"a": sp.Function("a"), "b": sp.Function("b"), "r": r, "theta": th}
    for name, idx in [("tt", 0), ("rr", 1), ("thth", 2)]:
        _check(
            sp.simplify(B2[idx, idx] - sp.sympify(stored[name], locals=loc)) == 0,
            f"stored reduced row {name} differs from independent recomputation",
        )

    print("BH0_STATIC_SPHERICAL_BACKGROUND: all independent checks passed")


if __name__ == "__main__":
    verify_certificate()
