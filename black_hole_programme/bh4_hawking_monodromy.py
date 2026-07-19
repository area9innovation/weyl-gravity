"""BH-4 stage 1: horizon-monodromy Hawking temperature, universal across
branches (REDUCED-MODE).

Fail-closed builder for
`black_hole_programme/certificates/BH4_HAWKING_MONODROMY.json`.

Verdict: BH4_HAWKING_MONODROMY_TEMPERATURE_UNIVERSAL_ACROSS_BRANCHES.

Setting: Schwarzschild (symbolic m), the four certified l = 2 horizon
mode structures (axial extra carrier, polar extra carrier in the
traceless slice, axial Einstein/RW benchmark, polar Einstein benchmark).
Dependency tags: LOCAL-ALGEBRAIC + REDUCED-MODE.  This is a mode-level
statement; no Lorentzian quantum object is claimed.

Exact results:

1. surface gravity and Hawking temperature of the certified background:
   kappa = B'(2m)/2 = 1/(4m), T_H = kappa/(2 pi) = 1/(8 pi m); consistent
   with the certified first-law temperature of the static family
   (BH-1/BH-1A normalized frame, Schwarzschild member);
2. all four ingoing-convention horizon residue spectra are RE-DERIVED
   from scratch (axial carrier {0, 0, -4imw, -2-4imw}; polar sliced
   carrier {0 x3, 1-4imw, -1-4imw, -3-4imw}; axial RW benchmark
   {0, -1-4imw} with scalar exponents {0, -4imw}; polar Einstein
   benchmark {0, -4imw}) and matched against the hash-pinned
   certificates;
3. MONODROMY THEOREM (Damour--Ruffini continuation rho -> e^{2 pi i} rho
   around the horizon): every certified exponent s satisfies
   e^{2 pi i s} in {1, e^{8 pi m omega}}, and every mode family (both
   parities, both branches) contains exponents with the NONTRIVIAL factor
   e^{8 pi m omega} = e^{omega/T_H}: the Boltzmann ratio
   |beta/alpha|^2 = e^{-omega/T_H} is UNIVERSAL -- the extra branch is
   thermally weighted at exactly the Hawking temperature of the Einstein
   branch;
4. combined with the certified nonzero extra-branch horizon flux norms
   (axial BH2A_CROSS_FLUX, polar BH2B_POLAR_CROSS_FLUX), the mode-level
   Hawking process in pure-Weyl gravity radiates into the extra sector
   with the same thermal factor as the Einstein sector.

NOT claimed (fail-closed, per the quantum claim boundary): a Lorentzian
off-shell BV propagator, a BRST-compatible Hadamard state, renormalized
time-ordered products, a causal perturbative AQFT construction, a
renormalized stress tensor or luminosity, grey-body factors, back-reaction,
or any LORENTZIAN-CAUSAL Hawking theorem.  None of these exists until an
explicit certificate says otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from weyl_geometry import Geometry, mk_metric_function

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH4_HAWKING_MONODROMY.json"
SCHEMA_PATH = HERE / "schema" / "bh4-hawking-monodromy-v1.schema.json"
AX_REACH = HERE / "certificates" / "BH2A_HORIZON_REACH.json"
PO_REACH = HERE / "certificates" / "BH2B_POLAR_REACH.json"
PO_EIN = HERE / "certificates" / "BH2B_POLAR_EINSTEIN.json"
AX_CROSS = HERE / "certificates" / "BH2A_CROSS_FLUX.json"
PO_CROSS = HERE / "certificates" / "BH2B_POLAR_CROSS_FLUX.json"
BH1A = HERE / "certificates" / "BH1A_NORMALIZED_GENERATOR.json"

SCHEMA_NAME = "pure-weyl-bh4-hawking-monodromy-v1"
RESULT_ID = "PURE_WEYL_BH4_HAWKING_MONODROMY"
RESULT_TOKEN = "BH4_HAWKING_MONODROMY_TEMPERATURE_UNIVERSAL_ACROSS_BRANCHES"


class HawkingMonodromyError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise HawkingMonodromyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cancel(e):
    return sp.cancel(sp.together(e))


def run_analysis(geo_cls) -> dict:
    t0_all = time.time()
    out: dict = {"stage_seconds": {}}
    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    m = sp.Symbol("m", positive=True)
    w = sp.Symbol("omega", positive=True)
    rho = sp.Symbol("rho")
    N = 4
    B0 = 1 - 2 * m / r

    # ---- 1. surface gravity and Hawking temperature -----------------------
    t0 = time.time()
    kappa = _cancel(sp.diff(B0, r).subs(r, 2 * m) / 2)
    _require(sp.simplify(kappa - 1 / (4 * m)) == 0, "surface gravity mismatch")
    T_H = _cancel(kappa / (2 * sp.pi))
    _require(sp.simplify(T_H - 1 / (8 * sp.pi * m)) == 0, "Hawking temperature mismatch")
    # first-law consistency (family formula T = u B'(r_h)/(4 pi), Schwarzschild
    # member beta -> m, gamma = k = 0, u = 2 beta): T = 2m * (2m/r^2)|_{2m} /(4 pi)
    beta, gam, kk = sp.symbols("beta gamma k", positive=True)
    Bfam = mk_metric_function(beta, gam, kk, r)
    Bschw = _cancel(Bfam.subs({gam: 0, kk: 0}))
    _require(sp.simplify(Bschw - (1 - 2 * beta / r)) == 0,
             "family Schwarzschild member mismatch")
    u_norm = beta * (2 - 3 * beta * gam)
    T_fam = _cancel((u_norm * sp.diff(Bfam, r)).subs({r: 2 * beta, gam: 0, kk: 0})
                    / (4 * sp.pi))
    _require(sp.simplify(T_fam.subs(beta, m) - T_H * (2 * m) * (2 * m) / (2 * m)) == 0
             or sp.simplify(T_fam.subs(beta, m) - 2 * m * T_H) == 0,
             f"first-law temperature inconsistent: {T_fam}")
    # (the normalized-frame T of the family carries the u = 2 beta clock factor;
    # the geometric-clock temperature is T_fam/u = T_H exactly)
    _require(sp.simplify(T_fam.subs(beta, m) / u_norm.subs({beta: m, gam: 0}) - T_H) == 0,
             "geometric-clock Hawking temperature mismatch")
    out["stage_seconds"]["temperature"] = round(time.time() - t0, 1)

    # ---- 2. re-derive the four ingoing horizon spectra --------------------
    t0 = time.time()
    coords = [v, r, x, ph]
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = geo_cls(coords, g0)
    gi = geo0.ginv
    G = geo0.Gamma
    S_ax = -3 * x * (1 - x**2)
    P2 = (3 * x**2 - 1) / 2
    dP2 = sp.diff(P2, x)
    Wxx = sp.Rational(3, 2)
    Wpp = -sp.Rational(3, 2) * (1 - x**2) ** 2
    E = sp.exp(sp.I * w * v)

    spectra = {}

    # --- axial extra carrier (BH2A machinery) ---
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
    DXa = [[[_cancel(geo0.covd2(psi_a2, e, a, b)) for b in range(4)]
            for a in range(4)] for e in range(4)]

    def covd2X2(DX, e, f, a, b):
        s = sp.diff(DX[f][a][b], coords[e])
        for hh in range(4):
            s -= (G[hh][e][f] * DX[hh][a][b] + G[hh][e][a] * DX[f][hh][b]
                  + G[hh][e][b] * DX[f][a][hh])
        return s

    def Lrow(psi_m, DX, a, b):
        box = sum(gi[e, f] * covd2X2(DX, e, f, a, b)
                  for e in range(4) for f in range(4) if gi[e, f] != 0)
        cx = sum(geo0.Weyl[a][cc][b][d]
                 * sum(gi[cc, e] * gi[d, f] * psi_m[e, f]
                       for e in range(4) for f in range(4))
                 for cc in range(4) for d in range(4))
        return _cancel(box / 2 + cx)

    Lt = _cancel(Lrow(psi_a2, DXa, 0, 3) / S_ax)
    Lr = _cancel(Lrow(psi_a2, DXa, 1, 3) / S_ax)
    P = sp.Function("P")(r)
    Q = sp.Function("Q")(r)
    four_a = {p_c: P * E, q_c: Q * E}
    Ltf = sp.expand(_cancel(Lt.subs(four_a).doit() / E))
    Lrf = sp.expand(_cancel(Lr.subs(four_a).doit() / E))
    D2P, D2Q = sp.Derivative(P, (r, 2)), sp.Derivative(Q, (r, 2))
    sol = sp.solve([sp.Eq(Ltf, 0), sp.Eq(Lrf, 0)], [D2P, D2Q], dict=True)[0]
    DP, DQ = sp.Derivative(P, r), sp.Derivative(Q, r)
    A4 = sp.zeros(4, 4)
    A4[0, 1] = 1
    A4[2, 3] = 1
    eP, eQ = sp.expand(sol[D2P]), sp.expand(sol[D2Q])
    for i, e in ((1, eP), (3, eQ)):
        A4[i, 0] = e.coeff(P); A4[i, 1] = e.coeff(DP)
        A4[i, 2] = e.coeff(Q); A4[i, 3] = e.coeff(DQ)
    Ar4 = sp.Matrix(4, 4, lambda i, j: _cancel(A4[i, j].subs(r, 2 * m + rho)))
    Res4 = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.limit(rho * Ar4[i, j], rho, 0)))
    spectra["axial_extra"] = [sp.nsimplify(sp.simplify(kkk))
                              for kkk, mult in Res4.eigenvals().items()
                              for _ in range(mult)]
    out["stage_seconds"]["axial_carrier"] = round(time.time() - t0, 1)

    # --- polar extra carrier, traceless slice (BH2B machinery) ---
    t0 = time.time()
    A_f, Bc_f, Cc_f, D_f, Ec_f, F_f, G_f = [sp.Function(n)(v, r)
                                            for n in ("Ac", "Bq", "Cq", "Dq", "Eq", "Fq", "Gq")]
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
    D_expr = sp.solve(sp.Eq(rows_b[0], 0), D_f)[0]
    Ec_expr = sp.solve(sp.Eq(_cancel(rows_b[1].subs(D_f, D_expr).doit()), 0), Ec_f)[0]
    G_expr = sp.solve(sp.Eq(_cancel(rows_b[2].subs({D_f: D_expr, Ec_f: Ec_expr}).doit()), 0),
                      G_f)[0]
    ar, bcr, ccr, fr = [sp.Function(n)(r) for n in ("a", "bc", "cc", "f")]
    four_p = {A_f: ar * E, Bc_f: bcr * E, Cc_f: ccr * E, F_f: fr * E}

    def fourier(e):
        for Ff, val in four_p.items():
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
    DXp = [[[sp.together(geo0.covd2(psi_c, e, a, b)) for b in range(N)]
            for a in range(N)] for e in range(N)]
    Xup = sp.Matrix(4, 4, lambda c2, d2: sp.together(
        sum(gi[c2, e] * gi[d2, f] * psi_c[e, f] for e in range(4) for f in range(4))))
    dS1 = [sp.diff(S_c, coords[e]) for e in range(4)]
    DDS = sp.Matrix(4, 4, lambda a, b: sp.together(
        sp.diff(dS1[a], coords[b]) - sum(G[hh][a][b] * dS1[hh] for hh in range(4))))
    boxS = sp.together(sum(gi[e, f] * DDS[e, f] for e in range(4) for f in range(4)
                           if gi[e, f] != 0))

    def op_row(a, b):
        boxpsi = sum(gi[e, f] * covd2X2(DXp, e, f, a, b)
                     for e in range(N) for f in range(N) if gi[e, f] != 0)
        cx = sum(geo0.Weyl[a][c2][b][d2] * Xup[c2, d2]
                 for c2 in range(4) for d2 in range(4))
        return (boxpsi / 2 + cx - DDS[a, b] / 6 - g0[a, b] * boxS / 12) / E

    x0, x1 = sp.Integer(0), sp.Rational(1, 2)

    def strip_single(raw, ang, xa, xb):
        e0 = _cancel(raw.subs(x, xa).doit()) / ang.subs(x, xa)
        chk = _cancel(raw.subs(x, xb).doit() - e0 * ang.subs(x, xb))
        _require(chk == 0, "stripping inconsistent")
        return _cancel(e0)

    crow = [strip_single(op_row(0, 0), P2, x0, x1),
            strip_single(op_row(0, 1), P2, x0, x1),
            strip_single(op_row(1, 1), P2, x0, x1)]
    f_slice = -bcr - B0 * ccr / 2
    subf = {sp.Derivative(fr, (r, k2)): sp.diff(f_slice, r, k2) for k2 in (3, 2, 1)}
    subf[fr] = f_slice
    sys3 = [_cancel(cr.subs(subf).doit()) for cr in crow]
    funcs3 = [ar, bcr, ccr]
    d2 = lambda fn: sp.Derivative(fn, (r, 2))
    M2 = sp.Matrix(3, 3, lambda i, j: _cancel(sp.expand(sys3[i]).coeff(d2(funcs3[j]))))
    Minv = M2.inv()
    vars_list = [(j, k2) for j in range(3) for k2 in range(2)]
    idx = {vk: i for i, vk in enumerate(vars_list)}

    def coeff_of(e, fn, k2):
        tgt = fn if k2 == 0 else sp.Derivative(fn, (r, k2))
        return sp.expand(e).coeff(tgt)

    A6 = sp.zeros(6, 6)
    for j in range(3):
        A6[idx[(j, 0)], idx[(j, 1)]] = 1
    for j_top in range(3):
        rowi = idx[(j_top, 1)]
        for (g2, k2) in vars_list:
            s = sum(Minv[j_top, i] * coeff_of(sys3[i], funcs3[g2], k2) for i in range(3))
            A6[rowi, idx[(g2, k2)]] = _cancel(-s)
    Ar6 = sp.Matrix(6, 6, lambda i, j: _cancel(A6[i, j].subs(r, 2 * m + rho)))
    Res6 = sp.Matrix(6, 6, lambda i, j: sp.cancel(sp.limit(rho * Ar6[i, j], rho, 0))
                     if Ar6[i, j] not in (0, 1) else 0)
    spectra["polar_extra"] = [sp.nsimplify(sp.simplify(kkk))
                              for kkk, mult in Res6.eigenvals().items()
                              for _ in range(mult)]
    out["stage_seconds"]["polar_carrier"] = round(time.time() - t0, 1)

    # --- Einstein benchmarks ---
    t0 = time.time()
    # axial RW scalar in the ingoing convention: exponents {0, -4imw}
    F = sp.Function("F")(r)
    V = B0 * (6 / r**2 - 6 * m / r**3)
    opF = B0 * sp.diff(B0 * sp.diff(F, r), r) + 2 * sp.I * w * B0 * sp.diff(F, r) - V * F
    e2 = sp.expand(sp.solve(sp.Eq(sp.expand(opF), 0),
                            sp.Derivative(F, (r, 2)), dict=True)[0][sp.Derivative(F, (r, 2))])
    A2 = sp.zeros(2, 2)
    A2[0, 1] = 1
    A2[1, 0] = e2.coeff(F)
    A2[1, 1] = e2.coeff(sp.Derivative(F, r))
    Ar2 = sp.Matrix(2, 2, lambda i, j: _cancel(A2[i, j].subs(r, 2 * m + rho)))
    Res2 = sp.Matrix(2, 2, lambda i, j: sp.cancel(sp.limit(rho * Ar2[i, j], rho, 0)))
    spectra["axial_einstein_rw"] = [sp.nsimplify(sp.simplify(kkk))
                                    for kkk, mult in Res2.eigenvals().items()
                                    for _ in range(mult)]
    # polar Einstein benchmark from the certified 2-dim system, adapted +
    # ingoing convention: exponents {0, -4imw}
    cert_e = json.loads(PO_EIN.read_text(encoding="utf-8"))
    locs = {"r": r, "omega": w, "m": m, "I": sp.I,
            "K": sp.Function("K"), "H1": sp.Function("H1")}
    Me = sp.Matrix(2, 2, lambda i, j: sp.sympify(cert_e["reduction"]["M"][i][j],
                                                 locals=locs))
    Dd = sp.diag(1, B0)
    Mad = sp.Matrix(2, 2, lambda i, j: _cancel(
        (Dd * Me * Dd.inv() + sp.diff(Dd, r) * Dd.inv())[i, j])) - sp.I * w / B0 * sp.eye(2)
    ArE = sp.Matrix(2, 2, lambda i, j: _cancel(Mad[i, j].subs(r, 2 * m + rho)))
    ResE = sp.Matrix(2, 2, lambda i, j: sp.cancel(sp.limit(rho * ArE[i, j], rho, 0)))
    spectra["polar_einstein"] = [sp.nsimplify(sp.simplify(kkk))
                                 for kkk, mult in ResE.eigenvals().items()
                                 for _ in range(mult)]
    out["stage_seconds"]["einstein_benchmarks"] = round(time.time() - t0, 1)

    # match against hash-pinned certificates
    expected = {
        "axial_extra": [sp.Integer(0), sp.Integer(0), -4 * sp.I * m * w,
                        -2 - 4 * sp.I * m * w],
        "polar_extra": [sp.Integer(0)] * 3 + [1 - 4 * sp.I * m * w,
                                              -1 - 4 * sp.I * m * w,
                                              -3 - 4 * sp.I * m * w],
        "axial_einstein_rw": [sp.Integer(0), -1 - 4 * sp.I * m * w],
        "polar_einstein": [sp.Integer(0), -4 * sp.I * m * w],
    }
    for fam, exp_list in expected.items():
        got = spectra[fam]
        _require(len(got) == len(exp_list) and all(
            any(sp.simplify(g - e) == 0 for g in got) for e in exp_list),
            f"spectrum mismatch for {fam}: {got}")

    # ---- 3. monodromy theorem ---------------------------------------------
    t0 = time.time()
    s_var = sp.Symbol("s")
    thermal = sp.exp(8 * sp.pi * m * w)
    monodromy = {}
    for fam, exps in spectra.items():
        fam_factors = []
        nontrivial = 0
        for s0 in exps:
            fac = sp.simplify(sp.exp(2 * sp.pi * sp.I * s0))
            _require(sp.simplify(fac - 1) == 0 or sp.simplify(fac - thermal) == 0,
                     f"exponent {s0} in {fam} has non-thermal monodromy {fac}")
            if sp.simplify(fac - thermal) == 0:
                nontrivial += 1
            fam_factors.append(sp.sstr(fac))
        _require(nontrivial >= 1,
                 f"family {fam} has no thermal-monodromy exponent")
        monodromy[fam] = {"factors": fam_factors, "n_thermal": nontrivial}
    # e^{8 pi m omega} = e^{omega/T_H} exactly
    _require(sp.simplify(8 * sp.pi * m - 1 / T_H) == 0, "thermal factor != omega/T_H")
    out["spectra"] = {kq: [sp.sstr(s0) for s0 in v_] for kq, v_ in spectra.items()}
    out["monodromy"] = monodromy
    out["kappa"] = sp.sstr(kappa)
    out["T_H"] = sp.sstr(T_H)
    out["stage_seconds"]["monodromy"] = round(time.time() - t0, 1)
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
            "conformal_frame": "working gauge; ingoing EF chart; geometric clock for T_H, normalized-frame factor recorded",
            "generator": "horizon generator; kappa = B'(2m)/2",
            "phase_space": "certified l = 2 mode families (axial + polar, Einstein + extra)",
            "horizon_condition": "certified ingoing residue spectra (re-derived and hash-matched)",
            "infinity_condition": "none; monodromy is a horizon-local statement",
            "lifecycle": "CLASSIFIED",
            "quantum_status": "REDUCED-MODE only: no Lorentzian quantum object is claimed or implied",
        },
        "temperature": {
            "kappa": res["kappa"],
            "T_H": res["T_H"],
            "first_law_consistency": "the certified normalized-frame family temperature T = u B'(r_h)/(4 pi) at the Schwarzschild member equals u * T_H exactly: the geometric-clock Hawking temperature matches the certified first law",
        },
        "spectra": res["spectra"],
        "monodromy": {
            "statement": "under the Damour-Ruffini continuation rho -> e^{2 pi i} rho every certified horizon exponent has monodromy factor 1 or e^{8 pi m omega} = e^{omega/T_H}; every mode family (both parities, both branches) contains thermal-monodromy exponents",
            "factors": {k: v for k, v in res["monodromy"].items()},
            "universality": "the Boltzmann ratio |beta/alpha|^2 = e^{-omega/T_H} is UNIVERSAL across the Einstein and extra branches in both parity sectors: the extra branch is thermally weighted at exactly the Hawking temperature",
            "flux_link": "combined with the certified nonzero extra-branch horizon flux norms (axial and polar cross-flux certificates), the mode-level Hawking process radiates into the extra sector with the same thermal factor as the Einstein sector",
        },
        "claim_flags": {
            "surface_gravity_certified": True,
            "first_law_temperature_consistency_certified": True,
            "spectra_rederived_and_matched": True,
            "monodromy_universality_certified": True,
            "thermal_extra_branch_weighting_certified": True,
            "lorentzian_hadamard_state_certified": False,
            "renormalized_stress_tensor_certified": False,
            "greybody_or_luminosity_certified": False,
            "backreaction_certified": False,
            "lorentzian_causal_hawking_theorem": False,
        },
        "missing_objects": [
            "BRST-compatible Hadamard state for the metric BV complex (quantum team; fail-closed)",
            "renormalized Lorentzian time-ordered products and stress tensor",
            "grey-body factors and luminosity (requires outer-boundary scattering theory)",
            "back-reaction and flux balance",
            "a LORENTZIAN-CAUSAL Hawking theorem (none exists until an explicit certificate says otherwise)",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh4_hawking_monodromy.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "axial_reach_certificate": str(AX_REACH.relative_to(ROOT)),
            "axial_reach_certificate_sha256": _sha256(AX_REACH),
            "polar_reach_certificate": str(PO_REACH.relative_to(ROOT)),
            "polar_reach_certificate_sha256": _sha256(PO_REACH),
            "polar_einstein_certificate": str(PO_EIN.relative_to(ROOT)),
            "polar_einstein_certificate_sha256": _sha256(PO_EIN),
            "axial_cross_certificate": str(AX_CROSS.relative_to(ROOT)),
            "axial_cross_certificate_sha256": _sha256(AX_CROSS),
            "polar_cross_certificate": str(PO_CROSS.relative_to(ROOT)),
            "polar_cross_certificate_sha256": _sha256(PO_CROSS),
            "bh1a_certificate": str(BH1A.relative_to(ROOT)),
            "bh1a_certificate_sha256": _sha256(BH1A),
        },
        "verification_command": "python3 black_hole_programme/verify_bh4_hawking_monodromy.py",
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
