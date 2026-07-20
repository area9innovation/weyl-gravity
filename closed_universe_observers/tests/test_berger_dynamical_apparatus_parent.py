import json

from closed_universe_observers.generate_berger_dynamical_apparatus_parent import (
    CERTIFICATE,
    PAYLOAD,
)


def cert():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_complete_minimal_carrier_and_pairing():
    value = payload()["carrier"]
    assert value["physical_even_row_count"] == 28
    assert value["odd_cotangent_row_count"] == 28
    assert value["odd_pairing_rank"] == 56
    assert value["ghost_rows"] == []


def test_action_derives_nontrivial_binary_orbit():
    action = payload()["local_action"]
    assert action["quadratic_terms_generate_q1"] is True
    assert action["cubic_third_derivative_record_count_per_detector"] == 12


def test_all_action_identities_and_k_covariance_close():
    assert all(
        value == 0 or value == "0"
        for key, value in payload()["exact_identities"].items()
        if key != "reason"
    )


def test_rank_two_survives_but_all_jet_stays_open():
    assert cert()["observer_result"]["status"] == "SURVIVES"
    assert cert()["observer_result"]["rank"] == 2
    assert cert()["downstream_disposition"]["all_jet_temporal_source_membership"] == (
        "NO_CERTIFIED_MAP"
    )


def test_new_rows_do_not_touch_pure_old_source_support():
    source = cert()["source_class_result"]
    assert source["intersection_rank"] == 0
    assert source["pure_old_coordinate_count"] == 0
    assert source["source_status"] == "UNCHANGED_AND_EXPLICITLY_UNRESOLVED_ALL_JET"


def test_mutations_are_decisive():
    assert all(row["rejected"] for row in payload()["mutations"].values())
