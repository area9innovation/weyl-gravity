import json

from closed_universe_observers.generate_berger_auxiliary_diff_bv_scalar_orbit_repair import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_complete_scalar_orbit_is_uniquely_normalized():
    value = result()
    assert value["extended_common_action_family"]["q2"][
        "scalar_diff_bv_key_count"
    ] == 32
    closure = value["representation_closure"]
    assert closure["normalization"].startswith("alpha=1")
    assert closure["contractible_covariance"]["inherited_defect_manifest"][
        "operator_key_count"
    ] == 30
    assert closure["contractible_covariance"]["sum_at_alpha_one"] == "ZERO"


def test_earliest_arity_two_gate_remains_obstructed():
    gate = result()["arity_two_gate"]
    witness = gate["decisive_witness"]
    assert gate["status"] == "OBSTRUCTED"
    assert gate["admissible_locus_in_alpha_lambda"] == "EMPTY"
    assert witness["output_row_id"] == "tau_star"
    assert witness["coefficient"] == [[1, 1], [0, 1]]
    assert witness["scalar_orbit_coefficient"] == 0
    assert witness["repair_q2_required_key_present"] is False


def test_prior_arity_three_witness_also_survives():
    gate = result()["arity_three_diagnostic"]
    witness = gate["decisive_witness"]
    assert witness["output_row_id"] == "c_spatial_star_1"
    assert witness["old_repair_coefficient"] == [[-4, 1], [0, 1]]
    assert witness["scalar_repair_cross_coefficient"] == 0
    assert witness["quartic_parameter_column_coefficient"] == 0


def test_fail_closed_observer_disposition_and_mutations():
    value = result()
    assert value["atlas_status"] == "OBSTRUCTED"
    disposition = value["K_Berger_and_observer_disposition"]
    assert disposition["same_action_apparatus_memory_detector_map"] == (
        "NO_CERTIFIED_MAP"
    )
    assert disposition["gauge_reduction"].startswith("OBSTRUCTED")
    assert all(mutation["detected"] for mutation in value["mutations"].values())


def test_payload_contains_action_derived_orbit_not_a_fitted_key():
    entries = payload()["scalar_diff_bv_q2_entries"]
    assert len(entries) == 32
    assert {entry["output"] for entry in entries} == {
        49,
        50,
        51,
        52,
        108,
        109,
    }
