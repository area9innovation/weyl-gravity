import json
from fractions import Fraction
from closed_universe_observers.generate_berger_high_clock_power_moment_rail import CERTIFICATE
VALUE=json.loads(CERTIFICATE.read_text())
def test_complete_even_power_rail():
 assert [2*r["k"] for r in VALUE["normalized_clock_even_moments"]]==list(range(0,29,2))
def test_low_rows_overlap_and_high_rows_are_positive():
 assert all(r["overlap"] for r in VALUE["low_order_compatibility_audit"])
 for row in VALUE["normalized_clock_even_moments"][7:]:
  x=row["normalized_even_moment"];assert 0<Fraction(x["lower"])<Fraction(x["upper"])
def test_downstream_claims_stay_open():
 assert VALUE["flags"]["ADAPTIVE_EXTERNAL_CLOCK_WEIGHTED_SCALAR_STREAMS_P12_TO_P28_EXPORTED"] is False
