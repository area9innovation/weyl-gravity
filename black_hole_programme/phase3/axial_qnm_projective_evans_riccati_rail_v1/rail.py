#!/usr/bin/env python3
"""Typed projective chart and one validated outgoing Riccati step."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from flint import acb, arb, ctx

from ..axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    midpoint,
    radius_from,
    reference_step,
    remainder_step,
)
from ..axial_qnm_ecs_centered_projective_initializer_v1 import (
    centered_initializer as ci,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "rail-run.json"

PANEL = 0
PANEL_COUNT = 512
ORDER = 26
R_START = Fraction(45)
STEP = Fraction(-1, 20)


def _fraction(path: tuple[str, ...]) -> Fraction:
    value = json.loads(ci.ECS.read_text())
    for key in path:
        value = value[key]
    return Fraction(value)


def exact_chart_identities() -> dict:
    """Check the generic CP1 chart and its two parameter tangents."""
    a11, a12, a21, a22 = sp.symbols("A11 A12 A21 A22")
    a11t, a12t, a21t, a22t = sp.symbols(
        "A11_tau A12_tau A21_tau A22_tau"
    )
    a11w, a12w, a21w, a22w = sp.symbols(
        "A11_omega A12_omega A21_omega A22_omega"
    )
    v, vt, vw = sp.symbols("v v_tau v_omega")
    f = a21 + (a22 - a11) * v - a12 * v**2
    fv = sp.diff(f, v)
    ft = (
        a21t + (a22t - a11t) * v - a12t * v**2
    )
    fw = (
        a21w + (a22w - a11w) * v - a12w * v**2
    )

    # Independent quotient-rule derivation from Y2/Y1.
    y1, y2 = sp.symbols("Y1 Y2", nonzero=True)
    quotient = sp.expand(
        ((a21 * y1 + a22 * y2) * y1
         - y2 * (a11 * y1 + a12 * y2)) / y1**2
    ).subs(y2, v * y1)
    if sp.simplify(quotient - f) != 0:
        raise RuntimeError("generic Riccati quotient identity failed")

    omega = sp.symbols("omega")
    potential, cocycle = sp.symbols("V calI")
    q = sp.symbols("q")
    scalar_f = 2 * sp.I * omega * q + potential - cocycle - q**2
    scalar_fv = sp.diff(scalar_f, q)
    # The intrinsic family is evaluated at tau=0, so its forcing is -calI.
    return {
        "generic_chart": "v=Y2/Y1",
        "generic_base": sp.sstr(f),
        "generic_F_v": sp.sstr(fv),
        "generic_tau": sp.sstr(ft + fv * vt),
        "generic_omega": sp.sstr(fw + fv * vw),
        "outgoing_phase": "psi=exp(-I*omega*r_star)*P_out",
        "implemented_chart": "q=(partial_x P_out)/P_out",
        "implemented_base": "q_x=2*I*omega*q+V-tau*calI-q**2",
        "implemented_tau": (
            "q_tau_x=(2*I*omega-2*q)*q_tau-calI"
        ),
        "implemented_omega": (
            "q_omega_x=(2*I*omega-2*q)*q_omega+2*I*q"
        ),
        "implemented_F_v": sp.sstr(
            scalar_fv.subs(cocycle, sp.symbols("tau") * cocycle)
        ),
    }


def outgoing_seed() -> tuple[acb, acb, acb, acb, acb]:
    """Reissue the refined outgoing seed, including its chart pivot."""
    ecs = json.loads(ci.ECS.read_text())
    tail = json.loads(ci.TAIL.read_text())
    tangent = json.loads(ci.TANGENT.read_text())
    spin2 = next(
        item for item in ecs["volterra"]["channels"]
        if item["channel"] == "spin_two"
    )
    omega = ci.panel_box(
        PANEL,
        PANEL_COUNT,
        Fraction(ecs["disk"]["center_re"]),
        Fraction(ecs["disk"]["center_im"]),
        Fraction(ecs["disk"]["radius"]),
    )
    omega_lower = Fraction(ecs["disk"]["omega_modulus_lower"])
    kappa = Fraction(ecs["disk"]["phase_decay_rate_lower"])
    alpha = Fraction(spin2["operator_norm_upper"])
    potential_point = Fraction(spin2["potential_point_upper_at_t0"])
    potential_weighted = Fraction(
        spin2["exponentially_weighted_integral_upper"]
    )
    source_kernel = Fraction(
        tangent["source_bounds"]["source_volterra_kernel_norm_upper"]
    )
    source_weighted = Fraction(
        tangent["source_bounds"][
            "source_exponentially_weighted_integral_upper"
        ]
    )
    radius = 45
    slope = Fraction(2, 3)

    base, aa, bb, cc = ci.base_series(omega, 16)
    residual = ci.apply_operator(base, aa, bb, cc)
    _, base_p, base_j, base_k = ci.residual_bounds(
        residual,
        radius=radius,
        slope=slope,
        kappa=kappa,
        omega_lower=omega_lower,
    )
    base_error = base_k / (1 - ci.af(alpha))
    base_error_x = base_j / (1 - ci.af(alpha))
    value_center, derivative_center = ci.evaluate(base, radius)
    value = ci.inflate(value_center, base_error)
    derivative = ci.inflate(derivative_center, base_error_x)
    if 0 in value:
        raise RuntimeError("outgoing reduced-amplitude pivot contains zero")
    q = derivative / value

    tau_coefficients, source = ci.tangent_series(
        omega, base, aa, bb, cc, 16
    )
    tau_residual = ci.tangent_residual(
        tau_coefficients, base, aa, bb, cc, source
    )
    _, _, tau_j, tau_k = ci.residual_bounds(
        tau_residual,
        radius=radius,
        slope=slope,
        kappa=kappa,
        omega_lower=omega_lower,
    )
    tau_error = (
        tau_k + ci.af(source_kernel) * base_error
    ) / (1 - ci.af(alpha))
    tau_error_x = (
        ci.af(potential_weighted) * tau_error
        + tau_j
        + ci.af(source_weighted) * base_error
    )
    tau_value_center, tau_derivative_center = ci.evaluate(
        tau_coefficients, radius
    )
    tau_value = ci.inflate(tau_value_center, tau_error)
    tau_derivative = ci.inflate(tau_derivative_center, tau_error_x)
    q_tau = (
        tau_derivative * value - derivative * tau_value
    ) / (value * value)

    _, omega_coefficients, oa, ob, ob_dot, oc = ci.omega_series(
        omega, 16
    )
    omega_residual = ci.omega_residual(
        base, omega_coefficients, oa, ob, ob_dot, oc
    )
    _, omega_p, omega_j, omega_k = ci.residual_bounds(
        omega_residual,
        radius=radius,
        slope=slope,
        kappa=kappa,
        omega_lower=omega_lower,
    )
    kernel_omega = (
        ci.af(potential_point)
        / (ci.af(omega_lower) * ci.af(kappa) ** 2)
        + ci.af(alpha) / ci.af(omega_lower)
    )
    residual_kernel_omega = (
        base_p / (ci.af(omega_lower) * ci.af(kappa) ** 2)
        + base_k / ci.af(omega_lower)
    )
    omega_error = (
        omega_k + residual_kernel_omega + kernel_omega * base_error
    ) / (1 - ci.af(alpha))
    omega_error_x = (
        omega_j
        + 2 * base_p / ci.af(kappa) ** 2
        + ci.af(potential_weighted) * omega_error
        + 2 * ci.af(potential_point) * base_error / ci.af(kappa) ** 2
    )
    omega_value_center, omega_derivative_center = ci.evaluate(
        omega_coefficients, radius
    )
    omega_value = ci.inflate(omega_value_center, omega_error)
    omega_derivative = ci.inflate(
        omega_derivative_center, omega_error_x
    )
    q_omega = (
        omega_derivative * value - derivative * omega_value
    ) / (value * value)
    return omega, value, q, q_tau, q_omega


def compute() -> dict:
    ctx.prec = 128
    identities = exact_chart_identities()
    omega, pivot, q, q_tau, q_omega = outgoing_seed()
    omega_center = midpoint(omega)
    omega_radius = radius_from(omega, omega_center)
    q_center = midpoint(q)
    qt_center = midpoint(q_tau)
    qw_center = midpoint(q_omega)
    q_radius = radius_from(q, q_center)
    qt_radius = radius_from(q_tau, qt_center)
    qw_radius = radius_from(q_omega, qw_center)

    reference, reference_metadata = reference_step(
        R_START,
        STEP,
        q_center,
        qt_center,
        qw_center,
        omega_center,
        order=ORDER,
    )
    if reference is None:
        return {
            "schema": "phase3-axial-qnm-projective-evans-riccati-run-v1",
            "passed": False,
            "failure": {
                "stage": "singleton_reference",
                **reference_metadata,
            },
            "identities": identities,
        }
    q1, qt1, qw1 = (midpoint(item) for item in reference)
    remainder, remainder_metadata = remainder_step(
        q_radius=q_radius,
        eta_radius=qt_radius,
        xi_radius=qw_radius,
        r0=R_START,
        step=STEP,
        omega_radius=omega_radius,
        omega_center=omega_center,
        q0=q_center,
        q1=q1,
        eta0=qt_center,
        eta1=qt1,
        xi0=qw_center,
        xi1=qw1,
        omega_lower=_fraction(("disk", "omega_modulus_lower")),
    )
    if remainder is None:
        return {
            "schema": "phase3-axial-qnm-projective-evans-riccati-run-v1",
            "passed": False,
            "failure": {
                "stage": "shared_parameter_remainder",
                **remainder_metadata,
            },
            "identities": identities,
        }
    q_rem, qt_rem, qw_rem = remainder
    q_rem += radius_from(reference[0], q1)
    qt_rem += radius_from(reference[1], qt1)
    qw_rem += radius_from(reference[2], qw1)
    next_q = ci.inflate(q1, q_rem)
    next_qt = ci.inflate(qt1, qt_rem)
    next_qw = ci.inflate(qw1, qw_rem)
    return {
        "schema": "phase3-axial-qnm-projective-evans-riccati-run-v1",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "passed": True,
        "identities": identities,
        "spectral_panel": {
            "panel": PANEL,
            "panel_count": PANEL_COUNT,
            "omega_box": str(omega),
            "omega_center": str(omega_center),
            "omega_remainder_radius": str(omega_radius.upper()),
        },
        "chart_gate": {
            "chart": "q=(partial_x P_out)/P_out",
            "pivot": "P_out",
            "pivot_ball": str(pivot),
            "pivot_modulus_lower": str(pivot.abs_lower()),
            "pivot_excludes_zero": 0 not in pivot,
            "reciprocal_chart_used": False,
            "analytic_chart_through_step": True,
            "reason": (
                "the initial pivot excludes zero and the validated Riccati "
                "self-map encloses a finite analytic q solution on the "
                "complete Taylor disk"
            ),
        },
        "initial_state": {
            "radius": str(R_START),
            "q": str(q),
            "q_tau": str(q_tau),
            "q_omega": str(q_omega),
        },
        "transport": {
            "from_r": str(R_START),
            "to_r": str(R_START + STEP),
            "step": str(STEP),
            "taylor_order": ORDER,
            "q": str(next_q),
            "q_tau": str(next_qt),
            "q_omega": str(next_qw),
            "remainder_radii": {
                "q": str(q_rem.upper()),
                "q_tau": str(qt_rem.upper()),
                "q_omega": str(qw_rem.upper()),
            },
            "reference_gate": reference_metadata,
            "remainder_gate": remainder_metadata,
        },
        "scope": {
            "endpoint": "outgoing infinity",
            "line": "phase-factored spin-two outgoing line",
            "radial_panel_count": 1,
            "two_sided": False,
        },
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
