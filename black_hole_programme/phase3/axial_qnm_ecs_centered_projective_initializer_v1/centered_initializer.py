#!/usr/bin/env python3
"""Validated phase-factored asymptotic centers and residual-only balls."""
from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ECS = ROOT / "black_hole_programme/phase3/axial_qnm_ecs_inverse_tortoise_v1/certificate.json"
TAIL = ROOT / "black_hole_programme/phase3/axial_qnm_infinity_tail_gate_v1/certificate.json"
TANGENT = ROOT / "black_hole_programme/phase3/axial_qnm_ecs_tangent_initializer_v1/certificate.json"
RUN = HERE / "centered-run.json"


def af(value: Fraction | int) -> arb:
    value = Fraction(value)
    return arb(value.numerator) / value.denominator


def panel_box(panel: int, panel_count: int, center_re: Fraction,
              center_im: Fraction, radius: Fraction) -> acb:
    theta = arb.pi() * arb(2 * panel + 1) / panel_count
    half_width = arb.pi() / panel_count
    chord = 2 * af(radius) * (half_width / 2).sin()
    return acb(
        af(center_re) + af(radius) * theta.cos(),
        af(center_im) + af(radius) * theta.sin(),
    ) + acb(arb(0, chord), arb(0, chord))


def base_series(omega: acb, order: int) -> tuple[list, list, list, list]:
    # For y=exp(-i*omega*x)v, z=1/r, and after division by z^2:
    # A(z)v_zz+B(z)v_z+C(z)v=0.
    aa = [0, 0, 1, -4, 4]
    bb = [2j * omega, 2 - 4j * omega, -10, 12]
    cc = [-6, 18, -12]
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


def apply_operator(coefficients: list, aa: list, bb: list,
                   cc: list) -> list:
    result = [acb(0)] * (len(coefficients) + 6)
    for j, value in enumerate(aa):
        for k, coefficient in enumerate(coefficients):
            if k >= 2:
                result[j + k - 2] += (
                    value * k * (k - 1) * coefficient
                )
    for j, value in enumerate(bb):
        for k, coefficient in enumerate(coefficients):
            if k >= 1:
                result[j + k - 1] += value * k * coefficient
    for j, value in enumerate(cc):
        for k, coefficient in enumerate(coefficients):
            result[j + k] += value * coefficient
    return result


def tangent_series(omega: acb, base: list, aa: list, bb: list,
                   cc: list, order: int) -> tuple[list, list]:
    # calI/z^2 for
    # calI=i(r-2)(2*w^2*r+3*w^2+12)/(5*w*r^4).
    source = [
        2j * omega / 5,
        1j * (12 - omega * omega) / (5 * omega),
        -6j * (omega * omega + 4) / (5 * omega),
    ]
    coefficients = [acb(0)]
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
        for j, value in enumerate(source):
            k = n - j
            if 0 <= k < len(base):
                known += value * base[k]
        coefficients.append(-known / pivot)
    return coefficients, source


def tangent_residual(tangent: list, base: list, aa: list, bb: list,
                     cc: list, source: list) -> list:
    result = apply_operator(tangent, aa, bb, cc)
    for j, value in enumerate(source):
        for k, coefficient in enumerate(base):
            result[j + k] += value * coefficient
    return result


def omega_series(omega: acb, order: int) -> tuple:
    aa = [0, 0, 1, -4, 4]
    bb = [2j * omega, 2 - 4j * omega, -10, 12]
    bb_dot = [2j, -4j, 0, 0]
    cc = [-6, 18, -12]
    base = [acb(1)]
    tangent = [acb(0)]
    for n in range(order - 1):
        target = n + 1
        known = acb(0)
        known_dot = acb(0)
        pivot = acb(0)
        pivot_dot = acb(0)
        for j, value in enumerate(aa):
            k = n - j + 2
            if k >= 0:
                term = value * k * (k - 1)
                if k == target:
                    pivot += term
                elif k < len(base):
                    known += term * base[k]
                    known_dot += term * tangent[k]
        for j, value in enumerate(bb):
            k = n - j + 1
            if k >= 0:
                term = value * k
                term_dot = bb_dot[j] * k
                if k == target:
                    pivot += term
                    pivot_dot += term_dot
                elif k < len(base):
                    known += term * base[k]
                    known_dot += term * tangent[k] + term_dot * base[k]
        for j, value in enumerate(cc):
            k = n - j
            if 0 <= k < len(base):
                known += value * base[k]
                known_dot += value * tangent[k]
        next_base = -known / pivot
        next_tangent = -(
            known_dot * pivot - known * pivot_dot
        ) / (pivot * pivot)
        base.append(next_base)
        tangent.append(next_tangent)
    return base, tangent, aa, bb, bb_dot, cc


def omega_residual(base: list, tangent: list, aa: list, bb: list,
                   bb_dot: list, cc: list) -> list:
    result = apply_operator(tangent, aa, bb, cc)
    for j, value in enumerate(bb_dot):
        for k, coefficient in enumerate(base):
            if k >= 1:
                result[j + k - 1] += value * k * coefficient
    return result


def evaluate(coefficients: list, radius: int) -> tuple[acb, acb]:
    z = af(Fraction(1, radius))
    value = acb(0)
    r_derivative = acb(0)
    for n, coefficient in enumerate(coefficients):
        value += coefficient * z**n
        r_derivative += -n * coefficient * z ** (n + 1)
    x_derivative = af(Fraction(radius - 2, radius)) * r_derivative
    return value, x_derivative


def residual_bounds(residual: list, *, radius: int, slope: Fraction,
                    kappa: Fraction, omega_lower: Fraction) -> tuple:
    integral = arb(0)
    point = arb(0)
    # The residual above is for the equation divided by z^2, so its
    # coefficient at z^k contributes r^(-k-2) to the x-equation.
    for k, coefficient in enumerate(residual):
        power = k + 2
        magnitude = coefficient.abs_upper()
        integral += magnitude / (
            af(slope) * af(power - 1) * af(radius) ** (power - 1)
        )
        point += magnitude / af(radius) ** power
    weighted = point / af(kappa)
    kernel = (integral + weighted) / (2 * af(omega_lower))
    return integral, point, weighted, kernel


def inflate(value: acb, radius: arb) -> acb:
    return value + acb(arb(0, radius), arb(0, radius))


def q_step(r0: Fraction, step: Fraction, q0: acb, omega: acb,
           omega_upper: Fraction, order: int) -> tuple[acb | None, dict]:
    rho = 2 * abs(step)
    rmin = af(r0 - rho)
    rmax = af(r0 + rho)
    denominator = af(r0 - 2 - rho)
    c_bound = rmax / denominator
    b_bound = arb(6) * (rmax + 1) / rmin**3
    a_bound = 2 * af(omega_upper) * c_bound
    q_abs = q0.abs_upper()
    qa = float((af(rho) * c_bound).upper())
    qb = float((af(rho) * a_bound - 1).upper())
    qc = float((q_abs + af(rho) * b_bound).upper())
    discriminant = qb * qb - 4 * qa * qc
    metadata = {"majorant_discriminant": repr(discriminant)}
    if discriminant <= 0:
        metadata["failure"] = "NONPOSITIVE_MAJORANT_DISCRIMINANT"
        return None, metadata
    bound_float = (-qb - math.sqrt(discriminant)) / (2 * qa)
    if bound_float <= float(q_abs.upper()):
        metadata["failure"] = "NO_MAJORANT_ROOT_ABOVE_CURRENT_BALL"
        return None, metadata
    bound = arb(bound_float * 1.000001)
    rhs = q_abs + af(rho) * (
        a_bound * bound + b_bound + c_bound * bound * bound
    )
    if float(rhs.upper()) >= float(bound.lower()):
        metadata["failure"] = "MAJORANT_SELF_MAP_NOT_STRICT"
        return None, metadata

    rr = af(r0)
    dd = af(r0 - 2)
    abc = []
    for k in range(order):
        c_coefficient = (
            arb(1) + arb(2) / dd
            if k == 0 else arb(2) * ((-1) ** k) / dd ** (k + 1)
        )
        b_coefficient = arb(6) * ((-1) ** k) * (
            arb(k + 1) / rr ** (k + 2)
            - arb((k + 1) * (k + 2)) / 2 / rr ** (k + 3)
        )
        abc.append((2j * omega * c_coefficient,
                    acb(b_coefficient), acb(c_coefficient)))
    series = [q0]
    for n in range(order - 1):
        total = acb(0)
        for k in range(n + 1):
            total += abc[k][0] * series[n - k]
        total += abc[n][1]
        for k in range(n + 1):
            for j in range(n - k + 1):
                total -= abc[k][2] * series[j] * series[n - k - j]
        series.append(total / (n + 1))
    result = acb(0)
    power = arb(1)
    for coefficient in series:
        result += coefficient * power
        power *= af(step)
    ratio = af(abs(step)) / af(rho)
    tail = bound * ratio**order / (1 - ratio)
    result = inflate(result, tail)
    metadata.update({"failure": None, "tail_upper": str(tail.upper())})
    return result, metadata


def certified_panel_state(panel: int, panel_count: int = 16,
                          order: int = 16) -> tuple[acb, acb, acb, acb]:
    """Return the certified omega, q, eta, xi balls at r=45."""
    ctx.prec = 128
    ecs = json.loads(ECS.read_text())
    tail = json.loads(TAIL.read_text())
    tangent_certificate = json.loads(TANGENT.read_text())
    spin2 = next(
        item for item in ecs["volterra"]["channels"]
        if item["channel"] == "spin_two"
    )
    omega = panel_box(
        panel, panel_count, Fraction(ecs["disk"]["center_re"]),
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
        tangent_certificate["source_bounds"][
            "source_volterra_kernel_norm_upper"
        ]
    )
    source_weighted = Fraction(
        tangent_certificate["source_bounds"][
            "source_exponentially_weighted_integral_upper"
        ]
    )
    radius = 45
    slope = Fraction(2, 3)

    base, aa, bb, cc = base_series(omega, order)
    base_residual = apply_operator(base, aa, bb, cc)
    base_i, base_p, base_j, base_k = residual_bounds(
        base_residual, radius=radius, slope=slope, kappa=kappa,
        omega_lower=omega_lower,
    )
    base_error = base_k / (1 - af(alpha))
    base_error_x = base_j / (1 - af(alpha))
    value_center, derivative_center = evaluate(base, radius)
    value = inflate(value_center, base_error)
    derivative = inflate(derivative_center, base_error_x)
    q = derivative / value

    tau_coefficients, source = tangent_series(
        omega, base, aa, bb, cc, order
    )
    tau_residual = tangent_residual(
        tau_coefficients, base, aa, bb, cc, source
    )
    _, _, tau_j, tau_k = residual_bounds(
        tau_residual, radius=radius, slope=slope, kappa=kappa,
        omega_lower=omega_lower,
    )
    tau_error = (
        tau_k + af(source_kernel) * base_error
    ) / (1 - af(alpha))
    tau_error_x = (
        af(potential_weighted) * tau_error
        + tau_j
        + af(source_weighted) * base_error
    )
    tau_value_center, tau_derivative_center = evaluate(
        tau_coefficients, radius
    )
    tau_value = inflate(tau_value_center, tau_error)
    tau_derivative = inflate(tau_derivative_center, tau_error_x)
    eta = (
        tau_derivative * value - derivative * tau_value
    ) / (value * value)

    _, omega_coefficients, oa, ob, ob_dot, oc = omega_series(
        omega, order
    )
    omega_res = omega_residual(
        base, omega_coefficients, oa, ob, ob_dot, oc
    )
    _, omega_p, omega_j, omega_k = residual_bounds(
        omega_res, radius=radius, slope=slope, kappa=kappa,
        omega_lower=omega_lower,
    )
    kernel_omega = (
        af(potential_point) / (af(omega_lower) * af(kappa) ** 2)
        + af(alpha) / af(omega_lower)
    )
    residual_kernel_omega = (
        base_p / (af(omega_lower) * af(kappa) ** 2)
        + base_k / af(omega_lower)
    )
    omega_error = (
        omega_k + residual_kernel_omega
        + kernel_omega * base_error
    ) / (1 - af(alpha))
    omega_error_x = (
        omega_j + 2 * base_p / af(kappa) ** 2
        + af(potential_weighted) * omega_error
        + 2 * af(potential_point) * base_error / af(kappa) ** 2
    )
    omega_value_center, omega_derivative_center = evaluate(
        omega_coefficients, radius
    )
    omega_value = inflate(omega_value_center, omega_error)
    omega_derivative = inflate(omega_derivative_center, omega_error_x)
    xi = (
        omega_derivative * value - derivative * omega_value
    ) / (value * value)
    return omega, q, eta, xi


def compute(panel_count: int = 16, order: int = 16) -> dict:
    ctx.prec = 128
    ecs = json.loads(ECS.read_text())
    tail = json.loads(TAIL.read_text())
    tangent_certificate = json.loads(TANGENT.read_text())
    spin2 = next(
        item for item in ecs["volterra"]["channels"]
        if item["channel"] == "spin_two"
    )
    center_re = Fraction(ecs["disk"]["center_re"])
    center_im = Fraction(ecs["disk"]["center_im"])
    disk_radius = Fraction(ecs["disk"]["radius"])
    omega_lower = Fraction(ecs["disk"]["omega_modulus_lower"])
    omega_upper = Fraction(tail["disk"]["omega_modulus_l1_upper"])
    kappa = Fraction(ecs["disk"]["phase_decay_rate_lower"])
    alpha = Fraction(spin2["operator_norm_upper"])
    potential_point = Fraction(spin2["potential_point_upper_at_t0"])
    potential_weighted = Fraction(
        spin2["exponentially_weighted_integral_upper"]
    )
    source_kernel = Fraction(
        tangent_certificate["source_bounds"][
            "source_volterra_kernel_norm_upper"
        ]
    )
    source_weighted = Fraction(
        tangent_certificate["source_bounds"][
            "source_exponentially_weighted_integral_upper"
        ]
    )
    radius = 45
    slope = Fraction(2, 3)
    rows = []
    for panel in range(panel_count):
        omega = panel_box(
            panel, panel_count, center_re, center_im, disk_radius
        )
        base, aa, bb, cc = base_series(omega, order)
        base_residual = apply_operator(base, aa, bb, cc)
        base_i, base_p, base_j, base_k = residual_bounds(
            base_residual, radius=radius, slope=slope, kappa=kappa,
            omega_lower=omega_lower,
        )
        base_error = base_k / (1 - af(alpha))
        base_error_x = base_j / (1 - af(alpha))
        value_center, derivative_center = evaluate(base, radius)
        value = inflate(value_center, base_error)
        derivative = inflate(derivative_center, base_error_x)
        q = derivative / value

        tau_coefficients, source = tangent_series(
            omega, base, aa, bb, cc, order
        )
        tau_residual = tangent_residual(
            tau_coefficients, base, aa, bb, cc, source
        )
        tau_i, tau_p, tau_j, tau_k = residual_bounds(
            tau_residual, radius=radius, slope=slope, kappa=kappa,
            omega_lower=omega_lower,
        )
        tau_error = (
            tau_k + af(source_kernel) * base_error
        ) / (1 - af(alpha))
        tau_error_x = (
            af(potential_weighted) * tau_error
            + tau_j
            + af(source_weighted) * base_error
        )
        tau_value_center, tau_derivative_center = evaluate(
            tau_coefficients, radius
        )
        tau_value = inflate(tau_value_center, tau_error)
        tau_derivative = inflate(tau_derivative_center, tau_error_x)
        eta = (
            tau_derivative * value - derivative * tau_value
        ) / (value * value)

        _, omega_coefficients, oa, ob, ob_dot, oc = omega_series(
            omega, order
        )
        omega_res = omega_residual(
            base, omega_coefficients, oa, ob, ob_dot, oc
        )
        omega_i, omega_p, omega_j, omega_k = residual_bounds(
            omega_res, radius=radius, slope=slope, kappa=kappa,
            omega_lower=omega_lower,
        )
        kernel_omega = (
            af(potential_point) / (af(omega_lower) * af(kappa) ** 2)
            + af(alpha) / af(omega_lower)
        )
        residual_kernel_omega = (
            base_p / (af(omega_lower) * af(kappa) ** 2)
            + base_k / af(omega_lower)
        )
        omega_error = (
            omega_k + residual_kernel_omega
            + kernel_omega * base_error
        ) / (1 - af(alpha))
        omega_error_x = (
            omega_j + 2 * base_p / af(kappa) ** 2
            + af(potential_weighted) * omega_error
            + 2 * af(potential_point) * base_error / af(kappa) ** 2
        )
        omega_value_center, omega_derivative_center = evaluate(
            omega_coefficients, radius
        )
        omega_value = inflate(omega_value_center, omega_error)
        omega_derivative = inflate(
            omega_derivative_center, omega_error_x
        )
        xi = (
            omega_derivative * value - derivative * omega_value
        ) / (value * value)

        first_q, first_metadata = q_step(
            Fraction(45), Fraction(-1, 20), q, omega,
            omega_upper, 14,
        )
        projective = q
        current_radius = Fraction(45)
        successful_steps = 0
        terminal = None
        while current_radius > 4:
            step = max(Fraction(-1, 20), Fraction(4) - current_radius)
            candidate, metadata = q_step(
                current_radius, step, projective, omega,
                omega_upper, 14,
            )
            if candidate is None:
                terminal = metadata["failure"]
                break
            projective = candidate
            current_radius += step
            successful_steps += 1

        rows.append({
            "panel": panel,
            "omega_box": str(omega),
            "base": {
                "finite_center_value": str(value_center),
                "finite_center_x_derivative": str(derivative_center),
                "residual_value_radius": str(base_error.upper()),
                "residual_x_derivative_radius": str(base_error_x.upper()),
                "value_ball": str(value),
                "value_ball_excludes_zero": 0 not in value,
                "x_derivative_ball": str(derivative),
                "q_ball": str(q),
            },
            "tau_sensitivity": {
                "finite_center_value": str(tau_value_center),
                "finite_center_x_derivative": str(tau_derivative_center),
                "residual_value_radius": str(tau_error.upper()),
                "residual_x_derivative_radius": str(tau_error_x.upper()),
                "value_ball": str(tau_value),
                "x_derivative_ball": str(tau_derivative),
                "eta_ball": str(eta),
            },
            "omega_sensitivity": {
                "finite_center_value": str(omega_value_center),
                "finite_center_x_derivative": str(
                    omega_derivative_center
                ),
                "residual_value_radius": str(omega_error.upper()),
                "residual_x_derivative_radius": str(
                    omega_error_x.upper()
                ),
                "value_ball": str(omega_value),
                "x_derivative_ball": str(omega_derivative),
                "xi_ball": str(xi),
            },
            "first_projective_segment": {
                "from_r": "45",
                "to_r": "899/20",
                "certified": first_q is not None,
                "q_ball": None if first_q is None else str(first_q),
                "metadata": first_metadata,
            },
            "q_only_continuation_preflight": {
                "step": "-1/20",
                "successful_steps": successful_steps,
                "last_certified_radius": str(current_radius),
                "terminal_status": terminal,
            },
        })
    return {
        "schema": "phase3-axial-qnm-ecs-centered-projective-run-v1",
        "arithmetic": "python-flint acb, 128 bits",
        "panel_count": panel_count,
        "asymptotic_order": order,
        "factored_phase": "exp(-I*omega*r_star)",
        "rows": rows,
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
