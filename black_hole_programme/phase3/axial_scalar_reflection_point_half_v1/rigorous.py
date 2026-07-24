"""Arb-backed defect integration for the fixed-frequency RW reflection rail.

The calculation is intentionally pointwise in frequency.  It avoids the
shared-frequency wrapping that defeated the earlier whole-cell interaction
rail.  Every local Taylor polynomial is checked a posteriori using a Cauchy
bound for the exact coefficient tail and a Gronwall bound for the solution
defect.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from flint import acb, acb_series, arb, ctx


OMEGA = 0.5
X_LEFT = -25.0
X_RIGHT = 250.0
CAUCHY_RADIUS = 0.25
PRECISION_BITS = 160


def _next_up(value: float) -> float:
    return math.nextafter(value, math.inf)


def _next_down(value: float) -> float:
    return math.nextafter(value, -math.inf)


def _add_up(left: float, right: float) -> float:
    return _next_up(left + right)


def _mul_up(left: float, right: float) -> float:
    if left < 0.0 or right < 0.0:
        raise ValueError("directed product expects nonnegative inputs")
    return _next_up(left * right)


def _exp_up(value: float) -> float:
    return _next_up(float(arb(value).exp().upper()))


def _expm1_up(value: float) -> float:
    return _next_up(float((arb(value).exp() - 1).upper()))


def _arb_upper(value: arb) -> float:
    return _next_up(float(value.upper()))


def _arb_lower(value: arb) -> float:
    return _next_down(float(value.lower()))


def _abs_upper(value: acb) -> float:
    return _arb_upper(abs(value))


def _abs_lower(value: acb) -> float:
    return max(0.0, _arb_lower(abs(value)))


def _radius_upper(value: acb) -> float:
    return _abs_upper(value - value.mid())


def _positive_sum(values: list[float]) -> float:
    total = 0.0
    for value in values:
        total = _add_up(total, value)
    return total


def _positive_power(value: float, exponent: int) -> float:
    result = 1.0
    for _ in range(exponent):
        result = _mul_up(result, value)
    return result


def _r_of_x(value: acb | acb_series) -> acb | acb_series:
    return 2 * (1 + (value / 2 - 1).exp().lambertw())


def _potential(r: acb | acb_series, spin: int) -> acb | acb_series:
    if spin == 1:
        return 6 * (r - 2) / r**3
    if spin == 2:
        return 6 * (r - 2) * (r - 1) / r**4
    raise ValueError(f"unsupported spin {spin}")


def _coefficient_series(x0: float, spin: int, order: int) -> list:
    x = acb_series([acb(x0), acb(1)], prec=order)
    potential = _potential(_r_of_x(x), spin)
    phase_plus = (acb(1j) * x).exp()
    phase_minus = 1 / phase_plus
    matrix = (
        (-acb(1j) * potential, -acb(1j) * potential * phase_minus),
        (acb(1j) * potential * phase_plus, acb(1j) * potential),
    )
    return [
        [
            [matrix[row][col][degree] for degree in range(order)]
            for col in range(2)
        ]
        for row in range(2)
    ]


def _coefficient_disk_bound(x0: float, spin: int, radius: float) -> float:
    # This rectangle contains the complex Cauchy disk.  Since |Im x|<1/4,
    # exp(x/2-1) stays in the open right half-plane; the principal Lambert-W
    # branch and both rational potentials are analytic throughout it.
    x = acb(arb(x0, radius), arb(0, radius))
    potential = _potential(_r_of_x(x), spin)
    if not potential.is_finite():
        raise RuntimeError("Cauchy rectangle lost the analytic RW branch")
    return _mul_up(_abs_upper(potential), _exp_up(radius))


def _matrix_vector(matrix: list, vector: list[acb]) -> list[acb]:
    return [
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    ]


@dataclass(frozen=True)
class Geometry:
    name: str
    step: float
    order: int


@dataclass
class StepDiagnostics:
    coefficient_tail_row_norm: float
    residual_sup_norm: float
    generator_row_norm: float


def _step(
    x0: float,
    centre: list[acb],
    error: float,
    spin: int,
    geometry: Geometry,
) -> tuple[list[acb], float, StepDiagnostics]:
    h = geometry.step
    order = geometry.order
    radius = CAUCHY_RADIUS
    if not 0.0 < h < radius:
        raise ValueError("Taylor step must lie strictly inside Cauchy disk")

    coefficient_balls = _coefficient_series(x0, spin, order)
    coefficients = [
        [
            [coefficient_balls[i][j][k].mid() for k in range(order)]
            for j in range(2)
        ]
        for i in range(2)
    ]

    solution = [[centre[i]] for i in range(2)]
    for degree in range(order):
        convolution = [acb(0), acb(0)]
        for left_degree in range(degree + 1):
            term = _matrix_vector(
                [
                    [
                        coefficients[i][j][left_degree]
                        for j in range(2)
                    ]
                    for i in range(2)
                ],
                [
                    solution[0][degree - left_degree],
                    solution[1][degree - left_degree],
                ],
            )
            convolution[0] += term[0]
            convolution[1] += term[1]
        solution[0].append(convolution[0] / (degree + 1))
        solution[1].append(convolution[1] / (degree + 1))

    coefficient_rounding = 0.0
    for row in range(2):
        row_bound = 0.0
        for col in range(2):
            row_bound = _add_up(
                row_bound,
                _positive_sum([
                    _mul_up(
                        _radius_upper(coefficient_balls[row][col][degree]),
                        _positive_power(h, degree),
                    )
                    for degree in range(order)
                ]),
            )
        coefficient_rounding = max(coefficient_rounding, row_bound)

    cauchy_bound = _coefficient_disk_bound(x0, spin, radius)
    ratio = h / radius
    scalar_tail = _mul_up(
        cauchy_bound,
        _next_up(_positive_power(ratio, order) / (1.0 - ratio)),
    )
    # Each row has two entries.
    coefficient_tail = _add_up(
        coefficient_rounding, _mul_up(2.0, scalar_tail)
    )

    polynomial_generator_norm = 0.0
    for row in range(2):
        row_bound = 0.0
        for col in range(2):
            row_bound = _add_up(
                row_bound,
                _positive_sum([
                    _mul_up(
                        _abs_upper(coefficients[row][col][degree]),
                        _positive_power(h, degree),
                    )
                    for degree in range(order)
                ]),
            )
        polynomial_generator_norm = max(
            polynomial_generator_norm, row_bound
        )
    generator_norm = _add_up(
        polynomial_generator_norm, coefficient_tail
    )

    solution_sup = max(
        _positive_sum([
            _mul_up(
                _abs_upper(solution[row][degree]),
                _positive_power(h, degree),
            )
            for degree in range(order + 1)
        ])
        for row in range(2)
    )

    residual_coefficients = [
        [acb(0) for _ in range(2 * order)] for _ in range(2)
    ]
    for degree in range(order):
        for row in range(2):
            residual_coefficients[row][degree] += (
                (degree + 1) * solution[row][degree + 1]
            )
    for left_degree in range(order):
        for right_degree in range(order + 1):
            term = _matrix_vector(
                [
                    [
                        coefficients[i][j][left_degree]
                        for j in range(2)
                    ]
                    for i in range(2)
                ],
                [
                    solution[0][right_degree],
                    solution[1][right_degree],
                ],
            )
            residual_coefficients[0][left_degree + right_degree] -= term[0]
            residual_coefficients[1][left_degree + right_degree] -= term[1]

    polynomial_residual = max(
        _positive_sum([
            _mul_up(
                _abs_upper(residual_coefficients[row][degree]),
                _positive_power(h, degree),
            )
            for degree in range(2 * order)
        ])
        for row in range(2)
    )
    residual_sup = _add_up(
        polynomial_residual, _mul_up(coefficient_tail, solution_sup)
    )

    amplification = _exp_up(_mul_up(generator_norm, h))
    if generator_norm > 0.0:
        defect_integral = _next_up(float(
            (
                (arb(_mul_up(generator_norm, h)).exp() - 1)
                / arb(generator_norm)
            ).upper()
        ))
    else:
        defect_integral = _next_up(h)
    output_error = _add_up(
        _mul_up(amplification, error),
        _mul_up(defect_integral, residual_sup),
    )

    output = []
    output_rounding = 0.0
    for row in range(2):
        value = acb(0)
        for degree in range(order, -1, -1):
            value = value * h + solution[row][degree]
        output_rounding = max(output_rounding, _radius_upper(value))
        output.append(value.mid())
    output_error = _add_up(output_error, output_rounding)
    return output, output_error, StepDiagnostics(
        coefficient_tail_row_norm=coefficient_tail,
        residual_sup_norm=residual_sup,
        generator_row_norm=generator_norm,
    )


def _horizon_tail(spin: int) -> tuple[acb, float, float]:
    r0 = _r_of_x(acb(X_LEFT))
    if spin == 1:
        integral = 3 - 6 / r0
        formula = "3-6/r(-25)"
    else:
        integral = acb("2.25") - 6 / r0 + 3 / r0**2
        formula = "9/4-6/r(-25)+3/r(-25)^2"
    del formula
    integral_upper = _arb_upper(integral.real)
    matrix_l1_upper = _mul_up(2.0, integral_upper)
    return r0, integral_upper, _expm1_up(matrix_l1_upper)


def _infinity_tail(
    spin: int, centre: list[acb], finite_error: float
) -> tuple[acb, float, float, float]:
    r1 = _r_of_x(acb(X_RIGHT))
    if spin == 1:
        integral = 6 / r1
    else:
        integral = 6 / r1 - 3 / r1**2
    integral_upper = _arb_upper(integral.real)
    matrix_l1_upper = _mul_up(2.0, integral_upper)
    endpoint_norm = _add_up(
        max(_abs_upper(centre[0]), _abs_upper(centre[1])),
        finite_error,
    )
    tail_error = _mul_up(
        _expm1_up(matrix_l1_upper), endpoint_norm
    )
    return r1, integral_upper, matrix_l1_upper, tail_error


def run_channel(spin: int, geometry: Geometry) -> dict:
    ctx.prec = PRECISION_BITS
    steps_float = (X_RIGHT - X_LEFT) / geometry.step
    steps = int(round(steps_float))
    if abs(steps - steps_float) != 0.0:
        raise RuntimeError("integration interval is not tiled exactly")

    r0, horizon_integral, finite_error = _horizon_tail(spin)
    # The declared exp(+i omega r*) future-horizon phase is the a-line.
    centre = [acb(1), acb(0)]
    max_coefficient_tail = 0.0
    max_residual = 0.0
    max_generator = 0.0
    for index in range(steps):
        centre, finite_error, diagnostics = _step(
            X_LEFT + index * geometry.step,
            centre,
            finite_error,
            spin,
            geometry,
        )
        max_coefficient_tail = max(
            max_coefficient_tail,
            diagnostics.coefficient_tail_row_norm,
        )
        max_residual = max(max_residual, diagnostics.residual_sup_norm)
        max_generator = max(max_generator, diagnostics.generator_row_norm)

    r1, infinity_integral, infinity_matrix_l1, tail_error = (
        _infinity_tail(spin, centre, finite_error)
    )
    outgoing_centre_lower = _abs_lower(centre[1])
    total_error = _add_up(finite_error, tail_error)
    outgoing_lower = _next_down(outgoing_centre_lower - total_error)
    outgoing_squared_lower = _next_down(outgoing_lower * outgoing_lower)
    if outgoing_lower <= 0.0:
        raise RuntimeError(f"spin-{spin} outgoing ball contains zero")

    return {
        "spin": spin,
        "geometry": {
            "name": geometry.name,
            "step": repr(geometry.step),
            "order": geometry.order,
            "steps": steps,
            "cauchy_radius": repr(CAUCHY_RADIUS),
            "precision_bits": PRECISION_BITS,
        },
        "endpoint_coordinates": {
            "x_left": repr(X_LEFT),
            "x_right": repr(X_RIGHT),
            "r_left": str(r0),
            "r_right": str(r1),
        },
        "finite_endpoint_centre": {
            "A_in": str(centre[0]),
            "A_out": str(centre[1]),
        },
        "errors": {
            "horizon_potential_L1_upper": repr(horizon_integral),
            "finite_transport_error_upper": repr(finite_error),
            "infinity_potential_L1_upper": repr(infinity_integral),
            "infinity_generator_L1_upper": repr(infinity_matrix_l1),
            "infinity_tail_error_upper": repr(tail_error),
            "total_A_out_error_upper": repr(total_error),
            "maximum_local_coefficient_tail_row_norm": repr(
                max_coefficient_tail
            ),
            "maximum_local_residual_sup_norm": repr(max_residual),
            "maximum_local_generator_row_norm": repr(max_generator),
        },
        "bounds": {
            "finite_A_out_centre_modulus_lower": repr(
                outgoing_centre_lower
            ),
            "abs_A_out_lower": repr(outgoing_lower),
            "abs_A_out_squared_lower": repr(outgoing_squared_lower),
            "zero_excluded": True,
        },
    }


PRIMARY = Geometry("primary_h1_over_8_n24", 0.125, 24)
SECONDARY = Geometry("secondary_h1_over_16_n20", 0.0625, 20)


def run_all() -> dict:
    return {
        geometry.name: {
            f"spin_{spin}": run_channel(spin, geometry)
            for spin in (1, 2)
        }
        for geometry in (PRIMARY, SECONDARY)
    }
