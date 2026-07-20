import json

from closed_universe_observers.generate_berger_order_three_common_action_promotion_gate import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_filtered_ibp_family_is_complete_and_both_parities_are_present():
    value = result()["invariant_classification"]
    assert value["target_grade_raw_dimension_per_emitter"] == 3960
    assert value["infinitesimal_generator_rank_per_emitter"] == 3028
    assert value["invariant_dimension_per_emitter"] == 932
    assert value["reflection_dimensions_per_emitter"] == {
        "reflection_even": 466,
        "reflection_odd": 466,
    }
    assert len(payload()["modules"]) == 1864


def test_constant_unary_common_action_repairs_typed_source():
    image = result()["exact_action_image"]
    assert image["complete_through_order_three_rank"] == 1922
    assert image["order_three_plus_typed_source_rank"] == 1922
    assert image["typed_source_in_image"]
    assert image["repair_module_count"] == 36
    assert image["repair_q2_manifest"]["key_count"] == 636


def test_decisive_64_coordinate_quotient_is_killed():
    quotient = result()["decisive_quotient"]
    assert quotient["source_support_coordinate_count"] == 64
    assert quotient["complete_through_order_three_projected_rank"] == 592
    assert quotient["source_augmented_projected_rank"] == 592


def test_q3_is_fail_closed_on_exact_quartic_nonuniqueness():
    value = result()
    gate = value["conditional_same_action_q3_gate"]
    assert gate["repair_q2_self_composition"] == "ZERO_STRUCTURAL"
    assert gate["maxwell_gauge_invariant_repair_exists"]
    ambiguity = gate["quartic_completion_nonuniqueness"]
    assert ambiguity["same_certified_q1_q2"]
    assert ambiguity["different_q3"]
    assert ambiguity["disposition"] == "OBSTRUCTED"
    assert not value["activation_disposition"]["same_action_q3_authorized"]
    assert not value["activation_disposition"]["nonlinear_detector_replay_authorized"]


def test_mutation_ledger_detects_module_parity_and_quartic_choices():
    mutations = result()["mutations"]
    assert mutations["drop_one_invariant_action"]["detected"]
    assert mutations["discard_reflection_odd_sector"]["detected"]
    assert mutations["set_quartic_lambda_zero_vs_one"]["same_q1_q2_different_q3"]
