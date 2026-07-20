import json

from closed_universe_observers.generate_berger_quartic_completion_moduli_observer_invariance import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_parameter_map_is_complete_and_cyclic():
    value = result()
    completion = value["completion_space"]
    assert completion["ambient_parameter_space"] == "R^12"
    assert len(completion["basis"]) == 12
    assert completion["q3_parameter_map_rank"] == 12
    assert completion["odd_cyclicity_defect_polynomial"].startswith("0 for every")


def test_full_arity_three_locus_is_empty():
    gate = result()["full_arity_three_gate"]
    assert gate["repair_q2_key_count"] == 636
    assert gate["relevant_complete_q2_key_count"] == 1140
    assert gate["parameter_column_rank"] == 12
    assert gate["cross_defect_coordinates_outside_parameter_support"] > 0
    assert gate["witness_polynomial"] == "-4*g0*h0 + sum_i lambda_i*0"
    assert gate["admissible_subvariety"] == "EMPTY"


def test_decisive_witness_is_source_typed():
    witness = payload()["decisive_witness"]
    assert witness["output_row_id"] == "c_spatial_star_1"
    assert witness["coefficient"] == [[-4, 1], [0, 1]]
    assert witness["old_q2_factor"]["source"] == "emitter_Diff_BV"
    assert witness["repair_q2_factor"]["operator_key"] == [97, 55, [0, 2], 108, []]
    assert witness["quartic_parameter_column_coefficient"] == 0


def test_equivalence_and_observer_promotions_fail_closed():
    value = result()
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["equivalence_quotient"]["admissible_orbit_space"].startswith("EMPTY")
    disposition = value["K_Berger_and_observer_disposition"]
    assert disposition["K_Berger_defect_on_admissible_subvariety"].startswith(
        "NOT_APPLICABLE"
    )
    assert disposition["same_action_apparatus_memory_detector_map"].startswith(
        "NO_CERTIFIED_MAP"
    )
    assert all(mutation["detected"] for mutation in value["mutations"].values())
