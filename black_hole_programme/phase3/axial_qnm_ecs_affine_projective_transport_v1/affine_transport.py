#!/usr/bin/env python3
"""Midpoint reference transport plus logarithmic-norm remainder bounds."""
from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

from ..axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    ECS,
    TAIL,
    af,
    certified_panel_state,
    inflate,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "affine-run.json"


def midpoint(value: acb) -> acb:
    # A binary64 midpoint is merely a chosen singleton reference.  The
    # difference from the certified ball is retained in the remainder.
    return acb(float(value.real.mid()), float(value.imag.mid()))


def radius_from(value: acb, center: acb) -> arb:
    return (value - center).abs_upper()


def taylor_coefficients(r0: Fraction, order: int,
                        omega: acb) -> tuple[list, list, list]:
    rr = af(r0)
    distance = af(r0 - 2)
    c_coefficients = []
    b_coefficients = []
    i_coefficients = []
    for k in range(order):
        c_coefficient = (
            arb(1) + arb(2) / distance
            if k == 0
            else arb(2) * ((-1) ** k) / distance ** (k + 1)
        )
        b_coefficient = arb(6) * ((-1) ** k) * (
            arb(k + 1) / rr ** (k + 2)
            - arb((k + 1) * (k + 2)) / 2 / rr ** (k + 3)
        )

        def inverse_power(power: int) -> arb:
            return (
                ((-1) ** k)
                * math.comb(power + k - 1, k)
                / rr ** (power + k)
            )

        cocycle = 1j / (5 * omega) * (
            2 * omega * omega * inverse_power(2)
            + (12 - omega * omega) * inverse_power(3)
            - (6 * omega * omega + 24) * inverse_power(4)
        )
        c_coefficients.append(acb(c_coefficient))
        b_coefficients.append(acb(b_coefficient))
        i_coefficients.append(acb(cocycle))
    return c_coefficients, b_coefficients, i_coefficients


def convolution(left: list, right: list, n: int) -> acb:
    return sum(
        (left[k] * right[n - k] for k in range(n + 1)),
        acb(0),
    )


def strict_candidate(raw_upper: arb, multiplier: float = 1.000001) -> arb:
    return arb(float(raw_upper.upper()) * multiplier)


def reference_step(r0: Fraction, step: Fraction, q0: acb, eta0: acb,
                   xi0: acb, omega: acb,
                   order: int = 14) -> tuple[tuple | None, dict]:
    c_coefficients, b_coefficients, i_coefficients = taylor_coefficients(
        r0, order, omega
    )
    q_series = [q0]
    eta_series = [eta0]
    xi_series = [xi0]
    for n in range(order - 1):
        q_rhs = acb(0)
        eta_rhs = acb(0)
        xi_rhs = acb(0)
        for k in range(n + 1):
            q_rhs += c_coefficients[k] * (
                2j * omega * q_series[n - k]
                - convolution(q_series, q_series, n - k)
            )
            eta_rhs += c_coefficients[k] * (
                2j * omega * eta_series[n - k]
                - 2 * convolution(q_series, eta_series, n - k)
                - i_coefficients[n - k]
            )
            xi_rhs += c_coefficients[k] * (
                2j * omega * xi_series[n - k]
                - 2 * convolution(q_series, xi_series, n - k)
                + 2j * q_series[n - k]
            )
        q_rhs += b_coefficients[n]
        q_series.append(q_rhs / (n + 1))
        eta_series.append(eta_rhs / (n + 1))
        xi_series.append(xi_rhs / (n + 1))

    rho = 2 * abs(step)
    r_lower = af(r0 - rho)
    c_bound = r_lower / (r_lower - 2)
    omega_bound = omega.abs_upper()
    q_initial = q0.abs_upper()
    qa = af(rho) * c_bound
    qb = af(rho) * 2 * omega_bound * c_bound - 1
    qc = q_initial + af(rho) * (
        arb(6) * (r_lower + 1) / r_lower**3
    )
    discriminant = qb * qb - 4 * qa * qc
    metadata = {"failure": None}
    if discriminant.lower() <= 0:
        metadata["failure"] = "REFERENCE_Q_MAJORANT_DISCRIMINANT"
        return None, metadata
    proposed = (
        -float(qb.mid()) - math.sqrt(float(discriminant.lower()))
    ) / (2 * float(qa.lower()))
    q_bound = arb(proposed * 1.000001)
    q_rhs_bound = q_initial + af(rho) * (
        2 * omega_bound * c_bound * q_bound
        + c_bound * q_bound * q_bound
        + arb(6) * (r_lower + 1) / r_lower**3
    )
    if q_rhs_bound.upper() >= q_bound.lower():
        metadata["failure"] = "REFERENCE_Q_MAJORANT_SELF_MAP"
        return None, metadata

    omega_lower = omega.abs_lower()
    cocycle_bound = 1 / (5 * omega_lower) * (
        2 * omega_bound**2 / r_lower**2
        + (12 + omega_bound**2) / r_lower**3
        + (6 * omega_bound**2 + 24) / r_lower**4
    )
    linear = af(rho) * c_bound * (
        2 * omega_bound + 2 * q_bound
    )
    if linear.upper() >= 1:
        metadata["failure"] = "REFERENCE_SENSITIVITY_MAJORANT_LINEAR"
        return None, metadata
    eta_raw = (
        eta0.abs_upper() + af(rho) * c_bound * cocycle_bound
    ) / (1 - linear)
    eta_bound = strict_candidate(eta_raw)
    eta_rhs_bound = eta0.abs_upper() + af(rho) * c_bound * (
        (2 * omega_bound + 2 * q_bound) * eta_bound
        + cocycle_bound
    )
    if eta_rhs_bound.upper() >= eta_bound.lower():
        metadata["failure"] = "REFERENCE_ETA_MAJORANT_SELF_MAP"
        return None, metadata
    xi_raw = (
        xi0.abs_upper() + af(rho) * c_bound * 2 * q_bound
    ) / (1 - linear)
    xi_bound = strict_candidate(xi_raw)
    xi_rhs_bound = xi0.abs_upper() + af(rho) * c_bound * (
        (2 * omega_bound + 2 * q_bound) * xi_bound + 2 * q_bound
    )
    if xi_rhs_bound.upper() >= xi_bound.lower():
        metadata["failure"] = "REFERENCE_XI_MAJORANT_SELF_MAP"
        return None, metadata

    values = []
    ratio = af(abs(step)) / af(rho)
    for series, bound in (
        (q_series, q_bound),
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
        for bound in (q_bound, eta_bound, xi_bound)
    ]
    return tuple(values), metadata


def remainder_step(
    *,
    q_radius: arb,
    eta_radius: arb,
    xi_radius: arb,
    r0: Fraction,
    step: Fraction,
    omega_radius: arb,
    omega_center: acb,
    q0: acb,
    q1: acb,
    eta0: acb,
    eta1: acb,
    xi0: acb,
    xi1: acb,
    omega_lower: Fraction,
) -> tuple[tuple | None, dict]:
    h = af(abs(step))
    r_lower = af(r0 + step)
    c_bound = r_lower / (r_lower - 2)
    q_reference = max(q0.abs_upper(), q1.abs_upper())
    eta_reference = max(eta0.abs_upper(), eta1.abs_upper())
    xi_reference = max(xi0.abs_upper(), xi1.abs_upper())
    q_real_upper = max(q0.real.upper(), q1.real.upper())
    # For backward radial transport the scalar logarithmic norm of
    # -c*(2*i*omega-2*q) is c*(2*Im(omega)+2*Re(q)).
    mu = c_bound * (
        2 * omega_center.imag.upper() + 2 * q_real_upper
    )
    linear_q = mu + 2 * c_bound * omega_radius
    forcing_q = 2 * c_bound * omega_radius * q_reference
    qa = h * c_bound
    qb = h * linear_q - 1
    qc = q_radius + h * forcing_q
    discriminant = qb * qb - 4 * qa * qc
    metadata = {
        "failure": None,
        "logarithmic_norm_upper": str(mu.upper()),
    }
    if discriminant.lower() <= 0:
        metadata["failure"] = "AFFINE_Q_REMAINDER_DISCRIMINANT"
        return None, metadata
    proposed = (
        -float(qb.mid()) - math.sqrt(float(discriminant.lower()))
    ) / (2 * float(qa.lower()))
    q_bound = arb(proposed * 1.000001)
    q_rhs = q_radius + h * (
        linear_q * q_bound
        + c_bound * q_bound * q_bound
        + forcing_q
    )
    if q_rhs.upper() >= q_bound.lower():
        metadata["failure"] = "AFFINE_Q_REMAINDER_SELF_MAP"
        return None, metadata

    omega_min = af(omega_lower)
    cocycle_lipschitz = omega_radius / 5 * (
        2 / r_lower**2
        + (12 / omega_min**2 + 1) / r_lower**3
        + (6 + 24 / omega_min**2) / r_lower**4
    )
    sensitivity_linear = (
        mu + 2 * c_bound * omega_radius
        + 2 * c_bound * q_bound
    )
    denominator = 1 - h * sensitivity_linear
    if denominator.lower() <= 0:
        metadata["failure"] = "AFFINE_SENSITIVITY_REMAINDER_LINEAR"
        return None, metadata
    eta_raw = (
        eta_radius + h * (
            2 * c_bound * (omega_radius + q_bound) * eta_reference
            + c_bound * cocycle_lipschitz
        )
    ) / denominator
    eta_bound = strict_candidate(eta_raw)
    eta_rhs = eta_radius + h * (
        sensitivity_linear * eta_bound
        + 2 * c_bound * (omega_radius + q_bound) * eta_reference
        + c_bound * cocycle_lipschitz
    )
    if eta_rhs.upper() >= eta_bound.lower():
        metadata["failure"] = "AFFINE_ETA_REMAINDER_SELF_MAP"
        return None, metadata
    xi_raw = (
        xi_radius + h * (
            2 * c_bound * (omega_radius + q_bound) * xi_reference
            + 2 * c_bound * q_bound
        )
    ) / denominator
    xi_bound = strict_candidate(xi_raw)
    xi_rhs = xi_radius + h * (
        sensitivity_linear * xi_bound
        + 2 * c_bound * (omega_radius + q_bound) * xi_reference
        + 2 * c_bound * q_bound
    )
    if xi_rhs.upper() >= xi_bound.lower():
        metadata["failure"] = "AFFINE_XI_REMAINDER_SELF_MAP"
        return None, metadata
    return (q_bound, eta_bound, xi_bound), metadata


def compute(panel_count: int = 16, match_radius: int = 32) -> dict:
    ctx.prec = 128
    ecs = json.loads(ECS.read_text())
    omega_lower = Fraction(ecs["disk"]["omega_modulus_lower"])
    rows = []
    for panel in range(panel_count):
        omega_box, q_box, eta_box, xi_box = certified_panel_state(
            panel, panel_count
        )
        omega_center = midpoint(omega_box)
        omega_radius = radius_from(omega_box, omega_center)
        q_center = midpoint(q_box)
        eta_center = midpoint(eta_box)
        xi_center = midpoint(xi_box)
        q_radius = radius_from(q_box, q_center)
        eta_radius = radius_from(eta_box, eta_center)
        xi_radius = radius_from(xi_box, xi_center)
        r = Fraction(45)
        target_passed = True
        target_snapshot = None
        terminal = None
        successful_steps = 0
        while r > 4:
            step = max(Fraction(-1, 20), Fraction(4) - r)
            reference, reference_metadata = reference_step(
                r, step, q_center, eta_center, xi_center, omega_center
            )
            if reference is None:
                terminal = {
                    "radius": str(r),
                    "stage": "reference",
                    **reference_metadata,
                }
                break
            q_ball, eta_ball, xi_ball = reference
            q_next = midpoint(q_ball)
            eta_next = midpoint(eta_ball)
            xi_next = midpoint(xi_ball)
            remainder, remainder_metadata = remainder_step(
                q_radius=q_radius,
                eta_radius=eta_radius,
                xi_radius=xi_radius,
                r0=r,
                step=step,
                omega_radius=omega_radius,
                omega_center=omega_center,
                q0=q_center,
                q1=q_next,
                eta0=eta_center,
                eta1=eta_next,
                xi0=xi_center,
                xi1=xi_next,
                omega_lower=omega_lower,
            )
            if remainder is None:
                terminal = {
                    "radius": str(r),
                    "stage": "remainder",
                    "q_radius": str(q_radius.upper()),
                    "eta_radius": str(eta_radius.upper()),
                    "xi_radius": str(xi_radius.upper()),
                    **remainder_metadata,
                }
                if r > match_radius:
                    target_passed = False
                break
            q_radius, eta_radius, xi_radius = remainder
            q_radius += radius_from(q_ball, q_next)
            eta_radius += radius_from(eta_ball, eta_next)
            xi_radius += radius_from(xi_ball, xi_next)
            q_center, eta_center, xi_center = q_next, eta_next, xi_next
            r += step
            successful_steps += 1
            if r == match_radius:
                target_snapshot = {
                    "radius": str(r),
                    "q_center": str(q_center),
                    "eta_center": str(eta_center),
                    "xi_center": str(xi_center),
                    "q_remainder_radius": str(q_radius.upper()),
                    "eta_remainder_radius": str(eta_radius.upper()),
                    "xi_remainder_radius": str(xi_radius.upper()),
                }
        rows.append({
            "panel": panel,
            "omega_box": str(omega_box),
            "omega_center": str(omega_center),
            "omega_remainder_radius": str(omega_radius.upper()),
            "successful_steps": successful_steps,
            "match_radius": match_radius,
            "match_radius_certified": target_passed and target_snapshot is not None,
            "match_snapshot": target_snapshot,
            "first_terminal_obstruction": terminal,
        })
    return {
        "schema": "phase3-axial-qnm-ecs-affine-projective-run-v1",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "representation": (
            "midpoint reference Taylor series plus zero-centered shared-omega "
            "remainder controlled by backward logarithmic norms"
        ),
        "panel_count": panel_count,
        "match_radius": match_radius,
        "radial_step": "-1/20",
        "rows": rows,
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
