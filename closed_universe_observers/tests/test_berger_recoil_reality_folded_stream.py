from fractions import Fraction

import pytest

from closed_universe_observers import berger_recoil_reality_folded_stream as stream
from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.berger_recoil_reality_folded_shell import (
    complete_reality_folded_shell,
)


CHANNELS = [
    f"I_{detector}{source}{feedback}"
    for detector in (0, 1)
    for source in (0, 1)
    for feedback in (0, 1)
]
FAKE_CARRIERS = {
    "cutoff": 5,
    "detector_image": {},
    "cross_window_remainder": {},
    "exact_kernel": {},
}


def _interval(lower, upper=None):
    upper = lower if upper is None else upper
    return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}


def _representative_rows(two_j, column):
    return [
        {
            "channel_id": channel,
            "two_j": two_j,
            "column": column,
            "partition_count": 2,
            "coefficient_block_interval": {
                "real": _interval(column + 1),
                "imaginary": _interval(0 if column == two_j - column else column + 2),
            },
        }
        for channel in CHANNELS
    ]


def _folded(two_j):
    return complete_reality_folded_shell(
        two_j=two_j,
        representative_columns=[
            {
                "two_j": two_j,
                "column": column,
                "partition_count": 2,
                "channels": _representative_rows(two_j, column),
            }
            for column in range(two_j // 2 + 1)
        ],
    )


def test_one_shell_adapter_evaluates_only_reality_representatives(monkeypatch):
    monkeypatch.setattr(stream, "_carrier_cutoff", lambda carriers: carriers["cutoff"])
    monkeypatch.setattr(
        stream,
        "build_direct_finite_shell_payload",
        lambda **kwargs: {"two_j": kwargs["two_j"], "payload_sha256": "fixture"},
    )
    monkeypatch.setattr(
        stream,
        "bind_direct_finite_shell_payload",
        lambda **kwargs: {"cutoff": kwargs["shell_payload"]["two_j"]},
    )
    calls = []

    def evaluator(two_j, column, carriers):
        calls.append((two_j, column, carriers["cutoff"]))
        return _representative_rows(two_j, column)

    result = stream.evaluate_reality_folded_feedback_shell(
        two_j=6,
        carriers=FAKE_CARRIERS,
        moment_certificate={},
        detector_profile_certificate={},
        switch_certificate={},
        spectral_certificate={},
        mass_squared_intervals={0: RationalInterval.point(1), 1: RationalInterval.point(1)},
        partition_count=2,
        radical_bits=80,
        outward_bits=96,
        representative_evaluator=evaluator,
    )
    assert calls == [(6, column, 6) for column in range(4)]
    assert result["folded_shell"]["direct_channel_column_count"] == 32
    assert result["folded_shell"]["reality_derived_channel_column_count"] == 24
    assert result["hashed_exact_T_stream_identification_status"] == "NO_CERTIFIED_MAP"


def test_one_shell_adapter_rejects_incomplete_representative(monkeypatch):
    monkeypatch.setattr(stream, "_carrier_cutoff", lambda carriers: carriers["cutoff"])
    monkeypatch.setattr(
        stream,
        "build_direct_finite_shell_payload",
        lambda **kwargs: {"two_j": kwargs["two_j"], "payload_sha256": "fixture"},
    )
    monkeypatch.setattr(
        stream,
        "bind_direct_finite_shell_payload",
        lambda **kwargs: {"cutoff": kwargs["shell_payload"]["two_j"]},
    )
    with pytest.raises(ValueError, match="all eight channels"):
        stream.evaluate_reality_folded_feedback_shell(
            two_j=6,
            carriers=FAKE_CARRIERS,
            moment_certificate={},
            detector_profile_certificate={},
            switch_certificate={},
            spectral_certificate={},
            mass_squared_intervals={0: RationalInterval.point(1), 1: RationalInterval.point(1)},
            partition_count=2,
            radical_bits=80,
            outward_bits=96,
            representative_evaluator=lambda two_j, column, carriers: _representative_rows(two_j, column)[:-1],
        )


def test_reality_folded_shell_aggregates_all_four_entries():
    result = stream.aggregate_reality_folded_shell(
        folded_shell=_folded(2),
        couplings={0: Fraction(1), 1: Fraction(1)},
        inverse_berger_volume=RationalInterval.point(1),
    )
    assert set(result["shell_intervals"]) == {"00", "01", "10", "11"}
    assert set(tuple(row["shell_interval"].values()) for row in result["aggregate_rows"]) == {
        ("24", "24", "0")
    }


def test_reality_folded_shell_rejects_duplicate_completed_column():
    folded = _folded(2)
    folded["completed_columns"][2]["column"] = 1
    with pytest.raises(ValueError, match="every passive column"):
        stream.aggregate_reality_folded_shell(
            folded_shell=folded,
            couplings={0: Fraction(1), 1: Fraction(1)},
            inverse_berger_volume=RationalInterval.point(1),
        )


def test_stream_stops_after_first_certified_shell(monkeypatch):
    monkeypatch.setattr(stream, "_carrier_cutoff", lambda carriers: carriers["cutoff"])

    def shell_evaluator(two_j, carriers):
        assert two_j == carriers["cutoff"] + 1
        return {
            "two_j": two_j,
            "direct_carriers": {"cutoff": two_j},
            "folded_shell": _folded(two_j),
        }

    radii = {
        two_j: {key: Fraction(0) for key in stream.STREAM_KEYS}
        for two_j in (2, 3)
    }
    result = stream.run_reality_folded_shell_stream(
        two_js=[2, 3],
        carriers={"cutoff": 1},
        moment_certificate={},
        detector_profile_certificate={},
        switch_certificate={},
        spectral_certificate={},
        mass_squared_intervals={0: RationalInterval.point(1), 1: RationalInterval.point(1)},
        couplings={0: Fraction(1), 1: Fraction(1)},
        inverse_berger_volume=RationalInterval.point(1),
        tail_radii_by_two_j=radii,
        goal={"type": "entry_nonzero", "target": [0, 0]},
        partition_count=2,
        radical_bits=80,
        outward_bits=96,
        shell_evaluator=shell_evaluator,
    )
    assert result["stopped"] is True
    assert result["stop_two_j"] == 2
    assert result["evaluated_two_js"] == [2]


def test_stream_rejects_noncontiguous_shells_and_missing_tail_data(monkeypatch):
    monkeypatch.setattr(stream, "_carrier_cutoff", lambda carriers: carriers["cutoff"])
    common = dict(
        carriers={"cutoff": 1},
        moment_certificate={},
        detector_profile_certificate={},
        switch_certificate={},
        spectral_certificate={},
        mass_squared_intervals={0: RationalInterval.point(1), 1: RationalInterval.point(1)},
        couplings={0: Fraction(1), 1: Fraction(1)},
        inverse_berger_volume=RationalInterval.point(1),
        goal={"type": "rank_two"},
        partition_count=2,
        radical_bits=80,
        outward_bits=96,
        shell_evaluator=lambda two_j, carriers: {},
    )
    with pytest.raises(ValueError, match="unique and contiguous"):
        stream.run_reality_folded_shell_stream(
            two_js=[2, 4], tail_radii_by_two_j={}, **common
        )
    with pytest.raises(ValueError, match="after every declared shell"):
        stream.run_reality_folded_shell_stream(
            two_js=[2], tail_radii_by_two_j={}, **common
        )
    with pytest.raises(ValueError, match="nonnegative"):
        stream.run_reality_folded_shell_stream(
            two_js=[2],
            tail_radii_by_two_j={
                2: {
                    key: Fraction(-1 if key == (0, 0) else 0)
                    for key in stream.STREAM_KEYS
                }
            },
            **common,
        )
