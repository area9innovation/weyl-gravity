import json

from closed_universe_observers.atlas import generate_counterflow_charged_time_physical_instantiation_after_repaired_q70_health_nonactivation_atlas as atlas


def test_atlas_is_current_and_fail_closed():
    result = atlas.build()
    assert json.loads(atlas.OUTPUT.read_text()) == result
    assert [row["status"] for row in result["rows"]] == [
        "OBSTRUCTED", "OBSTRUCTED", "OBSTRUCTED", "NO_CERTIFIED_MAP", "NO_CERTIFIED_MAP", "NO_CERTIFIED_MAP"
    ]
    required = {"theory", "background", "boundaries", "charge_sector", "carrier", "degree", "parity", "ell", "m", "k", "omega"}
    assert all(required <= set(row["mode_scope"]) for row in result["rows"])
