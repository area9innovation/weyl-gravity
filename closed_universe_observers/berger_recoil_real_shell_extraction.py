"""Reality-reduce complex Berger feedback columns to real shell inputs.

For the symmetric-power convention used by the observer programme, the
passive Peter--Weyl columns ``k`` and ``two_j-k`` are exact conjugate
partners.  This module uses that certified correlation; it does not add the
two independently rounded imaginary rectangles and hope that they cancel.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping, Sequence

from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
    RationalInterval,
)


def _complex_interval(value: Mapping[str, Mapping[str, str]]) -> ComplexRationalInterval:
    return ComplexRationalInterval(
        RationalInterval.from_serialized(value["real"]),
        RationalInterval.from_serialized(value["imaginary"]),
    )


def conjugate_interval(value: ComplexRationalInterval) -> ComplexRationalInterval:
    """Conjugate a rectangular complex interval exactly."""
    return ComplexRationalInterval(value.real, -value.imaginary)


def _same_interval(left: ComplexRationalInterval, right: ComplexRationalInterval) -> bool:
    return left.real == right.real and left.imaginary == right.imaginary


def extract_real_channel_column_sum(
    channel_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Extract ``sum_k I_abc[two_j,k]`` as a real rational interval.

    The caller supplies one complete channel at one shell and partition.  The
    exact SU(2) reality theorem identifies partner *values*.  Equality of the
    serialized partner rectangles under conjugation is checked separately as
    a fail-closed carrier audit.  Each pair therefore contributes twice the
    real enclosure of one representative.  For even ``two_j`` the central
    self-partner contributes its real enclosure once.
    """
    if not channel_rows:
        raise ValueError("a complete nonempty channel is required")
    first = channel_rows[0]
    required = ("channel_id", "two_j", "column", "coefficient_block_interval")
    if any(any(key not in row for key in required) for row in channel_rows):
        raise ValueError("channel row is missing reality-extraction metadata")
    channel_id = first["channel_id"]
    two_j = first["two_j"]
    partition_count = first.get("partition_count")
    if not isinstance(two_j, int) or two_j < 0:
        raise ValueError("two_j must be a nonnegative integer")
    if any(
        row["channel_id"] != channel_id
        or row["two_j"] != two_j
        or row.get("partition_count") != partition_count
        for row in channel_rows
    ):
        raise ValueError("rows must share channel, shell and partition")
    by_column = {row["column"]: row for row in channel_rows}
    expected = set(range(two_j + 1))
    if set(by_column) != expected or len(channel_rows) != two_j + 1:
        raise ValueError("channel must contain each passive column exactly once")

    total = RationalInterval.point(0)
    contributions: list[dict[str, Any]] = []
    for column in range((two_j + 1) // 2):
        partner = two_j - column
        left = _complex_interval(by_column[column]["coefficient_block_interval"])
        right = _complex_interval(by_column[partner]["coefficient_block_interval"])
        if not _same_interval(right, conjugate_interval(left)):
            raise ValueError(
                f"columns {column} and {partner} are not conjugate carrier rectangles"
            )
        contribution = left.real.scale(2)
        total = total + contribution
        contributions.append(
            {
                "representative_column": column,
                "partner_column": partner,
                "representative_real_interval": left.real.serialize(),
                "representative_imaginary_interval": left.imaginary.serialize(),
                "real_pair_contribution": contribution.serialize(),
                "imaginary_pair_contribution": "0_exact_by_reality_correlation",
            }
        )

    if two_j % 2 == 0:
        column = two_j // 2
        central = _complex_interval(by_column[column]["coefficient_block_interval"])
        if not _same_interval(central, conjugate_interval(central)):
            raise ValueError("central self-partner rectangle is not conjugation invariant")
        total = total + central.real
        contributions.append(
            {
                "representative_column": column,
                "partner_column": column,
                "representative_real_interval": central.real.serialize(),
                "representative_imaginary_interval": central.imaginary.serialize(),
                "real_pair_contribution": central.real.serialize(),
                "imaginary_pair_contribution": "0_exact_by_self_partner_reality",
            }
        )

    return {
        "channel_id": channel_id,
        "two_j": two_j,
        "partition_count": partition_count,
        "passive_column_count": two_j + 1,
        "reality_pair_count": (two_j + 1) // 2,
        "self_partner_count": 1 if two_j % 2 == 0 else 0,
        "pair_contributions": contributions,
        "real_column_sum": total.serialize(),
        "imaginary_column_sum": {"lower": "0", "upper": "0", "width": "0"},
        "claim_boundary": (
            "real extraction uses the certified conjugate-column correlation; "
            "it is invalid for unrelated complex rectangles or another carrier"
        ),
    }


def reality_reduced_columns(
    channel_rows: Sequence[Mapping[str, Any]],
) -> list[RationalInterval]:
    """Return aggregator-compatible real contributions with exact pair folding."""
    extracted = extract_real_channel_column_sum(channel_rows)
    two_j = extracted["two_j"]
    output = [RationalInterval.point(0) for _ in range(two_j + 1)]
    for row in extracted["pair_contributions"]:
        output[row["representative_column"]] = RationalInterval.from_serialized(
            row["real_pair_contribution"]
        )
    return output
