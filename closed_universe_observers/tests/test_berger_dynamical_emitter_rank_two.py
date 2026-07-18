from __future__ import annotations

from closed_universe_observers.generate_berger_dynamical_emitter_rank_two import build, local_polarization_audit, response_audit


def test_massive_polarization_is_constraint_compatible_and_switched() -> None:
    audit = local_polarization_audit()
    assert audit["mass_shell_defect"] == "0"
    assert audit["constraint_defect_count"] == 0
    assert audit["switched_current_polarization_nonzero"]
    assert not local_polarization_audit(delete_electric_component=True)["switched_current_polarization_nonzero"]


def test_actual_emitter_response_is_causally_triangular_rank_two() -> None:
    audit = response_audit()
    assert audit["causal_zero_present"]
    assert audit["determinant_forced_to_nonzero_product"]
    assert audit["rank"] == 2
    assert response_audit(clone_second_preparation=True)["rank"] == 1
    assert not response_audit(erase_causal_order=True)["determinant_forced_to_nonzero_product"]


def test_scope_is_fail_closed_after_rank_promotion() -> None:
    flags = build()["flags"]
    assert flags["TWO_LOCALIZED_FREE_MASSIVE_EMITTER_CAUCHY_PREPARATIONS_CONSTRUCTED"]
    assert flags["DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_CERTIFIED"]
    assert not flags["DETECTOR_RECOIL_G2_COEFFICIENT_EVALUATED"]
    assert not flags["EMITTER_STRESS_BACKREACTION_INCLUDED"]
    assert not flags["QUANTUM_CLAIM"]
