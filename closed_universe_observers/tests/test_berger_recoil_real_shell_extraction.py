from copy import deepcopy

import pytest

from closed_universe_observers.berger_recoil_real_shell_extraction import (
    extract_real_channel_column_sum,
    reality_reduced_columns,
)
from closed_universe_observers.generate_berger_recoil_real_shell_extraction import build


def _row(two_j, column, real, imaginary, channel="I_000"):
    def interval(lower, upper):
        return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}
    return {
        "channel_id": channel,
        "two_j": two_j,
        "column": column,
        "partition_count": 2,
        "coefficient_block_interval": {
            "real": interval(*real),
            "imaginary": interval(*imaginary),
        },
    }


def test_odd_shell_pair_correlation_removes_imaginary_part_exactly():
    rows = [
        _row(1, 0, (-2, 3), (-5, 7)),
        _row(1, 1, (-2, 3), (-7, 5)),
    ]
    value = extract_real_channel_column_sum(rows)
    assert value["real_column_sum"] == {"lower": "-4", "upper": "6", "width": "10"}
    assert value["imaginary_column_sum"] == {"lower": "0", "upper": "0", "width": "0"}
    reduced = reality_reduced_columns(rows)
    assert (reduced[0].lower, reduced[0].upper) == (-4, 6)
    assert (reduced[1].lower, reduced[1].upper) == (0, 0)


def test_even_shell_central_self_partner_is_taken_once():
    rows = [
        _row(2, 0, (1, 2), (-3, 4)),
        _row(2, 1, (-5, 6), (-7, 7)),
        _row(2, 2, (1, 2), (-4, 3)),
    ]
    value = extract_real_channel_column_sum(rows)
    assert value["real_column_sum"] == {"lower": "-3", "upper": "10", "width": "13"}
    assert value["self_partner_count"] == 1


def test_partner_rectangle_mutation_fails_closed():
    rows = [
        _row(1, 0, (-2, 3), (-5, 7)),
        _row(1, 1, (-2, 3), (-7, 5)),
    ]
    mutated = deepcopy(rows)
    mutated[1]["coefficient_block_interval"]["real"]["upper"] = "4"
    with pytest.raises(ValueError, match="conjugate carrier rectangles"):
        extract_real_channel_column_sum(mutated)


def test_generated_certificate_keeps_physical_gate_closed():
    value = build()
    assert value["flags"]["COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED"]
    assert len(value["two_j5_real_channel_sums"]) == 8
    assert not value["flags"]["TWO_J6_FEEDBACK_CHANNELS_EVALUATED"]
    assert not value["flags"]["FOUR_PHYSICAL_RECOIL_INTERVALS_EXPORTED"]
