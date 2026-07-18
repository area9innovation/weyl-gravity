"""BH-2A stage 1: axial l=2 exterior operator and exact branch split.

Fail-closed builder for
`black_hole_programme/certificates/BH2A_AXIAL_OPERATOR.json`.

Verdict: BH2A_AXIAL_L2_OPERATOR_AND_BRANCH_SPLIT_CLASSIFIED.

Exact results (rational chart x = cos(theta); axial l=2, m=0 perturbation
h_{t phi} = h0(t,r) S, h_{r phi} = h1(t,r) S with S = -3x(1-x^2); all
sympy-exact):

1. First-order machinery `linearized_bach.LinearizedBach` validated on
   three controls: conformal direction -> 0, family-tangent -> 0, and an
   l=0 mutation direction matching the epsilon-derivative of the exact
   nonlinear Bach tensor (nonzero) componentwise.
2. The complete linearized axial Bach rows on Schwarzschild: nonzero
   components (t,phi), (r,phi), (x,phi) only; the exact linearized trace
   identity g^{ab} dB_ab = 0 and Bianchi-type divergence identity
   nabla^a dB_ab = 0 hold componentwise.
3. Literature reproduction (required benchmark): eliminating h0 through
   the constraint row, psi = B h1 / r satisfies exactly the Regge--Wheeler
   master equation  B (B psi')' + (omega^2 - V) psi = 0  with
   V = B (6/r^2 - 6 m/r^3)  (l = 2).
4. Exact branch-split identity on the Ricci-flat background:
       delta B_ab = (1/2) Box (delta Ric)_ab + C_acbd (delta Ric)^{cd},
   componentwise, with the universal constants (1/2, 1).  Hence the
   Einstein (Regge--Wheeler) branch delta Ric = 0 injects into the Bach
   kernel, and the extra fourth-order branch is exactly the second-order
   Lichnerowicz-type wave field psi_ab := delta Ric_ab with
   (1/2) Box psi + C psi = 0.
5. On the extra-branch fixture background (non-Ricci-flat) the same
   two-term identity admits no constant-coefficient fit: the naive split
   is OBSTRUCTED there and the branch decomposition around non-Einstein
   backgrounds remains open.

NOT claimed: general l, polar sector, ingoing/outgoing operator domains,
horizon reach of the extra branch, any flux matrix or pairing, causal
well-posedness, stability, or ringdown.  This is the first block of
BH-2A, not its closure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from linearized_bach import LinearizedBach
from weyl_geometry import Geometry, mk_metric_function, static_spherical_metric

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2A_AXIAL_OPERATOR.json"
SCHEMA_PATH = HERE / "schema" / "bh2a-axial-operator-v1.schema.json"
BH0_CERT = HERE / "certificates" / "BH0_STATIC_SPHERICAL_BACKGROUND.json"

SCHEMA_NAME = "pure-weyl-bh2a-axial-operator-v1"
RESULT_ID = "PURE_WEYL_BH2A_AXIAL_OPERATOR"
RESULT_TOKEN = "BH2A_AXIAL_L2_OPERATOR_AND_BRANCH_SPLIT_CLASSIFIED"


class BH2AError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise BH2AError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    t, ph = sp.symbols("t phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    th = sp.Symbol("theta", positive=True)
    m = sp.Symbol("m", positive=True)
    w = sp.Symbol("omega")
    eps = sp.Symbol("epsilon")
    beta, gam, kk = sp.symbols("beta gamma k")
    coords = [t, r, x, ph]
    receipts = {}

    def stage(name, t0):
        receipts[name] = round(time.time() - t0, 1)
        print(f"[{name}] {receipts[name]} s", flush=True)

    # ---- 1. machinery controls (diagonal chart, cheap exact) --------------
    t0 = time.time()
    tc = [t, r, th, ph]
    B_s = 1 - 2 * m / r
    g_s = static_spherical_metric(B_s, 1 / B_s, r, th)
    geo_s = Geometry(tc, g_s)
    lb_s = LinearizedBach(geo_s)
    om_f = sp.Function("omega_c")(t, r)
    dB_conf = lb_s.build(2 * om_f * g_s)
    _require(
        all(sp.simplify(dB_conf[i, j]) == 0 for i in range(4) for j in range(4)),
        "control 1 (conformal) failed",
    )
    fx = {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), kk: sp.Rational(1, 19)}
    Bfam = mk_metric_function(beta, gam, kk, r)
    gfam = static_spherical_metric(Bfam, 1 / Bfam, r, th)
    gfx = gfam.subs(fx)
    geo_fx = Geometry(tc, gfx)
    lb_fx = LinearizedBach(geo_fx)
    dB_tan = lb_fx.build(sp.Matrix(4, 4, lambda i, j: sp.diff(gfam[i, j], beta)).subs(fx))
    _require(
        all(sp.simplify(dB_tan[i, j]) == 0 for i in range(4) for j in range(4)),
        "control 2 (family tangent) failed",
    )
    Beps = Bfam.subs(fx) + eps / (7 * r**2)
    g_eps = static_spherical_metric(Beps, 1 / Beps, r, th)
    Bach_eps = Geometry(tc, g_eps).bach()
    target = sp.Matrix(4, 4, lambda i, j: sp.diff(Bach_eps[i, j], eps).subs(eps, 0))
    dB_mut = lb_fx.build(sp.Matrix(4, 4, lambda i, j: sp.diff(g_eps[i, j], eps).subs(eps, 0)))
    _require(
        any(sp.simplify(target[i, j]) != 0 for i in range(4) for j in range(4)),
        "control 3 target unexpectedly zero",
    )
    _require(
        all(sp.simplify(dB_mut[i, j] - target[i, j]) == 0 for i in range(4) for j in range(4)),
        "control 3 (mutation vs exact nonlinear) failed",
    )
    stage("machinery_controls", t0)

    # ---- 2. axial rows on Schwarzschild, trace and divergence identities --
    t0 = time.time()
    B0 = 1 - 2 * m / r
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = Geometry(coords, g0)
    lb = LinearizedBach(geo0)
    h0 = sp.Function("h0")(t, r)
    h1 = sp.Function("h1")(t, r)
    S = -3 * x * (1 - x**2)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0 * S
    h[1, 3] = h[3, 1] = h1 * S
    dB = lb.build(h)
    nz = {(i, j) for i in range(4) for j in range(i, 4) if sp.cancel(sp.together(dB[i, j])) != 0}
    _require(nz == {(0, 3), (1, 3), (2, 3)}, f"unexpected nonzero rows {nz}")
    gi = geo0.ginv
    trace = sp.simplify(sum(gi[a, b] * dB[a, b] for a in range(4) for b in range(4)))
    _require(trace == 0, "linearized trace identity fails")
    for b in range(4):
        s = sp.Integer(0)
        for a in range(4):
            for e in range(4):
                if gi[a, e] != 0:
                    s += gi[a, e] * geo0.covd2(dB, e, a, b)
        _require(sp.simplify(sp.cancel(sp.together(s))) == 0, f"divergence identity fails at b={b}")
    stage("axial_rows_and_identities", t0)

    # ---- 3. Regge--Wheeler literature reproduction ------------------------
    t0 = time.time()
    dRic = lb.dRic
    R1 = sp.cancel(sp.cancel(sp.together(dRic[1, 3])) / S)
    R2 = sp.cancel(sp.cancel(sp.together(dRic[2, 3])) / (3 * (x - 1) * (x + 1)))
    _require(not R1.has(x) and not R2.has(x), "angular stripping failed")
    H0 = sp.Function("H0")(r)
    H1 = sp.Function("H1")(r)
    four = {h0: H0 * sp.exp(sp.I * w * t), h1: H1 * sp.exp(sp.I * w * t)}
    E = sp.exp(sp.I * w * t)
    R1f = sp.cancel(sp.together(sp.expand(R1.subs(four).doit() / E)))
    R2f = sp.cancel(sp.together(sp.expand(R2.subs(four).doit() / E)))
    H0sol = sp.solve(sp.Eq(R2f, 0), H0)[0]
    resid = sp.cancel(sp.together(
        R1f.subs({sp.Derivative(H0, r): sp.diff(H0sol, r), H0: H0sol}).doit()))
    num, _den = sp.fraction(resid)
    _require(not sp.expand(num).has(H0), "H0 not eliminated")
    psi = sp.Function("psi")(r)
    n2, _ = sp.fraction(sp.cancel(sp.together(sp.expand(num).subs(H1, r * psi / B0).doit())))
    V = B0 * (6 / r**2 - 6 * m / r**3)
    master = sp.expand(B0 * sp.diff(B0 * sp.diff(psi, r), r) + (w**2 - V) * psi)
    ratio = sp.cancel(sp.together(sp.expand(n2) / master))
    _require(not ratio.has(psi), "reduction is not proportional to the RW master equation")
    _require(sp.simplify(ratio + r**6) == 0, f"unexpected proportionality factor {ratio}")
    stage("regge_wheeler_reproduction", t0)

    # ---- 4. exact branch-split identity -----------------------------------
    t0 = time.time()
    X = dRic
    G = geo0.Gamma
    DX = [[[sp.cancel(sp.together(geo0.covd2(X, e, a, b))) for b in range(4)]
           for a in range(4)] for e in range(4)]

    def covd2X2(e, f, a, b):
        s = sp.diff(DX[f][a][b], coords[e])
        for hh in range(4):
            s -= (G[hh][e][f] * DX[hh][a][b] + G[hh][e][a] * DX[f][hh][b]
                  + G[hh][e][b] * DX[f][a][hh])
        return s

    boxX = sp.Matrix(4, 4, lambda a, b: sp.cancel(sp.together(
        sum(gi[e, f] * covd2X2(e, f, a, b) for e in range(4) for f in range(4)
            if gi[e, f] != 0))))
    Xup = sp.Matrix(4, 4, lambda c, d: sp.cancel(
        sum(gi[c, e] * gi[d, f] * X[e, f] for e in range(4) for f in range(4))))
    CX = sp.Matrix(4, 4, lambda a, b: sp.cancel(sp.together(
        sum(geo0.Weyl[a][c][b][d] * Xup[c, d] for c in range(4) for d in range(4)
            if Xup[c, d] != 0))))
    for a in range(4):
        for b in range(a, 4):
            _require(
                sp.simplify(sp.expand(sp.cancel(sp.together(
                    dB[a, b] - boxX[a, b] / 2 - CX[a, b])))) == 0,
                f"branch-split identity fails at ({a},{b})",
            )
    stage("branch_split_identity", t0)

    # ---- 5. fixture background: naive two-term identity is obstructed ------
    t0 = time.time()
    Bf = Bfam.subs(fx)
    gf = sp.diag(-Bf, 1 / Bf, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geof = Geometry(coords, gf)
    lbf2 = LinearizedBach(geof)
    dBf = lbf2.build(h)
    Xf = lbf2.dRic
    gif = geof.ginv
    Gf = geof.Gamma
    DXf = [[[sp.cancel(sp.together(geof.covd2(Xf, e, a, b))) for b in range(4)]
            for a in range(4)] for e in range(4)]

    def covd2Xf(e, f, a, b):
        s = sp.diff(DXf[f][a][b], coords[e])
        for hh in range(4):
            s -= (Gf[hh][e][f] * DXf[hh][a][b] + Gf[hh][e][a] * DXf[f][hh][b]
                  + Gf[hh][e][b] * DXf[f][a][hh])
        return s

    boxXf = sp.Matrix(4, 4, lambda a, b: sp.cancel(sp.together(
        sum(gif[e, f] * covd2Xf(e, f, a, b) for e in range(4) for f in range(4)
            if gif[e, f] != 0))))
    Xupf = sp.Matrix(4, 4, lambda c, d: sp.cancel(
        sum(gif[c, e] * gif[d, f] * Xf[e, f] for e in range(4) for f in range(4))))
    CXf = sp.Matrix(4, 4, lambda a, b: sp.cancel(sp.together(
        sum(geof.Weyl[a][c][b][d] * Xupf[c, d] for c in range(4) for d in range(4)
            if Xupf[c, d] != 0))))
    p, q = sp.symbols("p q")
    r03 = sp.expand(sp.cancel(sp.together(dBf[0, 3] - p * boxXf[0, 3] - q * CXf[0, 3])))
    a1 = sp.Derivative(h0, (r, 2))
    sol = sp.solve(
        [sp.Eq(sp.expand(r03.coeff(a1)), 0), sp.Eq(sp.expand(r03.coeff(h0)), 0)],
        [p, q], dict=True,
    )
    obstructed = True
    if sol:
        s0 = sol[0]
        if len(s0) == 2:
            resid_all = [
                sp.simplify(sp.expand(sp.cancel(sp.together(
                    dBf[i, j] - s0[p] * boxXf[i, j] - s0[q] * CXf[i, j]))))
                for i in range(4) for j in range(i, 4)
            ]
            obstructed = any(v != 0 for v in resid_all)
    _require(obstructed, "naive two-term identity unexpectedly holds on the fixture")
    stage("fixture_obstruction", t0)

    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "Schwarzschild (symbolic m) for the split theorem; three-horizon MK fixture for the obstruction",
            "conformal_frame": "working gauge; rational chart x = cos(theta)",
            "generator": "not used at this stage; operator-level statements only",
            "phase_space": "none constructed; no flux or pairing claim",
            "horizon_condition": "none imposed; operator domains open",
            "infinity_condition": "none imposed",
            "lifecycle": "CLASSIFIED",
        },
        "perturbation": {
            "sector": "axial (odd parity), l = 2, m = 0",
            "ansatz": "h_tphi = h0(t,r) S, h_rphi = h1(t,r) S, S = -3 x (1 - x**2) = sin(th) dP2/dth",
            "gauge": "Regge-Wheeler gauge (h2 = 0); l=0 gauge sectors certified separately in BH-1B",
        },
        "machinery": {
            "module": "black_hole_programme/linearized_bach.py",
            "controls": "conformal -> 0; family tangent -> 0; l=0 mutation direction matches the epsilon-derivative of the exact nonlinear Bach componentwise (nonzero)",
        },
        "axial_rows": {
            "nonzero_components": ["(t,phi)", "(r,phi)", "(x,phi)"],
            "trace_identity": "g^{ab} dB_ab = 0 exactly",
            "divergence_identity": "nabla^a dB_ab = 0 exactly (linearized Bianchi consistency)",
            "order": "fourth order in (t, r) derivatives",
        },
        "regge_wheeler_benchmark": {
            "statement": "eliminating h0 via the constraint row, psi = B h1/r satisfies B (B psi')' + (omega^2 - V) psi = 0 with V = B (6/r^2 - 6 m/r^3), exactly (proportionality factor -r^6)",
            "reference": "Regge-Wheeler axial master equation, l = 2",
        },
        "branch_split": {
            "identity": "delta B_ab = (1/2) Box (delta Ric)_ab + C_acbd (delta Ric)^{cd} on the Ricci-flat background, componentwise",
            "constants": {"p": "1/2", "q": "1"},
            "einstein_branch": "delta Ric = 0 (Regge-Wheeler) injects exactly into the Bach kernel",
            "extra_branch": "carrier psi_ab := delta Ric_ab satisfies the second-order Lichnerowicz-type wave equation (1/2) Box psi + C psi = 0; the fourth-order system is exactly the composition",
            "fixture_obstruction": "on the non-Ricci-flat extra-branch fixture no constant (p, q) reproduces delta B: the naive two-term split is OBSTRUCTED and the branch decomposition around non-Einstein backgrounds is open",
        },
        "claim_flags": {
            "machinery_controls_certified": True,
            "axial_l2_rows_certified": True,
            "trace_and_divergence_identities_certified": True,
            "regge_wheeler_reproduced": True,
            "branch_split_identity_certified": True,
            "fixture_two_term_split_obstructed": True,
            "general_l_certified": False,
            "polar_sector_certified": False,
            "operator_domains_certified": False,
            "extra_branch_horizon_reach_certified": False,
            "flux_matrix_certified": False,
            "causal_well_posedness_certified": False,
            "stability_or_ringdown_certified": False,
        },
        "missing_objects": [
            "general-l axial operator and the polar sector",
            "ingoing-horizon and outer-boundary operator domains",
            "horizon reach of the extra Lichnerowicz-type branch (indicial analysis)",
            "bilinear symplectic flux matrix and Lee-Wald pairing on both branches",
            "causal exterior well-posedness and any stability/ringdown statement",
            "branch decomposition around non-Einstein (extra-branch) backgrounds",
        ],
        "stage_seconds": receipts,
        "provenance": {
            "generator_path": "black_hole_programme/bh2a_axial_operator.py",
            "machinery_path": "black_hole_programme/linearized_bach.py",
            "machinery_sha256": _sha256(HERE / "linearized_bach.py"),
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "bh0_certificate": str(BH0_CERT.relative_to(ROOT)),
            "bh0_certificate_sha256": _sha256(BH0_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2a_axial_operator.py",
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
