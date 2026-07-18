from closed_universe_observers.generate_berger_emitter_stress_clock_backreaction import (
    build,
    cyclic_orbit_audit,
    reduced_noether_audit,
)


def test_reduced_noether_energy_exchange_closes() -> None:
    assert reduced_noether_audit()["ward_residual"] == "0"
    assert reduced_noether_audit()["ward_defect_count"] == 0


def test_clock_source_is_reciprocal_and_required() -> None:
    assert reduced_noether_audit(omit_clock_source=True)["ward_defect_count"] > 0


def test_common_action_q2_orbits_are_cyclic() -> None:
    assert cyclic_orbit_audit()["cyclicity_defect_count"] == 0
    assert cyclic_orbit_audit(omit_metric_output=True)["cyclicity_defect_count"] > 0
    assert cyclic_orbit_audit(omit_clock_output=True)["cyclicity_defect_count"] > 0


def test_claims_remain_fail_closed_beyond_first_jet() -> None:
    flags = build()["flags"]
    assert flags["EMITTER_STRESS_AND_CLOCK_SWITCH_Q2_BACKREACTION_INCLUDED"] is True
    assert flags["COMPLETE_108_ROW_Q1_Q2_IDENTITY_CERTIFIED"] is False
    assert flags["FULL_NONLINEAR_EMITTER_BACKREACTION_INCLUDED"] is False
    assert flags["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
    assert flags["QUANTUM_CLAIM"] is False
