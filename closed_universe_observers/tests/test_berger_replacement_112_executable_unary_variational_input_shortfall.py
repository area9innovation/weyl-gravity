import json
from closed_universe_observers import generate_berger_replacement_112_executable_unary_variational_input_shortfall as subject


def test_old_executable_payload_uses_local_phi2_symbols():
    assert "Phi2_00" in subject.build_payload()["exact_absence_replay"]["old_local_Phi2_symbols"]


def test_replacement_exports_only_retained_phi2_coefficients():
    replay = subject.build_payload()["exact_absence_replay"]
    assert len(replay["replacement_retained_Phi2_sparse"]) == 4
    assert replay["replacement_retained_to_component_jet_crosswalk_present"] is False


def test_first_missing_derivative_is_fail_closed():
    missing = subject.build_payload()["first_missing_variational_derivative"]
    assert missing["status"] == "NO_CERTIFIED_MAP"
    assert "D^3 S_108_nonrod" in missing["formula"]


def test_material_parent_is_not_reached():
    assert subject.build_payload()["disposition"]["material_parent_56_export"] == "NOT_REACHED"


def test_written_certificate_matches_fresh_build():
    payload = subject.build_payload()
    assert json.loads(subject.CERTIFICATE.read_text()) == subject.build_certificate(payload)
