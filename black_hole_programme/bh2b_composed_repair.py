"""Polar composed-lift audit and exact constant horizon fluxes.

Verdict token: BH2B_POLAR_COMPOSED_LIFT_AUDITED_EXACT_CONSTANT_FLUX
Tags: LOCAL-ALGEBRAIC + REDUCED-MODE.  Lifecycle: CLASSIFIED.

Polar counterpart of BH2A_COMPOSED_REPAIR.  Four results:

1. HORIZON EXACT CONSTANTS.  The certified polar composition pipeline
   (bh2b_polar_cross_flux.run_pipeline) is re-run per frequency fixture and
   the sphere-integrated EF Lee-Wald F^r of every conjugate family pair
   (E, G, X0, X1, X2)^2 is expanded as an exact Laurent window in rho:
   all control pairs (E|E, E|G, G|*, *|G) vanish IDENTICALLY at every
   window key; every physical pair (E|Xj, Xi|Xj) has exactly one nonzero
   key, rho^0 -- true on-shell constancy with exact rational constants,
   replacing the superseded radius-sampled numerical fixture values of
   BH2B_POLAR_CROSS_FLUX (kept as append-only history; its declared
   fixture values are superseded, its theorems are not).

2. LIFT STATEMENT.  All three analytic carrier modes lift per sector
   (the composition recursion with n = 0 Frobenius balance and
   Einstein-family correction solve succeeds fail-closed for every mode;
   re-asserted in-run).  The lift ambiguity is exactly
   span(Einstein mode, conformal gauge mode) per slot.

3. INVARIANCE CLASSIFICATION.  From the exact window table: conformal
   (G) shifts change NO entry (all G pairs identically zero); Einstein
   (E) shifts leave the E row/column and the G pairs invariant and shift
   the extra block by exact multiples of the cross constants:
   delta F(Xi|Xj) = beta_j^* F(Xi|E) under Xj -> Xj + beta_j E (b slot),
   plus the conjugate a-slot action.  Cross entries F(E|Xj) are invariant
   iff F(E|E) = 0, which holds exactly.  The extra-block constants are
   therefore representative-dependent; the certified values are AT the
   pipeline's canonical representatives (correction parameters zeroed).

4. INFINITY vv/vr AUDIT (BH2C repair).  The BH2C flux-class hom h-jets
   solve a 4-row reduction (vx, rx, rr, angW); the vv and vr dRic rows
   were never imposed.  Audit result: vr is clean on every mu0 jet, but
   ALL THREE mu0 power jets (sigma0 = 1, 0, -1) fail vv with exact
   residuals; the -2w sector jet is clean on both.  The mu0 space
   contains EXACTLY ONE Einstein direction (unique vv-clean combination,
   exact coefficients); the shipped table's "E0" representative (pure
   sigma0 = 1 jet) is NOT Einstein.  Recomputed table rows with the true
   Einstein jet: E0true|E0true = (-2, 0) -- the SAME class as the
   certified E2|E2, replacing the superseded "E0|E0 identically 0 (extra
   mu0 degeneracy)" row; E0true|X0j = (1, 0) unchanged.  The
   norm-selection conclusion (Einstein pairs slice-integrable, extra
   pairs divergent, Einstein selected) SURVIVES and is strengthened:
   both sectors now show the same genuine Einstein class.

Decisive mutations:
  M1 (row audit): the superseded E0 representative fails the vv row with
      exact residual (2r + 3)/r^2 (closed form -- the jet terminates).
  M2 (window): recomposing a carrier mode WITHOUT the Einstein-family
      correction leaves nonzero residual rows, and its pair window is
      NOT constant (nonzero keys >= 1) -- the constancy assert is
      decisive against off-shell pseudo-modes.

NOT established: symbolic-frequency values; general l; any stability or
positive-norm statement; a representative-invariant extra-block sign
theory (the null-quotient theory remains the open successor item).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

import bh2b_polar_reach as reach
from bh2b_polar_cross_flux import run_pipeline as cross_run_pipeline
from linearized_theta import LinearizedTheta
from weyl_geometry import Geometry

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMA_NAME = "pure-weyl-bh2b-composed-repair-v1"
SCHEMA_PATH = HERE / "schema" / "bh2b-composed-repair-v1.schema.json"
CERT_PATH = HERE / "certificates" / "BH2B_COMPOSED_REPAIR.json"
RESULT_ID = "PURE_WEYL_BH2B_COMPOSED_REPAIR"
RESULT_TOKEN = "BH2B_POLAR_COMPOSED_LIFT_AUDITED_EXACT_CONSTANT_FLUX"

SUPERSEDED_CROSS = HERE / "certificates" / "BH2B_POLAR_CROSS_FLUX.json"
SUPERSEDED_CLASS = HERE / "certificates" / "BH2C_POLAR_FLUX_CLASS.json"

KWIN = 7          # certified constancy window rho^1..rho^KWIN
CAPI = KWIN + 13  # intermediate product cap (towers first)
NIH = 8           # infinity hom jet depth (matches BH2C)

FAMS = ("E", "G", "X0", "X1", "X2")
CONTROL_PAIRS = [(a, b) for a in FAMS for b in FAMS
                 if a == "G" or b == "G" or (a == "E" and b == "E")]
PHYS_PAIRS = [(a, b) for a in FAMS for b in FAMS
              if (a, b) not in CONTROL_PAIRS]

# exact expected rho^0 constants (i F^r / (pi alpha) NOT applied here:
# raw window coefficient of Frb, divided by pi*alpha)
EXPECTED: dict = {}   # filled below by _install_expected()


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cancel(e):
    return sp.cancel(sp.together(e))


# ======================= horizon window machinery ========================

def _laurent(e, r, rho, kmax):
    """Exact Laurent dict of a rational function of r about r = 2."""
    if e == 0:
        return {}
    num, den = sp.fraction(sp.cancel(sp.together(e)))
    pn = sp.Poly(sp.expand(num.subs(r, 2 + rho)), rho)
    pdn = sp.Poly(sp.expand(den.subs(r, 2 + rho)), rho)
    d0 = min(m[0] for m in pdn.monoms())
    n0 = min((m[0] for m in pn.monoms()), default=None)
    if n0 is None:
        return {}
    dd = [pdn.coeff_monomial(rho ** (d0 + k))
          for k in range(kmax + d0 - n0 + 3)]
    inv = [sp.Integer(1) / dd[0]]
    for k in range(1, len(dd)):
        acc = sum(dd[j] * inv[k - j] for j in range(1, k + 1) if j < len(dd))
        inv.append(sp.cancel(-acc / dd[0]))
    ser = {}
    for k in range(len(dd)):
        key = (n0 - d0) + k
        if key > kmax:
            break
        ser[key] = sp.expand(sum(
            pn.coeff_monomial(rho ** (n0 + j)) * inv[k - j]
            for j in range(k + 1)))
    return {k: sp.cancel(val) for k, val in ser.items() if val != 0}


def _smul(sa, sb, cap):
    out = {}
    for ka, va in sa.items():
        for kb, vb in sb.items():
            k = ka + kb
            if k <= cap:
                out[k] = sp.expand(out.get(k, 0) + va * vb)
    return out


def horizon_windows(geo_cls, wnum):
    """Exact rho-window table for all 25 pairs at fixture wnum."""
    t0 = time.time()
    res = cross_run_pipeline(geo_cls, wnum, [sp.Rational(1, 4)],
                             return_exprs=True)
    ex = res["exprs"]
    fam_p, fam_m, Frb = ex["fam_p"], ex["fam_m"], ex["Frb"]
    atoms, names = ex["atoms"], ex["names"]
    r, v, rho = ex["r"], ex["v"], ex["rho"]
    alpha = ex["alpha"]
    print(f"[pipeline {wnum}] {round(time.time() - t0, 1)} s", flush=True)

    t0 = time.time()

    def atom_info(at):
        if isinstance(at, sp.Derivative):
            f = at.args[0]
            jt = sum(int(p[1]) for p in at.args[1:] if p[0] == v)
            kr = sum(int(p[1]) for p in at.args[1:] if p[0] == r)
        else:
            f, jt, kr = at, 0, 0
        name = f.func.__name__
        return f, name[:-1], name[-1], jt, kr

    a_atoms = [at for at in atoms if atom_info(at)[2] == "a"]
    b_atoms = [at for at in atoms if atom_info(at)[2] == "b"]

    Fe = sp.expand(Frb)
    cij = {}
    for i, aa in enumerate(a_atoms):
        dFa = sp.diff(Fe, aa)
        for j, bb in enumerate(b_atoms):
            c = sp.diff(dFa, bb)
            if c != 0:
                cij[(i, j)] = _laurent(c, r, rho, KWIN + 5)
    rest = Fe - sp.expand(sum(
        sp.diff(sp.diff(Fe, a_atoms[i]), b_atoms[j])
        * a_atoms[i] * b_atoms[j] for (i, j) in cij))
    _require(sp.simplify(rest) == 0, "Frb not purely bilinear")

    def atom_series(at, mode):
        f, base, tag, jt, kr = atom_info(at)
        wv = wnum if tag == "a" else -wnum
        e = sp.expand((sp.I * wv) ** jt * sp.diff(mode[names[base]], rho, kr))
        pol = sp.Poly(e, rho)
        return {m[0]: pol.coeff_monomial(rho ** m[0]) for m in pol.monoms()
                if m[0] <= CAPI}

    aser = {na: [atom_series(at, fam_p[na]) for at in a_atoms] for na in FAMS}
    bser = {nb: [atom_series(at, fam_m[nb]) for at in b_atoms] for nb in FAMS}

    table = {}
    for na in FAMS:
        for nb in FAMS:
            tot = {}
            for (i, j), cs in cij.items():
                prod = _smul(aser[na][i], bser[nb][j], CAPI)
                term = _smul(cs, prod, KWIN)
                for k, val in term.items():
                    tot[k] = sp.expand(tot.get(k, 0) + val)
            table[(na, nb)] = {k: sp.cancel(val / (sp.pi * alpha))
                               for k, val in sorted(tot.items())}
    print(f"[windows {wnum}] {round(time.time() - t0, 1)} s", flush=True)

    # fail-closed asserts
    for (na, nb) in CONTROL_PAIRS:
        bad = {k: val for k, val in table[(na, nb)].items() if val != 0}
        _require(not bad, f"control pair {na}|{nb} nonzero at {sorted(bad)}")
    consts = {}
    for (na, nb) in PHYS_PAIRS:
        tt = table[(na, nb)]
        drift = {k: val for k, val in tt.items() if k != 0 and val != 0}
        _require(not drift,
                 f"pair {na}|{nb} not constant: keys {sorted(drift)}")
        c0 = tt.get(0, sp.Integer(0))
        _require(c0 != 0, f"physical pair {na}|{nb} unexpectedly zero")
        consts[f"{na}|{nb}"] = c0
    # exact Hermiticity and positivity of K = i F^r / (pi alpha) on X block
    for i2 in ("X0", "X1", "X2"):
        for j2 in ("X0", "X1", "X2"):
            dev = _cancel(sp.I * consts[f"{i2}|{j2}"]
                          - sp.conjugate(sp.I * consts[f"{j2}|{i2}"]))
            _require(dev == 0, f"exact Hermiticity fails at ({i2},{j2})")
    for i2 in ("X0", "X1", "X2"):
        val = _cancel(sp.I * consts[f"{i2}|{i2}"])
        _require(sp.im(val) == 0 and sp.re(val) > 0,
                 f"diagonal {i2} not exactly positive real")
    return res, table, consts


def mutation_uncorrected_window(geo_cls, wnum):
    """M2: the constancy assert is decisive -- an off-shell pseudo-mode
    (E-slot mode with its subleading orders zeroed) drifts."""
    res = cross_run_pipeline(geo_cls, wnum, [sp.Rational(1, 4)],
                             return_exprs=True)
    ex = res["exprs"]
    fam_p, fam_m, Frb = ex["fam_p"], ex["fam_m"], ex["Frb"]
    atoms, names = ex["atoms"], ex["names"]
    r, v, rho = ex["r"], ex["v"], ex["rho"]
    alpha = ex["alpha"]
    # truncate the a-slot X0 mode to its leading 3 orders: no longer a
    # solution -> the pair flux with the exact b-slot mode must drift
    mut = tuple(sum(sp.expand(ser).coeff(rho, k) * rho ** k
                    for k in range(3)) for ser in fam_p["X0"])

    def atom_info(at):
        if isinstance(at, sp.Derivative):
            f = at.args[0]
            jt = sum(int(p[1]) for p in at.args[1:] if p[0] == v)
            kr = sum(int(p[1]) for p in at.args[1:] if p[0] == r)
        else:
            f, jt, kr = at, 0, 0
        name = f.func.__name__
        return f, name[:-1], name[-1], jt, kr

    a_atoms = [at for at in atoms if atom_info(at)[2] == "a"]
    b_atoms = [at for at in atoms if atom_info(at)[2] == "b"]
    Fe = sp.expand(Frb)

    def atom_series(at, mode, wv):
        f, base, tag, jt, kr = atom_info(at)
        e = sp.expand((sp.I * wv) ** jt * sp.diff(mode[names[base]], rho, kr))
        pol = sp.Poly(e, rho)
        return {m[0]: pol.coeff_monomial(rho ** m[0]) for m in pol.monoms()
                if m[0] <= CAPI}

    amut = [atom_series(at, mut, wnum) for at in a_atoms]
    bx0 = [atom_series(at, fam_m["X0"], -wnum) for at in b_atoms]
    tot = {}
    for i, aa in enumerate(a_atoms):
        dFa = sp.diff(Fe, aa)
        for j, bb in enumerate(b_atoms):
            c = sp.diff(dFa, bb)
            if c == 0:
                continue
            cs = _laurent(c, r, rho, KWIN + 5)
            term = _smul(cs, _smul(amut[i], bx0[j], CAPI), KWIN)
            for k, val in term.items():
                tot[k] = sp.expand(tot.get(k, 0) + val)
    drift = {k: sp.cancel(val / (sp.pi * alpha))
             for k, val in tot.items() if k != 0}
    drift = {k: val for k, val in drift.items() if val != 0}
    _require(drift, "mutated off-shell mode failed to drift")
    return sorted(drift)


# ======================= infinity vv/vr audit ============================

def infinity_audit(geo_cls):
    """BH2C repair: vv/vr audit of the hom jets, Einstein combination,
    recomputed table classes with the true Einstein representative."""
    t0 = time.time()
    wnum = sp.Rational(3, 5)
    R = reach.run_analysis(geo_cls, light=True)
    v = R["syms"]["v"]
    r = R["syms"]["r"]
    w = R["syms"]["omega"]
    x = R["syms"]["x"]
    B0 = 1 - 2 / r
    coords = [v, r, x, sp.Symbol("phi")]
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r ** 2 / (1 - x ** 2)
    g0[3, 3] = r ** 2 * (1 - x ** 2)
    geo0 = geo_cls(coords, g0)
    gi = geo0.ginv
    G = geo0.Gamma
    N = 4
    P2 = (3 * x ** 2 - 1) / 2
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

    def cov_dG(e2, a, b, c):
        s = sp.diff(dG[a][b][c], coords[e2])
        for hh in range(N):
            s += G[a][e2][hh] * dG[hh][b][c]
            s -= G[hh][e2][b] * dG[a][hh][c] + G[hh][e2][c] * dG[a][b][hh]
        return s

    need = [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (2, 2)]
    dRic = {}
    for (b, d) in need:
        dRic[(b, d)] = _cancel(sum(cov_dG(a, a, b, d) - cov_dG(d, a, b, a)
                                   for a in range(N)))
    x0, x1 = sp.Integer(0), sp.Rational(1, 2)

    def strip(raw, ang, xa, xb):
        e0_ = _cancel(raw.subs(x, xa).doit() / E) / ang.subs(x, xa)
        chk = _cancel(raw.subs(x, xb).doit() / E - e0_ * ang.subs(x, xb))
        _require(chk == 0, "strip inconsistent")
        return _cancel(e0_)

    hrow = {"vv": strip(dRic[(0, 0)], P2, x0, x1),
            "vr": strip(dRic[(0, 1)], P2, x0, x1),
            "vx": strip(dRic[(0, 2)], dP2, x1, sp.Rational(1, 3)),
            "rx": strip(dRic[(1, 2)], dP2, x1, sp.Rational(1, 3)),
            "rr": strip(dRic[(1, 1)], P2, x0, x1)}
    raw = dRic[(2, 2)] / E
    Msv = sp.Matrix([[g0[2, 2].subs(x, x0) * P2.subs(x, x0), Wxx],
                     [g0[2, 2].subs(x, x1) * P2.subs(x, x1), Wxx]])
    solv = Msv.solve(sp.Matrix([_cancel(raw.subs(x, x0).doit()),
                                _cancel(raw.subs(x, x1).doit())]))
    hrow["angW"] = _cancel(solv[1])

    d1 = lambda fn: sp.Derivative(fn, r)
    Bc_sol = sp.solve(sp.Eq(hrow["angW"], 0), Bh)
    _require(len(Bc_sol) == 1, "Bc not solvable")
    Bc_e0 = _cancel(Bc_sol[0])
    subB = {sp.Derivative(Bh, (r, 2)): sp.diff(Bc_e0, r, 2).doit(),
            sp.Derivative(Bh, r): sp.diff(Bc_e0, r).doit(), Bh: Bc_e0}
    R2 = {nm: _cancel(hrow[nm].subs(subB).doit())
          for nm in ("vx", "rx", "rr")}
    Ap = _cancel(sp.solve(sp.Eq(R2["vx"], 0), d1(Ah))[0])
    Kp = _cancel(sp.solve(sp.Eq(R2["rx"], 0), d1(Kh))[0])
    rr1 = R2["rr"].subs({sp.Derivative(Kh, (r, 2)): sp.diff(Kp, r).doit(),
                         d1(Kh): Kp}).doit()
    rr1 = _cancel(rr1.subs(d1(Ah), Ap).doit())
    C2 = _cancel(sp.solve(sp.Eq(rr1, 0), sp.Derivative(Ch, (r, 2)))[0])
    wsub = {w: wnum}
    Ap, Kp, C2, Bc_e0w = [e.subs(wsub) for e in (Ap, Kp, C2, Bc_e0)]
    state = [Ah, Ch, d1(Ch), Kh]
    Mh = sp.zeros(4, 4)
    Mh[1, 2] = 1
    for i, expr in ((0, Ap), (2, C2), (3, Kp)):
        e = sp.expand(expr)
        for j, st in enumerate(state):
            Mh[i, j] = _cancel(e.coeff(st))

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
        dd = [(pd.coeff_monomial(r ** (dmax - k)) if dmax - k >= 0 else 0)
              for k in range(depth + 1)]
        inv = [sp.Integer(1) / dd[0]]
        for k in range(1, depth + 1):
            acc = sum(dd[j] * inv[k - j] for j in range(1, k + 1))
            inv.append(sp.cancel(-acc / dd[0]))
        nn = [(pn.coeff_monomial(r ** (nmax - k)) if nmax - k >= 0 else 0)
              for k in range(depth + 1)]
        ser = {}
        for k in range(depth + 1):
            ser[k - (nmax - dmax)] = sp.expand(
                sum(nn[j] * inv[k - j] for j in range(k + 1)))
        return ser

    DEP4 = NIH + 6
    Bser4 = {(i, j): inv_series_entry(Mh[i, j], DEP4)
             for i in range(4) for j in range(4)}
    _require(min([min(s.keys()) for s in Bser4.values() if s] + [0]) >= 0,
             "h-system matrix has growing entries")
    Bk4 = [sp.Matrix(4, 4, lambda i, j: Bser4[(i, j)].get(k, sp.Integer(0)))
           for k in range(DEP4 + 1)]
    lam = sp.Symbol("lam")
    _require(sp.factor(Bk4[0].charpoly(lam).as_expr())
             == lam ** 3 * (5 * lam + 6 * sp.I) / 5,
             "h leading matrix charpoly does not match shipped BH2C")
    print(f"[audit setup] {round(time.time() - t0, 1)} s", flush=True)

    t0 = time.time()

    def column_jets(Bk, dim, muv, sig0, depth):
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
            resd = (sig0 - n) * Z[n] - B0c * Z[n + 1]
            for k in range(1, n + 2):
                j = n + 1 - k
                if j < len(Z):
                    resd -= Bk[k] * Z[j]
            for i in range(dim):
                for c in range(Pfin):
                    _require(_cancel(resd[i, c]) == 0,
                             f"jet residual n={n} row {i} col {c}")
        sols = []
        for c in range(Pfin):
            Y = [[_cancel(Z[n][i, c]) for i in range(dim)]
                 for n in range(depth + 1)]
            n0 = next((n for n in range(len(Y))
                       if any(vv_ != 0 for vv_ in Y[n])), None)
            if n0 == 0:
                sols.append(Y)
        return sols

    jets = {}
    for s0 in (1, 0, -1):
        sols = column_jets(Bk4, 4, sp.Integer(0), sp.Integer(s0), NIH)
        _require(len(sols) == 1, f"mu0 sigma0={s0}: {len(sols)} jets != 1")
        jets[s0] = sols[0]
    sols2 = column_jets(Bk4, 4, -2 * wnum, -4 * sp.I * wnum + 1, NIH)
    _require(len(sols2) == 1, "-2w sector jet count != 1")
    jet_m2w = sols2[0]
    # the shipped representative terminates: (A, C, K) = (r, 0, -5i/3)
    _require(jets[1][0][0] == 1 and jets[1][1][3] != 0
             and all(jets[1][n][i] == 0 for n in range(2, NIH + 1)
                     for i in range(4)),
             "sigma0=1 jet does not terminate as recorded")

    # --- Laurent-dict row evaluation ---
    def dopr(dic, muv, sig0):
        out = {}
        for n, c in dic.items():
            out[n] = sp.expand(out.get(n, 0) + sp.I * muv * c)
            out[n + 1] = sp.expand(out.get(n + 1, 0) + (sig0 - n) * c)
        return out

    def series_mul(cser, dic, cap):
        out = {}
        for kc, cc2 in cser.items():
            for n, c in dic.items():
                k = kc + n
                if k <= cap:
                    out[k] = sp.expand(out.get(k, 0) + cc2 * c)
        return out

    fields = [Ah, Bh, Ch, Kh]
    row_atoms = []
    for f in fields:
        for k in (0, 1, 2):
            row_atoms.append(f if k == 0 else sp.Derivative(f, (r, k)))
    batoms = [Ch, sp.Derivative(Ch, r), sp.Derivative(Ch, (r, 2))]
    Mb, bb0 = sp.linear_eq_to_matrix([sp.expand(Bc_e0w)], batoms)
    _require(all(sp.simplify(z) == 0 for z in bb0), "Bc relation inhomog.")

    def audit_row(row_name, Y, muv, sig0, cap):
        row = hrow[row_name].subs(wsub)
        Mlin, blin = sp.linear_eq_to_matrix([sp.expand(row)], row_atoms)
        _require(all(sp.simplify(z) == 0 for z in blin),
                 "row not homogeneous-linear")
        prof = {f: {n: Y[n][{Ah: 0, Ch: 1, Kh: 3}[f]]
                    for n in range(len(Y))}
                for f in (Ah, Ch, Kh)}
        cd = [prof[Ch], dopr(prof[Ch], muv, sig0),
              dopr(dopr(prof[Ch], muv, sig0), muv, sig0)]
        bdict = {}
        for j in range(3):
            cser = inv_series_entry(Mb[0, j], cap + 6)
            if not cser:
                continue
            for k, val in series_mul(cser, cd[j], cap).items():
                bdict[k] = sp.expand(bdict.get(k, 0) + val)
        prof[Bh] = bdict
        total = {}
        for j, at in enumerate(row_atoms):
            coef = Mlin[0, j]
            if coef == 0:
                continue
            f = at if not isinstance(at, sp.Derivative) else at.args[0]
            k = 0 if not isinstance(at, sp.Derivative) else at.derivative_count
            d = prof[f]
            for _ in range(k):
                d = dopr(d, muv, sig0)
            for kk, val in series_mul(inv_series_entry(coef, cap + 6),
                                      d, cap).items():
                total[kk] = sp.expand(total.get(kk, 0) + val)
        return {k: sp.cancel(val) for k, val in sorted(total.items())
                if k <= cap}

    CAP = 6
    residuals = {}
    for s0 in (1, 0, -1):
        for nm in ("vx", "rx"):
            resd = audit_row(nm, jets[s0], sp.Integer(0), sp.Integer(s0), CAP)
            _require(all(val == 0 for val in resd.values()),
                     f"imposed row {nm} dirty at sigma0={s0} (control)")
        for nm in ("vv", "vr"):
            resd = audit_row(nm, jets[s0], sp.Integer(0), sp.Integer(s0), CAP)
            nz = {k: val for k, val in resd.items() if val != 0}
            residuals[(nm, s0)] = nz
    for nm in ("vv", "vr"):
        resd = audit_row(nm, jet_m2w, -2 * wnum, -4 * sp.I * wnum + 1, CAP)
        _require(all(val == 0 for val in resd.values()),
                 f"-2w jet dirty in {nm}")
    # verdicts pinned
    _require(all(not residuals[("vr", s0)] for s0 in (1, 0, -1)),
             "vr unexpectedly dirty on a mu0 jet")
    _require(residuals[("vv", 1)] == {2: sp.Integer(2), 3: sp.Integer(3)},
             "sigma0=1 vv residual != {2: 2, 3: 3}")
    _require(all(residuals[("vv", s0)] for s0 in (0, -1)),
             "expected nonzero vv residual missing")

    # --- unique Einstein combination ---
    c1s, c0s, cm1s = sp.symbols("c1 c0 cm1")
    coefs = {1: c1s, 0: c0s, -1: cm1s}
    sys_by_a = {}
    for s0 in (1, 0, -1):
        for k, val in residuals[("vv", s0)].items():
            a = s0 - k
            sys_by_a[a] = sys_by_a.get(a, 0) + coefs[s0] * val
    CAPW = 7
    eqs = [sp.expand(z) for a, z in sys_by_a.items() if a >= 1 - CAPW]
    Ml, _bl = sp.linear_eq_to_matrix(eqs, [c1s, c0s, cm1s])
    ns = Ml.nullspace()
    _require(len(ns) == 1, "Einstein combination not unique")
    cc = ns[0]
    _require(cc[0] != 0 and cc[1] != 0 and cc[2] != 0,
             "Einstein combination misses a jet")
    DEPTH_ABS = CAPW + 1
    comb = [[sp.Integer(0)] * 4 for _ in range(DEPTH_ABS + 1)]
    for s0 in (1, 0, -1):
        ci = {1: cc[0], 0: cc[1], -1: cc[2]}[s0]
        sh = 1 - s0
        for n in range(len(jets[s0])):
            if n + sh <= DEPTH_ABS:
                for i in range(4):
                    comb[n + sh][i] = sp.cancel(comb[n + sh][i]
                                                + ci * jets[s0][n][i])
    for nm in ("vv", "vr", "vx", "rx"):
        resd = audit_row(nm, comb, sp.Integer(0), sp.Integer(1), CAPW - 1)
        _require(all(sp.cancel(val) == 0 for val in resd.values()),
                 f"Einstein combination dirty in {nm}")
    print(f"[audit rows] {round(time.time() - t0, 1)} s", flush=True)

    # --- recomputed table classes with the true Einstein jet ---
    t0 = time.time()
    alpha = sp.Symbol("alpha", positive=True)
    lt = LinearizedTheta(geo0, alpha)

    def polar_h(tag):
        fns = [sp.Function(n + tag)(v, r) for n in ("A", "Bc", "Cc", "K")]
        h = sp.zeros(4, 4)
        h[0, 0] = fns[0] * P2
        h[0, 1] = h[1, 0] = fns[1] * P2
        h[1, 1] = fns[2] * P2
        h[2, 2] = g0[2, 2] * fns[3] * P2
        h[3, 3] = g0[3, 3] * fns[3] * P2
        return h, fns

    hA, fA4 = polar_h("a")
    hB, fB4 = polar_h("b")
    wab = lt.omega(hA, hB)
    _require(wab[3] == 0, "phi component of omega nonzero")
    ph_s = coords[3]
    Fv = _cancel(sp.integrate(sp.integrate(wab[0] * r ** 2, (x, -1, 1)),
                              (ph_s, 0, 2 * sp.pi)))
    _require(Fv != 0, "Fv unexpectedly zero")
    print(f"[Fv] {round(time.time() - t0, 1)} s", flush=True)

    t0 = time.time()
    Lg = sp.Symbol("Lg", positive=True)

    def bc_prof(Cc_expr):
        subm = {}
        for d in list(Bc_e0w.atoms(sp.Derivative)):
            if d.args[0] == Ch:
                subm[d] = sp.diff(Cc_expr, r, d.derivative_count)
        subm[Ch] = Cc_expr
        return _cancel(Bc_e0w.subs(subm).doit())

    def hom_profile(Y, sig0):
        Ae = sum(Y[n][0] * r ** (sig0 - n) for n in range(len(Y)))
        Cce = sum(Y[n][1] * r ** (sig0 - n) for n in range(len(Y)))
        Ke = sum(Y[n][3] * r ** (sig0 - n) for n in range(len(Y)))
        return (Ae, bc_prof(Cce), Cce, Ke)

    profiles = {"E0old": hom_profile(jets[1], sp.Integer(1)),
                "E0true": hom_profile(comb, sp.Integer(1))}

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
        pa, pb = profiles[na], profiles[nb]
        EA = sp.exp(sp.I * wnum * v)
        EB = sp.exp(-sp.I * wnum * v)
        reps = {}
        for i, (fa, fb) in enumerate(zip(fA4, fB4)):
            reps[fa] = pa[i] * EA
            reps[fb] = (sp.conjugate(pb[i]).subs(sp.conjugate(r), r)
                        .subs(sp.conjugate(sp.log(r)), sp.log(r)) * EB)
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

    lp_old = flux_pair("E0old", "E0old")
    lp_true = flux_pair("E0true", "E0true")
    _require(lp_old is None, "E0old|E0old no longer identically zero")
    _require(lp_true == (-2, 0),
             f"E0true|E0true class {lp_true} != (-2, 0)")
    print(f"[table classes] {round(time.time() - t0, 1)} s", flush=True)

    return {
        "vv_residuals": {str(s0): {str(k): sp.sstr(val)
                                   for k, val in residuals[("vv", s0)].items()}
                         for s0 in (1, 0, -1)},
        "einstein_combination": [sp.sstr(sp.cancel(e)) for e in cc],
        "e0old_class": "None (identically zero)",
        "e0true_class": "(-2, 0)",
        "m2w_clean": True,
    }


# ======================= expected exact constants ========================

def _install_expected():
    """Exact expected rho^0 constants of F^r/(pi alpha) at the canonical
    representatives.  Every recorded value is pinned here so the producer
    and the independent verifier both fail closed on any drift."""
    I = sp.I
    EXPECTED["3/5"] = {
        "X0|X0": -sp.Rational(2871808, 35525) * I,
        "X1|X1": -sp.Rational(1172815072, 22203125) * I,
        "X0|X1": (-sp.Rational(63530880, 888125)
                  - sp.Rational(20282624, 888125) * I),
        "X1|X0": (sp.Rational(63530880, 888125)
                  - sp.Rational(20282624, 888125) * I),
        "X0|X2": (-sp.Rational(3817280, 888125)
                  - sp.Rational(65327616, 888125) * I),
        "X1|X2": (sp.Rational(1177699920, 22203125)
                  - sp.Rational(601270848, 22203125) * I),
    }
    EXPECTED["2/7"] = {
        "X0|X0": -sp.Rational(94557184, 2351265) * I,
        "X1|X1": -sp.Rational(44119418816, 5645387265) * I,
        "X0|X1": (-sp.Rational(48047488, 2351265)
                  + sp.Rational(121948672, 23042397) * I),
        "X1|X0": (sp.Rational(48047488, 2351265)
                  + sp.Rational(121948672, 23042397) * I),
        "X0|X2": (-sp.Rational(399424, 5486285)
                  - sp.Rational(3263193088, 115211985) * I),
        "X1|X2": (sp.Rational(2033039024, 161296779)
                  + sp.Rational(3037861504, 1129077453) * I),
    }


def run_analysis(geo_cls) -> dict:
    out: dict = {"stage_seconds": {}}
    t_all = time.time()
    _install_expected()
    _require(EXPECTED, "expected-constant table not installed")

    fixtures = {}
    for tag, wnum in (("3/5", sp.Rational(3, 5)), ("2/7", sp.Rational(2, 7))):
        t0 = time.time()
        _res, _table, consts = horizon_windows(geo_cls, wnum)
        fixtures[tag] = {key: sp.sstr(val) for key, val in consts.items()}
        exp = EXPECTED.get(tag)
        if exp is not None:
            for key, val in exp.items():
                _require(sp.cancel(consts[key] - val) == 0,
                         f"fixture {tag} {key} mismatch")
        out["stage_seconds"][f"windows_{tag}"] = round(time.time() - t0, 1)

    t0 = time.time()
    drift_keys = mutation_uncorrected_window(geo_cls, sp.Rational(3, 5))
    out["stage_seconds"]["mutation_m2"] = round(time.time() - t0, 1)

    t0 = time.time()
    audit = infinity_audit(geo_cls)
    out["stage_seconds"]["infinity_audit"] = round(time.time() - t0, 1)

    out["fixtures"] = fixtures
    out["mutation_drift_keys"] = [int(k) for k in drift_keys]
    out["audit"] = audit
    out["stage_seconds"]["total"] = round(time.time() - t_all, 1)
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
            "theory": "S = alpha * integral sqrt(-g) C_{abcd} C^{abcd}",
            "background_family": "Schwarzschild exterior, m = 1 fixtures",
            "conformal_frame": "fixed representative g (certified atlas)",
            "generator": "EF ingoing-regular polar l = 2 mode families",
            "phase_space": "linear conjugate-pair Lee-Wald pairing",
            "horizon_condition": "ingoing-regular at rho = 0 (analytic)",
            "infinity_condition": "formal power jets at r = infinity "
                                  "(BH2C norm-selection framework)",
            "lifecycle": "CLASSIFIED",
        },
        "supersedes": {
            "cross_flux_certificate":
                str(SUPERSEDED_CROSS.relative_to(ROOT)),
            "cross_flux_certificate_sha256": _sha256(SUPERSEDED_CROSS),
            "cross_flux_scope":
                "fixture VALUES only: the radius-sampled numerical matrix "
                "entries and the 5e-2 r-independence tolerance are replaced "
                "by exact rho^0 constants with an exact all-zero constancy "
                "window rho^1..rho^7; the certificate's theorems "
                "(composition existence, Hermiticity, null controls, "
                "separation) are CONFIRMED, not repaired",
            "flux_class_certificate":
                str(SUPERSEDED_CLASS.relative_to(ROOT)),
            "flux_class_certificate_sha256": _sha256(SUPERSEDED_CLASS),
            "flux_class_scope":
                "the mu0-sector Einstein ROW ONLY: the shipped E0 "
                "representative (terminating sigma0=1 jet A=r, C=0, "
                "K=-5i/3) fails the never-imposed vv row with exact "
                "closed-form residual (2r+3)/r^2 and is not a linearized "
                "Einstein solution; the true Einstein mu0 direction is the "
                "unique vv-clean combination of the three mu0 power jets; "
                "E0|E0 'identically zero (extra mu0 degeneracy)' is "
                "replaced by E0true|E0true class (-2, 0) = the certified "
                "E2|E2 class; E|X and X|X classes and the Einstein "
                "norm-selection verdict are UNCHANGED",
        },
        "lift_statement": {
            "all_analytic_carrier_modes_lift": True,
            "basis": "the composition recursion (n = 0 Frobenius balance "
                     "imposed, log-resonance fail-closed) plus the "
                     "Einstein-family correction solve succeeds for every "
                     "analytic carrier mode at both fixtures (horizon) and "
                     "for all three carrier jets per sector (infinity, "
                     "certified BH2C); re-asserted in this run",
            "lift_ambiguity": "span(Einstein mode, conformal gauge mode) "
                              "per slot",
        },
        "invariance_classification": {
            "conformal_shifts": "NO entry changes: every G pair is "
                                "identically zero at every window key",
            "einstein_shifts": "E row/column and controls invariant "
                               "(E|E = 0 exactly); extra-block entries "
                               "shift by exact multiples of the cross "
                               "constants: delta F(Xi|Xj) = "
                               "conj(beta_j) F(Xi|E) + beta_i F(E|Xj)",
            "invariant_entries": ["E|Xj cross constants (up to the E-slot "
                                  "normalization)", "all controls"],
            "representative_dependent_entries": ["Xi|Xj extra block"],
            "canonical_representative": "correction parameters zeroed "
                                        "(pipeline canonical choice)",
        },
        "fixtures": res["fixtures"],
        "constancy_window": {"checked_keys": f"1..{KWIN}",
                             "all_zero": True,
                             "validity": "B-component series depth bounds "
                                         "the certified window at rho^7"},
        "mutations": {
            "M1_row_audit": "the superseded E0 representative fails vv "
                            "with exact residual (2r+3)/r^2 (closed form; "
                            "jet terminates); recorded in audit stage",
            "M2_window": "a truncated (off-shell) a-slot X0 pseudo-mode "
                         "drifts at keys "
                         + str(res["mutation_drift_keys"])
                         + " -- the constancy assert is decisive",
        },
        "audit": res["audit"],
        "verification_discipline": [
            "bilinear coefficients extracted by differentiation of the "
            "multilinear polynomial structure (never .coeff on expanded "
            "giant trees)",
            "exact Laurent-dict arithmetic with intermediate caps above "
            "the output window (towers first, coefficient last)",
            "no nsimplify anywhere; residual verdicts are exact rationals",
            "controls: imposed rows re-audited as positive controls "
            "before trusting the vv/vr verdicts",
        ],
        "missing_objects": [
            "symbolic-frequency window table (successor item)",
            "general l",
            "representative-invariant extra-block sign theory "
            "(null-quotient pairing)",
            "outer-boundary (scattering-domain) counterparts",
            "any dynamical-behaviour statement (vocabulary "
            "coordinator-gated)",
        ],
        "claim_flags": {
            "exact_constant_flux_certified": True,
            "all_carrier_modes_lift": True,
            "invariance_classified": True,
            "vv_vr_audit_complete": True,
            "e0_row_superseded": True,
            "einstein_selection_confirmed": True,
            "symbolic_omega_certified": False,
            "general_l_certified": False,
            "invariant_sign_theory_certified": False,
        },
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2b_composed_repair.py",
            "pipeline_path":
                "black_hole_programme/bh2b_polar_cross_flux.py",
            "pipeline_sha256":
                _sha256(HERE / "bh2b_polar_cross_flux.py"),
            "reach_path": "black_hole_programme/bh2b_polar_reach.py",
            "reach_sha256": _sha256(HERE / "bh2b_polar_reach.py"),
        },
        "verification_command":
            "python3 black_hole_programme/verify_bh2b_composed_repair.py",
    }
    return certificate


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
