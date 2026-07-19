"""BH-2B stage 2: the polar extra branch reaches the horizon (linear mode level).

Fail-closed builder for
`black_hole_programme/certificates/BH2B_POLAR_REACH.json`.

Verdict: BH2B_POLAR_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL.

Setting: ingoing Eddington--Finkelstein chart (v, r, x = cos theta, phi) on
Schwarzschild (symbolic m); polar l=2 trace-coupled extra-branch carrier
(psi_ab, S = tr psi) with even-parity harmonics P2, dP2/dx and the traceless
tensor harmonic (W_xx, W_phiphi) = (3/2, -3(1-x^2)^2/2), satisfying the
certified polar extra-branch operator (BH-2B stage 1)

    E_ab = (1/2) Box psi_ab + C_acbd psi^cd - (1/6) D_a D_b S
           - (1/12) g_ab Box S = 0,
    with the linearized-Bianchi constraint  D^a psi_ab = (1/2) D_b S.

Exact results:

1. the three Bianchi constraint rows solve ALGEBRAICALLY (cascade) for the
   (vx), (rx) and W-sector angular carrier components, with x-independent
   solutions: the constrained carrier has 4 free radial functions
   (a, bc, cc, f) = (psi_vv, psi_vr, psi_rr, psi-angular-trace components);
2. the constrained operator obeys two exact tensor identities, identically
   in the 4 free functions:  g^{ab} E_ab = 0  and  D^a E_ab = 0; combined
   with the algebraic-solvability pattern of the harmonic ansatz these force
   the (vx), (rx), angular-P2 and angular-W operator rows to vanish on
   solutions of the (vv), (vr), (rr) rows: the polar carrier system is
   EXACTLY 3 second-order equations in 4 functions;
3. the one-function underdeterminacy is CONFORMAL GAUGE: for arbitrary
   phi(r), psi_conf = -DD Phi - (1/2) g Box Phi (= delta Ric[Phi g],
   Phi = phi e^{i omega v} P2) satisfies the Bianchi constraint and
   annihilates all seven operator rows (linearized conformal covariance of
   the Bach tensor around a Bach-flat background);
4. on the traceless slice S = 0 (algebraically f = -bc - B0 cc/2) the
   principal part diagonalizes to the scalar wave operator; the Fourier
   first-order system (6-dim) has a REGULAR singular point at r = 2m with
   residue spectrum {0 (x3), 1 - 4imw, -1 - 4imw, -3 - 4imw} and zero
   eigenvalue of geometric multiplicity 3;
5. residual conformal gauge inside the slice is Box Phi = 0 with horizon
   exponents {0, -4imw}; the regular (s=0) gauge mode maps onto a NONZERO
   all-regular carrier direction, the singular (s=-4imw) gauge mode maps
   onto component exponents (-4imw, -4imw-1, -4imw-2), i.e. leading state
   behavior -3-4imw;
6. explicit polynomial Frobenius fixtures at sample rational frequencies
   confirm a 3-dimensional analytic (ingoing-regular) family with no log
   obstruction; quotienting the 1-dimensional regular conformal-gauge
   direction leaves a TWO-parameter physical ingoing-regular polar
   extra-branch family at every real omega != 0 -- the polar twin of the
   certified axial reach theorem.

Consequence (exact, scoped): future-horizon regularity can never exclude
the polar extra branch either; pure-Weyl exteriors cannot be truncated to
the Einstein sector by horizon boundary conditions in any parity sector
of l = 2.

NOT claimed: polar flux matrix or Lee--Wald signs, Zerilli/Einstein-branch
polar benchmark, outer-boundary domains, causal disposition, growth or
stability, general l, non-Einstein backgrounds, or any ringdown statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from weyl_geometry import Geometry

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2B_POLAR_REACH.json"
SCHEMA_PATH = HERE / "schema" / "bh2b-polar-reach-v1.schema.json"
BH2B_SPLIT_CERT = HERE / "certificates" / "BH2B_POLAR_SPLIT.json"

SCHEMA_NAME = "pure-weyl-bh2b-polar-reach-v1"
RESULT_ID = "PURE_WEYL_BH2B_POLAR_REACH"
RESULT_TOKEN = "BH2B_POLAR_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL"


class BH2BReachError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise BH2BReachError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cancel(e):
    return sp.cancel(sp.together(e))


def run_analysis(geo_cls, light: bool = False) -> dict:
    """Full polar-reach analysis; geo_cls is the curvature engine class.

    With light=True the expensive analytic-family fixture stage is skipped
    and additional intermediate objects are exposed on the returned dict for
    downstream certificates (bh2c_polar_flux_class); every _require up to
    that stage still runs.  The certificate itself is always built with the
    default light=False."""
    t0_all = time.time()
    out: dict = {"stage_seconds": {}}
    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    m = sp.Symbol("m", positive=True)
    w = sp.Symbol("omega")
    rho = sp.Symbol("rho")
    coords = [v, r, x, ph]
    N = 4
    B0 = 1 - 2 * m / r
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = geo_cls(coords, g0)
    gi = geo0.ginv
    G = geo0.Gamma
    P2 = (3 * x**2 - 1) / 2
    dP2 = sp.diff(P2, x)
    Wxx = sp.Rational(3, 2)
    Wpp = -sp.Rational(3, 2) * (1 - x**2) ** 2
    # tracelessness of the W harmonic on the sphere block
    _require(_cancel(gi[2, 2] * Wxx + gi[3, 3] * Wpp) == 0, "W harmonic not traceless")

    # ---- carrier ansatz and Bianchi cascade -------------------------------
    t0 = time.time()
    A_f, Bc_f, Cc_f, D_f, Ec_f, F_f, G_f = [sp.Function(n)(v, r)
                                            for n in ("A", "Bc", "Cc", "D", "Ec", "F", "Gc")]
    psi = sp.zeros(4, 4)
    psi[0, 0] = A_f * P2
    psi[0, 1] = psi[1, 0] = Bc_f * P2
    psi[1, 1] = Cc_f * P2
    psi[0, 2] = psi[2, 0] = D_f * dP2
    psi[1, 2] = psi[2, 1] = Ec_f * dP2
    psi[2, 2] = g0[2, 2] * F_f * P2 + G_f * Wxx
    psi[3, 3] = g0[3, 3] * F_f * P2 + G_f * Wpp
    S_tr = _cancel(sum(gi[a, b] * psi[a, b] for a in range(N) for b in range(N)))

    def bianchi_row(psi_m, S_m, b):
        s = sum(gi[a, e] * geo0.covd2(psi_m, e, a, b)
                for a in range(N) for e in range(N) if gi[a, e] != 0)
        return _cancel(s - sp.diff(S_m, coords[b]) / sp.Integer(2))

    rows_b = [bianchi_row(psi, S_tr, b) for b in range(3)]
    # algebraic-solvability pattern of the harmonic ansatz (also used for the
    # operator-row dependency argument, item 2 of the docstring)
    for b, fld in [(0, D_f), (1, Ec_f), (2, G_f)]:
        _require(rows_b[b].has(fld), f"row {b} misses its cascade field")
        _require(not any(d.args[0] == fld for d in rows_b[b].atoms(sp.Derivative)),
                 f"cascade field appears differentiated in row {b}")
    sol_D = sp.solve(sp.Eq(rows_b[0], 0), D_f)
    _require(len(sol_D) == 1, "D not uniquely solvable")
    D_expr = sol_D[0]
    row1 = _cancel(rows_b[1].subs(D_f, D_expr).doit())
    sol_E = sp.solve(sp.Eq(row1, 0), Ec_f)
    _require(len(sol_E) == 1, "Ec not uniquely solvable")
    Ec_expr = sol_E[0]
    row2 = _cancel(rows_b[2].subs({D_f: D_expr, Ec_f: Ec_expr}).doit())
    sol_G = sp.solve(sp.Eq(row2, 0), G_f)
    _require(len(sol_G) == 1, "G not uniquely solvable")
    G_expr = sol_G[0]
    for nm, ee in [("D", D_expr), ("Ec", Ec_expr), ("G", G_expr)]:
        _require(not ee.has(x), f"cascade solution {nm} is x-dependent")
    out["stage_seconds"]["cascade"] = round(time.time() - t0, 1)

    # ---- Fourier reduction and constrained carrier ------------------------
    t0 = time.time()
    E = sp.exp(sp.I * w * v)
    ar, bcr, ccr, fr = [sp.Function(n)(r) for n in ("a", "bc", "cc", "f")]
    four = {A_f: ar * E, Bc_f: bcr * E, Cc_f: ccr * E, F_f: fr * E}

    def fourier(e):
        for Ff, val in four.items():
            e = e.subs({sp.Derivative(Ff, (v, 2)): sp.diff(val, v, 2),
                        sp.Derivative(Ff, v, r): sp.diff(val, v, r),
                        sp.Derivative(Ff, (r, 2)): sp.diff(val, r, 2),
                        sp.Derivative(Ff, v): sp.diff(val, v),
                        sp.Derivative(Ff, r): sp.diff(val, r),
                        Ff: val})
        return e.doit()

    G_c = _cancel(fourier(G_expr.subs({D_f: D_expr, Ec_f: Ec_expr}).doit()) / E)
    D_c = _cancel(fourier(D_expr) / E)
    Ec_c = _cancel(fourier(Ec_expr.subs(D_f, D_expr).doit()) / E)
    psi_c = sp.zeros(4, 4)
    psi_c[0, 0] = ar * P2
    psi_c[0, 1] = psi_c[1, 0] = bcr * P2
    psi_c[1, 1] = ccr * P2
    psi_c[0, 2] = psi_c[2, 0] = D_c * dP2
    psi_c[1, 2] = psi_c[2, 1] = Ec_c * dP2
    psi_c[2, 2] = g0[2, 2] * fr * P2 + G_c * Wxx
    psi_c[3, 3] = g0[3, 3] * fr * P2 + G_c * Wpp
    psi_c = psi_c.applyfunc(lambda e: e * E)
    S_c = _cancel(sum(gi[a, b] * psi_c[a, b] for a in range(N) for b in range(N)))
    for b in range(3):
        _require(bianchi_row(psi_c, S_c, b) == 0, f"constrained Bianchi row {b} nonzero")
    # trace formula behind the traceless slice
    _require(_cancel(S_c - (2 * bcr + B0 * ccr + 2 * fr) * P2 * E) == 0,
             "trace formula mismatch")
    out["stage_seconds"]["constrained_carrier"] = round(time.time() - t0, 1)

    # ---- operator rows via numeric-x harmonic extraction ------------------
    t0 = time.time()
    DX = [[[sp.together(geo0.covd2(psi_c, e, a, b)) for b in range(N)]
           for a in range(N)] for e in range(N)]

    def covd2X2(e, f, a, b):
        s = sp.diff(DX[f][a][b], coords[e])
        for hh in range(N):
            s -= (G[hh][e][f] * DX[hh][a][b] + G[hh][e][a] * DX[f][hh][b]
                  + G[hh][e][b] * DX[f][a][hh])
        return s

    Xup = sp.Matrix(4, 4, lambda c2, d2: sp.together(
        sum(gi[c2, e] * gi[d2, f] * psi_c[e, f] for e in range(4) for f in range(4))))
    dS1 = [sp.diff(S_c, coords[e]) for e in range(4)]
    DDS = sp.Matrix(4, 4, lambda a, b: sp.together(
        sp.diff(dS1[a], coords[b]) - sum(G[hh][a][b] * dS1[hh] for hh in range(4))))
    boxS = sp.together(sum(gi[e, f] * DDS[e, f] for e in range(4) for f in range(4)
                           if gi[e, f] != 0))

    def op_row(a, b):
        boxpsi = sum(gi[e, f] * covd2X2(e, f, a, b)
                     for e in range(N) for f in range(N) if gi[e, f] != 0)
        cx = sum(geo0.Weyl[a][c2][b][d2] * Xup[c2, d2]
                 for c2 in range(4) for d2 in range(4))
        return (boxpsi / 2 + cx - DDS[a, b] / 6 - g0[a, b] * boxS / 12) / E

    x0, x1, x2c = sp.Integer(0), sp.Rational(1, 2), sp.Rational(1, 3)

    def strip_single(raw, ang, xa, xb):
        e0 = _cancel(raw.subs(x, xa).doit()) / ang.subs(x, xa)
        chk = _cancel(raw.subs(x, xb).doit() - e0 * ang.subs(x, xb))
        _require(chk == 0, "harmonic stripping inconsistent")
        return _cancel(e0)

    rows = {}
    rows["vv"] = strip_single(op_row(0, 0), P2, x0, x1)
    rows["vr"] = strip_single(op_row(0, 1), P2, x0, x1)
    rows["rr"] = strip_single(op_row(1, 1), P2, x0, x1)
    rows["vx"] = strip_single(op_row(0, 2), dP2, x1, x2c)
    rows["rx"] = strip_single(op_row(1, 2), dP2, x1, x2c)
    ang_ab = {}
    for (a, b), gname in [((2, 2), "xx"), ((3, 3), "pp")]:
        raw = op_row(a, b)
        gab = g0[a, b]
        Wab = Wxx if gname == "xx" else Wpp
        vals = {xv: _cancel(raw.subs(x, xv).doit()) for xv in (x0, x1, x2c)}
        M = sp.Matrix([[gab.subs(x, x0) * P2.subs(x, x0), Wab.subs(x, x0)],
                       [gab.subs(x, x1) * P2.subs(x, x1), Wab.subs(x, x1)]])
        sol = M.solve(sp.Matrix([vals[x0], vals[x1]]))
        alpha, beta = _cancel(sol[0]), _cancel(sol[1])
        chk = _cancel(vals[x2c] - alpha * gab.subs(x, x2c) * P2.subs(x, x2c)
                      - beta * Wab.subs(x, x2c))
        _require(chk == 0, f"angular harmonic decomposition failed ({gname})")
        ang_ab[gname] = (alpha, beta)
    _require(_cancel(ang_ab["xx"][0] - ang_ab["pp"][0]) == 0
             and _cancel(ang_ab["xx"][1] - ang_ab["pp"][1]) == 0,
             "xx/phiphi angular rows inconsistent")
    rows["angP"], rows["angW"] = ang_ab["xx"]
    out["stage_seconds"]["operator_rows"] = round(time.time() - t0, 1)

    # ---- exact operator identities => 3 independent equations -------------
    t0 = time.time()
    # trace identity: g^{ab} E_ab = (2 vr + B0 rr + 2 angP) P2 E = 0
    _require(_cancel(2 * rows["vr"] + B0 * rows["rr"] + 2 * rows["angP"]) == 0,
             "trace identity g^{ab}E_ab = 0 fails")
    # divergence identity: D^a E_ab = 0, b = v, r, x (phi trivial), assembled
    # from the stripped rows and the harmonic ansatz
    Emat = sp.zeros(4, 4)
    Emat[0, 0] = rows["vv"] * P2
    Emat[0, 1] = Emat[1, 0] = rows["vr"] * P2
    Emat[1, 1] = rows["rr"] * P2
    Emat[0, 2] = Emat[2, 0] = rows["vx"] * dP2
    Emat[1, 2] = Emat[2, 1] = rows["rx"] * dP2
    Emat[2, 2] = g0[2, 2] * rows["angP"] * P2 + rows["angW"] * Wxx
    Emat[3, 3] = g0[3, 3] * rows["angP"] * P2 + rows["angW"] * Wpp
    Emat = Emat.applyfunc(lambda e: e * E)
    for b in range(3):
        s = sum(gi[a, e] * geo0.covd2(Emat, e, a, b)
                for a in range(N) for e in range(N) if gi[a, e] != 0)
        _require(_cancel(s) == 0, f"divergence identity D^a E_ab = 0 fails (b={b})")
    # with the cascade algebraic-solvability pattern (asserted above on the
    # generic harmonic ansatz), these identities solve the four rows angP,
    # vx, rx, angW in terms of vv, vr, rr: the system is 3 equations.
    out["stage_seconds"]["operator_identities"] = round(time.time() - t0, 1)

    # ---- traceless slice, first-order reduction, residue ------------------
    t0 = time.time()
    f_slice = -bcr - B0 * ccr / 2
    sub = {sp.Derivative(fr, (r, k)): sp.diff(f_slice, r, k) for k in (3, 2, 1)}
    sub[fr] = f_slice
    sys3 = [_cancel(rows[nm].subs(sub).doit()) for nm in ("vv", "vr", "rr")]
    funcs3 = [ar, bcr, ccr]
    d2 = lambda fn: sp.Derivative(fn, (r, 2))
    M2 = sp.Matrix(3, 3, lambda i, j: _cancel(sp.expand(sys3[i]).coeff(d2(funcs3[j]))))
    for i in range(3):
        for j in range(3):
            expect = _cancel((r - 2 * m) / (2 * r)) if i == j else sp.Integer(0)
            _require(_cancel(M2[i, j] - expect) == 0,
                     f"sliced principal part not diagonal wave form at ({i},{j})")
    Minv = M2.inv()
    dim = 6
    vars_list = [(j, k) for j in range(3) for k in range(2)]
    idx = {vk: i for i, vk in enumerate(vars_list)}

    def coeff_of(e, fn, k):
        tgt = fn if k == 0 else sp.Derivative(fn, (r, k))
        return sp.expand(e).coeff(tgt)

    Amat = sp.zeros(dim, dim)
    for j in range(3):
        Amat[idx[(j, 0)], idx[(j, 1)]] = 1
    for j_top in range(3):
        rowi = idx[(j_top, 1)]
        for (g2, k) in vars_list:
            s = sum(Minv[j_top, i] * coeff_of(sys3[i], funcs3[g2], k) for i in range(3))
            Amat[rowi, idx[(g2, k)]] = _cancel(-s)
    Arho = sp.Matrix(dim, dim, lambda i, j: _cancel(Amat[i, j].subs(r, 2 * m + rho)))
    for i in range(dim):
        for j in range(dim):
            if Arho[i, j] in (0, 1):
                continue
            _require(sp.simplify(sp.limit(rho**2 * Arho[i, j], rho, 0)) == 0,
                     f"irregular singular point: rho^2 A[{i}{j}] != 0")
    Res = sp.Matrix(dim, dim, lambda i, j: sp.cancel(sp.limit(rho * Arho[i, j], rho, 0))
                    if Arho[i, j] not in (0, 1) else sp.Integer(0))
    ev = {sp.nsimplify(sp.simplify(kk)): mult for kk, mult in Res.eigenvals().items()}
    expected = {sp.Integer(0): 3,
                sp.nsimplify(1 - 4 * sp.I * m * w): 1,
                sp.nsimplify(-1 - 4 * sp.I * m * w): 1,
                sp.nsimplify(-3 - 4 * sp.I * m * w): 1}
    _require(
        len(ev) == len(expected) and all(
            any(sp.simplify(kk - ee) == 0 and mult == emult for ee, emult in expected.items())
            for kk, mult in ev.items()),
        f"unexpected sliced residue spectrum {ev}",
    )
    null = Res.nullspace()
    _require(len(null) == 3, "zero exponent not geometric multiplicity 3")
    comp = sp.Matrix(3, 3, lambda i, j: null[i][idx[(j, 0)]])
    _require(comp.rank() == 3, "kernel vectors do not span independent (a,bc,cc) data")
    out["stage_seconds"]["slice_residue"] = round(time.time() - t0, 1)
    out["Res"] = Res
    out["sys3"] = sys3
    out["funcs3"] = funcs3

    # ---- conformal gauge generator ----------------------------------------
    t0 = time.time()
    phi_f = sp.Function("phi")(r)
    Phi = phi_f * E * P2
    dPhi = [sp.diff(Phi, coords[e]) for e in range(N)]
    DDPhi = sp.Matrix(4, 4, lambda a, b: sp.together(
        sp.diff(dPhi[a], coords[b]) - sum(G[hh][a][b] * dPhi[hh] for hh in range(4))))
    boxPhi = sp.together(sum(gi[e, f] * DDPhi[e, f] for e in range(4) for f in range(4)
                             if gi[e, f] != 0))
    psi_conf = sp.Matrix(4, 4, lambda a, b: sp.together(
        -DDPhi[a, b] - g0[a, b] * boxPhi / 2))
    S_conf = _cancel(sum(gi[a, b] * psi_conf[a, b] for a in range(4) for b in range(4)))
    _require(_cancel(S_conf + 3 * boxPhi) == 0, "conformal trace relation fails")
    for b in range(3):
        s = sum(gi[a, e] * geo0.covd2(psi_conf, e, a, b)
                for a in range(N) for e in range(N) if gi[a, e] != 0)
        _require(_cancel(s - sp.diff(S_conf, coords[b]) / 2) == 0,
                 f"conformal generator violates Bianchi (b={b})")
    comp_conf = {}
    comp_conf["a"] = _cancel(psi_conf[0, 0] / (P2 * E))
    comp_conf["bc"] = _cancel(psi_conf[0, 1] / (P2 * E))
    comp_conf["cc"] = _cancel(psi_conf[1, 1] / (P2 * E))
    e_xx = psi_conf[2, 2] / E
    Msolve = sp.Matrix([[g0[2, 2].subs(x, x0) * P2.subs(x, x0), Wxx],
                        [g0[2, 2].subs(x, x1) * P2.subs(x, x1), Wxx]])
    solv = Msolve.solve(sp.Matrix([_cancel(e_xx.subs(x, x0)), _cancel(e_xx.subs(x, x1))]))
    comp_conf["f"] = _cancel(solv[0])
    chk = _cancel(e_xx.subs(x, x2c) - comp_conf["f"] * g0[2, 2].subs(x, x2c) * P2.subs(x, x2c)
                  - _cancel(solv[1]) * Wxx)
    _require(chk == 0, "conformal angular decomposition failed")
    for kq, ee in comp_conf.items():
        _require(not ee.has(x), f"conformal component {kq} x-dependent")
    conf_subs = {}
    for nm, fn in [("a", ar), ("bc", bcr), ("cc", ccr), ("f", fr)]:
        val = comp_conf[nm]
        for k in (4, 3, 2, 1):
            conf_subs[sp.Derivative(fn, (r, k))] = sp.diff(val, r, k)
        conf_subs[fn] = val
    for nm in ("vv", "vr", "rr", "vx", "rx", "angP", "angW"):
        _require(_cancel(rows[nm].subs(conf_subs).doit()) == 0,
                 f"conformal gauge identity fails on row {nm}")
    wave = _cancel(boxPhi / (P2 * E))
    out["stage_seconds"]["conformal_generator"] = round(time.time() - t0, 1)
    out["wave"] = wave
    out["comp_conf"] = comp_conf
    out["phi_f"] = phi_f

    # ---- residual gauge exponents and images ------------------------------
    t0 = time.time()
    s_ = sp.Symbol("s")
    c2 = sp.expand(wave).coeff(sp.Derivative(phi_f, (r, 2)))
    c1 = sp.expand(wave).coeff(sp.Derivative(phi_f, r))
    c0 = _cancel((wave - c2 * sp.Derivative(phi_f, (r, 2))
                  - c1 * sp.Derivative(phi_f, r)) / phi_f)
    _require(not c0.has(phi_f), "wave operator coefficient extraction failed")
    c2r, c1r, c0r = [_cancel(cx.subs(r, 2 * m + rho)) for cx in (c2, c1, c0)]
    indicial = sp.expand(sp.limit(c2r / rho, rho, 0) * s_ * (s_ - 1)
                         + sp.limit(c1r, rho, 0) * s_
                         + sp.limit(rho * c0r, rho, 0))
    g_roots = sp.solve(indicial, s_)
    _require(
        len(g_roots) == 2 and any(sp.simplify(rr0) == 0 for rr0 in g_roots)
        and any(sp.simplify(rr0 + 4 * sp.I * m * w) == 0 for rr0 in g_roots),
        f"unexpected residual-gauge exponents {g_roots}",
    )

    sig = sp.Symbol("sigma")
    subs_sig = {sp.Derivative(phi_f, (r, 2)): sig * (sig - 1) / (r - 2 * m) ** 2,
                sp.Derivative(phi_f, r): sig / (r - 2 * m),
                phi_f: sp.Integer(1)}
    wave_sym = _cancel(wave.subs(subs_sig))
    comp_sym = {nm: _cancel(comp_conf[nm].subs(subs_sig)) for nm in ("a", "bc", "cc")}

    def rat_series(e, depth):
        num, den = sp.fraction(_cancel(e))
        pn = sp.Poly(sp.expand(num), rho)
        pd = sp.Poly(sp.expand(den), rho)
        n0 = min(mo[0] for mo in pn.monoms())
        d0 = min(mo[0] for mo in pd.monoms())
        den_shift = sp.Poly(sp.expand(sp.expand(den) / rho**d0), rho)
        dd0 = den_shift.coeff_monomial(1)
        inv = [sp.Integer(1) / dd0]
        for kk in range(1, depth + 1):
            acc = sum(den_shift.coeff_monomial(rho**jj) * inv[kk - jj]
                      for jj in range(1, kk + 1))
            inv.append(sp.cancel(-acc / dd0))
        res = {}
        for kk in range(depth + 1):
            acc = sum(pn.coeff_monomial(rho**(jj + n0)) * inv[kk - jj]
                      for jj in range(kk + 1))
            res[kk + n0 - d0] = sp.expand(acc)
        return res

    NORD = 5
    PK = min(rat_series(wave_sym.subs(r, 2 * m + rho), 2).keys())
    _require(PK == -1, f"wave leading Laurent slot {PK} != -1")

    def wave_series(s0):
        u = [sp.Integer(1)]
        for n in range(1, NORD + 1):
            acc = sp.Integer(0)
            for j in range(n):
                ser = rat_series(wave_sym.subs(sig, s0 + j).subs(r, 2 * m + rho), NORD + 2)
                acc += u[j] * ser.get(n + PK - j, sp.Integer(0))
            pivot = rat_series(wave_sym.subs(sig, s0 + n).subs(r, 2 * m + rho), 2)[PK]
            u.append(sp.cancel(-acc / pivot))
        return u

    def image_exponents(s0):
        u = wave_series(s0)
        outs = {}
        for nm in ("a", "bc", "cc"):
            tot = {}
            for n in range(NORD + 1):
                ser = rat_series(comp_sym[nm].subs(sig, s0 + n).subs(r, 2 * m + rho),
                                 NORD - n + 2)
                for kk, val in ser.items():
                    tot[n + kk] = sp.expand(tot.get(n + kk, 0) + u[n] * val)
            lead = None
            for kk in sorted(tot):
                if kk > NORD - 2:
                    break
                if sp.simplify(tot[kk]) != 0:
                    lead = kk
                    break
            _require(lead is not None, f"image component {nm} vanished to depth")
            outs[nm] = sp.simplify(s0 + lead)
        return outs

    img0 = image_exponents(sp.Integer(0))
    _require(all(sp.simplify(img0[nm]) == 0 for nm in img0),
             f"regular gauge image exponents {img0} != all 0")
    imgS = image_exponents(-4 * sp.I * m * w)
    _require(
        sp.simplify(imgS["a"] + 4 * sp.I * m * w) == 0
        and sp.simplify(imgS["bc"] + 4 * sp.I * m * w + 1) == 0
        and sp.simplify(imgS["cc"] + 4 * sp.I * m * w + 2) == 0,
        f"singular gauge image exponents {imgS} unexpected",
    )
    out["stage_seconds"]["gauge_exponents"] = round(time.time() - t0, 1)

    if light:
        out["syms"] = {"v": v, "r": r, "x": x, "m": m, "omega": w}
        out["funcs4"] = (ar, bcr, ccr, fr)
        out["cascade"] = {"D": D_c, "Ec": Ec_c, "G": G_c}
        out["rows"] = rows
        out["stage_seconds"]["total"] = round(time.time() - t0_all, 1)
        return out

    # ---- analytic-family fixtures (no log obstruction) --------------------
    # A degree-NFIX polynomial jet substituted into the (regular-coefficient)
    # second-order system produces series orders in which the absent tail
    # coefficient c_{j, NFIX+1} first enters at order NFIX; imposing all
    # orders <= NFIX-1 is therefore exact for genuine truncated solutions,
    # and the solution space must be exactly the 3-dim analytic family.
    t0 = time.time()
    NFIX = 6
    for (mv, wv) in [(sp.Integer(1), sp.Rational(3, 5)), (sp.Integer(1), sp.Rational(2, 7))]:
        coefs = {(j, n): sp.Symbol(f"c_{j}_{n}") for j in range(3) for n in range(NFIX + 1)}
        polys = [sum(coefs[(j, n)] * rho**n for n in range(NFIX + 1)) for j in range(3)]
        eqs = []
        for i in range(3):
            e = sys3[i].subs({m: mv, w: wv})
            for j, fn in enumerate(funcs3):
                e = e.subs({sp.Derivative(fn, (r, 2)): sp.diff(polys[j], rho, 2),
                            sp.Derivative(fn, r): sp.diff(polys[j], rho),
                            fn: polys[j]})
            e = _cancel(e.doit().subs(r, 2 * mv + rho))
            ser = rat_series(e, NFIX + 3)
            for kk in sorted(ser):
                if kk <= NFIX - 1:
                    eqs.append(ser[kk])
        unknowns = [coefs[k] for k in sorted(coefs)]
        Mlin, blin = sp.linear_eq_to_matrix(eqs, unknowns)
        _require(blin.norm() == 0, "fixture system inhomogeneous")
        nullity = len(unknowns) - Mlin.rank()
        _require(nullity == 3,
                 f"analytic family dimension {nullity} != 3 at omega={wv}")
    out["stage_seconds"]["analytic_fixtures"] = round(time.time() - t0, 1)
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
            "background_family": "Schwarzschild (symbolic m)",
            "conformal_frame": "working gauge; ingoing EF chart (v, r, x = cos theta, phi)",
            "generator": "not used; mode-level statements only",
            "phase_space": "none; no flux or pairing claim",
            "horizon_condition": "analyticity at r = 2m in the ingoing EF chart (future-horizon regularity)",
            "infinity_condition": "none imposed",
            "frequency_domain": "real omega != 0 (resonance-free case); omega = 0 not classified",
            "lifecycle": "CLASSIFIED",
        },
        "carrier": {
            "definition": "polar l=2 trace-coupled carrier (psi_ab, S = tr psi): harmonics P2, dP2, W = (3/2, -3(1-x^2)^2/2); components (vx), (rx), W-sector solved algebraically from the Bianchi cascade; free radial functions (a, bc, cc, f)",
            "equation": "(1/2) Box psi + C psi - (1/6) DD S - (1/12) g Box S = 0 (certified polar extra-branch operator, BH-2B stage 1)",
            "system_content": "exact identities g^{ab}E_ab = 0 and D^a E_ab = 0 plus the algebraic-solvability pattern reduce the 7 operator rows to the 3 rows (vv), (vr), (rr): 3 second-order equations in 4 functions",
            "gauge_structure": "the one-function underdeterminacy is linearized conformal gauge: psi_conf = -DD Phi - (1/2) g Box Phi annihilates all rows for arbitrary phi (Bach conformal covariance); verified exactly",
        },
        "horizon_analysis": {
            "slice": "traceless gauge S = 0 (algebraic: f = -bc - B0 cc / 2); principal part diagonalizes to the scalar wave operator",
            "singular_point": "r = 2m is a regular singular point of the 6-dim Fourier first-order system (rho^2 A -> 0 componentwise)",
            "indicial_exponents": ["0 (multiplicity 3)", "1 - 4*I*m*omega",
                                    "-1 - 4*I*m*omega", "-3 - 4*I*m*omega"],
            "zero_eigenspace": "geometric multiplicity 3: three analytic ingoing directions, no leading logarithm; polynomial Frobenius fixtures at omega = 3/5, 2/7 (m = 1) confirm a 3-dim analytic family with no log obstruction",
            "residual_gauge": "Box Phi = 0 in the slice; horizon exponents {0, -4*I*m*omega}; the regular gauge mode is a nonzero all-regular carrier direction, the singular gauge mode has component exponents (-4imw, -4imw-1, -4imw-2)",
            "physical_family": "analytic family (3-dim) modulo the regular conformal-gauge direction (1-dim): a TWO-parameter physical ingoing-regular polar extra-branch family at every real omega != 0",
            "conclusion": "the polar extra branch reaches the future horizon; horizon regularity cannot exclude it in either parity sector of l = 2",
        },
        "claim_flags": {
            "bianchi_cascade_certified": True,
            "operator_identity_reduction_certified": True,
            "conformal_gauge_identity_certified": True,
            "regular_singular_point_certified": True,
            "indicial_exponents_certified": True,
            "ingoing_family_dimension_certified": True,
            "gauge_quotient_certified": True,
            "flux_or_sign_certified": False,
            "zerilli_benchmark_certified": False,
            "outer_boundary_domain_certified": False,
            "causal_exclusion_decided": False,
            "growth_or_stability_certified": False,
            "general_l_certified": False,
            "omega_zero_classified": False,
            "non_einstein_background_certified": False,
        },
        "missing_objects": [
            "polar bilinear symplectic flux matrix and Lee-Wald signs",
            "Zerilli/Einstein-branch polar benchmark (must be derived by ansatz fitting, not imported)",
            "outer-boundary operator domains and falloff classification (polar)",
            "causal disposition of the polar extra branch",
            "growth/stability data; general l; omega = 0 static sector",
            "polar horizon analysis on non-Einstein backgrounds",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2b_polar_reach.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "bh2b_split_certificate": str(BH2B_SPLIT_CERT.relative_to(ROOT)),
            "bh2b_split_certificate_sha256": _sha256(BH2B_SPLIT_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2b_polar_reach.py",
    }
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    certificate = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
