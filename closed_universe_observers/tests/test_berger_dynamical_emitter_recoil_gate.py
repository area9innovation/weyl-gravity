from __future__ import annotations

from closed_universe_observers.generate_berger_dynamical_emitter_recoil_gate import build, recoil_audit


def test_two_compatible_emitter_completions_have_different_recoil() -> None:
    audit = recoil_audit()
    assert audit["retarded_recoil_coefficients"] == ["1/2", "1/5"]
    assert audit["coefficient_difference"] == "3/10"
    assert audit["different_recoil"]
    assert not recoil_audit(collapse_masses=True)["different_recoil"]


def test_formal_rank_two_survives_unknown_recoil() -> None:
    value = build()
    assert value["formal_rank_stability"]["determinant_constant"] == "-40*C_1*S_0/9"
    assert value["formal_rank_stability"]["rank"] == 2
    assert not recoil_audit(erase_constant_determinant=True)["constant_is_nonzero"]


def test_scope_is_fail_closed() -> None:
    flags = build()["flags"]
    assert flags["DYNAMICAL_EMITTER_INPUT_UNDERDETERMINATION_CERTIFIED"]
    assert flags["FORMAL_RECOIL_RANK_TWO_STABILITY_CERTIFIED"]
    assert not flags["SPECIFIC_DYNAMICAL_EMITTER_MODEL_SELECTED"]
    assert not flags["EMITTER_BV_COMPLEX_CONSTRUCTED"]
    assert not flags["RECOIL_COEFFICIENT_COMPUTED"]
    assert not flags["QUANTUM_CLAIM"]
