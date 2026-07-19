from closed_universe_observers.generate_berger_108_row_normalized_readout_q2_pbw import (
    J_VERTICAL_ORDER,
    action_blocks,
    build,
    component_first_jet_replay_audit,
    merge_blocks,
    payload_document,
    symmetry_defects,
    symbolic_first_jet_audit,
)


def test_full_first_jet_matches_direct_symbolic_differentiation():
    assert symbolic_first_jet_audit()["direct_symbolic_defect_count"] == 0
    assert all(component_first_jet_replay_audit(channel)["component_replay_defect_count"] == 0 for channel in (0, 1))
    assert symbolic_first_jet_audit(delete_jacobian_variation=True)["jacobian_deletion_defect_count"] == 1


def test_jacobian_vertical_coordinates_are_complete_and_distinct():
    assert len(J_VERTICAL_ORDER) == len(set(J_VERTICAL_ORDER)) == 26
    assert J_VERTICAL_ORDER[:3] == ("g00", "g01", "g02")
    assert J_VERTICAL_ORDER[-1] == "r2_3"


def test_two_channels_export_all_three_cyclic_orbits():
    blocks = action_blocks()
    assert len(blocks) == 6
    assert all(blocks.values())


def test_normalized_readout_q2_is_symmetric():
    assert symmetry_defects(merge_blocks(action_blocks())) == 0


def test_payload_has_both_detector_channels_and_all_factor_sources():
    payload = payload_document()
    assert payload["operator_key_count"] > 0
    assert payload["serialized_term_count"] >= payload["operator_key_count"]
    for channel in ("D0", "D1"):
        assert set(payload["first_variation_source_counts"][channel]) == {
            "clock_bump",
            "metric_contraction",
            "normalized_Jacobian_clock",
            "normalized_Jacobian_metric",
            "normalized_Jacobian_rod",
            "polarization_clock",
            "polarization_rod",
            "rod_bump",
            "volume",
        }


def test_only_emitter_keeps_complete_q2_closed():
    disposition = build()["activation_disposition"]
    assert disposition["normalized_readout_q2_subblock_exported"] is True
    assert disposition["complete_apparatus_q2_exported"] is True
    assert disposition["complete_emitter_q2_exported"] is False
    assert disposition["complete_scalar_q2_exported"] is False
    assert disposition["detector_response_on_second_order_cone_authorized"] is False
