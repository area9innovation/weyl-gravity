"""BH-1 preflight: unrenormalized Lee--Wald surface form on the MK family.

Fail-closed builder for
`black_hole_programme/certificates/BH1_LEE_WALD_PREFLIGHT.json`.

Exact results (chi = d_t, static parameter variations delta in
{d_beta, d_gamma, d_k}, all sympy-exact):

- normalization control: the same machinery with the Einstein tensor
  E^{abcd} = (g^{ac}g^{bd} - g^{ad}g^{bc})/2 gives F = 16 pi delta m on
  Schwarzschild and Schwarzschild--de Sitter (Wald/ADM value, L = R);
- bare charges on the family, exactly r-independent from horizon to
  infinity (static flux balance):
      F_beta  = 16 pi alpha (12 beta gamma k - gamma^2 - 4 k)
      F_gamma = 16 pi alpha beta (6 beta k - gamma)
      F_k     = -16 pi alpha beta (2 - 3 beta gamma)
- non-integrability: the parameter-space 1-form F is not closed;
  dF = 16 pi alpha [ gamma d beta ^ d gamma
                     - 2 (3 beta gamma - 1) d beta ^ d k
                     - 3 beta^2 d gamma ^ d k ]  (nonzero),
  so NO boundary function W(beta, gamma, k) of the static parameters can
  make the bare form a total variation;
- gauge degeneracy: the residual-gauge c-direction
  gen_c = (-3 beta^2, 6 beta gamma - 2, gamma) satisfies
  iota_{gen_c} dF = 0 and F(gen_c) = 0 exactly, so the obstruction
  2-form descends to the physical quotient, where it is nondegenerate;
- Euler identity: the dilation direction gen_lambda = (-beta, gamma, 2k)
  satisfies iota_{gen_lambda} dF = F and F(gen_lambda) = 0 exactly.

Lifecycle: preflight only.  No entropy, first law, full phase space,
stability, or dynamical (time-dependent) perturbation claim is made.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

import lee_wald as lw
from weyl_geometry import Geometry, mk_metric_function, static_spherical_metric

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH1_LEE_WALD_PREFLIGHT.json"
SCHEMA_PATH = HERE / "schema" / "bh1-lee-wald-preflight-v1.schema.json"
BH0_CERT = HERE / "certificates" / "BH0_STATIC_SPHERICAL_BACKGROUND.json"

SCHEMA_NAME = "pure-weyl-bh1-lee-wald-preflight-v1"
RESULT_ID = "PURE_WEYL_BH1_LEE_WALD_PREFLIGHT"
RESULT_TOKEN = "BH1_PREFLIGHT_COMPLETE_BARE_FORM_NONINTEGRABLE"


class BH1Error(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise BH1Error(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _charge(Bfun, psym, E_maker, coords, r, th, ph):
    """F = Int_{S_r} (delta Q - i_chi theta) for chi = d_t, delta = d/dpsym."""
    g = static_spherical_metric(Bfun, 1 / Bfun, r, th)
    geo = Geometry(coords, g)
    E_up = E_maker(geo)
    chi_up = [sp.Integer(1), 0, 0, 0]
    dg = sp.Matrix(4, 4, lambda i, j: sp.diff(g[i, j], psym))
    q_form, itheta = lw.surface_forms(geo, E_up, chi_up, dg)
    dQ = sp.diff(q_form, psym)
    F = sp.simplify(lw.sphere_integral(sp.cancel(sp.together(dQ - itheta)), th, ph))
    return F, q_form


def build_certificate() -> dict:
    t, ph = sp.symbols("t phi")
    r, th = sp.symbols("r theta", positive=True)
    beta, gam, k, alpha = sp.symbols("beta gamma k alpha")
    m = sp.Symbol("m", positive=True)
    coords = [t, r, th, ph]

    # ---- normalization controls (Einstein gravity, L = R) ----------------
    F_gr, _ = _charge(1 - 2 * m / r, m, lw.E_einstein, coords, r, th, ph)
    _require(sp.simplify(F_gr - 16 * sp.pi) == 0, f"GR Schwarzschild control failed: {F_gr}")
    F_grsds, _ = _charge(1 - 2 * m / r - k * r**2, m, lw.E_einstein, coords, r, th, ph)
    _require(sp.simplify(F_grsds - 16 * sp.pi) == 0, f"GR S-dS control failed: {F_grsds}")

    # ---- pure-Weyl charges on the MK family ------------------------------
    MK = mk_metric_function(beta, gam, k, r)
    E_maker = lambda geo: lw.E_weyl(geo, alpha)  # noqa: E731
    expected = {
        beta: 16 * sp.pi * alpha * (12 * beta * gam * k - gam**2 - 4 * k),
        gam: 16 * sp.pi * alpha * beta * (6 * beta * k - gam),
        k: 16 * sp.pi * alpha * beta * (3 * beta * gam - 2),
    }
    charges = {}
    q_forms = {}
    for psym in (beta, gam, k):
        F, q_form = _charge(MK, psym, E_maker, coords, r, th, ph)
        _require(
            r not in F.free_symbols,
            f"charge for delta {psym} is not r-independent: {F}",
        )
        _require(
            sp.simplify(F - expected[psym]) == 0,
            f"charge for delta {psym} unexpected: {F}",
        )
        charges[str(psym)] = F
        q_forms[str(psym)] = q_form
    # Schwarzschild member: all charges vanish except the k-variation pairing
    schw = {beta: beta, gam: sp.Integer(0), k: sp.Integer(0)}
    _require(
        sp.simplify(charges["beta"].subs(schw)) == 0
        and sp.simplify(charges["gamma"].subs(schw)) == 0,
        "Schwarzschild member charges unexpected",
    )

    # ---- nontriviality witness: delta Q alone is r-dependent -------------
    dQ_gamma = sp.simplify(
        lw.sphere_integral(sp.diff(q_forms["gamma"], gam), th, ph)
    )
    _require(
        r in dQ_gamma.free_symbols,
        "witness failed: sphere integral of delta_gamma Q is r-independent, "
        "so constancy of F would be vacuous",
    )

    # ---- obstruction 2-form dF, kernel, Euler identity --------------------
    ps = [beta, gam, k]
    Fvec = [charges["beta"], charges["gamma"], charges["k"]]
    dF = {
        (i, j): sp.simplify(sp.diff(Fvec[j], ps[i]) - sp.diff(Fvec[i], ps[j]))
        for i in range(3)
        for j in range(i + 1, 3)
    }
    _require(any(v != 0 for v in dF.values()), "dF vanishes; obstruction claim wrong")
    gen_c = [-3 * beta**2, 6 * beta * gam - 2, gam]
    gen_l = [-beta, gam, 2 * k]

    def iota(V):
        out = []
        for j in range(3):
            s = sp.Integer(0)
            for i in range(3):
                if i < j:
                    s += V[i] * dF[(i, j)]
                elif i > j:
                    s -= V[i] * dF[(j, i)]
            out.append(sp.simplify(s))
        return out

    _require(all(e == 0 for e in iota(gen_c)), "gen_c not in ker dF")
    _require(
        all(sp.simplify(a - b) == 0 for a, b in zip(iota(gen_l), Fvec)),
        "Euler identity iota_{gen_lambda} dF = F fails",
    )
    _require(
        sp.simplify(sum(F * v for F, v in zip(Fvec, gen_c))) == 0,
        "F(gen_c) != 0",
    )
    _require(
        sp.simplify(sum(F * v for F, v in zip(Fvec, gen_l))) == 0,
        "F(gen_lambda) != 0",
    )

    # ---- fixture values ----------------------------------------------------
    fx = {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), k: sp.Rational(1, 19)}
    fixture_charges = {
        name: sp.sstr(sp.nsimplify(sp.simplify(F.subs(fx))))
        for name, F in charges.items()
    }

    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "MK static spherical Bach vacuum (BH-0 certificate)",
            "conformal_frame": "working gauge b = 1/a; no physical frame declared",
            "generator": "chart vector d_t (equals d_v on the sphere forms); normalization conventional, family not asymptotically flat",
            "phase_space": "static parameter slice only: variations restricted to d_beta, d_gamma, d_k",
            "horizon_condition": "surface integrals evaluated on S_r at every r; constancy makes horizon and infinity values equal",
            "infinity_condition": "none imposed; no falloff enlargement beyond the static family",
            "lifecycle": "PREFLIGHT",
        },
        "conventions": {
            "E_tensor": "E^{abcd} = dL/dR_{abcd}; Weyl case E^{abcd} = 2 alpha C^{abcd}",
            "theta": "theta^a = 2 (E^{abcd} nabla_d dg_{bc} - dg_{bc} nabla_d E^{abcd})",
            "Q": "Q^{ab} = -E^{abcd} nabla_c chi_d + 2 chi_d nabla_c E^{abcd}",
            "sphere_forms": "(Q-form)_{thph} = 2 sqrt(-g) Q^{tr}; (i_chi theta)_{thph} = -sqrt(-g) chi^t theta^r; eps_{t r th ph} = +sqrt(-g)",
            "normalization_control": "Einstein E-tensor reproduces F = 16 pi delta m on Schwarzschild and Schwarzschild-de Sitter (L = R, 16 pi G = 1, Wald/ADM)",
        },
        "controls": {
            "gr_schwarzschild_F": sp.sstr(F_gr),
            "gr_schwarzschild_de_sitter_F": sp.sstr(F_grsds),
            "weyl_schwarzschild_all_zero_except_k_pairing": True,
        },
        "bare_charges": {
            "F_beta": sp.sstr(charges["beta"]),
            "F_gamma": sp.sstr(charges["gamma"]),
            "F_k": sp.sstr(charges["k"]),
            "r_independent": True,
            "static_flux_balance": "each F is one exact constant, so the horizon and infinity surface integrals agree for every static on-shell variation; no dynamical flux statement is made",
            "nontriviality_witness": sp.sstr(dQ_gamma),
            "nontriviality_statement": "the delta_gamma Q sphere integral alone depends on r, so constancy of F is a nontrivial on-shell identity",
        },
        "integrability_obstruction": {
            "dF_beta_gamma": sp.sstr(dF[(0, 1)]),
            "dF_beta_k": sp.sstr(dF[(0, 2)]),
            "dF_gamma_k": sp.sstr(dF[(1, 2)]),
            "nonzero": True,
            "no_local_boundary_term": "no function W(beta, gamma, k) of the static parameters satisfies delta W = F, because dF != 0 exactly; this proves the bare form is not differentiable on the full static family",
            "kernel": "ker dF = span(gen_c), gen_c = (-3*beta**2, 6*beta*gamma - 2, gamma) (residual-gauge c-direction)",
            "descends_to_quotient": "iota_{gen_c} dF = 0 and F(gen_c) = 0, so F and dF descend to the 2-dimensional residual-gauge quotient, where dF is nondegenerate: the obstruction is physical, not gauge",
            "euler_identity": "iota_{gen_lambda} dF = F with gen_lambda = (-beta, gamma, 2*k); F(gen_lambda) = 0",
            "integrable_slices": "exactly the 2-dimensional parameter surfaces ruled by the c-direction (pullback of dF vanishes iff the tangent plane contains ker dF), plus all 1-dimensional subfamilies",
            "minimal_ansatz_for_bh1": "the first differentiability solve must either quotient the c-direction and pair only one physical direction at a time, or enlarge the phase space with non-parameter boundary/falloff data; no parameter-local corner term can work",
        },
        "einstein_subfamily_observations": {
            "schwarzschild_mass_charge": "F_beta = 0 at gamma = k = 0: the bare Noether mass of Schwarzschild vanishes in pure-Weyl gravity",
            "k_pairing_at_schwarzschild": sp.sstr(sp.simplify(charges["k"].subs(schw))),
            "extra_branch_variation_charged": sp.sstr(
                sp.simplify(charges["gamma"].subs(gam, 0))
            ),
            "note": "at Einstein points with beta*k != 0 the variation into the extra Weyl branch (delta gamma) carries nonzero bare charge",
        },
        "horizon_fixture_charges": {
            "parameters": {"beta": "3/2", "gamma": "12/19", "k": "1/19"},
            "F_beta": fixture_charges["beta"],
            "F_gamma": fixture_charges["gamma"],
            "F_k": fixture_charges["k"],
        },
        "claim_flags": {
            "normalization_control_certified": True,
            "bare_static_charges_certified": True,
            "static_flux_balance_certified": True,
            "bare_form_nonintegrable_certified": True,
            "obstruction_gauge_degenerate_certified": True,
            "differentiable_hamiltonian_certified": False,
            "entropy_or_first_law_certified": False,
            "full_horizon_phase_space_certified": False,
            "dynamical_perturbation_flux_certified": False,
            "stability_certified": False,
        },
        "missing_objects": [
            "action-derived presymplectic form for time-dependent perturbations",
            "falloff-enlarged phase space and boundary/corner term solve (BH-1 proper)",
            "Iyer-Wald entropy and first law in a fixed generator normalization",
            "horizon generator selection beyond the chart vector d_t",
            "any Lorentzian causal or dynamical statement",
        ],
        "provenance": {
            "generator_path": "black_hole_programme/bh1_lee_wald_preflight.py",
            "machinery_path": "black_hole_programme/lee_wald.py",
            "machinery_sha256": _sha256(HERE / "lee_wald.py"),
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "bh0_certificate": str(BH0_CERT.relative_to(ROOT)),
            "bh0_certificate_sha256": _sha256(BH0_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh1_lee_wald_preflight.py",
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
