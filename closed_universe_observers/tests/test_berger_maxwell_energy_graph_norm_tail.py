from fractions import Fraction

from closed_universe_observers.generate_berger_maxwell_energy_graph_norm_tail import build


def test_field_strength_cost_changes_tail_power():
    value = build()
    theorem = value["field_strength_tail_theorem"]
    assert "Lambda_N^(-3/2)" in theorem["single_component_bound"]
    assert theorem["field_strength_components"] == [
        "d_Sigma A_Sigma",
        "partial_t A_Sigma",
        "d_Sigma A_0",
    ]


def test_graph_tail_cutoff_is_minimal_for_both_profiles():
    value = build()
    assert value["calculation"]["first_sufficient_component_sum_graph_tail_retained_max_two_j"] == 68743
    for row in value["calculation"]["polarization_bounds"]:
        assert Fraction(row["component_sum_graph_tail_upper_at_first_subunit_cutoff"]) < 1
        assert Fraction(row["component_sum_graph_tail_upper_at_previous_cutoff"]) >= 1


def test_dense_rail_is_not_promoted_to_recoil():
    value = build()
    assert value["calculation"]["first_sufficient_cutoff_capacity"]["supported_detector_coordinate_entries"] == 14_177_143_864
    assert value["route_disposition"]["response_specific_shell_stream"] == "ACTIVE"
    assert value["flags"]["MAXWELL_TAIL_TO_RECOIL_SCALAR_MAP_CERTIFIED"] is False
