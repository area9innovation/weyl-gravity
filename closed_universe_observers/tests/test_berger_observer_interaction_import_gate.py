from __future__ import annotations

import json

from closed_universe_observers import generate_berger_observer_interaction_import_gate as producer
from closed_universe_observers import verify_berger_observer_interaction_import_gate as verifier


def _data() -> dict:
    return json.loads(producer.INPUT.read_text())


def test_action_degree_to_q_arity_is_not_off_by_one() -> None:
    data = _data()
    assert [(row["action_degree"], row["induced_operation"]) for row in data["action_arity_ledger"]] == [
        (2, "q1"), (3, "q2"), (4, "q3")
    ]
    assert all(row["action_degree"] == row["input_arity"] + 1 for row in data["action_arity_ledger"])


def test_probe_rank_two_is_not_promoted_without_extended_q1_and_green_operator() -> None:
    certificate = producer.build()
    assert certificate["probe_baseline"]["rank"] == 2
    assert certificate["flags"]["PROBE_LIMIT_RANK_TWO_BASELINE_IMPORTED"] is True
    assert certificate["flags"]["EXTENDED_APPARATUS_Q1_CERTIFIED"] is False
    assert certificate["flags"]["EXTENDED_RETARDED_GREEN_CERTIFIED"] is False
    assert certificate["flags"]["EXTENDED_LINEAR_RANK_TWO_TRANSFER_CERTIFIED"] is False


def test_apparatus_model_uses_composite_polarization_and_external_source_boundary() -> None:
    model = producer.build()["apparatus_interface_contract"]["model"]
    assert model["polarization"].startswith("COMPOSITE_P_A_EQUALS_DTHETA_WEDGE_DRA")
    assert model["source_role"] == "EXTERNAL_Q_CLOSED_CONSERVED_SOURCE_AT_THIS_GATE"
    assert model["dynamical_emitter_deferred"] is True


def test_team_handoff_and_conditional_formal_rank_lemma_are_explicit() -> None:
    certificate = producer.build()
    assert certificate["formal_rank_stability_lemma"]["determinant_constant_term"] == "C_00*C_11>0"
    assert certificate["formal_rank_stability_lemma"]["actual_interacting_deformation_constructed"] is False
    assert "nonlinear team" in certificate["gauge_and_team_boundary"]["nonlinear_team_supplies"]
    assert certificate["gauge_and_team_boundary"]["observer_evaluation_chain_morphism"] is False


def test_each_corrected_interaction_gate_mutation_fails_closed() -> None:
    data = _data()
    for mutation in data["mutations"]:
        result = producer.evaluate(data, mutation["patch"])
        assert result["requirements"][mutation["expected_failed_requirement"]] is False


def test_independent_corrected_interaction_gate_replay() -> None:
    assert verifier.main() == 0
