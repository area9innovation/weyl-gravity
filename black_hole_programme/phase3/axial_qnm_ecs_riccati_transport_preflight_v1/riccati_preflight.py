#!/usr/bin/env python3
"""Validated acb Riccati Taylor/Cauchy transport with chart switching."""
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


def af(value: Fraction | int) -> arb:
    value = Fraction(value)
    return arb(value.numerator) / value.denominator


def square(center: complex | int, radius: Fraction) -> acb:
    center = complex(center)
    rad = af(radius)
    return acb(arb(center.real, rad), arb(center.imag, rad))


def coefficients(r0: Fraction, order: int, omega: acb, chart: str) -> list:
    """Series for z'=A*z+B-C*z^2 in q or reciprocal p chart."""
    rr = af(r0)
    d = af(r0 - 2)
    result = []
    for k in range(order):
        c = (
            arb(1) + arb(2) / d
            if k == 0
            else arb(2) * ((-1) ** k) / d ** (k + 1)
        )
        b = arb(6) * ((-1) ** k) * (
            arb(k + 1) / rr ** (k + 2)
            - arb((k + 1) * (k + 2)) / 2 / rr ** (k + 3)
        )
        a = 2j * omega * c
        result.append(
            (a, acb(b), acb(c))
            if chart == "q"
            else (-a, acb(c), acb(b))
        )
    return result


def validated_step(
    r0: Fraction,
    step: Fraction,
    z0: acb,
    omega: acb,
    omega_upper: Fraction,
    chart: str,
    order: int,
) -> tuple[acb | None, dict]:
    rho = 2 * abs(step)
    rmin = af(r0 - rho)
    rmax = af(r0 + rho)
    denominator = af(r0 - 2 - rho)
    c_bound = rmax / denominator
    b_bound = arb(6) * (rmax + 1) / rmin**3
    a_bound = 2 * af(omega_upper) * c_bound
    if chart == "q":
        aa_bound, bb_bound, cc_bound = a_bound, b_bound, c_bound
    else:
        aa_bound, bb_bound, cc_bound = a_bound, c_bound, b_bound

    z_bound = z0.abs_upper()
    qa = float((af(rho) * cc_bound).upper())
    qb = float((af(rho) * aa_bound - 1).upper())
    qc = float((z_bound + af(rho) * bb_bound).upper())
    discriminant = qb * qb - 4 * qa * qc
    metadata = {
        "chart": chart,
        "r0": str(r0),
        "step": str(step),
        "majorant_quadratic": [repr(qa), repr(qb), repr(qc)],
        "majorant_discriminant_upper_float": repr(discriminant),
    }
    if discriminant <= 0:
        metadata["failure"] = "NONPOSITIVE_MAJORANT_DISCRIMINANT"
        return None, metadata
    q_candidate = (-qb - math.sqrt(discriminant)) / (2 * qa)
    if q_candidate <= float(z_bound.upper()):
        metadata["failure"] = "NO_MAJORANT_ROOT_ABOVE_CURRENT_BALL"
        return None, metadata
    q_bound = arb(q_candidate * 1.000001)
    rhs = z_bound + af(rho) * (
        aa_bound * q_bound
        + bb_bound
        + cc_bound * q_bound * q_bound
    )
    if float(rhs.upper()) >= float(q_bound.lower()):
        metadata["failure"] = "MAJORANT_SELF_MAP_NOT_STRICT"
        return None, metadata

    abc = coefficients(r0, order, omega, chart)
    series = [z0]
    for n in range(order - 1):
        total = acb(0)
        for k in range(n + 1):
            total += abc[k][0] * series[n - k]
        total += abc[n][1]
        for k in range(n + 1):
            for j in range(n - k + 1):
                total -= abc[k][2] * series[j] * series[n - k - j]
        series.append(total / (n + 1))

    value = acb(0)
    power = arb(1)
    for item in series:
        value += item * power
        power *= af(step)
    ratio = af(abs(step)) / af(rho)
    tail = q_bound * ratio**order / (1 - ratio)
    value += acb(arb(0, tail), arb(0, tail))
    metadata["tail_upper"] = str(tail.upper())
    metadata["failure"] = None
    return value, metadata


def compute(panel_count: int = 16, order: int = 14) -> dict:
    ctx.prec = 128
    ecs = json.loads(ECS.read_text())
    tail = json.loads(TAIL.read_text())
    spin2 = next(
        item for item in ecs["volterra"]["channels"]
        if item["channel"] == "spin_two"
    )
    center_re = Fraction(ecs["disk"]["center_re"])
    center_im = Fraction(ecs["disk"]["center_im"])
    radius = Fraction(ecs["disk"]["radius"])
    omega_upper = Fraction(tail["disk"]["omega_modulus_l1_upper"])
    value_radius = Fraction(spin2["reduced_value_ball"]["radius"])
    derivative_radius = Fraction(
        spin2["reduced_x_derivative_ball"]["radius"]
    )

    rows = []
    for panel in range(panel_count):
        theta = arb.pi() * arb(2 * panel + 1) / panel_count
        half_width = arb.pi() / panel_count
        chord = 2 * af(radius) * (half_width / 2).sin()
        omega = acb(
            af(center_re) + af(radius) * theta.cos(),
            af(center_im) + af(radius) * theta.sin(),
        ) + acb(arb(0, chord), arb(0, chord))

        value = square(1, value_radius)
        derivative = square(0, derivative_radius)
        projective = derivative / value
        chart = "q"
        r = Fraction(45)
        switches = 0
        successful_steps = 0
        failure = None
        while r > 4:
            if float(projective.abs_lower()) > 1:
                projective = 1 / projective
                chart = "p" if chart == "q" else "q"
                switches += 1
            step = max(Fraction(-1, 20), Fraction(4) - r)
            candidate, metadata = validated_step(
                r, step, projective, omega, omega_upper, chart, order
            )
            if candidate is None and 0 not in projective:
                projective = 1 / projective
                chart = "p" if chart == "q" else "q"
                switches += 1
                candidate, metadata = validated_step(
                    r, step, projective, omega, omega_upper, chart, order
                )
            if candidate is None:
                failure = {
                    **metadata,
                    "projective_ball": str(projective),
                    "projective_ball_contains_zero": 0 in projective,
                    "projective_component_radius_lower": [
                        str(projective.real.rad().lower()),
                        str(projective.imag.rad().lower()),
                    ],
                }
                break
            projective = candidate
            r += step
            successful_steps += 1
        rows.append(
            {
                "panel": panel,
                "omega_box": str(omega),
                "successful_steps": successful_steps,
                "chart_switches": switches,
                "last_certified_radius": str(r),
                "failure": failure,
            }
        )
    return {
        "schema": "phase3-axial-qnm-ecs-riccati-preflight-run-v1",
        "arithmetic": "python-flint acb, 128 bits",
        "panel_count": panel_count,
        "taylor_order": order,
        "radial_step": "-1/20",
        "rows": rows,
    }


def main() -> None:
    output = HERE / "riccati-run.json"
    output.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
