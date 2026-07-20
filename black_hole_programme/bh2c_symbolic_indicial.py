"""Symbolic-frequency indicial structure at Schwarzschild infinity.

Verdict token: BH2C_SYMBOLIC_INDICIAL_EXCEPTIONAL_SET_IS_OMEGA_ZERO
Tags: LOCAL-ALGEBRAIC + REDUCED-MODE.  Lifecycle: CLASSIFIED.

This is the first split of the asymptotic-Jordan work item: the indicial
layer, computed with SYMBOLIC omega in both parities.  Every existing
asymptotic certificate records this data at the omega = 3/5 fixture (and
BH2C_ASYMPTOTIC_JORDAN explicitly flags
`polar_mu2w_symbolic_certified: False`); a fixture cannot decide which
frequencies are exceptional, because an exceptional frequency is by
definition one where the indicial data degenerates.

Results (all exact in symbolic omega):

1. POLAR carrier (6-dim first-order system at infinity).
   Leading matrix charpoly  lam^3 (lam + 2 I omega)^3.  Both oscillatory
   eigenvalues mu in {0, -2 I omega} have geometric = algebraic
   multiplicity 3, so the two sectors split semisimply for every
   omega != 0.  Frobenius exponents (producer convention, profiles
   r^{sigma0 - n}):
       mu = 0        : sigma0 in {-1, -2, -3}
       mu = -2I omega: sigma0 in {-4 I omega - 1, -4 I omega - 2,
                                  -4 I omega - 3}
   The leading entries reproduce EXACTLY the sigma0 values the certified
   BH2C producers feed in at the fixture (-1 and -4 I omega - 1), which
   is the cross-validation rail against certified data.  The
   mu = -2 omega sector is thereby lifted from fixture-only to symbolic.

2. AXIAL.  The level-1 cascade K is algebraic in H1 with coefficient
   omega^2/4 - 1/r^2 + 2/r^3 (leading omega^2/4).  The level-2
   (H0'', H2'') block has IDENTICALLY ZERO determinant -- rank 1 --
   reproducing symbolically the structure certified at the fixtures by
   BH2A_COMPOSED_REPAIR.  In Regge-Wheeler gauge (H2 = 0) a single
   second-order ODE closes, with leading charpoly lam (lam + 2 I omega)
   and simple semisimple exponents in each sector.

3. RESONANCE STRUCTURE IS FREQUENCY-INDEPENDENT.  Within either sector
   the exponent differences are the integers {1, 2}, independent of
   omega.  Across sectors the differences are 4 I omega + k, which is an
   integer only for imaginary omega -- never for real omega != 0.  Hence
   no resonance condition moves with real frequency.

4. Re(sigma) IS FREQUENCY-INDEPENDENT (polar carrier).  Since 4 I omega
   is purely imaginary for real omega, Re(sigma0) = -1, -2, -3 in BOTH
   OSCILLATORY SECTORS of the polar carrier for every real omega.  The
   curvature-level decay rates therefore do not depend on the frequency.
   (This is a statement about the carrier, not the metric: the axial
   RW-gauge h-system exponents are +1 and -4 I omega + 1, i.e. metric-
   level growth r^1, consistent with the certified hom h-jets and with
   BH2C_METRIC_LEADING's one-power enhancement bound.)

5. EXCEPTIONAL SET.  For real omega the indicial data degenerates only at
   omega = 0, and it does so in two independent ways: the two oscillatory
   eigenvalues collide (0 = -2 I omega), and the axial cascade
   coefficient loses its leading term (omega^2/4 -> 0).  omega = 0 is
   separately classified by BH2_OMEGA_ZERO.  So:
       exceptional set (real frequencies) = {0}.

Decisive mutations:
  M1: at omega = 0 the polar leading matrix charpoly collapses to lam^6
      with geometric multiplicity 3 < 6 -- a genuine Jordan degeneration,
      confirming omega = 0 is exceptional rather than a coordinate
      artifact.
  M2: the cascade coefficient's leading term is omega^2/4, which vanishes
      exactly at omega = 0 and nowhere else.

NOT established here (successor splits of the same work item):
  - all-orders metric reconstruction maps;
  - the symbolic-frequency finite-flux power table (result 4 makes the
    Einstein-selection classification frequency-independent PLAUSIBLE but
    it is NOT computed here and is NOT claimed);
  - the assembled endpoint-nonselection theorem;
  - general l; summability.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

import bh2b_polar_reach as reach
from weyl_geometry import Geometry

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMA_NAME = "pure-weyl-bh2c-symbolic-indicial-v1"
SCHEMA_PATH = HERE / "schema" / "bh2c-symbolic-indicial-v1.schema.json"
CERT_PATH = HERE / "certificates" / "BH2C_SYMBOLIC_INDICIAL.json"
RESULT_ID = "PURE_WEYL_BH2C_SYMBOLIC_INDICIAL"
RESULT_TOKEN = "BH2C_SYMBOLIC_INDICIAL_EXCEPTIONAL_SET_IS_OMEGA_ZERO"
JORDAN_CERT = HERE / "certificates" / "BH2C_ASYMPTOTIC_JORDAN.json"

NORD = 6            # 1/r jet depth for the axial series reduction
N = 4

_cancel = lambda e: sp.cancel(sp.together(e))
lam = sp.Symbol("lam")


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ======================= polar carrier (6-dim) ==========================

def polar_indicial(geo_cls):
    R = reach.run_analysis(geo_cls, light=True)
    r = R["syms"]["r"]
    m = R["syms"]["m"]
    w = R["syms"]["omega"]
    sys3 = [_cancel(e.subs({m: sp.Integer(1)})) for e in R["sys3"]]
    funcs3 = R["funcs3"]

    d2 = lambda fn: sp.Derivative(fn, (r, 2))
    M2 = sp.Matrix(3, 3, lambda i, j:
                   _cancel(sp.expand(sys3[i]).coeff(d2(funcs3[j]))))
    _require(_cancel(M2.det()) != 0, "sliced principal part singular")
    Minv = M2.inv()
    dim = 6
    vars_list = [(j, k) for j in range(3) for k in range(2)]
    idx = {vk: i for i, vk in enumerate(vars_list)}

    def coeff_of(e, fn, k):
        tgt = fn if k == 0 else sp.Derivative(fn, (r, k))
        return sp.expand(e).coeff(tgt)

    A6 = sp.zeros(dim, dim)
    for j in range(3):
        A6[idx[(j, 0)], idx[(j, 1)]] = 1
    for j_top in range(3):
        rowi = idx[(j_top, 1)]
        for (g2, k) in vars_list:
            s = sum(Minv[j_top, i] * coeff_of(sys3[i], funcs3[g2], k)
                    for i in range(3))
            A6[rowi, idx[(g2, k)]] = _cancel(-s)

    u = sp.Symbol("u", positive=True)

    def ser(e, kmax=1):
        if e == 0:
            return {}
        num, den = sp.fraction(_cancel(e))
        ratio = sp.cancel(sp.expand(num.subs(r, 1 / u))
                          / sp.expand(den.subs(r, 1 / u)))
        s = sp.series(ratio, u, 0, kmax + 1).removeO()
        pol = sp.Poly(sp.expand(s), u)
        return {mo[0]: pol.coeff_monomial(u**mo[0]) for mo in pol.monoms()
                if mo[0] <= kmax}

    A0 = sp.zeros(dim, dim)
    A1 = sp.zeros(dim, dim)
    for i in range(dim):
        for j in range(dim):
            s = ser(A6[i, j], 1)
            A0[i, j] = _cancel(s.get(0, sp.Integer(0)))
            A1[i, j] = _cancel(s.get(1, sp.Integer(0)))

    cp0 = sp.factor(sp.expand(A0.charpoly(lam).as_expr()))
    _require(sp.simplify(cp0 - lam**3 * (lam + 2 * sp.I * w)**3) == 0,
             f"polar leading charpoly unexpected: {cp0}")

    out = {"charpoly": sp.sstr(cp0), "sectors": {}}
    for mu in (sp.Integer(0), -2 * sp.I * w):
        E = (A0 - mu * sp.eye(dim)).nullspace()
        _require(len(E) == 3, f"sector {mu}: geometric multiplicity "
                              f"{len(E)} != 3 (algebraic 3)")
        other = -2 * sp.I * w if mu == 0 else sp.Integer(0)
        F = sp.Matrix.hstack(*(A0 - other * sp.eye(dim)).nullspace())
        M = sp.Matrix.hstack(*E).row_join(F)
        _require(_cancel(M.det()) != 0, "eigenbasis degenerate")
        Ared = (M.inv() * A1 * M)[:3, :3].applyfunc(_cancel)
        rts = sp.roots(sp.Poly(Ared.charpoly(lam).as_expr(), lam))
        # producer convention: profiles r^{sigma0 - n}; sigma0 = +eigenvalue
        sig0 = sorted([_cancel(k) for k in rts], key=lambda z: sp.sstr(z))
        _require(sum(rts.values()) == 3, "exponent count != 3")
        for s0 in sig0:
            gm = len((Ared - s0 * sp.eye(3)).nullspace())
            _require(gm == rts[s0], f"exponent {s0} not semisimple")
        out["sectors"][sp.sstr(mu)] = [sp.sstr(s) for s in sig0]

    # expected exact exponent sets
    exp0 = {sp.Integer(-1), sp.Integer(-2), sp.Integer(-3)}
    expm = {-4 * sp.I * w - 1, -4 * sp.I * w - 2, -4 * sp.I * w - 3}
    got0 = {sp.sympify(s) for s in out["sectors"]["0"]}
    gotm = {sp.sympify(s) for s in out["sectors"][sp.sstr(-2 * sp.I * w)]}
    _require(all(any(sp.simplify(a - b) == 0 for b in got0) for a in exp0),
             f"mu=0 exponents {got0} != {exp0}")
    _require(all(any(sp.simplify(a - b) == 0 for b in gotm) for a in expm),
             f"mu=-2Iw exponents {gotm} != {expm}")

    # M1 mutation: at omega = 0 the sectors collide into a Jordan block
    A0z = A0.subs(w, 0)
    cpz = sp.factor(sp.expand(A0z.charpoly(lam).as_expr()))
    gmz = len(A0z.nullspace())
    _require(sp.simplify(cpz - lam**6) == 0, f"omega=0 charpoly {cpz} != lam^6")
    _require(gmz < 6, "omega=0 unexpectedly diagonalizable")
    out["omega_zero_mutation"] = {"charpoly": sp.sstr(cpz),
                                  "geometric_multiplicity": gmz,
                                  "algebraic_multiplicity": 6}
    return out


# ======================= axial (series reduction) =======================

def axial_indicial(geo_cls):
    v = sp.Symbol("v")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    ph = sp.Symbol("phi")
    w = sp.Symbol("omega", positive=True)
    B0 = 1 - 2 / r
    S_ax = -3 * x * (1 - x**2)

    g_ef = sp.zeros(4, 4)
    g_ef[0, 0] = -B0
    g_ef[0, 1] = g_ef[1, 0] = 1
    g_ef[2, 2] = r**2 / (1 - x**2)
    g_ef[3, 3] = r**2 * (1 - x**2)
    geoE = geo_cls([v, r, x, ph], g_ef)
    giE, GE = geoE.ginv, geoE.Gamma

    h0f, h1f, h2f = [sp.Function(n)(v, r) for n in ("h0", "h1", "h2")]
    hE = sp.zeros(4, 4)
    hE[0, 3] = hE[3, 0] = h0f * S_ax
    hE[1, 3] = hE[3, 1] = h1f * S_ax
    hE[2, 3] = hE[3, 2] = h2f * 3 * (x**2 - 1)
    dG = [[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)]
    for a in range(N):
        for b in range(N):
            for c in range(b, N):
                s = sum(giE[a, d] * (geoE.covd2(hE, b, d, c)
                                     + geoE.covd2(hE, c, b, d)
                                     - geoE.covd2(hE, d, b, c))
                        for d in range(N) if giE[a, d] != 0)
                val = _cancel(s / 2)
                dG[a][b][c] = val
                dG[a][c][b] = val

    def cov_dG(e, a, b, c):
        s = sp.diff(dG[a][b][c], [v, r, x, ph][e])
        for hh in range(N):
            s += GE[a][e][hh] * dG[hh][b][c]
            s -= GE[hh][e][b] * dG[a][hh][c] + GE[hh][e][c] * dG[a][b][hh]
        return s

    angs = {"Rt": S_ax, "Rr": S_ax, "Rx": 3 * (x - 1) * (x + 1)}
    rows = {}
    for (b, d, nm) in ((0, 3, "Rt"), (1, 3, "Rr"), (2, 3, "Rx")):
        val = _cancel(sum(cov_dG(a, a, d, b) - cov_dG(d, a, a, b)
                          for a in range(N)))
        rw = _cancel(val / angs[nm])
        _require(not rw.has(x), f"row {nm} not x-free")
        rows[nm] = rw
    H0, H1, H2 = [sp.Function(n)(r) for n in ("H0", "H1", "H2")]
    E = sp.exp(sp.I * w * v)
    four = {h0f: H0 * E, h1f: H1 * E, h2f: H2 * E}
    rowsF = {nm: sp.expand(_cancel(rows[nm].subs(four).doit() / E))
             for nm in ("Rt", "Rr", "Rx")}

    u = sp.Symbol("u", positive=True)

    def lser(e, kmax=NORD):
        e = _cancel(e)
        if e == 0:
            return {}
        num, den = sp.fraction(e)
        pn = sp.Poly(sp.expand(num), r)
        pd = sp.Poly(sp.expand(den), r)
        nmax = max(mo[0] for mo in pn.monoms())
        dmax = max(mo[0] for mo in pd.monoms())
        nn = [(pn.coeff_monomial(r**(nmax - k)) if nmax - k >= 0 else 0)
              for k in range(kmax + dmax + 2)]
        dd = [(pd.coeff_monomial(r**(dmax - k)) if dmax - k >= 0 else 0)
              for k in range(kmax + dmax + 2)]
        nn = [c if c is not None else sp.Integer(0) for c in nn]
        dd = [c if c is not None else sp.Integer(0) for c in dd]
        inv = [sp.Integer(1) / dd[0]]
        for k in range(1, len(dd)):
            acc = sum(dd[j] * inv[k - j] for j in range(1, k + 1) if j < len(dd))
            inv.append(sp.cancel(-acc / dd[0]))
        shift = -(nmax - dmax)
        out = {}
        for k in range(kmax + 1 + max(0, -shift)):
            c = sp.expand(sum(nn[j] * inv[k - j] for j in range(k + 1)))
            key = k + shift
            if 0 <= key <= kmax:
                out[key] = sp.cancel(c)
            elif key < 0:
                _require(sp.cancel(c) == 0, f"growing term u^{key}")
        return {k: c for k, c in out.items() if c != 0}

    d1 = lambda f: sp.Derivative(f, r)
    d2 = lambda f: sp.Derivative(f, (r, 2))
    atoms = [H0, d1(H0), d2(H0), H1, d1(H1), d2(H1), H2, d1(H2), d2(H2)]
    ROW = {}
    for nm in ("Rt", "Rr", "Rx"):
        M, b = sp.linear_eq_to_matrix([sp.expand(rowsF[nm])], atoms)
        _require(all(sp.simplify(z) == 0 for z in b), f"row {nm} inhomogeneous")
        ROW[nm] = [lser(M[0, j]) for j in range(len(atoms))]

    def clean(d):
        return {k: sp.cancel(vv) for k, vv in d.items()
                if sp.cancel(vv) != 0 and k <= NORD}

    def smul(a, b):
        o = {}
        for ka, va in a.items():
            for kb, vb in b.items():
                k = ka + kb
                if k <= NORD:
                    o[k] = sp.expand(o.get(k, 0) + va * vb)
        return clean(o)

    def sadd(*ds):
        o = {}
        for d in ds:
            for k, vv in d.items():
                o[k] = sp.expand(o.get(k, 0) + vv)
        return clean(o)

    def sscale(d, s):
        return clean({k: vv * s for k, vv in d.items()})

    def sinv(d):
        d0 = d.get(0)
        _require(d0 is not None and sp.cancel(d0) != 0,
                 "series not invertible at u^0")
        inv = {0: sp.cancel(1 / d0)}
        for k in range(1, NORD + 1):
            acc = sum(d.get(j, 0) * inv.get(k - j, 0) for j in range(1, k + 1))
            inv[k] = sp.cancel(-acc / d0)
        return clean(inv)

    def dser(d):
        return clean({k + 1: -k * vv for k, vv in d.items() if k >= 1})

    A_H0, A_H0p, A_H0pp, A_H1, A_H1p, A_H1pp, A_H2, A_H2p, A_H2pp = range(9)
    a_c, e_c = ROW["Rr"][A_H0pp], ROW["Rt"][A_H0pp]
    K = [sadd(smul(e_c, ROW["Rr"][j]), sscale(smul(a_c, ROW["Rt"][j]), -1))
         for j in range(9)]
    _require(not K[A_H0pp], "cascade retains H0''")
    _require(not K[A_H1p] and not K[A_H1pp],
             "cascade not algebraic in H1")
    casc = K[A_H1]
    _require(sp.simplify(casc.get(0) - w**2 / 4) == 0,
             f"cascade leading coefficient {casc.get(0)} != omega^2/4")
    cascade_series = {str(k): sp.sstr(sp.factor(c))
                      for k, c in sorted(casc.items())}

    NB = 6
    IH0, IH0p, IH2, IH2p, IH0pp, IH2pp = range(NB)
    cinv = sinv(casc)
    H1_lf = [dict() for _ in range(NB)]
    for src, dst in ((A_H0, IH0), (A_H0p, IH0p), (A_H2, IH2), (A_H2p, IH2p)):
        if K[src]:
            H1_lf[dst] = smul(sscale(K[src], -1), cinv)

    def lf_d(f):
        out = [dict() for _ in range(NB)]
        for i in range(NB):
            if f[i]:
                out[i] = sadd(out[i], dser(f[i]))
        for i, j in ((IH0, IH0p), (IH0p, IH0pp), (IH2, IH2p), (IH2p, IH2pp)):
            if f[i]:
                out[j] = sadd(out[j], f[i])
        return out

    H1p_lf = lf_d(H1_lf)
    H1pp_lf = lf_d(H1p_lf)

    def row_to_lf(row):
        out = [dict() for _ in range(NB)]
        for a, i in ((A_H0, IH0), (A_H0p, IH0p), (A_H0pp, IH0pp),
                     (A_H2, IH2), (A_H2p, IH2p), (A_H2pp, IH2pp)):
            if row[a]:
                out[i] = sadd(out[i], row[a])
        for a, lf in ((A_H1, H1_lf), (A_H1p, H1p_lf), (A_H1pp, H1pp_lf)):
            if row[a]:
                out = [sadd(out[i], smul(lf[i], row[a])) for i in range(NB)]
        return out

    Rt_lf, Rx_lf = row_to_lf(ROW["Rt"]), row_to_lf(ROW["Rx"])
    det = sadd(smul(Rt_lf[IH0pp], Rx_lf[IH2pp]),
               sscale(smul(Rt_lf[IH2pp], Rx_lf[IH0pp]), -1))
    _require(not det, f"level-2 determinant not identically zero: {det}")

    # RW gauge (H2 = 0): the row whose H0'' coefficient is regular at u^0
    pick = None
    for nm, lf in (("Rt", Rt_lf), ("Rx", Rx_lf)):
        if lf[IH0pp] and 0 in lf[IH0pp]:
            pick = (nm, lf[IH0], lf[IH0p], lf[IH0pp])
            break
    _require(pick is not None, "no RW-gauge row regular at u^0")
    nm, a0, a1, a2 = pick
    a2inv = sinv(a2)
    A2 = [[dict(), {0: sp.Integer(1)}],
          [smul(sscale(a0, -1), a2inv), smul(sscale(a1, -1), a2inv)]]
    A0 = sp.Matrix(2, 2, lambda i, j: sp.cancel(A2[i][j].get(0, sp.Integer(0))))
    A1 = sp.Matrix(2, 2, lambda i, j: sp.cancel(A2[i][j].get(1, sp.Integer(0))))
    cp0 = sp.factor(sp.expand(A0.charpoly(lam).as_expr()))
    _require(sp.simplify(cp0 - lam * (lam + 2 * sp.I * w)) == 0,
             f"axial RW charpoly unexpected: {cp0}")
    sectors = {}
    for mu in (sp.Integer(0), -2 * sp.I * w):
        Em = (A0 - mu * sp.eye(2)).nullspace()
        _require(len(Em) == 1, f"axial sector {mu} multiplicity")
        other = -2 * sp.I * w if mu == 0 else sp.Integer(0)
        M = sp.Matrix.hstack(*(Em + (A0 - other * sp.eye(2)).nullspace()))
        _require(sp.cancel(M.det()) != 0, "axial eigenbasis degenerate")
        Ared = (M.inv() * A1 * M)[:1, :1].applyfunc(sp.cancel)
        sectors[sp.sstr(mu)] = sp.sstr(sp.cancel(Ared[0, 0]))
    return {"rw_charpoly": sp.sstr(cp0), "rw_row": nm,
            "cascade_series": cascade_series,
            "level2_determinant": "identically zero (rank 1)",
            "rw_sectors": sectors}


# ======================= assembly =======================================

def run_analysis(geo_cls) -> dict:
    out = {"stage_seconds": {}}
    t0 = time.time()
    polar = polar_indicial(geo_cls)
    out["stage_seconds"]["polar"] = round(time.time() - t0, 1)
    t0 = time.time()
    axial = axial_indicial(geo_cls)
    out["stage_seconds"]["axial"] = round(time.time() - t0, 1)

    # the frequency symbol carried by the reach pipeline has NO assumptions;
    # reality of omega is a DECLARED hypothesis of this certificate, applied
    # explicitly via w_real below (never assumed silently)
    w = sp.Symbol("omega")
    w_real = sp.Symbol("omega", real=True)
    # resonance structure: within-sector differences are omega-free integers
    within = set()
    for sec, sigs in polar["sectors"].items():
        vals = [sp.sympify(s, locals={"omega": w, "I": sp.I}) for s in sigs]
        for a in vals:
            for b in vals:
                if a != b:
                    d = sp.simplify(a - b)
                    _require(d.is_integer is True or d.is_Integer,
                             f"non-integer within-sector difference {d}")
                    _require(not d.has(w), f"difference depends on omega: {d}")
                    within.add(int(d))
    _require(within == {1, 2, -1, -2}, f"unexpected difference set {within}")

    # cross-sector differences are integral only for imaginary omega
    cross = set()
    loc = {"omega": w, "I": sp.I}
    for a in [sp.sympify(s, locals=loc) for s in polar["sectors"]["0"]]:
        for b in [sp.sympify(s, locals=loc) for s in polar["sectors"][sp.sstr(-2 * sp.I * w)]]:
            cross.add(sp.sstr(sp.simplify(a - b)))
    for s in cross:
        _require("omega" in s, f"cross-sector difference {s} omega-free")

    # Re(sigma) is omega-independent for real omega (omega is declared
    # positive, hence real, so sp.re evaluates the 4 I omega part to 0)
    re_parts = {}
    for sec, sigs in polar["sectors"].items():
        rp = []
        for s in sigs:
            expr = sp.sympify(s, locals={"omega": w, "I": sp.I})
            rv = sp.simplify(sp.re(expr.subs(w, w_real)))
            _require(not rv.free_symbols,
                     f"Re(sigma) not a pure number for real omega: {rv}")
            rp.append(int(rv))
        re_parts[sec] = sorted(rp)
    _require(all(rp == [-3, -2, -1] for rp in re_parts.values()),
             f"Re(sigma) not omega-independent: {re_parts}")

    out["polar"] = polar
    out["axial"] = axial
    out["resonance"] = {
        "within_sector_differences": sorted(within),
        "within_sector_omega_dependent": False,
        "cross_sector_differences": sorted(cross),
        "cross_sector_integral_only_for_imaginary_omega": True,
        "real_parts_by_sector": {k: v for k, v in re_parts.items()},
        "real_parts_omega_independent": True,
    }
    out["exceptional_set"] = {
        "real_frequencies": ["0"],
        "mechanisms": [
            "oscillatory eigenvalue collision: 0 = -2 I omega only at omega = 0",
            "axial cascade leading coefficient omega^2/4 vanishes only at omega = 0",
        ],
        "omega_zero_handled_by": "BH2_OMEGA_ZERO",
    }
    return out


def build_certificate() -> dict:
    res = run_analysis(Geometry)
    return {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "S = alpha * integral sqrt(-g) C_{abcd} C^{abcd}",
            "background_family": "Schwarzschild exterior, m = 1",
            "conformal_frame": "fixed representative g (certified atlas)",
            "generator": "l = 2 asymptotic formal systems, both parities",
            "phase_space": "not constructed here (indicial layer only)",
            "horizon_condition": "not used (this is the infinity endpoint)",
            "infinity_condition": "regular singular point at r = infinity "
                                  "after the oscillatory split",
            "lifecycle": "CLASSIFIED",
        },
        "extends": {
            "certificate": str(JORDAN_CERT.relative_to(ROOT)),
            "certificate_sha256": _sha256(JORDAN_CERT),
            "scope": "lifts the polar mu = -2 omega sector from fixture-only "
                     "to symbolic frequency (that certificate records "
                     "polar_mu2w_symbolic_certified = false) and adds the "
                     "exceptional-frequency determination; supersedes "
                     "nothing",
        },
        "polar": res["polar"],
        "axial": res["axial"],
        "resonance": res["resonance"],
        "exceptional_set": res["exceptional_set"],
        "cross_validation": {
            "leading_sigma0_matches_certified_producer_inputs": True,
            "detail": "the leading exponents -1 (mu = 0) and "
                      "-4 I omega - 1 (mu = -2 omega) are exactly the "
                      "sigma0 values the certified BH2C producers feed to "
                      "column_jets at the fixture",
        },
        "mutations": {
            "M1_omega_zero_jordan": "at omega = 0 the polar leading charpoly "
                                    "collapses to lam^6 with geometric "
                                    "multiplicity "
                                    + str(res["polar"]["omega_zero_mutation"]
                                          ["geometric_multiplicity"])
                                    + " < 6 -- a genuine Jordan degeneration",
            "M2_cascade": "the axial cascade leading coefficient omega^2/4 "
                          "vanishes exactly at omega = 0 and nowhere else",
        },
        "verification_discipline": [
            "closed-form symbolic reduction HANGS at symbolic omega; all "
            "reductions use exact truncated Laurent series in u = 1/r",
            "no floating point and no nsimplify anywhere",
            "semisimplicity checked by explicit nullspace dimension, never "
            "inferred from the characteristic polynomial alone",
            "exponents cross-validated against the sigma0 inputs of the "
            "certified fixture producers",
        ],
        "claim_flags": {
            "polar_symbolic_exponents_certified": True,
            "polar_mu2w_symbolic_certified": True,
            "axial_symbolic_exponents_certified": True,
            "semisimplicity_certified": True,
            "exceptional_set_certified": True,
            "resonance_omega_independence_certified": True,
            "metric_reconstruction_all_orders_certified": False,
            "symbolic_flux_table_certified": False,
            "endpoint_nonselection_theorem_certified": False,
            "general_l_certified": False,
        },
        "missing_objects": [
            "all-orders metric reconstruction maps (successor split)",
            "symbolic-frequency finite-flux power table (successor split); "
            "the omega-independence of Re(sigma) makes a frequency-"
            "independent Einstein selection plausible but it is NOT computed "
            "or claimed here",
            "the assembled endpoint-nonselection theorem (successor split)",
            "general l",
            "Borel/analytic summability of the formal series",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2c_symbolic_indicial.py",
            "reach_path": "black_hole_programme/bh2b_polar_reach.py",
            "reach_sha256": _sha256(HERE / "bh2b_polar_reach.py"),
        },
        "verification_command":
            "python3 black_hole_programme/verify_bh2c_symbolic_indicial.py",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(CERT_PATH))
    args = parser.parse_args()
    cert = build_certificate()
    Path(args.out).write_text(json.dumps(cert, indent=2, sort_keys=True)
                              + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
