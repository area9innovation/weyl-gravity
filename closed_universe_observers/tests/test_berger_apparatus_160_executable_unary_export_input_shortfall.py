import json

from closed_universe_observers import generate_berger_apparatus_160_executable_unary_export_input_shortfall as subject


def test_both_immediate_base_producers_are_incomplete():
    audit = subject.build_payload()["base_input_audit"]
    assert set(audit) == {"replacement_112", "material_parent_56"}
    assert {entry["status"] for entry in audit.values()} == {"NO_CERTIFIED_MAP"}


def test_replacement_missing_sparse_q1():
    missing = subject.build_payload()["base_input_audit"]["replacement_112"]["required_fields_missing"]
    assert "sparse_entries" in missing
    assert "coefficient_ring" in missing


def test_material_parent_missing_q1_and_pairing_entries():
    missing = subject.build_payload()["base_input_audit"]["material_parent_56"]["required_fields_missing"]
    assert "q1_sparse_entries" in missing
    assert "pairing_sparse_entries" in missing


def test_old_executable_108_is_rejected():
    replay = subject.build_payload()["non_substitution_replay"]
    assert replay["old_108_block_count"] > 0
    assert replay["verdict"] == "EXECUTABLE_BUT_FORBIDDEN_AS_REPLACEMENT_INPUT"


def test_written_certificate_matches_fresh_build():
    payload = subject.build_payload()
    assert json.loads(subject.CERTIFICATE.read_text()) == subject.build_certificate(payload)
