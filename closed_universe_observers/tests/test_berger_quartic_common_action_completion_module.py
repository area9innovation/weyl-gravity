import json

from closed_universe_observers.generate_berger_quartic_common_action_completion_module import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_complete_minimal_quartic_module_dimensions():
    classifications = result()["module_classification"]
    assert len(classifications) == 2
    assert all(row["raw_K_DA_dimension"] == 96 for row in classifications)
    assert all(row["Berger_U1_invariant_dimension"] == 28 for row in classifications)
    assert all(row["Maxwell_gauge_variation_rank"] == 22 for row in classifications)
    assert all(row["Maxwell_and_U1_invariant_dimension"] == 6 for row in classifications)
    assert all(
        row["Maxwell_kernel_reflection_dimensions"]
        == {"reflection_even": 3, "reflection_odd": 3}
        for row in classifications
    )
    assert len(payload()["modules"]) == 12


def test_quartic_family_changes_q3_but_not_q1_q2():
    operation = result()["action_derived_operations"]
    assert operation["q1_variation_at_zero_auxiliary_background"] == 0
    assert operation["q2_variation_at_zero_auxiliary_background"] == 0
    assert operation["q3_module_rank"] == 12
    assert operation["odd_cyclicity"] == "CERTIFIED_BY_COMMON_QUARTIC_ACTION"


def test_q3_selection_remains_obstructed():
    value = result()
    obstruction = value["coefficient_selection_obstruction"]
    assert obstruction["dimension"] == 12
    assert obstruction["zero_and_each_basis_completion_share_terminal_q1_q2"]
    assert obstruction["zero_and_each_basis_completion_have_distinct_q3"]
    assert not obstruction["unique_q3_selected"]
    assert value["atlas_status"] == "OBSTRUCTED"
    assert not value["activation_disposition"]["nonlinear_redshift_or_detector_rank_authorized"]


def test_mutations_are_fail_closed():
    mutations = result()["mutations"]
    assert mutations["drop_one_Maxwell_kernel_line"]["detected"]
    assert mutations["flip_antisymmetric_DA_sign"]["detected"]
    assert mutations["set_one_lambda_zero_vs_one"]["same_q1_q2_different_q3"]
