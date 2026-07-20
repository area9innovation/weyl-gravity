import json

from closed_universe_observers.generate_berger_replacement_112_unary_theory_obstruction import (
    CERTIFICATE,
    PAYLOAD,
)


def payload():
    return json.loads(PAYLOAD.read_text())


def certificate():
    return json.loads(CERTIFICATE.read_text())


def test_replacement_row_contract_is_complete():
    contract = payload()["replacement_contract"]
    assert contract["row_count"] == 112
    assert [row["index"] for row in contract["rows"]] == list(range(112))
    assert len(contract["new_pairing_entries"]) == 4


def test_background_closes_but_identity_action_is_not_invariant():
    value = payload()
    assert value["background"]["basis_rank"] == 8
    assert value["background"]["closure_defect_count"] == 0
    assert value["background"]["generator_symmetric_defect_rank"] == 4
    assert value["first_obstruction"]["principal_commutator_rank"] == 4


def test_minimal_mutations_fail():
    value = payload()["minimality_and_next_enlargement"]
    assert value["remove_R0_4_pair_background_rank"] == 7
    assert value["remove_R1_4_pair_background_rank"] == 7
    assert value["replace_A_by_skew_part_background_defect_rank"] == 4
    assert value["positive_diagonal_kinetic_repair"].startswith("OBSTRUCTED")


def test_changed_kinetic_action_is_only_a_candidate():
    value = payload()["minimality_and_next_enlargement"]
    assert value["canonical_candidate"] == "H=B^(-T) B^(-1)"
    assert value["candidate_changes_certified_action"] is True
    assert value["candidate_stress_Phi2_and_unary_status"] == "NO_CERTIFIED_MAP"


def test_fail_closed_downstream_disposition():
    value = certificate()
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["downstream_disposition"]["complete_112_row_q1"] == (
        "NO_CERTIFIED_MAP"
    )
    assert value["downstream_disposition"][
        "cohomology_apparatus_memory_redshift"
    ] == "NO_CERTIFIED_MAP"
