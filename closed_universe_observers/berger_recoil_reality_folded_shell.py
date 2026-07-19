"""Complete a finite Berger feedback shell from reality representatives."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from typing import Any, Mapping, Sequence

from closed_universe_observers.berger_recoil_real_shell_extraction import (
    extract_real_channel_column_sum,
)


def _negated_interval(value: Mapping[str, str]) -> dict[str, str]:
    lower = -Fraction(value["upper"])
    upper = -Fraction(value["lower"])
    return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}


def conjugate_serialized_rectangle(
    value: Mapping[str, Mapping[str, str]],
) -> dict[str, dict[str, str]]:
    """Conjugate one serialized complex rectangle exactly."""
    return {
        "real": dict(value["real"]),
        "imaginary": _negated_interval(value["imaginary"]),
    }


def derive_reality_partner(row: Mapping[str, Any], *, partner_column: int) -> dict[str, Any]:
    """Derive one passive-column channel row from its exact reality partner."""
    source_column = int(row["column"])
    two_j = int(row["two_j"])
    if partner_column != two_j - source_column or partner_column == source_column:
        raise ValueError("requested column is not a distinct SU(2) reality partner")
    derived = deepcopy(dict(row))
    derived["column"] = partner_column
    derived["coefficient_block_interval"] = conjugate_serialized_rectangle(
        row["coefficient_block_interval"]
    )
    derived["evaluation_method"] = "EXACT_SU2_REALITY_DERIVATION"
    derived["reality_source_column"] = source_column
    derived["direct_backend_evaluated"] = False
    derived.pop("full_payload_sha256", None)
    return derived


def complete_reality_folded_shell(
    *,
    two_j: int,
    representative_columns: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Complete all channel columns and export their certified real sums.

    Representatives must be exactly ``0,...,floor(two_j/2)``.  The central
    column of an even shell is directly evaluated and self-conjugate; every
    larger column is derived from its smaller partner.
    """
    if not isinstance(two_j, int) or two_j < 0:
        raise ValueError("two_j must be a nonnegative integer")
    expected_representatives = set(range(two_j // 2 + 1))
    by_column = {int(row["column"]): row for row in representative_columns}
    if set(by_column) != expected_representatives or len(by_column) != len(representative_columns):
        raise ValueError("representative columns must be complete and unique")
    channel_ids = None
    for column, bundle in by_column.items():
        if int(bundle["two_j"]) != two_j:
            raise ValueError("representative shell mismatch")
        ids = {row["channel_id"] for row in bundle["channels"]}
        if len(ids) != len(bundle["channels"]):
            raise ValueError("duplicate channel in representative bundle")
        channel_ids = ids if channel_ids is None else channel_ids
        if ids != channel_ids:
            raise ValueError("representative channel coverage differs by column")
        for row in bundle["channels"]:
            if int(row["column"]) != column or int(row["two_j"]) != two_j:
                raise ValueError("channel metadata disagrees with its bundle")

    completed = []
    direct_count = 0
    derived_count = 0
    for column in range(two_j + 1):
        if column <= two_j // 2:
            bundle = deepcopy(dict(by_column[column]))
            for row in bundle["channels"]:
                row["evaluation_method"] = "DIRECT_PARTITIONED_CAUSAL_BACKEND"
                row["direct_backend_evaluated"] = True
            direct_count += len(bundle["channels"])
        else:
            source_column = two_j - column
            source = by_column[source_column]
            bundle = {
                "two_j": two_j,
                "column": column,
                "partition_count": source["partition_count"],
                "channels": [
                    derive_reality_partner(row, partner_column=column)
                    for row in source["channels"]
                ],
            }
            derived_count += len(bundle["channels"])
        completed.append(bundle)

    grouped = {
        channel: [
            row
            for bundle in completed
            for row in bundle["channels"]
            if row["channel_id"] == channel
        ]
        for channel in sorted(channel_ids or ())
    }
    real_sums = [extract_real_channel_column_sum(grouped[channel]) for channel in grouped]
    return {
        "two_j": two_j,
        "representative_columns": sorted(by_column),
        "completed_columns": completed,
        "direct_channel_column_count": direct_count,
        "reality_derived_channel_column_count": derived_count,
        "real_channel_sums": real_sums,
    }
