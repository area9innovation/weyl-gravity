#!/usr/bin/env python3
"""Produce an exact pi/4 ECS branch and scalar Volterra contraction certificate."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TAIL = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_infinity_tail_gate_v1"
    / "certificate.json"
)
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md",
    "report.md",
    "schema.json",
    "produce.py",
    "verify.py",
    "test_ecs_inverse_tortoise.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def scalar_gate(
    *,
    name: str,
    potential: str,
    integral_bound: Fraction,
    point_bound: Fraction,
    omega_lower: Fraction,
    kappa_lower: Fraction,
) -> dict:
    exponential_integral = point_bound / kappa_lower
    operator_norm = (integral_bound + exponential_integral) / (2 * omega_lower)
    if operator_norm >= 1:
        raise RuntimeError(f"{name} Volterra bound is not contractive")
    margin = 1 - operator_norm
    value_radius = operator_norm / margin
    derivative_radius = exponential_integral / margin
    if value_radius >= 1:
        raise RuntimeError(f"{name} reduced Jost value ball contains zero")
    return {
        "channel": name,
        "potential": potential,
        "potential_integral_upper": text(integral_bound),
        "potential_point_upper_at_t0": text(point_bound),
        "exponentially_weighted_integral_upper": text(exponential_integral),
        "operator_norm_upper": text(operator_norm),
        "contraction_margin_lower": text(margin),
        "reduced_value_ball": {
            "center": "1",
            "radius": text(value_radius),
            "excludes_zero": True,
        },
        "reduced_x_derivative_ball": {
            "center": "0",
            "radius": text(derivative_radius),
        },
    }


def produce() -> dict:
    tail = json.loads(TAIL.read_text())
    disk = tail["disk"]
    center_re = Fraction(disk["center_re"])
    center_im = Fraction(disk["center_im"])
    radius = Fraction(disk["radius"])
    omega_lower = Fraction(disk["omega_modulus_lower_from_real_part"])
    delta = Fraction(tail["ecs_replacement"]["delta"])

    if omega_lower <= 0 or delta <= 0:
        raise RuntimeError("imported spectral disk lacks the required margins")

    # Along x=x0+zeta*t, r solves dr/dt=zeta*(r-2)/r.  If
    # r=a+i*b with a>=45 and b>=0, then
    #
    # Re dr/dt >= (1-(1+sqrt(2))/45)/sqrt(2)
    #           = (22*sqrt(2)-1)/45 > 2/3.
    #
    # The final strict inequality is equivalent to 22*sqrt(2)>31 and is
    # certified by 968>961 after squaring positive quantities.
    radial_slope_lower = Fraction(2, 3)
    if 22 * 22 * 2 <= 31 * 31:
        raise RuntimeError("radial slope comparison failed")

    r0 = 45
    # |r(t)| >= 45+(2/3)t.  Integrating the rational potential majorants
    # gives the following exact L1 bounds.
    spin1_integral = Fraction(6, 1) / radial_slope_lower * (
        Fraction(1, r0) + Fraction(1, r0**2)
    )
    spin2_integral = Fraction(6, 1) / radial_slope_lower * (
        Fraction(1, r0)
        + Fraction(3, 2 * r0**2)
        + Fraction(2, 3 * r0**3)
    )
    spin1_point = Fraction(6, 1) * (
        Fraction(1, r0**2) + Fraction(2, r0**3)
    )
    spin2_point = Fraction(6, 1) * (
        Fraction(1, r0**2)
        + Fraction(3, r0**3)
        + Fraction(2, r0**4)
    )

    # sqrt(2)>7/5 gives a rational lower bound for the ECS decay exponent.
    if 2 * 25 <= 49:
        raise RuntimeError("sqrt(2)>7/5 comparison failed")
    kappa_lower = Fraction(7, 5) * delta

    gates = [
        scalar_gate(
            name="spin_one",
            potential="6*(r-2)/r**3",
            integral_bound=spin1_integral,
            point_bound=spin1_point,
            omega_lower=omega_lower,
            kappa_lower=kappa_lower,
        ),
        scalar_gate(
            name="spin_two",
            potential="6*(r-2)*(r-1)/r**4",
            integral_bound=spin2_integral,
            point_bound=spin2_point,
            omega_lower=omega_lower,
            kappa_lower=kappa_lower,
        ),
    ]

    return {
        "schema": "phase3-axial-qnm-ecs-inverse-tortoise-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "EXACT_ECS_INVERSE_TORTOISE_BRANCH_AND_UNIFORM_SCALAR_"
            "VOLTERRA_CONTRACTION_WITH_COARSE_REDUCED_INITIALIZER"
        ),
        "imports": {
            "infinity_tail_gate": {
                "path": str(TAIL.relative_to(ROOT)),
                "sha256": sha256(TAIL),
                "authority": (
                    "exact seed-disk geometry, omega lower bound and "
                    "pi/4 phase-damping margin"
                ),
            }
        },
        "disk": {
            "center_re": str(center_re),
            "center_im": str(center_im),
            "radius": str(radius),
            "omega_modulus_lower": text(omega_lower),
            "phase_delta": text(delta),
            "phase_decay_rate_lower": text(kappa_lower),
        },
        "inverse_tortoise_branch": {
            "mass": 1,
            "starting_radius": r0,
            "starting_tortoise": "45+2*log(43/2)",
            "ray": "x(t)=x0+exp(I*pi/4)*t, t>=0",
            "tortoise_map": "x(r)=r+2*Log(r/2-1)",
            "inverse_ode": "dr/dt=exp(I*pi/4)*(r-2)/r, r(0)=45",
            "invariant_region": "Re(r)>=45 and Im(r)>=0",
            "real_part_slope_exact_lower": "(22*sqrt(2)-1)/45",
            "real_part_slope_rational_lower": text(radial_slope_lower),
            "strict_slope_witness": "22*sqrt(2)>31 because 968>961",
            "radial_growth": "abs(r(t))>=Re(r(t))>=45+(2/3)*t",
            "distance_from_zero_lower": "45",
            "distance_from_horizon_lower": "43",
            "principal_log_domain": "Re(r-2)>=43",
            "analytic_inverse_on_ray_neighbourhood": True,
            "avoidance_of_r0_and_r2": True,
            "proof_note": (
                "The ODE preserves the invariant region and has bounded "
                "holomorphic vector field there. Differentiating the "
                "principal-log tortoise map along the solution gives "
                "dx/dt=exp(I*pi/4). Since x'(r)=r/(r-2) has positive real "
                "part on Re(r)>2, the branch is locally univalent and "
                "continues analytically along the ray."
            ),
        },
        "volterra": {
            "factored_unknown": "y=exp(-I*omega*x)*v",
            "equation": (
                "v(x)=1+integral_x^infinity "
                "(1-exp(2*I*omega*(x-s)))/(2*I*omega)"
                "*V(r(s))*v(s) ds"
            ),
            "kernel_bound": (
                "|K(t,u)|<=(1+exp(-kappa*(u-t)))/(2*|omega|)"
            ),
            "potential_majorants": {
                "spin_one": "6*(R**-2+2*R**-3)",
                "spin_two": "6*(R**-2+3*R**-3+2*R**-4)",
                "R": "45+(2/3)*t",
            },
            "channels": gates,
            "uniform_contraction_on_closed_disk": True,
            "analytic_frequency_dependence": (
                "uniformly convergent Neumann series on the closed disk"
            ),
            "initializer_scope": (
                "coarse parameter-uniform balls for the reduced scalar "
                "Jost value v(x0) and derivative dv/dx(x0)"
            ),
        },
        "claim_flags": {
            "ecs_inverse_tortoise_branch_certified": True,
            "ecs_branch_avoids_r0_and_r2": True,
            "spin_one_ecs_volterra_contraction_certified": True,
            "spin_two_ecs_volterra_contraction_certified": True,
            "coarse_reduced_scalar_outgoing_initializer_constructed": True,
            "full_bach_outgoing_frame_constructed": False,
            "finite_interval_complex_transport_certified": False,
            "Evans_boundary_nonzero_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "next_gates": [
            (
                "transport the coarse reduced scalar balls from r=45 to a "
                "finite matching point with validated complex arithmetic"
            ),
            (
                "construct compatible endpoint tau-jets and the mixed "
                "spin-two/spin-one four-state outgoing frame"
            ),
            (
                "combine the outgoing column with a validated horizon column "
                "on the complete contour boundary"
            ),
        ],
        "does_not_establish": [
            "a full six-state or four-state Bach outgoing frame",
            "validated finite-interval complex transport from r=45",
            "nonvanishing of an Evans/Jost determinant on a contour",
            "an argument-principle QNM root count",
            "a defective Smith fibre, QNM or EP2",
            "time-domain stability or a Lorentzian-causal theorem",
        ],
    }


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-ecs-inverse-tortoise-receipt-v1",
        "producer": "produce.py",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "input_sha256": {"infinity_tail_gate": sha256(TAIL)},
        "artifact_sha256": {
            name: sha256(HERE / name) for name in ARTIFACTS
        },
        "commands": [
            (
                "python3 -m black_hole_programme.phase3."
                "axial_qnm_ecs_inverse_tortoise_v1.produce"
            ),
            (
                "python3 -m black_hole_programme.phase3."
                "axial_qnm_ecs_inverse_tortoise_v1.verify"
            ),
            (
                "python3 -m unittest -v black_hole_programme.phase3."
                "axial_qnm_ecs_inverse_tortoise_v1."
                "test_ecs_inverse_tortoise"
            ),
            (
                "python3 -m py_compile black_hole_programme/phase3/"
                "axial_qnm_ecs_inverse_tortoise_v1/produce.py "
                "black_hole_programme/phase3/"
                "axial_qnm_ecs_inverse_tortoise_v1/verify.py "
                "black_hole_programme/phase3/"
                "axial_qnm_ecs_inverse_tortoise_v1/"
                "test_ecs_inverse_tortoise.py"
            ),
        ],
        "tier_2_not_run": (
            "No shared operator changed; the package independently advances "
            "one imported exact infinity-tail gate."
        ),
        "tier_3_not_run": "Not a freeze, release or physical theorem promotion.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
