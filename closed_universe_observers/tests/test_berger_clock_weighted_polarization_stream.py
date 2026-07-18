import json
from fractions import Fraction
import sympy as sp
from closed_universe_observers.generate_berger_clock_weighted_polarization_stream import CERTIFICATE, DEPENDENCIES, POWERS, _fast_complex_interval, polarization_intervals
from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import _complex_interval
from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import _component_rules, axial_scalar_recurrence

VALUE = json.loads(CERTIFICATE.read_text())

def test_generated_certificate_has_the_complete_exhaustive_coverage():
    assert VALUE["result_id"] == "BERGER_CLOCK_WEIGHTED_POLARIZATION_STREAM_TWO_J138"
    assert len(VALUE["mode_summaries"]) == 139

def test_full_detector_prefactored_coverage_and_hashes():
    value=VALUE; coverage=value["coverage"]
    assert coverage["unique_coordinate_recurrence_entry_count"]==57824
    assert coverage["unique_coordinate_scalar_term_count"]==154012
    assert coverage["detector_component_entry_count"]==86736
    assert coverage["detector_component_scalar_term_application_count"]==231018
    assert coverage["clock_power_interval_count"]==520416
    assert len(value["canonical_full_stream_sha256"])==64
    assert all(len(row["canonical_stream_sha256"])==64 for row in value["mode_summaries"])

def test_direct_low_mode_replay_has_no_interval_defect():
    assert VALUE["direct_low_mode_compatibility_audit"]=={"audited_two_j_maximum":4,"interval_comparison_count":1980,"nonoverlap_defect_count":0}

def test_representative_top_mode_entry_reconstructs_quickly():
    streams = {power: json.loads(DEPENDENCIES[f"s{power}"].read_text())["modes"] for power in POWERS}
    intervals, terms = polarization_intervals(streams, "D0", 2, 138, 69, 69)
    assert 1 <= terms <= 4
    assert set(intervals) == set(POWERS)
    assert all(interval[0][0] <= interval[0][1] and interval[1][0] <= interval[1][1] for interval in intervals.values())

def test_fast_signed_square_root_enclosures_match_generic_low_rail():
    for two_j in range(5):
        for rules in _component_rules().values():
            for coordinate, prefactor in rules:
                for row in range(two_j + 1):
                    for column in range(two_j + 1):
                        for term in axial_scalar_recurrence(two_j, row, column, coordinate):
                            coefficient = prefactor * sp.sympify(term["coefficient"])
                            assert _fast_complex_interval(coefficient) == _complex_interval(coefficient)

def test_widths_are_finite_and_green_tail_recoil_stay_open():
    value=VALUE; assert set(map(int,value["maximum_interval_width_by_clock_power"]))==set(POWERS)
    assert all(Fraction(width)>0 for width in value["maximum_interval_width_by_clock_power"].values())
    flags=value["flags"]
    assert flags["DETECTOR_PREFACTORED_POLARIZATION_INTERVAL_STREAM_TWO_J0_TO_138_EXPORTED"] is True
    assert flags["TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED"] is False
    assert flags["GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED"] is False
    assert flags["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
