import json
from fractions import Fraction
from closed_universe_observers.generate_berger_adaptive_clock_weighted_polarization_stream import CERTIFICATE,POWERS
VALUE=json.loads(CERTIFICATE.read_text())
def test_adaptive_polarization_coverage():
 assert VALUE["coverage"]=={"detector_component_entry_count":86736,"detector_component_scalar_term_application_count":231018,"clock_power_interval_count":780624};assert len(VALUE["mode_summaries"])==139
def test_direct_p12_audit_and_hashes():
 assert VALUE["direct_p12_compatibility_audit"]=={"clock_power":12,"audited_two_j_maximum":4,"interval_comparison_count":330,"nonoverlap_defect_count":0};assert len(VALUE["canonical_full_stream_sha256"])==64
def test_widths_and_green_claim():
 assert set(map(int,VALUE["maximum_interval_width_by_clock_power"]))==set(POWERS);assert all(Fraction(x)>0 for x in VALUE["maximum_interval_width_by_clock_power"].values());assert VALUE["flags"]["TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED"] is False
