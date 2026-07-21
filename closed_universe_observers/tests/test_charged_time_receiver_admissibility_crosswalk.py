from closed_universe_observers.generate_charged_time_receiver_admissibility_crosswalk import build,classify
def test_failure_classification_is_typed():
 assert classify(exact=True)=="ZERO_RESPONSE" and classify(nonradical=False)=="RADICAL_UNDEFINED_RESPONSE"
 assert classify(denominator=False)=="UNDEFINED_ZERO_DENOMINATOR" and classify(crosswalk=False)=="NO_CERTIFIED_MAP"
 assert classify(retarded=False)=="CAUSAL_INTERPRETATION_LOST" and classify(clock=False)=="CLOCK_REMOVED_OBSTRUCTED"
def test_positive_control_and_interface():
 v,i=build();assert classify()=="CERTIFIED_ADMISSIBLE" and len(i["receiver_required_fields"])>=10 and len(i["crosswalk_required_fields"])>=8
 assert v["flags"]["RECEIVER_ADMISSIBILITY_CONTRACT_CERTIFIED"] and not v["flags"]["ACTION_DERIVED_NONZERO_RECEIVER_CERTIFIED"]
def test_census_is_complete_and_fail_closed():
 v,_=build();c=v["census_completeness"];assert c["complete"] and c["discovered_count"]==c["classified_count"]==5 and not c["unclassified_ids"]
 assert not any(r["physical_receiver_promoted"] for r in v["observer_carrier_census"])
