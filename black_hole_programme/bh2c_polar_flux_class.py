"""BH-2C stage 4: polar norm-selection table at infinity.

Fail-closed builder for
`black_hole_programme/certificates/BH2C_POLAR_FLUX_CLASS.json`.

Verdict: BH2C_POLAR_NORM_SELECTION_EINSTEIN_SELECTED_AT_INFINITY.

Setting: Schwarzschild m = 1, polar (even-parity) l = 2, EF chart,
omega = 3/5 fixture.  Carrier foundation imported live from the certified
BH2B_POLAR_REACH analysis (bh2b_polar_reach.run_analysis, light mode: every
_require of the reach chain up to the gauge-exponent stage re-runs here).

Exact results:

1. COMPOSED-LIFT CLASSIFICATION: solving delta Ric[h] = psi at r -> infinity
   for each of the three leading carrier formal solutions per sector, with
   depth-12 carrier jets (the derived sources D, Ec, G carry r-weights up to
   4, so source keys are valid only through depth - 4; shallow jets produce
   spurious inconsistencies):
     sector mu = 0:    pure-power and single/double-log ansaetze at the
       naive base ALL FAIL; the lift requires ONE POWER ENHANCEMENT plus a
       single log: class (extra, nlog) = (1, 1), s_base = 1 -- the
       inhomogeneous realization of the rank-1 resonance certified in
       BH2C_ASYMPTOTIC_JORDAN ("at most one power enhancement");
     sector mu = -2w:  pure power, no enhancement, no log: class (0, 0),
       s_base = -12 I/5 (unit modulus: oscillatory, non-growing).
   Parity contrast: the axial composed lifts carry single-log tails in BOTH
   sectors with no enhancement (BH2C_FLUX_CLASS).
   Gauge control: the exact conformal-gauge carrier jet (harmonic Phi)
   classifies as (0, 0) through the same machinery.
2. FLUX POWER TABLE: substituting conjugate pair classes into the EF
   sphere-integrated Lee--Wald slice density F^v:
     Einstein x Einstein: sector 0 identically ZERO in the slice density
       (an extra mu = 0 degeneracy); sector -2w falls as r^-2, exactly the
       axial Einstein behavior: slice norm FINITE in both sectors.  (The
       certified BH2B_POLAR_FLUX statement -- the polar Einstein-branch
       RADIAL flux F^r vanishes identically for conjugate pairs -- is a
       separate exact nullness, not a claim about F^v.)
     Einstein x composed: r^1 (sector 0) and r^3 (sector -2w): DIVERGENT;
     composed x composed: r^2 (sector 0) and r^4 (sector -2w): DIVERGENT;
   for every leading carrier jet (all 3 per sector; all pair combinations).
3. NOISE-FLOOR DISCIPLINE: each certified-nonzero table entry lies strictly
   above the truncation noise floor of its pair.

Consequence: at the fixture mode level the polar finite-slice-norm phase
space at infinity again contains EXACTLY the Einstein sector.  Together
with BH2C_FLUX_CLASS this completes the two-parity norm-selection table of
the planning directive at the fixture level.

NOT claimed: symbolic-frequency table, summability, an asymptotically flat
phase-space construction, charge algebra, general l, the sign/value of any
finite norm, or any stability statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

import bh2b_polar_reach as reach
from linearized_theta import LinearizedTheta
from weyl_geometry import Geometry

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2C_POLAR_FLUX_CLASS.json"
SCHEMA_PATH = HERE / "schema" / "bh2c-polar-flux-class-v1.schema.json"
JORDAN = HERE / "certificates" / "BH2C_ASYMPTOTIC_JORDAN.json"
AXIAL = HERE / "certificates" / "BH2C_FLUX_CLASS.json"
PFLUX = HERE / "certificates" / "BH2B_POLAR_FLUX.json"

SCHEMA_NAME = "pure-weyl-bh2c-polar-flux-class-v1"
RESULT_ID = "PURE_WEYL_BH2C_POLAR_FLUX_CLASS"
RESULT_TOKEN = "BH2C_POLAR_NORM_SELECTION_EINSTEIN_SELECTED_AT_INFINITY"


class PolarFluxClassError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise PolarFluxClassError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cancel(e):
    return sp.cancel(sp.together(e))


def run_analysis(geo_cls) -> dict:
    t0_all = time.time()
    out: dict = {"stage_seconds": {}}
    wnum = sp.Rational(3, 5)
    NI = 4        # staircase window
    CAR_NJ = 12   # carrier jet depth (sources valid through CAR_NJ - 4)
    NIH = 8       # homogeneous h jet depth for the flux table
    SRC_W = 4     # max positive r-weight of the derived sources (angW path)

    # ---- certified carrier foundation (reach, light mode) ------------------
    t0 = time.time()
    R = reach.run_analysis(geo_cls, light=True)
    v = R["syms"]["v"]
    r = R["syms"]["r"]
    m = R["syms"]["m"]
    w = R["syms"]["omega"]
    ar, bcr, ccr, fr = R["funcs4"]
    m1 = {m: sp.Integer(1)}
    wnum_sub = {w: wnum}
    sys3 = [_cancel(e.subs(m1).subs(wnum_sub)) for e in R["sys3"]]
    funcs3 = R["funcs3"]
    D_c = _cancel(R["cascade"]["D"].subs(m1).subs(wnum_sub))
    Ec_c = _cancel(R["cascade"]["Ec"].subs(m1).subs(wnum_sub))
    G_c = _cancel(R["cascade"]["G"].subs(m1).subs(wnum_sub))
    wave = _cancel(R["wave"].subs(m1).subs(wnum_sub))
    phi_f = R["phi_f"]
    B0 = 1 - 2 / r
    out["stage_seconds"]["reach_light"] = round(time.time() - t0, 1)
    print(f"[reach_light] {out['stage_seconds']['reach_light']} s", flush=True)

    # ---- 6-dim first-order carrier system at m = 1, omega = 3/5 ------------
    t0 = time.time()
    d2 = lambda fn: sp.Derivative(fn, (r, 2))
    M2 = sp.Matrix(3, 3, lambda i, j: _cancel(sp.expand(sys3[i]).coeff(d2(funcs3[j]))))
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
    out["stage_seconds"]["carrier_system"] = round(time.time() - t0, 1)
    print(f"[carrier_system] {out['stage_seconds']['carrier_system']} s", flush=True)

    # ---- series helpers ----------------------------------------------------
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

    DEP6 = CAR_NJ + 2
    Bser6 = {(i, j): inv_series_entry(A6[i, j], DEP6)
             for i in range(6) for j in range(6)}
    _require(min([min(s.keys()) for s in Bser6.values() if s] + [0]) >= 0,
             "carrier matrix has growing entries")
    Bk6 = [sp.Matrix(6, 6, lambda i, j: Bser6[(i, j)].get(k, sp.Integer(0)))
           for k in range(DEP6 + 1)]

    # ---- column-parametric jet staircase (shared: carrier and hom) ---------
    t0 = time.time()

    def column_jets(Bk, dim, muv, sig0, depth):
        """Leading (n0 = 0) formal power jets of y' = A y at infinity.

        Kernel parameters are carried as separate exact rational columns and
        left-null consistency conditions are solved per order via a
        nullspace re-parametrization: no symbolic parameters, no global
        nullspace of the stacked jet system (which blows up at this depth).
        """
        B0c = Bk[0] - sp.I * muv * sp.eye(dim)
        Aug = B0c.row_join(sp.eye(dim))
        RA = Aug.rref()[0]
        Rm, Emat = RA[:, :dim], RA[:, dim:]
        zero_rows = [i for i in range(dim)
                     if all(Rm[i, j] == 0 for j in range(dim))]
        pivots = []
        for i in range(dim):
            if i in zero_rows:
                continue
            j = next(j for j in range(dim) if Rm[i, j] != 0)
            pivots.append((i, j))
        kern = B0c.nullspace()
        K = len(kern)
        kmat = sp.Matrix.hstack(*kern) if K else sp.zeros(dim, 0)

        def particular(Rn):
            Er = Emat * Rn
            xp = sp.zeros(dim, Rn.cols)
            for i, j in pivots:
                for c in range(Rn.cols):
                    xp[j, c] = Er[i, c]
            return xp

        Z = [kmat]
        for n in range(0, depth):
            Rn = (sig0 - n) * Z[n]
            for k in range(1, n + 2):
                j = n + 1 - k
                if j < len(Z):
                    Rn -= Bk[k] * Z[j]
            Rn = Rn.applyfunc(_cancel)
            Er = (Emat * Rn).applyfunc(_cancel)
            crows = [Er[i, :] for i in zero_rows
                     if any(Er[i, c] != 0 for c in range(Er.cols))]
            if crows:
                C = sp.Matrix.vstack(*crows)
                Nm = (sp.Matrix.hstack(*C.nullspace())
                      if C.nullspace() else sp.zeros(C.cols, 0))
                Z = [(zz * Nm).applyfunc(_cancel) for zz in Z]
                Rn = (Rn * Nm).applyfunc(_cancel)
            Z.append(particular(Rn).applyfunc(_cancel).row_join(kmat))
            Z = [zz.row_join(sp.zeros(dim, K)) if zz.cols < Z[-1].cols else zz
                 for zz in Z[:-1]] + [Z[-1]]
        Pfin = Z[0].cols
        for n in range(0, depth):
            res = (sig0 - n) * Z[n] - B0c * Z[n + 1]
            for k in range(1, n + 2):
                j = n + 1 - k
                if j < len(Z):
                    res -= Bk[k] * Z[j]
            for i in range(dim):
                for c in range(Pfin):
                    _require(_cancel(res[i, c]) == 0,
                             f"jet residual n={n} row {i} col {c}")
        sols = []
        for c in range(Pfin):
            Y = [[_cancel(Z[n][i, c]) for i in range(dim)]
                 for n in range(depth + 1)]
            n0 = next((n for n in range(len(Y))
                       if any(vv != 0 for vv in Y[n])), None)
            if n0 == 0:
                sols.append(Y)
        return sols

    car = {"0": column_jets(Bk6, 6, sp.Integer(0), sp.Integer(-1), CAR_NJ),
           "-2w": column_jets(Bk6, 6, -2 * wnum, -4 * sp.I * wnum - 1,
                              CAR_NJ)}
    for key, expect in (("0", 3), ("-2w", 3)):
        _require(len(car[key]) == expect,
                 f"sector {key}: {len(car[key])} leading jets != {expect}")
    out["stage_seconds"]["carrier_jets"] = round(time.time() - t0, 1)
    print(f"[carrier_jets] {out['stage_seconds']['carrier_jets']} s", flush=True)

    # ---- sourced polar h-system (delta Ric[h] = psi rows) ------------------
    t0 = time.time()
    x = R["syms"]["x"]
    coords = [v, r, x, sp.Symbol("phi")]
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = geo_cls(coords, g0)
    gi = geo0.ginv
    G = geo0.Gamma
    N = 4
    P2 = (3 * x**2 - 1) / 2
    dP2 = sp.diff(P2, x)
    Wxx = sp.Rational(3, 2)
    E = sp.exp(sp.I * w * v)
    Ah, Bh, Ch, Kh = [sp.Function(n)(r) for n in ("Ah", "Bh", "Ch", "Kh")]
    hp = sp.zeros(4, 4)
    hp[0, 0] = Ah * P2 * E
    hp[0, 1] = hp[1, 0] = Bh * P2 * E
    hp[1, 1] = Ch * P2 * E
    hp[2, 2] = g0[2, 2] * Kh * P2 * E
    hp[3, 3] = g0[3, 3] * Kh * P2 * E
    dG = [[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)]
    for a in range(N):
        for b in range(N):
            for c in range(b, N):
                s = sum(gi[a, d] * (geo0.covd2(hp, b, d, c)
                                    + geo0.covd2(hp, c, b, d)
                                    - geo0.covd2(hp, d, b, c))
                        for d in range(N) if gi[a, d] != 0)
                val = _cancel(s / 2)
                dG[a][b][c] = val
                dG[a][c][b] = val

    def cov_dG(e, a, b, c):
        s = sp.diff(dG[a][b][c], coords[e])
        for hh in range(N):
            s += G[a][e][hh] * dG[hh][b][c]
            s -= G[hh][e][b] * dG[a][hh][c] + G[hh][e][c] * dG[a][b][hh]
        return s

    dRic = sp.zeros(4, 4)
    for b in range(N):
        for d in range(b, N):
            val = _cancel(sum(cov_dG(a, a, b, d) - cov_dG(d, a, b, a)
                              for a in range(N)))
            dRic[b, d] = val
            dRic[d, b] = val
    x0, x1 = sp.Integer(0), sp.Rational(1, 2)

    def strip(raw, ang, xa, xb):
        e0_ = _cancel(raw.subs(x, xa).doit() / E) / ang.subs(x, xa)
        chk = _cancel(raw.subs(x, xb).doit() / E - e0_ * ang.subs(x, xb))
        _require(chk == 0, "strip inconsistent")
        return _cancel(e0_)

    hrow = {}
    hrow["vx"] = strip(dRic[0, 2], dP2, x1, sp.Rational(1, 3))
    hrow["rx"] = strip(dRic[1, 2], dP2, x1, sp.Rational(1, 3))
    hrow["rr"] = strip(dRic[1, 1], P2, x0, x1)
    raw = dRic[2, 2] / E
    Msv = sp.Matrix([[g0[2, 2].subs(x, x0) * P2.subs(x, x0), Wxx],
                     [g0[2, 2].subs(x, x1) * P2.subs(x, x1), Wxx]])
    solv = Msv.solve(sp.Matrix([_cancel(raw.subs(x, x0).doit()),
                                _cancel(raw.subs(x, x1).doit())]))
    hrow["angW"] = _cancel(solv[1])
    # sourced relations: delta Ric[h] rows = carrier source components
    s_fun = {nm: sp.Function("s_" + nm)(r)
             for nm in ("rr", "vx", "rx", "angW")}
    Bc_sol = sp.solve(sp.Eq(hrow["angW"], s_fun["angW"]), Bh)
    _require(len(Bc_sol) == 1, "Bc not solvable")
    Bc_e = _cancel(Bc_sol[0])
    subB = {sp.Derivative(Bh, (r, 2)): sp.diff(Bc_e, r, 2).doit(),
            sp.Derivative(Bh, r): sp.diff(Bc_e, r).doit(), Bh: Bc_e}
    d1 = lambda fn: sp.Derivative(fn, r)
    R2 = {nm: _cancel(hrow[nm].subs(subB).doit()) for nm in ("vx", "rx", "rr")}
    Ap = _cancel(sp.solve(sp.Eq(R2["vx"], s_fun["vx"]), d1(Ah))[0])
    Kp = _cancel(sp.solve(sp.Eq(R2["rx"], s_fun["rx"]), d1(Kh))[0])
    rr1 = R2["rr"].subs({sp.Derivative(Kh, (r, 2)): sp.diff(Kp, r).doit(),
                         d1(Kh): Kp}).doit()
    rr1 = _cancel(rr1.subs(d1(Ah), Ap).doit())
    C2 = _cancel(sp.solve(sp.Eq(rr1, s_fun["rr"]), sp.Derivative(Ch, (r, 2)))[0])
    Ap, Kp, C2, Bc_e = [e.subs(wnum_sub) for e in (Ap, Kp, C2, Bc_e)]
    state = [Ah, Ch, d1(Ch), Kh]
    Mh = sp.zeros(4, 4)
    Mh[1, 2] = 1
    hom_parts = {}
    zero_src = {}
    for sf in s_fun.values():
        for k in (2, 1):
            zero_src[sp.Derivative(sf, (r, k))] = sp.Integer(0)
        zero_src[sf] = sp.Integer(0)
    for i, expr in ((0, Ap), (2, C2), (3, Kp)):
        e = sp.expand(expr.subs(zero_src))
        hom_parts[i] = e
        for j, st in enumerate(state):
            Mh[i, j] = _cancel(e.coeff(st))
    DEP4 = NIH + 6
    Bser4 = {(i, j): inv_series_entry(Mh[i, j], DEP4)
             for i in range(4) for j in range(4)}
    _require(min([min(s.keys()) for s in Bser4.values() if s] + [0]) >= 0,
             "h-system matrix has growing entries")
    Bk4 = [sp.Matrix(4, 4, lambda i, j: Bser4[(i, j)].get(k, sp.Integer(0)))
           for k in range(DEP4 + 1)]
    lam = sp.Symbol("lam")
    _require(sp.factor((Bk4[0]).charpoly(lam).as_expr())
             == lam**3 * (5 * lam + 6 * sp.I) / 5,
             "h leading matrix charpoly unexpected")
    out["stage_seconds"]["h_system"] = round(time.time() - t0, 1)
    print(f"[h_system] {out['stage_seconds']['h_system']} s", flush=True)

    # ---- carrier sources for the lift --------------------------------------
    DEP_SRC = CAR_NJ - SRC_W  # validity bound for derived-source keys
    B0ser = inv_series_entry(B0, DEP_SRC)
    u_inv = sp.Symbol("u_inv")
    sig0s = sp.Symbol("sig0_")

    def carrier_sources(Y, muv, sig_top):
        aser = [Y[n][0] for n in range(len(Y))]
        bser = [Y[n][2] for n in range(len(Y))]
        cser = [Y[n][4] for n in range(len(Y))]
        fser = {}
        for k, ak in enumerate(bser):
            fser[k] = sp.expand(fser.get(k, 0) - ak)
        for kb, vb in B0ser.items():
            for k, ck in enumerate(cser):
                if kb + k <= DEP_SRC:
                    fser[kb + k] = sp.expand(fser.get(kb + k, 0) - vb * ck / 2)

        def rsub(expr):
            AA = sum(aser[k] * u_inv**k for k in range(len(aser)))
            BB = sum(bser[k] * u_inv**k for k in range(len(bser)))
            CC = sum(cser[k] * u_inv**k for k in range(len(cser)))
            FF = sum(fser.get(k, 0) * u_inv**k for k in range(DEP_SRC + 1))
            vals = {ar: AA, bcr: BB, ccr: CC, fr: FF}
            subm = {}
            for fn, VV in vals.items():
                val = sp.exp(sp.I * muv * r) * r**sig0s * VV.subs(u_inv, 1 / r)
                for d in list(expr.atoms(sp.Derivative)):
                    if d.args[0] == fn:
                        subm[d] = sp.diff(val, r, d.derivative_count)
                subm[fn] = val
            e = expr.subs(subm).doit()
            e = sp.powsimp(sp.expand(e / (sp.exp(sp.I * muv * r) * r**sig0s)),
                           force=True)
            e = e.subs(sig0s, sig_top)
            return inv_series_entry(_cancel(e), DEP_SRC)

        return {"rr": {k: cser[k] for k in range(len(cser))},
                "vx": rsub(D_c), "rx": rsub(Ec_c), "angW": rsub(G_c)}

    def source_rows(src, muv, sig_top):
        smap = {}
        for nm, sf in s_fun.items():
            pol = sum(src[nm].get(k, 0) * u_inv**k for k in range(DEP_SRC + 1))
            val = sp.exp(sp.I * muv * r) * r**sig0s * pol.subs(u_inv, 1 / r)
            for e in (Ap, Kp, C2):
                for d in e.atoms(sp.Derivative):
                    if d.args[0] == sf:
                        smap[d] = sp.diff(val, r, d.derivative_count)
            smap[sf] = val
        rows_ = []
        for i, e in enumerate((Ap, None, C2, Kp)):
            if i == 1:
                rows_.append({})
                continue
            e2 = e.subs(smap).doit()
            zmap = {}
            for fn in (Ah, Ch, Kh):
                for d in list(e2.atoms(sp.Derivative)):
                    if d.args[0] == fn:
                        zmap[d] = 0
                zmap[fn] = 0
            e2 = e2.subs(zmap).doit()
            e2 = sp.powsimp(sp.expand(e2 / (sp.exp(sp.I * muv * r) * r**sig0s)),
                            force=True)
            e2 = e2.subs(sig0s, sig_top)
            rows_.append(inv_series_entry(_cancel(e2), DEP_SRC))
        return rows_

    # ---- enhanced staircase -------------------------------------------------
    def staircase_en(srows, muv, sig_top, nlog, extra):
        B0c = Bk4[0] - sp.I * muv * sp.eye(4)
        kmin = min([min(sr.keys()) for sr in srows if sr] + [0])
        S = 1 - kmin
        s_base = sig_top + S + extra
        njet = NI + extra
        _require(njet + 1 - S - extra <= DEP_SRC,
                 "staircase would read source keys beyond validity")
        tags = [f"t{li}" for li in range(nlog + 1)]

        def vv_(tg, n):
            return sp.Matrix(4, 1, lambda i, _: sp.Symbol(f"{tg}_{n}_{i}"))

        unk = [sp.Symbol(f"{tg}_{n}_{i}") for tg in tags
               for n in range(njet + 1) for i in range(4)]
        eqs = []
        for n in range(-1, njet):
            for li, tg in enumerate(tags):
                if 0 <= n <= njet:
                    lhs = (s_base - n) * vv_(tg, n)
                    if li + 1 <= nlog:
                        lhs = lhs + (li + 1) * vv_(tags[li + 1], n)
                else:
                    lhs = sp.zeros(4, 1)
                rhs = sp.zeros(4, 1)
                for k in range(0, n + 2):
                    j = n + 1 - k
                    if 0 <= j <= njet:
                        Bkk = B0c if k == 0 else Bk4[k]
                        rhs += Bkk * vv_(tg, j)
                sv = (sp.Matrix(4, 1, lambda i, _:
                                srows[i].get(n + 1 - S - extra, sp.Integer(0))
                                if srows[i] else sp.Integer(0))
                      if li == 0 else sp.zeros(4, 1))
                d_ = (lhs - rhs - sv) if 0 <= n <= njet else -(rhs + sv)
                eqs.extend(sp.expand(d_[i]) for i in range(4))
        Ml, bl = sp.linear_eq_to_matrix(eqs, unk)
        try:
            soln, params = Ml.gauss_jordan_solve(bl)
            soln = soln.subs({pp: 0 for pp in params})
        except ValueError:
            return None
        nj1 = njet + 1
        packs = []
        for li in range(nlog + 1):
            packs.append([sp.Matrix(4, 1, lambda i, _:
                                    soln[4 * nj1 * li + 4 * n + i])
                          for n in range(nj1)])
        return (s_base, packs)

    # ---- gauge control ------------------------------------------------------
    t0 = time.time()
    NPHI = CAR_NJ + 4
    c2w = sp.expand(wave).coeff(sp.Derivative(phi_f, (r, 2)))
    c1w = sp.expand(wave).coeff(sp.Derivative(phi_f, r))
    c0w = _cancel((wave - c2w * sp.Derivative(phi_f, (r, 2))
                   - c1w * sp.Derivative(phi_f, r)) / phi_f)
    uco = [sp.Integer(1)]
    un = sp.Symbol("un")
    for n in range(1, NPHI + 1):
        trial = sum(uco[k] * r**(-1 - k) for k in range(n)) + un * r**(-1 - n)
        e = c2w * sp.diff(trial, r, 2) + c1w * sp.diff(trial, r) + c0w * trial
        num, _den = sp.fraction(_cancel(e))
        pn = sp.Poly(sp.expand(num * r**(n + 6)), r)
        sol = None
        for mono in sorted(pn.monoms(), reverse=True):
            cc_ = pn.coeff_monomial(r**mono[0])
            if cc_.has(un):
                sol = sp.solve(sp.Eq(cc_, 0), un)
                break
        _require(sol is not None and len(sol) == 1, f"phi recurrence fails at {n}")
        uco.append(_cancel(sol[0]))
    phi_ser = sum(uco[k] * r**(-1 - k) for k in range(NPHI + 1))
    comp_conf = {kq: _cancel(ee.subs(m1).subs(wnum_sub))
                 for kq, ee in R["comp_conf"].items()}
    gc = {}
    for nm in ("a", "bc", "cc"):
        e = comp_conf[nm]
        subm = {d: sp.diff(phi_ser, r, d.derivative_count)
                for d in e.atoms(sp.Derivative) if d.args[0] == phi_f}
        subm[phi_f] = phi_ser
        gc[nm] = _cancel(e.subs(subm).doit())
    zst = [gc["a"], sp.diff(gc["a"], r), gc["bc"], sp.diff(gc["bc"], r),
           gc["cc"], sp.diff(gc["cc"], r)]
    state_ser = [inv_series_entry(zz, CAR_NJ + 4) for zz in zst]
    gjet = [[state_ser[i].get(1 + n, sp.Integer(0)) for i in range(6)]
            for n in range(CAR_NJ + 1)]
    src_g = carrier_sources(gjet, sp.Integer(0), sp.Integer(-1))
    srows_g = source_rows(src_g, sp.Integer(0), sp.Integer(-1))
    _require(staircase_en(srows_g, sp.Integer(0), sp.Integer(-1), 0, 0)
             is not None, "gauge control: pure-power lift inconsistent")
    out["stage_seconds"]["gauge_control"] = round(time.time() - t0, 1)
    print(f"[gauge_control] {out['stage_seconds']['gauge_control']} s", flush=True)

    # ---- per-jet composed classification -----------------------------------
    t0 = time.time()
    composed = {}
    for key, muv, sig_top, want in (
            ("0", sp.Integer(0), sp.Integer(-1), (1, 1)),
            ("-2w", -2 * wnum, -4 * sp.I * wnum - 1, (0, 0))):
        sector = []
        for jn, Y in enumerate(car[key]):
            src = carrier_sources(Y, muv, sig_top)
            srows = source_rows(src, muv, sig_top)
            found = None
            for extra in (0, 1):
                for nlog in (0, 1, 2):
                    res = staircase_en(srows, muv, sig_top, nlog, extra)
                    if res is not None:
                        found = (extra, nlog, res)
                        break
                if found:
                    break
            _require(found is not None,
                     f"sector {key} jet {jn}: no (extra<=1, nlog<=2) class")
            extra, nlog, (s_base, packs) = found
            _require((extra, nlog) == want,
                     f"sector {key} jet {jn}: class ({extra},{nlog}) != {want}")
            if nlog > 0:
                _require(any(any(packs[-1][n][i, 0] != 0 for i in range(4))
                             for n in range(len(packs[-1]))),
                         f"sector {key} jet {jn}: top log part vanished")
            if extra > 0:
                _require(any(packs[li][0][i, 0] != 0 for li in range(nlog + 1)
                             for i in range(4)),
                         f"sector {key} jet {jn}: enhanced top slot vanished")
            sector.append({"jet": jn, "extra": extra, "nlog": nlog,
                           "s_base": s_base, "packs": packs, "src": src})
        composed[key] = (muv, sig_top, sector)
        print(f"[classify {key}] all jets ({want[0]},{want[1]})", flush=True)
    out["classes"] = {key: [(e["extra"], e["nlog"], sp.sstr(e["s_base"]))
                            for e in composed[key][2]] for key in composed}
    out["stage_seconds"]["classification"] = round(time.time() - t0, 1)
    print(f"[classification] {out['stage_seconds']['classification']} s", flush=True)

    # ---- homogeneous h jets (depth NIH, same column scheme) ----------------
    # true leading exponents are 1 and -4 I w + 1 (the shallow global-null
    # construction at sigma_0 = 2 returned the same solutions with a zero
    # top coefficient)
    t0 = time.time()
    hom = {"0": column_jets(Bk4, 4, sp.Integer(0), sp.Integer(1), NIH),
           "-2w": column_jets(Bk4, 4, -2 * wnum, -4 * sp.I * wnum + 1, NIH)}
    for key in hom:
        _require(len(hom[key]) == 1, f"hom sector {key}: {len(hom[key])} != 1")
    out["stage_seconds"]["hom"] = round(time.time() - t0, 1)
    print(f"[hom] {out['stage_seconds']['hom']} s", flush=True)

    # ---- EF polar flux bilinear --------------------------------------------
    t0 = time.time()
    alpha = sp.Symbol("alpha", positive=True)
    lt = LinearizedTheta(geo0, alpha)

    def polar_h(tag):
        fA, fB, fC, fK = [sp.Function(n + tag)(v, r)
                          for n in ("A", "Bc", "Cc", "K")]
        h = sp.zeros(4, 4)
        h[0, 0] = fA * P2
        h[0, 1] = h[1, 0] = fB * P2
        h[1, 1] = fC * P2
        h[2, 2] = g0[2, 2] * fK * P2
        h[3, 3] = g0[3, 3] * fK * P2
        return h, (fA, fB, fC, fK)

    hA, fA4 = polar_h("a")
    hB, fB4 = polar_h("b")
    wab = lt.omega(hA, hB)
    _require(wab[3] == 0, "phi component of omega nonzero")
    ph_s = coords[3]
    Fv = _cancel(sp.integrate(sp.integrate(wab[0] * r**2, (x, -1, 1)),
                              (ph_s, 0, 2 * sp.pi)))
    _require(Fv != 0, "Fv unexpectedly zero")
    out["stage_seconds"]["Fv"] = round(time.time() - t0, 1)
    print(f"[Fv] {out['stage_seconds']['Fv']} s", flush=True)

    # ---- profiles and flux table -------------------------------------------
    t0 = time.time()
    Lg = sp.Symbol("Lg", positive=True)
    sangW_only = {}
    for nm, sf in s_fun.items():
        if nm == "angW":
            continue
        for k in (2, 1):
            sangW_only[sp.Derivative(sf, (r, k))] = sp.Integer(0)
        sangW_only[sf] = sp.Integer(0)
    Bc_e0 = _cancel(Bc_e.subs(sangW_only))

    def bc_from(Cc_expr, sangW_expr):
        subm = {}
        sfW = s_fun["angW"]
        for d in list(Bc_e0.atoms(sp.Derivative)):
            if d.args[0] == Ch:
                subm[d] = sp.diff(Cc_expr, r, d.derivative_count)
            elif d.args[0] == sfW:
                subm[d] = sp.diff(sangW_expr, r, d.derivative_count)
        subm[Ch] = Cc_expr
        subm[sfW] = sangW_expr
        return _cancel(Bc_e0.subs(subm).doit())

    def hom_profile(Yj, muv, sig0):
        Ae = sum(Yj[n][0] * r**(sig0 - n) for n in range(len(Yj)))
        Cce = sum(Yj[n][1] * r**(sig0 - n) for n in range(len(Yj)))
        Ke = sum(Yj[n][3] * r**(sig0 - n) for n in range(len(Yj)))
        ph_ = sp.exp(sp.I * muv * r)
        return (Ae * ph_, bc_from(Cce, sp.Integer(0)) * ph_,
                Cce * ph_, Ke * ph_)

    def comp_profile(key, entry):
        muv, sig_top, _sector = composed[key]
        s_base = entry["s_base"]
        packs = entry["packs"]

        def fld(i):
            e = sp.Integer(0)
            for li, P in enumerate(packs):
                e += sp.log(r)**li * sum(P[n][i, 0] * r**(s_base - n)
                                         for n in range(len(P)))
            return e

        Ae, Cce, Ke = fld(0), fld(1), fld(3)
        sw = entry["src"]["angW"]
        sangW = sum(cs * r**(sig_top - k) for k, cs in sw.items())
        ph_ = sp.exp(sp.I * muv * r)
        return (Ae * ph_, bc_from(Cce, sangW) * ph_, Cce * ph_, Ke * ph_)

    profiles = {"E0": hom_profile(hom["0"][0], sp.Integer(0), sp.Integer(1)),
                "E2": hom_profile(hom["-2w"][0], -2 * wnum,
                                  -4 * sp.I * wnum + 1)}
    for key, tag in (("0", "0"), ("-2w", "2")):
        for entry in composed[key][2]:
            profiles[f"X{tag}j{entry['jet']}"] = comp_profile(key, entry)

    def leading_power(expr):
        e = sp.expand(expr.subs(sp.log(r), Lg))
        e = _cancel(e)
        if e == 0:
            return None
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
        pa = profiles[na]
        pb = profiles[nb]
        EA = sp.exp(sp.I * wnum * v)
        EB = sp.exp(-sp.I * wnum * v)
        reps = {}
        for i, (fa, fb) in enumerate(zip(fA4, fB4)):
            reps[fa] = pa[i].rewrite(sp.exp) * EA
            reps[fb] = (sp.conjugate(pb[i]).subs(sp.conjugate(r), r)
                        .subs(sp.conjugate(sp.log(r)), sp.log(r))
                        .rewrite(sp.exp) * EB)
        sub = {}
        for f, val in reps.items():
            for d in list(Fv.atoms(sp.Derivative)):
                if d.args[0] == f:
                    dt = sum(int(p[1]) for p in d.args[1:] if p[0] == v)
                    dr = sum(int(p[1]) for p in d.args[1:] if p[0] == r)
                    sub[d] = sp.diff(val, v, dt, r, dr)
            sub[f] = val
        e = Fv.subs(sub).doit()
        e = sp.powsimp(sp.expand(e), force=True)
        return leading_power(e)

    # truncation noise floors: Re(s_a) - depth_a + Re(s_b) + W_F, W_F = 0
    floors = {}
    reS = {"E0": (1, NIH), "E2": (1, NIH)}
    for key, tag in (("0", "0"), ("-2w", "2")):
        for entry in composed[key][2]:
            sb = entry["s_base"]
            reS[f"X{tag}j{entry['jet']}"] = (sp.re(sb), NI + entry["extra"])

    def floor_of(na, nb):
        sa, da = reS[na]
        sb, db = reS[nb]
        return max(sa - da - 1 + sb, sb - db - 1 + sa)

    xnames = {"0": [f"X0j{e['jet']}" for e in composed["0"][2]],
              "2": [f"X2j{e['jet']}" for e in composed["-2w"][2]]}
    pairs = []
    for tag in ("0", "2"):
        En = f"E{tag}"
        pairs.append((En, En))
        for xn in xnames[tag]:
            pairs.append((En, xn))
        for i2, xn in enumerate(xnames[tag]):
            for xm in xnames[tag][i2:]:
                pairs.append((xn, xm))
    table = {}
    for na, nb in pairs:
        lp = flux_pair(na, nb)
        fl = floor_of(na, nb)
        table[f"{na}|{nb}"] = {
            "leading": [str(lp[0]), int(lp[1])] if lp else None,
            "noise_floor": str(fl),
        }
        print(f"[pair {na}|{nb}] {table[f'{na}|{nb}']}", flush=True)
    # semantics: Einstein pairs slice-integrable (<= r^-2); the rest divergent
    for tag in ("0", "2"):
        ee = table[f"E{tag}|E{tag}"]
        _require(ee["leading"] is None
                 or sp.Rational(ee["leading"][0]) <= -2,
                 f"E{tag}|E{tag} not slice-integrable")
        for kk, entry in table.items():
            if not kk.startswith(f"E{tag}|E") and kk.count(f"X{tag}") >= 1:
                _require(entry["leading"] is not None
                         and sp.Rational(entry["leading"][0])
                         > sp.Rational(entry["noise_floor"]),
                         f"{kk} not certified above noise floor")
                _require(sp.Rational(entry["leading"][0]) >= 1,
                         f"{kk} unexpectedly integrable")
    out["table"] = table
    out["stage_seconds"]["flux_table"] = round(time.time() - t0, 1)
    print(f"[flux_table] {out['stage_seconds']['flux_table']} s", flush=True)

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
            "conformal_frame": "working gauge; ingoing EF chart; traceless carrier slice",
            "generator": "none; asymptotic slice-norm classification",
            "phase_space": "EF sphere-integrated Lee-Wald slice density F^v on formal pair classes",
            "horizon_condition": "none; infinity-local statement",
            "infinity_condition": "leading (r-power, log-power) of F^v per class with truncation noise floors",
            "lifecycle": "CLASSIFIED",
        },
        "composed_classes": {
            "statement": ("polar composed lift classes (extra power, log degree) "
                          "per leading carrier jet: sector mu=0 all (1,1) at "
                          "s_base=1 (one power enhancement + single log; the "
                          "inhomogeneous realization of the certified rank-1 "
                          "resonance); sector mu=-2w all (0,0) at s_base=-12I/5 "
                          "(pure oscillatory power)"),
            "classes": res["classes"],
            "gauge_control": "exact conformal-gauge jet classifies (0,0) pure-power",
            "parity_contrast": ("axial composed lifts are single-log in both "
                                "sectors with no enhancement (BH2C_FLUX_CLASS)"),
        },
        "flux_table": res["table"],
        "einstein_finiteness": {
            "statement": ("the mu = 0 Einstein pair is identically zero in the "
                          "slice density F^v (an extra degeneracy of that "
                          "sector) and the mu = -2w Einstein pair falls as "
                          "r^-2, exactly the axial Einstein behavior: the "
                          "Einstein slice norm is finite in both sectors; the "
                          "certified polar Einstein-branch radial-flux "
                          "nullness for conjugate pairs (BH2B_POLAR_FLUX) is "
                          "a separate exact statement about F^r, not F^v"),
            "source_certificate": "BH2B_POLAR_FLUX",
        },
        "headline": {
            "statement": ("polar finite-slice-norm asymptotic phase space at "
                          "infinity = exactly the Einstein sector (whose "
                          "mu = 0 self-pair is identically zero in the slice "
                          "density); every extra-branch pair diverges as "
                          "r^1..r^4; two-parity norm selection now complete at "
                          "the fixture level"),
            "complement": ("the horizon endpoint diagnostics do not exclude the "
                           "extra branch (certified dispositions); at infinity, "
                           "symplectic-norm finiteness DOES select the Einstein "
                           "sector in both parities -- a phase-space "
                           "normalization, not a local boundary condition"),
        },
        "claim_flags": {
            "polar_composed_classes_certified": True,
            "polar_power_enhancement_certified": True,
            "polar_flux_power_table_certified": True,
            "polar_einstein_finite_class_certified": True,
            "polar_extra_divergent_class_certified": True,
            "symbolic_frequency_certified": False,
            "summability_certified": False,
            "asymptotic_phase_space_constructed": False,
            "general_l_certified": False,
            "norm_sign_certified": False,
        },
        "carrier_depths": {
            "carrier_jets": 12,
            "source_validity_keys": 8,
            "derived_source_max_weight": 4,
            "staircase_window": 4,
            "hom_depth": 8,
        },
        "missing_objects": [
            "symbolic-frequency table (omega = 3/5 fixture only)",
            "Borel/analytic summability of the enhanced/log series",
            "an asymptotically flat phase-space and charge-algebra construction",
            "general l",
            "sign or value of any finite norm",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2c_polar_flux_class.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "reach_generator_path": "black_hole_programme/bh2b_polar_reach.py",
            "reach_generator_sha256": _sha256(HERE / "bh2b_polar_reach.py"),
            "jordan_certificate": str(JORDAN.relative_to(ROOT)),
            "jordan_certificate_sha256": _sha256(JORDAN),
            "axial_flux_class_certificate": str(AXIAL.relative_to(ROOT)),
            "axial_flux_class_certificate_sha256": _sha256(AXIAL),
            "polar_flux_certificate": str(PFLUX.relative_to(ROOT)),
            "polar_flux_certificate_sha256": _sha256(PFLUX),
        },
        "verification_command":
            "python3 black_hole_programme/verify_bh2c_polar_flux_class.py",
    }
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    cert = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
