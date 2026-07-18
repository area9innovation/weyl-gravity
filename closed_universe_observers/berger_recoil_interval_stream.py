"""Exact interval primitives for Berger recoil shell aggregation.

This module exposes the certified finite detector-coefficient image and then
starts the shell evaluator after the still-open nested Green-convolution gate.
The shell inputs are already-enclosed channel values I_abc[two_j,k]; the
evaluator applies the certified coupling and Peter--Weyl factors.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import factorial
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class RationalInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError("interval lower endpoint exceeds upper endpoint")

    @classmethod
    def point(cls, value: Fraction | int) -> "RationalInterval":
        value = Fraction(value)
        return cls(value, value)

    @classmethod
    def from_serialized(cls, value: Mapping[str, str]) -> "RationalInterval":
        return cls(Fraction(value["lower"]), Fraction(value["upper"]))

    def __add__(self, other: "RationalInterval") -> "RationalInterval":
        return RationalInterval(self.lower + other.lower, self.upper + other.upper)

    def __mul__(self, other: "RationalInterval") -> "RationalInterval":
        products = (
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper,
        )
        return RationalInterval(min(products), max(products))

    def scale(self, scalar: Fraction | int) -> "RationalInterval":
        return self * RationalInterval.point(Fraction(scalar))

    def serialize(self) -> dict[str, str]:
        return {
            "lower": str(self.lower),
            "upper": str(self.upper),
            "width": str(self.upper - self.lower),
        }


def _sum_intervals(values: Sequence[RationalInterval]) -> RationalInterval:
    total = RationalInterval.point(0)
    for value in values:
        total = total + value
    return total


def detector_profile_coefficient_interval(
    certificate: Mapping[str, Any],
    *,
    detector: str,
    two_j: int,
    block: str,
    row: int,
    column: int,
    t_power: int,
    coframe_component: int | None = None,
) -> dict[str, object]:
    """Read one certified finite advanced-Maxwell detector coefficient.

    Missing serialized entries inside the validated index domain are exact
    structural zeros.  The provider is intentionally limited to two_j<=4.
    """
    if certificate.get("result_id") != "BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE":
        raise ValueError("wrong detector coefficient certificate")
    if detector not in ("D0", "D1"):
        raise ValueError("detector must be D0 or D1")
    if not 0 <= two_j <= 4:
        raise ValueError("finite detector coefficient provider covers only 0<=two_j<=4")
    dimension = two_j + 1
    if not 0 <= row < dimension or not 0 <= column < dimension:
        raise ValueError("row and column must lie in the selected representation")
    if t_power < 0:
        raise ValueError("t_power must be nonnegative")
    if block == "spatial_one_form_advanced_polynomial":
        if coframe_component not in (1, 2, 3):
            raise ValueError("spatial block requires coframe_component=1,2,3")
    elif block == "temporal_scalar_advanced_polynomial":
        if coframe_component is not None:
            raise ValueError("temporal block has no coframe component")
    else:
        raise ValueError("unknown detector coefficient block")

    detector_row = next(row_value for row_value in certificate["detectors"] if row_value["detector_id"] == detector)
    mode = next(mode_value for mode_value in detector_row["modes"] if mode_value["two_j"] == two_j)
    match = None
    for entry in mode[block]:
        if entry["row"] != row or entry["column"] != column:
            continue
        if block.startswith("spatial") and entry["coframe_component"] != coframe_component:
            continue
        match = next((coefficient for coefficient in entry["coefficients"] if coefficient["T_power"] == t_power), None)
        break
    if match is None:
        real = imaginary = RationalInterval.point(0)
        structural_zero = True
    else:
        real = RationalInterval.from_serialized(match["real"])
        imaginary = RationalInterval.from_serialized(match["imag"])
        structural_zero = False
    return {
        "detector": detector,
        "two_j": two_j,
        "block": block,
        "coframe_component": coframe_component,
        "row": row,
        "column": column,
        "T_power": t_power,
        "real": real.serialize(),
        "imaginary": imaginary.serialize(),
        "structural_zero": structural_zero,
        "uniform_entire_series_remainders": mode["uniform_entire_series_remainders"],
        "claim_boundary": "finite advanced Maxwell detector coefficient through two_j=4; not a massive or recoil-channel coefficient",
    }


def _absolute_upper(interval: RationalInterval) -> Fraction:
    return max(abs(interval.lower), abs(interval.upper))


def _polynomial_uniform_upper(
    coefficients: Sequence[RationalInterval], slab_length: Fraction
) -> Fraction:
    return sum(
        (_absolute_upper(coefficient) * slab_length**power for power, coefficient in enumerate(coefficients)),
        Fraction(0),
    )


def _volterra_polynomial_convolution(
    source: Sequence[RationalInterval], kernel: Sequence[RationalInterval]
) -> tuple[RationalInterval, ...]:
    output = [RationalInterval.point(0) for _ in range(len(source) + len(kernel))]
    for source_power, source_coefficient in enumerate(source):
        for kernel_power, kernel_coefficient in enumerate(kernel):
            output_power = source_power + kernel_power + 1
            beta = Fraction(
                factorial(source_power) * factorial(kernel_power),
                factorial(output_power),
            )
            output[output_power] = output[output_power] + (
                source_coefficient * kernel_coefficient
            ).scale(beta)
    return tuple(output)


def evaluate_nested_green_time_convolution_interval(
    *,
    source_coefficients: Sequence[RationalInterval],
    source_remainder_upper: Fraction,
    kernel_stages: Sequence[Mapping[str, Any]],
    slab_length: Fraction,
    orientation: str,
) -> dict[str, object]:
    """Compose supplied polynomial Green-kernel enclosures causally.

    In the retarded coordinate ``x=t-t_left`` and advanced coordinate
    ``x=t_right-t``, each stage evaluates ``integral_0^x K(x-y)f(y)dy``.
    Coefficients use the exact beta-integral factor, while uniform input and
    kernel remainders are propagated on the declared finite slab.
    """
    slab_length = Fraction(slab_length)
    source_remainder_upper = Fraction(source_remainder_upper)
    if orientation not in ("retarded", "advanced"):
        raise ValueError("orientation must be retarded or advanced")
    if slab_length <= 0:
        raise ValueError("slab_length must be positive")
    if source_remainder_upper < 0:
        raise ValueError("source remainder upper bound must be nonnegative")
    if not source_coefficients:
        raise ValueError("source polynomial must contain at least one coefficient")
    if not kernel_stages:
        raise ValueError("at least one Green-kernel stage is required")

    coefficients = tuple(source_coefficients)
    remainder = source_remainder_upper
    stage_rows = []
    for stage_index, stage in enumerate(kernel_stages):
        kernel = tuple(stage.get("coefficients", ()))
        kernel_remainder = Fraction(stage.get("uniform_remainder_upper", 0))
        if not kernel:
            raise ValueError("each Green-kernel stage needs polynomial coefficients")
        if kernel_remainder < 0:
            raise ValueError("kernel remainder upper bound must be nonnegative")
        source_upper = _polynomial_uniform_upper(coefficients, slab_length)
        kernel_upper = _polynomial_uniform_upper(kernel, slab_length)
        output = _volterra_polynomial_convolution(coefficients, kernel)
        output_remainder = slab_length * (
            source_upper * kernel_remainder
            + kernel_upper * remainder
            + remainder * kernel_remainder
        )
        stage_rows.append(
            {
                "stage": stage_index,
                "kernel_label": str(stage.get("label", f"stage_{stage_index}")),
                "polynomial_coefficients": [value.serialize() for value in output],
                "uniform_remainder_upper": str(output_remainder),
            }
        )
        coefficients = output
        remainder = output_remainder

    return {
        "orientation": orientation,
        "causal_coordinate": "t-t_left" if orientation == "retarded" else "t_right-t",
        "slab_length": str(slab_length),
        "stages": stage_rows,
        "polynomial_coefficients": [value.serialize() for value in coefficients],
        "uniform_remainder_upper": str(remainder),
        "claim_boundary": "supplied finite-slab polynomial Green enclosures only; no physical Berger mode binding or recoil channel evaluated",
    }


def evaluate_recoil_shell_interval(
    *,
    two_j: int,
    detector: int,
    source_preparation: int,
    source_coupling: Fraction,
    feedback_couplings: Mapping[int, Fraction],
    inverse_berger_volume: RationalInterval,
    channel_columns: Mapping[int, Sequence[RationalInterval]],
) -> dict[str, object]:
    """Aggregate one `(a,b,two_j)` shell from enclosed `I_abc[k]` values.

    The function evaluates
      ((two_j+1)/Vol) g_b sum_c g_c^2 sum_k I_abc[two_j,k].
    It does not construct any `I_abc`; that remains the detector-profile and
    nested causal-convolution responsibility.
    """
    if two_j < 0:
        raise ValueError("two_j must be nonnegative")
    if detector not in (0, 1) or source_preparation not in (0, 1):
        raise ValueError("detector and source_preparation must be 0 or 1")
    if set(feedback_couplings) != {0, 1} or set(channel_columns) != {0, 1}:
        raise ValueError("both feedback channels c=0,1 are required")
    if inverse_berger_volume.lower <= 0:
        raise ValueError("inverse Berger volume enclosure must be positive")
    expected_columns = two_j + 1
    if any(len(channel_columns[c]) != expected_columns for c in (0, 1)):
        raise ValueError("each feedback channel must contain two_j+1 passive columns")

    feedback_rows = []
    coupled_sum = RationalInterval.point(0)
    for feedback in (0, 1):
        bare = _sum_intervals(channel_columns[feedback])
        coupling_square = Fraction(feedback_couplings[feedback]) ** 2
        coupled = bare.scale(coupling_square)
        coupled_sum = coupled_sum + coupled
        feedback_rows.append(
            {
                "feedback_emitter": feedback,
                "passive_column_count": expected_columns,
                "bare_column_sum": bare.serialize(),
                "feedback_coupling_square": str(coupling_square),
                "coupled_column_sum": coupled.serialize(),
            }
        )

    source_scaled = coupled_sum.scale(Fraction(source_coupling))
    peter_weyl_weight = inverse_berger_volume.scale(two_j + 1)
    shell_interval = source_scaled * peter_weyl_weight
    return {
        "two_j": two_j,
        "detector": detector,
        "source_preparation": source_preparation,
        "feedback_rows": feedback_rows,
        "source_coupling": str(Fraction(source_coupling)),
        "source_scaled_sum": source_scaled.serialize(),
        "peter_weyl_weight": peter_weyl_weight.serialize(),
        "shell_interval": shell_interval.serialize(),
        "claim_boundary": "aggregation of supplied channel intervals only; no detector coefficient or Green convolution evaluated",
    }
