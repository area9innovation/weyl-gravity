"""Directed rational interval access to the certified Berger emitter switches."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping

import mpmath as mp

from closed_universe_observers.berger_recoil_interval_stream import RationalInterval


IV_DPS = 50
CRITICAL_LOWER = Fraction(759, 1000)
CRITICAL_UPPER = Fraction(761, 1000)


def _fraction_from_mpf_tuple(value: tuple[int, int, int, int]) -> Fraction:
    sign, mantissa, exponent, _ = value
    result = Fraction(mantissa)
    result = result * 2**exponent if exponent >= 0 else result / 2 ** (-exponent)
    return -result if sign else result


def _endpoints(value: Any) -> RationalInterval:
    lower, upper = value._mpi_
    return RationalInterval(_fraction_from_mpf_tuple(lower), _fraction_from_mpf_tuple(upper))


def _iv_fraction(value: Fraction):
    return mp.iv.mpf(value.numerator) / value.denominator


def _bump_at(value: Fraction) -> RationalInterval:
    value = abs(value)
    if value >= 1:
        return RationalInterval.point(0)
    if value == 0:
        return RationalInterval.point(1)
    x = _iv_fraction(value)
    return _endpoints(mp.iv.exp(1 - 1 / (1 - x * x)))


def _derivative_magnitude_on_point(value: Fraction) -> RationalInterval:
    value = abs(value)
    if value == 0 or value >= 1:
        return RationalInterval.point(0)
    x = _iv_fraction(value)
    return _endpoints(2 * x * mp.iv.exp(1 - 1 / (1 - x * x)) / (1 - x * x) ** 2)


def _derivative_magnitude_upper(lower: Fraction, upper: Fraction) -> Fraction:
    if not 0 <= lower <= upper <= 1:
        raise ValueError("absolute switch coordinates must lie in [0,1]")
    if lower**4 * 3 <= 1 <= upper**4 * 3:
        x = mp.iv.mpf([str(CRITICAL_LOWER), str(CRITICAL_UPPER)])
        return _endpoints(2 * x * mp.iv.exp(1 - 1 / (1 - x * x)) / (1 - x * x) ** 2).upper
    point = upper if upper**4 * 3 < 1 else lower
    return _derivative_magnitude_on_point(point).upper


def emitter_switch_interval(
    switch_certificate: Mapping[str, Any],
    moment_certificate: Mapping[str, Any],
    *,
    switch_id: str,
    physical_time_interval: RationalInterval,
) -> dict[str, object]:
    """Enclose one normalized switch and its physical-time derivative on a cell."""
    if switch_certificate.get("result_id") != "BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES":
        raise ValueError("wrong emitter-switch certificate")
    if moment_certificate.get("result_id") != "BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES":
        raise ValueError("wrong flat-bump moment certificate")
    switches = switch_certificate["causal_support_audit"]["switches"]
    switch = next((row for row in switches if row["id"] == switch_id), None)
    if switch is None:
        raise ValueError("switch_id must be h_0 or h_1")
    raw_zero = next(
        row["integral"]
        for row in moment_certificate["raw_radial_integral_enclosures"]
        if row["power"] == 0
    )
    core_integral = RationalInterval(2 * Fraction(raw_zero["lower"]), 2 * Fraction(raw_zero["upper"]))
    support_lower, support_upper = map(Fraction, switch["support_physical_time"])
    center = Fraction(switch["center_physical_time"])
    physical_radius = Fraction(switch["radius_physical_time"])
    clock_radius = Fraction(switch["radius_clock_phase"])
    cell = physical_time_interval
    if cell.upper <= support_lower or cell.lower >= support_upper:
        zero = RationalInterval.point(0)
        return {
            "switch_id": switch_id,
            "physical_time_interval": cell.serialize(),
            "value": zero.serialize(),
            "physical_time_derivative": zero.serialize(),
            "structural_zero": True,
        }

    inside_lower = max(cell.lower, support_lower)
    inside_upper = min(cell.upper, support_upper)
    s_lower = (inside_lower - center) / physical_radius
    s_upper = (inside_upper - center) / physical_radius
    partial_outside = cell.lower < support_lower or cell.upper > support_upper
    minimum_abs = Fraction(0) if s_lower <= 0 <= s_upper else min(abs(s_lower), abs(s_upper))
    maximum_abs = max(abs(s_lower), abs(s_upper))
    bump_lower = Fraction(0) if partial_outside else _bump_at(maximum_abs).lower
    bump_upper = _bump_at(minimum_abs).upper
    value = RationalInterval(
        bump_lower / (clock_radius * core_integral.upper),
        bump_upper / (clock_radius * core_integral.lower),
    )

    derivative_magnitude = _derivative_magnitude_upper(minimum_abs, maximum_abs)
    derivative_scale = clock_radius * physical_radius * core_integral.lower
    derivative_upper = derivative_magnitude / derivative_scale
    if s_upper <= 0:
        derivative = RationalInterval(Fraction(0), derivative_upper)
    elif s_lower >= 0:
        derivative = RationalInterval(-derivative_upper, Fraction(0))
    else:
        derivative = RationalInterval(-derivative_upper, derivative_upper)
    return {
        "switch_id": switch_id,
        "physical_time_interval": cell.serialize(),
        "value": value.serialize(),
        "physical_time_derivative": derivative.serialize(),
        "structural_zero": False,
        "support_physical_time": [str(support_lower), str(support_upper)],
        "core_integral_interval": core_integral.serialize(),
        "claim_boundary": "normalized switch value and physical-time derivative on one rational cell; no Green convolution, form contraction or emitter preparation coefficient",
    }
