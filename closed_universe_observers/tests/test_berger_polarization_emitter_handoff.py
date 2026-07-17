from __future__ import annotations

from closed_universe_observers.generate_berger_polarization_emitter_handoff import build, model_audit


def test_108_row_carrier_and_pairing_are_exact() -> None:
    audit = model_audit()
    assert audit["degree_ranks_minus1_0_1_2"] == [6, 48, 48, 6]
    assert audit["total_rows"] == 108
    assert audit["pairing_nondegenerate"]
    assert not model_audit(delete_cotangent_rows=True)["pairing_nondegenerate"]


def test_current_conservation_and_common_principal_cone() -> None:
    audit = model_audit()
    assert audit["source_conserved"]
    assert audit["principal_symbol_rank"] == 3
    assert not model_audit(use_unprotected_current=True)["source_conserved"]


def test_handoff_is_fail_closed() -> None:
    flags = build()["flags"]
    assert flags["SPECIFIC_DYNAMICAL_EMITTER_MODEL_SELECTED"]
    assert flags["AUTHORITATIVE_108_ROW_EMITTER_INTERFACE"]
    assert not flags["108_ROW_Q1_CERTIFIED"]
    assert not flags["DYNAMICAL_EMITTER_RECORD_RANK_TWO_CERTIFIED"]
    assert not flags["EMITTER_STRESS_BACKREACTION_INCLUDED"]
    assert not flags["QUANTUM_CLAIM"]
