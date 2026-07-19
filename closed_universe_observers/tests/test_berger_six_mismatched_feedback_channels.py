from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_six_mismatched_feedback_channels import (
    build,
)


@pytest.fixture(scope="module")
def certificate():
    return build()


def test_four_mismatched_channels_are_exact_support_zeros(certificate):
    value = certificate
    rows = value["causal_support_zero_channels"]
    assert {row["channel_id"] for row in rows} == {
        "I_001", "I_010", "I_011", "I_110"
    }
    assert all(row["causal_support_zero"] for row in rows)
    assert all(
        row["coefficient_block_interval"][part]["width"] == "0"
        for row in rows
        for part in ("real", "imaginary")
    )


def test_two_allowed_mismatched_channels_contract_but_remain_zero_containing(certificate):
    value = certificate
    rails = value["causally_allowed_partition_rails"]
    assert set(rails) == {"I_100", "I_101"}
    assert rails["I_100"][-1]["cross_window_detector_remainder_applied"]
    assert rails["I_101"][-1]["cross_window_retarded_propagation"]
    for rows in rails.values():
        assert [row["partition_count"] for row in rows] == [2, 4, 8]
        assert all(row["coefficient_block_contains_zero"] for row in rows)
        for part in ("real", "imaginary"):
            widths = [
                Fraction(row["coefficient_block_interval"][part]["width"])
                for row in rows
            ]
            assert widths[0] > widths[1] > widths[2]


def test_all_eight_finite_blocks_are_evaluated_without_all_shell_promotion(certificate):
    flags = certificate["flags"]
    assert flags["SIX_MISMATCHED_TWO_J0_K0_CHANNELS_EVALUATED"]
    assert flags["ALL_EIGHT_ABC_TWO_J0_K0_INTERVALS_EVALUATED"]
    assert not flags["ALL_EIGHT_ABC_ALL_SHELL_INTERVALS_EVALUATED"]
    assert not flags["FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED"]
