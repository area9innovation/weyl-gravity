"""BH-2B stage 3: the polar Einstein branch is exactly two-dimensional.

Fail-closed builder for
`black_hole_programme/certificates/BH2B_POLAR_EINSTEIN.json`.

Verdict: BH2B_POLAR_EINSTEIN_BRANCH_REDUCED_TWO_DIMENSIONAL.

Setting: Schwarzschild (symbolic m), t-chart Regge--Wheeler polar gauge,
l = 2 Fourier modes e^{i omega t}:

    h_tt = B H0 P2, h_tr = H1 P2, h_rr = H2/B P2,
    h_xx = g_xx K P2, h_phiphi = g_phiphi K P2.

Exact results (all derived, none imported):

1. the traceless angular (W-sector) row of delta Ric is (H0 - H2)/2:
   the polar Einstein branch forces H2 = H0;
2. the (tr), (tx), (rx) rows solve uniquely for K', H1', H0'; the (tt)
   row then becomes an algebraic constraint solving H0 in terms of
   (K, H1); the derivative of the algebraic H0 agrees exactly with the
   first-order H0' relation, and the remaining rows ((rr), (angP)) vanish
   identically: the polar Einstein branch is EXACTLY the two-dimensional
   first-order system dY/dr = M(r) Y, Y = (K, H1), recorded in the
   certificate;
3. in horizon-adapted variables (K, B H1) the system has a REGULAR
   singular point at r = 2m with t-chart residue spectrum {+2imw, -2imw}
   (the e^{+-i omega r*} pair) and ingoing-convention spectrum
   {0, -4imw} -- identical to the certified axial Regge--Wheeler
   benchmark: the polar Einstein branch has a one-parameter
   ingoing-regular family;
4. the branch injects into the Bach kernel by the certified general split
   identity (BH-2B stage 1): delta Ric = 0 implies delta B = 0 exactly.

NOT claimed / fail-closed: a Schroedinger-form master scalar (Zerilli
potential) was NOT certified -- bounded rational ansatz classes for the
master combination psi = a K + b H1 (poly/(r (3m+2r)^{1,2}) with and
without omega^2 numerator terms, and the inverse metric-reconstruction
ansatz) contain no solution with omega-free potential; the master-scalar
anchor remains OPEN and nothing here depends on it.  Also not claimed:
polar flux matrix, outer boundary, causal disposition, general l,
omega = 0, stability, or any ringdown statement.
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
DEFAULT_OUTPUT = HERE / "certificates" / "BH2B_POLAR_EINSTEIN.json"
SCHEMA_PATH = HERE / "schema" / "bh2b-polar-einstein-v1.schema.json"
BH2B_SPLIT_CERT = HERE / "certificates" / "BH2B_POLAR_SPLIT.json"

SCHEMA_NAME = "pure-weyl-bh2b-polar-einstein-v1"
RESULT_ID = "PURE_WEYL_BH2B_POLAR_EINSTEIN"
RESULT_TOKEN = "BH2B_POLAR_EINSTEIN_BRANCH_REDUCED_TWO_DIMENSIONAL"


class BH2BEinsteinError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise BH2BEinsteinError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cancel(e):
    return sp.cancel(sp.together(e))


def run_analysis(geo_cls) -> dict:
    t0_all = time.time()
    out: dict = {"stage_seconds": {}}
    t, ph = sp.symbols("t phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    w = sp.Symbol("omega")
    m = sp.Symbol("m", positive=True)
    rho = sp.Symbol("rho")
    coords = [t, r, x, ph]
    N = 4
    B0 = 1 - 2 * m / r
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = geo_cls(coords, g0)
    gi = geo0.ginv
    G = geo0.Gamma
    P2 = (3 * x**2 - 1) / 2
    dP2 = sp.diff(P2, x)
    E = sp.exp(sp.I * w * t)

    # ---- delta Ric rows of the RW-gauge polar ansatz ----------------------
    t0 = time.time()
    H0, H1, H2, K = [sp.Function(n)(r) for n in ("H0", "H1", "H2", "K")]
    h = sp.zeros(4, 4)
    h[0, 0] = B0 * H0 * P2 * E
    h[0, 1] = h[1, 0] = H1 * P2 * E
    h[1, 1] = H2 / B0 * P2 * E
    h[2, 2] = g0[2, 2] * K * P2 * E
    h[3, 3] = g0[3, 3] * K * P2 * E

    dG = [[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)]
    for a in range(N):
        for b in range(N):
            for c in range(b, N):
                s = sum(gi[a, d] * (geo0.covd2(h, b, d, c) + geo0.covd2(h, c, b, d)
                                    - geo0.covd2(h, d, b, c))
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
            val = _cancel(sum(cov_dG(a, a, b, d) - cov_dG(d, a, b, a) for a in range(N)))
            dRic[b, d] = val
            dRic[d, b] = val

    x0, x1, x2c = sp.Integer(0), sp.Rational(1, 2), sp.Rational(1, 3)

    def strip(raw, ang, xa, xb):
        e0 = _cancel(raw.subs(x, xa).doit() / E) / ang.subs(x, xa)
        chk = _cancel(raw.subs(x, xb).doit() / E - e0 * ang.subs(x, xb))
        _require(chk == 0, "harmonic stripping inconsistent")
        return _cancel(e0)

    rows = {}
    rows["tt"] = strip(dRic[0, 0], P2, x0, x1)
    rows["tr"] = strip(dRic[0, 1], P2, x0, x1)
    rows["rr"] = strip(dRic[1, 1], P2, x0, x1)
    rows["tx"] = strip(dRic[0, 2], dP2, x1, x2c)
    rows["rx"] = strip(dRic[1, 2], dP2, x1, x2c)
    Wxx = sp.Rational(3, 2)
    raw = dRic[2, 2] / E
    Msv = sp.Matrix([[g0[2, 2].subs(x, x0) * P2.subs(x, x0), Wxx],
                     [g0[2, 2].subs(x, x1) * P2.subs(x, x1), Wxx]])
    solv = Msv.solve(sp.Matrix([_cancel(raw.subs(x, x0).doit()),
                                _cancel(raw.subs(x, x1).doit())]))
    rows["angP"], rows["angW"] = _cancel(solv[0]), _cancel(solv[1])
    chk = _cancel(raw.subs(x, x2c).doit() - rows["angP"] * g0[2, 2].subs(x, x2c) * P2.subs(x, x2c)
                  - rows["angW"] * Wxx)
    _require(chk == 0, "angular harmonic decomposition failed")
    # W-sector forces H2 = H0
    _require(_cancel(rows["angW"] - (H0 - H2) / 2) == 0,
             "W-sector row is not (H0 - H2)/2")
    out["stage_seconds"]["rows"] = round(time.time() - t0, 1)

    # ---- reduction to the 2-dim (K, H1) system ----------------------------
    t0 = time.time()
    sub_h2 = {sp.Derivative(H2, (r, 2)): sp.Derivative(H0, (r, 2)),
              sp.Derivative(H2, r): sp.Derivative(H0, r), H2: H0}
    R = {k: _cancel(v_.subs(sub_h2)) for k, v_ in rows.items()}
    _require(R["angW"] == 0, "angW residual after H2 = H0")
    d1 = lambda fn: sp.Derivative(fn, r)
    sol_K = sp.solve(sp.Eq(R["tr"], 0), d1(K))
    _require(len(sol_K) == 1, "K' not uniquely solvable")
    Kp = _cancel(sol_K[0])
    sol_H1 = sp.solve(sp.Eq(R["tx"], 0), d1(H1))
    _require(len(sol_H1) == 1, "H1' not uniquely solvable")
    H1p = _cancel(sol_H1[0])
    rx1 = _cancel(R["rx"].subs(d1(K), Kp).doit())
    sol_H0 = sp.solve(sp.Eq(rx1, 0), d1(H0))
    _require(len(sol_H0) == 1, "H0' not uniquely solvable")
    H0p = _cancel(sol_H0[0])
    first = {d1(K): Kp, d1(H1): H1p, d1(H0): H0p}

    def reduce1(e):
        for _ in range(40):
            ds = list(e.atoms(sp.Derivative))
            if not ds:
                return e
            dd = max(ds, key=lambda z: z.derivative_count)
            fn = dd.args[0]
            k = dd.derivative_count
            repl = first[d1(fn)] if k == 1 else sp.diff(first[d1(fn)], r, k - 1)
            e = e.subs(dd, repl).doit()
        raise BH2BEinsteinError("first-order reduction did not converge")

    cons = {nm: _cancel(reduce1(R[nm])) for nm in ("tt", "rr", "angP")}
    for nm, cc in cons.items():
        _require(not cc.atoms(sp.Derivative), f"row {nm} not algebraic after reduction")
    sol = sp.solve(sp.Eq(cons["tt"], 0), H0)
    _require(len(sol) == 1, "constraint does not solve H0 uniquely")
    H0e = _cancel(sol[0])
    H0p_alg = _cancel(sp.diff(H0e, r).subs(first).doit().subs(H0, H0e).doit())
    H0p_sys = _cancel(H0p.subs(H0, H0e).doit())
    _require(sp.simplify(H0p_alg - H0p_sys) == 0, "H0' consistency fails")
    for nm in ("rr", "angP"):
        _require(sp.simplify(_cancel(cons[nm].subs(H0, H0e).doit())) == 0,
                 f"row {nm} residual nonzero on the reduced system")
    Kp2 = _cancel(Kp.subs(H0, H0e).doit())
    H1p2 = _cancel(H1p.subs(H0, H0e).doit())
    M = sp.zeros(2, 2)
    for i2, expr in enumerate((Kp2, H1p2)):
        e = sp.expand(expr)
        M[i2, 0] = _cancel(e.coeff(K))
        M[i2, 1] = _cancel(e.coeff(H1))
        _require(_cancel(e - M[i2, 0] * K - M[i2, 1] * H1) == 0,
                 "system not linear in (K, H1)")
    out["stage_seconds"]["reduction"] = round(time.time() - t0, 1)
    out["M"] = M
    out["H0"] = H0e

    # ---- horizon analysis in adapted variables ----------------------------
    t0 = time.time()
    D = sp.diag(1, B0)
    Mad = sp.Matrix(2, 2, lambda i, j: _cancel(
        (D * M * D.inv() + sp.diff(D, r) * D.inv())[i, j]))
    spectra = {}
    for label, Mm in [("t_chart", Mad), ("ingoing", Mad - sp.I * w / B0 * sp.eye(2))]:
        Ar = Mm.subs(r, 2 * m + rho)
        for i2 in range(2):
            for j2 in range(2):
                _require(sp.simplify(sp.limit(rho**2 * _cancel(Ar[i2, j2]), rho, 0)) == 0,
                         f"irregular singular point ({label})")
        Res = sp.Matrix(2, 2, lambda i2, j2: sp.cancel(
            sp.limit(rho * _cancel(Ar[i2, j2]), rho, 0)))
        ev = {sp.nsimplify(sp.simplify(kk)): mult for kk, mult in Res.eigenvals().items()}
        spectra[label] = ev
    exp_t = {sp.nsimplify(2 * sp.I * m * w): 1, sp.nsimplify(-2 * sp.I * m * w): 1}
    exp_in = {sp.Integer(0): 1, sp.nsimplify(-4 * sp.I * m * w): 1}
    for got, want, lab in [(spectra["t_chart"], exp_t, "t-chart"),
                           (spectra["ingoing"], exp_in, "ingoing")]:
        _require(
            len(got) == 2 and all(
                any(sp.simplify(kk - ee) == 0 for ee in want) for kk in got),
            f"unexpected {lab} spectrum {got}",
        )
    out["stage_seconds"]["horizon"] = round(time.time() - t0, 1)
    out["stage_seconds"]["total"] = round(time.time() - t0_all, 1)
    return out


def build_certificate() -> dict:
    res = run_analysis(Geometry)
    M = res["M"]
    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd (Einstein branch: delta Ric = 0 modes of the split)",
            "background_family": "Schwarzschild (symbolic m)",
            "conformal_frame": "working gauge; t-chart RW polar gauge, x = cos theta",
            "generator": "not used; mode-level statements only",
            "phase_space": "none; no flux or pairing claim",
            "horizon_condition": "regular-singular residue analysis at r = 2m in horizon-adapted variables (K, B H1)",
            "infinity_condition": "none imposed",
            "frequency_domain": "omega != 0 Fourier modes",
            "lifecycle": "CLASSIFIED",
        },
        "reduction": {
            "gauge": "RW polar gauge h = (B H0, H1, H2/B, K) x P2 e^{i omega t}",
            "w_sector": "traceless angular row = (H0 - H2)/2: H2 = H0 forced",
            "system": "dY/dr = M(r) Y, Y = (K, H1); H0 algebraic in (K, H1); all seven delta-Ric rows are consequences (verified identically)",
            "M": [[sp.sstr(M[i, j]) for j in range(2)] for i in range(2)],
            "H0_algebraic": sp.sstr(res["H0"]),
            "dimension": "exactly 2 per (l = 2, omega != 0)",
        },
        "horizon_analysis": {
            "adapted_variables": "(K, B H1); raw (K, H1) has a double pole (t-chart artifact)",
            "t_chart_spectrum": ["2*I*m*omega", "-2*I*m*omega"],
            "ingoing_spectrum": ["0", "-4*I*m*omega"],
            "benchmark": "identical to the certified axial Regge-Wheeler benchmark: a one-parameter ingoing-regular polar Einstein family",
        },
        "bach_kernel": "delta Ric = 0 implies delta B = 0 exactly by the certified general split identity (BH-2B stage 1)",
        "master_scalar": {
            "status": "OPEN",
            "statement": "no Schroedinger-form master combination psi = a K + b H1 with omega-independent potential was found within the searched bounded rational ansatz classes (poly/(r(3m+2r)) and poly/(r(3m+2r)^2) with and without omega^2 numerator terms; inverse metric-reconstruction ansatz poly/(3m+2r), i*omega*poly/((3m+2r)(r-2m))); the anchor remains fail-closed OPEN and no result here depends on it",
        },
        "claim_flags": {
            "polar_einstein_reduction_certified": True,
            "h2_equals_h0_certified": True,
            "two_dimensionality_certified": True,
            "horizon_benchmark_certified": True,
            "bach_kernel_injection_certified": True,
            "master_scalar_certified": False,
            "flux_or_sign_certified": False,
            "outer_boundary_domain_certified": False,
            "causal_exclusion_decided": False,
            "growth_or_stability_certified": False,
            "general_l_certified": False,
            "omega_zero_classified": False,
        },
        "missing_objects": [
            "Schroedinger-form polar master scalar with omega-free potential (Zerilli anchor)",
            "polar bilinear symplectic flux matrix and Lee-Wald signs",
            "outer-boundary operator domains and falloff classification (polar)",
            "causal disposition of the polar sector",
            "general l; omega = 0 static sector; growth/stability data",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2b_polar_einstein.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "bh2b_split_certificate": str(BH2B_SPLIT_CERT.relative_to(ROOT)),
            "bh2b_split_certificate_sha256": _sha256(BH2B_SPLIT_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2b_polar_einstein.py",
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
