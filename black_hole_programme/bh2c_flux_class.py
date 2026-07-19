"""BH-2C stage 3: finite-flux boundary class -- Einstein selected at infinity.

Fail-closed builder for
`black_hole_programme/certificates/BH2C_FLUX_CLASS.json`.

Verdict: BH2C_FINITE_FLUX_BOUNDARY_CLASS_EINSTEIN_SELECTED_AT_INFINITY.

Setting: Schwarzschild m = 1, axial l = 2, EF chart, omega = 3/5 fixture.

Exact results:

1. COMPOSED METRIC LOG TAILS: solving delta Ric[h] = psi at r -> infinity
   for each carrier formal solution, the pure-power ansatz is INCONSISTENT
   and the single-log ansatz e^{i mu r} sum (a_n + b_n ln r) r^{s-n} is
   CONSISTENT with nonzero log coefficients, in BOTH characteristic
   sectors: the composed (extra-branch) metric carries logarithmic tails
   at infinity -- the realization of the repeated-root resonance at the
   inhomogeneous level (the homogeneous formal systems are log-free);
2. FLUX POWER TABLE: substituting conjugate pair classes into the EF
   sphere-integrated Lee--Wald slice density F^v:
     Einstein x Einstein: r^-2 (both sectors)  -> slice norm FINITE;
     Einstein x composed: r^0 and r^1          -> DIVERGENT;
     composed x composed: r^0 ln r and r^2     -> DIVERGENT;
3. INVARIANCE: the divergences cannot be removed by Einstein-shifts of
   the composed representatives (the leading powers of the classes cannot
   cancel across rows): the non-normalizability of the extra sector at
   infinity is representative-independent.

Consequence: at the fixture mode level, the finite-slice-norm asymptotic
phase space at infinity contains EXACTLY the Einstein sector: the extra
branch, causally unavoidable at the horizon, is excluded at infinity by
symplectic-norm finiteness -- a phase-space normalization, not a local
boundary condition.  This decides the 'finite-flux boundary class'
station of the planning directive at the fixture level.

NOT claimed: symbolic-frequency table, the polar table, summability,
an asymptotically flat phase-space construction, charge algebra, general
l, or any stability statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

import weyl_geometry as wg
from linearized_bach import LinearizedBach
from linearized_theta import LinearizedTheta
from weyl_geometry import Geometry

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2C_FLUX_CLASS.json"
SCHEMA_PATH = HERE / "schema" / "bh2c-flux-class-v1.schema.json"
JORDAN = HERE / "certificates" / "BH2C_ASYMPTOTIC_JORDAN.json"
MET = HERE / "certificates" / "BH2C_METRIC_LEADING.json"

SCHEMA_NAME = "pure-weyl-bh2c-flux-class-v1"
RESULT_ID = "PURE_WEYL_BH2C_FLUX_CLASS"
RESULT_TOKEN = "BH2C_FINITE_FLUX_BOUNDARY_CLASS_EINSTEIN_SELECTED_AT_INFINITY"


class FluxClassError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise FluxClassError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_analysis(geo_cls) -> dict:
    t0_all = time.time()
    out: dict = {"stage_seconds": {}}
    wnum = sp.Rational(3, 5)
    NI = 4
    # Carrier depth: the composed X-source carries positive r-weights, so
    # source keys built from depth-N carrier jets are valid only through
    # N minus that weight.  NC = 12 gives a wide validity margin over the
    # staircase window (NI = 4); the table and log-tail dichotomy were
    # re-verified identical against the original NC = 4 run (2026-07-19,
    # polar-table campaign; see reports/bh2c-polar-flux-class.md).
    NC = 12
    DEP = NC + 4
    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    w = sp.Symbol("omega", positive=True)
    alpha = sp.Symbol("alpha", positive=True)
    Lg = sp.Symbol("Lg", positive=True)
    sig = sp.Symbol("sigma")

    def _cancel(e):
        return sp.cancel(sp.together(e))

    B0 = 1 - 2 / r
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = geo_cls([v, r, x, ph], g0)
    gi = geo0.ginv
    S_ax = -3 * x * (1 - x**2)
    E = sp.exp(sp.I * w * v)

    # ---- EF axial F^v -----------------------------------------------------
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

    # ---- sourced h-system -------------------------------------------------
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
    NXv = sp.Matrix([sp.expand(H0p).coeff(XS), 0, sp.expand(H1pp).coeff(XS)])
    NTv = sp.Matrix([0, 0, sp.expand(H1pp).coeff(TS)])
    M3w = M3.subs(w, wnum)

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

    Mser = {(i, j): inv_series_entry(M3w[i, j], DEP)
            for i in range(3) for j in range(3)}
    Mkc = [sp.Matrix(3, 3, lambda i, j: Mser[(i, j)].get(k, sp.Integer(0)))
           for k in range(DEP + 1)]
    out["stage_seconds"]["h_system"] = round(time.time() - t0, 1)

    # ---- carrier formal series at infinity --------------------------------
    t0 = time.time()
    p_c = sp.Function("p")(v, r)
    q_c = sp.Function("q")(v, r)
    c_c = sp.Function("c")(v, r)
    psi_a = sp.zeros(4, 4)
    psi_a[0, 3] = psi_a[3, 0] = p_c * S_ax
    psi_a[1, 3] = psi_a[3, 1] = q_c * S_ax
    psi_a[2, 3] = psi_a[3, 2] = c_c * 3 * (x**2 - 1)
    sdiv = sum(gi[a, e] * geo0.covd2(psi_a, e, a, 3)
               for a in range(4) for e in range(4) if gi[a, e] != 0)
    c_expr = sp.solve(sp.Eq(_cancel(sdiv), 0), c_c)[0]
    psi_a2 = sp.Matrix(4, 4, lambda i, j: _cancel(psi_a.subs(c_c, c_expr).doit()[i, j]))
    G = geo0.Gamma
    DXa = [[[_cancel(geo0.covd2(psi_a2, e, a, b)) for b in range(4)]
            for a in range(4)] for e in range(4)]

    def covd2X2(e, f, a, b):
        s = sp.diff(DXa[f][a][b], (v, r, x, ph)[e])
        for hh in range(4):
            s -= (G[hh][e][f] * DXa[hh][a][b] + G[hh][e][a] * DXa[f][hh][b]
                  + G[hh][e][b] * DXa[f][a][hh])
        return s

    def Lrow(a, b):
        box = sum(gi[e, f] * covd2X2(e, f, a, b)
                  for e in range(4) for f in range(4) if gi[e, f] != 0)
        cx = sum(geo0.Weyl[a][cc][b][d]
                 * sum(gi[cc, e] * gi[d, f] * psi_a2[e, f]
                       for e in range(4) for f in range(4))
                 for cc in range(4) for d in range(4))
        return _cancel(box / 2 + cx)

    Pf = sp.Function("P")(r)
    Qf = sp.Function("Q")(r)
    four_a = {p_c: Pf * E, q_c: Qf * E}
    rows_c = [sp.expand(_cancel(Lrow(0, 3).subs(four_a).doit() / (E * S_ax))),
              sp.expand(_cancel(Lrow(1, 3).subs(four_a).doit() / (E * S_ax)))]
    funcs_c = [Pf, Qf]

    def apply_slot(rr_, expo_mu, fn, depth):
        val = sp.exp(sp.I * expo_mu * r) * r**sig
        subm = {d: sp.diff(val, r, d.derivative_count)
                for d in rr_.atoms(sp.Derivative) if d.args[0] == fn}
        subm[fn] = val
        zmap = {}
        for other in funcs_c:
            if other == fn:
                continue
            for d in rr_.atoms(sp.Derivative):
                if d.args[0] == other:
                    zmap[d] = 0
            zmap[other] = 0
        e = _cancel(sp.expand(rr_.subs(subm).subs(zmap).doit()
                              / (sp.exp(sp.I * expo_mu * r) * r**sig)))
        return inv_series_entry(e, depth)

    def carrier_series(muv, sig_top):
        aps = [{slot: apply_slot(rows_c[i].subs(w, wnum), muv, fn, NC + 3)
                for slot, fn in (("P", Pf), ("Q", Qf))} for i in range(2)]
        glead = min(min(ser.keys()) for ap in aps for ser in ap.values())

        def MkC(k, sigval):
            return sp.Matrix(2, 2, lambda i, j: sp.expand(
                aps[i][("P", "Q")[j]].get(glead + k, sp.Integer(0))
                .subs(sig, sigval)))

        ns = MkC(0, sig_top).nullspace()
        _require(len(ns) == 1, "carrier leading nullspace not 1")
        c = [sp.Matrix(ns[0])]
        for n in range(1, NC + 1):
            rhs = -sum((MkC(n - j, sig_top - j) * c[j] for j in range(n)),
                       sp.zeros(2, 1))
            Mn = MkC(0, sig_top - n)
            if Mn.det() != 0:
                c.append(Mn.solve(rhs))
            else:
                soln, params = Mn.gauss_jordan_solve(rhs)
                c.append(soln.subs({pp: 0 for pp in params}))
        return c

    carriers = {"0": (sp.Integer(0), sp.Integer(0),
                      carrier_series(sp.Integer(0), sp.Integer(0))),
                "-2w": (-2 * wnum, -4 * sp.I * wnum,
                        carrier_series(-2 * wnum, -4 * sp.I * wnum))}
    out["stage_seconds"]["carrier_inf"] = round(time.time() - t0, 1)

    # ---- homogeneous h-solutions ------------------------------------------
    t0 = time.time()

    def hom_solutions(muv, sig0, njet=NI):
        B0c = Mkc[0] - sp.I * muv * sp.eye(3)
        unk = [sp.Symbol(f"z_{n}_{i}") for n in range(njet + 1) for i in range(3)]

        def yv(n):
            return sp.Matrix(3, 1, lambda i, _: sp.Symbol(f"z_{n}_{i}"))

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
           "-2w": hom_solutions(-2 * wnum, -4 * sp.I * wnum + 1)}
    _require(all(len(v2) >= 1 for v2 in hom.values()), "no homogeneous solutions")
    out["stage_seconds"]["hom"] = round(time.time() - t0, 1)

    # ---- composed series: pure-power fails, single-log succeeds -----------
    t0 = time.time()
    c_four = _cancel(sp.expand(c_expr.subs({p_c: Pf * E, q_c: Qf * E}).doit()
                               / E)).subs(w, wnum)

    def series_sub(expr, Pser, Qser, muv, depth, sig_val):
        u = sp.Symbol("u_inv")
        sig0 = sp.Symbol("sig0_")
        PP = sum(Pser[k] * u**k for k in range(len(Pser)))
        QQ = sum(Qser[k] * u**k for k in range(len(Qser)))
        val_P = sp.exp(sp.I * muv * r) * r**sig0 * PP.subs(u, 1 / r)
        val_Q = sp.exp(sp.I * muv * r) * r**sig0 * QQ.subs(u, 1 / r)
        subm = {}
        for d in list(expr.atoms(sp.Derivative)):
            if d.args[0] == Pf:
                subm[d] = sp.diff(val_P, r, d.derivative_count)
            if d.args[0] == Qf:
                subm[d] = sp.diff(val_Q, r, d.derivative_count)
        subm[Pf] = val_P
        subm[Qf] = val_Q
        e = expr.subs(subm).doit()
        e = sp.powsimp(sp.expand(e / (sp.exp(sp.I * muv * r) * r**sig0)),
                       force=True)
        e = e.subs(sig0, sig_val)
        return inv_series_entry(_cancel(sp.together(e)), depth)

    def conv(a, b, depth):
        outc = {}
        for ka, va in a.items():
            for kb, vb in b.items():
                if ka + kb <= depth:
                    outc[ka + kb] = sp.expand(outc.get(ka + kb, 0) + va * vb)
        return outc

    composed = {}
    for key, (muv, sig_top, ser) in carriers.items():
        Pser = [ser[n][0, 0] for n in range(len(ser))]
        Qser = [ser[n][1, 0] for n in range(len(ser))]
        Xser = series_sub(c_four, Pser, Qser, muv, DEP, sig_top)
        NXs = {i: inv_series_entry(NXv[i].subs(w, wnum), DEP) for i in range(3)}
        NTs = {i: inv_series_entry(NTv[i].subs(w, wnum), DEP) for i in range(3)}
        Qs = {k: Qser[k] for k in range(len(Qser))}
        src = {i: {} for i in range(3)}
        for i in range(3):
            for kk, vv2 in conv(NXs[i], Xser, DEP).items():
                src[i][kk] = sp.expand(src[i].get(kk, 0) + vv2)
            for kk, vv2 in conv(NTs[i], Qs, DEP).items():
                src[i][kk] = sp.expand(src[i].get(kk, 0) + vv2)
        B0c = Mkc[0] - sp.I * muv * sp.eye(3)
        njet = NI
        kmin = min([min(src[i].keys()) for i in range(3) if src[i]] + [0])
        S = 1 - kmin
        s_base = sig_top + S

        def av(n):
            return sp.Matrix(3, 1, lambda i, _: sp.Symbol(f"a_{n}_{i}"))

        def bv(n):
            return sp.Matrix(3, 1, lambda i, _: sp.Symbol(f"b_{n}_{i}"))

        # (i) pure-power ansatz must FAIL
        unkp = [sp.Symbol(f"a_{n}_{i}") for n in range(njet + 1) for i in range(3)]
        eqsp = []
        for n in range(-1, njet):
            lhs = (s_base - n) * av(n) if 0 <= n <= njet else sp.zeros(3, 1)
            rhs = sp.zeros(3, 1)
            for k in range(0, n + 2):
                j = n + 1 - k
                if 0 <= j <= njet:
                    Bk = B0c if k == 0 else Mkc[k]
                    rhs += Bk * av(j)
            sv = sp.Matrix(3, 1, lambda i, _: src[i].get(n + 1 - S, sp.Integer(0)))
            diff = (lhs - rhs - sv) if 0 <= n <= njet else -(rhs + sv)
            eqsp.extend(sp.expand(diff[i]) for i in range(3))
        Mlp, blp = sp.linear_eq_to_matrix(eqsp, unkp)
        pure_ok = True
        try:
            Mlp.gauss_jordan_solve(blp)
        except ValueError:
            pure_ok = False
        _require(not pure_ok, f"carrier {key}: pure-power unexpectedly consistent")
        # (ii) single-log ansatz must SUCCEED with nonzero log part
        unk = (unkp + [sp.Symbol(f"b_{n}_{i}") for n in range(njet + 1)
                       for i in range(3)])
        eqs = []
        for n in range(-1, njet):
            lhsL = (s_base - n) * bv(n) if 0 <= n <= njet else sp.zeros(3, 1)
            rhsL = sp.zeros(3, 1)
            lhs1 = (((s_base - n) * av(n) + bv(n)) if 0 <= n <= njet
                    else sp.zeros(3, 1))
            rhs1 = sp.zeros(3, 1)
            for k in range(0, n + 2):
                j = n + 1 - k
                if 0 <= j <= njet:
                    Bk = B0c if k == 0 else Mkc[k]
                    rhsL += Bk * bv(j)
                    rhs1 += Bk * av(j)
            sv = sp.Matrix(3, 1, lambda i, _: src[i].get(n + 1 - S, sp.Integer(0)))
            dL = (lhsL - rhsL) if 0 <= n <= njet else -rhsL
            d1_ = (lhs1 - rhs1 - sv) if 0 <= n <= njet else -(rhs1 + sv)
            eqs.extend(sp.expand(dL[i]) for i in range(3))
            eqs.extend(sp.expand(d1_[i]) for i in range(3))
        Ml, bl = sp.linear_eq_to_matrix(eqs, unk)
        soln, params = Ml.gauss_jordan_solve(bl)
        soln = soln.subs({pp: 0 for pp in params})
        na = (njet + 1) * 3
        A = [sp.Matrix(3, 1, lambda i, _: soln[3 * n + i]) for n in range(njet + 1)]
        Bl = [sp.Matrix(3, 1, lambda i, _: soln[na + 3 * n + i])
              for n in range(njet + 1)]
        _require(any(any(Bl[n][i, 0] != 0 for i in range(3))
                     for n in range(njet + 1)),
                 f"carrier {key}: log part vanished")
        composed[key] = (muv, s_base, A, Bl)
    out["stage_seconds"]["composed_log"] = round(time.time() - t0, 1)

    # ---- flux power table --------------------------------------------------
    t0 = time.time()

    def hom_profile(Y, muv, sig0):
        H0e = sum(Y[n][0, 0] * r**(sig0 - n) for n in range(len(Y)))
        H1e = sum(Y[n][1, 0] * r**(sig0 - n) for n in range(len(Y)))
        ph_ = sp.exp(sp.I * muv * r)
        return (H0e * ph_, H1e * ph_)

    def comp_profile(entry):
        muv, s_base, A, Bl = entry
        H0e = sum((A[n][0, 0] + Bl[n][0, 0] * sp.log(r)) * r**(s_base - n)
                  for n in range(len(A)))
        H1e = sum((A[n][1, 0] + Bl[n][1, 0] * sp.log(r)) * r**(s_base - n)
                  for n in range(len(A)))
        ph_ = sp.exp(sp.I * muv * r)
        return (H0e * ph_, H1e * ph_)

    profiles = {"E0": hom_profile(hom["0"][0], sp.Integer(0), sp.Integer(1)),
                "E2": hom_profile(hom["-2w"][0], -2 * wnum, -4 * sp.I * wnum + 1),
                "X0": comp_profile(composed["0"]),
                "X2": comp_profile(composed["-2w"])}

    def leading_power(expr):
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
        return best

    def flux_pair(na, nb):
        (h0A, h1A) = profiles[na]
        (h0B, h1B) = profiles[nb]
        EA = sp.exp(sp.I * wnum * v)
        EB = sp.exp(-sp.I * wnum * v)
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
        e = Fv.subs(sub).doit()
        return leading_power(sp.powsimp(sp.expand(e), force=True))

    expected = {("E0", "E0"): (-2, 0), ("E0", "X0"): (0, 0),
                ("X0", "X0"): (0, 1), ("E2", "E2"): (-2, 0),
                ("E2", "X2"): (1, 0), ("X2", "X2"): (2, 0)}
    table = {}
    for (na, nb), exp_lp in expected.items():
        lp = flux_pair(na, nb)
        _require(lp is not None and sp.Integer(lp[0]) == exp_lp[0]
                 and int(lp[1]) == exp_lp[1],
                 f"pair ({na},{nb}): leading {lp} != expected {exp_lp}")
        table[f"{na}|{nb}"] = [str(lp[0]), int(lp[1])]
    # invariance: divergent classes cannot be cancelled by Einstein shifts
    _require(expected[("X0", "X0")][0] >= 0 and expected[("X2", "X2")][0] >= 0
             and expected[("E0", "E0")][0] < -1 and expected[("E2", "E2")][0] < -1,
             "class separation lost")
    out["table"] = table
    out["stage_seconds"]["flux_table"] = round(time.time() - t0, 1)
    out["stage_seconds"]["total"] = round(time.time() - t0_all, 1)
    return out


def build_certificate() -> dict:
    res = run_analysis(Geometry)
    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "Schwarzschild m = 1 fixture; omega = 3/5",
            "conformal_frame": "working gauge; ingoing EF chart",
            "generator": "none; asymptotic slice-norm classification",
            "phase_space": "EF sphere-integrated Lee-Wald slice density F^v on formal pair classes",
            "horizon_condition": "none; infinity-local statement",
            "infinity_condition": "leading (r-power, log-power) of F^v per class",
            "lifecycle": "CLASSIFIED",
        },
        "log_tails": {
            "statement": "for each carrier formal solution the pure-power composed ansatz is INCONSISTENT and the single-log ansatz is CONSISTENT with nonzero log part, in both characteristic sectors: the composed (extra-branch) metric carries logarithmic tails at infinity",
            "contrast": "the homogeneous formal systems are log-free (BH2C_ASYMPTOTIC_JORDAN): the logs are injected by the source resonance -- the inhomogeneous realization of the repeated characteristic root",
        },
        "flux_table": res["table"],
        "headline": {
            "statement": "Einstein x Einstein slice density falls as r^-2 (slice norm FINITE); every class involving the composed modes has non-negative leading power (up to r^2 and r^0 log r): DIVERGENT slice norm, invariant under Einstein-shifts of the representative -- the finite-slice-norm asymptotic phase space at infinity contains exactly the Einstein sector at the fixture level",
            "complement": "the horizon endpoint diagnostics do not exclude the extra branch (certified dispositions); at infinity, symplectic-norm finiteness DOES select the Einstein sector -- a phase-space normalization, not a local boundary condition",
        },
        "claim_flags": {
            "composed_log_tails_certified": True,
            "pure_power_exclusion_certified": True,
            "flux_power_table_certified": True,
            "einstein_finite_class_certified": True,
            "extra_divergent_class_certified": True,
            "symbolic_frequency_certified": False,
            "polar_table_certified": False,
            "summability_certified": False,
            "asymptotic_phase_space_constructed": False,
            "general_l_certified": False,
        },
        "missing_objects": [
            "symbolic-frequency table (omega = 3/5 fixture only)",
            "the polar flux power table (needs the polar composed asymptotics)",
            "Borel/analytic summability of the log-extended series",
            "an asymptotically flat phase-space and charge-algebra construction",
            "general l",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2c_flux_class.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "jordan_certificate": str(JORDAN.relative_to(ROOT)),
            "jordan_certificate_sha256": _sha256(JORDAN),
            "metric_leading_certificate": str(MET.relative_to(ROOT)),
            "metric_leading_certificate_sha256": _sha256(MET),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2c_flux_class.py",
    }
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    certificate = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
