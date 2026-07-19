from fractions import Fraction

from closed_universe_observers.generate_berger_cross_window_detector_advanced_remainder import (
    build,
)


def test_cross_window_remainder_uses_the_full_d1_to_h0_separation():
    value = build()
    assert value["cross_window"]["strict_advanced_support_separation"]
    assert value["cross_window"]["kernel_tau_interval"] == ["7/24", "3/8"]
    assert value["cross_window"]["T_interval"] == ["5/16", "17/48"]
    assert value["flags"][
        "D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED"
    ]
    for row in value["mode_remainders"]:
        remainder = row["uniform_entire_series_remainders"]
        assert Fraction(remainder["tau_max"]) == Fraction(3, 8)
        assert Fraction(remainder["spatial_cosine_entry_remainder_upper"]) >= 0
        assert Fraction(remainder["temporal_sine_entry_remainder_upper"]) >= 0
