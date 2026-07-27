#!/usr/bin/env python3
"""Produce the analytic complete-massive Jost crosswalk certificate.

The machine checks exact endpoint normal forms and the finite-dimensional
Schur derivative.  The accompanying report supplies the standard
Frobenius/Volterra existence and uniqueness argument that turns those
identities into analytic endpoint planes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import acb, arb
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
INPUTS = {
    "complete_massive_first_jet": (
        ROOT
        / "black_hole_programme/phase4/"
        "axial_complete_massive_jet_crosswalk_v1/certificate.json"
    ),
    "ecs_inverse_tortoise": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_qnm_ecs_inverse_tortoise_v1/certificate.json"
    ),
    "intrinsic_qnm_selector": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_qnm_projective_evans_contour_completion/"
        "local_selector_v1/certificate.json"
    ),
    "spin_one_local_unit": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_qnm_spin_one_local_unit_v1/certificate.json"
    ),
}

R, W, M, K, SIGMA = sp.symbols(
    "r omega m k sigma", nonzero=True
)
I = sp.I
F = (R - 2) / R


def exact(value: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(value))


def encode(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(exact(value)))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dstar(value: sp.Expr) -> sp.Expr:
    return exact(F * sp.diff(value, R))


def matrix_strings(value: sp.Matrix) -> list[list[str]]:
    return [[encode(entry) for entry in row] for row in value.tolist()]


def produce() -> dict:
    # The complete Q,Z equation is Psi''+[(omega^2-mf)I+B]Psi=0.
    coupling = sp.Matrix(
        [
            [
                -F * (10 / R**2 - 16 / R**3),
                -8 * F * (R - 3) / R**3,
            ],
            [-2 * F / R**2, -F * (4 / R**2 + 2 / R**3)],
        ]
    ).applyfunc(exact)
    coupling_limit = (R**2 * coupling).applyfunc(
        lambda value: sp.limit(value, R, sp.oo)
    )
    horizon_coupling = (coupling / F).applyfunc(
        lambda value: exact(value).subs(R, 2)
    )

    # Exact Coulomb phase in tortoise coordinates:
    # phi_sigma=exp(sigma*i*k*x) r^(sigma*i*m/k).
    # Thus D log(phi)=sigma*i*(k+m*f/(k*r)).
    phase_log_derivative = exact(
        SIGMA * I * (K + M * F / (K * R))
    )
    phase_residual = exact(
        dstar(phase_log_derivative)
        + phase_log_derivative**2
        + (K**2 + M)
        - M * F
    ).subs(SIGMA**2, 1)
    expected_residual = exact(
        M
        * (
            4 * K**2 * R**2
            - I * K * R**2 * SIGMA
            + 6 * I * K * R * SIGMA
            - 8 * I * K * SIGMA
            - M * R**2
            + 4 * M * R
            - 4 * M
        )
        / (K**2 * R**4)
    )
    if exact(phase_residual - expected_residual) != 0:
        raise RuntimeError("Coulomb phase residual drift")
    residual_order = sp.limit(R**2 * phase_residual, R, sp.oo)

    k_mass_derivative = -sp.Rational(1, 2) / W
    rho = SIGMA * I * (2 * K + M / K)
    rho_mass_derivative = exact(
        sp.diff(rho, M)
        + sp.diff(rho, K) * k_mass_derivative
    ).subs({M: 0, K: W})
    if rho_mass_derivative != 0:
        raise RuntimeError("Coulomb exponent derivative no longer cancels")

    # At z=f=0, D=(z(1-z)^2/2)d/dz and the indicial roots are
    # lambda=+/-2*i*omega, each with multiplicity two.
    LAMBDA, N = sp.symbols("lam n")
    indicial = exact(LAMBDA**2 / 4 + W**2)
    plus_denominator = exact(
        ((LAMBDA + N) ** 2 / 4 + W**2).subs(
            LAMBDA, 2 * I * W
        )
    )
    minus_denominator = exact(
        ((LAMBDA + N) ** 2 / 4 + W**2).subs(
            LAMBDA, -2 * I * W
        )
    )

    # The certified root disk stays away from the imaginary axis, hence
    # from every Frobenius resonance omega=+/- i*n/4.
    selector = json.loads(INPUTS["intrinsic_qnm_selector"].read_text())
    qnm = selector["result"]["qnm_enclosure"]
    center_re = sp.Rational(qnm["center_re"])
    center_im = sp.Rational(qnm["center_im"])
    radius = sp.Rational(qnm["radius"])
    real_axis_margin = abs(center_re) - radius
    if real_axis_margin <= 0:
        raise RuntimeError("QNM disk reaches the Frobenius resonance axis")

    # An explicit small mass polydisc on which k=sqrt(omega^2-m), k(omega,0)
    # =omega, is analytic.  The stronger |omega| lower bound is unnecessary.
    mass_radius = sp.Rational(1, 10**6)
    k_square_margin = exact(real_axis_margin**2 - mass_radius)
    if k_square_margin <= 0:
        raise RuntimeError("declared mass polydisc can meet k=0")
    binomial_parameter_upper = exact(
        mass_radius / real_axis_margin**2
    )
    if binomial_parameter_upper >= 1:
        raise RuntimeError("wave-number binomial disk is not contractive")

    # On the imported pi/4 ECS ray, exp(-i*omega*x) decays.  This exact
    # lower bound exceeds 1/5 at m=0; analyticity leaves a smaller common
    # positive bound on the declared local mass polydisc.
    decay_at_zero_lower = exact(
        -(center_re + center_im + 2 * radius) / sp.sqrt(2)
    )
    if not bool(decay_at_zero_lower > sp.Rational(1, 5)):
        raise RuntimeError("outgoing ECS decay margin drift")
    decay_on_mass_disk_lower = exact(
        decay_at_zero_lower - mass_radius / real_axis_margin
    )
    if not bool(decay_on_mass_disk_lower > sp.Rational(1, 5)):
        raise RuntimeError("massive outgoing ECS decay margin drift")

    # Same-sign vector mixing is harmless at first order.  The derivative
    # of the spin-two Schur complement ignores O(m) off-diagonal blocks.
    a, g, a1, b1, c1, g1, eps = sp.symbols(
        "a g a1 b1 c1 g1 eps", nonzero=True
    )
    connection = sp.Matrix(
        [[a + eps * a1, eps * b1], [eps * c1, g + eps * g1]]
    )
    schur = exact(
        connection[0, 0]
        - connection[0, 1] * connection[1, 1] ** -1
        * connection[1, 0]
    )
    schur_derivative = exact(sp.diff(schur, eps).subs(eps, 0))
    determinant_root_derivative = exact(
        sp.diff(connection.det(), eps).subs({eps: 0, a: 0})
    )
    if schur_derivative != a1 or determinant_root_derivative != a1 * g:
        raise RuntimeError("spin-one Schur derivative drift")

    # Propagate the certified intrinsic selector through
    # nu=2*i*kappa/(3*omega).  The imported selector ball is
    # Re(kappa)=0+/-0.0468, Im(kappa)=0.1+/-0.0371.
    if selector["result"]["kappa_beta_over_alpha_enclosure"] != (
        "[+/- 0.0468] + [0.1 +/- 0.0371]j"
    ):
        raise RuntimeError("imported selector enclosure format drift")
    kappa_ball = acb(arb("0 +/- 0.0468"), arb("0.1 +/- 0.0371"))
    omega_ball = acb(
        arb(f"{float(center_re)} +/- {float(radius)}"),
        arb(f"{float(center_im)} +/- {float(radius)}"),
    )
    velocity_ball = 2 * acb(0, 1) * kappa_ball / (3 * omega_ball)
    velocity_re_outer = arb("0.169 +/- 0.082")
    velocity_im_outer = arb("0.0405 +/- 0.0945")
    if not velocity_re_outer.contains(velocity_ball.real):
        raise RuntimeError("velocity real enclosure drift")
    if not velocity_im_outer.contains(velocity_ball.imag):
        raise RuntimeError("velocity imaginary enclosure drift")
    if velocity_re_outer.contains(0):
        raise RuntimeError("reported velocity enclosure does not exclude zero")

    first_jet = json.loads(INPUTS["complete_massive_first_jet"].read_text())
    spin_one = json.loads(INPUTS["spin_one_local_unit"].read_text())
    ecs = json.loads(INPUTS["ecs_inverse_tortoise"].read_text())
    if not first_jet["claim_flags"]["factor_three_Bach_mass_crosswalk_exact"]:
        raise RuntimeError("complete first-jet authority is not green")
    if not spin_one["claim_flags"]["spin_one_jost_factor_unit_on_local_disk"]:
        raise RuntimeError("spin-one local unit authority is not green")
    if not ecs["claim_flags"]["ecs_inverse_tortoise_branch_certified"]:
        raise RuntimeError("ECS branch authority is not green")
    if not selector["claim_flags"]["intrinsic_tangent_selector_nonzero"]:
        raise RuntimeError("intrinsic selector authority is not green")

    document = {
        "schema": "phase4-axial-massive-jost-crosswalk-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE4_AXIAL_MASSIVE_JOST_CROSSWALK",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "ANALYTIC_COMPLETE_MASSIVE_JOST_CROSSWALK_AND_NONZERO_QNM_VELOCITY"
        ),
        "scope": {
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2 complete coupled Q,Z tensor system",
            "frequency_convention": "exp(+I*omega*t)",
            "mass_parameter": "m=mu**2, signed squared-mass coefficient",
            "qnm_center": {
                "re": str(center_re),
                "im": str(center_im),
                "radius": str(radius),
            },
            "local_mass_radius": str(mass_radius),
            "claim_kind": "REDUCED-MODE analytic endpoint and QNM branch",
        },
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
            }
            for name, path in INPUTS.items()
        },
        "infinity_jost": {
            "equation": (
                "D**2 Psi+(((omega**2-m*f)*I_2)+B(r))*Psi=0"
            ),
            "coupling_matrix_B": matrix_strings(coupling),
            "r_squared_coupling_limit": matrix_strings(coupling_limit),
            "row_sum_majorant": (
                "(1+2/R)*(18/R**2+40/R**3), R>=45"
            ),
            "wave_number": "k=sqrt(omega**2-m), k(omega,0)=omega",
            "binomial_parameter_abs_upper": encode(
                binomial_parameter_upper
            ),
            "phase": (
                "phi_sigma=exp(sigma*I*k*x)*r**(sigma*I*m/k)"
            ),
            "phase_log_derivative": encode(phase_log_derivative),
            "phase_residual": encode(phase_residual),
            "r_squared_phase_residual_limit": encode(residual_order),
            "coulomb_exponent": "sigma*I*(2*k+m/k)",
            "coulomb_exponent_mass_derivative_at_zero": encode(
                rho_mass_derivative
            ),
            "ecs_ray": "x=x(45)+exp(I*pi/4)*t",
            "decay_at_m_zero_lower": encode(decay_at_zero_lower),
            "decay_on_declared_mass_disk_lower": encode(
                decay_on_mass_disk_lower
            ),
            "two_stage_construction": [
                "scalar Coulomb Volterra equation with O(r**-2) residual",
                "matrix Volterra equation with B(r)=O(r**-2)",
            ],
            "analyticity": (
                "uniform Neumann series on a smaller parameter polydisc"
            ),
            "uniqueness": (
                "the sectorial Volterra normalization excludes the "
                "opposite exponential and defines a two-dimensional "
                "outgoing Jost plane up to analytic right GL(2)"
            ),
        },
        "horizon_jost": {
            "coordinate": "z=f=(r-2)/r",
            "derivative": "D=(z*(1-z)**2/2)*d/dz",
            "mass_and_coupling_order": "O(z)",
            "coupling_over_f_at_horizon": matrix_strings(horizon_coupling),
            "indicial_polynomial": encode(indicial),
            "indicial_roots": ["2*I*omega", "-2*I*omega"],
            "multiplicity_each": 2,
            "plus_recursion_denominator": encode(plus_denominator),
            "minus_recursion_denominator": encode(minus_denominator),
            "qnm_disk_real_axis_margin": encode(real_axis_margin),
            "analyticity": (
                "convergent nonresonant matrix Frobenius series in "
                "(z,omega,m)"
            ),
            "uniqueness": (
                "the selected exponent defines a two-dimensional ingoing "
                "plane up to analytic right GL(2)"
            ),
        },
        "endpoint_crosswalk": {
            "bach_to_complete_mass_tangent": "3*I*omega/2",
            "infinity_linear_term": (
                "(3*I*omega/2)*(-sigma*I*r/(6*omega))=sigma*r/4"
            ),
            "horizon_statement": (
                "the rational gauges are regular and preserve the selected "
                "Frobenius exponent"
            ),
            "opposite_jost_exclusion": (
                "after the exact leading phase match, the difference is "
                "homogeneous in the same Volterra/Frobenius class; endpoint "
                "uniqueness permits only same-sign analytic basis changes"
            ),
            "normalization_freedom": (
                "analytic right GL(2) endpoint changes add an analytic "
                "multiple of the unperturbed reduced Evans divisor"
            ),
        },
        "schur_reduction": {
            "connection_model": matrix_strings(connection),
            "spin_two_schur_complement": encode(schur),
            "mass_derivative_at_zero": encode(schur_derivative),
            "determinant_derivative_at_spin_two_root": encode(
                determinant_root_derivative
            ),
            "spin_one_unit": True,
            "conclusion": (
                "same-sign spin-one mixing is off-diagonal O(m) and does "
                "not enter the first derivative of the reduced spin-two "
                "divisor"
            ),
        },
        "mass_velocity": {
            "identity_at_qnm": (
                "b_B(omega_n)=(3*I*omega_n/2)"
                "*partial_m a_phys(omega_n,0)"
            ),
            "formula": "nu_n=2*I*kappa_n/(3*omega_n)",
            "parameter": "signed squared mass m=mu**2",
            "certified_outer_enclosure": {
                "re": ["0.087", "0.251"],
                "im": ["-0.054", "0.135"],
            },
            "excludes_zero": True,
        },
        "claim_flags": {
            "parameter_analytic_horizon_jost_plane": True,
            "parameter_analytic_infinity_jost_plane": True,
            "opposite_jost_admixture_excluded": True,
            "complete_massive_jost_crosswalk": True,
            "physical_squared_mass_qnm_velocity_identified": True,
            "physical_squared_mass_qnm_velocity_nonzero": True,
            "global_causal_resolvent_certified": False,
        },
        "does_not_establish": [
            "a global weighted exterior Fredholm domain",
            "a retarded inverse-Laplace contour deformation",
            "a complete causal quasinormal expansion or late-time theorem",
            "standard asymptotic falloff of the constant generalized metric component",
            "a real causal or specified astrophysical source",
        ],
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return document


if __name__ == "__main__":
    result = produce()
    print(result["status"])
