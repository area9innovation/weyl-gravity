import json
from closed_universe_observers import generate_berger_material_parent56_background_readout_interface as subject
def test_two_exact_profile_maps_are_row_indexed():
 p=subject.build_payload(); assert len(p["profile_maps"])==2
 assert all(x["source_carrier"]["rows"]==[55,56,57,58] for x in p["profile_maps"])
def test_four_action_hessian_entries_have_negative_unit_coefficient():
 p=subject.build_payload(); assert p["action_hessian_entry_count"]==4
 assert p["action_hessian_coefficients"]==["-1"]*4
def test_forward_and_adjoint_blocks_are_complete():
 a=subject.build_payload()["adjoint_and_pairing"]; assert a["forward_blocks"]==2 and a["adjoint_blocks"]==2 and a["formal_adjoint_defect_count"]==0
def test_chain_support_zero_mode_and_mutations_pass():
 p=subject.build_payload(); a=p["chain_and_support_audit"]
 assert not any(a[k] for k in ("generic_support_chain_defect_count","compact_support_chain_defect_count","spatial_zero_mode_chain_defect_count","mixed_nilpotency_defect_count","mixed_cyclicity_defect_count"))
 assert all(x["detected"] for x in p["mutations"])
def test_written_result_matches_fresh_build():
 p=subject.build_payload(); assert json.loads(subject.X.read_text())==p; assert json.loads(subject.C.read_text())==subject.build_certificate(p)
