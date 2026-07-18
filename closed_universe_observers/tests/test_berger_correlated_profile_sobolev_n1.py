from fractions import Fraction

from closed_universe_observers.generate_berger_correlated_profile_sobolev_n1 import angular_term_ledger, build


def test_exact_angular_reduction_has_twenty_one_interval_terms_per_polarization():
    assert len(angular_term_ledger("axial")) == 21
    assert len(angular_term_ledger("transverse")) == 21


def test_correlated_bounds_strictly_improve_triangle_bounds_but_are_not_small():
    value = build()
    for row in value["polarization_bounds"]:
        assert Fraction(row["tail_L2_upper_after_two_j1024"]) < Fraction(row["prior_triangle_tail_upper"])
        assert Fraction(row["tail_L2_upper_after_two_j1024"]) > 1
        assert row["strictly_improves_prior_triangle_bound"] is True
        assert row["small_tail_certified"] is False


def test_radial_refinement_mutation_is_detected():
    assert all(row["detected"] for row in build()["mutation_results"])


def test_true_tail_full_image_and_response_remain_fail_closed():
    flags = build()["flags"]
    assert flags["VALIDATED_CORRELATED_CLOCK_UNIFORM_DELTA1_NORM_EXPORTED"] is True
    assert flags["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_UPPER_BOUND_EXPORTED"] is True
    assert flags["CURRENT_CORRELATED_N1_BOUND_CERTIFIES_SMALL_TAIL"] is False
    assert flags["TRUE_TAIL_OBSTRUCTED"] is False
    assert flags["COMPLETE_LOW_MODE_PROJECTION_EXPORTED"] is False
    assert flags["FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED"] is False
    assert flags["DETECTOR_RESPONSE_EVALUATED"] is False
