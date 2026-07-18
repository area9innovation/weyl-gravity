import json
from fractions import Fraction
from closed_universe_observers.generate_berger_adaptive_clock_weighted_scalar_stream import CLOCK_POWERS,certificate_path
def test_all_adaptive_shards_are_typed_and_complete():
 for p in CLOCK_POWERS:
  v=json.loads(certificate_path(p).read_text());assert v["clock_weight"]["power"]==p;assert v["coverage"]["reconstructed_full_diagonal_count"]==9870
def test_top_intervals_are_positive_and_narrow():
 for p in CLOCK_POWERS:
  x=json.loads(certificate_path(p).read_text())["modes"][139]["unique_diagonal"][69]["clock_weighted_local_amplitude"];lo,hi=Fraction(x["lower"]),Fraction(x["upper"]);assert 0<lo<hi<1;assert hi-lo<Fraction(1,1000)
def test_green_claims_remain_open():
 assert all(json.loads(certificate_path(p).read_text())["flags"]["TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED"] is False for p in CLOCK_POWERS)
