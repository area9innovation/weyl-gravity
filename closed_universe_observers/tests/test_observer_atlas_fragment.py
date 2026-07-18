import json
from closed_universe_observers.atlas.generate_observer_atlas_fragment import OUTPUT, build

def test_generated_fragment_is_current():
    assert json.loads(OUTPUT.read_text()) == build()

def test_operational_fields_and_fail_closed_crosswalk():
    value = build()
    required = {"detector_response", "response_rank", "emitter_preparation", "clock_and_rod_dependence", "relational_redshift_contribution", "recoil_backreaction_order", "survives_gauge_reduction", "profile_green_boundary_dependencies"}
    assert all(set(row["operational_observable"]) == required for row in value["entries"])
    crosswalk = next(row for row in value["entries"] if "crosswalk" in row["id"])
    assert set(crosswalk["descriptions"].values()) == {"NO_CERTIFIED_MAP"}

def test_tangent_cone_is_not_promoted():
    row = next(row for row in build()["entries"] if row["id"] == "observer.berger.second_order_cone_restriction")
    assert row["tangent_cone"]["restriction_status"] == "OPEN"
    assert set(row["tangent_cone"]["correction_classes"].values()) == {"OPEN"}
