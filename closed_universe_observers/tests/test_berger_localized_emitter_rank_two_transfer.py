from __future__ import annotations

from closed_universe_observers.generate_berger_localized_emitter_rank_two_transfer import build, transfer_audit


def test_localized_triangular_transfer_has_rank_two() -> None:
    audit = transfer_audit()
    assert audit["rank"] == 2
    assert audit["causal_zero_present"]
    assert transfer_audit(clone_second_source=True)["rank"] == 1


def test_constraint_localization_and_causal_order_are_explicit() -> None:
    value = build()
    assert value["topological_localization"]["H1_dimension"] == 0
    assert value["topological_localization"]["H2_dimension"] == 0
    assert value["causal_support"]["inter_window_gap"] == "5/24"
    assert value["transfer_matrix"]["rank"] == 2


def test_scope_is_fail_closed() -> None:
    flags = build()["flags"]
    assert flags["TWO_PREDECLARED_SPATIALLY_LOCALIZED_CONSERVED_EMITTER_CURRENTS"]
    assert flags["LOCALIZED_EMITTER_TRANSFER_MATRIX_RANK_TWO"]
    assert not flags["ORIGINAL_COMMON_HOPF_EMITTER_AT_CLOCK_ZERO_CERTIFIED"]
    assert not flags["DYNAMICAL_EMITTER_RECOIL_INCLUDED"]
    assert not flags["FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED"]
    assert not flags["QUANTUM_CLAIM"]
