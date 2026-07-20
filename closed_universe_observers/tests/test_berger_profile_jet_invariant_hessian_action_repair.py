import json

from closed_universe_observers.generate_berger_profile_jet_invariant_hessian_action_repair import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_complete_invariant_ansatz_and_closure_split():
    value = result()
    ansatz = value["declared_action_ansatz"]
    assert ansatz["raw_monomial_dimension_per_emitter"] == 96
    assert ansatz["Berger_U1_invariant_dimension_per_emitter"] == 28
    assert ansatz["invariant_family_dimensions"] == {
        "K03_scalar": 6,
        "K12_pseudoscalar": 6,
        "K0_perp_vector": 8,
        "K3_perp_vector": 8,
    }
    closure = value["closure_disposition"]
    assert closure["modules_preserving_900_closure"] == 24
    assert closure["modules_escaping_900_closure"] == 32
    assert len(payload()["modules"]) == 56


def test_profile_jet_line_is_action_realized():
    repair = result()["profile_first_jet_repair"]
    assert repair["source_support_coordinate_count"] == 24
    assert repair["source_in_closure_preserving_action_image"]
    assert repair["profile_jet_quotient_class_killed"]
    assert repair["old_plus_epsilon_image_rank"] == 6
    assert repair["enlarged_closure_preserving_image_rank"] == 30


def test_complete_source_still_fails_closed():
    value = result()
    repair = value["profile_first_jet_repair"]
    obstruction = value["first_remaining_obstruction"]
    assert repair["typed_source_augmented_rank"] == 31
    assert obstruction["support_coordinate_count"] == 88
    assert obstruction["projected_current_image_rank"] == 6
    assert obstruction["source_augmented_projected_rank"] == 7
    assert value["activation_disposition"]["profile_first_jet_action_module_realized"]
    assert not value["activation_disposition"]["complete_typed_maxwell_source_in_action_image"]
    assert not value["activation_disposition"]["representation_complete_common_action_carrier_exists"]
