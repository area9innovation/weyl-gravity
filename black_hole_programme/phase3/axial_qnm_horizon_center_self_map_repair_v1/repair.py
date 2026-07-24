#!/usr/bin/env python3
"""Diagnose and repair the panel-77 horizon-center quadratic self-map."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

from flint import acb, arb, ctx

import black_hole_programme.phase3.axial_qnm_common_affine_evans_boundary_v1.common_affine as ca
import black_hole_programme.phase3.axial_qnm_horizon_projective_preflight_v1.horizon_preflight as hp
from ..axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    midpoint,
    radius_from,
    reference_step,
)

HERE = Path(__file__).resolve().parent
RUN = HERE / "repair-run.json"
PANEL = 77
PANEL_COUNT = 512
SEED_RADIUS = Fraction(2) + Fraction(1, 2**22)
FIRST_STEP = Fraction(1, 2**26)
STRICT_NUMERATOR = 1000001
STRICT_DENOMINATOR = 1000000


def strict_upper(value: arb) -> arb:
    """Outward candidate using an exact rational enlargement."""
    return (
        arb(value.upper()) * arb(STRICT_NUMERATOR) / STRICT_DENOMINATOR
    )


def seed_from_omega(omega: acb, order: int = 16) -> dict:
    """Reissue the centered Frobenius seed with a declared tail order."""
    base, tau, frequency = hp.frobenius(omega, order=order)
    rho = ca.af(Fraction(1, 2**22))
    majorant = arb(10**6)
    growth = arb(100)
    ratio = growth * rho
    value_tail = majorant * ratio**order / (1 - ratio)
    derivative_tail = (
        majorant * growth * order * ratio ** (order - 1)
        / (1 - ratio) ** 2
    )

    def evaluate(coefficients: list) -> tuple[acb, acb]:
        value = acb(0)
        derivative = acb(0)
        for n, coefficient in enumerate(coefficients):
            value += coefficient * rho**n
            if n:
                derivative += n * coefficient * rho ** (n - 1)
        return ca.inflate(value, value_tail), ca.inflate(
            derivative, derivative_tail
        )

    p, p_r = evaluate(base)
    p_tau, p_tau_r = evaluate(tau)
    p_omega, p_omega_r = evaluate(frequency)
    lapse = rho / (2 + rho)
    p_x = lapse * p_r
    p_tau_x = lapse * p_tau_r
    p_omega_x = lapse * p_omega_r
    q = p_x / p
    eta = (p_tau_x * p - p_x * p_tau) / (p * p)
    xi = (p_omega_x * p - p_x * p_omega) / (p * p)
    coefficient_gate = all(
        coefficient.abs_upper() <= majorant * growth**n
        for sequence in (base, tau, frequency)
        for n, coefficient in enumerate(sequence)
    )
    return {
        "q": q,
        "eta": eta,
        "xi": xi,
        "coefficient_majorant_gate": coefficient_gate,
        "frobenius_order": order,
        "value_tail_upper": value_tail.upper(),
        "derivative_tail_upper": derivative_tail.upper(),
    }


def first_step_audit(
    omega: acb,
    *,
    precision: int,
    seed_order: int,
    taylor_order: int,
    root_method: str,
    label: str,
) -> dict:
    """Audit the first direct-q remainder self-map without relaxing it."""
    old_precision = ctx.prec
    ctx.prec = precision
    try:
        seed = seed_from_omega(omega, order=seed_order)
        omega_center = midpoint(omega)
        omega_radius = radius_from(omega, omega_center)
        q_center = midpoint(seed["q"])
        eta_center = midpoint(-seed["eta"])
        xi_center = midpoint(-seed["xi"])
        dq = radius_from(seed["q"], q_center)
        de = radius_from(-seed["eta"], eta_center)
        dx = radius_from(-seed["xi"], xi_center)
        reference, metadata = reference_step(
            SEED_RADIUS,
            FIRST_STEP,
            q_center,
            eta_center,
            xi_center,
            -omega_center,
            order=taylor_order,
        )
        result = {
            "label": label,
            "precision_bits": precision,
            "frobenius_order": seed_order,
            "taylor_order": taylor_order,
            "root_method": root_method,
            "coefficient_majorant_gate": seed[
                "coefficient_majorant_gate"
            ],
            "seed": {
                "q_center": str(q_center),
                "eta_center": str(eta_center),
                "xi_center": str(xi_center),
                "q_radius": str(dq.upper()),
                "eta_radius": str(de.upper()),
                "xi_radius": str(dx.upper()),
                "omega_radius": str(omega_radius.upper()),
                "value_tail_upper": str(seed["value_tail_upper"]),
                "derivative_tail_upper": str(
                    seed["derivative_tail_upper"]
                ),
            },
            "reference_passed": reference is not None,
        }
        if reference is None:
            result.update({
                "self_map_passed": False,
                "failure": metadata["failure"],
            })
            return result
        q1, eta1, xi1 = (midpoint(value) for value in reference)
        h = ca.af(FIRST_STEP)
        c_bound = ca.af(SEED_RADIUS) / ca.af(SEED_RADIUS - 2)
        q_ref = max(q_center.abs_upper(), q1.abs_upper())
        mu = c_bound * (
            2 * omega_center.imag.upper()
            - 2 * min(q_center.real.lower(), q1.real.lower())
        )
        linear = mu + 2 * c_bound * omega_radius
        forcing = 2 * c_bound * omega_radius * q_ref
        qa = h * c_bound
        qb = h * linear - 1
        qc = dq + h * forcing
        discriminant = qb * qb - 4 * qa * qc
        result["quadratic"] = {
            "qa": str(qa),
            "qb": str(qb),
            "qc": str(qc),
            "discriminant": str(discriminant),
        }
        if discriminant.lower() <= 0:
            result.update({
                "self_map_passed": False,
                "failure": "HORIZON_Q_REMAINDER_DISCRIMINANT",
            })
            return result
        if root_method == "subtractive_binary64":
            proposed = (
                -float(qb.mid()) - float(discriminant.lower()) ** 0.5
            ) / (2 * float(qa.lower()))
            candidate = arb(proposed * 1.000001)
            raw_root = str(proposed)
        elif root_method == "stable_interval":
            root = 2 * qc / (-qb + discriminant.sqrt())
            candidate = strict_upper(root)
            raw_root = str(root)
        else:
            raise ValueError(root_method)
        rhs = dq + h * (
            linear * candidate
            + c_bound * candidate * candidate
            + forcing
        )
        margin = candidate.lower() - rhs.upper()
        passed = margin > 0
        result.update({
            "candidate_raw_root": raw_root,
            "candidate": str(candidate),
            "self_map_rhs": str(rhs),
            "strict_margin": str(margin),
            "self_map_passed": passed,
            "failure": None if passed else "HORIZON_Q_REMAINDER_SELF_MAP",
        })
        return result
    finally:
        ctx.prec = old_precision


def stable_forward_remainder(
    dq: arb,
    de: arb,
    dx: arb,
    r0: Fraction,
    step: Fraction,
    delta: arb,
    omega: acb,
    q0: acb,
    q1: acb,
    e0: acb,
    e1: acb,
    x0: acb,
    x1: acb,
    omega_lower: Fraction,
) -> tuple[tuple | None, str | None]:
    """Original remainder theorem with a stable interval quadratic root."""
    h = ca.af(step)
    c_bound = ca.af(r0) / ca.af(r0 - 2)
    q_ref = max(q0.abs_upper(), q1.abs_upper())
    e_ref = max(e0.abs_upper(), e1.abs_upper())
    x_ref = max(x0.abs_upper(), x1.abs_upper())
    mu = c_bound * (
        2 * omega.imag.upper()
        - 2 * min(q0.real.lower(), q1.real.lower())
    )
    linear = mu + 2 * c_bound * delta
    forcing = 2 * c_bound * delta * q_ref
    qa = h * c_bound
    qb = h * linear - 1
    qc = dq + h * forcing
    discriminant = qb * qb - 4 * qa * qc
    if discriminant.lower() <= 0:
        return None, "HORIZON_Q_REMAINDER_DISCRIMINANT"
    smaller_root = 2 * qc / (-qb + discriminant.sqrt())
    bq = strict_upper(smaller_root)
    if (
        dq + h * (
            linear * bq + c_bound * bq * bq + forcing
        )
    ).upper() >= bq.lower():
        return None, "HORIZON_Q_REMAINDER_SELF_MAP"
    r_lower = ca.af(r0)
    omega_min = ca.af(omega_lower)
    cocycle_lipschitz = delta / 5 * (
        2 / r_lower**2
        + (12 / omega_min**2 + 1) / r_lower**3
        + (6 + 24 / omega_min**2) / r_lower**4
    )
    sensitivity_linear = (
        mu + 2 * c_bound * delta + 2 * c_bound * bq
    )
    denominator = 1 - h * sensitivity_linear
    if denominator.lower() <= 0:
        return None, "HORIZON_SENSITIVITY_REMAINDER_LINEAR"
    be = strict_upper((
        de + h * (
            2 * c_bound * (delta + bq) * e_ref
            + c_bound * cocycle_lipschitz
        )
    ) / denominator)
    bx = strict_upper((
        dx + h * (
            2 * c_bound * (delta + bq) * x_ref + 2 * c_bound * bq
        )
    ) / denominator)
    if (
        de + h * (
            sensitivity_linear * be
            + 2 * c_bound * (delta + bq) * e_ref
            + c_bound * cocycle_lipschitz
        )
    ).upper() >= be.lower():
        return None, "HORIZON_ETA_REMAINDER_SELF_MAP"
    if (
        dx + h * (
            sensitivity_linear * bx
            + 2 * c_bound * (delta + bq) * x_ref
            + 2 * c_bound * bq
        )
    ).upper() >= bx.lower():
        return None, "HORIZON_XI_REMAINDER_SELF_MAP"
    return (bq, be, bx), None


def reciprocal_pivot(omega: acb, label: str) -> dict:
    seed = seed_from_omega(omega)
    q_center = midpoint(seed["q"])
    q_radius = radius_from(seed["q"], q_center)
    q_full = ca.inflate(q_center, q_radius)
    lower = q_full.abs_lower()
    return {
        "label": label,
        "chart": "p=1/q",
        "q_full": str(q_full),
        "q_modulus_lower": str(lower),
        "pivot_excludes_zero": lower > 0,
        "transport_attempted": False,
        "reason": (
            "stable direct-q self-map already proves the full repaired "
            "transport; reciprocal chart retained as a certified alternative"
        ),
    }


def compute() -> dict:
    ctx.prec = 128
    omega_box, omega_center, _ = ca._panel_geometry(PANEL, PANEL_COUNT)
    singleton = acb(
        float(omega_center.real.mid()),
        float(omega_center.imag.mid()),
    )
    grid = [
        first_step_audit(
            omega_box,
            precision=128,
            seed_order=16,
            taylor_order=26,
            root_method="subtractive_binary64",
            label="box_baseline",
        ),
        first_step_audit(
            singleton,
            precision=128,
            seed_order=16,
            taylor_order=26,
            root_method="subtractive_binary64",
            label="center_baseline",
        ),
        first_step_audit(
            singleton,
            precision=256,
            seed_order=16,
            taylor_order=26,
            root_method="subtractive_binary64",
            label="center_higher_precision",
        ),
        first_step_audit(
            singleton,
            precision=128,
            seed_order=24,
            taylor_order=32,
            root_method="subtractive_binary64",
            label="center_higher_seed_and_taylor_order",
        ),
        first_step_audit(
            singleton,
            precision=128,
            seed_order=16,
            taylor_order=26,
            root_method="stable_interval",
            label="center_stable_interval_root",
        ),
    ]
    reciprocal = [
        reciprocal_pivot(omega_box, "box_reciprocal_pivot"),
        reciprocal_pivot(singleton, "center_reciprocal_pivot"),
    ]
    with patch.object(hp, "forward_remainder", stable_forward_remainder):
        panel = ca.compute_panel(PANEL, PANEL_COUNT)
    return {
        "schema": "phase3-axial-qnm-horizon-center-self-map-repair-run-v1",
        "panel": PANEL,
        "panel_count": PANEL_COUNT,
        "seed_radius": "2+2^-22",
        "first_step": str(FIRST_STEP),
        "diagnostic_grid": grid,
        "reciprocal_chart": reciprocal,
        "repair": {
            "method": (
                "stable smaller root 2*qc/(-qb+sqrt(discriminant)) "
                "with exact rational strict enlargement 1000001/1000000"
            ),
            "threshold_lowered": False,
            "strict_self_map_rechecked": True,
        },
        "repaired_panel": panel,
    }


if __name__ == "__main__":
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)
