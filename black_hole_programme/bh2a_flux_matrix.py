"""BH-2A stage 3: axial flux matrix and the symplectically null RW branch.

Fail-closed builder for
`black_hole_programme/certificates/BH2A_FLUX_MATRIX.json`.

Verdict: BH2A_FLUX_MATRIX_STAGE1_RW_BRANCH_SYMPLECTICALLY_NULL.

Exact results (Schwarzschild, axial l=2, rational chart x = cos theta):

1. machinery revalidation: the fast action-derived symplectic current of
   `linearized_theta.py` reproduces both certified BH-1B values;
2. the general axial bilinear: sphere-integrated symplectic density F^t
   and radial flux F^r between two arbitrary axial perturbations
   (h0a, h1a) and (h0b, h1b), stored exactly;
3. the exact OFF-SHELL identity
       d_t F^t + d_r F^r = 4 alpha Int_S2 sqrt(g) [h_B . dB(h_A) - h_A . dB(h_B)],
   which simultaneously proves on-shell conservation and pins the action
   normalization (the bilinear is the Lee--Wald current of S = alpha C^2);
4. RW-branch block: substituting on-shell Regge--Wheeler pairs
   (frequencies omega1, omega2) and reducing modulo the master equations,
       F^r = -192 pi alpha (omega1^2 - omega2^2) psi1 psi2 / (5 omega1 omega2 r),
   which VANISHES identically for conjugate pairs omega2 = +/- omega1:
   the Einstein/Regge--Wheeler branch is SYMPLECTICALLY NULL in pure Weyl
   gravity -- Einstein gravitational waves carry zero Lee--Wald flux at
   linear order in this theory;
5. independent validation: the unreduced bilinear equals the closed
   formula exactly (rational point evaluation with generic data at two
   radii, derivatives supplied by the master ODE).

Consequence: all symplectic flux pairing must live in the
Einstein x extra cross-block (critical-gravity-like structure), making the
causal disposition of the extra branch the decisive physical question.

NOT claimed: the RW x extra cross-block and extra x extra block values,
horizon/boundary flux signs on the extra family, operator domains, causal
well-posedness, general l, polar sector, or any stability/ringdown
statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from linearized_bach import LinearizedBach
from linearized_theta import LinearizedTheta
from weyl_geometry import Geometry, mk_metric_function, static_spherical_metric

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2A_FLUX_MATRIX.json"
SCHEMA_PATH = HERE / "schema" / "bh2a-flux-matrix-v1.schema.json"
BH1B_CERT = HERE / "certificates" / "BH1B_DYNAMICAL_EXTENSION.json"
BH2A_CERT = HERE / "certificates" / "BH2A_AXIAL_OPERATOR.json"

SCHEMA_NAME = "pure-weyl-bh2a-flux-matrix-v1"
RESULT_ID = "PURE_WEYL_BH2A_FLUX_MATRIX"
RESULT_TOKEN = "BH2A_FLUX_MATRIX_STAGE1_RW_BRANCH_SYMPLECTICALLY_NULL"


class FluxError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise FluxError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    t, ph = sp.symbols("t phi")
    r, th = sp.symbols("r theta", positive=True)
    x = sp.Symbol("x")
    m = sp.Symbol("m", positive=True)
    alpha = sp.Symbol("alpha")
    w1, w2 = sp.symbols("omega1 omega2")
    receipts = {}

    def stage(name, t0):
        receipts[name] = round(time.time() - t0, 1)
        print(f"[{name}] {receipts[name]} s", flush=True)

    # ---- 1. machinery revalidation against certified BH-1B values ---------
    t0 = time.time()
    tc = [t, r, th, ph]
    B_s = 1 - 2 * m / r
    g_s = static_spherical_metric(B_s, 1 / B_s, r, th)
    lt_s = LinearizedTheta(Geometry(tc, g_s), alpha)
    om_c = sp.Function("omega_c")(t, r)
    h_par = sp.Matrix(4, 4, lambda i, j: sp.diff(
        static_spherical_metric(1 - 2 * m / r, 1 / (1 - 2 * m / r), r, th)[i, j], m))
    w_cp = lt_s.omega(2 * om_c * g_s, h_par)
    _require(all(v == 0 for v in w_cp), "control: omega(conf, param) != 0")
    beta, gam, kk = sp.symbols("beta gamma k")
    fx = {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), kk: sp.Rational(1, 19)}
    Bfam = mk_metric_function(beta, gam, kk, r)
    gfam = static_spherical_metric(Bfam, 1 / Bfam, r, th)
    lt_f = LinearizedTheta(Geometry(tc, gfam.subs(fx)), alpha)
    w_bg = lt_f.omega(
        sp.Matrix(4, 4, lambda i, j: sp.diff(gfam[i, j], beta)).subs(fx),
        sp.Matrix(4, 4, lambda i, j: sp.diff(gfam[i, j], gam)).subs(fx))
    _require(
        w_bg[0] == 0 and w_bg[2] == 0 and w_bg[3] == 0
        and sp.simplify(w_bg[1] - 48 * alpha / (19 * r**2)) == 0,
        "control: static pair current mismatch",
    )
    stage("machinery_controls", t0)

    # ---- 2. general axial bilinear ---------------------------------------
    t0 = time.time()
    coords = [t, r, x, ph]
    g0 = sp.diag(-B_s, 1 / B_s, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = Geometry(coords, g0)
    lt = LinearizedTheta(geo0, alpha)
    S = -3 * x * (1 - x**2)
    h0a = sp.Function("h0a")(t, r); h1a = sp.Function("h1a")(t, r)
    h0b = sp.Function("h0b")(t, r); h1b = sp.Function("h1b")(t, r)
    hA = sp.zeros(4, 4); hA[0, 3] = hA[3, 0] = h0a * S; hA[1, 3] = hA[3, 1] = h1a * S
    hB = sp.zeros(4, 4); hB[0, 3] = hB[3, 0] = h0b * S; hB[1, 3] = hB[3, 1] = h1b * S
    w = lt.omega(hA, hB)
    _require(w[3] == 0, "phi component of omega nonzero")
    Ft = sp.simplify(sp.cancel(sp.together(
        sp.integrate(sp.integrate(w[0] * r**2, (x, -1, 1)), (ph, 0, 2 * sp.pi)))))
    Fr = sp.simplify(sp.cancel(sp.together(
        sp.integrate(sp.integrate(w[1] * r**2, (x, -1, 1)), (ph, 0, 2 * sp.pi)))))
    _require(Ft != 0 and Fr != 0, "bilinear unexpectedly zero")
    stage("axial_bilinear", t0)

    # ---- 3. off-shell 4 alpha identity ------------------------------------
    t0 = time.time()
    D = sp.expand(sp.diff(Ft, t) + sp.diff(Fr, r))
    lbA = LinearizedBach(geo0)
    dBA = lbA.build(hA)
    lbB = LinearizedBach(geo0)
    dBB = lbB.build(hB)
    gi = geo0.ginv

    def contract(h, dB):
        s = sp.Integer(0)
        for b in range(4):
            for c in range(4):
                if h[b, c] == 0:
                    continue
                up = sum(gi[b, p] * gi[c, q] * dB[p, q] for p in range(4) for q in range(4))
                s += h[b, c] * up
        return s

    integrand = sp.cancel(sp.together(contract(hB, dBA) - contract(hA, dBB))) * r**2
    Xi = sp.expand(sp.simplify(sp.cancel(sp.together(
        sp.integrate(sp.integrate(integrand, (x, -1, 1)), (ph, 0, 2 * sp.pi))))))
    _require(sp.simplify(sp.expand(D - 4 * alpha * Xi)) == 0, "off-shell identity fails")
    stage("offshell_identity", t0)

    # ---- 4. RW-branch block ------------------------------------------------
    t0 = time.time()
    lb = LinearizedBach(geo0)
    h0f = sp.Function("h0")(t, r)
    h1f = sp.Function("h1")(t, r)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0f * S
    h[1, 3] = h[3, 1] = h1f * S
    lb.build(h)
    R2 = sp.cancel(sp.cancel(sp.together(lb.dRic[2, 3])) / (3 * (x - 1) * (x + 1)))
    H0s = sp.Symbol("H0s")
    E1 = sp.exp(sp.I * w1 * t)
    R2f = sp.cancel(sp.together(sp.expand(
        R2.subs({h0f: H0s * E1, h1f: sp.Function("H1")(r) * E1}).doit() / E1)))
    H0expr = sp.solve(sp.Eq(R2f, 0), H0s)[0]
    H1g = sp.Function("H1")(r)
    psi1 = sp.Function("psi1")(r)
    psi2 = sp.Function("psi2")(r)
    E2 = sp.exp(sp.I * w2 * t)
    B0 = B_s
    H0e_1 = H0expr.subs({H1g: r * psi1 / B0,
                         sp.Derivative(H1g, r): sp.diff(r * psi1 / B0, r)}).doit()
    H0e_2 = H0expr.subs({H1g: r * psi2 / B0,
                         sp.Derivative(H1g, r): sp.diff(r * psi2 / B0, r), w1: w2}).doit()
    subs_map = {
        h0a: H0e_1 * E1, h1a: (r * psi1 / B0) * E1,
        h0b: H0e_2 * E2, h1b: (r * psi2 / B0) * E2,
    }
    Fr_sub = sp.expand(sp.cancel(sp.together(Fr.subs(subs_map).doit() / (E1 * E2))))
    V = B0 * (6 / r**2 - 6 * m / r**3)

    def reduce_master(expr, psi, wv):
        p2 = (-(sp.diff(B0, r) / B0) * sp.Derivative(psi, r)
              - (wv**2 - V) / B0**2 * psi)
        for _ in range(4):
            expr = expr.subs(sp.Derivative(psi, (r, 4)), sp.diff(p2, r, 2))
            expr = expr.subs(sp.Derivative(psi, (r, 3)), sp.diff(p2, r))
            expr = expr.subs(sp.Derivative(psi, (r, 2)), p2)
            expr = sp.expand(expr.doit())
        return expr

    Fr_rw = sp.simplify(sp.cancel(sp.together(
        reduce_master(reduce_master(Fr_sub, psi1, w1), psi2, w2))))
    closed = -192 * sp.pi * alpha * (w1 - w2) * (w1 + w2) * psi1 * psi2 / (5 * w1 * w2 * r)
    _require(sp.simplify(Fr_rw - closed) == 0, f"RW block mismatch: {Fr_rw}")
    _require(sp.simplify(closed.subs(w2, w1)) == 0
             and sp.simplify(closed.subs(w2, -w1)) == 0,
             "conjugate-pair null check failed")
    stage("rw_block", t0)

    # ---- 5. independent point validation ----------------------------------
    t0 = time.time()
    mval = sp.Integer(1)
    wvals = {w1: sp.Integer(1), w2: sp.Integer(2)}
    for r0, data1, data2 in [
        (sp.Integer(5), (sp.Integer(1), sp.Rational(1, 3)), (sp.Rational(2, 7), sp.Integer(1))),
        (sp.Integer(7), (sp.Rational(3, 2), sp.Rational(-1, 4)), (sp.Integer(2), sp.Rational(1, 5))),
    ]:
        vals = {}
        for psi, wv, (a0, b0) in [(psi1, 1, data1), (psi2, 2, data2)]:
            p2 = (-(sp.diff(B0, r) / B0) * sp.Derivative(psi, r)
                  - (wv**2 - V) / B0**2 * psi)
            d = {psi: a0, sp.Derivative(psi, r): b0}
            d[sp.Derivative(psi, (r, 2))] = sp.nsimplify(
                p2.subs({m: mval}).subs(d).subs(r, r0))
            d[sp.Derivative(psi, (r, 3))] = sp.nsimplify(
                sp.diff(p2, r).subs({m: mval}).subs(d).subs(r, r0))
            d[sp.Derivative(psi, (r, 4))] = sp.nsimplify(
                sp.diff(p2, r, 2).subs({m: mval}).subs(d).subs(r, r0))
            vals.update(d)
        lhs = sp.simplify(Fr_sub.subs({m: mval, **wvals}).subs(vals).subs(r, r0))
        rhs = sp.simplify(closed.subs({m: mval, **wvals}).subs(vals).subs(r, r0))
        _require(sp.simplify(lhs - rhs) == 0, f"point validation fails at r0={r0}")
    stage("point_validation", t0)

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
            "conformal_frame": "working gauge; rational chart x = cos theta",
            "generator": "none; bilinear symplectic statements only",
            "phase_space": "linear axial l=2 perturbations; sphere-integrated Lee-Wald current",
            "horizon_condition": "none imposed at this stage",
            "infinity_condition": "none imposed at this stage",
            "lifecycle": "CLASSIFIED",
        },
        "bilinear": {
            "F_t": sp.sstr(Ft),
            "F_r": sp.sstr(Fr),
            "construction": "corrected symplectic current of linearized_theta.py (density variation), sphere-integrated with measure r^2 dx dphi",
        },
        "offshell_identity": {
            "statement": "d_t F^t + d_r F^r = 4*alpha * Int_S2 r^2 [h_B.dB(h_A) - h_A.dB(h_B)] dx dphi, exactly, off shell",
            "consequences": "on-shell conservation; the bilinear is the action-derived Lee-Wald current with pinned normalization",
        },
        "rw_block": {
            "on_shell_flux": "F^r = -192*pi*alpha*(omega1**2 - omega2**2)*psi1*psi2/(5*omega1*omega2*r)",
            "null_statement": "vanishes identically for conjugate pairs omega2 = +/- omega1: the Einstein/Regge-Wheeler branch is symplectically null in pure Weyl gravity",
            "validation": "unreduced bilinear equals the closed formula by exact rational point evaluation at r0 = 5 and r0 = 7 with generic data (ODE-supplied derivatives)",
        },
        "interpretation": {
            "structure": "all symplectic flux pairing must live in the Einstein x extra cross-block (critical-gravity-like); consistent with the certified H = 0 static Schwarzschild sector and the extra branch reaching the horizon",
            "consequence": "the causal/boundary disposition of the extra branch decides whether pure-Weyl black-hole radiation carries flux",
        },
        "claim_flags": {
            "machinery_revalidated_certified": True,
            "axial_bilinear_certified": True,
            "offshell_identity_certified": True,
            "rw_block_certified": True,
            "rw_branch_null_certified": True,
            "point_validation_certified": True,
            "cross_block_certified": False,
            "extra_block_certified": False,
            "horizon_flux_signs_certified": False,
            "operator_domains_certified": False,
            "causal_disposition_decided": False,
            "stability_or_ringdown_certified": False,
        },
        "missing_objects": [
            "RW x extra cross-block and extra x extra block of the flux matrix",
            "horizon and outer-boundary flux signs on the ingoing-regular extra family",
            "operator domains and causal disposition of the extra branch",
            "general l, polar sector, non-Einstein backgrounds",
            "any stability or ringdown statement",
        ],
        "stage_seconds": receipts,
        "provenance": {
            "generator_path": "black_hole_programme/bh2a_flux_matrix.py",
            "machinery_paths": ["black_hole_programme/linearized_theta.py",
                                 "black_hole_programme/linearized_bach.py"],
            "machinery_sha256": {
                "linearized_theta": _sha256(HERE / "linearized_theta.py"),
                "linearized_bach": _sha256(HERE / "linearized_bach.py"),
            },
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "bh1b_certificate": str(BH1B_CERT.relative_to(ROOT)),
            "bh1b_certificate_sha256": _sha256(BH1B_CERT),
            "bh2a_certificate": str(BH2A_CERT.relative_to(ROOT)),
            "bh2a_certificate_sha256": _sha256(BH2A_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2a_flux_matrix.py",
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
