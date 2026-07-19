from fractions import Fraction

from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
)
from closed_universe_observers.berger_recoil_matched_feedback_channel import (
    _integrate_lorentzian_two_form_pairing,
    _reverse_translate_polynomial,
)
from closed_universe_observers.generate_berger_recoil_matched_feedback_channel import (
    build,
)


def _point(value: int) -> ComplexRationalInterval:
    return ComplexRationalInterval.point(value)


def test_reverse_translation_preserves_polynomial_exactly():
    # P(x)=1+2x, so P(3-s)=7-2s.
    translated = _reverse_translate_polynomial([[_point(1)], [_point(2)]], Fraction(3))
    assert translated == [[_point(7)], [_point(-2)]]


def test_lorentzian_two_form_pairing_uses_temporal_minus_sign():
    result = _integrate_lorentzian_two_form_pairing(
        advanced_coefficients=[[_point(1), _point(2)]],
        advanced_remainder_upper=Fraction(0),
        retarded_source_coefficients=[[_point(1), _point(2)]],
        retarded_source_remainder_upper=Fraction(0),
        length=Fraction(1),
        temporal_dimension=1,
    )
    assert result["coefficient_block_interval"]["real"]["lower"] == "3"
    assert result["coefficient_block_interval"]["real"]["upper"] == "3"
    assert result["coefficient_block_interval"]["imaginary"]["lower"] == "0"


def test_two_matched_feedback_channels_are_evaluated_but_fail_closed_on_sign():
    value = build()
    assert [channel["channel_id"] for channel in value["channels"]] == [
        "I_000",
        "I_111",
    ]
    assert all(
        channel["coefficient_block_contains_zero"]
        for channel in value["channels"]
    )
    assert value["flags"]["MASSIVE_ONE_FORM_PHYSICAL_CORRECTION_BOUND"]
    assert not value["flags"]["ALL_EIGHT_ABC_CHANNEL_INTERVALS_EVALUATED"]
    assert not value["flags"]["FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED"]
