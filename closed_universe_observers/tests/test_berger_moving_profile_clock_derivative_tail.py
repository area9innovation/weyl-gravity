from fractions import Fraction
from closed_universe_observers.generate_berger_moving_profile_clock_derivative_tail import build

def test_moving_profile_derivative_channels_are_nonzero():
    for row in build()["calculation"]["polarization_bounds"]:
        assert all(Fraction(item["normalized_Delta1_amplitude_derivative_L2_norm_upper"])>0 for item in row["amplitude_derivatives"])

def test_sufficient_cutoff_is_minimal_for_bound():
    value=build()["calculation"]
    assert all(Fraction(v)<1 for v in value["sufficient_cutoff_tail_uppers"].values())
    assert not all(Fraction(v)<1 for v in value["previous_cutoff_tail_uppers"].values())

def test_projection_and_response_remain_open():
    flags=build()["flags"]
    assert flags["COMPLETE_LOW_MODE_PROJECTION_EXPORTED"] is False
    assert flags["FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED"] is False
    assert flags["DETECTOR_RESPONSE_EVALUATED"] is False
