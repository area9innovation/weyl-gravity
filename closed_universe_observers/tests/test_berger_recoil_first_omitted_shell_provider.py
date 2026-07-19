from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_recoil_first_omitted_shell_provider import (
    build,
)


@pytest.fixture(scope="module")
def certificate():
    return build()


def test_direct_carrier_overlap_is_exact_and_exact_t_stream_stays_unidentified(certificate):
    crosswalk = certificate["carrier_crosswalk"]
    assert crosswalk["detector_generator_source_hash_matches_import"]
    assert crosswalk["cross_window_generator_source_hash_matches_import"]
    assert crosswalk["kernel_generator_source_hash_matches_import"]
    assert (
        crosswalk["hashed_exact_T_two_j138_stream_identification_status"]
        == "NO_CERTIFIED_MAP"
    )


def test_two_j5_detector_and_kernel_provider_rows_are_complete(certificate):
    detector = certificate["detector_provider_extension"]
    assert detector["two_j"] == 5
    assert {row["detector_id"] for row in detector["detectors"]} == {"D0", "D1"}
    assert all(row["dimension"] == 6 for row in detector["detectors"])
    blocks = certificate["kernel_provider_extension"]["blocks"]
    assert {(row["family"], row["form_degree"]) for row in blocks} == {
        ("Maxwell", 0),
        ("Maxwell", 1),
        ("massive_two_form", 0),
        ("massive_two_form", 1),
        ("massive_two_form", 2),
    }
    assert all(row["recurrence_defect_count_through_order4"] == 0 for row in blocks)


def test_cross_window_tail_is_distinct_and_feedback_remains_open(certificate):
    detector = certificate["detector_provider_extension"]
    d1 = next(row for row in detector["detectors"] if row["detector_id"] == "D1")
    cross = detector["D1_on_h0_cross_window_remainder"]
    assert Fraction(cross["tau_max"]) == Fraction(3, 8)
    assert cross != d1["corresponding_window_remainder"]
    assert all(row["detected"] for row in certificate["mutation_results"])
    assert not certificate["flags"]["TWO_J5_FEEDBACK_CHANNELS_EVALUATED"]
    assert not certificate["flags"]["COMPLETE_ALL_SHELL_PROVIDER_EXPORTED"]


def test_tail_radii_are_derived_from_certified_physical_time_supports(certificate):
    rows = {
        row["window"]: row for row in certificate["support_audit"]["rows"]
    }
    assert {name: Fraction(row["derived_tau_max"]) for name, row in rows.items()} == {
        "D0_on_h0": Fraction(1, 8),
        "D1_on_h1": Fraction(5, 24),
        "D1_on_h0": Fraction(3, 8),
    }
    assert all(row["matches_remainder_input"] for row in rows.values())
