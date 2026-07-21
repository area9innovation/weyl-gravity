import copy
import json

import pytest

from closed_universe_observers import generate_berger_replacement112_132_defect_minimal_nilpotent_repair as subject
from closed_universe_observers import verify_berger_replacement112_132_defect_minimal_nilpotent_repair as verifier


def test_complete_generated_hessian_ansatz_has_one_action_orbit():
    ansatz = subject.build_payload()["complete_local_action_hessian_ansatz"]
    assert ansatz["raw_dimension"] == 4
    assert set(ansatz["raw_block_amplitudes"]) == {"K_RR", "K_Rh", "K_hR", "Delta_K_hh_rod"}
    assert set(ansatz["fixed_degree_zero_control_blocks"]) == {"Gamma_R", "Gamma_R_sharp"}
    assert ansatz["single_action_origin"] == "S_nonrod-S_R,I6+S_R,H"
    assert ansatz["integrability_constraint_rank"] == 3
    assert ansatz["action_orbit_dimension"] == 1
    assert ansatz["action_orbit_vector"] == [1, 1, 1, 1]
    assert ansatz["K_Berger_invariance_defect_count"] == 0
    assert ansatz["real_structure_defect_count"] == 0


def test_background_preservation_eliminates_the_action_orbit():
    gate = subject.build_payload()["background_preservation_gate"]
    assert gate["specialized_anchor_coefficient"] == "-125/81"
    assert gate["constraint_rank"] == 1
    assert gate["admissible_dimension"] == 0


def test_exact_nilpotency_equations_have_augmented_rank_jump():
    equation = subject.build_payload()["nilpotency_equation"]
    assert equation["scalar_equation_count"] == 4542
    assert equation["coefficient_matrix_rank"] == 1
    assert equation["augmented_matrix_rank"] == 2
    assert equation["solution_status"] == "INCONSISTENT"
    assert verifier.rank_pair(subject.build_payload()) == (1, 2)


def test_first_unavoidable_coefficient_is_typed_and_outside_the_orbit():
    witness = subject.build_payload()["nilpotency_equation"]["first_unavoidable_defect"]
    assert (witness["output_row_id"], witness["input_row_id"]) == ("h_hat_star_00", "sigma")
    assert witness["input_pbw_word"] == [] and witness["time_mode"] == -2
    assert witness["basis_monomial"]["x0"] == 2 and witness["basis_monomial"]["j"] == 1
    assert witness["correction_coefficient"] == "0"
    assert witness["right_hand_side"] != "0"


def test_material_parent_stays_separate_and_pushout_stays_undefined():
    disposition = subject.build_payload()["control_and_consumer_disposition"]
    assert disposition["material_parent56_internal_q1_and_rank2_detector"] == "CERTIFIED_SEPARATE_UNCHANGED"
    assert disposition["complete_repaired_replacement112_q1"] == "NO_CERTIFIED_MAP"
    assert disposition["apparatus_160_pushout"] == "NONDEFINED"


def test_mutation_splitting_an_integrable_block_is_rejected():
    mutated = copy.deepcopy(subject.build_payload())
    mutated["complete_local_action_hessian_ansatz"]["action_orbit_vector"][1] = 0
    with pytest.raises(AssertionError):
        verifier.validate_payload(mutated)


def test_mutation_deleting_target_only_equation_is_rejected():
    mutated = copy.deepcopy(subject.build_payload())
    mutated["nilpotency_equation"]["target_only_equation"]["right_hand_side"] = "0"
    with pytest.raises(AssertionError):
        verifier.validate_payload(mutated)


def test_mutation_zeroing_background_anchor_is_rejected():
    mutated = copy.deepcopy(subject.build_payload())
    mutated["background_preservation_gate"]["specialized_anchor_coefficient"] = "0"
    with pytest.raises(AssertionError):
        verifier.validate_payload(mutated)


def test_written_artifacts_match_fresh_cached_build():
    payload = subject.build_payload()
    assert json.loads(subject.X.read_text()) == payload
    assert json.loads(subject.C.read_text()) == subject.build_certificate(payload)
