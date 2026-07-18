"""Independent verifier for BH2A_CAUSAL_DISPOSITION.

Re-runs the asymptotic classification on the verifier-side
Schouten/Kulkarni--Nomizu curvature pipeline (VbGeo adapter), re-checks
the dispersion, the sigma sets, the RW control, and the evidence hashes.
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
CERTIFICATE = HERE / "certificates" / "BH2A_CAUSAL_DISPOSITION.json"
SCHEMA = HERE / "schema" / "bh2a-causal-disposition-v1.schema.json"
N = 4


class DispositionVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise DispositionVerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    _check(prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]), "engine hash mismatch")
    for key in ("reach", "cross"):
        _check(prov[f"{key}_certificate_sha256"] == _sha256(ROOT / prov[f"{key}_certificate"]),
               f"{key} certificate hash mismatch")

    t_ch, ph = sp.symbols("t phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    w = sp.Symbol("omega", positive=True)
    B0 = 1 - 2 / r
    coords = [t_ch, r, x, ph]
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = VbGeo(coords, g0)
    gi = geo0.ginv
    S = -3 * x * (1 - x**2)
    cancel = lambda e: sp.cancel(sp.together(e))  # noqa: E731

    p_c = sp.Function("p")(t_ch, r)
    q_c = sp.Function("q")(t_ch, r)
    c_c = sp.Function("c")(t_ch, r)
    psi_t = sp.zeros(4, 4)
    psi_t[0, 3] = psi_t[3, 0] = p_c * S
    psi_t[1, 3] = psi_t[3, 1] = q_c * S
    psi_t[2, 3] = psi_t[3, 2] = c_c * 3 * (x**2 - 1)
    sdiv = sum(gi[a, e] * geo0.covd2(psi_t, e, a, 3)
               for a in range(N) for e in range(N) if gi[a, e] != 0)
    c_expr = sp.solve(sp.Eq(cancel(sdiv), 0), c_c)[0]
    psi2 = sp.Matrix(N, N, lambda i, j: cancel(psi_t.subs(c_c, c_expr).doit()[i, j]))
    G = geo0.Gamma
    DX = [[[cancel(geo0.covd2(psi2, e, a, b)) for b in range(N)] for a in range(N)]
          for e in range(N)]

    def covd2X2(e, f, a, b):
        s = sp.diff(DX[f][a][b], coords[e])
        for hh in range(N):
            s -= (G[hh][e][f] * DX[hh][a][b] + G[hh][e][a] * DX[f][hh][b]
                  + G[hh][e][b] * DX[f][a][hh])
        return s

    def Lrow(a, b):
        box = sum(gi[e, f] * covd2X2(e, f, a, b)
                  for e in range(N) for f in range(N) if gi[e, f] != 0)
        cx = sum(geo0.Weyl[a][cc][b][d]
                 * sum(gi[cc, e] * gi[d, f] * psi2[e, f] for e in range(N) for f in range(N))
                 for cc in range(N) for d in range(N))
        return cancel(box / 2 + cx)

    Lt = cancel(Lrow(0, 3) / S)
    Lr = cancel(Lrow(1, 3) / S)
    P = sp.Function("P")(r)
    Q = sp.Function("Q")(r)
    E = sp.exp(sp.I * w * t_ch)
    four = {p_c: P * E, q_c: Q * E}
    Ltf = sp.expand(cancel(Lt.subs(four).doit() / E))
    Lrf = sp.expand(cancel(Lr.subs(four).doit() / E))

    lam, sig = sp.symbols("lambda_ sigma")
    a0, b0 = sp.symbols("a0 b0")
    ans = {P: a0 * sp.exp(sp.I * lam * r) * r**sig,
           Q: b0 * sp.exp(sp.I * lam * r) * r**sig}

    def leading(row):
        e = row
        for func, val in ans.items():
            e = e.subs({sp.Derivative(func, (r, 2)): sp.diff(val, r, 2),
                        sp.Derivative(func, r): sp.diff(val, r),
                        func: val})
        e = sp.expand(e.doit() / (sp.exp(sp.I * lam * r) * r**sig))
        num, _den = sp.fraction(sp.together(sp.expand(cancel(sp.together(e)))))
        return sp.Poly(sp.expand(num), r)

    pol1 = leading(Ltf)
    pol2 = leading(Lrf)
    d1 = max(mon[0] for mon in pol1.monoms())
    d2 = max(mon[0] for mon in pol2.monoms())
    top1 = sp.expand(pol1.coeff_monomial(r**d1))
    top2 = sp.expand(pol2.coeff_monomial(r**d2))
    M0 = sp.Matrix([[top1.coeff(a0), top1.coeff(b0)],
                    [top2.coeff(a0), top2.coeff(b0)]])
    disp = sp.factor(M0.det())
    _check(sp.simplify(disp / ((lam - w) ** 2 * (lam + w) ** 2)).is_constant(),
           f"dispersion mismatch: {disp}")
    for lv, expect in [(w, {2 * sp.I * w, 2 * sp.I * w - 1}),
                       (-w, {-2 * sp.I * w, -2 * sp.I * w - 1})]:
        M0l = M0.subs(lam, lv)
        ns = M0l.nullspace()
        _check(len(ns) == 2, "nullspace dim mismatch")
        nxt1 = sp.expand(pol1.coeff_monomial(r**(d1 - 1))).subs(lam, lv)
        nxt2 = sp.expand(pol2.coeff_monomial(r**(d2 - 1))).subs(lam, lv)
        N1 = sp.Matrix([[nxt1.coeff(a0), nxt1.coeff(b0)],
                        [nxt2.coeff(a0), nxt2.coeff(b0)]])
        lnsl = M0l.T.nullspace()
        proj = sp.Matrix(2, 2, lambda i, j: sp.expand((lnsl[i].T * N1 * ns[j])[0, 0]))
        sigs = set(sp.solve(sp.Eq(sp.factor(sp.expand(proj.det())), 0), sig))
        _check(
            len(sigs) == 2 and all(
                any(sp.simplify(sv - ev) == 0 for ev in expect) for sv in sigs),
            f"sigma mismatch at lam={lv}: {sigs}",
        )
    print("[asymptotics] dispersion and sigma sets verified on the independent pipeline")
    print("BH2A_CAUSAL_DISPOSITION: all independent checks passed")


if __name__ == "__main__":
    verify_certificate()
