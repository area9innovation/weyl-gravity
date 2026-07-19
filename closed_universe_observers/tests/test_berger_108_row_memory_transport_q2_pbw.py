from closed_universe_observers.generate_berger_108_row_memory_transport_q2_pbw import action_blocks, build, merge_blocks, payload_document, symmetry_defects, symbolic_velocity_audit

def test_velocity_first_jet_is_directly_verified(): assert symbolic_velocity_audit()["direct_symbolic_defect_count"] == 0
def test_two_channels_export_all_three_cyclic_orbits():
    blocks=action_blocks(); assert len(blocks) == 6; assert all(blocks.values())
def test_memory_transport_q2_is_symmetric(): assert symmetry_defects(merge_blocks(action_blocks())) == 0
def test_payload_support_and_size_are_exact():
    payload=payload_document(); assert payload["nonzero_output_rows"] == [27,28,29,30,31,34,36,38,80,81,82,83]; assert payload["operator_key_count"] == payload["serialized_term_count"]
def test_downstream_gates_stay_closed():
    disposition=build()["activation_disposition"]; assert disposition["memory_transport_q2_subblock_exported"] is True; assert disposition["complete_apparatus_q2_exported"] is False; assert disposition["scalar_q3_exported"] is False; assert disposition["detector_response_on_second_order_cone_authorized"] is False
