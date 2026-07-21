import json

from closed_universe_observers.atlas import generate_phase1_relational_observable_disposition_synthesis_atlas as atlas


def test_atlas_is_current_and_fail_closed():
    result = atlas.build()
    assert json.loads(atlas.OUTPUT.read_text()) == result
    assert [row["status"] for row in result["rows"]] == [
        "CERTIFIED", "CERTIFIED", "CERTIFIED", "CERTIFIED", "CERTIFIED", "CERTIFIED",
        "CERTIFIED", "OBSTRUCTED", "NO_CERTIFIED_MAP", "NO_CERTIFIED_MAP"
    ]
    for row in result["rows"]:
        assert set(["theory", "background", "boundaries", "charge_sector", "carrier", "degree", "parity", "ell", "m", "k", "omega"]) <= set(row["mode_scope"])
