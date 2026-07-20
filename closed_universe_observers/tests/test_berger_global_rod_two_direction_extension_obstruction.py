import json

from closed_universe_observers.generate_berger_global_rod_two_direction_extension_obstruction import (
    CERTIFICATE,
    PAYLOAD,
)


def cert():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_exact_four_row_action_and_pairing_extension():
    rows = payload()["row_extension"]
    assert rows["new_degree_zero_rows"] == ["R0_4", "R1_4"]
    assert rows["new_degree_one_rows"] == ["R0_4_plus", "R1_4_plus"]
    assert rows["prospective_row_count"] == 112
    assert rows["pairing_rank_added"] == 4


def test_background_closure_rank_is_minimal():
    value = payload()
    assert value["background_completion"]["current_rank"] == 6
    assert value["background_completion"]["completed_rank"] == 8
    assert value["minimality"]["one_rod_completion_rank"] == 7
    assert value["minimality"]["two_rod_completion_rank"] == 8


def test_eight_rod_source_is_exactly_solved():
    equation = payload()["background_equation"]
    assert equation["Noether_closed"] is True
    assert equation["cokernel_projection"] == "ZERO"
    assert equation["canonical_primitive_exported"] is True
    assert equation["old_Phi2_is_unchanged"] is False
    assert all(
        block["primitive_residual_nonzero_count"] == 0
        for block in equation["exact_blocks"].values()
    )


def test_local_chain_embedding_is_obstructed():
    failure = payload()["first_later_incompatibility"]
    assert failure["canonical_inclusion_chain_defect_count"] == 2
    assert failure["local_embedding_status"] == "OBSTRUCTED"
    assert failure["only_formal_solution"] == (
        "P(s)=-c/s, a nonlocal order-minus-one map"
    )


def test_no_112_row_or_observer_promotion():
    value = cert()
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["downstream_disposition"]["complete_112_row_q1"] == (
        "NO_CERTIFIED_MAP"
    )
    assert value["downstream_disposition"][
        "original_108_row_local_chain_embedding"
    ] == "OBSTRUCTED"
    assert value["downstream_disposition"][
        "cohomology_Z2_memory_and_redshift"
    ] == "NO_CERTIFIED_MAP"
