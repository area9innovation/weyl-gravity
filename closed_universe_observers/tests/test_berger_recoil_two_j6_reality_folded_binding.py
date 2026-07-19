from copy import deepcopy

import pytest

from closed_universe_observers.berger_recoil_reality_folded_shell import (
    complete_reality_folded_shell,
)


def _interval(lower, upper):
    return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}


def _row(column, real, imaginary):
    return {
        "channel_id": "I_000",
        "two_j": 2,
        "column": column,
        "partition_count": 2,
        "coefficient_block_interval": {
            "real": _interval(*real),
            "imaginary": _interval(*imaginary),
        },
    }


def test_even_shell_is_completed_from_representatives_only():
    representatives = [
        {"two_j": 2, "column": 0, "partition_count": 2, "channels": [_row(0, (-2, 3), (-5, 7))]},
        {"two_j": 2, "column": 1, "partition_count": 2, "channels": [_row(1, (-4, 6), (-8, 8))]},
    ]
    value = complete_reality_folded_shell(two_j=2, representative_columns=representatives)
    assert value["direct_channel_column_count"] == 2
    assert value["reality_derived_channel_column_count"] == 1
    partner = value["completed_columns"][2]["channels"][0]
    assert partner["reality_source_column"] == 0
    assert partner["coefficient_block_interval"]["imaginary"] == _interval(-7, 5)
    assert value["real_channel_sums"][0]["real_column_sum"] == _interval(-8, 12)


def test_missing_representative_fails_closed():
    with pytest.raises(ValueError, match="complete and unique"):
        complete_reality_folded_shell(
            two_j=2,
            representative_columns=[
                {"two_j": 2, "column": 0, "partition_count": 2, "channels": [_row(0, (-2, 3), (-5, 7))]}
            ],
        )


def test_central_non_self_conjugate_rectangle_fails_closed():
    representatives = [
        {"two_j": 2, "column": 0, "partition_count": 2, "channels": [_row(0, (-2, 3), (-5, 7))]},
        {"two_j": 2, "column": 1, "partition_count": 2, "channels": [_row(1, (-4, 6), (-8, 9))]},
    ]
    with pytest.raises(ValueError, match="central self-partner"):
        complete_reality_folded_shell(two_j=2, representative_columns=deepcopy(representatives))
