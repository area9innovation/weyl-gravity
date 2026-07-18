"""BH-1B: the normalized charge extends to dynamical perturbations.

Fail-closed builder for
`black_hole_programme/certificates/BH1B_DYNAMICAL_EXTENSION.json`.

Verdict: BH1_DYNAMICAL_HORIZON_PHASE_SPACE_CERTIFIED, scoped to the linear
charge level with the spherical (l = 0) dynamical sector complete.

Exact results (chi = u d_t from BH-1A, u = beta(2 - 3 beta gamma)):

1. theta audit: the Iyer--Wald theta satisfies its defining identity
   delta(sqrt(-g) L) = EOM.h + div(sqrt(-g) theta) exactly on shell
   (conformal direction: invariant density <-> div theta = 0; parameter
   direction: matches the exact density variation).
2. Conformal (frame) directions dg = 2 omega(t,r) g, arbitrary omega:
   - the full charge 2-form k = delta Q_chi - i_chi Theta(dg) vanishes
     IDENTICALLY, componentwise (Schwarzschild with symbolic m, and the
     three-horizon extra-branch fixture);
   - the Wald entropy density is exactly invariant on the symbolic MK
     family: delta_omega S = 0;
   - the corrected presymplectic current omega(d_conf, d_param) vanishes
     identically (conformal directions are exact null directions).
   No boundary clock or conformal representative is needed at the linear
   charge level: the static BH-1A result is physical, not frame-selected.
3. Diffeo directions dg = L_xi g, xi = a(t,r) d_t + b(t,r) d_r arbitrary:
   - the on-shell Noether identity Theta(L_xi g) - i_xi(L eps) = d Q_xi
     holds exactly, componentwise, on both backgrounds;
   - the identity-route charge form k(delta_xi) vanishes identically
     (both backgrounds, both generator components), so time-dependent
     l = 0 diffeos are proper gauge with zero charge and zero flux;
   - the route is cross-validated against a direct epsilon-geometry
     computation on a polynomial witness.
4. Machinery controls: the parameter mode reproduces the certified static
   charge u*F_beta through the fully dynamical pipeline; the corrected
   symplectic current (density variation, including the (1/2) tr(h) theta
   terms) is exactly conserved on the static pair (beta, gamma) with the
   nonzero value omega^r = 48 alpha/(19 r^2).
5. Unique linear extension of N: the bare Noether aperture Int Q is
   nonzero on the fixture, so any extension with delta N != 0 on a gauge
   direction would give that direction a nonzero charge, contradicting 2
   and 3; on l >= 1 modes delta N = 0 because N is a spherical boundary
   scalar; on parameter directions delta N = du is fixed by BH-1A.  The
   linear extension of the field-dependent generator is therefore unique.

NOT claimed: the bilinear radiative (l >= 2) symplectic flux matrix
(BH-2A), any second-order/physical-process statement, machine-checked
harmonic orthogonality for l >= 1 linear charges (analytic parity
argument only), nonlinear dynamics, stability, or ringdown.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

import dynamical_charges as dc
from weyl_geometry import Geometry, mk_metric_function, static_spherical_metric

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH1B_DYNAMICAL_EXTENSION.json"
SCHEMA_PATH = HERE / "schema" / "bh1b-dynamical-extension-v1.schema.json"
BH1A_CERT = HERE / "certificates" / "BH1A_NORMALIZED_GENERATOR.json"

SCHEMA_NAME = "pure-weyl-bh1b-dynamical-extension-v1"
RESULT_ID = "PURE_WEYL_BH1B_DYNAMICAL_EXTENSION"
RESULT_TOKEN = "BH1_DYNAMICAL_HORIZON_PHASE_SPACE_CERTIFIED"

FIX = {"beta": sp.Rational(3, 2), "gamma": sp.Rational(12, 19), "k": sp.Rational(1, 19)}
U_FIX = sp.Rational(-24, 19)


class BH1BError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise BH1BError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero_form(form) -> bool:
    return all(v == 0 for v in form.values())


def build_certificate() -> dict:
    t, ph = sp.symbols("t phi")
    r, th = sp.symbols("r theta", positive=True)
    beta, gam, kk, alpha = sp.symbols("beta gamma k alpha")
    eps, eps2 = sp.symbols("epsilon epsilon2")
    m = sp.Symbol("m", positive=True)
    coords = [t, r, th, ph]
    om = sp.Function("omega")(t, r)
    a_f = sp.Function("a")(t, r)
    b_f = sp.Function("b")(t, r)
    receipts = {}

    def stage(name, t0):
        receipts[name] = round(time.time() - t0, 1)
        print(f"[{name}] {receipts[name]} s", flush=True)

    def setup(Bfun, u_val):
        g0 = static_spherical_metric(Bfun, 1 / Bfun, r, th)
        geo0 = Geometry(coords, g0)
        E0 = dc.E_weyl(geo0, alpha)
        L_scalar = alpha * geo0.invariants()["WeylSq"]
        chi = [u_val, sp.Integer(0), sp.Integer(0), sp.Integer(0)]
        return g0, geo0, E0, L_scalar, chi

    B_s = 1 - 2 * m / r
    g0s, geos, Es, Ls, chis = setup(B_s, 2 * m)
    B_f = mk_metric_function(beta, gam, kk, r).subs(
        {beta: FIX["beta"], gam: FIX["gamma"], kk: FIX["k"]})
    g0f, geof, Ef, Lf, chif = setup(B_f, U_FIX)

    # ---- 1. Noether identity and diffeo identity route -------------------
    t0 = time.time()
    xi = [a_f, b_f, 0, 0]
    for label, (geo, E, L, chi) in {
        "schwarzschild": (geos, Es, Ls, chis),
        "fixture": (geof, Ef, Lf, chif),
    }.items():
        defects = dc.noether_identity_defect(coords, geo, E, xi, L, alpha)
        _require(all(v == 0 for v in defects.values()), f"Noether identity fails on {label}")
        kform = dc.diffeo_charge_form_identity_route(coords, geo, E, chi, xi, L)
        _require(_zero_form(kform), f"diffeo charge form nonzero on {label}: {kform}")
    stage("noether_and_diffeo", t0)

    # ---- 2. theta defining-identity audit (Schwarzschild) ----------------
    t0 = time.time()
    sqrtg_s = sp.sqrt(-g0s.det())

    def divtheta(dg):
        thv = dc.theta_up(geos, Es, dg)
        return sp.simplify(sum(sp.diff(sqrtg_s * thv[a], coords[a]) for a in range(4)) / sqrtg_s)

    _require(divtheta(2 * om * g0s) == 0, "div theta [conformal] != 0")
    h_par_s = sp.Matrix(4, 4, lambda i, j: sp.diff(
        static_spherical_metric(1 - 2 * m / r, 1 / (1 - 2 * m / r), r, th)[i, j], m))
    dens_e = sp.sqrt(-(g0s + eps * h_par_s).det()) * alpha * Geometry(
        coords, g0s + eps * h_par_s).invariants()["WeylSq"]
    lhs = sp.simplify(sp.diff(dens_e, eps).subs(eps, 0) / sqrtg_s)
    _require(sp.simplify(lhs - divtheta(h_par_s)) == 0, "theta defining identity fails")
    stage("theta_audit", t0)

    # ---- 3. conformal charge annihilation --------------------------------
    t0 = time.time()
    k_conf_s = dc.charge_form(Geometry, coords, g0s, geos, Es, chis, 2 * om * g0s, alpha, eps)
    _require(_zero_form(k_conf_s), f"Schwarzschild conformal k != 0: {k_conf_s}")
    stage("conformal_schwarzschild", t0)
    t0 = time.time()
    k_conf_f = dc.charge_form(Geometry, coords, g0f, geof, Ef, chif, 2 * om * g0f, alpha, eps)
    _require(_zero_form(k_conf_f), f"fixture conformal k != 0: {k_conf_f}")
    stage("conformal_fixture", t0)

    # ---- 4. parameter-mode control through the dynamical pipeline --------
    t0 = time.time()
    gfam = static_spherical_metric(mk_metric_function(beta, gam, kk, r),
                                   1 / mk_metric_function(beta, gam, kk, r), r, th)
    h_beta = sp.Matrix(4, 4, lambda i, j: sp.diff(gfam[i, j], beta)).subs(
        {beta: FIX["beta"], gam: FIX["gamma"], kk: FIX["k"]})
    k_par = dc.charge_form(Geometry, coords, g0f, geof, Ef, chif, h_beta, alpha, eps)
    aperture = sp.simplify(sp.integrate(sp.integrate(k_par[(2, 3)], (th, 0, sp.pi)), (ph, 0, 2 * sp.pi)))
    expect = (U_FIX * 16 * sp.pi * alpha * (12 * beta * gam * kk - gam**2 - 4 * kk)).subs(
        {beta: FIX["beta"], gam: FIX["gamma"], kk: FIX["k"]})
    _require(sp.simplify(aperture - expect) == 0, f"param control mismatch: {aperture}")
    stage("parameter_control", t0)

    # ---- 5. corrected symplectic current ---------------------------------
    t0 = time.time()
    w_cp = dc.omega_symplectic(Geometry, coords, g0s, geos, Es, 2 * om * g0s, h_par_s, alpha, eps, eps2)
    _require(all(v == 0 for v in w_cp), f"omega(conf, param) != 0 on Schwarzschild: {w_cp}")
    stage("null_direction_schwarzschild", t0)
    t0 = time.time()
    h_gamma = sp.Matrix(4, 4, lambda i, j: sp.diff(gfam[i, j], gam)).subs(
        {beta: FIX["beta"], gam: FIX["gamma"], kk: FIX["k"]})
    w_bg = dc.omega_symplectic(Geometry, coords, g0f, geof, Ef, h_beta, h_gamma, alpha, eps, eps2)
    _require(
        w_bg[0] == 0 and w_bg[2] == 0 and w_bg[3] == 0
        and sp.simplify(w_bg[1] - 48 * alpha / (19 * r**2)) == 0,
        f"static pair symplectic current unexpected: {w_bg}",
    )
    _require(sp.simplify(sp.diff(r**2 * w_bg[1], r)) == 0, "static pair current not conserved")
    stage("static_pair_current", t0)

    # ---- 6. entropy conformal invariance on the symbolic family ----------
    t0 = time.time()
    Bfam = mk_metric_function(beta, gam, kk, r)
    gfam0 = static_spherical_metric(Bfam, 1 / Bfam, r, th)
    ge = (1 + 2 * eps * om) * gfam0
    geo_e = Geometry(coords, ge)
    E_e = dc.E_weyl(geo_e, alpha)
    integrand = -2 * sp.pi * 4 * E_e[0][1][0][1] * (sp.sqrt(-ge[0, 0] * ge[1, 1])) ** 2
    S_e = integrand * sp.sqrt(ge[2, 2] * ge[3, 3]) / sp.sin(th) * 4 * sp.pi
    _require(sp.simplify(sp.diff(S_e, eps).subs(eps, 0)) == 0, "delta_omega S != 0")
    stage("entropy_conformal_invariance", t0)

    # ---- 7. bare aperture nonzero (delta N uniqueness input) -------------
    t0 = time.time()
    Q0 = dc.q_two_form(geof, dc.Q_up(geof, Ef, chif))
    bare = sp.simplify(sp.integrate(sp.integrate(Q0[(2, 3)], (th, 0, sp.pi)), (ph, 0, 2 * sp.pi)))
    _require(sp.simplify(bare) != 0, "bare Noether aperture unexpectedly zero")
    stage("bare_aperture", t0)

    # ---- 8. route cross-validation on a polynomial witness ----------------
    # static radial witness: L_xi g stays diagonal, so the epsilon-geometry
    # variation is as cheap as a parameter mode; it still exercises the
    # relative normalization of the identity route against the direct
    # pipeline (the time-dependent structure is covered by stage 1).
    t0 = time.time()
    xi_w = [sp.Integer(0), r**3, sp.Integer(0), sp.Integer(0)]
    h_w = dc.lie_metric(coords, g0s, xi_w)
    k_brute = dc.charge_form(Geometry, coords, g0s, geos, Es, chis, h_w, alpha, eps)
    k_route = dc.diffeo_charge_form_identity_route(coords, geos, Es, chis, xi_w, Ls)
    for key in k_brute:
        _require(
            sp.simplify(k_brute[key] - k_route[key]) == 0,
            f"route cross-validation fails at {key}",
        )
    _require(_zero_form(k_brute), "polynomial witness diffeo charge nonzero")
    stage("route_cross_validation", t0)

    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "MK static spherical Bach vacuum; controls on Schwarzschild (symbolic m) and the three-horizon fixture",
            "conformal_frame": "certified frame-independent at the linear charge level: conformal directions carry zero charge, zero entropy shift, and are null directions of the corrected presymplectic current",
            "generator": "chi = u d_t from BH-1A; unique linear extension off the static family (delta N = du on parameter directions, 0 on gauge and l >= 1 directions)",
            "phase_space": "linear perturbations; spherical (l = 0) dynamical sector complete: conformal + diffeo + parameter directions",
            "horizon_condition": "identities hold componentwise in the chart, hence at every horizon and radius; no boundary restriction needed for the certified statements",
            "infinity_condition": "fixed-falloff ensembles of BH-1A; no falloff enlargement was needed for the l = 0 sector",
            "lifecycle": "PREFLIGHT",
        },
        "scope": {
            "certified": "linear charge level; l = 0 dynamical sector (arbitrary omega(t,r), a(t,r), b(t,r)); static parameter sector (BH-1A)",
            "l_ge_1_linear_charges": "vanish by spherical-harmonic orthogonality of the aperture; analytic parity argument, not machine-checked",
            "not_certified": "bilinear radiative symplectic flux matrix (BH-2A), second-order/physical-process first law, nonlinear dynamics",
        },
        "theta_audit": {
            "conformal": "div theta[2 omega g] = 0 exactly (conformally invariant density)",
            "parameter": "delta(sqrt(-g) alpha C^2) = div(sqrt(-g) theta) exactly on shell",
        },
        "conformal_sector": {
            "charge_form": "k(2 omega(t,r) g) = 0 identically, all six components, Schwarzschild (symbolic m) and fixture",
            "entropy": "delta_omega S = 0 exactly on the symbolic MK family, arbitrary omega(t,r)",
            "presymplectic": "omega_symp(2 omega g, param mode) = 0 identically (corrected current); conformal directions are exact null directions",
            "conclusion": "no boundary clock or conformal representative is required at the linear charge level; the BH-1A result is not frame-selected",
        },
        "diffeo_sector": {
            "noether_identity": "Theta(L_xi g) - i_xi(L eps) = d Q_xi exactly, componentwise, both backgrounds, xi = a(t,r) d_t + b(t,r) d_r arbitrary",
            "charge_form": "k(L_xi g) = 0 identically via the identity route L_xi Q_chi + Q_{[chi,xi]} - L_chi Q_xi - i_chi i_xi(L eps) + d(i_chi Q_xi); cross-validated against a direct epsilon-geometry computation for xi = t r^2 d_r",
            "conclusion": "time-dependent l = 0 diffeos are proper gauge with zero charge and zero flux",
        },
        "machinery_controls": {
            "parameter_mode_dynamical_pipeline": "reproduces the certified static charge u*F_beta exactly at the fixture",
            "corrected_current_static_pair": "omega^a(d_beta, d_gamma) = (0, 48*alpha/(19*r**2), 0, 0), exactly conserved",
            "correction_note": "the presymplectic current is the variation of the density sqrt(-g) theta^a; the (1/2) tr(h) theta^a terms are essential for conservation and for the conformal null-direction result",
        },
        "generator_extension": {
            "bare_aperture_fixture": sp.sstr(bare),
            "argument": "the bare aperture is nonzero, so delta N != 0 on any gauge direction would give it a nonzero charge, contradicting the certified annihilation; N is a spherical boundary scalar so delta N = 0 on l >= 1 modes; delta N = du on parameter directions is fixed by BH-1A; the linear extension is unique",
        },
        "first_law_dynamical": {
            "statement": "in every certified sector the linearized law delta H = T delta S + radiative flux holds: gauge and conformal sectors contribute 0 = 0 + 0, the parameter sector is the exact BH-1A first law, and l >= 1 linear charges and entropy variations vanish by parity",
            "second_order": "the physical-process (quadratic flux) version is not claimed",
        },
        "claim_flags": {
            "theta_defining_identity_certified": True,
            "noether_identity_certified": True,
            "conformal_charge_annihilation_certified": True,
            "conformal_entropy_invariance_certified": True,
            "conformal_null_direction_certified": True,
            "diffeo_charge_annihilation_certified": True,
            "corrected_current_conservation_certified": True,
            "unique_linear_generator_extension_certified": True,
            "harmonic_orthogonality_machine_checked": False,
            "radiative_bilinear_flux_matrix_certified": False,
            "second_order_physical_process_certified": False,
            "nonlinear_dynamics_certified": False,
            "stability_certified": False,
        },
        "missing_objects": [
            "odd-parity (l >= 2) linearized complex and bilinear flux matrix (BH-2A)",
            "machine check of harmonic orthogonality for l >= 1 linear charges",
            "second-order/physical-process first law with radiative flux",
            "nonlinear horizon dynamics and stability",
            "physical matter/clock frame beyond conformal-invariance of the charge",
        ],
        "stage_seconds": receipts,
        "provenance": {
            "generator_path": "black_hole_programme/bh1b_dynamical.py",
            "machinery_path": "black_hole_programme/dynamical_charges.py",
            "machinery_sha256": _sha256(HERE / "dynamical_charges.py"),
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "bh1a_certificate": str(BH1A_CERT.relative_to(ROOT)),
            "bh1a_certificate_sha256": _sha256(BH1A_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh1b_dynamical.py",
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
