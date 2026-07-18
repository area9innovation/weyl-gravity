import json

import pytest

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import CERTIFICATE, build


@pytest.fixture(scope="module")
def value():
    return build()


def test_generated_certificate_is_current(value):
    assert json.loads(CERTIFICATE.read_text()) == value


def test_temporal_derivative_is_green_weighted(value):
    assert value["coderivative_and_integration_by_parts"]["boundary_term_zero"]
    assert value["flags"]["TEMPORAL_CODERIVATIVE_GREEN_WEIGHTED"]
    assert all(mode["spatial_one_form_advanced_polynomial"] for row in value["detectors"] for mode in row["modes"])


def test_spatial_tail_remains_fail_closed(value):
    assert value["flags"]["FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED"]
    assert not value["flags"]["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED"]
    assert not value["flags"]["FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED"]


def test_boundary_flatness_mutation_is_rejected():
    with pytest.raises(AssertionError, match="boundary term"):
        build(omit_integration_by_parts=True)
