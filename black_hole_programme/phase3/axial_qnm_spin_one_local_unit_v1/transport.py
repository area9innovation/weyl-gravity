#!/usr/bin/env python3
"""Validated spin-one projective transport on the local QNM disk.

The physical scalar is written as

    y = exp(-i*omega*x) v       at infinity,
    y = exp(+i*omega*x) P       at the future horizon.

For q=v_x/v (respectively P_x/P), both reduced lines use the same radial
Riccati equation after replacing omega by -omega for the horizon line.
Only the spin-one potential term differs from the already certified
spin-two rail:

    V_1 = 6 (r-2) / r^3,       (dr/dx)^(-1) V_1 = 6/r^2.

The implementation retains a singleton reference trajectory and a common
complex-ball parameter remainder.  Every proposed remainder radius is
checked against the strict self-map inequality that proves it.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from flint import acb, arb

from ..axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    midpoint,
    radius_from,
    strict_candidate,
)
from ..axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    af,
    apply_operator,
    evaluate,
    inflate,
    residual_bounds,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ECS = (
    ROOT
    / "black_hole_programme/phase3/"
    "axial_qnm_ecs_inverse_tortoise_v1/certificate.json"
)

MATCH_RADIUS = Fraction(32)
OUTER_RADIUS = Fraction(45)
HORIZON_RHO = Fraction(1, 2**22)
DEFAULT_ORDER = 48


def _ecs() -> dict:
    return json.loads(ECS.read_text())


def _spin_one_gate() -> dict:
    return next(
        row for row in _ecs()["volterra"]["channels"]
        if row["channel"] == "spin_one"
    )


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


def infinity_series(omega: acb, order: int) -> tuple[list, list, list, list]:
    """Reduced outgoing series in z=1/r for the spin-one RW potential."""
    aa = [0, 0, 1, -4, 4]
    bb = [2j * omega, 2 - 4j * omega, -10, 12]
    # -V_1/z^2 = -6 + 12 z.
    cc = [-6, 12]
    coefficients = [acb(1)]
    for n in range(order - 1):
        target = n + 1
        known = acb(0)
        pivot = acb(0)
        for j, value in enumerate(aa):
            k = n - j + 2
            if k >= 0:
                term = value * k * (k - 1)
                if k == target:
                    pivot += term
                elif k < len(coefficients):
                    known += term * coefficients[k]
        for j, value in enumerate(bb):
            k = n - j + 1
            if k >= 0:
                term = value * k
                if k == target:
                    pivot += term
                elif k < len(coefficients):
                    known += term * coefficients[k]
        for j, value in enumerate(cc):
            k = n - j
            if 0 <= k < len(coefficients):
                known += value * coefficients[k]
        coefficients.append(-known / pivot)
    return coefficients, aa, bb, cc


def infinity_seed(omega_box: acb, order: int = DEFAULT_ORDER) -> dict:
    """Certify the reduced outgoing spin-one logarithmic derivative at r=45."""
    ecs = _ecs()
    gate = _spin_one_gate()
    omega_lower = Fraction(ecs["disk"]["omega_modulus_lower"])
    kappa = Fraction(ecs["disk"]["phase_decay_rate_lower"])
    alpha = Fraction(gate["operator_norm_upper"])
    base, aa, bb, cc = infinity_series(omega_box, order)
    residual = apply_operator(base, aa, bb, cc)
    _, _, weighted, kernel = residual_bounds(
        residual,
        radius=int(OUTER_RADIUS),
        slope=Fraction(2, 3),
        kappa=kappa,
        omega_lower=omega_lower,
    )
    value_error = kernel / (1 - af(alpha))
    derivative_error = weighted / (1 - af(alpha))
    value_center, derivative_center = evaluate(base, int(OUTER_RADIUS))
    value = inflate(value_center, value_error)
    derivative = inflate(derivative_center, derivative_error)
    if 0 in value:
        return {
            "passed": False,
            "failure": "SPIN_ONE_INFINITY_REDUCED_VALUE_CONTAINS_ZERO",
        }
    return {
        "passed": True,
        "q": derivative / value,
        "value": value,
        "derivative": derivative,
        "order": order,
        "residual_kernel_upper": kernel,
        "value_error_upper": value_error,
        "derivative_error_upper": derivative_error,
    }


def horizon_series(omega: acb, order: int) -> list:
    """Moving-phase future-horizon Frobenius series for spin one."""
    aa = [0, 4, 4, 1]
    bb = [
        4 + 16j * omega,
        2 + 24j * omega,
        12j * omega,
        2j * omega,
    ]
    # -6 r = -12 - 6 rho for r=2+rho.
    cc = [-12, -6]
    coefficients = [acb(1)]
    for n in range(order - 1):
        target = n + 1
        pivot = acb(0)
        known = acb(0)
        for j, value in enumerate(aa):
            k = n - j + 2
            if k >= 0:
                term = value * k * (k - 1)
                if k == target:
                    pivot += term
                elif k < len(coefficients):
                    known += term * coefficients[k]
        for j, value in enumerate(bb):
            k = n - j + 1
            if k >= 0:
                term = value * k
                if k == target:
                    pivot += term
                elif k < len(coefficients):
                    known += term * coefficients[k]
        for j, value in enumerate(cc):
            k = n - j
            if 0 <= k < len(coefficients):
                known += value * coefficients[k]
        coefficients.append(-known / pivot)
    return coefficients


def horizon_seed(omega_box: acb, order: int = DEFAULT_ORDER) -> dict:
    """Certify the moving-phase spin-one horizon line at rho=2^-22."""
    # The local QNM square obeys |omega|<1 and Im(omega)<1/8.  For n>=2,
    # the recurrence pivot is at least 4(n+1)(n+1/2).  Assuming the previous
    # coefficients obey M*100^k, the normalized numerator is bounded by
    #
    #   (38/100 + 10/10000 + 2/1000000) / 2
    #       = 190501/1000000 < 1.
    #
    # This proves the geometric coefficient majorant after the finite seed.
    if omega_box.abs_upper() >= 1 or omega_box.imag.upper() >= af(Fraction(1, 8)):
        return {
            "passed": False,
            "failure": "SPIN_ONE_HORIZON_MAJORANT_FREQUENCY_DOMAIN",
        }
    induction_multiplier = Fraction(190_501, 1_000_000)
    if induction_multiplier >= 1:
        raise RuntimeError("invalid horizon induction multiplier")
    coefficients = horizon_series(omega_box, order)
    majorant = arb(10**6)
    growth = arb(100)
    coefficient_gate = all(
        coefficient.abs_upper() <= majorant * growth**n
        for n, coefficient in enumerate(coefficients)
    )
    if not coefficient_gate:
        return {
            "passed": False,
            "failure": "SPIN_ONE_HORIZON_FINITE_COEFFICIENT_GATE",
        }
    rho = af(HORIZON_RHO)
    x = growth * rho
    value_tail = majorant * x**order / (1 - x)
    derivative_tail = (
        majorant * growth * order * x ** (order - 1) / (1 - x) ** 2
    )
    value = acb(0)
    derivative_rho = acb(0)
    for n, coefficient in enumerate(coefficients):
        value += coefficient * rho**n
        if n:
            derivative_rho += n * coefficient * rho ** (n - 1)
    value = inflate(value, value_tail)
    derivative_rho = inflate(derivative_rho, derivative_tail)
    if 0 in value:
        return {
            "passed": False,
            "failure": "SPIN_ONE_HORIZON_REDUCED_VALUE_CONTAINS_ZERO",
        }
    lapse = rho / (2 + rho)
    return {
        "passed": True,
        "q": lapse * derivative_rho / value,
        "value": value,
        "derivative_rho": derivative_rho,
        "order": order,
        "coefficient_gate": coefficient_gate,
        "induction_multiplier": induction_multiplier,
        "value_tail_upper": value_tail,
        "derivative_tail_upper": derivative_tail,
    }


def _radial_coefficients(
    r0: Fraction,
    order: int,
) -> tuple[list[acb], list[acb]]:
    """Taylor coefficients of c=r/(r-2) and b_1=6/r^2."""
    rr = af(r0)
    distance = af(r0 - 2)
    c_coefficients = []
    b_coefficients = []
    for k in range(order):
        c_coefficient = (
            arb(1) + arb(2) / distance
            if k == 0
            else arb(2) * ((-1) ** k) / distance ** (k + 1)
        )
        b_coefficient = (
            arb(6) * ((-1) ** k) * arb(k + 1) / rr ** (k + 2)
        )
        c_coefficients.append(acb(c_coefficient))
        b_coefficients.append(acb(b_coefficient))
    return c_coefficients, b_coefficients


def reference_step(
    r0: Fraction,
    step: Fraction,
    q0: acb,
    omega: acb,
    *,
    order: int,
) -> tuple[acb | None, str | None]:
    """Taylor reference step with a proved analytic tail."""
    c_coefficients, b_coefficients = _radial_coefficients(r0, order)
    series = [q0]
    for n in range(order - 1):
        rhs = acb(0)
        for k in range(n + 1):
            convolution = sum(
                (
                    series[j] * series[n - k - j]
                    for j in range(n - k + 1)
                ),
                acb(0),
            )
            rhs += c_coefficients[k] * (
                2j * omega * series[n - k] - convolution
            )
        rhs += b_coefficients[n]
        series.append(rhs / (n + 1))

    rho = 2 * abs(step)
    r_lower = af(r0 - rho)
    if r_lower <= 2:
        return None, "SPIN_ONE_REFERENCE_DISK_CROSSES_HORIZON"
    c_bound = r_lower / (r_lower - 2)
    b_bound = 6 / r_lower**2
    q_initial = q0.abs_upper()
    qa = af(rho) * c_bound
    qb = af(rho) * 2 * omega.abs_upper() * c_bound - 1
    qc = q_initial + af(rho) * b_bound
    discriminant = qb * qb - 4 * qa * qc
    if discriminant.lower() <= 0:
        return None, "SPIN_ONE_REFERENCE_Q_DISCRIMINANT"
    q_bound = _strict_small_root(qa, qb, qc, discriminant)
    if q_bound is None:
        return None, "SPIN_ONE_REFERENCE_Q_ROOT"
    rhs_bound = q_initial + af(rho) * (
        2 * omega.abs_upper() * c_bound * q_bound
        + c_bound * q_bound * q_bound
        + b_bound
    )
    if rhs_bound.upper() >= q_bound.lower():
        return None, "SPIN_ONE_REFERENCE_Q_SELF_MAP"
    value = acb(0)
    power = arb(1)
    for coefficient in series:
        value += coefficient * power
        power *= af(step)
    ratio = af(abs(step)) / af(rho)
    tail = q_bound * ratio**order / (1 - ratio)
    return inflate(value, tail), None


def backward_remainder(
    *,
    q_radius: arb,
    r0: Fraction,
    step: Fraction,
    omega_radius: arb,
    omega_center: acb,
    q0: acb,
    q1: acb,
) -> tuple[arb | None, str | None]:
    """Affine parameter remainder for inward outgoing transport."""
    h = af(abs(step))
    r_lower = af(r0 + step)
    c_bound = r_lower / (r_lower - 2)
    q_reference = max(q0.abs_upper(), q1.abs_upper())
    q_real_upper = max(q0.real.upper(), q1.real.upper())
    mu = c_bound * (
        2 * omega_center.imag.upper() + 2 * q_real_upper
    )
    linear = mu + 2 * c_bound * omega_radius
    forcing = 2 * c_bound * omega_radius * q_reference
    qa = h * c_bound
    qb = h * linear - 1
    qc = q_radius + h * forcing
    discriminant = qb * qb - 4 * qa * qc
    if discriminant.lower() <= 0:
        return None, "SPIN_ONE_BACKWARD_REMAINDER_DISCRIMINANT"
    bound = _strict_small_root(qa, qb, qc, discriminant)
    if bound is None:
        return None, "SPIN_ONE_BACKWARD_REMAINDER_ROOT"
    rhs = q_radius + h * (
        linear * bound + c_bound * bound * bound + forcing
    )
    if rhs.upper() >= bound.lower():
        return None, "SPIN_ONE_BACKWARD_REMAINDER_SELF_MAP"
    return bound, None


def forward_remainder(
    *,
    q_radius: arb,
    r0: Fraction,
    step: Fraction,
    omega_radius: arb,
    omega_center: acb,
    q0: acb,
    q1: acb,
) -> tuple[arb | None, str | None]:
    """Affine parameter remainder for outward horizon transport."""
    h = af(step)
    c_bound = af(r0) / af(r0 - 2)
    q_reference = max(q0.abs_upper(), q1.abs_upper())
    mu = c_bound * (
        2 * omega_center.imag.upper()
        - 2 * min(q0.real.lower(), q1.real.lower())
    )
    linear = mu + 2 * c_bound * omega_radius
    forcing = 2 * c_bound * omega_radius * q_reference
    qa = h * c_bound
    qb = h * linear - 1
    qc = q_radius + h * forcing
    discriminant = qb * qb - 4 * qa * qc
    if discriminant.lower() <= 0:
        return None, "SPIN_ONE_FORWARD_REMAINDER_DISCRIMINANT"
    bound = _strict_small_root(qa, qb, qc, discriminant)
    if bound is None:
        return None, "SPIN_ONE_FORWARD_REMAINDER_ROOT"
    rhs = q_radius + h * (
        linear * bound + c_bound * bound * bound + forcing
    )
    if rhs.upper() >= bound.lower():
        return None, "SPIN_ONE_FORWARD_REMAINDER_SELF_MAP"
    return bound, None


def outgoing_transport(omega_box: acb, order: int = DEFAULT_ORDER) -> dict:
    """Transport the outgoing spin-one line from r=45 to r=32."""
    seed = infinity_seed(omega_box, order)
    if not seed["passed"]:
        return seed
    omega_center = midpoint(omega_box)
    omega_radius = radius_from(omega_box, omega_center)
    q_center = midpoint(seed["q"])
    q_radius = radius_from(seed["q"], q_center)
    r = OUTER_RADIUS
    accepted = 0
    rejected = 0
    while r > MATCH_RADIUS:
        step = max(Fraction(-1, 20), MATCH_RADIUS - r)
        while True:
            reference, failure = reference_step(
                r, step, q_center, omega_center, order=order
            )
            if reference is not None:
                q1 = midpoint(reference)
                remainder, failure = backward_remainder(
                    q_radius=q_radius,
                    r0=r,
                    step=step,
                    omega_radius=omega_radius,
                    omega_center=omega_center,
                    q0=q_center,
                    q1=q1,
                )
            else:
                remainder = None
            if remainder is not None:
                break
            rejected += 1
            step /= 2
            if abs(step) < Fraction(1, 10240):
                return {
                    "passed": False,
                    "radius": str(r),
                    "failure": failure,
                }
        q_radius = remainder + radius_from(reference, q1)
        q_center = q1
        r += step
        accepted += 1
    return {
        "passed": True,
        "q": inflate(q_center, q_radius),
        "seed": seed,
        "accepted_steps": accepted,
        "rejected_trials": rejected,
        "order": order,
    }


def horizon_transport(omega_box: acb, order: int = DEFAULT_ORDER) -> dict:
    """Transport the future-horizon-regular spin-one line to r=32."""
    seed = horizon_seed(omega_box, order)
    if not seed["passed"]:
        return seed
    omega_center = midpoint(omega_box)
    omega_radius = radius_from(omega_box, omega_center)
    q_center = midpoint(seed["q"])
    q_radius = radius_from(seed["q"], q_center)
    r = Fraction(2) + HORIZON_RHO
    accepted = 0
    rejected = 0
    while r < MATCH_RADIUS:
        step = min(
            (r - 2) / 16,
            Fraction(1, 100) if r < 4 else Fraction(1, 20),
            MATCH_RADIUS - r,
        )
        while True:
            # omega -> -omega converts the moving ingoing phase to the
            # outgoing reduced Riccati convention.
            reference, failure = reference_step(
                r, step, q_center, -omega_center, order=order
            )
            if reference is not None:
                q1 = midpoint(reference)
                remainder, failure = forward_remainder(
                    q_radius=q_radius,
                    r0=r,
                    step=step,
                    omega_radius=omega_radius,
                    omega_center=omega_center,
                    q0=q_center,
                    q1=q1,
                )
            else:
                remainder = None
            if remainder is not None:
                break
            rejected += 1
            step /= 2
            if step < (r - 2) / 2**40:
                return {
                    "passed": False,
                    "radius": str(r),
                    "failure": failure,
                }
        q_radius = remainder + radius_from(reference, q1)
        q_center = q1
        r += step
        accepted += 1
    return {
        "passed": True,
        "q": inflate(q_center, q_radius),
        "seed": seed,
        "accepted_steps": accepted,
        "rejected_trials": rejected,
        "order": order,
    }


def mismatch(omega_box: acb, order: int = DEFAULT_ORDER) -> dict:
    """Return the certified spin-one projective Evans mismatch at r=32."""
    outgoing = outgoing_transport(omega_box, order)
    horizon = horizon_transport(omega_box, order)
    if not outgoing["passed"] or not horizon["passed"]:
        return {
            "passed": False,
            "outgoing": outgoing,
            "horizon": horizon,
        }
    delta = horizon["q"] - outgoing["q"] + 2j * omega_box
    return {
        "passed": True,
        "delta": delta,
        "outgoing": outgoing,
        "horizon": horizon,
        "excludes_zero": 0 not in delta,
    }
