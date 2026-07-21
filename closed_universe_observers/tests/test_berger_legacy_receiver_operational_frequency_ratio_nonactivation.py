from closed_universe_observers.generate_berger_legacy_receiver_operational_frequency_ratio_nonactivation import (
    HISTORICAL_CROSSWALK,
    build,
    historical_contract,
    request_value,
)
import pytest


def test_all_maximal_candidates_are_nonactivated():
    result, _ = build()
    assert len(result["maximal_candidate_replay"]) == 3
    assert all(row["response_rank"] == 2 for row in result["maximal_candidate_replay"])
    assert all(row["ratio_status"] == "UNDEFINED_NO_PHYSICAL_RECEIVER" for row in result["maximal_candidate_replay"])
    assert result["operational_ratio_theorem"]["domain_on_legacy_census"] == "EMPTY"


def test_exactly_one_minimal_request_is_emitted():
    result, request = build()
    assert result["producer_request"]["count"] == 1
    assert request == request_value()
    assert request["body"]["state"] == "REQUESTED"
    assert "smallest common missing datum" in request["body"]["notes"][1]


def test_coordinate_control_is_not_promoted():
    result, _ = build()
    assert result["coordinate_control"]["exact_ratio"] == "1"
    assert result["coordinate_control"]["status"] == "COORDINATE_CONTROL_ONLY_NOT_OPERATIONAL_REDSHIFT"
    assert not result["flags"]["OPERATIONAL_FREQUENCY_RATIO_DEFINED"]
    assert not result["flags"]["COORDINATE_RATIO_PROMOTED_AS_REDSHIFT"]


@pytest.mark.parametrize(
    "mutation",
    [
        {"source_commit": "0" * 40},
        {"repository_path": HISTORICAL_CROSSWALK["repository_path"] + ".missing"},
        {"sha256": "0" * 64},
        {"source_commit": "HEAD"},
    ],
)
def test_historical_source_mutations_fail_closed(mutation):
    ref = dict(HISTORICAL_CROSSWALK)
    ref.update(mutation)
    with pytest.raises(Exception):
        historical_contract(ref)
