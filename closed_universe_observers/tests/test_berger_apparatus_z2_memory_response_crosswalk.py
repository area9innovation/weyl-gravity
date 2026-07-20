import json

from closed_universe_observers.generate_berger_apparatus_z2_memory_response_crosswalk import (
    CERTIFICATE,
    CONTRACT,
)


def cert():
    return json.loads(CERTIFICATE.read_text())


def contract():
    return json.loads(CONTRACT.read_text())


def test_missing_same_background_receiver_is_fail_closed():
    assert cert()["claim_status"] == (
        "SHORTFALL_MISSING_SAME_BACKGROUND_BERGER_Z2_RECEIVER"
    )
    assert cert()["atlas_status"] == "OPEN"
    assert all(contract()["current_absence_audit"].values())


def test_receiver_covers_mixed_pair_and_all_correction_classes():
    value = contract()
    assert value["input_span"]["required_quadratic_pairs"] == [
        "(u_0,u_0)",
        "(u_0,u_1)",
        "(u_1,u_1)",
    ]
    assert set(value["correction_classes"]) == {
        "bounded_or_quasiperiodic",
        "smooth_secular",
        "causal_or_retarded",
    }


def test_leading_rank_is_retained_without_nonlinear_promotion():
    value = cert()["observer_disposition"]
    assert value["leading_linear_response_rank"] == (
        "CERTIFIED_RANK_TWO_IN_PARENT_SCOPE_ONLY"
    )
    assert value["nonlinear_response_rank_and_kernel"] == "NO_CERTIFIED_MAP"
    assert value["persistent_relational_memory"] == "NO_CERTIFIED_MAP"


def test_contract_forbids_cross_background_identification():
    assert (
        "compact-product modes identified with Berger modes by matching names"
        in contract()["forbid"]
    )
    assert cert()["request_ref"]["typed"] == (
        "same-background-berger-z2-integrability-receiver"
    )


def test_receiver_requires_exact_obstruction_and_response_outputs():
    required = contract()["required_exact_objects"]
    assert {"stabilizer_receiver", "resonant_receiver", "Z2_ideal"} <= set(required)
    assert {
        "response_restriction",
        "memory_transport",
        "correction_class_operators",
    } <= set(required)
