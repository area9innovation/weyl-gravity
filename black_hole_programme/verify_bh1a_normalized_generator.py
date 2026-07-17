"""Structurally independent verifier for BH1A_NORMALIZED_GENERATOR.

Independence: the Weyl component entering the Wald entropy is recomputed on
the verifier-side Schouten/Kulkarni--Nomizu curvature pipeline
(`verify_bh0_background.curvature`); the charge closed forms are taken from
the BH-1 certificate (independently verified there) and every derived
statement — Frobenius, closure, basicness, Hamiltonian, functional
dependence on J, entropy, first law, ensemble audit, fixture values — is
recomputed here with separately written algebra.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

import verify_bh0_background as vb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH1A_NORMALIZED_GENERATOR.json"
SCHEMA = HERE / "schema" / "bh1a-normalized-generator-v1.schema.json"


class BH1AVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise BH1AVerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    _check(
        prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]),
        "engine hash mismatch",
    )
    for name in ("bh0", "bh1"):
        _check(
            prov[f"{name}_certificate_sha256"] == _sha256(ROOT / prov[f"{name}_certificate"]),
            f"{name} certificate hash mismatch",
        )

    beta, gam, k, alpha = sp.symbols("beta gamma k alpha")
    rh = sp.Symbol("r_h")
    x, c, lam = sp.symbols("x c lambda")
    ps = [beta, gam, k]
    SYM = {"beta": beta, "gamma": gam, "k": k, "alpha": alpha, "pi": sp.pi, "r_h": rh}

    def _sym(s):
        return sp.sympify(s, locals=dict(SYM))

    # charges from the (independently verified) BH-1 certificate
    bh1 = json.loads((ROOT / prov["bh1_certificate"]).read_text(encoding="utf-8"))
    F = [
        _sym(bh1["bare_charges"]["F_beta"]),
        _sym(bh1["bare_charges"]["F_gamma"]),
        _sym(bh1["bare_charges"]["F_k"]),
    ]
    u = beta * (2 - 3 * beta * gam)
    w = 1 - 3 * beta * gam

    # Frobenius and normalized closure/basicness
    dF = {
        (i, j): sp.expand(sp.diff(F[j], ps[i]) - sp.diff(F[i], ps[j]))
        for i in range(3)
        for j in range(i + 1, 3)
    }
    _check(
        sp.simplify(F[0] * dF[(1, 2)] - F[1] * dF[(0, 2)] + F[2] * dF[(0, 1)]) == 0,
        "Frobenius fails",
    )
    _check(any(v != 0 for v in dF.values()), "bare dF unexpectedly zero")
    NF = [sp.expand(u * e) for e in F]
    for (i, j) in [(0, 1), (0, 2), (1, 2)]:
        _check(
            sp.simplify(sp.diff(NF[j], ps[i]) - sp.diff(NF[i], ps[j])) == 0,
            "u F not closed",
        )
    gen_c = [-3 * beta**2, 6 * beta * gam - 2, gam]
    gen_l = [-beta, gam, 2 * k]
    _check(
        sp.simplify(sum(v * sp.diff(u, p) for v, p in zip(gen_c, ps))) == 0,
        "u not c-invariant",
    )
    _check(
        sp.simplify(sum(v * sp.diff(u, p) for v, p in zip(gen_l, ps)) + u) == 0,
        "u dilation weight != -1",
    )
    _check(
        sp.simplify(sum(nf * v for nf, v in zip(NF, gen_c))) == 0
        and sp.simplify(sum(nf * v for nf, v in zip(NF, gen_l))) == 0,
        "u F not horizontal",
    )

    # Hamiltonian, discriminant relation, functional dependence on J
    H = _sym(payload["hamiltonian"]["H"])
    for p, nf in zip(ps, NF):
        _check(sp.simplify(sp.diff(H, p) - nf) == 0, f"dH/d{p} mismatch")
    D1 = _sym(payload["hamiltonian"]["D1"])
    D2 = _sym(payload["hamiltonian"]["D2"])
    _check(sp.simplify(H + 16 * sp.pi * alpha * beta**2 * D2) == 0, "H != -16 pi alpha beta^2 D2")
    Q = -u * x**3 + w * x**2 + gam * x - k
    J = sp.expand(u**2 * sp.discriminant(Q, x))
    _check(sp.simplify(J + u**2 * D1 * D2) == 0, "J != -u^2 D1 D2")
    dJ = [sp.diff(J, p) for p in ps]
    dH = [sp.diff(H, p) for p in ps]
    for (i, j) in [(0, 1), (0, 2), (1, 2)]:
        _check(sp.simplify(dJ[i] * dH[j] - dJ[j] * dH[i]) == 0, "dH ^ dJ != 0")

    # Wald entropy via the independent curvature pipeline
    t, ph = sp.symbols("t phi")
    r, th = sp.symbols("r theta", positive=True)
    MK = 1 - 3 * beta * gam - beta * (2 - 3 * beta * gam) / r + gam * r - k * r**2
    g = sp.diag(-MK, 1 / MK, r**2, r**2 * sp.sin(th) ** 2)
    ginv, _Gam, _Ric, _Rsc, C = vb.curvature([t, r, th, ph], g)
    C_up = sp.simplify(ginv[0, 0] ** 2 * ginv[1, 1] ** 2 * C[0][1][0][1])
    S_r = sp.simplify(-2 * sp.pi * (2 * alpha) * 4 * C_up * 4 * sp.pi * r**2)
    S = _sym(payload["wald_entropy"]["S"])
    _check(sp.simplify(S_r.subs(r, rh) - S) == 0, "independent Wald entropy mismatch")

    # first law modulo the horizon condition, independent reduction
    B_rh = w - u / rh + gam * rh - k * rh**2
    Bp = sp.diff(w - u / r + gam * r - k * r**2, r).subs(r, rh)
    P = sp.Poly(sp.expand(rh * B_rh), rh)
    T = u * Bp / (4 * sp.pi)
    for p in ps:
        dS_p = sp.diff(S, p) - sp.diff(S, rh) * sp.diff(B_rh, p) / Bp
        num, den = sp.fraction(sp.cancel(sp.together(sp.diff(H, p) - T * dS_p)))
        rem = sp.rem(sp.Poly(sp.expand(num), rh), P).as_expr()
        _check(sp.simplify(sp.cancel(rem / den)) == 0, f"first law fails: {p}")

    # ensemble audit
    gt = gam - 2 * c * w - 3 * c**2 * u
    kt = k + c * gam - c**2 * w - c**3 * u
    _check(
        sp.solve([sp.Eq(gt, gam), sp.Eq(kt, k)], c, dict=True) == [{c: 0}],
        "ensemble-preserving c not unique",
    )
    locus = sp.factor(sp.resultant(sp.expand((gt - gam) / c), sp.expand((kt - k) / c), c))
    _check(
        sp.simplify(
            locus - beta * (3 * beta * gam - 2) * sp.expand(w**2 - 3)
        ) == 0,
        f"nonzero-c locus mismatch: {locus}",
    )
    _check(
        {lam: 1} in sp.solve([sp.Eq(lam * gam, gam), sp.Eq(lam**2 * k, k)], lam, dict=True),
        "dilation audit failed",
    )
    _check(sp.simplify(H.subs({gam: 0, k: 0})) == 0, "Schwarzschild H != 0")
    _check(
        sp.simplify(S.subs({gam: 0, rh: 2 * beta}) - 64 * sp.pi**2 * alpha) == 0,
        "Schwarzschild entropy mismatch",
    )

    # fixture
    fx = {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), k: sp.Rational(1, 19)}
    hf = payload["horizon_fixture"]
    _check(sp.nsimplify(u.subs(fx)) == _sym(hf["u"]), "fixture u mismatch")
    _check(sp.simplify(H.subs(fx) - _sym(hf["H"])) == 0, "fixture H mismatch")
    for entry in hf["horizons"]:
        r0 = sp.Integer(int(entry["r"]))
        _check(
            sp.simplify(S.subs(fx).subs(rh, r0) - _sym(entry["S"])) == 0,
            f"fixture S mismatch at {r0}",
        )
        _check(
            sp.simplify(T.subs(fx).subs(rh, r0) - _sym(entry["T"])) == 0,
            f"fixture T mismatch at {r0}",
        )
        for p in ps:
            dS_p = sp.diff(S, p) - sp.diff(S, rh) * sp.diff(B_rh, p) / Bp
            _check(
                sp.simplify((sp.diff(H, p) - T * dS_p).subs(fx).subs(rh, r0)) == 0,
                f"fixture first law fails at {r0}, {p}",
            )

    print("BH1A_NORMALIZED_GENERATOR: all independent checks passed")


if __name__ == "__main__":
    verify_certificate()
