from closed_universe_observers.generate_charged_physical_time_event_map_theorem import action_angle_audit,build,ratio_audit,reduction_audit,stability_audit
def test_action_angle_covariance_and_basis():
 a=action_angle_audit(); assert a["bracket_psi_Q"]=="1" and a["R_covariance_defect"]=="0" and a["D_covariance_defect"]=="0"
 assert action_angle_audit(flip_charge_with_orientation=False)["orientation_symplectic_defect"]!="0"
 assert action_angle_audit(identify_K_with_D=True)["incorrect_K_equals_D_defect"]!="0"
def test_stability_and_reduction_are_distinct():
 s=stability_audit(); assert not s["lifted_phase"]["monotone_and_bounded"] and s["compact_phase_orbital"]["certified"] and s["modulated"]["certified"]
 assert reduction_audit()["one_clock_fixed_charge_destroyed"] and reduction_audit()["D_clock_class_dimension"]==0
def test_ratio_and_nontriviality_fail_closed():
 assert ratio_audit()["origin_independent"] and not ratio_audit(same_orientation=False)["origin_independent"]
 v=build(); assert v["conditional_nontriviality"]["status"]=="CONDITIONAL" and not v["flags"]["COUNTERFLOW_PHYSICAL_INSTANTIATION_CERTIFIED"] and not v["flags"]["QUANTUM_CLAIM"]
 assert v["counterflow_instance"]["first_undefined_block"]=="retained_gravity_scalar" and v["counterflow_instance"]["physical_nonzero_receiver"].startswith("NO_CERTIFIED_MAP")
