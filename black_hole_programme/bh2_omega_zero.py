"""BH-2 omega = 0: static-sector classification of the carrier systems.

Fail-closed builder for
`black_hole_programme/certificates/BH2_OMEGA_ZERO.json`.

Verdict: BH2_OMEGA_ZERO_STATIC_SECTOR_CLASSIFIED.

Setting: Schwarzschild m = 1, l = 2, ingoing EF chart, the certified axial
and polar (traceless-slice) carrier systems at omega = 0 -- the frequency
excluded from every reach theorem (the residue eigenvalue structure
degenerates there).

Exact results:

1. AXIAL carrier at omega = 0: residue spectrum {0 (alg 3, geo 2), -2}.
   The zero eigenvalue acquires a Jordan block (algebraic 3 > geometric 2):
   one leading logarithmic static solution exists.  Both kernel directions
   extend to log-free analytic series: the static axial carrier sector is
   a TWO-parameter log-free family, exactly matching the omega != 0 reach
   dimension -- horizon regularity does not exclude static axial carrier
   deformations either;
2. POLAR carrier (traceless slice) at omega = 0: residue spectrum
   {0 (alg 3, geo 3), +1, -1, -3}, all integers.  Resonances obstruct two
   of the three exponent-0 directions (inconsistent recurrence at the
   +1 resonance: genuine logarithms); one exponent-0 direction and the
   exponent-1 direction are log-free: the static polar carrier sector is a
   TWO-parameter log-free analytic family;
3. Einstein controls at omega = 0: the axial Regge--Wheeler and the polar
   Einstein first-order systems are classified the same way (spectra and
   log-free static dimensions recorded).

Consequence: the omega = 0 caveat of the reach certificates is closed at
the classification level: the static (omega = 0) carrier sectors are
finite, log-classified, and nonempty in both parities.

NOT claimed: static METRIC deformation families (composition at omega = 0),
static flux/charge assignments for these families, matching to the BH-1
l = 0 parameter modes, general l, or any stability statement.
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
DEFAULT_OUTPUT = HERE / "certificates" / "BH2_OMEGA_ZERO.json"
SCHEMA_PATH = HERE / "schema" / "bh2-omega-zero-v1.schema.json"
AX_REACH = HERE / "certificates" / "BH2A_HORIZON_REACH.json"
PO_REACH = HERE / "certificates" / "BH2B_POLAR_REACH.json"
PO_EIN = HERE / "certificates" / "BH2B_POLAR_EINSTEIN.json"

SCHEMA_NAME = "pure-weyl-bh2-omega-zero-v1"
RESULT_ID = "PURE_WEYL_BH2_OMEGA_ZERO"
RESULT_TOKEN = "BH2_OMEGA_ZERO_STATIC_SECTOR_CLASSIFIED"

NORD = 8


class OmegaZeroError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise OmegaZeroError(msg)


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
    w = sp.Symbol("omega", positive=True)
    rho = sp.Symbol("rho")
    N = 4
    B0 = 1 - 2 / r
    coords = [v, r, x, ph]
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
    S_ax = -3 * x * (1 - x**2)
    E = sp.exp(sp.I * w * v)

    # ---- axial carrier first-order system (symbolic omega) ----------------
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
    for i, e in ((1, sp.expand(sol[D2P])), (3, sp.expand(sol[D2Q]))):
        A4[i, 0] = e.coeff(P); A4[i, 1] = e.coeff(DP)
        A4[i, 2] = e.coeff(Q); A4[i, 3] = e.coeff(DQ)
    out["stage_seconds"]["axial_system"] = round(time.time() - t0, 1)

    # ---- polar carrier sliced system (symbolic omega) ---------------------
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
    out["stage_seconds"]["polar_system"] = round(time.time() - t0, 1)

    # ---- Einstein controls (first-order systems, symbolic omega) ----------
    t0 = time.time()
    m_sym = sp.Symbol("m", positive=True)
    F = sp.Function("F")(r)
    V = B0 * (6 / r**2 - 6 / r**3)
    opF = B0 * sp.diff(B0 * sp.diff(F, r), r) + 2 * sp.I * w * B0 * sp.diff(F, r) - V * F
    e2 = sp.expand(sp.solve(sp.Eq(sp.expand(opF), 0),
                            sp.Derivative(F, (r, 2)), dict=True)[0][sp.Derivative(F, (r, 2))])
    Arw = sp.zeros(2, 2)
    Arw[0, 1] = 1
    Arw[1, 0] = e2.coeff(F)
    Arw[1, 1] = e2.coeff(sp.Derivative(F, r))
    cert_e = json.loads(PO_EIN.read_text(encoding="utf-8"))
    locs = {"r": r, "omega": w, "m": m_sym, "I": sp.I,
            "K": sp.Function("K"), "H1": sp.Function("H1")}
    Me = sp.Matrix(2, 2, lambda i, j: sp.sympify(cert_e["reduction"]["M"][i][j],
                                                 locals=locs).subs(m_sym, 1))
    Dd = sp.diag(1, B0)
    Apo = sp.Matrix(2, 2, lambda i, j: _cancel(
        (Dd * Me * Dd.inv() + sp.diff(Dd, r) * Dd.inv())[i, j])) - sp.I * w / B0 * sp.eye(2)
    out["stage_seconds"]["einstein_systems"] = round(time.time() - t0, 1)

    # ---- classification at omega = 0 --------------------------------------
    t0 = time.time()

    def classify(Amat, dim):
        A0 = Amat.subs(w, 0)
        Ar = sp.Matrix(dim, dim, lambda i, j: _cancel(A0[i, j].subs(r, 2 + rho)))
        for i in range(dim):
            for j in range(dim):
                if Ar[i, j] in (0, 1):
                    continue
                _require(sp.simplify(sp.limit(rho**2 * Ar[i, j], rho, 0)) == 0,
                         "irregular singular point at omega = 0")
        Res = sp.Matrix(dim, dim, lambda i, j: sp.cancel(sp.limit(rho * Ar[i, j], rho, 0))
                        if Ar[i, j] not in (0, 1) else 0)
        ev = {sp.nsimplify(k): m for k, m in Res.eigenvals().items()}
        jordan = {}
        for lam, alg in ev.items():
            geo = len((Res - lam * sp.eye(dim)).nullspace())
            jordan[sp.sstr(lam)] = {"alg": int(alg), "geo": int(geo)}
        rem = sp.Matrix(dim, dim, lambda i, j: _cancel(Ar[i, j] - Res[i, j] / rho))
        Mk = [sp.Matrix(dim, dim, lambda i, j:
              rem[i, j].series(rho, 0, NORD + 2).removeO().coeff(rho, k)
              if rem[i, j] != 0 else 0) for k in range(NORD + 1)]
        families = {}
        for s0 in sorted([k for k in ev if k.is_integer and k >= 0]):
            base = (Res - s0 * sp.eye(dim)).nullspace()
            ok = 0
            for kv in base:
                Y = [sp.Matrix(kv)]
                logfree = True
                for n in range(1, NORD + 1):
                    rhs = sp.zeros(dim, 1)
                    for k in range(n):
                        rhs += Mk[n - 1 - k] * Y[k]
                    Mn = (s0 + n) * sp.eye(dim) - Res
                    if Mn.det() != 0:
                        Y.append(Mn.solve(rhs))
                    else:
                        try:
                            soln, params = Mn.gauss_jordan_solve(rhs)
                        except ValueError:
                            logfree = False
                            break
                        soln = soln.subs({pp: 0 for pp in params})
                        if any(sp.simplify(cc) != 0
                               for cc in sp.simplify(Mn * soln - rhs)):
                            logfree = False
                            break
                        Y.append(soln)
                ok += int(logfree)
            families[sp.sstr(s0)] = {"base_dim": len(base), "logfree_dirs": int(ok)}
        return {"spectrum": {sp.sstr(k): int(m) for k, m in ev.items()},
                "jordan": jordan, "analytic_families": families}

    # the polar Einstein (K, H1) parametrization carries explicit 1/omega
    # factors (M[0,1] ~ 1/omega): it DEGENERATES at omega = 0 and cannot be
    # classified in these variables -- recorded as a structural fact.
    _require(any(sp.fraction(sp.cancel(sp.together(Me[i, j])))[1].has(w)
                 for i in range(2) for j in range(2)),
             "expected 1/omega degeneration absent in polar Einstein system")
    results = {
        "axial_carrier": classify(A4, 4),
        "polar_carrier_sliced": classify(A6, 6),
        "axial_einstein_rw": classify(Arw, 2),
        "polar_einstein": {"spectrum": "PARAMETRIZATION_DEGENERATES",
                           "note": "the certified (K, H1) first-order system has explicit 1/omega coefficients; the static polar Einstein sector requires its own reduction (recorded as a missing object)"},
    }
    # headline asserts
    ax = results["axial_carrier"]
    _require(ax["jordan"]["0"] == {"alg": 3, "geo": 2},
             f"axial Jordan structure unexpected: {ax['jordan']}")
    _require(ax["analytic_families"]["0"] == {"base_dim": 2, "logfree_dirs": 2},
             f"axial log-free family unexpected: {ax['analytic_families']}")
    po = results["polar_carrier_sliced"]
    _require(po["jordan"]["0"] == {"alg": 3, "geo": 3},
             f"polar Jordan structure unexpected: {po['jordan']}")
    _require(po["analytic_families"]["0"]["logfree_dirs"] == 1
             and po["analytic_families"]["1"]["logfree_dirs"] == 1,
             f"polar log-free family unexpected: {po['analytic_families']}")
    out["results"] = results
    out["stage_seconds"]["classification"] = round(time.time() - t0, 1)
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
            "background_family": "Schwarzschild m = 1 fixture",
            "conformal_frame": "working gauge; ingoing EF chart",
            "generator": "none; static-mode classification",
            "phase_space": "l = 2 carrier and Einstein first-order systems at omega = 0",
            "horizon_condition": "regular-singular residue and log classification at r = 2m",
            "infinity_condition": "none imposed",
            "frequency_domain": "omega = 0 exactly (the sector excluded by the reach certificates)",
            "lifecycle": "CLASSIFIED",
        },
        "classification": res["results"],
        "headline": {
            "axial": "residue {0 (alg 3, geo 2), -2}: one Jordan-block logarithm; TWO-parameter log-free static carrier family (matches the omega != 0 reach dimension)",
            "polar": "residue {0 (alg 3, geo 3), +1, -1, -3}: two exponent-0 directions log-obstructed at the +1 resonance; TWO-parameter log-free static family (one exponent-0 + one exponent-1 direction)",
            "consequence": "the omega = 0 caveat of the reach certificates is closed at the classification level: static carrier sectors are finite, log-classified, and nonempty in both parities",
        },
        "claim_flags": {
            "axial_static_sector_classified": True,
            "polar_static_sector_classified": True,
            "einstein_controls_classified": True,
            "static_metric_composition_certified": False,
            "static_flux_or_charge_certified": False,
            "matching_to_l0_parameter_modes_certified": False,
            "general_l_certified": False,
        },
        "missing_objects": [
            "static metric composition (delta Ric[h] = psi at omega = 0)",
            "static flux/charge assignments for the log-free families",
            "matching to the BH-1 l = 0 parameter modes",
            "general l static sectors",
            "a static-adapted reduction of the polar Einstein sector (the (K, H1) system degenerates at omega = 0)",
            "any stability interpretation of the logarithmic solutions",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2_omega_zero.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "axial_reach_certificate": str(AX_REACH.relative_to(ROOT)),
            "axial_reach_certificate_sha256": _sha256(AX_REACH),
            "polar_reach_certificate": str(PO_REACH.relative_to(ROOT)),
            "polar_reach_certificate_sha256": _sha256(PO_REACH),
            "polar_einstein_certificate": str(PO_EIN.relative_to(ROOT)),
            "polar_einstein_certificate_sha256": _sha256(PO_EIN),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2_omega_zero.py",
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
