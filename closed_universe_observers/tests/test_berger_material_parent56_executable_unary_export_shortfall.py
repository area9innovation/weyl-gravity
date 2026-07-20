import json

from closed_universe_observers import generate_berger_material_parent56_executable_unary_export_shortfall as subject


def test_complete_row_dictionary_and_pairing_are_derived():
    payload = subject.build_payload()
    assert payload["carrier"]["row_count"] == 56
    assert payload["carrier"]["pairing_rank"] == 56
    assert len(payload["carrier"]["pairing_entries"]) == 56


def test_internal_action_hessian_is_executable():
    internal = subject.build_payload()["derivable_internal_unary"]
    assert internal["entry_count"] == 52
    assert internal["generic_rank_over_Q_Omega_s"] == 28
    assert internal["zero_mode_rank_over_Q_Omega"] == 24
    assert internal["q1_squared_defect_count"] == 0
    assert internal["formal_cyclicity_defect_count"] == 0
    assert internal["K_commutator_defect_count"] == 0


def test_coordinate_detector_map_is_only_partial():
    detector = subject.build_payload()["detector_smearing_partial_map"]
    assert detector["coordinate_selection_rank"] == 2
    assert detector["internal_chain_defect_count"] == 0
    assert detector["full_action_chain_map"] == "NO_CERTIFIED_MAP because the mixed lambda-F unary interface has no row realization"


def test_first_missing_variation_is_nonzero_and_unplaceable():
    missing = subject.build_payload()["first_missing_variational_object"]
    assert missing["status"] == "NO_CERTIFIED_MAP"
    assert len(missing["nonzero_unplaceable_derivatives"]) == 4
    assert {item["coefficient"] for item in missing["nonzero_unplaceable_derivatives"]} == {"-1"}


def test_written_certificate_matches_fresh_build():
    payload = subject.build_payload()
    assert json.loads(subject.PAYLOAD.read_text()) == payload
    assert json.loads(subject.CERTIFICATE.read_text()) == subject.build_certificate(payload)
