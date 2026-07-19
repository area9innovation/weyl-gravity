from fractions import Fraction

from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
)
from closed_universe_observers.berger_recoil_partitioned_feedback_channel import (
    _causal_convolution_cell_enclosures,
)
from closed_universe_observers.generate_berger_recoil_partitioned_matched_feedback import (
    build,
)


def _point(value: int) -> ComplexRationalInterval:
    return ComplexRationalInterval.point(value)


def _constant_kernel() -> dict[str, object]:
    return {
        "label": "constant_one",
        "coefficient_matrices": [[[_point(1)]]],
        "uniform_remainder_upper": Fraction(0),
    }


def test_partitioned_causal_convolution_orients_diagonal_triangles():
    source = [[_point(1)], [_point(1)]]
    retarded = _causal_convolution_cell_enclosures(
        source_cells=source,
        kernel_stage=_constant_kernel(),
        cell_width=Fraction(1, 2),
        orientation="retarded",
    )
    advanced = _causal_convolution_cell_enclosures(
        source_cells=source,
        kernel_stage=_constant_kernel(),
        cell_width=Fraction(1, 2),
        orientation="advanced",
    )
    assert retarded[0][0].real.serialize() == {
        "lower": "0", "upper": "1/2", "width": "1/2"
    }
    assert retarded[1][0].real.serialize() == {
        "lower": "1/2", "upper": "1", "width": "1/2"
    }
    assert advanced[0][0].real == retarded[1][0].real
    assert advanced[1][0].real == retarded[0][0].real


def test_partitioned_matched_feedback_contracts_but_remains_fail_closed():
    value = build()
    assert value["flags"][
        "ALL_MATCHED_FEEDBACK_SWITCH_OCCURRENCES_CELL_PARTITIONED"
    ]
    assert value["flags"][
        "MATCHED_FEEDBACK_WIDTHS_STRICTLY_CONTRACT_2_TO_4_TO_8"
    ]
    assert value["flags"]["PARTITION8_WIDTHS_STRICTLY_BELOW_COARSE_HULLS"]
    assert not value["flags"]["PARTITION8_MATCHED_FEEDBACK_INTERVALS_EXCLUDE_ZERO"]
    assert not value["flags"]["ALL_EIGHT_ABC_CHANNEL_INTERVALS_EVALUATED"]
    for rows in value["partition_rails"].values():
        assert [row["partition_count"] for row in rows] == [2, 4, 8]
        assert all(row["coefficient_block_contains_zero"] for row in rows)
        for component in ("real", "imaginary"):
            widths = [
                Fraction(row["coefficient_block_interval"][component]["width"])
                for row in rows
            ]
            assert widths[0] > widths[1] > widths[2]
