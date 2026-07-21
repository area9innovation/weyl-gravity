from __future__ import annotations

from closed_universe_observers.generate_two_phase_counterflow_relational_observable import build, prequotient_diagnostic, reduction_audit


def test_fixed_charge_derived_fibre_is_acyclic() -> None:
    audit = reduction_audit()
    assert audit["d_squared_zero"]
    assert audit["dS_plus_Sd_identity"]
    assert audit["cohomology_dimensions"] == [0, 0, 0]
    assert audit["relative_clock_dimension"] == 0
    assert audit["pairing_rank"] == 0
    assert not audit["positive_relative_clock_survives"]


def test_clock_survival_mutation_is_exposed() -> None:
    mutant = reduction_audit(retain_clock_after_quotient=True)
    assert mutant["relative_clock_dimension"] == 1
    assert mutant["positive_relative_clock_survives"]


def test_prequotient_values_are_quarantined() -> None:
    value = build()
    assert prequotient_diagnostic()["rank"] == 2
    assert prequotient_diagnostic()["formal_ratio"] == "5/2"
    assert prequotient_diagnostic(clone_phase=True)["rank"] == 1
    assert prequotient_diagnostic(advanced=True)["advanced_contamination"]
    assert value["retarded_response_disposition"]["rank"] is None
    assert value["relational_frequency_disposition"]["one_plus_z_rel"] is None
    assert not value["flags"]["PHYSICAL_RELATIVE_PHASE_OBSERVABLE_CERTIFIED"]
    assert not value["flags"]["QUANTUM_CLAIM"]
