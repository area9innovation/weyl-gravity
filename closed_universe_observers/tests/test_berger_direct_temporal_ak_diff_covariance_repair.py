import json

from closed_universe_observers.generate_berger_direct_temporal_ak_diff_covariance_repair import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_direct_temporal_projection_is_in_the_complete_action_image():
    for audit in payload()["emitter_audits"].values():
        direct = audit["direct_temporal_AK_projection"]
        assert direct["admissible"] is True
        assert direct["action_image_rank"] == 934
        assert direct["source_augmented_rank"] == 934
        assert direct["target_reaching_column_count"] > 0


def test_full_covariance_projection_has_rank_one_obstruction():
    for audit in payload()["emitter_audits"].values():
        full = audit["complete_covariance_projection"]
        assert full["admissible"] is False
        assert full["action_image_rank"] == 934
        assert full["source_augmented_rank"] == 935
        assert full["first_quotient_witness"]["output"] == 59
        assert full["first_quotient_witness"]["coefficient"] == [
            [-3, 1],
            [0, 1],
        ]


def test_profile_and_diff_mutations_are_detected():
    for audit in payload()["emitter_audits"].values():
        assert all(
            mutation["detected"] for mutation in audit["mutations"].values()
        )


def test_quartic_and_observer_gates_fail_closed():
    value = result()
    assert value["arity_two_gate"]["status"] == "OBSTRUCTED"
    assert value["arity_three_and_quartic_gate"]["status"].startswith(
        "NOT_REACHED"
    )
    assert all(
        route["status"] == "NO_CERTIFIED_MAP"
        for route in payload()["quartic_descendant_route_ledger"]
    )
    assert value["K_Berger_and_observer_disposition"][
        "detector_response"
    ] == "NO_CERTIFIED_MAP"


def test_next_representation_is_antifield_covariance():
    missing = result()["first_missing_action_representation"]
    assert "antifield covariance" in missing["object"]
    assert "A_plus_0" in missing["selected_support"]
