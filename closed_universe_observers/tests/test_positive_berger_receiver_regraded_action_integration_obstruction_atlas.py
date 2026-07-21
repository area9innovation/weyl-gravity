import json

from closed_universe_observers.atlas import generate_positive_berger_receiver_regraded_action_integration_obstruction_atlas as atlas


def test_atlas_is_current_and_fail_closed():
    result = atlas.build()
    assert json.loads(atlas.OUTPUT.read_text()) == result
    assert [row["status"] for row in result["rows"]] == ["CERTIFIED", "CERTIFIED", "OBSTRUCTED", "NO_CERTIFIED_MAP"]
