"""BH-1A: normalized generator, boundary ensembles, entropy and first law.

Fail-closed builder for
`black_hole_programme/certificates/BH1A_NORMALIZED_GENERATOR.json`.

Verdict: BH1_NONINTEGRABILITY_REMOVED_BY_FIELD_DEPENDENT_GENERATOR.

Exact results (all sympy-exact, on the static MK family with the bare
charges of the BH-1 preflight certificate, pinned by hash):

1. Frobenius: F ^ dF = 0, so an integrating factor exists.
2. Basicness fixes the normalization: N must be invariant under the
   residual c-map and carry dilation weight -1; the invariant ring forces
   N = u * f(J) with u = beta*(2 - 3*beta*gamma).  For N = u the
   normalized charge form u*F is exactly closed, horizontal, and
   Lie-invariant for both residual generators (fully basic).
3. Exact Hamiltonian: H = -16*pi*alpha*beta**2*D2 with
   D2 = 9*beta**2*gamma**2*k - beta*gamma**3 - 12*beta*gamma*k
        + gamma**2 + 4*k,
   and J = -u**2*D1*D2 (D1 = 27*beta**2*k - 3*beta*gamma - 1), so H
   vanishes exactly on the D2-branch of the degenerate-horizon locus.
   dH ^ dJ = 0: H is functionally dependent on the single residual
   invariant J, as basicness requires.  The f(J) freedom in N only
   reparametrizes H = G(J).
4. Wald entropy S = -2*pi Int E^{abcd} eps_ab eps_cd dA
   = 64*pi**2*alpha*beta*(2 - 3*beta*gamma + gamma*r_h)/r_h.
5. First law with T = kappa_N/(2*pi) = u*B'(r_h)/(4*pi):
   dH - T dS = 0 identically modulo the horizon condition B(r_h) = 0,
   for all three parameter directions and at EVERY simple root, hence
   the exact multi-horizon identity T_i dS_i = dH.
6. Ensemble audit: the only residual c preserving a fixed-falloff
   ensemble {gamma, k fixed} is c = 0 away from the exact locus
   u*(w**2 - 3) = 0 (w = 1 - 3*beta*gamma; w**2 = 3 is never rational);
   the dilation preserves an ensemble only at lambda = 1 except on the
   Schwarzschild sub-ensemble gamma = k = 0, where it acts freely and
   consistently (H = 0, S constant there).

Orientation caveat: sign(u) = sign(2 - 3*beta*gamma); on components where
u < 0 (e.g. the three-horizon fixture) the future-directed normalization
is N = -u and all charges flip sign.  N is fixed up to this component
sign and the f(J) reparametrization.

NOT claimed: any dynamical (time-dependent) perturbation, presymplectic
form beyond the static slice, stability, uniqueness of the horizon
generator among non-static candidates, or the full BH-1 phase-space
theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from weyl_geometry import Geometry, mk_metric_function, static_spherical_metric

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH1A_NORMALIZED_GENERATOR.json"
SCHEMA_PATH = HERE / "schema" / "bh1a-normalized-generator-v1.schema.json"
BH0_CERT = HERE / "certificates" / "BH0_STATIC_SPHERICAL_BACKGROUND.json"
BH1_CERT = HERE / "certificates" / "BH1_LEE_WALD_PREFLIGHT.json"

SCHEMA_NAME = "pure-weyl-bh1a-normalized-generator-v1"
RESULT_ID = "PURE_WEYL_BH1A_NORMALIZED_GENERATOR"
RESULT_TOKEN = "BH1_NONINTEGRABILITY_REMOVED_BY_FIELD_DEPENDENT_GENERATOR"


class BH1AError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise BH1AError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    beta, gam, k, alpha = sp.symbols("beta gamma k alpha")
    rh = sp.Symbol("r_h")
    x, c, lam = sp.symbols("x c lambda")
    ps = [beta, gam, k]

    u = beta * (2 - 3 * beta * gam)
    w = 1 - 3 * beta * gam
    D1 = 27 * beta**2 * k - 3 * beta * gam - 1
    D2 = 9 * beta**2 * gam**2 * k - beta * gam**3 - 12 * beta * gam * k + gam**2 + 4 * k
    Q = -u * x**3 + w * x**2 + gam * x - k
    J = sp.expand(u**2 * sp.discriminant(Q, x))
    _require(sp.simplify(J + u**2 * D1 * D2) == 0, "J != -u^2 D1 D2")

    # ---- bare charges: pinned import, revalidated against closed forms ----
    bh1 = json.loads(BH1_CERT.read_text(encoding="utf-8"))
    SYM = {"beta": beta, "gamma": gam, "k": k, "alpha": alpha, "pi": sp.pi}
    F = [
        sp.sympify(bh1["bare_charges"]["F_beta"], locals=dict(SYM)),
        sp.sympify(bh1["bare_charges"]["F_gamma"], locals=dict(SYM)),
        sp.sympify(bh1["bare_charges"]["F_k"], locals=dict(SYM)),
    ]
    _require(
        sp.simplify(F[0] - 16 * sp.pi * alpha * (12 * beta * gam * k - gam**2 - 4 * k)) == 0
        and sp.simplify(F[1] - 16 * sp.pi * alpha * beta * (6 * beta * k - gam)) == 0
        and sp.simplify(F[2] - 16 * sp.pi * alpha * beta * (3 * beta * gam - 2)) == 0,
        "imported bare charges differ from certified closed forms",
    )

    # ---- 1. Frobenius --------------------------------------------------------
    dF = {
        (i, j): sp.expand(sp.diff(F[j], ps[i]) - sp.diff(F[i], ps[j]))
        for i in range(3)
        for j in range(i + 1, 3)
    }
    frob = sp.simplify(F[0] * dF[(1, 2)] - F[1] * dF[(0, 2)] + F[2] * dF[(0, 1)])
    _require(frob == 0, f"Frobenius F^dF = {frob} != 0")

    # ---- 2. basicness constraints on N and closure of u F -------------------
    gen_c = [-3 * beta**2, 6 * beta * gam - 2, gam]
    gen_l = [-beta, gam, 2 * k]
    Xc = lambda f: sum(v * sp.diff(f, p) for v, p in zip(gen_c, ps))  # noqa: E731
    Xl = lambda f: sum(v * sp.diff(f, p) for v, p in zip(gen_l, ps))  # noqa: E731
    _require(sp.simplify(Xc(u)) == 0, "u is not c-invariant")
    _require(sp.simplify(Xl(u) + u) == 0, "u does not have dilation weight -1")
    NF = [sp.expand(u * e) for e in F]
    for (i, j) in [(0, 1), (0, 2), (1, 2)]:
        _require(
            sp.simplify(sp.diff(NF[j], ps[i]) - sp.diff(NF[i], ps[j])) == 0,
            "u F is not closed",
        )
    _require(
        sp.simplify(sum(nf * v for nf, v in zip(NF, gen_c))) == 0
        and sp.simplify(sum(nf * v for nf, v in zip(NF, gen_l))) == 0,
        "u F is not horizontal for the residual generators",
    )
    # control: the bare (N = 1) form must NOT be closed
    _require(any(v != 0 for v in dF.values()), "control failed: bare dF = 0")

    # ---- 3. exact Hamiltonian ------------------------------------------------
    H = -16 * sp.pi * alpha * beta**2 * D2
    for p, nf in zip(ps, NF):
        _require(sp.simplify(sp.diff(H, p) - nf) == 0, f"dH/d{p} != (uF)_{p}")
    dJ = [sp.diff(J, p) for p in ps]
    dH = [sp.diff(H, p) for p in ps]
    for (i, j) in [(0, 1), (0, 2), (1, 2)]:
        _require(
            sp.simplify(dJ[i] * dH[j] - dJ[j] * dH[i]) == 0,
            "dH ^ dJ != 0: H not functionally dependent on J",
        )

    # ---- 4. Wald entropy -----------------------------------------------------
    t, ph = sp.symbols("t phi")
    r, th = sp.symbols("r theta", positive=True)
    MK = mk_metric_function(beta, gam, k, r)
    geo = Geometry([t, r, th, ph], static_spherical_metric(MK, 1 / MK, r, th))
    C_up_trtr = sp.simplify(geo.ginv[0, 0] ** 2 * geo.ginv[1, 1] ** 2 * geo.Weyl[0][1][0][1])
    S_r = sp.simplify(-2 * sp.pi * (2 * alpha) * 4 * C_up_trtr * 4 * sp.pi * r**2)
    S_expected = 64 * sp.pi**2 * alpha * beta * (2 - 3 * beta * gam + gam * r) / r
    _require(sp.simplify(S_r - S_expected) == 0, "Wald entropy closed form mismatch")
    S = S_expected.subs(r, rh)
    _require(
        sp.simplify(S.subs({gam: 0, rh: 2 * beta}) - 64 * sp.pi**2 * alpha) == 0,
        "Schwarzschild entropy is not the constant 64 pi^2 alpha",
    )

    # ---- 5. first law modulo the horizon condition ---------------------------
    B_rh = w - u / rh + gam * rh - k * rh**2
    Bp = sp.diff(w - u / r + gam * r - k * r**2, r).subs(r, rh)
    P = sp.expand(rh * B_rh)
    T = u * Bp / (4 * sp.pi)
    for p in ps:
        dS_p = sp.diff(S, p) + sp.diff(S, rh) * (-sp.diff(B_rh, p) / Bp)
        X = sp.together(sp.diff(H, p) - T * dS_p)
        num, den = sp.fraction(sp.cancel(X))
        numred = sp.rem(sp.expand(num), P, rh)
        _require(
            sp.simplify(sp.cancel(numred / den)) == 0,
            f"first law fails in direction {p}",
        )

    # ---- 6. ensemble and admissibility audit ---------------------------------
    gt = gam - 2 * c * w - 3 * c**2 * u
    kt = k + c * gam - c**2 * w - c**3 * u
    sols = sp.solve([sp.Eq(gt, gam), sp.Eq(kt, k)], c, dict=True)
    _require(sols == [{c: 0}], f"ensemble-preserving c not unique: {sols}")
    locus = sp.factor(
        sp.resultant(sp.expand((gt - gam) / c), sp.expand((kt - k) / c), c)
    )
    _require(
        sp.simplify(locus - beta * (3 * beta * gam - 2) * (9 * beta**2 * gam**2 - 6 * beta * gam - 2)) == 0,
        f"nonzero-c locus unexpected: {locus}",
    )
    _require(
        sp.simplify(sp.expand(9 * beta**2 * gam**2 - 6 * beta * gam - 2 - (w**2 - 3))) == 0,
        "locus factor is not w^2 - 3",
    )
    dil = sp.solve([sp.Eq(lam * gam, gam), sp.Eq(lam**2 * k, k)], lam, dict=True)
    _require({lam: 1} in dil, "dilation ensemble solve unexpected")
    _require(
        sp.simplify(H.subs({gam: 0, k: 0})) == 0
        and sp.simplify(S.subs({gam: 0}) - 128 * sp.pi**2 * alpha * beta / rh) == 0,
        "Schwarzschild sub-ensemble consistency failed",
    )

    # ---- fixture data ---------------------------------------------------------
    fx = {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), k: sp.Rational(1, 19)}
    ufx = sp.nsimplify(u.subs(fx))
    _require(ufx == sp.Rational(-24, 19), "fixture u unexpected")
    Hfx = sp.simplify(H.subs(fx))
    horizons = []
    for r0 in (1, 3, 8):
        Sfx = sp.nsimplify(S.subs(fx).subs(rh, r0))
        Tfx = sp.nsimplify(T.subs(fx).subs(rh, r0))
        # exact directional first-law test at the fixture
        for p in ps:
            dS_p = sp.diff(S, p) + sp.diff(S, rh) * (-sp.diff(B_rh, p) / Bp)
            lhs = sp.simplify((sp.diff(H, p) - T * dS_p).subs(fx).subs(rh, r0))
            _require(lhs == 0, f"fixture first law fails at r={r0}, direction {p}")
        horizons.append(
            {"r": str(r0), "S": sp.sstr(Sfx), "T": sp.sstr(Tfx)}
        )

    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "MK static spherical Bach vacuum (BH-0)",
            "conformal_frame": "working gauge b = 1/a; no physical frame declared",
            "generator": "normalized field-dependent chi = N d_t with N = u = beta*(2 - 3*beta*gamma), unique up to component sign (future-directedness) and f(J) reparametrization",
            "phase_space": "static parameter slice; variations d_beta, d_gamma, d_k only",
            "horizon_condition": "any simple root of B; first law certified modulo B(r_h) = 0 at every root",
            "infinity_condition": "fixed-falloff ensembles {gamma, k fixed} audited against the residual group",
            "lifecycle": "PREFLIGHT",
        },
        "normalization": {
            "N": "u = beta*(2 - 3*beta*gamma)",
            "why": "basicness: N must be c-invariant with dilation weight -1; the invariant ring forces N = u*f(J)",
            "frobenius": "F ^ dF = 0 exactly",
            "field_dependent_correction": "for spacetime-constant N the Q_{delta chi} correction cancels the dN terms exactly, so the corrected charge form is N*F",
            "closure": "d(u F) = 0 exactly on the full static family",
            "basicness": "iota and Lie derivative of u F vanish for both residual generators",
            "bare_control": "d F != 0 for N = 1 (bare form remains nonintegrable)",
            "orientation_caveat": "sign(u) = sign(2 - 3*beta*gamma); use N = -u on components with u < 0 for a future-directed generator (all charges flip sign)",
        },
        "hamiltonian": {
            "H": sp.sstr(sp.expand(H)),
            "H_factored": "-16*pi*alpha*beta**2*D2",
            "D1": sp.sstr(D1),
            "D2": sp.sstr(D2),
            "discriminant_relation": "J = -u**2*D1*D2, so H vanishes exactly on the D2-branch of the degenerate-horizon locus",
            "basic_on_quotient": "dH ^ dJ = 0: H is functionally dependent on the single residual invariant J",
            "einstein_control_ensemble": "Schwarzschild-(A)dS slice gamma = 0: H = -64*pi*alpha*beta**2*k; one-boundary AdS control has k < 0",
        },
        "wald_entropy": {
            "S": "64*pi**2*alpha*beta*(2 - 3*beta*gamma + gamma*r_h)/r_h",
            "construction": "S = -2*pi Int E^{abcd} eps_ab eps_cd dA with E = 2*alpha*C^{abcd}, eps_tr = 1",
            "schwarzschild_value": "64*pi**2*alpha, mass-independent, consistent with H = 0 on that ensemble",
        },
        "first_law": {
            "temperature": "T = kappa_N/(2*pi) = u*B'(r_h)/(4*pi)",
            "statement": "dH - T dS = 0 identically modulo B(r_h) = 0, in all three parameter directions, at every simple root",
            "multi_horizon_identity": "T_i dS_i = dH for every horizon r_i simultaneously; verified exactly at the fixture roots 1, 3, 8",
            "no_extra_terms": "no boundary source or pressure-volume term is needed on the static family in this normalization",
        },
        "ensemble_audit": {
            "c_preservation": "the only residual c preserving a fixed-falloff ensemble {gamma, k fixed} is c = 0",
            "nonzero_c_locus": "u*(w**2 - 3) = 0 with w = 1 - 3*beta*gamma; w**2 = 3 is never satisfied at rational parameters, u = 0 degenerates the normalization",
            "dilation_preservation": "lambda = 1 unless gamma = k = 0; on the Schwarzschild sub-ensemble the dilation acts freely and consistently (H = 0, S constant)",
            "global_admissibility": "the c-map factor Omega = 1/(1 + c*r) is smooth and positive on an exterior [r_h, r_out] iff 1 + c*r > 0 there, i.e. c > -1/r_out; on any fixed-falloff ensemble the residual directions are frozen anyway",
        },
        "horizon_fixture": {
            "parameters": {"beta": "3/2", "gamma": "12/19", "k": "1/19"},
            "u": sp.sstr(ufx),
            "H": sp.sstr(Hfx),
            "horizons": horizons,
            "first_law_directional_test": "dH = T dS verified exactly at r = 1, 3, 8 in all three parameter directions",
        },
        "claim_flags": {
            "frobenius_certified": True,
            "normalized_form_closed_certified": True,
            "normalized_form_basic_certified": True,
            "hamiltonian_potential_certified": True,
            "wald_entropy_certified": True,
            "static_first_law_certified": True,
            "ensemble_audit_certified": True,
            "full_bh1_phase_space_certified": False,
            "dynamical_perturbation_flux_certified": False,
            "generator_unique_among_nonstatic_certified": False,
            "stability_certified": False,
            "quantum_or_hawking_certified": False,
        },
        "missing_objects": [
            "presymplectic form and charges for time-dependent perturbations (full BH-1)",
            "uniqueness of the normalized generator among non-static candidates",
            "physical matter/clock frame and its horizon regularity",
            "Lorentzian causal exterior theorem (BH-2 gate)",
            "any stability, ringdown, or quantum statement",
        ],
        "provenance": {
            "generator_path": "black_hole_programme/bh1a_normalized_generator.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "bh0_certificate": str(BH0_CERT.relative_to(ROOT)),
            "bh0_certificate_sha256": _sha256(BH0_CERT),
            "bh1_certificate": str(BH1_CERT.relative_to(ROOT)),
            "bh1_certificate_sha256": _sha256(BH1_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh1a_normalized_generator.py",
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
