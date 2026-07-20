import json

from closed_universe_observers.generate_berger_dynamical_apparatus_combined_q1_crosswalk_obstruction import (
    CERTIFICATE,
    PAYLOAD,
)


def cert():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_typed_pushout_does_not_concatenate_semantic_names():
    candidate = payload()["candidate_pushout"]
    assert candidate["candidate_row_count"] == 156
    assert candidate["parent_only_row_count"] == 48
    assert len(candidate["shared_row_relations"]) == 8
    assert candidate["status"] == "CANDIDATE_REJECTED_AT_K_INTERFACE"


def test_material_rods_cannot_replace_missing_global_rods():
    audit = payload()["first_incompatibility"][
        "parent_material_rows_cannot_supply_missing_directions"
    ]
    assert audit["material_transport_determinant"] == 1
    assert audit["coefficient_constraint_rank"] == 24
    assert audit["constant_mixing_nullity"] == 0


def test_global_rod_K_closure_requires_two_real_directions():
    closure = payload()["first_incompatibility"]["global_rod_closure"]
    assert closure["current_real_rod_span_rank"] == 6
    assert closure["time_translation_closure_rank"] == 8
    assert closure["minimal_additional_real_rod_directions"] == 2
    assert closure["constant_internal_6_by_6_completion_exists"] is False


def test_minimal_pairing_repair_has_four_rows():
    repair = payload()["minimal_repair"]
    assert repair["added_degree_zero_rows"] == 2
    assert repair["added_degree_one_cotangent_rows"] == 2
    assert repair["repaired_base_row_count"] == 112
    assert repair["prospective_identified_union_row_count"] == 160


def test_failure_is_fail_closed_before_cohomology():
    value = cert()
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["interface_disposition"]["K_Berger_matrix"] == "OBSTRUCTED"
    assert value["interface_disposition"]["complete_sparse_combined_q1"] == (
        "NO_CERTIFIED_MAP"
    )
    assert all(
        status == "NO_CERTIFIED_MAP"
        for status in value["downstream_disposition"].values()
    )
