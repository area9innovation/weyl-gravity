import json
from fractions import Fraction

import pytest

from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
    RationalInterval,
)
from closed_universe_observers.berger_recoil_massive_diagonal_preparation import (
    evaluate_switched_detector_diagonal_massive_advanced_image_at_support_left,
    translate_vector_polynomial,
)
from closed_universe_observers.generate_berger_recoil_massive_diagonal_preparation import DEPENDENCIES, build


@pytest.fixture(scope="module")
def certificates():
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def test_exact_vector_polynomial_translation():
    value = translate_vector_polynomial(
        coefficients=[[ComplexRationalInterval.point(1)], [ComplexRationalInterval.point(2)]],
        shift=Fraction(1, 3),
    )
    assert value["polynomial_coefficients"][0][0]["real"]["lower"] == "5/3"
    assert value["polynomial_coefficients"][1][0]["real"]["lower"] == "2"


def _evaluate(certificates, detector, two_j, column, mass=None):
    return evaluate_switched_detector_diagonal_massive_advanced_image_at_support_left(
        detector_image_certificate=certificates["detector_image"],
        detector_profile_certificate=certificates["profiles"],
        switch_certificate=certificates["switches"],
        moment_certificate=certificates["moments"],
        exact_kernel_certificate=certificates["kernels"],
        detector=detector,
        two_j=two_j,
        column=column,
        mass_squared_interval=mass or RationalInterval(Fraction(1), Fraction(2)),
        radical_bits=32,
    )


def test_both_physical_support_coordinate_bridges_and_odd_kernel_powers(certificates):
    d0 = _evaluate(certificates, "D0", 0, 0)
    d1 = _evaluate(certificates, "D1", 0, 0)
    assert d0["support_physical_time"] == ["7/48", "3/16"]
    assert d1["support_physical_time"] == ["5/16", "7/16"]
    assert d0["detector_T_to_source_y_shift"] == "1/16"
    assert d1["detector_T_to_source_y_shift"] == "1/16"
    assert d0["kernel_nonzero_tau_powers"] == [1, 3, 5, 7, 9, 11]


def test_finite_massive_image_has_correct_dimension_and_remainder(certificates):
    value = _evaluate(certificates, "D1", 2, 1)
    assert len(value["support_left_diagonal_massive_wave_image"]) == 18
    assert Fraction(value["image_uniform_remainder_upper"]) >= 0
    assert Fraction(value["kernel_uniform_remainder_upper"]) > 0


def test_mass_domain_and_mode_scope_fail_closed(certificates):
    with pytest.raises(ValueError, match="strictly positive"):
        _evaluate(certificates, "D0", 0, 0, RationalInterval(Fraction(0), Fraction(1)))
    with pytest.raises(ValueError, match="only"):
        _evaluate(certificates, "D0", 5, 0)


def test_certificate_stops_before_physical_proca_and_cauchy_gates():
    value = build()
    assert value["flags"]["DIAGONAL_MASSIVE_DEGREE_TWO_ADVANCED_IMAGE_AT_SUPPORT_LEFT_EXPORTED"] is True
    assert value["flags"]["PHYSICAL_PROCA_TWO_FORM_GREEN_CORRECTION_EXPORTED"] is False
    assert value["flags"]["EMITTER_CAUCHY_MOMENTUM_EXPORTED"] is False
