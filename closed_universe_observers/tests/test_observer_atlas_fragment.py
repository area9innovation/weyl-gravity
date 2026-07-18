import json
from closed_universe_observers.atlas.generate_observer_atlas_fragment import OBSERVER_FIELDS, OUTPUT, build
from residual_atlas.validate_fragment import validate

def test_generated_fragment_is_current():
    assert json.loads(OUTPUT.read_text()) == build()
    validate(OUTPUT)

def test_operational_fields_and_fail_closed_crosswalk():
    value = build()
    assert all(set(row["observer_data"]) == set(OBSERVER_FIELDS) for row in value["entries"])
    crosswalks = [row for row in value["entries"] if "crosswalk" in row["id"]]
    assert len(crosswalks) == 2
    assert all(set(row["descriptions"].values()) == {"NO_CERTIFIED_MAP"} for row in crosswalks)


def test_berger_physical_branch_bridge_is_inactive():
    row = next(row for row in build()["entries"] if row["id"] == "observer.crosswalk.berger_physical_branch_to_detector")
    assert row["observer_data"]["detector_response"]["status"] == "NO_CERTIFIED_MAP"
    assert row["mode_data"]["second_order"]["causal_retarded"]["status"] == "NO_CERTIFIED_MAP"

def test_tangent_cone_is_not_promoted():
    row = next(row for row in build()["entries"] if row["id"] == "observer.berger.second_order_cone_restriction")
    assert row["observer_data"]["detector_restriction_to_second_order_cone"]["status"] == "OPEN"
    second_order = row["mode_data"]["second_order"]
    assert {second_order[name]["status"] for name in ("bounded_or_finite_quasiperiodic", "smooth_secular", "causal_retarded")} == {"OPEN"}


def test_mixed_unary_precedes_apparatus_and_affine_k_morphism():
    value = build()
    row = next(row for row in value["entries"] if row["id"] == "observer.berger.massive_emitter.preparation_pair")
    result_ids = [evidence["result_id"] for evidence in row["evidence"]]
    assert result_ids.index("BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY") < result_ids.index("BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE")
    assert result_ids.index("BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE") < result_ids.index("BERGER_AFFINE_K_OBSERVER_MORPHISM")


def test_adaptive_row_imports_polarization_stream_without_green_promotion():
    row = next(row for row in build()["entries"] if row["id"] == "observer.berger.detector_profile.adaptive_cutoff_preflight")
    assert "BERGER_CLOCK_WEIGHTED_POLARIZATION_STREAM_TWO_J138" in {
        evidence["result_id"] for evidence in row["evidence"]
    }
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
