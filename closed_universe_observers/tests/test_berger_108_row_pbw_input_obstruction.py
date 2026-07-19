from closed_universe_observers.generate_berger_108_row_pbw_input_obstruction import (
    build,
    profile_nondetermination_audit,
    switch_nondetermination_audit,
)


def test_normalized_detector_profile_width_is_not_fixed():
    audit = profile_nondetermination_audit()
    assert audit["normalized_centre_value_ratio_B_over_A"] == "8"
    assert audit["readout_q2_coefficient_differs"] is True


def test_unit_switch_radius_is_not_fixed():
    audit = switch_nondetermination_audit()
    assert audit["unit_integral_centre_value_ratio_B_over_A"] == "2"
    assert audit["emitter_q2_clock_and_interaction_coefficients_differ"] is True


def test_identity_mutations_collapse_witnesses():
    assert profile_nondetermination_audit(identify_widths=True)["readout_q2_coefficient_differs"] is False
    assert switch_nondetermination_audit(identify_radii=True)["emitter_q2_clock_and_interaction_coefficients_differ"] is False


def test_build_is_fail_closed_and_preserves_covariant_result():
    value = build()
    flags = value["flags"]
    assert flags["PINNED_64_ROW_PBW_PAYLOAD_VERIFIED"] is True
    assert flags["COVARIANT_108_ROW_Q1_Q2_IDENTITY_PRESERVED"] is True
    assert flags["DEPENDENCY_CLOSURE_PBW_NONUNIQUENESS_CERTIFIED"] is True
    assert flags["SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED"] is False
    assert flags["COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED"] is False
    assert value["atlas_status"] == "NO_CERTIFIED_MAP"


def test_minimal_activation_contract_names_machine_objects():
    objects = build()["minimal_activation_contract"]["new_machine_readable_objects"]
    assert len(objects) == 4
    assert any("coefficient-jet" in item for item in objects)
    assert any("q1" in item for item in objects)
    assert any("q2" in item for item in objects)
