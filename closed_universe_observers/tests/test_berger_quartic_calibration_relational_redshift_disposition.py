import json

import pytest

from closed_universe_observers.generate_berger_quartic_calibration_relational_redshift_disposition import (
    CERTIFICATE,
)
from closed_universe_observers import (
    verify_berger_quartic_calibration_relational_redshift_disposition as verifier,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def test_ambient_quartic_family_is_not_an_admissible_theory_locus():
    value = result()
    family = value["imported_quartic_family"]
    assert family["ambient_parameter_dimension"] == 12
    assert family["q3_parameter_map_rank"] == 12
    assert value["master_identity_precedence"][
        "latest_arity_two_admissible_locus"
    ] == "EMPTY_ADMISSIBLE_LOCUS"


def test_calibration_map_is_not_applicable_rather_than_zero():
    calibration = result()["calibration_map_disposition"]
    assert calibration["not_the_zero_map"] is True
    assert calibration["moduli_to_detector_tensor_polynomial"] == (
        "NOT_APPLICABLE_EMPTY_DOMAIN"
    )
    assert calibration["minimal_calibration_observables"] == (
        "NOT_APPLICABLE_EMPTY_DOMAIN"
    )


def test_nonlinear_relational_redshift_fails_closed():
    redshift = result()["relational_redshift_disposition"]
    assert redshift["completion_independent_nonlinear_redshift"] == (
        "NO_CERTIFIED_MAP"
    )
    assert redshift["two_event_dynamical_clock_construction_performed"] is False
    assert redshift["causal_support"] == "NO_CERTIFIED_MAP"
    assert redshift["K_Berger_covariance"] == "NO_CERTIFIED_MAP"


def test_standalone_observables_survive_without_promotion():
    value = result()
    assert len(value["standalone_observable_survival_ledger"]) == 5
    theorem = value["nonpromotion_theorem"]
    assert theorem["linear_or_source_free_results_invalidated"] == []
    assert theorem["linear_or_source_free_results_promoted"] == []


def test_next_representation_is_temporal_maxwell_antifield_covariance():
    missing = result()["smallest_additional_action_representation"]
    assert "Maxwell/emitter antifield covariance" in missing["object"]
    assert "A_plus_0" in missing["selected_support"]


def test_moduli_zero_map_mutation_is_rejected(tmp_path, monkeypatch):
    value = result()
    value["calibration_map_disposition"][
        "moduli_to_detector_tensor_polynomial"
    ] = "0"
    mutated = tmp_path / "mutated-moduli.json"
    mutated.write_text(json.dumps(value))
    monkeypatch.setattr(verifier, "CERTIFICATE", mutated)
    with pytest.raises(AssertionError):
        verifier.main()


def test_causal_support_promotion_mutation_is_rejected(tmp_path, monkeypatch):
    value = result()
    value["relational_redshift_disposition"]["causal_support"] = "CERTIFIED"
    mutated = tmp_path / "mutated-causal.json"
    mutated.write_text(json.dumps(value))
    monkeypatch.setattr(verifier, "CERTIFICATE", mutated)
    with pytest.raises(AssertionError):
        verifier.main()
