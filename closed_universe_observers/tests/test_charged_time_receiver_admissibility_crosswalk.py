import copy
import json

import pytest

from closed_universe_observers.generate_charged_time_receiver_admissibility_crosswalk import (
    LEGACY_IDS,
    LEGACY_SOURCES,
    ROOT,
    build,
    classify,
)
from closed_universe_observers.verify_charged_time_receiver_admissibility_crosswalk import (
    I,
    reconstruct_legacy_classifications,
    verify_value,
)


def test_failure_classification_is_typed():
    assert classify(exact=True) == "ZERO_RESPONSE"
    assert classify(nonradical=False) == "RADICAL_UNDEFINED_RESPONSE"
    assert classify(denominator=False) == "UNDEFINED_ZERO_DENOMINATOR"
    assert classify(crosswalk=False) == "NO_CERTIFIED_MAP"
    assert classify(retarded=False) == "CAUSAL_INTERPRETATION_LOST"
    assert classify(clock=False) == "CLOCK_REMOVED_OBSTRUCTED"


def test_positive_control_and_interface():
    value, interface = build()
    assert classify() == "CERTIFIED_ADMISSIBLE"
    assert len(interface["receiver_required_fields"]) >= 10
    assert len(interface["crosswalk_required_fields"]) >= 8
    assert value["flags"]["RECEIVER_ADMISSIBILITY_CONTRACT_CERTIFIED"]
    assert not value["flags"]["ACTION_DERIVED_NONZERO_RECEIVER_CERTIFIED"]


def test_seven_row_census_is_complete_and_fail_closed():
    value, _ = build()
    completeness = value["census_completeness"]
    assert completeness["complete"]
    assert completeness["discovered_count"] == completeness["classified_count"] == 7
    assert not completeness["unclassified_ids"]
    rows = {row["atlas_id"]: row for row in value["observer_carrier_census"]}
    assert all(rows[key]["admissibility_status"] == "NO_CERTIFIED_MAP" for key in LEGACY_IDS)
    assert not any(row["physical_receiver_promoted"] for row in rows.values())


def test_independent_source_reconstruction_agrees():
    value, interface = build()
    verify_value(value, interface)


@pytest.mark.parametrize("legacy_id", LEGACY_IDS)
def test_deleting_either_legacy_row_fails_closed(legacy_id):
    value, interface = build()
    mutated = copy.deepcopy(value)
    mutated["observer_carrier_census"] = [
        row for row in mutated["observer_carrier_census"] if row["atlas_id"] != legacy_id
    ]
    with pytest.raises(AssertionError):
        verify_value(mutated, interface)


@pytest.mark.parametrize("bad_status", ["UNCLASSIFIED", "CERTIFIED_ADMISSIBLE"])
def test_legacy_status_promotion_fails_closed(bad_status):
    value, interface = build()
    mutated = copy.deepcopy(value)
    row = next(row for row in mutated["observer_carrier_census"] if row["atlas_id"] == LEGACY_IDS[0])
    row["admissibility_status"] = bad_status
    with pytest.raises((AssertionError, Exception)):
        verify_value(mutated, interface)


def test_coordinate_ratio_cannot_be_promoted_to_redshift():
    replay = json.loads((ROOT / LEGACY_SOURCES["legacy_replay"][0]).read_text())
    ratio = json.loads((ROOT / LEGACY_SOURCES["legacy_ratio"][0]).read_text())
    ratio["flags"]["COORDINATE_RATIO_PROMOTED_AS_REDSHIFT"] = True
    with pytest.raises(AssertionError):
        reconstruct_legacy_classifications(replay, ratio)


def test_original_five_dispositions_cannot_change():
    value, interface = build()
    mutated = copy.deepcopy(value)
    row = next(
        row
        for row in mutated["observer_carrier_census"]
        if row["atlas_id"] == "observer.general.charged_physical_time_relational_event_map"
    )
    row["admissibility_status"] = "NO_CERTIFIED_MAP"
    with pytest.raises(AssertionError):
        verify_value(mutated, interface)


def test_stale_legacy_dependency_hash_fails_closed(monkeypatch):
    path, _ = LEGACY_SOURCES["legacy_replay"]
    monkeypatch.setitem(LEGACY_SOURCES, "legacy_replay", (path, "0" * 64))
    with pytest.raises(AssertionError, match="legacy source drift legacy_replay"):
        build()
