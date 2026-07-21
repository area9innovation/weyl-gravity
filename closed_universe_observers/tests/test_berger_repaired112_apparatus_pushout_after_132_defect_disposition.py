import copy

import pytest

from closed_universe_observers import generate_berger_repaired112_apparatus_pushout_after_132_defect_disposition as subject


def test_negative_repair_branch_makes_fresh_pushout_nondefined():
    payload = subject.build_payload()
    gate = payload["category_of_complexes_gate"]
    assert gate["replacement_source_object"] == "NONEXISTENT_IN_DECLARED_REPLACEMENT_FAMILY"
    assert gate["apparatus_pushout"] == "NONDEFINED"
    assert gate["identification_relation"] == "NOT_REACHED"
    assert gate["derived_combined_row_count"] == "NO_CERTIFIED_MAP"


def test_exact_separator_is_imported_without_rank_substitution():
    separator = subject.build_payload()["exact_nonactivation_separator"]
    assert separator["scalar_equation_count"] == 4542
    assert separator["coefficient_matrix_rank"] == 1
    assert separator["augmented_matrix_rank"] == 2
    assert separator["canonical_augmented_determinant"] != "0"
    assert separator["background_preserving_correction_dimension"] == 0


def test_material_parent_survives_only_as_a_separate_complex():
    survivor = subject.build_payload()["material_parent_survivor"]
    assert survivor["row_count"] == 56
    assert survivor["signed_pairing_rank"] == 56
    assert survivor["detector_coordinate_rank"] == 2
    assert survivor["combined_interpretation"] == "SEPARATE_ONLY"


def test_escape_signature_requires_a_genuinely_new_bv_direction():
    escape = subject.build_payload()["minimal_escape_signature"]
    assert escape["minimum_new_coefficient_image_dimension"] == 1
    assert escape["one_pair_route"]["minimum_new_rows"] == 2
    assert "degree-0" in escape["one_pair_route"]["field_row"]
    assert "degree-1" in escape["one_pair_route"]["antifield_row"]
    assert escape["classification_status"] == "SIGNATURE_ONLY_NOT_A_VIABLE_EXTENSION"


def test_mutated_repair_success_is_rejected():
    values = {name: subject.json.loads(path.read_text()) for name, path in subject.DEPS.items()}
    mutated = copy.deepcopy(values)
    mutated["repair_no_go"]["gate_results"]["complete_repaired_replacement112_q1"] = "CERTIFIED"
    with pytest.raises(AssertionError):
        subject.validate_imports(mutated)


def test_mutated_material_parent_failure_is_rejected():
    values = {name: subject.json.loads(path.read_text()) for name, path in subject.DEPS.items()}
    mutated = copy.deepcopy(values)
    mutated["material_parent"]["atlas_status"] = "OBSTRUCTED"
    with pytest.raises(AssertionError):
        subject.validate_imports(mutated)


def test_downstream_physical_claims_remain_fail_closed():
    disposition = subject.build_payload()["nonactivation_disposition"]
    assert disposition["physical_reduction"] == "NO_CERTIFIED_MAP"
    assert disposition["detector_response_after_reduction"] == "NO_CERTIFIED_MAP"
    assert disposition["memory_redshift_recoil_q2_q3_quantum"] == "NOT_REACHED"
