#!/usr/bin/env python3
"""Switch the horizon projective rail from q to p=1/q and continue to r=4."""
from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

from ..axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    convolution,
    midpoint,
    radius_from,
    strict_candidate,
    taylor_coefficients,
)
from ..axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    ECS,
    af,
    inflate,
)
from ..axial_qnm_horizon_projective_preflight_v1.horizon_preflight import (
    forward_remainder,
    horizon_seed,
    reference_step,
)

HERE = Path(__file__).resolve().parent
RUN = HERE / "reciprocal-run.json"


def first_obstruction(panel: int) -> dict:
    """Reproduce the q-chart rail up to its first certified obstruction."""
    ecs = json.loads(ECS.read_text())
    omega_lower = Fraction(ecs["disk"]["omega_modulus_lower"])
    omega_box, q_box, eta_box, xi_box, *_ = horizon_seed(panel)
    omega_center = midpoint(omega_box)
    delta = radius_from(omega_box, omega_center)
    # Keep the sign convention used by the predecessor: E=-q_tau, X=-q_omega.
    q_center = midpoint(q_box)
    e_center = midpoint(-eta_box)
    x_center = midpoint(-xi_box)
    dq = radius_from(q_box, q_center)
    de = radius_from(-eta_box, e_center)
    dx = radius_from(-xi_box, x_center)
    r = Fraction(2) + Fraction(1, 2**22)
    steps = 0
    while r < 4:
        rho = r - 2
        step = min(rho / 16, Fraction(1, 20), Fraction(4) - r)
        reference, metadata = reference_step(
            r, step, q_center, e_center, x_center, -omega_center
        )
        if reference is None:
            return {
                "panel": panel,
                "omega_box": omega_box,
                "omega_center": omega_center,
                "omega_radius": delta,
                "radius": r,
                "steps": steps,
                "failure": metadata["failure"],
                "q_center": q_center,
                "e_center": e_center,
                "x_center": x_center,
                "q_radius": dq,
                "e_radius": de,
                "x_radius": dx,
            }
        q1, e1, x1 = (midpoint(value) for value in reference)
        remainder, failure = forward_remainder(
            dq, de, dx, r, step, delta, omega_center,
            q_center, q1, e_center, e1, x_center, x1, omega_lower,
        )
        if remainder is None:
            return {
                "panel": panel,
                "omega_box": omega_box,
                "omega_center": omega_center,
                "omega_radius": delta,
                "radius": r,
                "steps": steps,
                "failure": failure,
                "q_center": q_center,
                "e_center": e_center,
                "x_center": x_center,
                "q_radius": dq,
                "e_radius": de,
                "x_radius": dx,
            }
        dq, de, dx = remainder
        dq += radius_from(reference[0], q1)
        de += radius_from(reference[1], e1)
        dx += radius_from(reference[2], x1)
        q_center, e_center, x_center = q1, e1, x1
        r += step
        steps += 1
    raise RuntimeError("q chart unexpectedly reached r=4 without an obstruction")


def product(left: list[acb], right: list[acb], n: int) -> acb:
    return convolution(left, right, n)


def triple(left: list[acb], middle: list[acb],
           right: list[acb], n: int) -> acb:
    return sum(
        (
            left[j] * middle[k] * right[n - j - k]
            for j in range(n + 1)
            for k in range(n - j + 1)
        ),
        acb(0),
    )


def p_reference_step(
    r0: Fraction,
    step: Fraction,
    p0: acb,
    eta0: acb,
    xi0: acb,
    omega: acb,
    order: int = 14,
) -> tuple[tuple | None, dict]:
    """Taylor/majorant step for p=1/q and its shared tau/omega derivatives."""
    c_series, b_series, i_series = taylor_coefficients(r0, order, omega)
    p_series = [p0]
    eta_series = [eta0]
    xi_series = [xi0]
    for n in range(order - 1):
        p_rhs = c_series[n]
        eta_rhs = acb(0)
        xi_rhs = acb(0)
        for k in range(n + 1):
            p_rhs += 2j * omega * c_series[k] * p_series[n - k]
            p_rhs -= b_series[k] * product(p_series, p_series, n - k)
            eta_rhs += (
                2j * omega * c_series[k] * eta_series[n - k]
                - 2 * b_series[k] * product(p_series, eta_series, n - k)
            )
            xi_rhs += (
                2j * omega * c_series[k] * xi_series[n - k]
                + 2j * c_series[k] * p_series[n - k]
                - 2 * b_series[k] * product(p_series, xi_series, n - k)
            )
        eta_rhs += triple(c_series, i_series, [
            product(p_series, p_series, k) for k in range(n + 1)
        ], n)
        p_series.append(p_rhs / (n + 1))
        eta_series.append(eta_rhs / (n + 1))
        xi_series.append(xi_rhs / (n + 1))

    rho = 2 * abs(step)
    r_lower = af(r0 - rho)
    r_upper = af(r0 + rho)
    c_bound = r_upper / (r_lower - 2)
    b_bound = 6 * (r_upper + 1) / r_lower**3
    omega_bound = omega.abs_upper()
    p_initial = p0.abs_upper()
    qa = af(rho) * b_bound
    qb = af(rho) * 2 * omega_bound * c_bound - 1
    qc = p_initial + af(rho) * c_bound
    discriminant = qb * qb - 4 * qa * qc
    metadata = {"failure": None}
    if discriminant.lower() <= 0:
        metadata["failure"] = "RECIPROCAL_REFERENCE_P_MAJORANT_DISCRIMINANT"
        return None, metadata
    proposed = (
        -float(qb.mid()) - math.sqrt(float(discriminant.lower()))
    ) / (2 * float(qa.lower()))
    p_bound = arb(proposed * 1.000001)
    p_rhs_bound = p_initial + af(rho) * (
        c_bound * (1 + 2 * omega_bound * p_bound)
        + b_bound * p_bound * p_bound
    )
    if p_rhs_bound.upper() >= p_bound.lower():
        metadata["failure"] = "RECIPROCAL_REFERENCE_P_MAJORANT_SELF_MAP"
        return None, metadata

    omega_lower = omega.abs_lower()
    cocycle_bound = 1 / (5 * omega_lower) * (
        2 * omega_bound**2 / r_lower**2
        + (12 + omega_bound**2) / r_lower**3
        + (6 * omega_bound**2 + 24) / r_lower**4
    )
    linear = af(rho) * (
        2 * omega_bound * c_bound + 2 * b_bound * p_bound
    )
    if linear.upper() >= 1:
        metadata["failure"] = "RECIPROCAL_REFERENCE_SENSITIVITY_LINEAR"
        return None, metadata
    eta_bound = strict_candidate((
        eta0.abs_upper()
        + af(rho) * c_bound * cocycle_bound * p_bound**2
    ) / (1 - linear))
    xi_bound = strict_candidate((
        xi0.abs_upper() + af(rho) * 2 * c_bound * p_bound
    ) / (1 - linear))

    values = []
    ratio = af(abs(step)) / af(rho)
    for series, bound in (
        (p_series, p_bound),
        (eta_series, eta_bound),
        (xi_series, xi_bound),
    ):
        value = acb(0)
        power = arb(1)
        for coefficient in series:
            value += coefficient * power
            power *= af(step)
        tail = bound * ratio**order / (1 - ratio)
        values.append(inflate(value, tail))
    metadata["reference_tail_upper"] = [
        str((bound * ratio**order / (1 - ratio)).upper())
        for bound in (p_bound, eta_bound, xi_bound)
    ]
    return tuple(values), metadata


def p_remainder_step(
    dp: arb,
    de: arb,
    dx: arb,
    r0: Fraction,
    step: Fraction,
    delta: arb,
    omega_center: acb,
    p0: acb,
    p1: acb,
    eta0: acb,
    eta1: acb,
    xi0: acb,
    xi1: acb,
    omega_lower: Fraction,
) -> tuple[tuple | None, str | None]:
    """Absolute panel remainder bound in the reciprocal chart."""
    h = af(step)
    rr = af(r0)
    c_bound = rr / (rr - 2)
    b_bound = 6 * (rr - 1) / rr**3
    p_ref = max(p0.abs_upper(), p1.abs_upper())
    eta_ref = max(eta0.abs_upper(), eta1.abs_upper())
    xi_ref = max(xi0.abs_upper(), xi1.abs_upper())
    omega_abs = omega_center.abs_upper()
    # Scalar logarithmic norm of the reference linearization
    # 2*i*omega*c-2*b*p.  Keeping its real part avoids the catastrophic
    # wrapping produced by an absolute-value Lipschitz constant.
    mu = (
        -2 * c_bound * omega_center.imag.lower()
        - 2 * b_bound * min(p0.real.lower(), p1.real.lower())
    )
    linear_p = mu + 2 * c_bound * delta
    forcing_p = 2 * c_bound * delta * p_ref
    qa = h * b_bound
    qb = h * linear_p - 1
    qc = dp + h * forcing_p
    discriminant = qb * qb - 4 * qa * qc
    if discriminant.lower() <= 0:
        return None, "RECIPROCAL_P_REMAINDER_DISCRIMINANT"
    proposed = (
        -float(qb.mid()) - math.sqrt(float(discriminant.lower()))
    ) / (2 * float(qa.lower()))
    bp = arb(proposed * 1.000001)
    if (
        dp + h * (linear_p * bp + b_bound * bp * bp + forcing_p)
    ).upper() >= bp.lower():
        return None, "RECIPROCAL_P_REMAINDER_SELF_MAP"

    omega_min = af(omega_lower)
    i_bound = 1 / (5 * omega_min) * (
        2 * (omega_abs + delta) ** 2 / rr**2
        + (12 + (omega_abs + delta) ** 2) / rr**3
        + (6 * (omega_abs + delta) ** 2 + 24) / rr**4
    )
    i_lipschitz = delta / 5 * (
        2 / rr**2 + 1 / rr**3 + 6 / rr**4
        + (12 / rr**3 + 24 / rr**4) / omega_min**2
    )
    p_total = p_ref + bp
    sensitivity_linear = mu + 2 * c_bound * delta + 2 * b_bound * bp
    denominator = 1 - h * sensitivity_linear
    if denominator.lower() <= 0:
        return None, "RECIPROCAL_SENSITIVITY_REMAINDER_LINEAR"
    coefficient_error = 2 * c_bound * delta + 2 * b_bound * bp
    eta_forcing = (
        coefficient_error * eta_ref
        + c_bound * (
            i_lipschitz * p_total**2
            + i_bound * bp * (2 * p_ref + bp)
        )
    )
    xi_forcing = coefficient_error * xi_ref + 2 * c_bound * bp
    be = strict_candidate((de + h * eta_forcing) / denominator)
    bx = strict_candidate((dx + h * xi_forcing) / denominator)
    return (bp, be, bx), None


def reciprocal_continue(obstruction: dict) -> dict:
    """Certify q!=0 on the full panel, switch, and continue to r=4."""
    q_full = inflate(obstruction["q_center"], obstruction["q_radius"])
    e_full = inflate(obstruction["e_center"], obstruction["e_radius"])
    x_full = inflate(obstruction["x_center"], obstruction["x_radius"])
    q_modulus_lower = q_full.abs_lower()
    switch = {
        "q_full": str(q_full),
        "q_modulus_lower": str(q_modulus_lower),
        "denominator_excludes_zero": q_modulus_lower > 0,
        "derivative_rule": (
            "p=1/q; p_tau=E/q^2 and p_omega=X/q^2 "
            "for predecessor variables E=-q_tau, X=-q_omega"
        ),
    }
    if q_modulus_lower <= 0:
        return {
            "switch": switch,
            "reached_r4": False,
            "terminal": {
                "radius": str(obstruction["radius"]),
                "failure": "RECIPROCAL_DENOMINATOR_CONTAINS_ZERO",
            },
        }
    p_full = 1 / q_full
    eta_full = e_full / (q_full * q_full)
    xi_full = x_full / (q_full * q_full)
    p_center = midpoint(p_full)
    eta_center = midpoint(eta_full)
    xi_center = midpoint(xi_full)
    dp = radius_from(p_full, p_center)
    de = radius_from(eta_full, eta_center)
    dx = radius_from(xi_full, xi_center)
    switch.update({
        "p_center": str(p_center),
        "p_radius": str(dp.upper()),
        "p_tau_center": str(eta_center),
        "p_tau_radius": str(de.upper()),
        "p_omega_center": str(xi_center),
        "p_omega_radius": str(dx.upper()),
    })

    r = obstruction["radius"]
    steps = 0
    rejected = 0
    minimum_step = Fraction(1, 2**20)
    while r < 4:
        step = min(Fraction(1, 100), Fraction(4) - r)
        while True:
            reference, metadata = p_reference_step(
                r, step, p_center, eta_center, xi_center,
                obstruction["omega_center"],
            )
            if reference is not None:
                p1, eta1, xi1 = (midpoint(value) for value in reference)
                remainder, failure = p_remainder_step(
                    dp, de, dx, r, step, obstruction["omega_radius"],
                    obstruction["omega_center"], p_center, p1,
                    eta_center, eta1, xi_center, xi1,
                    Fraction(json.loads(ECS.read_text())["disk"]["omega_modulus_lower"]),
                )
            else:
                failure = metadata["failure"]
                remainder = None
            if remainder is not None:
                break
            rejected += 1
            step /= 2
            if step < minimum_step:
                return {
                    "switch": switch,
                    "reached_r4": False,
                    "accepted_steps": steps,
                    "rejected_trials": rejected,
                    "terminal": {
                        "radius": str(r),
                        "failure": failure,
                        "attempted_step": str(step * 2),
                        "p_center": str(p_center),
                        "p_radius": str(dp.upper()),
                        "p_modulus_lower": str(
                            inflate(p_center, dp).abs_lower()
                        ),
                        "p_tau_radius": str(de.upper()),
                        "p_omega_radius": str(dx.upper()),
                    },
                }
        dp, de, dx = remainder
        dp += radius_from(reference[0], p1)
        de += radius_from(reference[1], eta1)
        dx += radius_from(reference[2], xi1)
        p_center, eta_center, xi_center = p1, eta1, xi1
        r += step
        steps += 1
    return {
        "switch": switch,
        "reached_r4": True,
        "accepted_steps": steps,
        "rejected_trials": rejected,
        "terminal": None,
        "checkpoint_r4": {
            "p_center": str(p_center),
            "p_radius": str(dp.upper()),
            "p_tau_center": str(eta_center),
            "p_tau_radius": str(de.upper()),
            "p_omega_center": str(xi_center),
            "p_omega_radius": str(dx.upper()),
        },
    }


def compute() -> dict:
    ctx.prec = 128
    rows = []
    for panel in range(16):
        obstruction = first_obstruction(panel)
        continuation = reciprocal_continue(obstruction)
        rows.append({
            "panel": panel,
            "first_obstruction": {
                "radius": str(obstruction["radius"]),
                "failure": obstruction["failure"],
                "predecessor_steps": obstruction["steps"],
                "q_center": str(obstruction["q_center"]),
                "q_radius": str(obstruction["q_radius"].upper()),
            },
            **continuation,
        })
    return {
        "schema": "phase3-axial-qnm-horizon-reciprocal-chart-run-v1",
        "panel_count": 16,
        "target_radius": "4",
        "chart": "p=1/q",
        "rows": rows,
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
