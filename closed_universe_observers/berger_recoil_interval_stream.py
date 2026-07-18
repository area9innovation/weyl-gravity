"""Exact interval primitives for Berger recoil shell aggregation.

This module deliberately starts after the detector coefficient and nested
Green-convolution gates.  Its inputs are already-enclosed channel values
I_abc[two_j,k]; it applies the certified coupling and Peter--Weyl factors.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping, Sequence


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
