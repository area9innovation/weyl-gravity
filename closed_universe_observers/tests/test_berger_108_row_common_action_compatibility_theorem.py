import json

from closed_universe_observers.generate_berger_108_row_common_action_compatibility_theorem import (
    CERTIFICATE,
)


def theorem():
    return json.loads(CERTIFICATE.read_text())


def test_general_cycle_holonomy_and_frozen_no_go():
    value = theorem()
    ward = value["ward_derivation"]
    general = value["compatibility_theorem"]
    assert general["determinant_polynomial"] == "b*c-a"
    assert general["nonzero_solution_iff"] == "a=b*c"
    assert general["frozen_holonomy"] == "2"
    assert ward["matrix"] == [[1, 0, -2], [1, -1, 0], [0, 1, -1]]
    assert (ward["determinant"], ward["rank"], ward["nullity"]) == (-1, 3, 0)


def test_all_three_one_edge_repairs_are_classified_but_not_promoted():
    repairs = theorem()["bounded_minimal_extension_ansatz"][
        "one_edge_action_normalizations"
    ]
    assert [repair["ratios"] for repair in repairs] == [
        [1, 1, 1],
        [2, 2, 1],
        [2, 1, 2],
    ]
    assert [repair["null_vector"] for repair in repairs] == [
        [1, 1, 1],
        [2, 1, 1],
        [2, 2, 1],
    ]
    assert all(repair["atlas_status"] == "NO_CERTIFIED_MAP" for repair in repairs)
    assert all(repair["lifecycle"] == "NECESSARY_CONDITION_ONLY" for repair in repairs)


def test_drop_controls_identify_each_decisive_orbit():
    controls = theorem()["counterexample_strategy"]["dropped_orbit_controls"]
    assert [control["null_vector"] for control in controls] == [
        [1, 1, 1],
        [2, 1, 1],
        [2, 2, 1],
    ]
    assert all(control["rank"] == 2 and control["detected"] for control in controls)


def test_one_row_extension_is_obstructed_and_every_promotion_is_closed():
    value = theorem()
    extension = value["bounded_minimal_extension_ansatz"]
    assert extension["one_row_carrier_enlargement"]["status"] == "OBSTRUCTED"
    assert extension["first_dimension_not_excluded"]["target_dimension"] == 110
    assert extension["first_dimension_not_excluded"]["status"] == "OPEN"
    assert extension["surviving_physics_candidates"] == []
    disposition = value["activation_disposition"]
    assert disposition["compatibility_theorem_certified"] is True
    assert all(
        status is False
        for name, status in disposition.items()
        if name != "compatibility_theorem_certified"
    )
