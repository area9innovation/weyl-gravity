from fractions import Fraction

from closed_universe_observers.generate_berger_clock_uniform_profile_sobolev_n1 import _bump_derivative_bounds, _operator_audit, build


def test_operator_matches_certified_coordinate_and_exact_form_rail():
    audit = _operator_audit()
    assert audit["scalar_coordinate_defect_count"] == 0
    assert audit["d_Delta_equals_Delta_d_defect_count"] == 0


def test_flat_bump_q_derivative_bounds_are_exact_declared_rationals():
    assert _bump_derivative_bounds() == [Fraction(1), Fraction(3, 2), Fraction(675, 32)]


def test_both_polarizations_have_finite_but_not_small_n1_tail_bounds():
    value = build()
    assert len(value["polarization_bounds"]) == 2
    for row in value["polarization_bounds"]:
        assert Fraction(row["clock_uniform_Delta1_profile_L2_norm_upper"]) > 0
        assert Fraction(row["tail_L2_upper_after_two_j1024"]) > 1
        assert row["small_tail_certified"] is False


def test_fail_closed_full_image_and_response_flags():
    value = build()
    assert all(row["detected"] for row in value["mutation_results"])
    flags = value["flags"]
    assert flags["CLOCK_UNIFORM_POLARIZED_DELTA1_PROFILE_NORM_EXPORTED"] is True
    assert flags["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_UPPER_BOUND_EXPORTED"] is True
    assert flags["CURRENT_N1_BOUND_CERTIFIES_SMALL_TAIL"] is False
    assert flags["COMPLETE_LOW_MODE_PROJECTION_EXPORTED"] is False
    assert flags["FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED"] is False
    assert flags["DETECTOR_RESPONSE_EVALUATED"] is False
