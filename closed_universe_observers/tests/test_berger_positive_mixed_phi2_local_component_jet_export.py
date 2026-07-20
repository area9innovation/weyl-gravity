import json

from closed_universe_observers import generate_berger_positive_mixed_phi2_local_component_jet_export as subject


def test_retained_basis_reconstructs_exact_positive_mixed_components():
    local = subject.build_payload()["retained_to_local_map"]
    assert local["reconstructed_nonzero_components"] == {
        "Phi2_00": "428/567",
        "Phi2_11": "-29/21",
        "Phi2_22": "-29/21",
        "Phi2_33": "-6/7",
    }


def test_all_consumed_component_jets_and_order_are_exported():
    local = subject.build_payload()["retained_to_local_map"]
    assert local["consumed_jet_count"] == 942
    assert local["maximum_derivative_order"] == 5
    assert len(local["consumed_component_jets"]) == 942


def test_exact_geometry_checks_and_connection_terms_pass():
    payload = subject.build_payload()
    local = payload["retained_to_local_map"]
    assert local["harmonic_projection_reconstruction_defect_count"] == 0
    assert local["pbw_commutator_defect_count"] == 0
    assert local["reality_defect_count"] == 0
    assert local["K_Berger_defect_count"] == 0
    assert len(payload["connection_and_covariant_jets"]["nonzero_connection_coefficients"]) == 6
    assert payload["connection_and_covariant_jets"]["nonzero_covariant_jet_entries"]


def test_universal_nonrod_d3s_terms_are_evaluated_fail_closed():
    payload = subject.build_payload()
    evaluation = payload["evaluated_nonrod_D3S"]
    assert evaluation["dependent_source_term_count"] == 6171
    assert evaluation["vanishing_after_evaluation_count"] == 6091
    assert evaluation["surviving_normalized_term_count"] == 20
    assert payload["independent_tensor_variation_anchor"]["direct_value"] == "-214/567"
    assert payload["disposition"]["replacement_112_complete_executable_q1"] == "NO_CERTIFIED_MAP"


def test_written_certificate_matches_fresh_exact_build():
    payload = subject.build_payload()
    assert json.loads(subject.PAYLOAD.read_text()) == payload
    assert json.loads(subject.CERTIFICATE.read_text()) == subject.build_certificate(payload)
