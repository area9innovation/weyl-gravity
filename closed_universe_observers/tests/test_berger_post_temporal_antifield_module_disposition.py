import json

from closed_universe_observers.generate_berger_post_temporal_antifield_module_disposition import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_four_row_mapping_cone_is_exact_and_cyclic():
    cone = payload()["mapping_cone"]
    assert cone["shape"] == [114, 114]
    assert cone["new_rows"] == 4
    assert all(
        count == 0 for count in cone["new_q1_squared_key_counts"].values()
    )
    assert cone["unary_cyclicity_defect_key_count"] == 0


def test_declared_first_jet_class_is_complete():
    value = payload()["declared_first_jet_class"]
    assert value["action_count_per_emitter"] == 28
    assert value["complete_within_declared_class"] is True
    assert value["Berger_U1_kernel_audits"]["order_0"][
        "invariant_dimension"
    ] == 4
    assert value["Berger_U1_kernel_audits"]["order_1"][
        "invariant_dimension"
    ] == 24


def test_both_emitters_retain_rank_one_source_obstruction():
    for emitter, audit in enumerate(payload()["emitter_audits"].values()):
        assert audit["terminal_full_action_image_rank"] == 2613
        assert audit["first_jet_quotient_rank"] == 4
        assert audit["full_action_image_rank"] == 2617
        assert audit["source_augmented_rank"] == 2618
        assert audit["source_outside_image"] is True
        witness = audit["first_quotient_witness"]
        assert witness["output"] == 59
        assert witness["left_input"] == [3, []]
        assert witness["right_input"] == [84 + 6 * emitter, [0, 1]]
        assert witness["coefficient"] == [[-3, 1], [0, 1]]


def test_obstruction_is_u1_weight_zero_with_explicit_emitter_crosswalk():
    value = payload()
    for audit in value["emitter_audits"].values():
        assert audit["representation"]["Berger_U1_weight"] == 0
        assert audit["representation"][
            "infinitesimal_orbit_quotient_manifest"
        ]["coordinate_count"] == 0
    assert value["emitter_exchange"]["normalized_source_classes_equal"] is True


def test_minimal_next_target_is_fail_closed():
    target = result()["minimal_unexcluded_target"]
    assert target["status"] == "OPEN"
    assert "order-two" in target["new_action_tier"]
    assert result()["finite_class_theorem"]["status"] == "OBSTRUCTED"


def test_observer_promotions_remain_closed():
    downstream = result()["downstream_disposition"]
    assert downstream["second_jet_action_prolongation"] == "OPEN"
    assert all(
        value == "NO_CERTIFIED_MAP"
        for key, value in downstream.items()
        if key != "second_jet_action_prolongation"
    )
