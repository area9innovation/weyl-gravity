"""BH-2C stage 1: asymptotic formal structure -- no Jordan logarithms.

Fail-closed builder for
`black_hole_programme/certificates/BH2C_ASYMPTOTIC_JORDAN.json`.

Verdict: BH2C_ASYMPTOTIC_FORMAL_SYSTEM_LOG_FREE_BOTH_PARITIES.

Setting: Schwarzschild m = 1, l = 2, the certified axial and polar
(traceless-slice) carrier systems at the irregular point r -> infinity.
The repeated-root problem flagged by Paper 14 ("first-order matrix and
Jordan form") is the question whether the integer-spaced exponents within
each characteristic sector force log r terms in the formal fundamental
system.

Exact results:

1. AXIAL (symbolic real omega): the two exponential sectors
   mu in {0, -2 omega} (t-chart lam = +-omega) have sigma-roots
   {0, -1} and {-4 i omega, -4 i omega - 1}: integer resonance of gap 1
   in each sector.  Constructing the formal series from the top sigma of
   each sector, the resonance is CONSISTENT in both sectors: the axial
   carrier has a LOG-FREE four-dimensional formal fundamental system
   e^{i mu r} r^sigma (series in 1/r);
2. POLAR mu = 0 sector (symbolic real omega): the jet system of window
   depth 6 from sigma_0 = -1 has nullity 6 with leading-matrix kernel 3
   (pure tail freedom): exactly THREE genuine log-free formal solutions
   (exponents -1, -2, -3), the full sector dimension;
3. POLAR mu = -2 omega sector (rational fixtures omega = 3/5 and 2/7):
   the same count gives THREE genuine log-free solutions (exponents
   -4 i omega - {1, 2, 3}), the full sector dimension.

Consequence: the formal fundamental systems at infinity are log-free in
BOTH parity sectors -- the repeated-root/Jordan gate resolves with no
Jordan blocks at the formal level.  The remaining asymptotic gates are
the metric reconstruction (h-level asymptotics of the composition) and
the finite-flux boundary class, which are NOT decided here.

NOT claimed: Borel/analytic summability of the formal series, metric
reconstruction at infinity, a finite-flux boundary class, an
asymptotically flat phase space, symbolic-frequency polar mu = -2 omega
counts, general l, or any stability statement.
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
DEFAULT_OUTPUT = HERE / "certificates" / "BH2C_ASYMPTOTIC_JORDAN.json"
SCHEMA_PATH = HERE / "schema" / "bh2c-asymptotic-jordan-v1.schema.json"
AX_DISP = HERE / "certificates" / "BH2A_CAUSAL_DISPOSITION.json"
PO_DISP = HERE / "certificates" / "BH2B_POLAR_DISPOSITION.json"

SCHEMA_NAME = "pure-weyl-bh2c-asymptotic-jordan-v1"
RESULT_ID = "PURE_WEYL_BH2C_ASYMPTOTIC_JORDAN"
RESULT_TOKEN = "BH2C_ASYMPTOTIC_FORMAL_SYSTEM_LOG_FREE_BOTH_PARITIES"

NINF = 8
N_JET = 4


class AsymptoticJordanError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise AsymptoticJordanError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cancel(e):
    return sp.cancel(sp.together(e))


def _inv_series(pn, pd, r, depth):
    nmax = max(m[0] for m in pn.monoms())
    dmax = max(m[0] for m in pd.monoms())
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
        ser[k - (nmax - dmax)] = sp.expand(sum(nn[j] * inv[k - j] for j in range(k + 1)))
    return ser


def run_analysis(geo_cls) -> dict:
    t0_all = time.time()
    out: dict = {"stage_seconds": {}}
    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    w = sp.Symbol("omega", positive=True)
    sig = sp.Symbol("sigma")
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

    # ---- axial second-order rows ------------------------------------------
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

    P = sp.Function("P")(r)
    Q = sp.Function("Q")(r)
    four_a = {p_c: P * E, q_c: Q * E}
    rows_ax = [sp.expand(_cancel(Lrow(psi_a2, DXa, 0, 3).subs(four_a).doit()
                                 / (E * S_ax))),
               sp.expand(_cancel(Lrow(psi_a2, DXa, 1, 3).subs(four_a).doit()
                                 / (E * S_ax)))]
    out["stage_seconds"]["axial_rows"] = round(time.time() - t0, 1)

    # ---- axial formal analysis (symbolic omega) ---------------------------
    t0 = time.time()
    funcs_ax = [P, Q]

    def apply_slot(row, funcs, expo_mu, expo_sig, fn, depth):
        val = sp.exp(sp.I * expo_mu * r) * r**expo_sig
        subm = {d: sp.diff(val, r, d.derivative_count)
                for d in row.atoms(sp.Derivative) if d.args[0] == fn}
        subm[fn] = val
        zmap = {}
        for other in funcs:
            if other == fn:
                continue
            for d in row.atoms(sp.Derivative):
                if d.args[0] == other:
                    zmap[d] = 0
            zmap[other] = 0
        e = _cancel(sp.expand(row.subs(subm).subs(zmap).doit()
                              / (sp.exp(sp.I * expo_mu * r) * r**expo_sig)))
        num, den = sp.fraction(e)
        return _inv_series(sp.Poly(sp.expand(num), r), sp.Poly(sp.expand(den), r),
                           r, depth)

    ax_summary = {}
    for muv, expect_sigs in [(sp.Integer(0), {sp.Integer(0), sp.Integer(-1)}),
                             (-2 * w, {-4 * sp.I * w, -4 * sp.I * w - 1})]:
        aps = [{slot: apply_slot(rows_ax[i], funcs_ax, muv, sig, fn, NINF + 2)
                for slot, fn in (("P", P), ("Q", Q))} for i in range(2)]
        glead = min(min(ser.keys()) for ap in aps for ser in ap.values())

        def Mk(k, sigval):
            return sp.Matrix(2, 2, lambda i, j: sp.expand(
                aps[i][("P", "Q")[j]].get(glead + k, sp.Integer(0)).subs(sig, sigval)))

        disp = sp.factor(Mk(0, sig).det())
        sigs = set(sp.solve(sp.Eq(disp, 0), sig))
        _require(len(sigs) == 2 and all(
            any(sp.simplify(s0 - e0) == 0 for e0 in expect_sigs) for s0 in sigs),
            f"axial sector mu={muv}: unexpected sigma roots {sigs}")
        sig_top = max(sigs, key=lambda s0: sp.re(s0) if s0.is_number else
                      sp.re(sp.simplify(s0 + 4 * sp.I * w)))
        ns = Mk(0, sig_top).nullspace()
        _require(len(ns) == 1, "axial leading nullspace not 1-dim")
        c = [sp.Matrix(ns[0])]
        for n in range(1, NINF):
            rhs = -sum((Mk(n - j, sig_top - j) * c[j] for j in range(n)),
                       sp.zeros(2, 1))
            Mn = Mk(0, sig_top - n)
            if Mn.det() != 0:
                c.append(Mn.solve(rhs))
            else:
                try:
                    soln, params = Mn.gauss_jordan_solve(rhs)
                except ValueError:
                    _require(False, f"axial sector mu={muv}: LOG at order {n}")
                soln = soln.subs({pp: 0 for pp in params})
                _require(all(sp.simplify(cc) == 0
                             for cc in sp.simplify(Mn * soln - rhs)),
                         f"axial sector mu={muv}: LOG at order {n}")
                c.append(soln)
        ax_summary[sp.sstr(muv)] = {"sigma_roots": sorted(sp.sstr(s0) for s0 in sigs),
                                    "log_free": True}
    out["axial"] = ax_summary
    out["stage_seconds"]["axial_formal"] = round(time.time() - t0, 1)

    # ---- polar sliced 6-dim first-order system ----------------------------
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

    # ---- polar jet counts --------------------------------------------------
    t0 = time.time()
    DEPTH = N_JET + 3

    def jet_count(wv_or_sym, muv, sig0, njet):
        Aw = A6 if wv_or_sym is None else A6.subs(w, wv_or_sym)
        Bser = {}
        for i in range(6):
            for j in range(6):
                e = Aw[i, j]
                if e == 0:
                    continue
                if e == 1:
                    Bser[(i, j)] = {0: sp.Integer(1)}
                    continue
                num, den = sp.fraction(_cancel(e))
                Bser[(i, j)] = _inv_series(sp.Poly(sp.expand(num), r),
                                           sp.Poly(sp.expand(den), r), r, njet + 3)

        def Bmat(k):
            return sp.Matrix(6, 6, lambda i, j: Bser.get((i, j), {}).get(k, sp.Integer(0)))

        Bk = [Bmat(k) for k in range(njet + 2)]
        B0c = Bk[0] - sp.I * muv * sp.eye(6)
        kerdim = len(B0c.nullspace())
        unk = [sp.Symbol(f"y_{n}_{i}") for n in range(njet + 1) for i in range(6)]

        def yvec(n):
            return sp.Matrix(6, 1, lambda i, _: sp.Symbol(f"y_{n}_{i}"))

        eqs = []
        for n in range(-1, njet):
            lhs = (sig0 - n) * yvec(n) if 0 <= n <= njet else sp.zeros(6, 1)
            rhs = sp.zeros(6, 1)
            for k in range(0, n + 2):
                j = n + 1 - k
                if 0 <= j <= njet:
                    Bkk = B0c if k == 0 else Bk[k]
                    rhs += Bkk * yvec(j)
            diff = (lhs - rhs) if 0 <= n <= njet else -rhs
            eqs.extend(sp.expand(diff[i]) for i in range(6))
        Ml, bl = sp.linear_eq_to_matrix(eqs, unk)
        _require(bl.norm() == 0, "jet system inhomogeneous")
        return kerdim, len(unk) - Ml.rank()

    polar_summary = {}
    kerdim, nullity = jet_count(None, sp.Integer(0), sp.Integer(-1), 6)
    _require(kerdim == 3 and nullity - kerdim == 3,
             f"polar mu=0 sector: ker {kerdim}, nullity {nullity}")
    polar_summary["mu=0 (symbolic omega)"] = {
        "window": 6, "tail_kernel": kerdim, "log_free": nullity - kerdim}
    for wv in (sp.Rational(3, 5), sp.Rational(2, 7)):
        kerdim, nullity = jet_count(wv, -2 * wv, -4 * sp.I * wv - 1, N_JET)
        _require(kerdim == 3 and nullity - kerdim == 3,
                 f"polar mu=-2w sector at omega={wv}: ker {kerdim}, nullity {nullity}")
        polar_summary[f"mu=-2*omega (omega={wv})"] = {
            "window": N_JET, "tail_kernel": kerdim, "log_free": nullity - kerdim}
    out["polar"] = polar_summary
    out["stage_seconds"]["polar_jets"] = round(time.time() - t0, 1)
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
            "generator": "none; formal asymptotic classification",
            "phase_space": "l = 2 carrier systems at the irregular point r -> infinity",
            "horizon_condition": "none; infinity-local statement",
            "infinity_condition": "formal fundamental system (all orders in 1/r per sector)",
            "frequency_domain": "axial and polar mu=0: symbolic real omega; polar mu=-2omega: rational fixtures 3/5, 2/7",
            "lifecycle": "CLASSIFIED",
        },
        "axial": res["axial"],
        "polar": res["polar"],
        "headline": {
            "statement": "the integer-spaced exponent resonances within each characteristic sector are CONSISTENT: the formal fundamental systems at r -> infinity are log-free in BOTH parity sectors (axial 4-dim, polar 6-dim); the repeated-root/Jordan gate of the asymptotic analysis resolves with no Jordan blocks at the formal level",
            "paper_gate": "this decides the 'first-order matrix and Jordan form' station of Paper 14's principal outer gate; metric reconstruction and the finite-flux boundary class remain",
        },
        "claim_flags": {
            "axial_log_free_certified": True,
            "polar_mu0_log_free_certified": True,
            "polar_mu2w_log_free_fixture_certified": True,
            "polar_mu2w_symbolic_certified": False,
            "summability_certified": False,
            "metric_reconstruction_certified": False,
            "finite_flux_boundary_class_certified": False,
            "general_l_certified": False,
        },
        "missing_objects": [
            "symbolic-frequency polar mu = -2 omega count (fixture-level only)",
            "Borel/analytic summability of the formal series",
            "metric reconstruction at infinity (h-level asymptotics of the composition)",
            "finite-flux boundary class and asymptotically flat phase space",
            "general l",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2c_asymptotic_jordan.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "axial_disposition_certificate": str(AX_DISP.relative_to(ROOT)),
            "axial_disposition_certificate_sha256": _sha256(AX_DISP),
            "polar_disposition_certificate": str(PO_DISP.relative_to(ROOT)),
            "polar_disposition_certificate_sha256": _sha256(PO_DISP),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2c_asymptotic_jordan.py",
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
