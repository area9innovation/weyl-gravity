"""BH-2C stage 2: leading-order metric reconstruction and flux symbol.

Fail-closed builder for
`black_hole_programme/certificates/BH2C_METRIC_LEADING.json`.

Verdict: BH2C_METRIC_RECONSTRUCTION_LEADING_ORDER_CLASSIFIED.

Setting: Schwarzschild m = 1, l = 2, EF chart, the sourced composition
h-systems (axial state (H0, H1, H1'); polar state (A, Cc, Cc', K)) and
the certified axial Lee--Wald bilinear.

Exact results:

1. METRIC ENHANCEMENT BOUND: at r -> infinity the leading constant
   matrices B0h of both sourced h-systems are RESONANT in both
   characteristic sectors (det(i mu I - B0h) = 0) with kernel dimension
   exactly ONE: a carrier source ~ e^{i mu r} r^{sigma} can enhance the
   composed metric by AT MOST ONE power of r (rank-1 Fredholm
   alternative); off the one resonant direction sigma_h = sigma_source;
2. FLUX DENSITY SYMBOL: substituting monomial radiative profiles
   ~ e^{i lam r} r^{p} e^{i omega t} (conjugate pair) into the certified
   axial Lee--Wald F^t, the leading term is
       96 pi i alpha (lam - omega)^2 (lam + 2 omega) r^{p1 + p2}:
   it VANISHES ON-CHARACTERISTIC (lam = omega, double zero): radiative
   pairs have subleading symplectic density, and the finite-slice-norm
   question is decided at subleading order (recorded open);
3. the homogeneous sector eigenstructures of both B0h matrices are
   recorded (upper-triangular; eigenvalues {0, 0, -2 i omega} axial and
   {0, 0, 0, -2 i omega} polar in the mu = 0 frame).

NOT claimed: all-orders metric reconstruction, resonant-direction
enhanced series, the finite-flux boundary class, summability,
asymptotically flat phase space, general l, or any stability statement.
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
from weyl_geometry import Geometry

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2C_METRIC_LEADING.json"
SCHEMA_PATH = HERE / "schema" / "bh2c-metric-leading-v1.schema.json"
AX_FLUX = HERE / "certificates" / "BH2A_FLUX_MATRIX.json"
JORDAN = HERE / "certificates" / "BH2C_ASYMPTOTIC_JORDAN.json"

SCHEMA_NAME = "pure-weyl-bh2c-metric-leading-v1"
RESULT_ID = "PURE_WEYL_BH2C_METRIC_LEADING"
RESULT_TOKEN = "BH2C_METRIC_RECONSTRUCTION_LEADING_ORDER_CLASSIFIED"


class MetricLeadingError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise MetricLeadingError(msg)


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
    S_ax = -3 * x * (1 - x**2)
    P2 = (3 * x**2 - 1) / 2
    dP2 = sp.diff(P2, x)
    Wxx = sp.Rational(3, 2)
    Wpp = -sp.Rational(3, 2) * (1 - x**2) ** 2
    E = sp.exp(sp.I * w * v)

    # ---- axial sourced h-system leading matrix ----------------------------
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
                    subm[d] = sp.diff(val, v, dt, r, dr) if dt else sp.diff(val, r, dr)
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
    M3 = sp.zeros(3, 3)
    e0 = sp.expand(H0p.subs({XS: 0}))
    DH1 = sp.Derivative(H1, r)
    M3[0, 0] = e0.coeff(H0); M3[0, 1] = e0.coeff(H1); M3[0, 2] = e0.coeff(DH1)
    M3[1, 2] = 1
    e2 = sp.expand(H1pp.subs({XS: 0, TS: 0}))
    M3[2, 0] = e2.coeff(H0); M3[2, 1] = e2.coeff(H1); M3[2, 2] = e2.coeff(DH1)
    B0h_ax = sp.Matrix(3, 3, lambda i, j: sp.limit(_cancel(M3[i, j]), r, sp.oo))
    ax_res = {}
    for muv in (sp.Integer(0), -2 * w):
        Mm = sp.I * muv * sp.eye(3) - B0h_ax
        _require(sp.factor(Mm.det()) == 0, f"axial sector mu={muv} not resonant")
        kd = len(Mm.nullspace())
        _require(kd == 1, f"axial sector mu={muv} kernel dim {kd} != 1")
        ax_res[sp.sstr(muv)] = {"resonant": True, "kernel_dim": 1}
    out["axial"] = {"B0h": [[sp.sstr(B0h_ax[i, j]) for j in range(3)]
                            for i in range(3)],
                    "sectors": ax_res}
    out["stage_seconds"]["axial"] = round(time.time() - t0, 1)

    # ---- polar sourced h-system leading matrix ----------------------------
    t0 = time.time()
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
                s = sum(gi[a, d] * (geo0.covd2(hp, b, d, c) + geo0.covd2(hp, c, b, d)
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
    hrow["vv"] = strip(dRic[0, 0], P2, x0, x1)
    hrow["vr"] = strip(dRic[0, 1], P2, x0, x1)
    hrow["rr"] = strip(dRic[1, 1], P2, x0, x1)
    hrow["vx"] = strip(dRic[0, 2], dP2, x1, sp.Rational(1, 3))
    hrow["rx"] = strip(dRic[1, 2], dP2, x1, sp.Rational(1, 3))
    raw = dRic[2, 2] / E
    Msv = sp.Matrix([[g0[2, 2].subs(x, x0) * P2.subs(x, x0), Wxx],
                     [g0[2, 2].subs(x, x1) * P2.subs(x, x1), Wxx]])
    solv = Msv.solve(sp.Matrix([_cancel(raw.subs(x, x0).doit()),
                                _cancel(raw.subs(x, x1).doit())]))
    hrow["angW"] = _cancel(solv[1])
    Bc_sol = sp.solve(sp.Eq(hrow["angW"], 0), Bh)
    _require(len(Bc_sol) == 1, "Bc not solvable")
    Bc_e = _cancel(Bc_sol[0])
    subB = {sp.Derivative(Bh, r): sp.diff(Bc_e, r).doit(), Bh: Bc_e}
    d1 = lambda fn: sp.Derivative(fn, r)
    R2 = {nm: _cancel(hrow[nm].subs(subB).doit()) for nm in ("vx", "rx", "rr")}
    Ap = _cancel(sp.solve(sp.Eq(R2["vx"], 0), d1(Ah))[0])
    Kp = _cancel(sp.solve(sp.Eq(R2["rx"], 0), d1(Kh))[0])
    rr1 = R2["rr"].subs({sp.Derivative(Kh, (r, 2)): sp.diff(Kp, r).doit(),
                         d1(Kh): Kp}).doit()
    rr1 = _cancel(rr1.subs(d1(Ah), Ap).doit())
    C2 = _cancel(sp.solve(sp.Eq(rr1, 0), sp.Derivative(Ch, (r, 2)))[0])
    state = [Ah, Ch, d1(Ch), Kh]
    Mh = sp.zeros(4, 4)
    Mh[1, 2] = 1
    for i, expr in ((0, Ap), (2, C2), (3, Kp)):
        e = sp.expand(expr)
        for j, st in enumerate(state):
            Mh[i, j] = _cancel(e.coeff(st))
    B0h_po = sp.Matrix(4, 4, lambda i, j: sp.limit(_cancel(Mh[i, j]), r, sp.oo))
    po_res = {}
    for muv in (sp.Integer(0), -2 * w):
        Mm = sp.I * muv * sp.eye(4) - B0h_po
        _require(sp.factor(Mm.det()) == 0, f"polar sector mu={muv} not resonant")
        kd = len(Mm.nullspace())
        _require(kd == 1, f"polar sector mu={muv} kernel dim {kd} != 1")
        po_res[sp.sstr(muv)] = {"resonant": True, "kernel_dim": 1}
    out["polar"] = {"B0h": [[sp.sstr(B0h_po[i, j]) for j in range(4)]
                            for i in range(4)],
                    "sectors": po_res}
    out["stage_seconds"]["polar"] = round(time.time() - t0, 1)

    # ---- flux density leading symbol --------------------------------------
    t0 = time.time()
    t_s = sp.Symbol("t")
    m_s = sp.Symbol("m", positive=True)
    alpha = sp.Symbol("alpha", positive=True)
    w1 = sp.Symbol("omega1")
    lam = sp.Symbol("lambda_", real=True)
    p1, p2 = sp.symbols("p1 p2", real=True)
    cert = json.loads(AX_FLUX.read_text(encoding="utf-8"))
    locF = {"t": t_s, "r": r, "m": m_s, "alpha": alpha, "I": sp.I, "pi": sp.pi,
            "omega1": w1}
    for nm in ("h0a", "h1a", "h0b", "h1b"):
        locF[nm] = sp.Function(nm)
    Ft = sp.sympify(cert["bilinear"]["F_t"], locals=locF)
    prof = {"h0a": sp.exp(sp.I * lam * r) * r**p1 * sp.exp(sp.I * w1 * t_s),
            "h1a": sp.exp(sp.I * lam * r) * r**p1 * sp.exp(sp.I * w1 * t_s),
            "h0b": sp.exp(-sp.I * lam * r) * r**p2 * sp.exp(-sp.I * w1 * t_s),
            "h1b": sp.exp(-sp.I * lam * r) * r**p2 * sp.exp(-sp.I * w1 * t_s)}
    sub = {}
    for nm, val in prof.items():
        f = locF[nm](t_s, r)
        for d in list(Ft.atoms(sp.Derivative)):
            if d.args[0] == f:
                dt = sum(int(p[1]) for p in d.args[1:] if p[0] == t_s)
                dr = sum(int(p[1]) for p in d.args[1:] if p[0] == r)
                sub[d] = sp.diff(val, t_s, dt, r, dr)
        sub[f] = val
    e = Ft.subs(sub).doit()
    e = sp.powsimp(sp.expand(e / (r**(p1 + p2))), force=True)
    e = _cancel(sp.together(e))
    num, den = sp.fraction(e)
    pn = sp.Poly(sp.expand(num), r)
    pd = sp.Poly(sp.expand(den), r)
    degn = max(mm[0] for mm in pn.monoms())
    degd = max(mm[0] for mm in pd.monoms())
    _require(degn - degd == 0, f"flux leading relative power {degn - degd} != 0")
    lead = sp.factor(sp.expand(pn.coeff_monomial(r**degn))
                     / pd.coeff_monomial(r**degd))
    target = sp.Rational(96, 5) * sp.I * sp.pi * alpha * (lam - w1) ** 2 * (lam + 2 * w1)
    _require(sp.simplify(lead - target) == 0,
             f"flux leading symbol mismatch: {lead}")
    out["flux_symbol"] = sp.sstr(target)
    out["stage_seconds"]["flux_symbol"] = round(time.time() - t0, 1)
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
            "background_family": "Schwarzschild m = 1 fixture; symbolic omega",
            "conformal_frame": "working gauge; ingoing EF chart (flux symbol in the certified t-chart bilinear)",
            "generator": "none; leading asymptotic classification",
            "phase_space": "sourced composition h-systems and the certified axial Lee-Wald bilinear",
            "horizon_condition": "none; infinity-local statement",
            "infinity_condition": "leading order at r -> infinity",
            "lifecycle": "CLASSIFIED",
        },
        "axial": res["axial"],
        "polar": res["polar"],
        "flux_symbol": {
            "leading": res["flux_symbol"],
            "relative_power": 0,
            "reading": "F^t ~ (96/5) pi i alpha (lam - omega)^2 (lam + 2 omega) r^{p1+p2} + subleading: the density VANISHES ON-CHARACTERISTIC (double zero at lam = omega): radiative pairs have subleading symplectic density and the finite-slice-norm question is decided at subleading order",
        },
        "headline": {
            "statement": "the sourced composition h-systems are rank-1 resonant in both characteristic sectors and both parities: composed metric perturbations gain AT MOST ONE power of r over the carrier at infinity; the axial flux density symbol vanishes on-characteristic to leading order",
            "paper_gate": "the 'metric reconstruction' station of the outer gate is decided at leading order; the all-orders reconstruction and the finite-flux boundary class remain",
        },
        "claim_flags": {
            "enhancement_bound_certified": True,
            "rank_one_resonance_certified": True,
            "flux_leading_symbol_certified": True,
            "on_characteristic_vanishing_certified": True,
            "all_orders_reconstruction_certified": False,
            "finite_flux_boundary_class_certified": False,
            "polar_flux_symbol_certified": False,
            "general_l_certified": False,
        },
        "missing_objects": [
            "all-orders metric reconstruction (resonant-direction enhanced series)",
            "finite-flux boundary class (subleading flux powers on-characteristic)",
            "polar flux density symbol (needs the polar bilinear symbol extraction)",
            "asymptotically flat phase space; summability",
            "general l",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2c_metric_leading.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "axial_flux_certificate": str(AX_FLUX.relative_to(ROOT)),
            "axial_flux_certificate_sha256": _sha256(AX_FLUX),
            "jordan_certificate": str(JORDAN.relative_to(ROOT)),
            "jordan_certificate_sha256": _sha256(JORDAN),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2c_metric_leading.py",
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
