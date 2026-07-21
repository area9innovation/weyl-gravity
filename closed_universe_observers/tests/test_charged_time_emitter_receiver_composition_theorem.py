from closed_universe_observers.generate_charged_time_emitter_receiver_composition_theorem import algebra_audit,build,orientation_audit
def test_matched_composition_and_reciprocity():
 a=algebra_audit();assert a["composition_exact"] and a["reciprocity_exact"] and a["composition_holonomy"]=="1"
def test_orientation_and_path_mutations():
 assert orientation_audit(-1,1,1)["edge_12_factor"]=="-1" and orientation_audit(-1,1,-1)["internal_cancellation"]
 assert not algebra_audit(match_internal=False)["composition_exact"] and not algebra_audit(reverse=False)["reciprocity_exact"]
def test_boundaries_fail_closed():
 v=build();assert v["causal_chain_composition"]["transitivity_without_crosswalk"]=="NO_CERTIFIED_MAP"
 assert v["conditional_nontriviality"]["physical_receiver"]=="NO_CERTIFIED_MAP" and not v["flags"]["PHYSICAL_REDSHIFT_CERTIFIED"] and not v["flags"]["ADVANCED_SIGNAL_PROMOTED"]
