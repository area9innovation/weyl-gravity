import json

from closed_universe_observers import generate_berger_replacement112_executable_unary_mixed_nilpotency_obstruction as subject


def test_exact_fixture_is_nondegenerate_and_on_both_unit_circles():
    fixture = subject.build_payload()["exact_fixture"]
    assert fixture["unit_circle_checks"] == {"ca_squared_plus_sa_squared": "1", "cu_squared_plus_su_squared": "1"}
    assert fixture["nonzero_parameter_product"] != "0"


def test_mixed_nilpotency_is_obstructed_after_wave_quotient():
    obstruction = subject.build_payload()["mixed_nilpotency_obstruction"]
    assert obstruction["rod_wave_defect_count"] == 0
    assert obstruction["quotient_defect_count"] == 132
    assert obstruction["quotient_defect_matrix_position_count"] == 28


def test_first_witness_is_typed_and_nonzero():
    obstruction = subject.build_payload()["mixed_nilpotency_obstruction"]
    witness = obstruction["first_exact_witness"]
    assert (witness["output_row_id"], witness["input_row_id"]) == ("h_hat_star_00", "sigma")
    assert witness["input_pbw_word"] == [] and witness["time_mode"] == -2
    assert obstruction["first_witness_nonzero"] is True


def test_failure_stops_executable_and_downstream_promotions():
    disposition = subject.build_payload()["gate_disposition"]
    assert disposition["complete_executable_replacement112_q1"] == "NO_CERTIFIED_MAP"
    assert disposition["combined_160_cohomology_memory_redshift"] == "NOT_REACHED"


def test_written_artifacts_match_fresh_cached_build():
    payload = subject.build_payload()
    assert json.loads(subject.X.read_text()) == payload
    assert json.loads(subject.C.read_text()) == subject.build_certificate(payload)
