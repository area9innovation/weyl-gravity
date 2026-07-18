"""Structurally independent verifier for BH2A_FLUX_MATRIX.

Recomputes the stored bilinear on the verifier-side
Schouten/Kulkarni--Nomizu pipeline (VbGeo adapter) with the frozen
machinery formulas, re-checks the off-shell 4-alpha identity there,
re-validates the RW closed formula by exact rational point evaluation
against the STORED bilinear, and re-checks the conjugate-pair null
statement.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from linearized_bach import LinearizedBach
from linearized_theta import LinearizedTheta
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2A_FLUX_MATRIX.json"
SCHEMA = HERE / "schema" / "bh2a-flux-matrix-v1.schema.json"


class FluxVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise FluxVerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    for name, sha in prov["machinery_sha256"].items():
        _check(sha == _sha256(HERE / f"{name}.py"), f"{name} hash mismatch")
    _check(prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]), "engine hash mismatch")
    for key in ("bh1b", "bh2a"):
        _check(prov[f"{key}_certificate_sha256"] == _sha256(ROOT / prov[f"{key}_certificate"]),
               f"{key} certificate hash mismatch")

    t, ph = sp.symbols("t phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    m = sp.Symbol("m", positive=True)
    alpha = sp.Symbol("alpha")
    w1, w2 = sp.symbols("omega1 omega2")
    coords = [t, r, x, ph]
    B0 = 1 - 2 * m / r

    loc = {"h0a": sp.Function("h0a"), "h1a": sp.Function("h1a"),
           "h0b": sp.Function("h0b"), "h1b": sp.Function("h1b"),
           "t": t, "r": r, "m": m, "alpha": alpha, "pi": sp.pi}
    Ft_st = sp.sympify(payload["bilinear"]["F_t"], locals=loc)
    Fr_st = sp.sympify(payload["bilinear"]["F_r"], locals=loc)

    # rebuild the bilinear on the verifier-side pipeline
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = VbGeo(coords, g0)
    lt = LinearizedTheta(geo0, alpha)
    S = -3 * x * (1 - x**2)
    h0a = loc["h0a"](t, r); h1a = loc["h1a"](t, r)
    h0b = loc["h0b"](t, r); h1b = loc["h1b"](t, r)
    hA = sp.zeros(4, 4); hA[0, 3] = hA[3, 0] = h0a * S; hA[1, 3] = hA[3, 1] = h1a * S
    hB = sp.zeros(4, 4); hB[0, 3] = hB[3, 0] = h0b * S; hB[1, 3] = hB[3, 1] = h1b * S
    w = lt.omega(hA, hB)
    Ft_new = sp.simplify(sp.cancel(sp.together(
        sp.integrate(sp.integrate(w[0] * r**2, (x, -1, 1)), (ph, 0, 2 * sp.pi)))))
    Fr_new = sp.simplify(sp.cancel(sp.together(
        sp.integrate(sp.integrate(w[1] * r**2, (x, -1, 1)), (ph, 0, 2 * sp.pi)))))
    _check(sp.simplify(sp.expand(Ft_new - Ft_st)) == 0, "stored F^t mismatch")
    _check(sp.simplify(sp.expand(Fr_new - Fr_st)) == 0, "stored F^r mismatch")
    print("[bilinear] verifier-side recomputation matches stored forms", flush=True)

    # off-shell identity on the verifier pipeline
    D = sp.expand(sp.diff(Ft_st, t) + sp.diff(Fr_st, r))
    lbA = LinearizedBach(geo0)
    dBA = lbA.build(hA)
    lbB = LinearizedBach(geo0)
    dBB = lbB.build(hB)
    gi = geo0.ginv

    def contract(h, dB):
        s = sp.Integer(0)
        for b in range(4):
            for c in range(4):
                if h[b, c] == 0:
                    continue
                up = sum(gi[b, p] * gi[c, q] * dB[p, q] for p in range(4) for q in range(4))
                s += h[b, c] * up
        return s

    integrand = sp.cancel(sp.together(contract(hB, dBA) - contract(hA, dBB))) * r**2
    Xi = sp.expand(sp.simplify(sp.cancel(sp.together(
        sp.integrate(sp.integrate(integrand, (x, -1, 1)), (ph, 0, 2 * sp.pi))))))
    _check(sp.simplify(sp.expand(D - 4 * alpha * Xi)) == 0, "off-shell identity fails")
    print("[identity] off-shell 4-alpha identity verified", flush=True)

    # RW closed formula: conjugate null + point validation against stored F^r
    ps1, ps2 = sp.symbols("ps1 ps2")
    closed_sym = sp.sympify(payload["rw_block"]["on_shell_flux"].split("= ", 1)[1],
                            locals={"pi": sp.pi, "alpha": alpha, "omega1": w1, "omega2": w2,
                                    "psi1": ps1, "psi2": ps2, "r": r})
    psi1 = sp.Function("psi1")(r)
    psi2 = sp.Function("psi2")(r)
    closed = closed_sym.subs({ps1: psi1, ps2: psi2})
    _check(sp.simplify(closed.subs(w2, w1)) == 0 and sp.simplify(closed.subs(w2, -w1)) == 0,
           "conjugate-pair null fails")

    # independent on-shell construction: constraint from verifier-side dRic
    lb = LinearizedBach(geo0)
    h0f = sp.Function("h0")(t, r)
    h1f = sp.Function("h1")(t, r)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0f * S
    h[1, 3] = h[3, 1] = h1f * S
    lb.build(h)
    R2 = sp.cancel(sp.cancel(sp.together(lb.dRic[2, 3])) / (3 * (x - 1) * (x + 1)))
    H0s = sp.Symbol("H0s")
    E1 = sp.exp(sp.I * w1 * t)
    R2f = sp.cancel(sp.together(sp.expand(
        R2.subs({h0f: H0s * E1, h1f: sp.Function("H1")(r) * E1}).doit() / E1)))
    H0expr = sp.solve(sp.Eq(R2f, 0), H0s)[0]
    H1g = sp.Function("H1")(r)
    E2 = sp.exp(sp.I * w2 * t)
    H0e_1 = H0expr.subs({H1g: r * psi1 / B0,
                         sp.Derivative(H1g, r): sp.diff(r * psi1 / B0, r)}).doit()
    H0e_2 = H0expr.subs({H1g: r * psi2 / B0,
                         sp.Derivative(H1g, r): sp.diff(r * psi2 / B0, r), w1: w2}).doit()
    Fr_sub = sp.expand(sp.cancel(sp.together(Fr_st.subs({
        h0a: H0e_1 * E1, h1a: (r * psi1 / B0) * E1,
        h0b: H0e_2 * E2, h1b: (r * psi2 / B0) * E2,
    }).doit() / (E1 * E2))))
    V = B0 * (6 / r**2 - 6 * m / r**3)
    mval = sp.Integer(1)
    wvals = {w1: sp.Integer(1), w2: sp.Integer(2)}
    for r0, data1, data2 in [
        (sp.Integer(5), (sp.Integer(1), sp.Rational(1, 3)), (sp.Rational(2, 7), sp.Integer(1))),
        (sp.Integer(7), (sp.Rational(3, 2), sp.Rational(-1, 4)), (sp.Integer(2), sp.Rational(1, 5))),
    ]:
        vals = {}
        for psi, wv, (a0, b0) in [(psi1, 1, data1), (psi2, 2, data2)]:
            p2 = (-(sp.diff(B0, r) / B0) * sp.Derivative(psi, r)
                  - (wv**2 - V) / B0**2 * psi)
            d = {psi: a0, sp.Derivative(psi, r): b0}
            d[sp.Derivative(psi, (r, 2))] = sp.nsimplify(p2.subs({m: mval}).subs(d).subs(r, r0))
            d[sp.Derivative(psi, (r, 3))] = sp.nsimplify(
                sp.diff(p2, r).subs({m: mval}).subs(d).subs(r, r0))
            d[sp.Derivative(psi, (r, 4))] = sp.nsimplify(
                sp.diff(p2, r, 2).subs({m: mval}).subs(d).subs(r, r0))
            vals.update(d)
        lhs = sp.simplify(Fr_sub.subs({m: mval, **wvals}).subs(vals).subs(r, r0))
        rhs = sp.simplify(closed.subs({m: mval, **wvals}).subs(vals).subs(r, r0))
        _check(sp.simplify(lhs - rhs) == 0, f"point validation fails at r0={r0}")
    print("[rw] closed formula, null statement, and point validation verified", flush=True)

    print("BH2A_FLUX_MATRIX: all independent checks passed")


if __name__ == "__main__":
    verify_certificate()
