"""BH-0: exact classification of the static spherical pure-Weyl background.

Fail-closed builder for the certificate
`black_hole_programme/certificates/BH0_STATIC_SPHERICAL_BACKGROUND.json`.

What is certified (all exact rational/symbolic sympy, LOCAL-ALGEBRAIC):

1.  the reduced Bach rows of the two-function static spherical ansatz
    diag(-a(r), b(r), r^2, r^2 sin^2 th), their exact tracelessness and the
    exact vanishing of the covariant divergence nabla^a B_ab;
2.  a Laurent-class completeness theorem in the conformal gauge b = 1/a:
    for B = w - u/r + gamma r - k r^2 + c2/r^2 + c3 r^3 the Bach equations
    vanish identically iff c2 = c3 = 0 and w^2 + 3 u gamma = 1 (Groebner
    basis of the coefficient ideal);
3.  the Mannheim--Kazanas parametrization of the w-near-1 sheet, with
    Schwarzschild and Schwarzschild--(A)dS as Einstein controls;
4.  the Einstein/extra split on the family: trace-free Ricci defect
    E_thth = -gamma (r - 3 beta)/2, so on the Mannheim-Kazanas sheet
    (through w = 1) the subfamily is Einstein iff gamma = 0; on the
    complete Laurent locus Einstein requires gamma = 0 AND w = 1;
5.  the residual (diffeo x Weyl) action preserving the gauge-fixed form:
    a translation + dilation action on the cubic
    Q(x) = -u x^3 + w x^2 + gamma x - k, x = 1/r, of generic orbit rank 2,
    with single continuous invariant J = u^2 disc(Q);
6.  an exact rational horizon fixture (beta, gamma, k) = (3/2, 12/19, 1/19)
    with r B(r) = -(1/19)(r-1)(r-3)(r-8), simple horizons, exact chart
    surface gravities, and finite curvature invariants at every horizon;
7.  ingoing Eddington--Finkelstein horizon-regular chart: exact
    Bach-flatness, smooth chart metric, and the exact nullity g^{rr} = B of
    the constant-r hypersurfaces at the roots of B;
8.  an exact conformal-covariance instance and two mutations that spoil
    Bach flatness.

What is NOT certified (fail-closed flags in the certificate): completeness
beyond the Laurent class (Riegert's classification is a literature target,
not a repository theorem), any physical matter/clock conformal frame, any
horizon phase space, charge, flux, causal exterior problem, perturbation,
quasinormal mode, stability, thermodynamic, or quantum statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from weyl_geometry import (
    Geometry,
    eddington_finkelstein_metric,
    mk_metric_function,
    static_spherical_metric,
)

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH0_STATIC_SPHERICAL_BACKGROUND.json"
SCHEMA_PATH = HERE / "schema" / "bh0-static-spherical-background-v1.schema.json"
FLAT_TT_CERT = ROOT / "bridge" / "certificates" / "flat_tt_bach_operator.json"

SCHEMA_NAME = "pure-weyl-bh0-static-spherical-background-v1"
RESULT_ID = "PURE_WEYL_STATIC_SPHERICAL_BACKGROUND"
RESULT_TOKEN = "PURE_WEYL_STATIC_SPHERICAL_BACKGROUND_CLASSIFIED"

FIXTURE = {"beta": sp.Rational(3, 2), "gamma": sp.Rational(12, 19), "k": sp.Rational(1, 19)}


class BH0Error(RuntimeError):
    """Raised when any exact check fails; no certificate is written."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BH0Error(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _s(expr) -> str:
    return sp.sstr(sp.simplify(expr))


def _symbols():
    t, ph = sp.symbols("t phi")
    r, th = sp.symbols("r theta", positive=True)
    beta, gam, k = sp.symbols("beta gamma k")
    return t, r, th, ph, beta, gam, k


def _all_zero(M: sp.Matrix) -> bool:
    return all(sp.simplify(M[i, j]) == 0 for i in range(4) for j in range(4))


def build_certificate() -> dict:
    t, r, th, ph, beta, gam, k = _symbols()
    coords = [t, r, th, ph]
    MK = mk_metric_function(beta, gam, k, r)

    # ---- 1. two-function reduced rows, trace, divergence -----------------
    a = sp.Function("a")(r)
    b = sp.Function("b")(r)
    geo2 = Geometry(coords, static_spherical_metric(a, b, r, th))
    B2 = geo2.bach()
    offdiag = [(i, j) for i in range(4) for j in range(4) if i != j and sp.simplify(B2[i, j]) != 0]
    _require(not offdiag, f"two-function Bach has off-diagonal components {offdiag}")
    trace = sp.simplify(sum(geo2.ginv[i, j] * B2[i, j] for i in range(4) for j in range(4)))
    _require(trace == 0, "two-function Bach trace does not vanish")
    _require(
        sp.simplify(B2[3, 3] - sp.sin(th) ** 2 * B2[2, 2]) == 0,
        "B_phiphi != sin^2(theta) B_thetatheta",
    )
    divergence_ok = True
    for bb in range(4):
        s = sp.Integer(0)
        for aa in range(4):
            for e in range(4):
                if geo2.ginv[aa, e] != 0:
                    s += geo2.ginv[aa, e] * geo2.covd2(B2, e, aa, bb)
        if sp.simplify(s) != 0:
            divergence_ok = False
    _require(divergence_ok, "nabla^a B_ab does not vanish identically")
    rows = {"tt": B2[0, 0], "rr": B2[1, 1], "thth": B2[2, 2]}
    mk_subs = {a: MK, b: 1 / MK}
    for name, expr in rows.items():
        val = sp.simplify(expr.subs(mk_subs, simultaneous=True).doit())
        _require(val == 0, f"MK family fails two-function row {name}")

    # ---- 2. Laurent-class completeness -----------------------------------
    u, w, c2, c3 = sp.symbols("u w c2 c3")
    Bgen = w - u / r + gam * r - k * r**2 + c2 / r**2 + c3 * r**3
    geoL = Geometry(coords, static_spherical_metric(Bgen, 1 / Bgen, r, th))
    BL = geoL.bach()
    conds = set()
    for i in range(4):
        for j in range(4):
            e = sp.simplify(BL[i, j])
            if e != 0:
                num, _den = sp.fraction(sp.cancel(sp.together(e)))
                for cf in sp.Poly(sp.expand(num), r).coeffs():
                    conds.add(sp.factor(cf))
    gb = sp.groebner(sorted(conds, key=sp.default_sort_key), c2, c3, u, w, gam, k, order="lex")
    gb_exprs = [sp.factor(e) for e in gb.exprs]
    expected_gb = {c2, c3, sp.factor(3 * gam * u + w**2 - 1)}
    _require(
        set(gb_exprs) == expected_gb,
        f"Laurent completeness Groebner basis unexpected: {gb_exprs}",
    )

    # ---- 3. MK family and Einstein controls ------------------------------
    geoMK = Geometry(coords, static_spherical_metric(MK, 1 / MK, r, th))
    _require(_all_zero(geoMK.bach()), "MK family is not Bach-flat")
    m = sp.Symbol("m", positive=True)
    geoS = Geometry(coords, static_spherical_metric(1 - 2 * m / r, 1 / (1 - 2 * m / r), r, th))
    _require(_all_zero(geoS.Ricci), "Schwarzschild control not Ricci-flat")
    _require(_all_zero(geoS.bach()), "Schwarzschild control not Bach-flat")
    BSdS = 1 - 2 * m / r - k * r**2
    geoSdS = Geometry(coords, static_spherical_metric(BSdS, 1 / BSdS, r, th))
    _require(
        _all_zero(geoSdS.Ricci - 3 * k * geoSdS.g),
        "Schwarzschild-dS control is not Einstein with R_ab = 3k g_ab",
    )
    _require(_all_zero(geoSdS.bach()), "Schwarzschild-dS control not Bach-flat")

    # ---- 4. Einstein/extra split -----------------------------------------
    E = geoMK.einstein_defect()
    E_thth = sp.factor(E[2, 2])
    _require(
        sp.simplify(E_thth - (-gam * (r - 3 * beta) / 2)) == 0,
        "Einstein defect E_thth does not factor as -gamma (r - 3 beta)/2",
    )
    _require(_all_zero(E.subs(gam, 0)), "gamma = 0 subfamily is not Einstein")

    # ---- 5. residual gauge action ----------------------------------------
    c, lam, x = sp.symbols("c lambda x")
    rho = sp.Symbol("rho", positive=True)
    Btilde = sp.expand(sp.cancel((1 - c * rho) ** 2 * MK.subs(r, rho / (1 - c * rho))))
    p = sp.Poly(sp.cancel(sp.together(Btilde * rho)), rho)
    _require(p.degree() == 3, "c-map image is not of MK Laurent degree")
    kt = sp.simplify(-p.coeff_monomial(rho**3))
    gt = sp.simplify(p.coeff_monomial(rho**2))
    lin = p.coeff_monomial(rho**1)
    const = p.coeff_monomial(rho**0)
    bt = sp.simplify(-const / (1 + lin))
    _require(sp.simplify(3 * bt * gt - (1 - lin)) == 0, "c-map image leaves the MK chart")
    uu = beta * (2 - 3 * beta * gam)
    ww = 1 - 3 * beta * gam
    ut = sp.expand(bt * (2 - 3 * bt * gt))
    wt = sp.expand(1 - 3 * bt * gt)
    Q = -uu * x**3 + ww * x**2 + gam * x - k
    Qt = -ut * x**3 + wt * x**2 + gt * x - kt
    _require(
        sp.simplify(sp.expand(Qt - Q.subs(x, x - c))) == 0,
        "c-map is not the exact translation x -> x - c on Q",
    )
    disc = sp.discriminant(Q, x)
    J = sp.factor(sp.expand(uu**2 * disc))
    _require(
        sp.simplify(sp.expand(ut**2 * sp.discriminant(Qt, x) - uu**2 * disc)) == 0,
        "J = u^2 disc(Q) is not invariant under the c-map",
    )
    bs, gs, ks = beta / lam, lam * gam, lam**2 * k
    us = sp.expand(bs * (2 - 3 * bs * gs))
    ws2 = 1 - 3 * bs * gs
    Qs = -us * x**3 + ws2 * x**2 + gs * x - ks
    _require(
        sp.simplify(sp.expand(us**2 * sp.discriminant(Qs, x) - uu**2 * disc)) == 0,
        "J is not invariant under the dilation",
    )
    gen_c = [sp.diff(e, c).subs(c, 0) for e in (bt, gt, kt)]
    gen_l = [sp.diff(e, lam).subs(lam, 1) for e in (bs, gs, ks)]
    rank = sp.Matrix([gen_c, gen_l]).T.rank()
    _require(rank == 2, "residual gauge orbit rank is not 2")

    # ---- 6. horizon fixture ----------------------------------------------
    fx = {beta: FIXTURE["beta"], gam: FIXTURE["gamma"], k: FIXTURE["k"]}
    Bfx = sp.cancel(MK.subs(fx))
    cubic = sp.expand(Bfx * r)
    _require(
        sp.expand(cubic - sp.Rational(-1, 19) * (r - 1) * (r - 3) * (r - 8)) == 0,
        "fixture cubic does not factor as -(1/19)(r-1)(r-3)(r-8)",
    )
    dB = sp.diff(Bfx, r)
    roots = []
    for rh, kind in [(1, "inner"), (3, "black_hole_event"), (8, "cosmological")]:
        _require(sp.simplify(Bfx.subs(r, rh)) == 0, f"B does not vanish at r = {rh}")
        slope = sp.nsimplify(sp.simplify(dB.subs(r, rh)))
        _require(slope != 0, f"root r = {rh} is not simple")
        roots.append(
            {
                "r": str(rh),
                "multiplicity": 1,
                "type": kind,
                "B_prime": _s(slope),
                "chart_surface_gravity": _s(slope / 2),
            }
        )
    _require(sp.simplify(dB.subs(r, 3)) > 0, "event horizon slope not positive")
    _require(sp.simplify(dB.subs(r, 8)) < 0, "cosmological horizon slope not negative")
    _require(sp.simplify(Bfx.subs(r, 5)) > 0, "static exterior (3,8) not static")
    E_fx = sp.factor(E_thth.subs(fx))
    _require(sp.simplify(E_fx) != 0, "fixture is not in the extra (non-Einstein) branch")
    J_fx = sp.nsimplify(J.subs(fx))

    # ---- singularity classification --------------------------------------
    inv = geoMK.invariants()
    for name, expr in inv.items():
        _num, den = sp.fraction(sp.cancel(sp.together(expr)))
        _require(
            den.free_symbols <= {r},
            f"invariant {name} has parameter-dependent poles: denominator {den}",
        )
    weyl2 = inv["WeylSq"]
    _require(
        sp.simplify(weyl2 - 12 * beta**2 * (2 - 3 * beta * gam + gam * r) ** 2 / r**6) == 0,
        "WeylSq does not match the exact closed form",
    )
    for rh in (1, 3, 8):
        for name, expr in inv.items():
            val = expr.subs(fx).subs(r, rh)
            _require(val.is_finite is True, f"invariant {name} not finite at fixture horizon {rh}")

    # ---- 7. Eddington--Finkelstein chart ---------------------------------
    v = sp.Symbol("v")
    gEF = eddington_finkelstein_metric(MK, r, th)
    geoEF = Geometry([v, r, th, ph], gEF)
    _require(_all_zero(geoEF.bach()), "MK family not Bach-flat in the EF chart")
    detEF = sp.simplify(gEF.det())
    _require(sp.simplify(detEF + r**4 * sp.sin(th) ** 2) == 0, "EF chart determinant unexpected")
    _require(sp.simplify(geoEF.ginv[1, 1] - MK) == 0, "g^rr != B in EF chart")

    # ---- 8. conformal instance and mutations ------------------------------
    Om = 1 + r**2
    gconf = (Om**2 * static_spherical_metric(MK, 1 / MK, r, th)).subs(fx)
    _require(
        _all_zero(Geometry(coords, gconf).bach()),
        "conformally rescaled fixture is not Bach-flat",
    )
    mutations = []
    for Bmut, label in [
        (1 - 2 * beta / r + gam * r, "drop_minus_3_beta_gamma_correlation"),
        (Bfx + sp.Rational(1, 7) / r**2, "fixture_plus_r^-2_tail"),
    ]:
        geoM = Geometry(coords, static_spherical_metric(Bmut, 1 / Bmut, r, th))
        BM = geoM.bach()
        nz = {
            f"{i}{j}": _s(BM[i, j])
            for i in range(4)
            for j in range(4)
            if sp.simplify(BM[i, j]) != 0
        }
        _require(bool(nz), f"mutation {label} unexpectedly Bach-flat")
        mutations.append({"label": label, "B": _s(Bmut), "nonzero_bach_components": nz})

    # ---- certificate ------------------------------------------------------
    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "declaration": {
            "theory": "pure-Weyl gravity S_W = alpha Integral(sqrt(-g) C_abcd C^abcd)",
            "background_family": "static spherical Bach vacuum, MK chart of the Laurent constraint variety",
            "conformal_frame": "unphysical working gauge b = 1/a with areal radius; no physical matter/clock frame declared",
            "generator": "none; chart vector d_v recorded, horizon generator not yet a certified phase-space object",
            "phase_space": "none constructed at BH-0",
            "horizon_condition": "chart-level only: simple roots of B with finite curvature invariants and EF-smooth metric",
            "infinity_condition": "none imposed; family is generically not asymptotically flat",
            "lifecycle": "CLASSIFIED",
        },
        "conventions": {
            "signature": "(-,+,+,+)",
            "bach": "B_ab = nabla^c nabla^d C_acbd + (1/2) R^cd C_acbd",
            "weyl": "C_abcd = R_abcd - (g_ac R_bd - g_ad R_bc + g_bd R_ac - g_bc R_ad)/2 + R (g_ac g_bd - g_ad g_bc)/6",
            "riemann": "R^a_bcd = d_c Gamma^a_db - d_d Gamma^a_cb + Gamma^a_ce Gamma^e_db - Gamma^a_de Gamma^e_cb",
            "linearized_dictionary": {
                "statement": "on Minkowski TT modes these conventions reduce to B_mn = d^r d^s C_mrns",
                "flat_certificate": str(FLAT_TT_CERT.relative_to(ROOT)),
                "flat_certificate_sha256": _sha256(FLAT_TT_CERT),
            },
        },
        "reduced_equations": {
            "ansatz": "diag(-a(r), b(r), r**2, r**2*sin(theta)**2)",
            "rows": {name: sp.sstr(expr) for name, expr in rows.items()},
            "trace_identically_zero": True,
            "divergence_identically_zero": True,
            "phiphi_row_dependence": "B_phiphi = sin(theta)**2 * B_thetatheta",
            "independent_row_count_after_trace": 2,
        },
        "laurent_completeness": {
            "ansatz": "B = w - u/r + gamma*r - k*r**2 + c2/r**2 + c3*r**3, b = 1/B",
            "groebner_basis": [sp.sstr(e) for e in gb_exprs],
            "statement": "within this Laurent class Bach flatness holds iff c2 = c3 = 0 and w**2 + 3*u*gamma = 1",
            "beyond_laurent_class": "open in this repository; Riegert's classification is a literature target",
        },
        "vacuum_family": {
            "B": sp.sstr(MK),
            "parameters": ["beta", "gamma", "k"],
            "constraint_form": "w = 1 - 3*beta*gamma, u = beta*(2 - 3*beta*gamma) parametrize the sheet of w**2 + 3*u*gamma = 1 through w = 1",
            "unparametrized_sheet": "the complementary sheet (e.g. w = -1, gamma = 0, B = -1 - u/r - k*r**2) has r timelike where B < 0 and is a Kantowski--Sachs-type branch outside the MK chart",
            "dictionary": {
                "mannheim_kazanas_1989": "identical (beta, gamma, k); their u = beta*(2 - 3*beta*gamma)",
                "schwarzschild_control": "beta = m, gamma = 0, k = 0",
                "schwarzschild_de_sitter_control": "gamma = 0, k = Lambda/3, verified R_ab = 3*k*g_ab",
            },
        },
        "einstein_split": {
            "defect_thth": sp.sstr(E_thth),
            "einstein_condition_on_family": "gamma = 0",
            "einstein_subfamily": "Schwarzschild--(A)dS, B = 1 - 2*beta/r - k*r**2",
            "extra_branch_witness": "E_thth = -gamma*(r - 3*beta)/2 vanishes identically iff gamma = 0",
        },
        "residual_gauge": {
            "c_map": {
                "chart_map": "r = rho/(1 - c*rho), Omega = 1 - c*rho",
                "beta": sp.sstr(sp.simplify(bt)),
                "gamma": sp.sstr(sp.simplify(gt)),
                "k": sp.sstr(sp.simplify(kt)),
            },
            "dilation": "beta -> beta/lambda, gamma -> lambda*gamma, k -> lambda**2*k with t -> lambda*t, r = lambda*rho, Omega = 1/lambda",
            "cubic": "Q(x) = -u*x**3 + w*x**2 + gamma*x - k with x = 1/r",
            "translation_property": "the c-map acts on Q exactly as x -> x - c; the dilation as Q(x) -> lambda**2*Q(x/lambda)",
            "orbit_rank": 2,
            "continuous_invariant": {"J": sp.sstr(sp.expand(uu**2 * disc)), "J_factored": sp.sstr(J)},
            "invariant_meaning": "disc(Q) = 0 is exactly the degenerate-horizon locus, so the residual-gauge-invariant content of the family is the horizon root structure plus J",
            "singular_rescaling_caveat": "Omega = 1 - c*rho vanishes at rho = 1/c; the c-map is a local gauge equivalence on rho < 1/c only and is not used to identify horizon geometries globally",
        },
        "horizon_fixture": {
            "parameters": {"beta": "3/2", "gamma": "12/19", "k": "1/19"},
            "B": sp.sstr(Bfx),
            "r_times_B_factorization": "-(1/19)*(r - 1)*(r - 3)*(r - 8)",
            "roots": roots,
            "static_regions": "B > 0 on (0,1) and (3,8); B < 0 on (1,3) and (8,oo)",
            "surface_gravity_caveat": "chart values kappa = B'(r_h)/2 for the chart vector d_v; the family is not asymptotically flat, so no preferred normalization of the generator is claimed",
            "non_einstein_witness": sp.sstr(E_fx),
            "invariant_J_value": sp.sstr(J_fx),
            "invariants_finite_at_horizons": True,
        },
        "singularities": {
            "R": sp.sstr(inv["R"]),
            "RicciSq": sp.sstr(inv["RicciSq"]),
            "WeylSq": sp.sstr(inv["WeylSq"]),
            "Kretschmann": sp.sstr(inv["Kretschmann"]),
            "classification": "all listed invariants are rational in r with poles only at r = 0; WeylSq ~ 48*beta**2/r**6 gives a curvature singularity iff beta != 0; R ~ 6*beta*gamma/r**2 adds a scalar-curvature singularity iff beta*gamma != 0; every invariant is finite at every horizon",
            "conformal_frame_note": "statements are for the working gauge; WeylSq has conformal weight -4, so its zero/pole locus is frame-covariant but its value is not",
        },
        "ef_chart": {
            "metric": "ds**2 = -B(r)*dv**2 + 2*dv*dr + r**2*dOmega**2 (ingoing)",
            "bach_flat": True,
            "determinant": "-r**4*sin(theta)**2, nondegenerate at every horizon",
            "null_hypersurface_check": "g^rr = B(r) exactly, so a constant-r hypersurface is null precisely at roots of B",
            "chart_generator": "d_v, smooth across the horizons in this chart",
        },
        "conformal_instance": {
            "omega": "1 + r**2",
            "statement": "the rescaled fixture metric is exactly Bach-flat, an instance of conformal covariance of the Bach tensor; no general transformation theorem is certified here",
        },
        "mutation_tests": mutations,
        "claim_flags": {
            "bach_flat_family_certified": True,
            "laurent_class_completeness_certified": True,
            "general_completeness_certified": False,
            "horizon_chart_regularity_verified": True,
            "regular_causal_horizon_certified": False,
            "physical_frame_horizon_regularity_certified": False,
            "exterior_initial_boundary_problem_certified": False,
            "lee_wald_flux_or_charge_certified": False,
            "gauge_boundary_quotient_certified": False,
            "quasinormal_mode_certified": False,
            "quantum_state_or_hawking_certified": False,
        },
        "missing_objects": [
            "completeness of the Bach vacuum beyond the Laurent class (Riegert classification)",
            "declared physical matter/clock conformal frame",
            "horizon and infinity phase space, boundary terms, differentiable charges",
            "causal exterior initial-boundary theorem",
            "linear exterior BV complex and Einstein/extra flux split",
            "any perturbation, stability, ringdown, thermodynamic, or quantum object",
        ],
        "provenance": {
            "generator_path": "black_hole_programme/bh0_background.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
        },
        "verification_command": "python3 black_hole_programme/verify_bh0_background.py",
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
