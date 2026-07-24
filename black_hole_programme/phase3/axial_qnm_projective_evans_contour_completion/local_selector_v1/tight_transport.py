#!/usr/bin/env python3
"""High-order projective transport with cancellation-safe remainder roots.

The earlier boundary rail deliberately used a conservative quadratic-root
formula.  At high Taylor order its remainder radii become so small that the
subtraction in that formula loses the strict self-map margin in binary64.
This module uses a larger, cancellation-free candidate and verifies the same
self-map inequalities afterward.  No inequality is accepted by construction.
"""
from __future__ import annotations

import json
from fractions import Fraction
from unittest.mock import patch

from flint import acb, arb

import black_hole_programme.phase3.axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer as ci
import black_hole_programme.phase3.axial_qnm_horizon_projective_preflight_v1.horizon_preflight as hp
from ...axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    midpoint,
    radius_from,
    reference_step,
    strict_candidate,
)
from ...axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    ECS,
    af,
    inflate,
)

MATCH_RADIUS = Fraction(32)
DEFAULT_ORDER = 48


def omega_lower() -> Fraction:
    """Certified lower bound for |omega| on the parent spectral disk."""
    return Fraction(json.loads(ECS.read_text())["disk"]["omega_modulus_lower"])


def _strict_small_root(
    qa: arb,
    qb: arb,
    qc: arb,
    discriminant: arb,
) -> arb | None:
    """Return the small quadratic root without subtractive cancellation."""
    denominator = -qb + discriminant.sqrt()
    if qa.lower() <= 0 or denominator.lower() <= 0:
        return None
    return strict_candidate(2 * qc / denominator, multiplier=1.01)


def backward_remainder(
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
) -> tuple[tuple[arb, arb, arb] | None, str | None]:
    """Validated remainder step for backward (infinity-to-match) transport."""
    h = af(abs(step))
    r_lower = af(r0 + step)
    c_bound = r_lower / (r_lower - 2)
    q_reference = max(q0.abs_upper(), q1.abs_upper())
    eta_reference = max(eta0.abs_upper(), eta1.abs_upper())
    xi_reference = max(xi0.abs_upper(), xi1.abs_upper())
    q_real_upper = max(q0.real.upper(), q1.real.upper())
    mu = c_bound * (
        2 * omega_center.imag.upper() + 2 * q_real_upper
    )
    linear_q = mu + 2 * c_bound * omega_radius
    forcing_q = 2 * c_bound * omega_radius * q_reference
    qa = h * c_bound
    qb = h * linear_q - 1
    qc = q_radius + h * forcing_q
    discriminant = qb * qb - 4 * qa * qc
    if discriminant.lower() <= 0:
        return None, "TIGHT_BACKWARD_Q_REMAINDER_DISCRIMINANT"
    q_bound = _strict_small_root(qa, qb, qc, discriminant)
    if q_bound is None:
        return None, "TIGHT_BACKWARD_Q_REMAINDER_LINEAR"
    q_rhs = q_radius + h * (
        linear_q * q_bound
        + c_bound * q_bound * q_bound
        + forcing_q
    )
    if q_rhs.upper() >= q_bound.lower():
        return None, "TIGHT_BACKWARD_Q_REMAINDER_SELF_MAP"

    omega_min = af(omega_lower())
    cocycle_lipschitz = omega_radius / 5 * (
        2 / r_lower**2
        + (12 / omega_min**2 + 1) / r_lower**3
        + (6 + 24 / omega_min**2) / r_lower**4
    )
    sensitivity_linear = (
        mu + 2 * c_bound * omega_radius + 2 * c_bound * q_bound
    )
    denominator = 1 - h * sensitivity_linear
    if denominator.lower() <= 0:
        return None, "TIGHT_BACKWARD_SENSITIVITY_REMAINDER_LINEAR"
    eta_raw = (
        eta_radius + h * (
            2 * c_bound * (omega_radius + q_bound) * eta_reference
            + c_bound * cocycle_lipschitz
        )
    ) / denominator
    eta_bound = strict_candidate(eta_raw, multiplier=1.01)
    eta_rhs = eta_radius + h * (
        sensitivity_linear * eta_bound
        + 2 * c_bound * (omega_radius + q_bound) * eta_reference
        + c_bound * cocycle_lipschitz
    )
    if eta_rhs.upper() >= eta_bound.lower():
        return None, "TIGHT_BACKWARD_ETA_REMAINDER_SELF_MAP"
    xi_raw = (
        xi_radius + h * (
            2 * c_bound * (omega_radius + q_bound) * xi_reference
            + 2 * c_bound * q_bound
        )
    ) / denominator
    xi_bound = strict_candidate(xi_raw, multiplier=1.01)
    xi_rhs = xi_radius + h * (
        sensitivity_linear * xi_bound
        + 2 * c_bound * (omega_radius + q_bound) * xi_reference
        + 2 * c_bound * q_bound
    )
    if xi_rhs.upper() >= xi_bound.lower():
        return None, "TIGHT_BACKWARD_XI_REMAINDER_SELF_MAP"
    return (q_bound, eta_bound, xi_bound), None


def forward_remainder(
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
) -> tuple[tuple[arb, arb, arb] | None, str | None]:
    """Validated remainder step for forward (horizon-to-match) transport."""
    h = af(step)
    c_bound = af(r0) / af(r0 - 2)
    q_reference = max(q0.abs_upper(), q1.abs_upper())
    eta_reference = max(eta0.abs_upper(), eta1.abs_upper())
    xi_reference = max(xi0.abs_upper(), xi1.abs_upper())
    mu = c_bound * (
        2 * omega_center.imag.upper()
        - 2 * min(q0.real.lower(), q1.real.lower())
    )
    linear_q = mu + 2 * c_bound * omega_radius
    forcing_q = 2 * c_bound * omega_radius * q_reference
    qa = h * c_bound
    qb = h * linear_q - 1
    qc = q_radius + h * forcing_q
    discriminant = qb * qb - 4 * qa * qc
    if discriminant.lower() <= 0:
        return None, "TIGHT_FORWARD_Q_REMAINDER_DISCRIMINANT"
    q_bound = _strict_small_root(qa, qb, qc, discriminant)
    if q_bound is None:
        return None, "TIGHT_FORWARD_Q_REMAINDER_LINEAR"
    q_rhs = q_radius + h * (
        linear_q * q_bound
        + c_bound * q_bound * q_bound
        + forcing_q
    )
    if q_rhs.upper() >= q_bound.lower():
        return None, "TIGHT_FORWARD_Q_REMAINDER_SELF_MAP"

    r_lower = af(r0)
    omega_min = af(omega_lower())
    cocycle_lipschitz = omega_radius / 5 * (
        2 / r_lower**2
        + (12 / omega_min**2 + 1) / r_lower**3
        + (6 + 24 / omega_min**2) / r_lower**4
    )
    sensitivity_linear = (
        mu + 2 * c_bound * omega_radius + 2 * c_bound * q_bound
    )
    denominator = 1 - h * sensitivity_linear
    if denominator.lower() <= 0:
        return None, "TIGHT_FORWARD_SENSITIVITY_REMAINDER_LINEAR"
    eta_raw = (
        eta_radius + h * (
            2 * c_bound * (omega_radius + q_bound) * eta_reference
            + c_bound * cocycle_lipschitz
        )
    ) / denominator
    eta_bound = strict_candidate(eta_raw, multiplier=1.01)
    eta_rhs = eta_radius + h * (
        sensitivity_linear * eta_bound
        + 2 * c_bound * (omega_radius + q_bound) * eta_reference
        + c_bound * cocycle_lipschitz
    )
    if eta_rhs.upper() >= eta_bound.lower():
        return None, "TIGHT_FORWARD_ETA_REMAINDER_SELF_MAP"
    xi_raw = (
        xi_radius + h * (
            2 * c_bound * (omega_radius + q_bound) * xi_reference
            + 2 * c_bound * q_bound
        )
    ) / denominator
    xi_bound = strict_candidate(xi_raw, multiplier=1.01)
    xi_rhs = xi_radius + h * (
        sensitivity_linear * xi_bound
        + 2 * c_bound * (omega_radius + q_bound) * xi_reference
        + 2 * c_bound * q_bound
    )
    if xi_rhs.upper() >= xi_bound.lower():
        return None, "TIGHT_FORWARD_XI_REMAINDER_SELF_MAP"
    return (q_bound, eta_bound, xi_bound), None


def outgoing_transport(
    omega_box: acb,
    *,
    order: int = DEFAULT_ORDER,
) -> dict:
    """Certify outgoing q, q_tau and q_omega at the matching radius."""
    with patch.object(ci, "panel_box", return_value=omega_box):
        _, q_box, eta_box, xi_box = ci.certified_panel_state(0, 1)
    omega_center = midpoint(omega_box)
    omega_radius = radius_from(omega_box, omega_center)
    q_center = midpoint(q_box)
    eta_center = midpoint(eta_box)
    xi_center = midpoint(xi_box)
    q_radius = radius_from(q_box, q_center)
    eta_radius = radius_from(eta_box, eta_center)
    xi_radius = radius_from(xi_box, xi_center)
    r = Fraction(45)
    accepted_steps = 0
    rejected_trials = 0
    while r > MATCH_RADIUS:
        step = max(Fraction(-1, 20), MATCH_RADIUS - r)
        while True:
            reference, metadata = reference_step(
                r, step, q_center, eta_center, xi_center, omega_center,
                order=order,
            )
            if reference is not None:
                q1, eta1, xi1 = (midpoint(value) for value in reference)
                remainder, failure = backward_remainder(
                    q_radius=q_radius,
                    eta_radius=eta_radius,
                    xi_radius=xi_radius,
                    r0=r,
                    step=step,
                    omega_radius=omega_radius,
                    omega_center=omega_center,
                    q0=q_center,
                    q1=q1,
                    eta0=eta_center,
                    eta1=eta1,
                    xi0=xi_center,
                    xi1=xi1,
                )
            else:
                remainder = None
                failure = metadata["failure"]
            if remainder is not None:
                break
            rejected_trials += 1
            step /= 2
            if abs(step) < Fraction(1, 10240):
                return {
                    "passed": False,
                    "radius": str(r),
                    "failure": failure,
                }
        q_radius, eta_radius, xi_radius = remainder
        q_radius += radius_from(reference[0], q1)
        eta_radius += radius_from(reference[1], eta1)
        xi_radius += radius_from(reference[2], xi1)
        q_center, eta_center, xi_center = q1, eta1, xi1
        r += step
        accepted_steps += 1
    return {
        "passed": True,
        "q": inflate(q_center, q_radius),
        "q_tau": inflate(eta_center, eta_radius),
        "q_omega": inflate(xi_center, xi_radius),
        "accepted_steps": accepted_steps,
        "rejected_trials": rejected_trials,
        "order": order,
    }


def horizon_transport(
    omega_box: acb,
    *,
    order: int = DEFAULT_ORDER,
) -> dict:
    """Certify horizon q, q_tau and q_omega at the matching radius."""
    with patch.object(hp, "panel_box", return_value=omega_box):
        _, q_box, eta_box, xi_box, *_ = hp.horizon_seed(0)
    omega_center = midpoint(omega_box)
    omega_radius = radius_from(omega_box, omega_center)
    q_center = midpoint(q_box)
    eta_center = midpoint(-eta_box)
    xi_center = midpoint(-xi_box)
    q_radius = radius_from(q_box, q_center)
    eta_radius = radius_from(-eta_box, eta_center)
    xi_radius = radius_from(-xi_box, xi_center)
    r = Fraction(2) + Fraction(1, 2**22)
    accepted_steps = 0
    rejected_trials = 0
    while r < MATCH_RADIUS:
        step = min(
            (r - 2) / 16,
            Fraction(1, 100) if r < 4 else Fraction(1, 20),
            MATCH_RADIUS - r,
        )
        while True:
            reference, metadata = reference_step(
                r, step, q_center, eta_center, xi_center, -omega_center,
                order=order,
            )
            if reference is not None:
                q1, eta1, xi1 = (midpoint(value) for value in reference)
                remainder, failure = forward_remainder(
                    q_radius=q_radius,
                    eta_radius=eta_radius,
                    xi_radius=xi_radius,
                    r0=r,
                    step=step,
                    omega_radius=omega_radius,
                    omega_center=omega_center,
                    q0=q_center,
                    q1=q1,
                    eta0=eta_center,
                    eta1=eta1,
                    xi0=xi_center,
                    xi1=xi1,
                )
            else:
                remainder = None
                failure = metadata["failure"]
            if remainder is not None:
                break
            rejected_trials += 1
            step /= 2
            if step < (r - 2) / 2**40:
                return {
                    "passed": False,
                    "radius": str(r),
                    "failure": failure,
                }
        q_radius, eta_radius, xi_radius = remainder
        q_radius += radius_from(reference[0], q1)
        eta_radius += radius_from(reference[1], eta1)
        xi_radius += radius_from(reference[2], xi1)
        q_center, eta_center, xi_center = q1, eta1, xi1
        r += step
        accepted_steps += 1
    return {
        "passed": True,
        "q": inflate(q_center, q_radius),
        "q_tau": inflate(-eta_center, eta_radius),
        "q_omega": inflate(-xi_center, xi_radius),
        "accepted_steps": accepted_steps,
        "rejected_trials": rejected_trials,
        "order": order,
    }
