"""Arb enclosure of RW reflection on a real-frequency ball.

This reuses the validated fixed-frequency Taylor/defect engine, but replaces
the scalar frequency by one real Arb ball.  At each spatial step the common
frequency dependence is conservatively absorbed into the coefficient and
solution defect.  The result is deliberately a small cell rather than an
attempt to transport the complete pilot interval in one rectangular ball.
"""
from __future__ import annotations

from contextlib import contextmanager

from flint import acb, arb

from ..axial_scalar_reflection_point_half_v1 import rigorous as base


OMEGA_INTERVAL = arb("0.5 +/- 0.00005")
OMEGA_LEFT = "0.49995"
OMEGA_RIGHT = "0.50005"


def _omega() -> acb:
    return acb(OMEGA_INTERVAL)


def _coefficient_series(x0: float, spin: int, order: int) -> list:
    x = base.acb_series([acb(x0), acb(1)], prec=order)
    potential = base._potential(base._r_of_x(x), spin)
    phase_plus = (2 * acb(1j) * _omega() * x).exp()
    phase_minus = 1 / phase_plus
    factor = 1 / (2 * _omega())
    matrix = (
        (
            -acb(1j) * factor * potential,
            -acb(1j) * factor * potential * phase_minus,
        ),
        (
            acb(1j) * factor * potential * phase_plus,
            acb(1j) * factor * potential,
        ),
    )
    return [
        [
            [matrix[row][col][degree] for degree in range(order)]
            for col in range(2)
        ]
        for row in range(2)
    ]


def _coefficient_disk_bound(
    x0: float, spin: int, radius: float
) -> float:
    x = acb(arb(x0, radius), arb(0, radius))
    potential = base._potential(base._r_of_x(x), spin)
    phase_plus = (2 * acb(1j) * _omega() * x).exp()
    factor = potential / (2 * _omega())
    entries = (factor, factor * phase_plus, factor / phase_plus)
    if not all(entry.is_finite() for entry in entries):
        raise RuntimeError("frequency-cell Cauchy rectangle is nonfinite")
    return max(base._abs_upper(entry) for entry in entries)


def _inverse_frequency_upper() -> float:
    return base._arb_upper(1 / OMEGA_INTERVAL)


def _horizon_tail(spin: int) -> tuple[acb, float, float]:
    r0 = base._r_of_x(acb(base.X_LEFT))
    if spin == 1:
        integral = 3 - 6 / r0
    elif spin == 2:
        integral = acb("2.25") - 6 / r0 + 3 / r0**2
    else:
        raise ValueError(f"unsupported spin {spin}")
    integral_upper = base._arb_upper(integral.real)
    matrix_l1_upper = base._mul_up(
        integral_upper, _inverse_frequency_upper()
    )
    return r0, integral_upper, base._expm1_up(matrix_l1_upper)


def _infinity_tail(
    spin: int, centre: list[acb], finite_error: float
) -> tuple[acb, float, float, float]:
    r1 = base._r_of_x(acb(base.X_RIGHT))
    if spin == 1:
        integral = 6 / r1
    elif spin == 2:
        integral = 6 / r1 - 3 / r1**2
    else:
        raise ValueError(f"unsupported spin {spin}")
    integral_upper = base._arb_upper(integral.real)
    matrix_l1_upper = base._mul_up(
        integral_upper, _inverse_frequency_upper()
    )
    endpoint_norm = base._add_up(
        max(
            base._abs_upper(centre[0]),
            base._abs_upper(centre[1]),
        ),
        finite_error,
    )
    tail_error = base._mul_up(
        base._expm1_up(matrix_l1_upper), endpoint_norm
    )
    return r1, integral_upper, matrix_l1_upper, tail_error


@contextmanager
def _cell_engine():
    names = (
        "_coefficient_series",
        "_coefficient_disk_bound",
        "_horizon_tail",
        "_infinity_tail",
    )
    originals = {name: getattr(base, name) for name in names}
    replacements = {
        "_coefficient_series": _coefficient_series,
        "_coefficient_disk_bound": _coefficient_disk_bound,
        "_horizon_tail": _horizon_tail,
        "_infinity_tail": _infinity_tail,
    }
    try:
        for name, value in replacements.items():
            setattr(base, name, value)
        yield
    finally:
        for name, value in originals.items():
            setattr(base, name, value)


def run_all() -> dict:
    with _cell_engine():
        return {
            geometry.name: {
                f"spin_{spin}": base.run_channel(spin, geometry)
                for spin in (1, 2)
            }
            for geometry in (base.PRIMARY, base.SECONDARY)
        }
