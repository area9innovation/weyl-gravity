import json

import pytest

from closed_universe_observers.berger_recoil_interval_stream import detector_profile_coefficient_interval
from closed_universe_observers.generate_berger_recoil_finite_detector_coefficient_provider import DEPENDENCIES, build


def _certificate():
    return json.loads(DEPENDENCIES["detector_image"].read_text())


def test_nonzero_finite_coefficient_and_remainder_are_returned():
    value = detector_profile_coefficient_interval(
        _certificate(), detector="D0", two_j=0,
        block="spatial_one_form_advanced_polynomial", coframe_component=3,
        row=0, column=0, t_power=0,
    )
    assert value["structural_zero"] is False
    assert value["real"]["upper"].startswith("-")
    assert "spatial_cosine_entry_remainder_upper" in value["uniform_entire_series_remainders"]


def test_omitted_valid_entry_is_explicit_structural_zero():
    value = detector_profile_coefficient_interval(
        _certificate(), detector="D0", two_j=0,
        block="temporal_scalar_advanced_polynomial", coframe_component=None,
        row=0, column=0, t_power=0,
    )
    assert value["structural_zero"] is True
    assert value["real"] == {"lower": "0", "upper": "0", "width": "0"}


def test_out_of_scope_shell_is_rejected():
    with pytest.raises(ValueError, match="only 0<=two_j<=4"):
        detector_profile_coefficient_interval(
            _certificate(), detector="D0", two_j=5,
            block="spatial_one_form_advanced_polynomial", coframe_component=1,
            row=0, column=0, t_power=0,
        )


def test_certificate_keeps_complete_provider_fail_closed():
    value = build()
    assert value["flags"]["FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED"] is True
    assert value["flags"]["COMPLETE_DETECTOR_COEFFICIENT_PROVIDER_EXPORTED"] is False
