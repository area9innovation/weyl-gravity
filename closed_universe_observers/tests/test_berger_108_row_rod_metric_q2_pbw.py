from closed_universe_observers.generate_berger_108_row_rod_metric_q2_pbw import (
    action_audit, action_blocks, build, merge_blocks, payload_document,
    tensor_symmetry_defects,
)


def test_densitized_metric_polarization_is_independent():
    audit = action_audit()
    assert audit["existing_metric_hessian_coefficient_defect_count"] == 0
    assert audit["direct_third_metric_variation_defect_count"] == 0
    assert audit["third_frechet_permutation_defect_count"] == 0


def test_all_five_rod_action_orbits_are_nonempty():
    blocks = action_blocks()
    assert set(blocks) == {"hrr_metric_output", "hhr_metric_output", "hhh_metric_output", "hr_rod_output", "hh_rod_output"}
    assert all(block for block in blocks.values())


def test_rod_q2_is_graded_symmetric_and_cyclic():
    audit = action_audit()
    assert tensor_symmetry_defects(merge_blocks(action_blocks())) == 0
    assert audit["hrr_to_hr_formal_transpose_defect_count"] == 0
    assert audit["hhr_to_hh_formal_transpose_defect_count"] == 0


def test_payload_has_exact_metric_and_rod_cotangent_support():
    payload = payload_document()
    assert payload["nonzero_output_rows"] == list(range(27, 37)) + list(range(74, 80))
    assert payload["operator_key_count"] > 0
    assert payload["serialized_term_count"] >= payload["operator_key_count"]


def test_subblock_remains_fail_closed_downstream():
    disposition = build()["activation_disposition"]
    assert disposition["rod_metric_q2_subblock_exported"] is True
    assert disposition["complete_apparatus_q2_exported"] is False
    assert disposition["scalar_q3_exported"] is False
    assert disposition["arity_replay_certified"] is False
    assert disposition["detector_response_on_second_order_cone_authorized"] is False
