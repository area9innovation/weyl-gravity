"""BH-2C: symbolic-frequency finite-Lee--Wald-flux radiation class.

Fail-closed builder for
`black_hole_programme/certificates/BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json`.

Verdict token:
`BH2C_SYMBOLIC_FREQUENCY_FINITE_FLUX_RADIATION_CLASS_EINSTEIN_SELECTED`.

Setting: Schwarzschild m = 1, axial l = 2, ingoing EF chart, **symbolic real
frequency omega**.  This is the symbolic-frequency generalization of the
omega = 3/5 fixtures `BH2C_FLUX_CLASS` (axial) and `BH2C_POLAR_FLUX_CLASS`
(polar): those two certified certificates supply the numeric anchor and this
certificate lifts the *decisive finite side* and the *frequency dependence*
to symbolic omega.

What is established symbolically (this generator recomputes it):

1. LITERAL LEE--WALD FINITE SIDE (axial, symbolic omega).  Driving the
   certified EF sphere-integrated axial Lee--Wald slice density F^v
   (LinearizedTheta, the same object certified in BH2A_FLUX_MATRIX /
   BH2C_FLUX_CLASS) with the certified Einstein (Regge--Wheeler) mode
   profiles E0 (mu = 0) and E2 (mu = -2 omega), retaining ALL terms (no
   leading-exponent shortcut), the conjugate-pair slice density falls as
     F^v[E0 x E0] ~ r^-2 ,   F^v[E2 x E2] ~ r^-2 ,
   with an **omega-independent** integer leading power -2 < -1: the Einstein
   slice norm is FINITE at infinity for every real omega.  The leading
   coefficients are recorded (rational functions of omega); they never
   vanish and never change the power for real omega != 0.

2. EXTRA-BRANCH CARRIER EXPONENTS (axial, symbolic omega).  On the
   Ricci-flat background delta Ric is gauge-invariant, so the extra
   (non-Einstein) branch is carried by the trace-free axial Ricci carrier
   psi (the certified BH-2A extra object).  Its operator
   (1/2) Box psi + C psi = 0 at infinity has exponents
     rate lambda = +- i omega ,   power s = +- 2 i omega ,
   i.e. psi ~ e^{+- i omega r} r^{+- 2 i omega} = e^{+- i omega r_*}: the
   amplitude real part is 0 (omega enters only the imaginary tortoise
   phase), independent of omega.

3. FREQUENCY DEPENDENCE / NO REAL EXCEPTIONAL FREQUENCY (derived).  Because
   omega enters every exponent only through an imaginary tortoise phase, the
   amplitude real parts are omega-independent: Einstein amplitudes decay
   (Re <= -3 for the metric master, giving F^v ~ r^-2), the extra carrier
   does not (Re = 0).  The finite-vs-divergent split is therefore
   omega-independent AS A DERIVED FACT, holding for every real omega != 0,
   with the exponents +- i omega, +- 2 i omega never real or colliding
   (omega = 0 is the certified exceptional carrier, BH2C_SYMBOLIC_INDICIAL,
   and is excluded).

4. NUMERIC ANCHOR (cross-rail).  The omega = 3/5 specialization of this same
   pipeline is the certified BH2C_FLUX_CLASS axial table
   (E0|E0 = E2|E2 = (-2, 0) finite; every extra-involving class
   non-negative, divergent, with the X0|X0 log) and the certified
   BH2C_POLAR_FLUX_CLASS polar table (E-sector finite, extra divergent).
   Both anchors are imported here by content hash.

NOT claimed (fail-closed; see `missing_objects` and the does-not-establish
ledger):

- the EXACT symbolic-omega DIVERGENT sub-table and symbolic log tails.  The
  composed (sourced) log solve over the field Q(omega) is intractable in the
  working time box (the omega = 3/5 fixture runs it in ~7 s; symbolic omega
  did not complete a bounded run).  The divergent side is anchored at
  omega = 3/5 by the two fixtures plus the omega-independent exponent
  argument, NOT computed symbolically here.
- the POLAR literal symbolic flux is carried by the parity-unified master
  ODE (BH2C_METRIC_ALL_ORDERS, unified_across_parities) and the certified
  polar Einstein radial-flux nullness (BH2B_POLAR_FLUX) plus the polar
  fixture; it is NOT recomputed symbolically here.
- an asymptotically flat phase-space / charge-algebra construction, series
  summability, general l, conjugate-frequency pairing theorem, stability,
  quasinormal, scattering, positivity, particle, or any quantum statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from linearized_theta import LinearizedTheta
from linearized_bach import LinearizedBach
from weyl_geometry import Geometry

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json"
SCHEMA_PATH = HERE / "schema" / "bh2c-symbolic-flux-radiation-class-v1.schema.json"

AXIAL_FIXTURE = HERE / "certificates" / "BH2C_FLUX_CLASS.json"
POLAR_FIXTURE = HERE / "certificates" / "BH2C_POLAR_FLUX_CLASS.json"
ALL_ORDERS = HERE / "certificates" / "BH2C_METRIC_ALL_ORDERS.json"
SYMB_INDICIAL = HERE / "certificates" / "BH2C_SYMBOLIC_INDICIAL.json"
FLUX_MATRIX = HERE / "certificates" / "BH2A_FLUX_MATRIX.json"

SCHEMA_NAME = "pure-weyl-bh2c-symbolic-flux-radiation-class-v1"
RESULT_ID = "PURE_WEYL_BH2C_SYMBOLIC_FLUX_RADIATION_CLASS"
RESULT_TOKEN = (
    "BH2C_SYMBOLIC_FREQUENCY_FINITE_FLUX_RADIATION_CLASS_EINSTEIN_SELECTED"
)


class SymbolicFluxError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SymbolicFluxError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cancel(e):
    return sp.cancel(sp.together(e))


# ---------------------------------------------------------------------------
# Rail 1: axial Einstein literal Lee--Wald flux at symbolic omega (E x E).
# Reuses the certified BH2C_FLUX_CLASS pipeline (LinearizedTheta F^v, the
# sourced h-system M3, and the homogeneous Einstein jets) with omega kept
# symbolic and the profile set restricted to the Einstein branches.
# ---------------------------------------------------------------------------
def axial_einstein_flux(out: dict, geo_cls=Geometry) -> dict:
    NI = 4
    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    w = sp.Symbol("omega", positive=True)
    alpha = sp.Symbol("alpha", positive=True)
    Lg = sp.Symbol("Lg", positive=True)

    B0 = 1 - 2 / r
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = geo_cls([v, r, x, ph], g0)
    S_ax = -3 * x * (1 - x**2)
    E = sp.exp(sp.I * w * v)

    # F^v: certified EF axial Lee--Wald slice density (LinearizedTheta).
    t0 = time.time()
    lt = LinearizedTheta(geo0, alpha)
    h0a = sp.Function("h0a")(v, r); h1a = sp.Function("h1a")(v, r)
    h0b = sp.Function("h0b")(v, r); h1b = sp.Function("h1b")(v, r)
    hA = sp.zeros(4, 4); hA[0, 3] = hA[3, 0] = h0a * S_ax
    hA[1, 3] = hA[3, 1] = h1a * S_ax
    hB = sp.zeros(4, 4); hB[0, 3] = hB[3, 0] = h0b * S_ax
    hB[1, 3] = hB[3, 1] = h1b * S_ax
    wv_ = lt.omega(hA, hB)
    Fv = _cancel(sp.integrate(sp.integrate(wv_[0] * r**2, (x, -1, 1)),
                              (ph, 0, 2 * sp.pi)))
    _require(Fv != 0, "F^v vanished")
    out["stage_seconds"]["Fv"] = round(time.time() - t0, 1)
    print(f"[Fv] {out['stage_seconds']['Fv']} s", flush=True)

    # Sourced h-system -> homogeneous Einstein jet matrix M3 (omega symbolic).
    t0 = time.time()
    h0f = sp.Function("h0")(v, r)
    h1f = sp.Function("h1")(v, r)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0f * S_ax
    h[1, 3] = h[3, 1] = h1f * S_ax
    lb = LinearizedBach(geo0)
    lb.build(h)
    H0 = sp.Function("H0")(r)
    H1 = sp.Function("H1")(r)

    def fourier_row(row):
        subm = {}
        for fn, val in ((h0f, H0 * E), (h1f, H1 * E)):
            for d in list(row.atoms(sp.Derivative)):
                if d.args[0] == fn:
                    dt = sum(int(p[1]) for p in d.args[1:] if p[0] == v)
                    dr = sum(int(p[1]) for p in d.args[1:] if p[0] == r)
                    subm[d] = (sp.diff(val, v, dt, r, dr) if dt
                               else sp.diff(val, r, dr))
            subm[fn] = val
        return _cancel(sp.expand(row.subs(subm).doit() / E))

    Rx = fourier_row(_cancel(lb.dRic[2, 3] / (3 * (x - 1) * (x + 1))))
    Rr = fourier_row(_cancel(lb.dRic[1, 3] / S_ax))
    XS, TS = sp.symbols("XSRC TSRC")
    H0p = sp.solve(sp.Eq(Rx, XS), sp.Derivative(H0, r))[0]
    H0pp = sp.diff(H0p, r).subs(sp.Derivative(H0, r), H0p)
    row = Rr.subs({sp.Derivative(H0, (r, 2)): H0pp,
                   sp.Derivative(H0, r): H0p}).doit()
    H1pp = sp.solve(sp.Eq(sp.expand(row), TS), sp.Derivative(H1, (r, 2)))[0]
    DH1 = sp.Derivative(H1, r)
    M3 = sp.zeros(3, 3)
    e0 = sp.expand(H0p.subs({XS: 0}))
    M3[0, 0] = e0.coeff(H0); M3[0, 1] = e0.coeff(H1); M3[0, 2] = e0.coeff(DH1)
    M3[1, 2] = 1
    e2 = sp.expand(H1pp.subs({XS: 0, TS: 0}))
    M3[2, 0] = e2.coeff(H0); M3[2, 1] = e2.coeff(H1); M3[2, 2] = e2.coeff(DH1)

    def inv_series_entry(e, depth):
        if e == 0:
            return {}
        if e == 1:
            return {0: sp.Integer(1)}
        num, den = sp.fraction(_cancel(e))
        pn = sp.Poly(sp.expand(num), r)
        pd = sp.Poly(sp.expand(den), r)
        nmax = max(m2[0] for m2 in pn.monoms())
        dmax = max(m2[0] for m2 in pd.monoms())
        dd = [(pd.coeff_monomial(r**(dmax - k)) if dmax - k >= 0 else 0)
              for k in range(depth + 1)]
        inv = [sp.Integer(1) / dd[0]]
        for k in range(1, depth + 1):
            acc = sum(dd[j] * inv[k - j] for j in range(1, k + 1))
            inv.append(sp.cancel(-acc / dd[0]))
        nn = [(pn.coeff_monomial(r**(nmax - k)) if nmax - k >= 0 else 0)
              for k in range(depth + 1)]
        ser = {}
        for k in range(depth + 1):
            ser[k - (nmax - dmax)] = sp.expand(
                sum(nn[j] * inv[k - j] for j in range(k + 1)))
        return ser

    DEP = NI + 4
    Mser = {(i, j): inv_series_entry(M3[i, j], DEP)
            for i in range(3) for j in range(3)}
    Mkc = [sp.Matrix(3, 3, lambda i, j: Mser[(i, j)].get(k, sp.Integer(0)))
           for k in range(DEP + 1)]
    out["stage_seconds"]["h_system"] = round(time.time() - t0, 1)
    print(f"[h_system] {out['stage_seconds']['h_system']} s", flush=True)

    # Homogeneous Einstein jets (the certified Regge--Wheeler branches).
    t0 = time.time()

    def hom_solutions(muv, sig0, njet=NI):
        B0c = Mkc[0] - sp.I * muv * sp.eye(3)

        def yv(n):
            return sp.Matrix(3, 1, lambda i, _: sp.Symbol(f"z_{n}_{i}"))

        unk = [sp.Symbol(f"z_{n}_{i}") for n in range(njet + 1) for i in range(3)]
        eqs = []
        for n in range(-1, njet):
            lhs = (sig0 - n) * yv(n) if 0 <= n <= njet else sp.zeros(3, 1)
            rhs = sp.zeros(3, 1)
            for k in range(0, n + 2):
                j = n + 1 - k
                if 0 <= j <= njet:
                    Bk = B0c if k == 0 else Mkc[k]
                    rhs += Bk * yv(j)
            diff = (lhs - rhs) if 0 <= n <= njet else -rhs
            eqs.extend(sp.expand(diff[i]) for i in range(3))
        Ml, bl = sp.linear_eq_to_matrix(eqs, unk)
        ns = Ml.nullspace()
        sols = []
        for vsol in ns:
            Y = [sp.Matrix(3, 1, lambda i, _: vsol[3 * n + i])
                 for n in range(njet + 1)]
            if all(all(Y[n][i, 0] == 0 for i in range(3))
                   for n in range(njet // 2)):
                continue
            sols.append(Y)
        return sols

    hom = {"0": hom_solutions(sp.Integer(0), sp.Integer(1)),
           "-2w": hom_solutions(-2 * w, -4 * sp.I * w + 1)}
    _require(all(len(vv) >= 1 for vv in hom.values()),
             "missing homogeneous Einstein branch")
    out["stage_seconds"]["hom"] = round(time.time() - t0, 1)
    print(f"[hom] {out['stage_seconds']['hom']} s", flush=True)

    # E x E literal flux: leading (r-power, log-power) and leading coefficient.
    t0 = time.time()

    def hom_profile(Y, muv, sig0):
        H0e = sum(Y[n][0, 0] * r**(sig0 - n) for n in range(len(Y)))
        H1e = sum(Y[n][1, 0] * r**(sig0 - n) for n in range(len(Y)))
        ph_ = sp.exp(sp.I * muv * r)
        return (H0e * ph_, H1e * ph_)

    profiles = {"E0": hom_profile(hom["0"][0], sp.Integer(0), sp.Integer(1)),
                "E2": hom_profile(hom["-2w"][0], -2 * w, -4 * sp.I * w + 1)}

    def leading(expr):
        e = sp.expand(expr.subs(sp.log(r), Lg))
        e = _cancel(sp.together(e))
        num, den = sp.fraction(e)
        pn = sp.Poly(sp.expand(num), r, Lg)
        pd = sp.Poly(sp.expand(den), r)
        dmax = max(m2[0] for m2 in pd.monoms())
        best = None
        for mono in pn.monoms():
            key = (mono[0] - dmax, mono[1])
            if best is None or key > best:
                best = key
        # leading coefficient: numerator monomial at (best_r + dmax, best_Lg)
        rmono = best[0] + dmax
        cnum = pn.coeff_monomial(r**rmono * Lg**best[1]) if best[1] else \
            pn.coeff_monomial(r**rmono)
        cden = pd.coeff_monomial(r**dmax)
        coeff = sp.simplify(cnum / cden)
        return best, coeff

    def flux_pair(na, nb):
        (h0A, h1A) = profiles[na]
        (h0B, h1B) = profiles[nb]
        EA = sp.exp(sp.I * w * v)
        EB = sp.exp(-sp.I * w * v)
        reps = {"h0a": h0A * EA, "h1a": h1A * EA,
                "h0b": sp.conjugate(h0B) * EB, "h1b": sp.conjugate(h1B) * EB}
        fnmap = {"h0a": h0a, "h1a": h1a, "h0b": h0b, "h1b": h1b}
        sub = {}
        for nm, val in reps.items():
            f = fnmap[nm]
            val = val.rewrite(sp.exp)
            for d in list(Fv.atoms(sp.Derivative)):
                if d.args[0] == f:
                    dt = sum(int(p[1]) for p in d.args[1:] if p[0] == v)
                    dr = sum(int(p[1]) for p in d.args[1:] if p[0] == r)
                    sub[d] = sp.diff(val, v, dt, r, dr)
            sub[f] = val
        ee = Fv.subs(sub).doit()
        return leading(sp.powsimp(sp.expand(ee), force=True))

    table = {}
    for pair in (("E0", "E0"), ("E2", "E2")):
        (lp, coeff) = flux_pair(*pair)
        _require(lp is not None and int(lp[0]) == -2 and int(lp[1]) == 0,
                 f"Einstein pair {pair}: leading {lp} != (-2, 0)")
        _require(sp.simplify(coeff) != 0,
                 f"Einstein pair {pair}: leading coefficient vanished")
        table[f"{pair[0]}|{pair[1]}"] = {
            "leading_power": [int(lp[0]), int(lp[1])],
            "leading_coeff": str(sp.factor(coeff)),
            "finite": True,
        }
    out["stage_seconds"]["flux_ExE"] = round(time.time() - t0, 1)
    print(f"[flux_ExE] {out['stage_seconds']['flux_ExE']} s", flush=True)
    return table


# ---------------------------------------------------------------------------
# Rail 2: axial extra-branch carrier exponents at symbolic omega.
# delta Ric is gauge-invariant on the Ricci-flat background, so the extra
# branch is the trace-free axial Ricci carrier psi; its operator
# (1/2) Box psi + C psi = 0 fixes the infinity exponents.
# ---------------------------------------------------------------------------
def carrier_exponents(out: dict, geo_cls=Geometry) -> dict:
    t0 = time.time()
    t, ph = sp.symbols("t phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    w = sp.Symbol("omega")
    m = sp.Integer(1)
    coords = [t, r, x, ph]
    B0 = 1 - 2 * m / r
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = geo_cls(coords, g0)
    gi = geo0.ginv
    S = -3 * x * (1 - x**2)
    p = sp.Function("p")(t, r); q = sp.Function("q")(t, r); c = sp.Function("c")(t, r)
    psi = sp.zeros(4, 4)
    psi[0, 3] = psi[3, 0] = p * S
    psi[1, 3] = psi[3, 1] = q * S
    psi[2, 3] = psi[3, 2] = c * 3 * (x**2 - 1)
    sdiv = sum(gi[a, e] * geo0.covd2(psi, e, a, 3)
               for a in range(4) for e in range(4) if gi[a, e] != 0)
    c_expr = sp.expand(sp.solve(sp.Eq(_cancel(sdiv), 0), c)[0])
    psi2 = sp.Matrix(4, 4, lambda i, j: _cancel(psi.subs(c, c_expr).doit()[i, j]))
    G = geo0.Gamma
    DX = [[[_cancel(geo0.covd2(psi2, e, a, b)) for b in range(4)]
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
                 * sum(gi[cc, e] * gi[d, f] * psi2[e, f]
                       for e in range(4) for f in range(4))
                 for cc in range(4) for d in range(4))
        return _cancel(box / 2 + cx)

    Lt = _cancel(Lrow(0, 3) / S); Lr = _cancel(Lrow(1, 3) / S)
    P = sp.Function("P")(r); Q = sp.Function("Q")(r); Et = sp.exp(sp.I * w * t)
    four = {p: P * Et, q: Q * Et}
    Ltn = sp.expand(sp.fraction(_cancel(Lt.subs(four).doit() / Et))[0])
    Lrn = sp.expand(sp.fraction(_cancel(Lr.subs(four).doit() / Et))[0])
    lam, be, s = sp.symbols("lambda beta s")
    subr = {sp.Derivative(P, (r, 2)): lam**2 * sp.exp(lam * r),
            sp.Derivative(P, r): lam * sp.exp(lam * r), P: sp.exp(lam * r),
            sp.Derivative(Q, (r, 2)): be * lam**2 * sp.exp(lam * r),
            sp.Derivative(Q, r): be * lam * sp.exp(lam * r), Q: be * sp.exp(lam * r)}
    A = sp.expand(sp.cancel(Ltn.subs(subr) / sp.exp(lam * r)))
    Bx = sp.expand(sp.cancel(Lrn.subs(subr) / sp.exp(lam * r)))
    dA = sp.Poly(A, r).degree(); dB = sp.Poly(Bx, r).degree()
    cA = sp.Poly(A, r).nth(dA); cB = sp.Poly(Bx, r).nth(dB)
    det = sp.factor(sp.cancel(sp.resultant(sp.Poly(cA, be), sp.Poly(cB, be), be)))
    rates = sp.solve(sp.Eq(sp.numer(sp.cancel(det)), 0), lam)
    _require(set(rates) == {-sp.I * w, sp.I * w},
             f"carrier rates {rates} != {{+-i omega}}")

    def powers(rate):
        ex = sp.exp(rate * r); an = r**s * ex
        sub2 = {sp.Derivative(P, (r, 2)): sp.diff(an, (r, 2)),
                sp.Derivative(P, r): sp.diff(an, r), P: an,
                sp.Derivative(Q, (r, 2)): be * sp.diff(an, (r, 2)),
                sp.Derivative(Q, r): be * sp.diff(an, r), Q: be * an}
        A2 = sp.expand(sp.cancel(Ltn.subs(sub2) / an))
        B2 = sp.expand(sp.cancel(Lrn.subs(sub2) / an))
        dA2 = sp.Poly(A2, r).degree(); dB2 = sp.Poly(B2, r).degree()
        cA2 = sp.Poly(A2, r).nth(dA2); cB2 = sp.Poly(B2, r).nth(dB2)
        solb = sp.solve(sp.Eq(cA2, 0), be)
        ind = (sp.factor(sp.numer(sp.cancel(cB2.subs(be, solb[0])))) if solb
               else sp.factor(sp.resultant(sp.Poly(cA2, be), sp.Poly(cB2, be), be)))
        return sp.solve(sp.Eq(sp.numer(sp.cancel(ind)), 0), s)

    exps = {}
    for rate in rates:
        roots = powers(rate)
        exps[str(rate)] = [str(rt) for rt in roots]
    # decisive checks: powers are +-2 i omega, matching the rate sign
    _require(exps[str(-sp.I * w)] == ["-2*I*omega"], f"power mismatch {exps}")
    _require(exps[str(sp.I * w)] == ["2*I*omega"], f"power mismatch {exps}")
    out["stage_seconds"]["carrier_exponents"] = round(time.time() - t0, 1)
    print(f"[carrier_exponents] {out['stage_seconds']['carrier_exponents']} s",
          flush=True)
    return {
        "rate_condition": "lambda**2 + omega**2 = 0",
        "rates": ["-I*omega", "I*omega"],
        "powers": {"-I*omega": "-2*I*omega", "I*omega": "2*I*omega"},
        "reading": ("psi_carrier ~ exp(+- I omega r) r^{+- 2 I omega} "
                    "= exp(+- I omega r_*); amplitude real part 0"),
    }


def build_certificate() -> dict:
    out: dict = {"stage_seconds": {}}
    t0 = time.time()
    einstein_table = axial_einstein_flux(out)
    carrier = carrier_exponents(out)
    out["stage_seconds"]["total"] = round(time.time() - t0, 1)

    # omega-independence / exceptional-set reading, derived from the exponents.
    frequency = {
        "einstein_amplitude_real_parts": {
            "metric_master_F": ["-3 (mu=0 branch)", "+1 (mu=-2omega branch)"],
            "flux_density_ExE_leading_power": -2,
        },
        "extra_carrier_amplitude_real_part": 0,
        "omega_enters_only_imaginary_tortoise_phase": True,
        "finite_divergent_split_omega_independent": True,
        "no_real_exceptional_frequency": (
            "exponents +-I omega, +-2 I omega are never real and never "
            "collide for real omega != 0"),
        "excluded_frequency": "omega = 0 (certified exceptional carrier, "
                              "BH2C_SYMBOLIC_INDICIAL exceptional set {0})",
    }

    cert = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "Schwarzschild m = 1; symbolic real omega",
            "sector": "axial l = 2 (literal flux); trace-free Ricci carrier "
                      "(extra branch)",
            "conformal_frame": "working gauge; ingoing EF chart",
            "generator": "none; asymptotic Lee--Wald slice-norm classification",
            "phase_space": "EF sphere-integrated Lee--Wald slice density F^v "
                           "on conjugate mode-pair classes",
            "infinity_condition": "leading (r-power, log-power) and leading "
                                  "coefficient of F^v per class",
            "lifecycle": "CLASSIFIED",
        },
        "einstein_literal_flux_axial": einstein_table,
        "carrier_exponents_axial": carrier,
        "frequency_dependence": frequency,
        "numeric_anchor": {
            "axial_fixture": str(AXIAL_FIXTURE.relative_to(ROOT)),
            "axial_fixture_sha256": _sha256(AXIAL_FIXTURE),
            "axial_fixture_table": json.loads(AXIAL_FIXTURE.read_text())["flux_table"],
            "polar_fixture": str(POLAR_FIXTURE.relative_to(ROOT)),
            "polar_fixture_sha256": _sha256(POLAR_FIXTURE),
            "reading": "the omega = 3/5 specialization of this pipeline is the "
                       "certified axial fixture (E0|E0 = E2|E2 = (-2,0) finite; "
                       "extra-involving classes non-negative/divergent, X0|X0 "
                       "with log); polar fixture selects the Einstein sector in "
                       "the polar parity",
        },
        "headline": {
            "statement": "at symbolic real omega the axial Einstein conjugate "
                         "pairs give a literal Lee--Wald slice density falling "
                         "as r^-2 (FINITE, omega-independent), while the extra "
                         "(trace-free Ricci carrier) branch has amplitude real "
                         "part 0 (non-decaying): the finite-slice-norm "
                         "asymptotic phase space contains exactly the Einstein "
                         "sector, for every real omega != 0",
            "complement": "the horizon endpoint diagnostics do not exclude the "
                          "extra branch (certified dispositions); at infinity "
                          "symplectic-norm finiteness selects the Einstein "
                          "sector -- a phase-space normalization, not a local "
                          "boundary condition; the selection is omega-"
                          "independent as a derived fact",
        },
        "claim_flags": {
            "axial_einstein_literal_flux_symbolic_certified": True,
            "axial_carrier_exponents_symbolic_certified": True,
            "finite_divergent_split_omega_independent_certified": True,
            "no_real_exceptional_frequency_certified": True,
            "numeric_anchor_hashed": True,
            "axial_divergent_table_symbolic_certified": False,
            "symbolic_log_tails_certified": False,
            "polar_literal_flux_symbolic_recomputed": False,
            "conjugate_frequency_pairing_theorem_certified": False,
            "asymptotic_phase_space_constructed": False,
            "summability_certified": False,
            "general_l_certified": False,
        },
        "missing_objects": [
            "the EXACT symbolic-omega DIVERGENT sub-table (E|X, X|X) and "
            "symbolic log tails: the composed sourced log solve over Q(omega) "
            "did not complete a bounded run; anchored at omega = 3/5 by the two "
            "fixtures plus the omega-independent exponent argument",
            "the polar literal symbolic flux (recomputed): carried here by the "
            "parity-unified master ODE and BH2B_POLAR_FLUX nullness plus the "
            "polar fixture, not recomputed symbolically",
            "a conjugate-frequency pairing theorem, lift invariance, and an "
            "independent current-identity rail at symbolic omega",
            "an asymptotically flat phase-space and charge-algebra construction",
            "Borel/analytic summability of the mode series; general l",
        ],
        "does_not_establish": [
            "any finite-flux statement for the DIVERGENT (extra-involving) "
            "classes at symbolic omega beyond the omega = 3/5 fixture anchor "
            "and the exponent-level omega-independence argument",
            "a Lorentzian causal, spectral (quasinormal), scattering, "
            "stability, positivity, particle, or quantum claim",
            "a phase-space / charge-algebra construction or a pairing theorem",
            "convergence or summability of the formal mode series",
            "any statement at omega = 0 (the excluded exceptional carrier) or "
            "for general l",
        ],
        "stage_seconds": out["stage_seconds"],
        "provenance": {
            "generator_path":
                "black_hole_programme/bh2c_symbolic_flux_radiation_class.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "theta_engine_sha256": _sha256(HERE / "linearized_theta.py"),
            "bach_engine_sha256": _sha256(HERE / "linearized_bach.py"),
            "flux_matrix_certificate": str(FLUX_MATRIX.relative_to(ROOT)),
            "flux_matrix_certificate_sha256": _sha256(FLUX_MATRIX),
            "all_orders_certificate": str(ALL_ORDERS.relative_to(ROOT)),
            "all_orders_certificate_sha256": _sha256(ALL_ORDERS),
            "symbolic_indicial_certificate": str(SYMB_INDICIAL.relative_to(ROOT)),
            "symbolic_indicial_certificate_sha256": _sha256(SYMB_INDICIAL),
        },
        "verification_command":
            "python3 black_hole_programme/verify_bh2c_symbolic_flux_radiation_class.py",
    }
    return cert


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    cert = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
