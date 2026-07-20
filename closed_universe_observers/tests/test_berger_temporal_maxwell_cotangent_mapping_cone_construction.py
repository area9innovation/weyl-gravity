import json

from closed_universe_observers.generate_berger_temporal_maxwell_cotangent_mapping_cone_construction import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_one_quadratic_action_generates_all_new_unary_rows():
    action = payload()["quadratic_mapping_cone_action"]
    assert action["derived_q1_key_count"] == 8
    assert action["derived_q1_equals_declared_extension"] is True


def test_filtered_second_jet_kernel_is_complete():
    for audit in payload()["emitter_audits"].values():
        kernel = audit["kernel_audit"]
        assert kernel["raw_dimension"] == 528
        assert kernel["generator_rank"] == 404
        assert kernel["kernel_dimension"] == 124
        assert kernel["tier_counts"] == {
            "order_0_profile_jet": 4,
            "order_1": 24,
            "order_2_filtered": 100,
        }
        assert audit["second_jet_action_count"] == 128


def test_both_emitters_retain_exact_rank_one_obstruction():
    for emitter, audit in enumerate(payload()["emitter_audits"].values()):
        assert audit["terminal_full_action_image_rank"] == 2613
        assert audit["second_jet_quotient_rank"] == 28
        assert audit["full_action_image_rank"] == 2641
        assert audit["source_augmented_rank"] == 2642
        assert audit["source_outside_image"] is True
        witness = audit["first_quotient_witness"]
        assert witness["output"] == 59
        assert witness["left_input"] == [3, []]
        assert witness["right_input"] == [84 + 6 * emitter, [0, 1]]
        assert witness["coefficient"] == [[-3, 1], [0, 1]]


def test_every_tier_deletion_retains_source_obstruction():
    for audit in payload()["emitter_audits"].values():
        for mutation in audit["mutations"].values():
            assert mutation["source_still_obstructed"] is True
            assert (
                mutation["source_augmented_rank"]
                == mutation["retained_quotient_rank"] + 1
            )


def test_k_and_observer_gates_stop_after_arity_two():
    downstream = result()["downstream_disposition"]
    assert downstream["K_Berger_covariance"] == (
        "NOT_EVALUATED_AFTER_ARITY_TWO_OBSTRUCTION"
    )
    assert all(
        value == "NO_CERTIFIED_MAP"
        for key, value in downstream.items()
        if key != "K_Berger_covariance"
    )


def test_next_target_is_open_not_promoted():
    assert result()["filtered_second_jet_theorem"]["status"] == "OBSTRUCTED"
    assert result()["next_unexcluded_target"]["status"] == "OPEN"
