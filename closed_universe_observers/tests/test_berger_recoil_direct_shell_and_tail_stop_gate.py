from fractions import Fraction

import pytest

from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
    compose_four_recoil_tail_radii,
    evaluate_four_recoil_stream_stop,
)
from closed_universe_observers.generate_berger_recoil_direct_shell_and_tail_stop_gate import build


def test_generated_gate_is_fail_closed_and_contiguous():
    value = build()
    assert set(value["direct_shell_provider"]["contiguous_carrier_cutoffs"].values()) == {6}
    assert value["direct_shell_provider"]["hashed_exact_T_two_j138_stream_identification_status"] == "NO_CERTIFIED_MAP"
    assert value["four_stream_stop_gate"]["certificate_derived_open_fixture"]["lifecycle_status"] == "OPEN"
    assert value["four_stream_stop_gate"]["synthetic_rank_two_stop_fixture"]["lifecycle_status"] == "CERTIFIED"
    assert not value["flags"]["TWO_J6_FEEDBACK_CHANNELS_EVALUATED"]
    assert not value["flags"]["FOUR_PHYSICAL_RECOIL_INTERVALS_EXPORTED"]


def test_tail_formula_keeps_outer_source_coupling_linear_absolute():
    radii = compose_four_recoil_tail_radii(
        detector_dual_norms={0: Fraction(2), 1: Fraction(3)},
        maxwell_tail_uppers={0: Fraction(5), 1: Fraction(7)},
        massive_tail_coefficients={0: (Fraction(11), Fraction(13)), 1: (Fraction(17), Fraction(19))},
        masses={0: Fraction(1), 1: Fraction(2)},
        couplings={0: Fraction(-2), 1: Fraction(3)},
    )
    common = 4 * (11 + 13) + 9 * (Fraction(17, 4) + Fraction(19, 2))
    assert radii[(0, 0)] == 2 * 2 * 5 * common
    assert radii[(0, 1)] == 3 * 2 * 7 * common


def test_stop_gate_rejects_missing_stream_and_goal():
    with pytest.raises(ValueError, match="all four"):
        evaluate_four_recoil_stream_stop(
            partial_intervals={(0, 0): RationalInterval.point(0)},
            tail_radii={(0, 0): Fraction(0)},
            goal={"type": "rank_two"},
        )
    full = {(a, b): RationalInterval.point(0) for a in (0, 1) for b in (0, 1)}
    radii = {(a, b): Fraction(0) for a in (0, 1) for b in (0, 1)}
    with pytest.raises(ValueError, match="unsupported or missing"):
        evaluate_four_recoil_stream_stop(partial_intervals=full, tail_radii=radii, goal={})
