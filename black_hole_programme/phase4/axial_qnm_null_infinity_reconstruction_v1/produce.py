#!/usr/bin/env python3
"""Produce the exact axial QNM null-infinity reconstruction certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_OUTPUT = HERE / "certificate.json"

IMPORTS = {
    "complete_reconstruction": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_complete_reconstruction_repair/certificate.json"
    ),
    "outgoing_frame": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_partial_jet_outgoing_frame_completion_v1/certificate.json"
    ),
    "infinity_metric_heads": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_endpoint_remainder_enclosures/infinity-metric-heads.json"
    ),
    "moving_phase": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_partial_jet_outgoing_kplus_moving_phase_gate_v1/certificate.json"
    ),
    "rw_equivalence": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_expr(value: str, *, r: sp.Symbol, omega: sp.Symbol) -> sp.Expr:
    state = {
        name: sp.Symbol(name)
        for name in ("H1", "F", "P", "Pp", "Q", "Qp")
    }
    return sp.sympify(
        value,
        locals={"r": r, "omega": omega, "I": sp.I, **state},
    )


def infinity_leading_coefficients() -> dict[str, sp.Expr]:
    """Reconstruct the exact leading E and R metric coefficients."""
    r, omega = sp.symbols("r omega", nonzero=True)

    reconstruction = json.loads(IMPORTS["complete_reconstruction"].read_text())
    heads = json.loads(IMPORTS["infinity_metric_heads"].read_text())["branches"]

    # E=2 EI2.  H0 is not separately stored in the metric-head table, so
    # derive it from the exact C=0 reconstruction row.
    ei2 = reconstruction["endpoint_bases"]["infinity"]["Einstein_kernel"]["EI2"]
    h1_coefficients = [
        parse_expr(value, r=r, omega=omega) for value in ei2["H1_head"]
    ]
    h1_power = parse_expr(ei2["H1_power"], r=r, omega=omega)
    phase = sp.exp(-2 * sp.I * omega * r) * r**h1_power
    h1_ei2 = phase * sum(
        coefficient / r**index
        for index, coefficient in enumerate(h1_coefficients)
    )
    f_ei2 = sp.diff(h1_ei2, r)
    h0_row = parse_expr(
        reconstruction["complete_reconstruction"]["H0_reconstruction"],
        r=r,
        omega=omega,
    )
    h0_ei2 = h0_row.subs(
        {
            sp.Symbol("H1"): h1_ei2,
            sp.Symbol("F"): f_ei2,
            sp.Symbol("P"): 0,
            sp.Symbol("Pp"): 0,
            sp.Symbol("Q"): 0,
            sp.Symbol("Qp"): 0,
        }
    )
    h0_ei2_lead = sp.simplify(sp.limit(h0_ei2 / phase, r, sp.oo))

    # R=XI2-c_R XI3 in the exact normalized outgoing frame.
    c_r = sp.I * (16 * omega**2 - 4 * sp.I * omega - 5) / omega

    def branch_coefficients(branch: str, component: str) -> list[sp.Expr]:
        return [
            parse_expr(value, r=r, omega=omega)
            for value in heads[branch][component][
                "coefficients_through_inverse_order_3"
            ]
        ]

    r_coefficients: dict[str, list[sp.Expr]] = {}
    for component in ("H0_from_C_equals_zero", "H1"):
        xi2 = branch_coefficients("XI2", component)
        xi3 = branch_coefficients("XI3", component)
        r_coefficients[component] = [
            sp.factor(sp.simplify(left - c_r * right))
            for left, right in zip(xi2, xi3)
        ]

    result = {
        "E_H0_r": sp.simplify(2 * h0_ei2_lead),
        "E_H1_r": sp.simplify(2 * h1_coefficients[0]),
        "R_H0_r2": r_coefficients["H0_from_C_equals_zero"][0],
        "R_H0_r": r_coefficients["H0_from_C_equals_zero"][1],
        "R_H1_r2": r_coefficients["H1"][0],
        "R_H1_r": r_coefficients["H1"][1],
    }

    assert result == {
        "E_H0_r": -1,
        "E_H1_r": 2,
        "R_H0_r2": sp.Rational(3, 4),
        "R_H0_r": -sp.Rational(3, 2),
        "R_H1_r2": -sp.Rational(3, 2),
        "R_H1_r": 0,
    }
    assert sp.simplify(
        result["R_H0_r2"] + sp.Rational(3, 4) * result["E_H0_r"]
    ) == 0
    assert sp.simplify(
        result["R_H1_r2"] + sp.Rational(3, 4) * result["E_H1_r"]
    ) == 0
    return result


def exact_data() -> dict:
    coefficients = infinity_leading_coefficients()
    omega, nu, kappa, alpha_w, alpha_n = sp.symbols(
        "omega nu kappa alpha_W alpha_n", nonzero=True
    )

    # In odd radiation gauge h_u'=0, xi=h_u/(i omega) and h2'=-2 xi.
    e_h2_r = sp.simplify(2 * sp.I * coefficients["E_H0_r"] / omega)
    r_h2_r2 = sp.simplify(2 * sp.I * coefficients["R_H0_r2"] / omega)
    r_h2_r = sp.simplify(2 * sp.I * coefficients["R_H0_r"] / omega)
    assert e_h2_r == -2 * sp.I / omega
    assert r_h2_r2 == 3 * sp.I / (2 * omega)
    assert r_h2_r == -3 * sp.I / omega

    # The parent double pole is -nu/(4 alpha_W alpha_n) E tensor tilde-u.
    scri_double = sp.simplify(
        (-nu / (4 * alpha_w * alpha_n)) * e_h2_r
    )
    contour_u = sp.simplify(sp.I * scri_double)
    contour_kappa = sp.simplify(
        contour_u.subs(nu, 2 * sp.I * kappa / omega)
    )
    assert scri_double == sp.I * nu / (2 * alpha_w * alpha_n * omega)
    assert contour_u == -nu / (2 * alpha_w * alpha_n * omega)
    assert contour_kappa == -sp.I * kappa / (
        alpha_w * alpha_n * omega**2
    )

    # Distinguish the fixed-frequency Jost derivative from the total
    # derivative along omega_n(m).  The latter has a Coulomb-log derivative,
    # but in the full spacetime phase it combines with t into null time.
    sigma, r, t, log_r = sp.symbols("sigma r t log_r")
    fixed_radial = -sigma * sp.I * r / (2 * omega)
    total_radial = (
        sigma * sp.I * (nu - 1 / (2 * omega)) * r
        + 2 * sigma * sp.I * nu * log_r
    )
    rstar_asymptotic = r + 2 * log_r
    null_time = t + sigma * rstar_asymptotic
    full_total = sp.expand(sp.I * nu * t + total_radial)
    phase_adapted = sp.expand(
        sp.I * nu * null_time - sigma * sp.I * r / (2 * omega)
    )
    assert sp.simplify(full_total - phase_adapted) == 0
    bach_phase_adapted = sp.simplify(
        (sp.I * omega / 2)
        * phase_adapted.subs(nu, 2 * sp.I * kappa / omega)
    )
    assert sp.simplify(
        bach_phase_adapted
        - (-sp.I * kappa * null_time + sigma * r / 4)
    ) == 0

    imports = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": digest(path),
        }
        for name, path in IMPORTS.items()
    }
    return {
        "schema": "axial-qnm-null-infinity-reconstruction-v1",
        "status": "EXACT_NULL_INFINITY_RECONSTRUCTION_SOURCE_OVERLAP_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "conventions": {
            "background": "Schwarzschild M=1",
            "sector": "axial ell=2",
            "fourier_phase": "exp(+I*omega*v)",
            "outgoing_physical_phase": "exp(-2*I*omega*rstar)",
            "retarded_time": "u=v-2*rstar",
            "odd_metric": (
                "h_{uA}=H0*X_A, h_{rA}=H1*X_A, "
                "h_{AB}=h2*X_AB"
            ),
            "bondi_shear_observable": "O_scri=lim_{r->infinity} h_AB/r",
            "strain": "h_AB/r**2",
            "gauge_class": (
                "standard small odd gauge transformations preserving "
                "the asymptotic Bondi frame"
            ),
        },
        "exact_asymptotic_reconstruction": {
            "common_retarded_phase": "exp(I*omega*u)",
            "E_normalization": "E=2*EI2",
            "R_normalization": (
                "R=XI2-I*(16*omega**2-4*I*omega-5)*XI3/omega"
            ),
            "E_metric": {
                "H0": "-r+O(1)",
                "H1": "2*r+O(1)",
            },
            "R_metric": {
                "H0": "3*r**2/4-3*r/2+O(1)",
                "H1": "-3*r**2/2+O(1)",
            },
            "leading_relation": "(H0,H1)_R=-3*r*(H0,H1)_E/4+O(E)",
            "moving_phase_rate_derivative": "-3/4",
        },
        "radiation_gauge": {
            "odd_gauge_law": "h_u_new=h_u-I*omega*xi; h2_new=h2-2*xi",
            "parameter": "xi=h_u/(I*omega)",
            "condition": "h_u_new=0",
            "reconstruction": "h2_new=2*I*h_u/omega",
            "E_h2": "-2*I*r*exp(I*omega*u)/omega+O(1)",
            "R_h2": (
                "(3*I*r**2/(2*omega)-3*I*r/omega+O(1))"
                "*exp(I*omega*u)"
            ),
            "E_bondi_shear": "-2*I*X_AB/omega",
            "E_bondi_shear_nonzero": True,
            "E_strain": (
                "-2*I*exp(I*omega*u)*X_AB/(omega*r)+O(r**-2)"
            ),
            "R_strain": (
                "3*I*exp(I*omega*u)*X_AB/(2*omega)+O(r**-1)"
            ),
            "R_standard_falloff": False,
            "linear_r_tangent_cancels": False,
            "weyl_gauge_cannot_remove_odd_tracefree_X_AB": True,
        },
        "qnm_tangent": {
            "fixed_omega_jost_derivative": (
                "-sigma*I*r/(2*omega)+O(1)"
            ),
            "fixed_omega_coulomb_exponent_derivative": "0",
            "total_qnm_radial_derivative": (
                "sigma*I*(nu-1/(2*omega))*r"
                "+2*sigma*I*nu*log(r)+O(1)"
            ),
            "total_coulomb_exponent_derivative": "2*sigma*I*nu",
            "phase_adapted_null_time": "u_sigma=t+sigma*rstar",
            "full_spacetime_tangent": (
                "I*nu*u_sigma-sigma*I*r/(2*omega)+O(1)"
            ),
            "bach_full_spacetime_tangent": (
                "-I*kappa*u_sigma+sigma*r/4+O(1)"
            ),
            "outgoing_sigma": "-1",
            "outgoing_null_time": "u=t-rstar",
            "outgoing_bach_tangent": "-I*kappa*u-r/4+O(1)",
            "normalization_changes_only_O1": True,
        },
        "observable_double_pole": {
            "parent_principal_operator": (
                "-nu*E tensor tilde_u/(4*alpha_W*alpha_n)"
            ),
            "scri_principal_coefficient": (
                "I*nu*X_AB tensor tilde_u/"
                "(2*alpha_W*alpha_n*omega)"
            ),
            "scri_principal_coefficient_nonzero_if": (
                "nu != 0 and alpha_W*alpha_n*omega != 0"
            ),
            "local_contour_strain_u_coefficient": (
                "-nu*u*exp(I*omega*u)*X_AB/"
                "(2*alpha_W*alpha_n*omega*r)"
            ),
            "selector_form": (
                "-I*kappa*u*exp(I*omega*u)*X_AB/"
                "(alpha_W*alpha_n*omega**2*r)"
            ),
            "source_factor": "<tilde_u,S(omega_n)F>",
            "source_overlap_status": "OPEN_FOR_SPECIFIED_PHYSICAL_SOURCE",
            "global_retarded_status": "OPEN",
        },
        "claim_flags": {
            "exact_E_metric_heads_reconstructed": True,
            "exact_R_metric_heads_reconstructed": True,
            "odd_radiation_gauge_reconstruction_exact": True,
            "einstein_bondi_shear_nonzero": True,
            "generalized_constant_component_standard_falloff": False,
            "scalar_linear_r_tangent_cancellation": False,
            "double_pole_observable_spatial_overlap_nonzero": True,
            "enhanced_local_contour_profile_standard_radiative": True,
            "specified_physical_source_overlap_nonzero": False,
            "full_generalized_mode_finite_bondi_flux": False,
            "global_causal_contour_theorem": False,
            "detector_observability": False,
        },
        "literature_convention": {
            "source": "Martel and Poisson, arXiv:gr-qc/0502028",
            "role": (
                "odd-parity gauge transformation and radiation-gauge "
                "normalization; all coefficient claims are rederived exactly"
            ),
        },
        "does_not_establish": [
            "nonzero excitation by a specified physical source",
            "a global retarded inverse-Laplace deformation",
            "finite Bondi flux or standard asymptotic flatness of the full generalized component",
            "a detector response or parameter-estimation theorem",
            "polar parity or multipoles other than axial ell=2",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = exact_data()
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
