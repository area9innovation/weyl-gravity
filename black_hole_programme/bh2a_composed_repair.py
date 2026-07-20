"""Corrected axial composed lift and exact horizon-flux constants.

Fail-closed builder for
`black_hole_programme/certificates/BH2A_COMPOSED_REPAIR.json`.

Verdict: BH2A_COMPOSED_LIFT_CORRECTED_EXACT_CONSTANT_FLUX.

Setting: Schwarzschild m = 1, axial l = 2, EF chart carrier, t-chart
Lee--Wald pairing, fixtures omega in {3/5, 2/7}.

This certificate SUPERSEDES the fixture values and the on-shell
r-independence language of BH2A_CROSS_FLUX (kept as historical record,
append-only).  Three defects in the original composed-mode pipeline are
documented and repaired:

  D1. the sourced first-order reduction differentiated through the
      radial source symbol as if constant (dropped X' term);
  D2. the particular recursion never imposed the n = 0 Frobenius balance
      (Res Y0 = -[N s]_{-1}), starting from Y0 = 0;
  D3. the reduction imposed an incomplete row system: the correct
      composition uses the Bianchi cascade constraint K (algebraic in
      H1) together with the (v, phi) row -- the row the original
      pipeline never imposed.

CORRECTED STRUCTURE (certified here, both fixtures):
  - level-1 cascade: K = e*Rt-row - a*Rr-row is ALGEBRAIC in H1;
  - level-2: the remaining 2x2 block in (H0'', H2'') is EXACTLY rank 1,
    and its null combination K2 = L.b is a PURE SOURCE-COMPATIBILITY
    identity: zero net coefficient on every field, and EXACTLY ZERO on
    the Bianchi-constrained carrier (verified with two independent
    arbitrary field substitutions);
  - hence one second-order equation for (H0, H2) with one function of
    gauge freedom: the lift EXISTS IN REGGE--WHEELER GAUGE (H2 = 0)
    through the correct row combination; the composed particular has
    ZERO n = 0 cokernel obstruction at both fixtures and is log-free;
  - the corrected mode satisfies ALL THREE delta-Ric rows with EXACTLY
    ZERO structured residual through the certified window.

EXACT CONSTANT FLUXES (t-chart sphere-integrated Lee--Wald F^r on
conjugate pairs; series route validated order-by-order against the
independent rational-function route; every window coefficient rho^1..8
EXACTLY ZERO -- true on-shell constancy, replacing the drifting values
of the defective mode):

  omega = 3/5: RW x RW  = 0 exactly (null control);
               RW x X   = -10893744/129625 + 780048 I/25925;
               X  x X   =  284488128 I/648125   (~ +438.9402 I).
  omega = 2/7: RW x RW  = 0 exactly;
               RW x X   = -15606912/844025 + 1283712 I/120575;
               X  x X   =  206883648 I/5908175  (~ +35.0165 I).

SIGN FINDING (frequency-robust): the corrected extra-block values are
POSITIVE-imaginary at both fixtures, the opposite sign from the
superseded fixtures; under the superseded certificate's convention
(i F^r/(pi alpha)) the corrected extra-block pairing is NEGATIVE at the
horizon at both frequencies.  Conventions are pinned by the certified
BH2A_FLUX_MATRIX bilinear and the slot order (mode(+w), conj mode(-w));
no representative-invariant sign theory is claimed.

NOT claimed: symbolic omega dependence, general l or m, the polar
sector, outer-boundary counterparts, any stability statement, or a
representative-invariant sign theory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from pathlib import Path

import sympy as sp

from axial_flux_modes import run_pipeline
from weyl_geometry import Geometry

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2A_COMPOSED_REPAIR.json"
SCHEMA_PATH = HERE / "schema" / "bh2a-composed-repair-v1.schema.json"
OLD_CROSS = HERE / "certificates" / "BH2A_CROSS_FLUX.json"
FLUXMAT = HERE / "certificates" / "BH2A_FLUX_MATRIX.json"

SCHEMA_NAME = "pure-weyl-bh2a-composed-repair-v1"
RESULT_ID = "PURE_WEYL_BH2A_COMPOSED_REPAIR"
RESULT_TOKEN = "BH2A_COMPOSED_LIFT_CORRECTED_EXACT_CONSTANT_FLUX"

EXPECTED = {
    sp.Rational(3, 5): {
        "cross": sp.Rational(-10893744, 129625)
        + sp.Rational(780048, 25925) * sp.I,
        "ee": sp.Rational(284488128, 648125) * sp.I,
    },
    sp.Rational(2, 7): {
        "cross": sp.Rational(-15606912, 844025)
        + sp.Rational(1283712, 120575) * sp.I,
        "ee": sp.Rational(206883648, 5908175) * sp.I,
    },
}


class ComposedRepairError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ComposedRepairError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cancel(e):
    return sp.cancel(sp.together(e))


def run_analysis(geo_cls) -> dict:
    t0_all = time.time()
    out: dict = {"stage_seconds": {}, "fixtures": {}}
    NORD = 16
    KWIN = 8
    r = sp.Symbol("r", positive=True)
    rho = sp.Symbol("rho")
    x = sp.Symbol("x")
    w = sp.Symbol("omega", positive=True)
    t_s, ph, v_ef = sp.symbols("t phi v")
    alpha = sp.Symbol("alpha", positive=True)
    B0 = 1 - 2 / r
    N = 4
    S_ax = -3 * x * (1 - x**2)

    # ---- 3-function dRic rows (EF chart, symbolic omega) --------------------
    t0 = time.time()
    g_ef = sp.zeros(4, 4)
    g_ef[0, 0] = -B0
    g_ef[0, 1] = g_ef[1, 0] = 1
    g_ef[2, 2] = r**2 / (1 - x**2)
    g_ef[3, 3] = r**2 * (1 - x**2)
    geoE = geo_cls([v_ef, r, x, ph], g_ef)
    giE = geoE.ginv
    GE = geoE.Gamma
    h0f, h1f, h2f = [sp.Function(n)(v_ef, r) for n in ("h0", "h1", "h2")]
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
        s = sp.diff(dG[a][b][c], [v_ef, r, x, ph][e])
        for hh in range(N):
            s += GE[a][e][hh] * dG[hh][b][c]
            s -= GE[hh][e][b] * dG[a][hh][c] + GE[hh][e][c] * dG[a][b][hh]
        return s

    rows_sym = {}
    for (b, d, nm, ang) in ((0, 3, "Rt", S_ax), (1, 3, "Rr", S_ax),
                            (2, 3, "Rx", 3 * (x - 1) * (x + 1))):
        val = _cancel(sum(cov_dG(a, a, d, b) - cov_dG(d, a, a, b)
                          for a in range(N)))
        rw = _cancel(val / ang)
        _require(not rw.has(x), f"row {nm} not x-free")
        rows_sym[nm] = rw
    H0, H1, H2 = [sp.Function(n)(r) for n in ("H0", "H1", "H2")]
    E = sp.exp(sp.I * w * v_ef)
    four = {h0f: H0 * E, h1f: H1 * E, h2f: H2 * E}
    rowsF = {nm: sp.expand(_cancel(rows_sym[nm].subs(four).doit() / E))
             for nm in ("Rt", "Rr", "Rx")}
    out["stage_seconds"]["rows"] = round(time.time() - t0, 1)
    print(f"[rows] {out['stage_seconds']['rows']} s", flush=True)

    d1 = lambda f: sp.Derivative(f, r)
    d2f = lambda f: sp.Derivative(f, (r, 2))
    PS, QS, CS = sp.symbols("PSRC QSRC CSRC")
    PSP, QSP, CSP = sp.symbols("PSRCP QSRCP CSRCP")
    srcsyms = [PS, QS, CS, PSP, QSP, CSP]

    def laurent(e, kmax_out):
        e = _cancel(e)
        if e == 0:
            return {}
        num, den = sp.fraction(e)
        pn = sp.Poly(sp.expand(num), rho)
        pd = sp.Poly(sp.expand(den), rho)
        nmin = min(m2[0] for m2 in pn.monoms())
        qmin = min(m2[0] for m2 in pd.monoms())
        lead = nmin - qmin
        depth = kmax_out - lead
        if depth < 0:
            return {}
        dd = [pd.coeff_monomial(rho**(qmin + k)) for k in range(depth + 1)]
        inv = [sp.Integer(1) / dd[0]]
        for k in range(1, depth + 1):
            acc = sum(dd[j] * inv[k - j] for j in range(1, k + 1))
            inv.append(sp.cancel(-acc / dd[0]))
        nn = [pn.coeff_monomial(rho**(nmin + k)) for k in range(depth + 1)]
        return {lead + k: sp.expand(sum(nn[j] * inv[k - j]
                                        for j in range(k + 1)))
                for k in range(depth + 1)}

    for wnum in (sp.Rational(3, 5), sp.Rational(2, 7)):
        wtag = str(wnum)
        fx: dict = {}
        t0 = time.time()
        pipe = run_pipeline(wnum, NORD=NORD, radii=[sp.Rational(65, 32)],
                            return_exprs=True, geo_cls=geo_cls)
        Pp, Qp, Xp = pipe["exprs"]["carrier_p"]
        out["stage_seconds"][f"carrier_{wtag}"] = round(time.time() - t0, 1)
        print(f"[carrier {wtag}] {out['stage_seconds'][f'carrier_{wtag}']} s",
              flush=True)

        # ---- cascades ------------------------------------------------------
        t0 = time.time()
        eqt = sp.expand(rowsF["Rt"].subs(w, wnum)) - PS
        eqr = sp.expand(rowsF["Rr"].subs(w, wnum)) - QS
        eqx = sp.expand(rowsF["Rx"].subs(w, wnum)) - CS
        a1 = _cancel(eqt.coeff(d2f(H0)))
        e1 = _cancel(eqr.coeff(d2f(H0)))
        K = sp.expand(e1 * eqt - a1 * eqr)
        c2 = _cancel(K.coeff(H1))
        _require(c2 != 0, "level-1 cascade: K lacks algebraic H1")
        H1_alg = _cancel(-(sp.expand(K - c2 * H1)) / c2)
        Pf, Qf, Cf = [sp.Function(n)(r) for n in ("Pw", "Qw", "Cw")]
        fsub = {PS: Pf, QS: Qf, CS: Cf}
        bsub = {sp.Derivative(Pf, r): PSP, sp.Derivative(Qf, r): QSP,
                sp.Derivative(Cf, r): CSP, Pf: PS, Qf: QS, Cf: CS}
        H1p_full = sp.diff(H1_alg.subs(fsub), r).doit().subs(bsub)
        subsH1 = {d1(H1): H1p_full, H1: H1_alg}
        et = eqt.subs(subsH1)
        ex_ = eqx.subs(subsH1)
        M2, b2 = sp.linear_eq_to_matrix([sp.expand(et), sp.expand(ex_)],
                                        [d2f(H0), d2f(H2)])
        _require(_cancel(M2.det()) == 0, "level-2 block not rank 1")
        LT = (M2.T).nullspace()
        _require(len(LT) == 1, "level-2 left-null not 1-dim")
        L = LT[0]
        K2 = sp.expand(_cancel(L[0]) * b2[0] + _cancel(L[1]) * b2[1])
        for atom in (H0, H2, d1(H0), d1(H2)):
            _require(_cancel(sp.expand(K2).coeff(atom)) == 0,
                     f"K2 has net field dependence on {atom}")
        # K2 vanishes exactly on the actual carrier, for two independent
        # arbitrary field substitutions
        srcsub = {PS: Pp.subs(rho, r - 2), QS: Qp.subs(rho, r - 2),
                  CS: Xp.subs(rho, r - 2),
                  PSP: sp.diff(Pp, rho).subs(rho, r - 2),
                  QSP: sp.diff(Qp, rho).subs(rho, r - 2),
                  CSP: sp.diff(Xp, rho).subs(rho, r - 2)}
        for f0, f2 in (((r - 2)**2 + 3, (r - 2) + 1),
                       (5 * (r - 2), 7 * (r - 2)**3 - 2)):
            kv = K2.subs(srcsub)
            kv = kv.subs({d1(H0): sp.diff(f0, r), H0: f0,
                          d1(H2): sp.diff(f2, r), H2: f2})
            _require(_cancel(kv.subs(r, 2 + rho)) == 0,
                     "K2 not zero on the Bianchi-constrained carrier")
        out["stage_seconds"][f"cascades_{wtag}"] = round(time.time() - t0, 1)
        print(f"[cascades {wtag}] {out['stage_seconds'][f'cascades_{wtag}']} s",
              flush=True)

        # ---- single ODE in RW gauge (H2 = 0), Frobenius particular ---------
        t0 = time.time()
        z2 = {d2f(H2): 0, d1(H2): 0, H2: 0}
        ode = sp.expand(et.subs(z2))
        cpp = _cancel(ode.coeff(d2f(H0)))
        cp = _cancel(ode.coeff(d1(H0)))
        c0 = _cancel(ode.coeff(H0))
        rest = sp.expand(ode - cpp * d2f(H0) - cp * d1(H0) - c0 * H0)
        leftover = rest
        for sy in srcsyms:
            leftover = leftover - _cancel(rest.coeff(sy)) * sy
        _require(sp.simplify(sp.expand(leftover)) == 0,
                 "single ODE has nonlinear leftover")
        M = sp.Matrix([[0, 1],
                       [_cancel(-c0 / cpp), _cancel(-cp / cpp)]])
        Nv = sp.Matrix(2, 6, lambda i, j: 0 if i == 0 else
                       _cancel(-rest.coeff(srcsyms[j]) / cpp))
        Mr = M.subs(r, 2 + rho)
        Mser = {(i, j): laurent(Mr[i, j], NORD)
                for i in range(2) for j in range(2)}
        _require(not [1 for s2 in Mser.values() if s2 and min(s2) < -1],
                 "M pole excess")
        Res = sp.Matrix(2, 2, lambda i, j: Mser[(i, j)].get(-1, sp.Integer(0)))
        Mk = [sp.Matrix(2, 2, lambda i, j: Mser[(i, j)].get(k, sp.Integer(0)))
              for k in range(NORD + 1)]
        svals = [Pp, Qp, Xp, sp.expand(sp.diff(Pp, rho)),
                 sp.expand(sp.diff(Qp, rho)), sp.expand(sp.diff(Xp, rho))]
        sser = []
        for sv in svals:
            p = sp.Poly(sp.expand(sv), rho)
            sser.append({k: p.coeff_monomial(rho**k)
                         for k in range(p.degree() + 1)})
        NvL = {(i, j): laurent(rho * Nv[i, j].subs(r, 2 + rho), NORD + 2)
               for i in range(2) for j in range(6)}
        _require(not [1 for s2 in NvL.values() if s2 and min(s2) < 0],
                 "source pole excess")
        SC = []
        for k in range(NORD + 1):
            col = sp.zeros(2, 1)
            for i in range(2):
                tot = sp.Integer(0)
                for j in range(6):
                    for ka, va in NvL[(i, j)].items():
                        kb = k - ka
                        if kb in sser[j]:
                            tot += va * sser[j][kb]
                col[i] = sp.expand(tot)
            SC.append(col)
        for L0 in (Res.T).nullspace():
            _require(_cancel(sum(L0[i] * SC[0][i] for i in range(2))) == 0,
                     "n = 0 cokernel obstruction nonzero")
        soln0, params0 = Res.gauss_jordan_solve(-SC[0])
        Y = [soln0.subs({pp: 0 for pp in params0})]
        for n in range(1, NORD + 1):
            rhs = sp.zeros(2, 1)
            for k in range(n):
                rhs += Mk[n - 1 - k] * Y[k]
            rhs += SC[n]
            Mn = n * sp.eye(2) - Res
            _require(Mn.det() != 0, f"unexpected resonance at n={n}")
            Y.append(Mn.solve(rhs))
        H0prof = sum(Y[n][0] * rho**n for n in range(NORD + 1)).subs(rho, r - 2)
        H1e = H1_alg.subs(srcsub).subs(z2)
        subP = {}
        for dd_ in list(H1e.atoms(sp.Derivative)):
            if dd_.args[0] == H0:
                subP[dd_] = sp.diff(H0prof, r, dd_.derivative_count)
        subP[H0] = H0prof
        H1prof = _cancel(H1e.subs(subP).doit())
        # RW homogeneous mode of the same single ODE
        ns0 = Res.nullspace()
        _require(len(ns0) == 1, "RW hom kernel not 1-dim")
        Yh = [sp.Matrix(ns0[0])]
        for n in range(1, NORD + 1):
            rhs = sp.zeros(2, 1)
            for k in range(n):
                rhs += Mk[n - 1 - k] * Yh[k]
            Yh.append((n * sp.eye(2) - Res).solve(rhs))
        H0h = sum(Yh[n][0] * rho**n for n in range(NORD + 1)).subs(rho, r - 2)
        H1eh = H1_alg.subs({s2: 0 for s2 in srcsyms}).subs(z2)
        subPh = {}
        for dd_ in list(H1eh.atoms(sp.Derivative)):
            if dd_.args[0] == H0:
                subPh[dd_] = sp.diff(H0h, r, dd_.derivative_count)
        subPh[H0] = H0h
        H1h = _cancel(H1eh.subs(subPh).doit())
        out["stage_seconds"][f"modes_{wtag}"] = round(time.time() - t0, 1)
        print(f"[modes {wtag}] {out['stage_seconds'][f'modes_{wtag}']} s",
              flush=True)

        # ---- structured 3-row receipt on the composed mode ------------------
        t0 = time.time()
        prof_ser = {"H0": laurent(H0prof.subs(r, 2 + rho), KWIN + 6),
                    "H1": laurent(H1prof.subs(r, 2 + rho), KWIN + 6),
                    "H2": {}}
        sser_rows = {"Rt": laurent(Pp, KWIN + 2), "Rr": laurent(Qp, KWIN + 2),
                     "Rx": laurent(Xp, KWIN + 2)}

        def dser(s2, times=1):
            for _ in range(times):
                s2 = {k - 1: k * v2 for k, v2 in s2.items() if k != 0}
            return s2

        fmap = {"H0": H0, "H1": H1, "H2": H2}
        for nm in ("Rt", "Rr", "Rx"):
            e = sp.expand(rowsF[nm].subs(w, wnum))
            total: dict = {}
            for key, f in fmap.items():
                for dd_ in list(e.atoms(sp.Derivative)):
                    if dd_.args[0] == f:
                        cl = laurent(_cancel(e.coeff(dd_)).subs(r, 2 + rho),
                                     KWIN + 8)
                        fs = dser(dict(prof_ser[key]), dd_.derivative_count)
                        for ka, va in cl.items():
                            for kb, vb in fs.items():
                                k = ka + kb
                                if k <= KWIN:
                                    total[k] = sp.expand(total.get(k, 0)
                                                         + va * vb)
                c = _cancel(e.coeff(f))
                if c != 0:
                    cl = laurent(c.subs(r, 2 + rho), KWIN + 8)
                    for ka, va in cl.items():
                        for kb, vb in prof_ser[key].items():
                            k = ka + kb
                            if k <= KWIN:
                                total[k] = sp.expand(total.get(k, 0) + va * vb)
            for k, v2 in sser_rows[nm].items():
                if k <= KWIN:
                    total[k] = sp.expand(total.get(k, 0) - v2)
            nz = [k for k, v2 in total.items() if sp.expand(v2) != 0]
            _require(not nz, f"row {nm} residual nonzero at orders {nz}")
        out["stage_seconds"][f"row_receipt_{wtag}"] = round(time.time() - t0, 1)
        print(f"[row_receipt {wtag}] "
              f"{out['stage_seconds'][f'row_receipt_{wtag}']} s", flush=True)

        # ---- flux windows (series machinery) --------------------------------
        t0 = time.time()
        loc = {"h0a": sp.Function("h0a"), "h1a": sp.Function("h1a"),
               "h0b": sp.Function("h0b"), "h1b": sp.Function("h1b"),
               "t": t_s, "r": r, "m": sp.Symbol("m"), "alpha": alpha,
               "pi": sp.pi}
        _cert = json.loads(FLUXMAT.read_text())
        Fr2 = sp.sympify(_cert["bilinear"]["F_r"], locals=loc).subs(loc["m"], 1)
        PDEPTH = 20
        invB = laurent(_cancel((1 / B0).subs(r, 2 + rho)), KWIN + 6)

        def smul_cap(a, b, cap):
            o = {}
            for ka, va in a.items():
                for kb, vb in b.items():
                    k = ka + kb
                    if k <= cap:
                        o[k] = sp.expand(o.get(k, 0) + va * vb)
            return o

        def sadd(a, b):
            o = dict(a)
            for k, v2 in b.items():
                o[k] = sp.expand(o.get(k, 0) + v2)
            return o

        def sdiff2(a):
            return {k - 1: k * v2 for k, v2 in a.items() if k != 0}

        def towers(h0ser, h1ser, sign):
            base = [dict(h0ser), sadd(dict(h1ser), smul_cap(invB, h0ser,
                                                            KWIN + 6))]
            PMAX, QMAX = 3, 4
            T = {}
            for i in range(2):
                cur = {0: base[i]}
                for q in range(1, QMAX + 1):
                    cur[q] = sadd(sdiff2(cur[q - 1]),
                                  smul_cap(invB,
                                           {k: sign * sp.I * wnum * v2
                                            for k, v2 in cur[q - 1].items()},
                                           KWIN + 6))
                for p in range(PMAX + 1):
                    for q in range(QMAX + 1):
                        T[(i, p, q)] = {k: (sign * sp.I * wnum) ** p * v2
                                        for k, v2 in cur[q].items()}
            return T

        def pair_window(pa, pb):
            """pa, pb: (h0ser, h1ser) Laurent dicts for slots a and b(+conj)."""
            Ga = towers(pa[0], pa[1], +1)
            pbc = [{k: sp.conjugate(v2) for k, v2 in s2.items()} for s2 in pb]
            Hb = towers(pbc[0], pbc[1], -1)
            name2i = {"h0a": (0, "a"), "h1a": (1, "a"),
                      "h0b": (0, "b"), "h1b": (1, "b")}
            total: dict = {}
            for tm in sp.Add.make_args(sp.expand(Fr2)):
                coeff = sp.Integer(1)
                ga = hb = None
                for fac in sp.Mul.make_args(tm):
                    base, _exp = fac.as_base_exp()
                    if isinstance(base, sp.Derivative) \
                            and base.args[0].func.__name__ in name2i:
                        f = base.args[0]
                        i, slot = name2i[f.func.__name__]
                        p = sum(int(pp2[1]) for pp2 in base.args[1:]
                                if pp2[0] == t_s)
                        q = sum(int(pp2[1]) for pp2 in base.args[1:]
                                if pp2[0] == r)
                        ser = Ga[(i, p, q)] if slot == "a" else Hb[(i, p, q)]
                        if slot == "a":
                            ga = ser
                        else:
                            hb = ser
                    elif isinstance(base, sp.Function) \
                            and base.func.__name__ in name2i:
                        i, slot = name2i[base.func.__name__]
                        ser = Ga[(i, 0, 0)] if slot == "a" else Hb[(i, 0, 0)]
                        if slot == "a":
                            ga = ser
                        else:
                            hb = ser
                    else:
                        coeff *= fac
                _require(ga is not None and hb is not None,
                         "non-bilinear flux term")
                cser = laurent(coeff.subs(r, 2 + rho), KWIN + 8)
                total = sadd(total, smul_cap(cser,
                                             smul_cap(ga, hb, KWIN + 40),
                                             KWIN))
            return total

        pX = (laurent(H0prof.subs(r, 2 + rho), KWIN + 6),
              laurent(H1prof.subs(r, 2 + rho), KWIN + 6))
        pE = (laurent(H0h.subs(r, 2 + rho), KWIN + 6),
              laurent(H1h.subs(r, 2 + rho), KWIN + 6))
        results = {}
        for nm, pa, pb in (("control", pE, pE), ("cross", pE, pX),
                           ("ee", pX, pX)):
            win = pair_window(pa, pb)
            c0v = sp.cancel(sp.expand(win.get(0, 0)) / (sp.pi * alpha))
            for k in range(1, KWIN + 1):
                _require(sp.expand(win.get(k, 0)) == 0,
                         f"{nm} flux not constant at rho^{k}")
            neg = [k for k, v2 in win.items() if k < 0 and sp.expand(v2) != 0]
            _require(not neg, f"{nm} flux singular at horizon: {neg}")
            results[nm] = c0v
        _require(results["control"] == 0, "null control nonzero")
        _require(sp.expand(results["cross"] - EXPECTED[wnum]["cross"]) == 0,
                 "cross value mismatch with banked constant")
        _require(sp.expand(results["ee"] - EXPECTED[wnum]["ee"]) == 0,
                 "ee value mismatch with banked constant")
        _require(sp.re(results["ee"]) == 0 and sp.im(results["ee"]) > 0,
                 "ee not positive-imaginary")
        fx["control"] = "0"
        fx["cross"] = sp.sstr(results["cross"])
        fx["ee"] = sp.sstr(results["ee"])
        fx["cross_float"] = str(complex(sp.N(results["cross"], 10)))
        fx["ee_float"] = str(complex(sp.N(results["ee"], 10)))
        out["fixtures"][wtag] = fx
        out["stage_seconds"][f"flux_{wtag}"] = round(time.time() - t0, 1)
        print(f"[flux {wtag}] {out['stage_seconds'][f'flux_{wtag}']} s",
              flush=True)

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
            "background_family": "Schwarzschild m = 1 fixtures",
            "conformal_frame": "EF-chart carrier; t-chart Lee-Wald pairing with exact e^{i omega rstar} factors",
            "generator": "none; bilinear pairings of ingoing-analytic modes",
            "phase_space": "axial l = 2 conjugate mode pairs at omega in {3/5, 2/7}",
            "horizon_condition": "ingoing analyticity; flux values are the EXACT CONSTANTS of on-shell pairs (rho^1..rho^8 identically zero)",
            "infinity_condition": "none; horizon-local statement",
            "lifecycle": "CLASSIFIED",
        },
        "supersedes": {
            "certificate": str(OLD_CROSS.relative_to(ROOT)),
            "certificate_sha256": _sha256(OLD_CROSS),
            "scope": "the composed-mode fixture values and the on-shell r-independence language of BH2A_CROSS_FLUX (kept as an append-only historical record)",
            "defects": [
                "D1: sourced reduction differentiated through the radial source symbol as constant (dropped X' term)",
                "D2: particular recursion omitted the n = 0 Frobenius balance (started at Y0 = 0)",
                "D3: incomplete row system: the correct composition is the Bianchi-cascade constraint (algebraic H1) plus the (v,phi) row, which the original pipeline never imposed",
            ],
        },
        "structure": {
            "level_1": "K = e*Rt - a*Rr is algebraic in H1 (cascade)",
            "level_2": "the remaining (H0'', H2'') block is exactly rank 1; its null combination K2 = L.b has zero net coefficient on every field and vanishes exactly on the Bianchi-constrained carrier: a pure source-compatibility identity",
            "content": "one second-order equation for (H0, H2) plus one function of gauge freedom; the lift exists in Regge-Wheeler gauge (H2 = 0); n = 0 cokernel exactly zero at both fixtures; particular log-free; all three delta-Ric rows exactly zero through the certified window",
        },
        "fixtures": res["fixtures"],
        "sign_finding": {
            "statement": ("the corrected extra-block constants are "
                          "positive-imaginary at both fixtures (superseded "
                          "values were negative-imaginary): under the "
                          "superseded convention i F^r/(pi alpha) the "
                          "corrected extra-block pairing is NEGATIVE at the "
                          "horizon at both frequencies"),
            "conventions": "pinned by the certified BH2A_FLUX_MATRIX bilinear and slot order (mode(+w), conj mode(-w)); representative-invariant sign theory remains OPEN",
        },
        "verification_discipline": [
            "series flux route validated order-by-order against the independent rational-function route on the superseded mode",
            "structured Laurent receipts only; no global cancel of large substituted trees, no nsimplify on residuals, no bare .coeff extraction on expanded giant trees (each failure mode was observed and is documented in the report)",
        ],
        "claim_flags": {
            "corrected_composition_certified": True,
            "rw_gauge_lift_exists": True,
            "exact_constant_flux_certified": True,
            "null_control_exact": True,
            "sign_flip_documented": True,
            "supersedes_bh2a_cross_flux_values": True,
            "symbolic_omega_certified": False,
            "general_l_certified": False,
            "polar_composed_repair_certified": False,
            "invariant_sign_theory_certified": False,
        },
        "missing_objects": [
            "symbolic omega dependence of the corrected constants",
            "general l, m; the polar composed-repair counterpart",
            "outer-boundary counterparts of the corrected fixtures",
            "a representative-invariant sign theory for the extra block",
            "any stability statement",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2a_composed_repair.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "pipeline_path": "black_hole_programme/axial_flux_modes.py",
            "pipeline_sha256": _sha256(HERE / "axial_flux_modes.py"),
            "flux_matrix_certificate": str(FLUXMAT.relative_to(ROOT)),
            "flux_matrix_certificate_sha256": _sha256(FLUXMAT),
        },
        "verification_command":
            "python3 black_hole_programme/verify_bh2a_composed_repair.py",
    }
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    certificate = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
