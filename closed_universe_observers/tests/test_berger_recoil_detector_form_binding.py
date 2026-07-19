import json
from fractions import Fraction

import pytest

from closed_universe_observers.berger_recoil_detector_form_binding import (
    _cosine_time_derivative_tail,
    apply_spacetime_dhat1_to_detector_advanced_maxwell,
    assemble_detector_advanced_maxwell_polynomial,
)
from closed_universe_observers.generate_berger_recoil_detector_form_binding import (
    DEPENDENCIES,
    build,
)


@pytest.fixture(scope="module")
def detector_certificate():
    return json.loads(DEPENDENCIES["detector_image"].read_text())


def test_component_major_detector_polynomial_is_assembled(detector_certificate):
    value = assemble_detector_advanced_maxwell_polynomial(
        detector_certificate, detector="D0", two_j=0, column=0
    )
    assert value["dimension"] == 4
    assert value["basis_order"].startswith("[temporal scalar")
    assert all(
        coefficient[0]["real"]["lower"] == "0"
        for coefficient in value["polynomial_coefficients"]
    )
    assert any(
        coefficient[3]["real"]["lower"] != "0"
        or coefficient[3]["imaginary"]["lower"] != "0"
        for coefficient in value["polynomial_coefficients"]
    )


def test_dhat1_uses_physical_time_minus_T_derivative(detector_certificate):
    assembled = assemble_detector_advanced_maxwell_polynomial(
        detector_certificate, detector="D0", two_j=0, column=0
    )
    applied = apply_spacetime_dhat1_to_detector_advanced_maxwell(
        detector_certificate, detector="D0", two_j=0, column=0
    )
    # theta3 occupies input row 3 and the corresponding dt-wedge-theta3 output row 2.
    input_t2 = assembled["polynomial_coefficients"][2][3]
    output_t1 = applied["polynomial_coefficients"][1][2]
    assert Fraction(output_t1["real"]["lower"]) == -2 * Fraction(input_t2["real"]["upper"])
    assert Fraction(output_t1["real"]["upper"]) == -2 * Fraction(input_t2["real"]["lower"])
    assert applied["physical_time_derivative"] == "partial_t=-partial_T"


def test_all_finite_dimensions_and_columns_bind(detector_certificate):
    for detector in ("D0", "D1"):
        for two_j in range(5):
            for column in range(two_j + 1):
                value = apply_spacetime_dhat1_to_detector_advanced_maxwell(
                    detector_certificate,
                    detector=detector,
                    two_j=two_j,
                    column=column,
                    radical_bits=32,
                )
                assert value["input_dimension"] == 4 * (two_j + 1)
                assert value["output_dimension"] == 6 * (two_j + 1)
                assert Fraction(value["remainder_audit"]["uniform_output_vector_remainder_upper"]) >= 0


def test_derivative_tail_formula_and_domain_fail_closed():
    tail = _cosine_time_derivative_tail(
        operator_norm=Fraction(2), tau_max=Fraction(1, 4), series_order=1
    )
    assert tail > 0
    with pytest.raises(ValueError, match="not contractive"):
        _cosine_time_derivative_tail(
            operator_norm=Fraction(1000), tau_max=Fraction(1), series_order=0
        )


def test_binding_scope_fails_closed(detector_certificate):
    with pytest.raises(ValueError, match="column"):
        assemble_detector_advanced_maxwell_polynomial(
            detector_certificate, detector="D0", two_j=0, column=1
        )
    with pytest.raises(ValueError, match="only"):
        apply_spacetime_dhat1_to_detector_advanced_maxwell(
            detector_certificate, detector="D0", two_j=5, column=0
        )


def test_certificate_stops_before_massive_preparation():
    value = build()
    assert value["flags"]["EXACT_SPACETIME_DHAT1_APPLIED_TO_DETECTOR_IMAGE"] is True
    assert value["flags"]["PHYSICAL_TIME_DERIVATIVE_TAIL_BOUND_EXPORTED"] is True
    assert value["flags"]["ADVANCED_MASSIVE_TWO_FORM_IMAGE_EVALUATED"] is False
