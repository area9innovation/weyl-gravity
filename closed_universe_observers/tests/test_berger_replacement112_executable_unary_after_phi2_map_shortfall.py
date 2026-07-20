import json
from closed_universe_observers import generate_berger_replacement112_executable_unary_after_phi2_map_shortfall as subject

def test_phi2_shortfall_is_closed():
    value = subject.build_payload()["certified_inputs_now_executable"]
    assert value["dependent_term_count"] == 6171
    assert value["unaffected_term_count"] == 288

def test_carrier_and_pairing_are_complete():
    value = subject.build_payload()["certified_inputs_now_executable"]
    assert value["row_count"] == 112 and value["pairing_rank"] == 112
    assert len(value["pairing_entries"]) == 112

def test_executable_hessian_fields_are_literally_absent():
    audit = subject.build_payload()["exact_absence_replay"]
    assert audit["normalized_sparse_entry_count"] == 0
    assert "eight_rod_hessian_sparse_entries" in audit["required_executable_fields_absent"]

def test_first_missing_derivative_is_metric_rod_hessian():
    missing = subject.build_payload()["first_missing_action_derivative"]
    assert missing["status"] == "NO_CERTIFIED_MAP"
    assert missing["formula"].startswith("D_g D_R S_R,H")

def test_written_result_matches_fresh_build():
    payload = subject.build_payload()
    assert json.loads(subject.X.read_text()) == payload
    assert json.loads(subject.C.read_text()) == subject.build_certificate(payload)
