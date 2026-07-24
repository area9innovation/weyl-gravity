#!/usr/bin/env python3
"""Validated acb Taylor transport of the coarse spin-two ECS base balls."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ECS = ROOT / "black_hole_programme/phase3/axial_qnm_ecs_inverse_tortoise_v1/certificate.json"
TAIL = ROOT / "black_hole_programme/phase3/axial_qnm_infinity_tail_gate_v1/certificate.json"


def af(value: Fraction) -> arb:
    return arb(value.numerator) / value.denominator


def complex_square(center: complex | int, radius: Fraction) -> acb:
    mid = complex(center)
    rad = af(radius)
    return acb(arb(mid.real, rad), arb(mid.imag, rad))


def matrix_coefficients(r0: Fraction, order: int, omega: acb) -> list:
    """Taylor coefficients of the spin-two reduced r-system matrix."""
    d = af(r0 - 2)
    rr = af(r0)
    result = []
    for k in range(order):
        a01 = (
            arb(1) + arb(2) / d
            if k == 0
            else arb(2) * ((-1) ** k) / d ** (k + 1)
        )
        q = arb(6) * ((-1) ** k) * (
            arb(k + 1) / rr ** (k + 2)
            - arb((k + 1) * (k + 2)) / 2 / rr ** (k + 3)
        )
        result.append(
            [[acb(0), acb(a01)], [acb(q), 2j * omega * a01]]
        )
    return result


def taylor_step(
    r0: Fraction,
    step: Fraction,
    state: list[acb],
    omega: acb,
    omega_upper: Fraction,
    order: int,
) -> tuple[list[acb], arb]:
    """One outward-rounded Taylor step with a Cauchy tail enclosure."""
    rho = Fraction(1)
    coefficients = matrix_coefficients(r0, order, omega)
    series = [[state[0], state[1]]]
    for n in range(order - 1):
        total = [acb(0), acb(0)]
        for k in range(n + 1):
            previous = series[n - k]
            for row in range(2):
                total[row] += (
                    coefficients[k][row][0] * previous[0]
                    + coefficients[k][row][1] * previous[1]
                )
        series.append([total[0] / (n + 1), total[1] / (n + 1)])

    result = [acb(0), acb(0)]
    power = af(Fraction(1))
    h = af(step)
    for coefficient in series:
        result[0] += coefficient[0] * power
        result[1] += coefficient[1] * power
        power *= h

    # On |r-r0|<=1 the coefficient norm is bounded by the expression
    # below. Cauchy's estimate for the analytic solution then encloses all
    # omitted Taylor coefficients.
    rmin = af(r0 - rho)
    rmax = af(r0 + rho)
    denominator = af(r0 - 2 - rho)
    r_factor = rmax / denominator
    q_bound = arb(6) * (rmax + 1) / rmin**3
    matrix_bound = (
        r_factor + q_bound + 2 * af(omega_upper) * r_factor
    )
    state_bound = state[0].abs_upper() + state[1].abs_upper()
    ratio = abs(h) / af(rho)
    tail = (
        (matrix_bound * af(rho)).exp()
        * state_bound
        * ratio**order
        / (1 - ratio)
    )
    square = acb(arb(0, tail), arb(0, tail))
    return [result[0] + square, result[1] + square], tail


def compute(panel_count: int = 16, order: int = 16) -> dict:
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
        chord = (
            arb(2) * af(radius) * (half_width / 2).sin()
        )
        omega_center = acb(
            af(center_re) + af(radius) * theta.cos(),
            af(center_im) + af(radius) * theta.sin(),
        )
        omega = omega_center + acb(arb(0, chord), arb(0, chord))
        state = [
            complex_square(1, value_radius),
            complex_square(0, derivative_radius),
        ]
        r = Fraction(45)
        maximum_tail = arb(0)
        while r > 4:
            step = max(Fraction(-1, 4), Fraction(4) - r)
            state, local_tail = taylor_step(
                r, step, state, omega, omega_upper, order
            )
            maximum_tail = maximum_tail.union(local_tail)
            r += step
        component_radii = [
            max(item.real.rad(), item.imag.rad()) for item in state
        ]
        rows.append(
            {
                "panel": panel,
                "omega_box": str(omega),
                "r4_state": [str(item) for item in state],
                "component_radius_lower": [
                    str(item.lower()) for item in component_radii
                ],
                "component_radius_upper": [
                    str(item.upper()) for item in component_radii
                ],
                "maximum_local_tail_upper": str(maximum_tail.upper()),
            }
        )
    return {
        "schema": "phase3-axial-qnm-ecs-panel-transport-preflight-run-v1",
        "arithmetic": "python-flint acb, 128 bits",
        "panel_count": panel_count,
        "taylor_order": order,
        "radial_step": "-1/4",
        "radial_interval": "[45,4]",
        "frequency_cover": (
            "rectangular acb supersets of 16 closed circular arcs"
        ),
        "rows": rows,
    }


def main() -> None:
    output = HERE / "panel-run.json"
    output.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
