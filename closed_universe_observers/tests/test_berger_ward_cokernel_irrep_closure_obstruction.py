import json

from closed_universe_observers.generate_berger_ward_cokernel_irrep_closure_obstruction import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_old_ward_space_is_not_a_berger_module():
    gate = result()["original_444_space_gate"]
    assert gate["dimension"] == 444
    assert gate["escaping_basis_vector_count"] == 392
    assert gate["distinct_first_step_outside_coordinate_count"] == 424
    assert gate["nonzero_escape_incidence_count"] == 848
    assert not gate["invariant_under_J_Berger_U1"]
    assert not gate["induced_action_on_440_cokernel_exists"]


def test_minimal_closed_replacement_has_exact_isotypic_census():
    value = result()["minimal_representation_closure"]
    assert value["dimension"] == len(payload()["closure_coordinate_basis"]) == 900
    assert value["added_coordinate_count"] == 456
    assert value["isotypic_dimensions"] == {"0": 460, "2": 424, "4": 16}
    quotient = result()["action_image_and_closed_cokernel"]
    assert quotient["action_image_dimension"] == 4
    assert quotient["minimal_closed_cokernel_dimension"] == 896
    assert quotient["minimal_closed_cokernel_isotypic_dimensions"] == {
        "0": 456,
        "2": 424,
        "4": 16,
    }


def test_source_types_and_invariant_witness_location():
    value = result()
    sources = value["source_pair_orbit_types"]
    assert sources["emitter_Diff_BV"]["isotypic_dimensions"] == {"0": 1, "2": 2}
    assert sources["base_maxwell_typed"]["isotypic_dimensions"] == {"0": 1}
    assert sources["base_maxwell_typed"]["dimension_mod_action_image"] == 1
    display = value["witness_location"]["display_coordinate_orbit"]
    assert display["cyclic_module_dimension"] == 3
    assert display["isotypic_dimensions"] == {"0": 1, "2": 2}
    assert display["display_coordinate_fraction_in_each_projector"] == "1/2"


def test_minimal_representation_content_is_fail_closed_at_action_level():
    value = result()
    theorem = value["representation_content_theorem"]
    assert theorem["minimal_new_isotypic_content"] == (
        "one additional weight-0 real line"
    )
    assert theorem["pure_weight_2_or_weight_4_channel"] == "INSUFFICIENT"
    assert theorem["action_level_sufficiency"].startswith("NO_CERTIFIED_MAP")
    assert value["candidate_family_disposition"][
        "requested_440_irrep_decomposition"
    ] == "OBSTRUCTED_NOT_A_MODULE"
    assert not any(value["activation_disposition"].values())
