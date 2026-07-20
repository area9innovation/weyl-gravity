import json

from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_normalization_cokernel_recovers_holonomy_two():
    value = result()["normalization_cokernel"]
    assert value["rank"] == 2
    assert value["cokernel_dimension"] == 1
    assert value["primitive_cycle_functional"] == [1, -1, -1]
    assert value["frozen_v2_vector"] == [1, 0, 0]
    assert value["cycle_projection"] == 1
    assert value["recovered_holonomy"] == "H=2"


def test_exact_action_image_and_cokernel_dimensions():
    value = result()["action_to_ward_map"]
    assert value["nonlinear_action_locus"]["equation"] == (
        "z_00*z_11-z_01*z_10=0"
    )
    assert value["nonlinear_action_locus"]["normalized_110_point"] == [
        [0, 0],
        [-1, -1],
    ]
    linear = value["linear_envelope"]
    assert linear["codomain_dimension"] == 444
    assert linear["image_rank"] == 4
    assert linear["cokernel_dimension"] == 440
    assert linear["zero_image_coordinate_functional_count"] == 204


def test_payload_is_complete_on_declared_source_pair_orbit():
    value = payload()
    assert len(value["coordinate_basis"]) == 444
    assert len(value["vectors"]["emitter_Diff_BV"]) == 228
    assert len(value["vectors"]["base_maxwell_typed"]) == 120
    assert [len(value["vectors"][name]) for name in ("z_00", "z_01", "z_10", "z_11")] == [
        30,
        30,
        90,
        90,
    ]
    reduction = value["canonical_linear_reduction"]
    assert len(reduction["pivot_coordinate_indices"]) == 4
    assert len(reduction["cokernel_representative_coordinate_indices"]) == 440


def test_both_source_pair_classes_are_outside_the_image():
    classes = result()["complete_declared_source_pair_orbit"][
        "source_pair_cokernel_classification"
    ]
    assert classes["emitter_Diff_BV"]["status"] == "NONZERO_COKERNEL_CLASS"
    assert classes["base_maxwell_typed"]["status"] == "NONZERO_COKERNEL_CLASS"
    assert classes["source_total"]["status"] == "NONZERO_COKERNEL_CLASS"
    assert {classes[name]["augmented_rank"] for name in classes} == {5}


def test_typed_projection_and_lower_bound_remain_fail_closed():
    value = result()
    projection = value["complete_declared_source_pair_orbit"][
        "typed_maxwell_projection_recovery"
    ]
    assert projection["display"] == "-2 g0 h0"
    assert projection["all_action_columns_zero"] is True
    theorem = value["minimal_lower_bound_theorem"]
    assert theorem["carrier_pair_lower_bound"] == 1
    assert theorem["required_degrees"] == [0, 1]
    assert theorem["required_hessian_projection"] == "A_0--K_12 nonzero"
    assert theorem["additional_pair_count_beyond_one"] == "OPEN"
    assert value["activation_disposition"]["new_common_action_candidate_exists"] is False
