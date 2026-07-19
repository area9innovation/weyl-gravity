import json
from fractions import Fraction

import pytest

from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.berger_recoil_switch_intervals import emitter_switch_interval
from closed_universe_observers.generate_berger_recoil_switch_interval_provider import build


def _inputs():
    with open("closed_universe_observers/certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json") as stream:
        switches = json.load(stream)
    with open("closed_universe_observers/certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json") as stream:
        moments = json.load(stream)
    return switches, moments


def test_centers_have_positive_value_and_zero_derivative():
    switches, moments = _inputs()
    for switch_id, center in (("h_0", Fraction(1, 6)), ("h_1", Fraction(3, 8))):
        value = emitter_switch_interval(switches, moments, switch_id=switch_id, physical_time_interval=RationalInterval.point(center))
        assert Fraction(value["value"]["lower"]) > 0
        assert value["physical_time_derivative"]["lower"] == "0"
        assert value["physical_time_derivative"]["upper"] == "0"


def test_support_cells_and_structural_zeros_are_fail_closed():
    switches, moments = _inputs()
    whole = emitter_switch_interval(switches, moments, switch_id="h_0", physical_time_interval=RationalInterval(Fraction(7, 48), Fraction(3, 16)))
    assert whole["value"]["lower"] == "0"
    assert Fraction(whole["physical_time_derivative"]["lower"]) < 0 < Fraction(whole["physical_time_derivative"]["upper"])
    outside = emitter_switch_interval(switches, moments, switch_id="h_0", physical_time_interval=RationalInterval(Fraction(1, 4), Fraction(1, 3)))
    assert outside["structural_zero"] is True
    with pytest.raises(ValueError, match="switch_id"):
        emitter_switch_interval(switches, moments, switch_id="h_2", physical_time_interval=RationalInterval.point(0))


def test_certificate_keeps_physical_channel_open():
    value = build()
    assert value["flags"]["NORMALIZED_SWITCH_AND_TIME_DERIVATIVE_INTERVAL_PROVIDER_EXPORTED"] is True
    assert value["flags"]["SWITCH_KERNEL_CONVOLUTION_BOUND"] is False
