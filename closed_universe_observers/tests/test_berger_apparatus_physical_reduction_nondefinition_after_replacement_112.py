import json

from closed_universe_observers import generate_berger_apparatus_physical_reduction_nondefinition_after_replacement_112 as subject


def test_executable_q1_fields_are_absent():
    audit = subject.build_payload()["executable_reduction_audit"]
    assert audit["combined_operator_fields_present"] == []
    assert audit["replacement_operator_fields_present"] == []


def test_old_complex_and_raw_rows_are_rejected():
    rejected = subject.build_payload()["forbidden_substitutions"]
    assert all(value.startswith("REJECTED") for value in rejected.values())


def test_every_reduction_output_fails_closed():
    disposition = subject.build_payload()["downstream_nondefinition"]
    assert set(disposition.values()) == {"NO_CERTIFIED_MAP"}


def test_activation_contract_requires_executable_sector_data():
    contract = subject.build_payload()["minimal_activation_contract"]
    assert "support and zero-mode sector" in contract["artifact"]
    assert "sparse_entries" in contract["must_export"]


def test_written_certificate_matches_fresh_build():
    assert json.loads(subject.CERTIFICATE.read_text()) == subject.build_certificate(subject.build_payload())
