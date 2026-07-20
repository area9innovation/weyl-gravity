import json

from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_auxiliary_domain_and_unique_odd_invariant_line():
    value = result()
    domain = value["auxiliary_cyclic_domain"]
    assert domain["carrier_rows"] == domain["pairing_rank"] == 110
    assert domain["additional_outer_scalar_pairs"] == 0
    tensors = value["transverse_tensor_classification"]
    assert tensors["invariant_dimension"] == 2
    assert tensors["reflection_odd_invariant_dimension"] == 1
    assert tensors["reflection_odd_basis"] == ["epsilon_ij"]


def test_local_action_is_cyclic_and_epsilon_columns_are_serialized():
    value = result()["local_common_action"]
    assert value["unit_action_monomials_per_emitter"] == 2
    assert value["action_derived_cyclic_q2_keys_per_emitter"] == 24
    assert value["unit_Ward_coordinates_per_emitter"] == 4
    assert value["normalized_cancellation_parameters"] == {
        "gamma_0": 2,
        "gamma_1": 2,
    }
    data = payload()
    assert all(
        len(data["cyclic_q2_entries"][f"emitter_{emitter}"]) == 24
        for emitter in (0, 1)
    )


def test_enlarged_closed_image_does_not_reach_typed_source():
    value = result()["image_in_representation_closure"]
    assert value["closure_dimension"] == 900
    assert value["old_action_image_dimension"] == 4
    assert value["new_epsilon_image_mod_old_dimension"] == 2
    assert value["enlarged_action_image_dimension"] == 6
    assert value["enlarged_closed_cokernel_dimension"] == 894
    assert value["enlarged_closed_cokernel_isotypic_dimensions"] == {
        "0": 454,
        "2": 424,
        "4": 16,
    }
    assert value["typed_source_augmented_rank"] == 7
    assert not value["typed_source_in_enlarged_image"]


def test_profile_first_jet_is_the_next_invariant_obstruction():
    value = result()
    residual = value["normalized_residual"]
    assert residual["support_coordinate_count"] == 112
    assert residual["Berger_type"] == "weight_0 trivial line"
    obstruction = value["next_invariant_obstruction"]
    assert obstruction["source_support_coordinate_count"] == 24
    assert obstruction["epsilon_channel_support_coordinate_count"] == 0
    assert obstruction["old_plus_epsilon_projected_image_rank"] == 2
    assert obstruction["source_augmented_projected_rank"] == 3
    assert not any(value["activation_disposition"].values())
