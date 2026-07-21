from closed_universe_observers.generate_berger_legacy_receiver_admissibility_replay import (
    build,
    classify_receiver,
)


def test_receiver_failures_are_typed():
    assert classify_receiver(nonradical=False) == "RADICAL_UNDEFINED_RESPONSE"
    assert classify_receiver(retarded=False) == "CAUSAL_INTERPRETATION_LOST"
    assert classify_receiver(background_map=False) == "NO_CERTIFIED_MAP"
    assert classify_receiver(receiver_class=False) == "NO_CERTIFIED_MAP"
    assert classify_receiver(denominator=False) == "UNDEFINED_ZERO_DENOMINATOR"
    assert classify_receiver() == "CERTIFIED_ADMISSIBLE"


def test_census_is_complete_and_fail_closed():
    result = build()
    census = result["census_completeness"]
    assert census["complete"]
    assert census["expected_count"] == census["discovered_count"] == census["classified_count"] == 7
    assert not census["unclassified_result_ids"]
    assert all(not row["physical_receiver_promoted"] for row in result["legacy_receiver_census"])


def test_prequotient_rank_is_not_receiver_descent():
    result = build()
    assert result["flags"]["THREE_PREQUOTIENT_RANK_TWO_RESPONSES_REPLAYED"]
    assert not result["flags"]["ACTION_DERIVED_PHYSICAL_RECEIVER_CERTIFIED"]
    for row in result["legacy_receiver_census"]:
        assert row["receiver_fields"]["descended_pairing"]["status"] != "CERTIFIED"
        assert row["receiver_fields"]["sampled_denominator_margin"]["status"] != "CERTIFIED"
