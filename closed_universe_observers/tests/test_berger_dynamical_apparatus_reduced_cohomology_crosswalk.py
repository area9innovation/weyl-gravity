import json

from closed_universe_observers.generate_berger_dynamical_apparatus_reduced_cohomology_crosswalk import (
    CERTIFICATE,
    CONTRACT,
)


def cert():
    return json.loads(CERTIFICATE.read_text())


def contract():
    return json.loads(CONTRACT.read_text())


def test_missing_combined_q1_is_fail_closed():
    assert cert()["claim_status"] == "SHORTFALL_MISSING_COMPLETE_COMBINED_Q1_CROSSWALK"
    assert cert()["atlas_status"] == "OPEN"
    assert all(contract()["current_absence_audit"].values())


def test_contract_requires_complete_row_and_operator_data():
    value = contract()
    assert len(value["required_row_table_columns"]) == 10
    assert set(value["required_exact_objects"]) == {
        "combined_q1",
        "inclusion_base",
        "inclusion_apparatus",
        "projection_base",
        "odd_pairing",
        "real_structure",
        "K_Berger",
        "detector_chain_map",
        "support_category",
    }


def test_no_isolated_reduction_or_physical_promotion():
    assert "isolated 56-row cohomology called the combined physical reduction" in (
        contract()["forbid"]
    )
    assert all(
        value == "NO_CERTIFIED_MAP"
        for value in cert()["downstream_disposition"].values()
    )


def test_next_gate_is_crosswalk_instantiation():
    assert cert()["next_gate"] == (
        "INSTANTIATE_AND_VERIFY_BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK"
    )
