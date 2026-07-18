import json

from closed_universe_observers.generate_berger_exact_detector_smearings import INPUT, adjoint_chain_audit, build, profile_audit


def test_exact_clock_supports_match_detector_windows() -> None:
    rows = profile_audit(json.loads(INPUT.read_text()))["detectors"]
    assert rows[0]["clock_support"] == ["11/64", "13/64"]
    assert rows[1]["clock_support"] == ["23/64", "25/64"]
    assert rows[0]["physical_time_support"] == ["11/48", "13/48"]
    assert rows[1]["physical_time_support"] == ["23/48", "25/48"]


def test_clock_and_radial_profiles_are_exactly_normalized() -> None:
    audit = profile_audit(json.loads(INPUT.read_text()))
    assert audit["unit_clock_integrals"] is True
    assert audit["unit_spatial_rod_integrals"] is True


def test_detector_profiles_remain_distinct_and_local() -> None:
    audit = profile_audit(json.loads(INPUT.read_text()))
    assert audit["clock_supports_disjoint"] is True
    assert audit["polarizations_distinct"] is True
    assert audit["spatial_supports_inside_declared_local_chart_families"] is True


def test_profile_and_adjoint_mutations_fail() -> None:
    data = json.loads(INPUT.read_text())
    assert profile_audit(data, omit_spatial_scale=True)["unit_spatial_rod_integrals"] is False
    assert profile_audit(data, duplicate_clock=True)["clock_supports_disjoint"] is False
    assert profile_audit(data, clone_polarization=True)["polarizations_distinct"] is False
    assert adjoint_chain_audit(delete_outer_coderivative=True)["maxwell_gauge_adjoint_well_typed"] is False


def test_green_evaluation_and_coordinate_profiles_remain_open() -> None:
    flags = build()["flags"]
    assert flags["ADVANCED_DETECTOR_TO_EMITTER_COVECTOR_OPERATOR_EXPORTED"] is True
    assert flags["ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED"] is False
    assert flags["ADVANCED_MASSIVE_EMITTER_GREEN_IMAGE_EVALUATED"] is False
    assert flags["COORDINATE_LEVEL_EMITTER_CAUCHY_PROFILES_SERIALIZED"] is False
    assert flags["QUANTUM_CLAIM"] is False
