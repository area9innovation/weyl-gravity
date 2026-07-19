"""BH-2B stage 6: polar causal disposition — the extra branch is unavoidable.

Fail-closed builder for
`black_hole_programme/certificates/BH2B_POLAR_DISPOSITION.json`.

Verdict: BH2B_POLAR_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE.

Exact computation (Schwarzschild m = 1, polar l = 2, traceless-slice
carrier system of the certified polar extra branch, symbolic real omega):
asymptotic ansatz (a, bc, cc) ~ e^{i mu r} r^sigma v0 in the ingoing EF
chart (equivalently e^{i lam r} r^{sigma_t} with lam = mu + omega,
sigma_t = sigma + 2 i omega in the t-chart):

1. leading dispersion mu^3 (mu + 2 omega)^3 = 0, i.e. the t-chart
   (lam^2 - omega^2)^3: the polar extra branch propagates on EXACTLY the
   Einstein characteristics (massless/luminal), with three-dimensional
   amplitude spaces at each sign (two physical + one conformal-gauge);
2. degenerate next-order solvability: t-chart sigma in
   {+-2 i omega - 1, +-2 i omega - 2, +-2 i omega - 3}: pure Coulomb
   log-phases with amplitude falloffs r^{-1}, r^{-2}, r^{-3} -- ALL
   DECAYING (strictly stronger than the axial r^0, r^{-1} case): no
   growing asymptotic solutions at real frequencies;
3. Einstein control: the certified 2-dim polar Einstein system eliminates
   to a K-scalar with dispersion proportional to (lam^2 - omega^2) and
   sigma = +-2 i omega -- the branches are asymptotically
   indistinguishable by characteristics;
4. conformal-gauge control: the scalar wave Box(phi P2 e^{i omega t}) = 0
   has dispersion (lam^2 - omega^2) and sigma = +-2 i omega - 1, matching
   one carrier branch (the gauge direction inside the carrier
   asymptotics).

Disposition (combining certified facts): the polar extra branch
(i) reaches the future horizon with a two-parameter physical
ingoing-regular family modulo conformal gauge (BH2B_POLAR_REACH),
(ii) carries nonzero horizon flux with the Einstein block null
(BH2B_POLAR_FLUX + BH2B_POLAR_CROSS_FLUX), and (iii) has bounded decaying
oscillatory asymptotics on the Einstein characteristics at infinity
(this certificate).  Therefore, at the polar l = 2 linear mode level, no
causal decay or regularity prescription at the horizon or at infinity
excludes the polar extra branch.  Together with the axial disposition
(BH2A stage 5), BH-2 is CLOSED at the l = 2 linear mode level in BOTH
parity sectors: pure-Weyl black-hole exteriors cannot be causally
truncated to the Einstein sector, and their radiation lives in the
mixed/extra sectors.

NOT claimed: complex-frequency structure, general l or m, nonlinear or
all-orders statements, initial-boundary well-posedness, stability, or
ringdown (vocabulary remains locked pending coordinator review).
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
DEFAULT_OUTPUT = HERE / "certificates" / "BH2B_POLAR_DISPOSITION.json"
SCHEMA_PATH = HERE / "schema" / "bh2b-polar-disposition-v1.schema.json"
REACH_CERT = HERE / "certificates" / "BH2B_POLAR_REACH.json"
FLUX_CERT = HERE / "certificates" / "BH2B_POLAR_FLUX.json"
CROSS_CERT = HERE / "certificates" / "BH2B_POLAR_CROSS_FLUX.json"
EIN_CERT = HERE / "certificates" / "BH2B_POLAR_EINSTEIN.json"

SCHEMA_NAME = "pure-weyl-bh2b-polar-disposition-v1"
RESULT_ID = "PURE_WEYL_BH2B_POLAR_DISPOSITION"
RESULT_TOKEN = "BH2B_POLAR_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE"


class PolarDispositionError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise PolarDispositionError(msg)


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
    E = sp.exp(sp.I * w * v)
    x0, x1 = sp.Integer(0), sp.Rational(1, 2)

    # ---- carrier sliced rows (EF chart, m = 1) ----------------------------
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
        _require(bianchi_row(psi_c, S_c, b) == 0, f"Bianchi row {b} nonzero")

    DXc = [[[sp.together(geo0.covd2(psi_c, e, a, b)) for b in range(N)]
            for a in range(N)] for e in range(N)]

    def covd2X2c(e, f, a, b):
        s = sp.diff(DXc[f][a][b], coords[e])
        for hh in range(N):
            s -= (G[hh][e][f] * DXc[hh][a][b] + G[hh][e][a] * DXc[f][hh][b]
                  + G[hh][e][b] * DXc[f][a][hh])
        return s

    Xup = sp.Matrix(4, 4, lambda c2, d2: sp.together(
        sum(gi[c2, e] * gi[d2, f] * psi_c[e, f] for e in range(4) for f in range(4))))
    dS1 = [sp.diff(S_c, coords[e]) for e in range(4)]
    DDS = sp.Matrix(4, 4, lambda a, b: sp.together(
        sp.diff(dS1[a], coords[b]) - sum(G[hh][a][b] * dS1[hh] for hh in range(4))))
    boxS = sp.together(sum(gi[e, f] * DDS[e, f] for e in range(4) for f in range(4)
                           if gi[e, f] != 0))

    def op_row(a, b):
        boxpsi = sum(gi[e, f] * covd2X2c(e, f, a, b)
                     for e in range(N) for f in range(N) if gi[e, f] != 0)
        cx = sum(geo0.Weyl[a][c2][b][d2] * Xup[c2, d2]
                 for c2 in range(4) for d2 in range(4))
        return (boxpsi / 2 + cx - DDS[a, b] / 6 - g0[a, b] * boxS / 12) / E

    def strip_single(raw, ang, xa, xb):
        e0 = _cancel(raw.subs(x, xa).doit()) / ang.subs(x, xa)
        chk = _cancel(raw.subs(x, xb).doit() - e0 * ang.subs(x, xb))
        _require(chk == 0, "harmonic stripping inconsistent")
        return _cancel(e0)

    crow = [strip_single(op_row(0, 0), P2, x0, x1),
            strip_single(op_row(0, 1), P2, x0, x1),
            strip_single(op_row(1, 1), P2, x0, x1)]
    f_slice = -bcr - B0 * ccr / 2
    subf = {sp.Derivative(fr, (r, k)): sp.diff(f_slice, r, k) for k in (3, 2, 1)}
    subf[fr] = f_slice
    sys3 = [_cancel(cr.subs(subf).doit()) for cr in crow]
    out["stage_seconds"]["carrier_rows"] = round(time.time() - t0, 1)

    # ---- carrier asymptotics ----------------------------------------------
    t0 = time.time()
    mu, sig = sp.symbols("mu sigma")
    a0, b0, c0 = sp.symbols("a0 b0 c0")
    amp = {ar: a0, bcr: b0, ccr: c0}
    ans = {fn: cv * sp.exp(sp.I * mu * r) * r**sig for fn, cv in amp.items()}

    def poly_of(row, subs_amp, phase_var):
        e = row
        for fn, val in subs_amp.items():
            subm = {}
            for d in list(e.atoms(sp.Derivative)):
                if d.args[0] == fn:
                    subm[d] = sp.diff(val, r, d.derivative_count)
            subm[fn] = val
            e = e.subs(subm)
        e = sp.expand(e.doit() / (sp.exp(sp.I * phase_var * r) * r**sig))
        num, _ = sp.fraction(sp.together(sp.expand(_cancel(sp.together(e)))))
        return sp.Poly(sp.expand(num), r)

    pols = [poly_of(row, ans, mu) for row in sys3]
    degs = [max(mon[0] for mon in p.monoms()) for p in pols]
    tops = [sp.expand(p.coeff_monomial(r**d)) for p, d in zip(pols, degs)]
    M0 = sp.Matrix(3, 3, lambda i, j: tops[i].coeff((a0, b0, c0)[j]))
    disp = sp.factor(M0.det())
    _require(not sp.simplify(disp / (mu**3 * (mu + 2 * w) ** 3)).has(mu),
             f"dispersion not mu^3 (mu + 2 omega)^3: {disp}")
    sig_results = {}
    for muv, expect in [(sp.Integer(0), {-1, -2, -3}),
                        (-2 * w, {-4 * sp.I * w - 1, -4 * sp.I * w - 2,
                                  -4 * sp.I * w - 3})]:
        M0l = M0.subs(mu, muv)
        ns = M0l.nullspace()
        lns = M0l.T.nullspace()
        _require(len(ns) == 3 and len(lns) == 3, "leading nullspace not 3-dim")
        nxt = [sp.expand(p.coeff_monomial(r**(d - 1))).subs(mu, muv)
               for p, d in zip(pols, degs)]
        N1 = sp.Matrix(3, 3, lambda i, j: nxt[i].coeff((a0, b0, c0)[j]))
        proj = sp.Matrix(3, 3, lambda i, j: sp.expand((lns[i].T * N1 * ns[j])[0, 0]))
        sigs = set(sp.solve(sp.Eq(sp.factor(sp.expand(proj.det())), 0), sig))
        _require(
            len(sigs) == 3 and all(
                any(sp.simplify(sv - ev) == 0 for ev in expect) for sv in sigs),
            f"unexpected sigma set at mu={muv}: {sigs}",
        )
        sig_results[sp.sstr(muv)] = sorted(sp.sstr(sv) for sv in sigs)
    out["sigma"] = sig_results
    out["stage_seconds"]["carrier_asymptotics"] = round(time.time() - t0, 1)

    # ---- Einstein K-scalar control ----------------------------------------
    t0 = time.time()
    cert_e = json.loads(EIN_CERT.read_text(encoding="utf-8"))
    m_sym = sp.Symbol("m", positive=True)
    locs = {"r": r, "omega": w, "m": m_sym, "I": sp.I,
            "K": sp.Function("K"), "H1": sp.Function("H1")}
    Me = sp.Matrix(2, 2, lambda i, j: sp.sympify(cert_e["reduction"]["M"][i][j],
                                                 locals=locs).subs(m_sym, 1))
    lam = sp.Symbol("lambda_")
    Ksc = sp.Function("Ksc")(r)
    H1e = _cancel((sp.Derivative(Ksc, r) - Me[0, 0] * Ksc) / Me[0, 1])
    ode = _cancel(sp.diff(H1e, r).doit() - Me[1, 0] * Ksc - Me[1, 1] * H1e)
    pE = poly_of(ode, {Ksc: a0 * sp.exp(sp.I * lam * r) * r**sig}, lam)
    dE = max(mon[0] for mon in pE.monoms())
    dispE = sp.factor(sp.expand(pE.coeff_monomial(r**dE)).coeff(a0))
    _require(not sp.simplify(dispE / ((lam - w) * (lam + w))).has(lam),
             f"Einstein control dispersion unexpected: {dispE}")
    for lv, expect in [(w, 2 * sp.I * w), (-w, -2 * sp.I * w)]:
        nx = sp.expand(pE.coeff_monomial(r**(dE - 1))).coeff(a0).subs(lam, lv)
        sv = sp.solve(sp.Eq(nx, 0), sig)
        _require(len(sv) == 1 and sp.simplify(sv[0] - expect) == 0,
                 f"Einstein control sigma unexpected at lam={lv}: {sv}")
    out["stage_seconds"]["einstein_control"] = round(time.time() - t0, 1)

    # ---- conformal-gauge scalar control (t-chart) -------------------------
    t0 = time.time()
    t_ch = sp.Symbol("t")
    g_t = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo_t = geo_cls([t_ch, r, x, ph], g_t)
    gi_t = geo_t.ginv
    G_t = geo_t.Gamma
    phi_f = sp.Function("phig")(r)
    Phi = phi_f * P2 * sp.exp(sp.I * w * t_ch)
    dPhi = [sp.diff(Phi, c) for c in (t_ch, r, x, ph)]
    boxPhi = sp.together(sum(
        gi_t[e2, f2] * (sp.diff(dPhi[e2], (t_ch, r, x, ph)[f2])
                        - sum(G_t[hh][e2][f2] * dPhi[hh] for hh in range(4)))
        for e2 in range(4) for f2 in range(4) if gi_t[e2, f2] != 0))
    wave = _cancel(boxPhi / (P2 * sp.exp(sp.I * w * t_ch)))
    pw = poly_of(wave, {phi_f: a0 * sp.exp(sp.I * lam * r) * r**sig}, lam)
    dw = max(mon[0] for mon in pw.monoms())
    dispw = sp.factor(sp.expand(pw.coeff_monomial(r**dw)).coeff(a0))
    _require(not sp.simplify(dispw / ((lam - w) * (lam + w))).has(lam),
             f"gauge control dispersion unexpected: {dispw}")
    for lv, expect in [(w, 2 * sp.I * w - 1), (-w, -2 * sp.I * w - 1)]:
        nx = sp.expand(pw.coeff_monomial(r**(dw - 1))).coeff(a0).subs(lam, lv)
        sv = sp.solve(sp.Eq(nx, 0), sig)
        _require(len(sv) == 1 and sp.simplify(sv[0] - expect) == 0,
                 f"gauge control sigma unexpected at lam={lv}: {sv}")
    out["stage_seconds"]["gauge_control"] = round(time.time() - t0, 1)
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
            "background_family": "Schwarzschild, m = 1 fixture; omega symbolic real",
            "conformal_frame": "working gauge; ingoing EF chart (t-chart equivalents stated)",
            "generator": "none; asymptotic mode classification",
            "phase_space": "polar l = 2 linear carrier modes (traceless slice)",
            "horizon_condition": "imported: certified two-parameter physical ingoing-regular polar family",
            "infinity_condition": "formal asymptotic classification at r -> infinity (leading two orders)",
            "lifecycle": "CLASSIFIED",
        },
        "asymptotics": {
            "dispersion": "mu^3 (mu + 2 omega)^3 in the EF chart, i.e. (lambda^2 - omega^2)^3 in the t-chart: the polar extra branch propagates on the Einstein characteristics (massless/luminal), 3-dim amplitude spaces at each sign (2 physical + 1 conformal-gauge)",
            "sigma_ef": res["sigma"],
            "interpretation": "t-chart sigma in {+-2 i omega - 1, -2, -3}: pure Coulomb log-phases with amplitude falloffs r^-1, r^-2, r^-3 -- ALL DECAYING (stronger than the axial r^0, r^-1): no growing asymptotic solutions at real frequencies",
            "einstein_control": "the certified 2-dim polar Einstein system eliminates to a K-scalar with dispersion (lambda^2 - omega^2) and sigma = +-2 i omega: same characteristics, asymptotically indistinguishable by falloff class",
            "gauge_control": "the conformal scalar wave has dispersion (lambda^2 - omega^2) and sigma = +-2 i omega - 1, matching one carrier branch (the gauge direction)",
        },
        "disposition": {
            "statement": "at the polar l = 2 linear mode level, the extra branch reaches the horizon (two-parameter physical ingoing-regular family modulo conformal gauge), carries nonzero horizon flux (Einstein block null, cross block nonzero), and is bounded decaying oscillatory radiation on the Einstein characteristics at infinity; no causal decay or regularity prescription at either boundary excludes it",
            "bh2_closure": "together with the axial disposition (BH-2A stage 5), BH-2 is closed at the l = 2 linear mode level in BOTH parity sectors: pure-Weyl black-hole exteriors cannot be causally truncated to the Einstein sector; their radiation lives in the mixed/extra sectors",
        },
        "claim_flags": {
            "dispersion_certified": True,
            "no_growing_asymptotics_certified": True,
            "einstein_control_certified": True,
            "gauge_control_certified": True,
            "bh2_polar_mode_level_closed": True,
            "complex_frequency_certified": False,
            "general_l_certified": False,
            "well_posedness_certified": False,
            "growth_or_stability_certified": False,
        },
        "missing_objects": [
            "complex-frequency structure (requires coordinator-gated BH-3 vocabulary)",
            "general l and m; omega = 0 static sector",
            "initial-boundary well-posedness theorem",
            "nonlinear and all-orders statements",
            "invariant extra-block sign theory (null-quotient pairing)",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2b_polar_disposition.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "bh2b_reach_certificate": str(REACH_CERT.relative_to(ROOT)),
            "bh2b_reach_certificate_sha256": _sha256(REACH_CERT),
            "bh2b_flux_certificate": str(FLUX_CERT.relative_to(ROOT)),
            "bh2b_flux_certificate_sha256": _sha256(FLUX_CERT),
            "bh2b_cross_flux_certificate": str(CROSS_CERT.relative_to(ROOT)),
            "bh2b_cross_flux_certificate_sha256": _sha256(CROSS_CERT),
            "bh2b_einstein_certificate": str(EIN_CERT.relative_to(ROOT)),
            "bh2b_einstein_certificate_sha256": _sha256(EIN_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2b_polar_disposition.py",
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
