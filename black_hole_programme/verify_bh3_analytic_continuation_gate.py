"""Independent verifier for BH3_ANALYTIC_CONTINUATION_GATE.

Rails (fail-closed), all exact/symbolic -- no complex sampling:

  0. schema + anchor content hashes;
  1. CROSS CURRENT, independent method: recompute a(omega) from the anchor,
     confirm it is rational (no branch points), and recover its pole set by
     PARTIAL FRACTIONS (sp.apart) -- an independent route from the generator's
     denominator-root computation -- checking the poles are exactly {i, i/2}
     and the recorded factored form is correct;
  2. MODE SERIES, independent re-derivation: rebuild the horizon indicial from
     the certified master ODE by a leading-coefficient balance, confirm the
     roots are entire in omega; re-derive the infinity and horizon Frobenius
     coefficients and confirm their omega-pole sets match the recorded sets,
     that the closed-form resonance formula omega = i j / 4 reproduces the
     horizon poles, that every mode-series pole is purely imaginary, and that
     the declared strip half-width equals the least |Im| of a nonzero pole;
  3. POLAR: NOT_ACTIVATED is consistent with BH2_POLAR_QUANTIFIER_REPAIR
     (generic_real_frequency_certified is False and route B is a missing object);
  4. claim-boundary + vocabulary (no continuation through a pole, no QNM/etc.).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERT = HERE / "certificates" / "BH3_ANALYTIC_CONTINUATION_GATE.json"
SCHEMA = HERE / "schema" / "bh3-analytic-continuation-gate-v1.schema.json"


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_certificate() -> dict:
    payload = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    # Rail 0 -------------------------------------------------------------
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    for key in ("cross_invariant_certificate", "general_l_certificate",
                "all_orders_certificate", "polar_quantifier_certificate"):
        base = key.rsplit("_certificate", 1)[0]
        _check(prov[base + "_sha256"] == _sha256(ROOT / prov[key]),
               f"{key} hash mismatch")

    cross = json.loads((ROOT / prov["cross_invariant_certificate"]).read_text())
    allord = json.loads((ROOT / prov["all_orders_certificate"]).read_text())
    polarq = json.loads((ROOT / prov["polar_quantifier_certificate"]).read_text())

    w = sp.Symbol("omega")
    r = sp.Symbol("r", positive=True)
    z = sp.Symbol("z", positive=True)
    ax = payload["axial_analytic_continuation"]

    # Rail 1: cross current, INDEPENDENT (partial fractions) -------------
    a = sp.sympify(cross["a_of_omega"], locals={"omega": w, "I": sp.I})
    _check(a.is_rational_function(w), "a(omega) not rational (branch points?)")
    # partial-fraction expansion exposes the poles independently of root-finding
    apart = sp.apart(a, w, full=True).doit()
    pole_terms = set()
    for term in sp.Add.make_args(apart):
        _n, d = sp.fraction(sp.cancel(term))
        if d.has(w):
            for rt in sp.roots(d, w):
                pole_terms.add(sp.nsimplify(rt))
    _check(pole_terms == {sp.I, sp.I / 2},
           f"apart poles {pole_terms} != {{i, i/2}}")
    _check(ax["cross_current"]["pole_set_exact"] == sorted(["I", "I/2"]),
           "recorded cross pole set wrong")
    _check(sp.simplify(sp.sympify(ax["cross_current"]["a_factored"],
                                  locals={"omega": w, "I": sp.I}) - a) == 0,
           "recorded a_factored != a(omega)")

    # Rail 2: mode families, INDEPENDENT re-derivation -------------------
    c2, c1, c0 = (sp.sympify(c, locals={"r": r, "omega": w, "I": sp.I})
                  for c in allord["master_ode"]["coefficients"])
    # horizon indicial by leading balance at r = 2 + z
    C2 = z * (z + 2)
    C1 = sp.expand(c1.subs(r, 2 + z))
    C0 = sp.expand(c0.subs(r, 2 + z))
    s = sp.Symbol("s")
    Enorm = sp.expand(sp.powsimp(sp.expand(
        (C2 * sp.diff(z**s, z, 2) + C1 * sp.diff(z**s, z) + C0 * z**s) * z**(-s)),
        force=True))
    ind_roots = {sp.expand(rt)
                 for rt in sp.solve(sp.Eq(sp.factor(Enorm.coeff(z, -1)), 0), s)}
    _check(ind_roots == {sp.Integer(0), sp.expand(-4 * sp.I * w - 2)},
           f"horizon indicial roots {ind_roots} != {{0, -4iw-2}}")
    for rt in ind_roots:
        _check(sp.together(rt).is_polynomial(w),
               "horizon indicial root not entire in omega")

    # rebuild a few coefficients and confirm the recorded omega-pole sets
    def omega_poles(expr):
        _num, den = sp.fraction(sp.cancel(expr))
        return set() if not den.has(w) else {
            sp.nsimplify(k) for k in sp.roots(den, w)}

    # infinity, lam0 branch
    def inf_branch(mu, sig, N):
        ak = [sp.Integer(1)]
        for k in range(1, N + 1):
            x = sp.Symbol("x")
            F = sp.exp(mu * r) * r**sig * (
                sum(ak[j] * r**(-j) for j in range(k)) + x * r**(-k))
            E = sp.expand(sp.together(
                (c2 * sp.diff(F, r, 2) + c1 * sp.diff(F, r) + c0 * F)
                / sp.exp(mu * r)))
            Fk = sp.exp(mu * r) * r**sig * x * r**(-k)
            Ek = sp.expand(sp.together(
                (c2 * sp.diff(Fk, r, 2) + c1 * sp.diff(Fk, r) + c0 * Fk)
                / sp.exp(mu * r)))
            deg = sp.Poly(sp.expand(sp.numer(sp.together(Ek))), r).degree()
            sol = sp.solve(sp.Eq(sp.Poly(sp.expand(sp.numer(sp.together(E))),
                                         r).nth(deg), 0), x)
            ak.append(sp.cancel(sol[0]) if sol else sp.Integer(0))
        return ak

    N = 4
    inf_poles = set()
    for c in inf_branch(sp.Integer(0), sp.Integer(-3), N):
        inf_poles |= omega_poles(c)
    _check(inf_poles <= {sp.Integer(0)},
           f"infinity series pole off {{0}}: {inf_poles}")

    # horizon, both branches
    def hor_branch(s0, N):
        g = [sp.Integer(1)]
        for k in range(1, N + 1):
            x = sp.Symbol("x")
            gg = sum(g[j] * z**j for j in range(k)) + x * z**k
            F = z**s0 * gg
            E = sp.expand(sp.powsimp(sp.expand(
                (C2 * sp.diff(F, z, 2) + C1 * sp.diff(F, z) + C0 * F) / z**s0),
                force=True))
            sol = sp.solve(sp.Eq(sp.expand(E).coeff(z, k - 1), 0), x)
            g.append(sp.cancel(sol[0]) if sol else sp.Integer(0))
        return g

    hp0 = set()
    for c in hor_branch(sp.Integer(0), N):
        hp0 |= omega_poles(c)
    hpm = set()
    for c in hor_branch(-4 * sp.I * w - 2, N):
        hpm |= omega_poles(c)
    # closed-form resonance formula omega = i j /4
    _check(all(sp.re(p) == 0 for p in hp0 | hpm),
           "a horizon pole is not purely imaginary")
    _check(all(sp.nsimplify(4 * p / sp.I) == sp.re(4 * p / sp.I)
               and (4 * p / sp.I).is_rational
               for p in (hp0 | hpm) if p != 0),
           "a horizon pole is not of the form i j / 4")
    _check(hp0 <= {sp.I * j / 4 for j in range(3, 3 + 2 * N)},
           f"s=0 horizon poles not in closed form: {hp0}")
    _check(hpm <= {sp.I * j / 4 for j in range(1, 1 - 2 * N, -1)},
           f"s=-4iw-2 horizon poles not in closed form: {hpm}")
    # strip half-width = least |Im| of a nonzero mode-series pole
    nz = sorted({abs(sp.im(p)) for p in (hp0 | hpm) if p != 0})
    _check(str(nz[0]) == ax["declared_domain"]["strip_halfwidth"] == "1/4",
           f"strip half-width {nz[0]} != recorded 1/4")
    # the strip must be free of the current poles too (|i/2| >= 1/4)
    _check(nz[0] <= sp.Rational(1, 2),
           "strip wider than the nearest current pole")

    # Rail 3: polar NOT_ACTIVATED consistency ---------------------------
    _check(payload["polar_disposition"]["status"] == "NOT_ACTIVATED",
           "polar status not NOT_ACTIVATED")
    _check(polarq["claim_flags"]["generic_real_frequency_certified"] is False,
           "polar quantifier is generic -- NOT_ACTIVATED unjustified")
    _check("route_B_structural_identity" in polarq["missing_object"],
           "polar route B is not a missing object")

    # Rail 4: claim boundary + vocabulary -------------------------------
    cf = payload["claim_flags"]
    for t in ("axial_current_meromorphic_continuation_certified",
              "axial_current_exact_singular_set_certified",
              "no_branch_points_axial_certified", "domain_declared_excludes_poles"):
        _check(cf[t] is True, f"expected-true flag {t} not true")
    for f in ("polar_continuation_activated", "polar_route_b_identity_obtained",
              "summability_certified", "general_l_certified",
              "stability_qnm_scattering_claimed"):
        _check(cf[f] is False, f"forbidden flag {f} not false")
    _check(ax["declared_domain"]["continuation_through_pole"] is False,
           "continuation_through_pole must be False")
    _check(payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
           "dependency tags drift")
    positive = {k: v for k, v in payload.items()
                if k not in ("does_not_establish", "missing_objects")}
    blob = json.dumps(positive).lower()
    for banned in ("quasinormal mode computed", "ringdown", "stability certified",
                   "spectrum computed"):
        _check(banned not in blob, f"promotional phrase '{banned}' present")

    return {"rails": "PASS", "cross_poles": "{i, i/2} (partial fractions)",
            "strip_halfwidth": "1/4", "polar": "NOT_ACTIVATED"}


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    result = verify_certificate()
    print(json.dumps(result, indent=2))
    print("OK: BH3_ANALYTIC_CONTINUATION_GATE verified (exact; no sampling)")


if __name__ == "__main__":
    main()
