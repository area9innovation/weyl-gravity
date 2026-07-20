import json

from closed_universe_observers.generate_berger_common_action_observable_replay_disposition import (
    CERTIFICATE,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def test_replay_fails_closed_without_repaired_action_carrier():
    gate = result()["replay_gate"]
    assert not gate["representation_complete_common_action_carrier_exists"]
    assert not gate["unary_q2_rebuild_performed"]
    assert not gate["nonlinear_observable_row_classified"]


def test_five_scoped_observer_results_survive_without_promotion():
    value = result()
    ledger = value["standalone_observable_survival_ledger"]
    assert len(ledger) == 5
    assert all(row["survival"].startswith("CERTIFIED") for row in ledger.values())
    assert set(value["nonpromotion_theorem"]["linear_results_invalidated"]) == set()
    assert set(value["nonpromotion_theorem"]["linear_results_promoted_to_nonlinear"]) == set()


def test_smallest_next_action_module_is_exact_and_fail_closed():
    module = result()["smallest_next_action_module"]
    assert module["id"] == "M_profile_first_jet_weight_zero"
    assert module["ambient_dimension"] == 108
    assert module["ambient_isotypic_dimensions"] == {"0": 60, "2": 48}
    assert module["current_projected_action_image_rank"] == 2
    assert module["source_augmented_rank"] == 3
    assert len(module["source_vector_entries"]) == 24
    assert module["action_realization_status"] == "NO_CERTIFIED_MAP"
    assert not any(result()["activation_disposition"].values())
