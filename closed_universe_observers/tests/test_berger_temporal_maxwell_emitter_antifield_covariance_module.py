import json

from closed_universe_observers.generate_berger_temporal_maxwell_emitter_antifield_covariance_module import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_complete_bounded_action_module_is_enumerated():
    for audit in payload()["emitter_audits"].values():
        module = audit["complete_antifield_module"]
        assert module["action_count"] == 2048
        assert module["sector_counts"] == {
            "A_plus_tau_K": 1024,
            "K_plus_tau_A": 1024,
        }
        assert module["tier_counts"] == {
            "order_0": 16,
            "order_1": 56,
            "order_2": 112,
            "order_3_IBP_closed": 1864,
        }
        assert set(module["reflection_counts"]) == {"even", "odd"}
        assert all(module["reflection_counts"].values())


def test_full_covariance_retains_rank_one_obstruction():
    for emitter, audit in enumerate(payload()["emitter_audits"].values()):
        projection = audit["complete_projection"]
        assert projection["admissible"] is False
        assert (
            projection["source_augmented_rank"]
            == projection["full_action_image_rank"] + 1
        )
        witness = projection["first_quotient_witness"]
        assert witness["output"] == 59
        assert witness["left_input"] == [3, []]
        assert witness["right_input"] == [84 + 6 * emitter, [0, 1]]
        assert witness["coefficient"] == [[-3, 1], [0, 1]]


def test_both_cotangent_sectors_are_rank_detectable():
    for audit in payload()["emitter_audits"].values():
        full_rank = audit["complete_projection"]["new_quotient_action_rank"]
        for name in ("omit_A_plus_tau_K", "omit_K_plus_tau_A"):
            mutation = audit["mutations"][name]
            assert mutation["detected"] is True
            assert mutation["quotient_action_rank"] < full_rank


def test_q1_pairing_and_action_hessian_boundaries_are_explicit():
    gate = result()["q1_pairing_real_structure"]
    assert gate["q1_change"] == "ZERO"
    assert gate["q1_nilpotency"].startswith("CERTIFIED")
    assert gate["action_Hessian"] == "CERTIFIED"
    assert gate["odd_cyclicity"].startswith("CERTIFIED")


def test_new_rows_and_downstream_observers_fail_closed():
    value = result()
    assert "new q1-preimage" in value["first_missing_representation"]["object"]
    assert value["arity_two_gate"]["status"] == "OBSTRUCTED"
    assert all(
        status == "NO_CERTIFIED_MAP"
        for status in value["downstream_disposition"].values()
    )


def test_claim_is_scoped_to_existing_rows_and_order_three():
    value = result()
    assert value["representation_and_action_module"][
        "carrier_extension"
    ].startswith("NO_NEW_ROWS")
    assert value["representation_and_action_module"][
        "bounded_derivative_orders"
    ] == [0, 1, 2, 3]
    assert value["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
