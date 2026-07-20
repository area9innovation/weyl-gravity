import json

from closed_universe_observers.generate_berger_temporal_curl_all_jet_disposition_shortfall import (
    CERTIFICATE,
    REQUEST,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def test_nonzero_second_jet_selects_all_jet_branch():
    lifecycle = result()["predecessor_lifecycle"]
    assert lifecycle["terminal_state"] == "OBSTRUCTED"
    assert lifecycle["branch_selected"] == "ALL_JET_FINITE_PRESENTATION"


def test_missing_exact_module_layers_are_explicit():
    audit = result()["capability_audit"]
    assert audit["audit_verdict"] == "MISSING_REQUIRED_EXACT_MODULE_MACHINERY"
    missing = " ".join(audit["missing_required_layers"])
    assert "syzygies" in missing
    assert "filtered" in missing


def test_all_jet_claim_remains_fail_closed():
    disposition = result()["all_jet_disposition"]
    assert disposition["status"] == "SHORTFALL"
    assert disposition["source_membership_at_any_finite_order"] == (
        "NO_CERTIFIED_MAP"
    )
    assert disposition["irreducible_cokernel_generator"] == "NO_CERTIFIED_MAP"


def test_typed_forge_request_is_open_and_bound():
    request = json.loads(REQUEST.read_text())
    assert request["schema"] == "work-v0"
    assert request["body"]["state"] in {"REQUESTED", "ACCEPTED"}
    assert request["id"] == result()["downstream_contract"]["blocking_request"]


def test_nonlinear_observer_promotions_are_closed():
    assert all(
        value == "NO_CERTIFIED_MAP"
        for value in result()["downstream_disposition"].values()
    )
