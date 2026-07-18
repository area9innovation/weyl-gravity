from fractions import Fraction

from closed_universe_observers.generate_berger_clock_microphase_tail_envelope import build


def test_second_derivative_envelope_is_positive_and_uniform():
    value = build()
    envelope = value["clock_envelope"]
    assert Fraction(envelope["weighted_second_derivative_L1_upper"]) > 0
    assert Fraction(envelope["normalized_envelope_constant_C_upper"]) > 0
    assert value["flags"]["UNIFORM_FIXED_VECTOR_CLOCK_MICROPHASE_ENVELOPE_EXPORTED"] is True


def test_frozen_profile_cutoff_is_minimal_for_this_bound():
    analysis = build()["cutoff_analysis"]
    assert analysis["first_sufficient_frozen_profile_retained_max_two_j"] == 3421
    assert not any(row["frozen_profile_tail_below_one"] for row in analysis["current_cutoff_rows"])
    assert all(row["frozen_profile_tail_below_one"] for row in analysis["first_sufficient_rows"])
    assert not all(row["frozen_profile_tail_below_one"] for row in analysis["minimality_witness_at_previous_cutoff"])


def test_moving_profile_and_full_image_remain_fail_closed():
    value = build()
    assert value["cutoff_analysis"]["moving_profile_status"] == "NO_CERTIFIED_MAP"
    flags = value["flags"]
    assert flags["MOVING_DETECTOR_PROFILE_CLOCK_DERIVATIVE_BOUND_EXPORTED"] is False
    assert flags["VALIDATED_PHYSICAL_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED"] is False
    assert flags["COMPLETE_LOW_MODE_PROJECTION_EXPORTED"] is False
    assert flags["FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED"] is False
    assert flags["DETECTOR_RESPONSE_EVALUATED"] is False


def test_total_variation_mutation_is_detected():
    assert all(row["detected"] for row in build()["mutation_results"])
